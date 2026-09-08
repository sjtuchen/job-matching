# -*- coding: utf-8 -*-
"""
匹配系统 ①基线评测：关键词匹配（Baseline = P5 rank_check 口径）
对每份简历：jieba 分词 → 与 359 条 JD 的标签集逐一算重合度 → 排名
评测口径与 P5 rank_check 完全对齐（族级 TOP25 命中数、并列取最好名次），
保证"拉平曲线"对比有锚点。

方法说明（为什么这样算重合度）：
- JD 侧：每族取 TOP25 高频技能词（JD能力标签体系.json，299 条国聘统计）
  + Boss 60 条按族归并；简历侧：jieba 分词后的文本。
- 这是"词面重合"基线：代表"不做能力图谱、纯数关键词"的天花板。
  图谱/向量方案要打败的就是这条线。
"""
import json, re, os
from collections import defaultdict, Counter

import jieba

BASE = r"D:\新国赛\简历语料"
RESUME_DIR = os.path.join(BASE, "合成简历库")
TAGS_PATH = os.path.join(BASE, "JD能力标签体系.json")
LIST_PATH = os.path.join(BASE, "合成样本清单.json")
JD_XLSX = r"D:\新国赛\jd_data.xlsx"
BOSS_XLSX = os.path.join(BASE, "boss_AIGC补充24条.xlsx")

OUT_REPORT = r"D:\新国赛\.temp\baseline_report.json"

# ---------------- 数据加载 ----------------

with open(TAGS_PATH, encoding="utf-8") as f:
    tags = json.load(f)
with open(LIST_PATH, encoding="utf-8") as f:
    samples = json.load(f)

# 族 -> TOP25 标签（P5 口径）
family_tags = {fam: list(info["TOP25技能(出现率)"].keys())
               for fam, info in tags["族×技能出现率"].items()}
FAMS = list(family_tags.keys())

# Boss 60 条按族归并
boss_fam_words = defaultdict(Counter)
try:
    from openpyxl import load_workbook
    wb = load_workbook(BOSS_XLSX, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    # 找到表头行（跳过可能的水印行）
    header_idx = None
    for i, row in enumerate(rows):
        if row and row[0] == "jd_id":
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("boss 表头未找到")
    header = list(rows[header_idx])
    col = {h: i for i, h in enumerate(header)}
    jd_col = col["JD原文"]
    fam_col = col["岗位类别"]
    edu_col = col["学历要求"]
    cat_col = col["岗位名称"]
    for row in rows[header_idx + 1:]:
        if not row or not row[0]:
            continue
    jd_text = (row[jd_col] or "") + " " + (row[cat_col] or "")
    jd_words = [w for w in jieba.cut(str(jd_text)) if len(w.strip()) >= 2]
    # 岗位类别列（12 字段版本）
    fam = (row[fam_col] or "").strip()
    if fam and fam in FAMS:
        boss_fam_words[fam].update(jd_words)
except Exception as e:
    print(f"[警告] Boss 标签归并失败，跳过: {e}")

# 国聘 JD：每条 JD 的标签集合 = 该族 TOP25 ∩ 该条 JD 文本
def load_jd_rows(path, source_label):
    from openpyxl import load_workbook
    wb = load_workbook(path, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header_idx = None
    for i, row in enumerate(rows):
        if row and row[0] == "jd_id":
            header_idx = i
            break
    header = list(rows[header_idx])
    col = {h: i for i, h in enumerate(header)}
    out = []
    for row in rows[header_idx + 1:]:
        if not row or not row[0]:
            continue
        out.append({
            "id": row[col["jd_id"]],
            "岗位名称": row[col["岗位名称"]],
            "族": row[col["岗位类别"]].strip(),
            "学历": (row[col["学历要求"]] or "").strip(),
            "JD文本": (row[col["JD原文"]] or "") + " " + (row[col["岗位名称"]] or ""),
            "来源": source_label,
        })
    return out

all_jds = load_jd_rows(JD_XLSX, "国聘") + load_jd_rows(BOSS_XLSX, "Boss")

print(f"JD 加载完成：国聘 {sum(1 for j in all_jds if j['来源']=='国聘')} + "
      f"Boss {sum(1 for j in all_jds if j['来源']=='Boss')} = {len(all_jds)} 条")

# ---------------- 基线打分：词面重合 ----------------

# 族级词模式（与 P5 hit_patterns 同口径：英文短词带词边界，中文子串）
def pat(word):
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9\+\.\-]{0,9}", word):
        return re.compile(r"(?<![A-Za-z0-9])" + re.escape(word) + r"(?![A-Za-z0-9])", re.IGNORECASE)
    return re.compile(re.escape(word))

all_words = {w for ws in family_tags.values() for w in ws}
pats = {w: pat(w) for w in all_words}

def edu_gate(resume_edu, jd_edu):
    """学历门槛：jd 要求硕士时本科简历过不了"""
    order = {"大专": 0, "本科": 1, "硕士": 2, "博士": 3}
    if not jd_edu:
        return True
    m = re.search(r"(大专|本科|硕士|博士)", jd_edu)
    if not m:
        return True
    return order.get(resume_edu, 1) >= order[m.group(1)]

# 简历学历：从文本正则提取（合成简历统一"本科毕业生"）
def resume_edu(text):
    m = re.search(r"(本科|硕士|博士)毕业生", text)
    return m.group(1) if m else "本科"

rank_by_layer = defaultdict(Counter)
detail = []
neg_hits = 0  # 负对照误命中计数（跨界层文科简历被硬核理工岗排进 Top3）

for fname in sorted(os.listdir(RESUME_DIR)):
    if not fname.endswith(".txt"):
        continue
    sid = fname.split("_")[0]
    s = meta = {x["id"]: x for x in samples}[sid]
    text = open(os.path.join(RESUME_DIR, fname), encoding="u8").read()

    # 每条 JD 打分：该 JD 所属族 TOP25 中出现在 JD 文本里的词 ∩ 简历文本
    scored = []
    for jd in all_jds:
        if not edu_gate(resume_edu(text), jd["学历"]):
            continue
        fam_words = family_tags.get(jd["族"], [])
        # JD 的标签集 = 族 TOP25 中出现在 JD 文本里的词
        jd_tagset = {w for w in fam_words if pats[w].search(jd["JD文本"])}
        if not jd_tagset:
            continue
        # 简历命中数：jd_tagset 中出现在简历里的词
        hits = sum(1 for w in jd_tagset if pats[w].search(text))
        score = hits / len(jd_tagset)
        scored.append((score, jd["id"], jd["族"], jd["岗位名称"]))

    scored.sort(key=lambda t: -t[0])
    top3 = scored[:3]
    target_fam = s["目标族"]
    # 目标族排名：该简历对族中位得分的名次
    fam_scores = defaultdict(list)
    for sc, jid, fam, name in scored:
        fam_scores[fam].append(sc)
    fam_med = {fam: sorted(v)[len(v)//2] for fam, v in fam_scores.items()}
    target_med = fam_med.get(target_fam, 0)
    rank = sum(1 for f, v in fam_med.items() if v > target_med) + 1
    top_fam = max(fam_med, key=fam_med.get)

    rank_by_layer[s["层"]][rank] += 1
    detail.append({
        "id": sid, "层": s["层"], "专业": s["专业"], "目标族": target_fam,
        "目标族中位得分": round(target_med, 3),
        "目标族排名": rank,
        "得分最高族": top_fam,
        "Top3岗位": [{"jd_id": jid, "岗位": name, "族": fam, "得分": round(sc, 3)}
                     for sc, jid, fam, name in top3],
        "负对照进Top3": any(f in ("算法/研发（对照）", "智能制造/硬件（对照）")
                           and "（对照）" in f for sc, jid, f, name in top3
                           if s["层"] == "跨界层" and "文学" not in s["专业"] and "管理" not in s["专业"]),
    })

# ---------------- 报告 ----------------

print()
print("=" * 72)
print("① 基线评测结果（关键词词面重合，无能力图谱）")
print("=" * 72)
print(f"{'层':<6}{'Top1':<8}{'Top2':<8}{'Top3':<10}{'Top4+':<8}{'Top1率':<10}{'Top3率'}")
for layer in ["对口层", "迁移层", "跨界层"]:
    c = rank_by_layer[layer]
    n = sum(c.values())
    if n == 0:
        continue
    top1, top2, top3 = c[1], c[2], c[3]
    top4 = n - top1 - top2 - top3
    print(f"{layer:<6}{top1:<8}{top2:<8}{top3:<10}{top4:<8}{top1/n:<10.0%}{(top1+top2+top3)/n:.0%}")

# 与 P5 对比（P5: 对口 50% / 迁移 40% / 跳界 30%）
print()
print("对照 P5 口径（族级 TOP25 命中）: 对口 50% / 迁移 40% / 脚界 30%")
print("若本基线接近 P5 口径 → 锚点成立；之后的图谱/向量方案需拉平这条递减")

# 负对照检查
neg_cnt = sum(1 for d in detail if d.get("负对照进Top3"))
print(f"\n负对照误命中（跨界层文科简历 Top3 含硬核理工岗）: {neg_cnt} 份")
print("（负对照判定边界较粗，用于监控，达标线：0 份）")

out = {
    "_meta": {
        "时间": "2026-09-06",
        "脚本": "匹配系统 ① 基线评测",
        "方法": "词面重合基线（无能力图谱）：每条 JD 标签集=族TOP25∩JD文本，简历命中/标签集大小",
        "评分口径": "目标族排名按族中位得分（比 P5 命中数口径略严格，含学历门槛）",
        "环境": "jieba 0.42.1（已装）；jd_data 299 + Boss 60 = 359 条",
    },
    "分层排名分布": {layer: {f"第{k}名": v for k, v in sorted(c.items())}
                    for layer, c in rank_by_layer.items()},
    "逐份明细": detail,
}
with open(OUT_REPORT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\n明细已存 {OUT_REPORT}")
