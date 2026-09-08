# -*- coding: utf-8 -*-
"""
匹配系统 ⑤ 图谱匹配算法 v1.0（清单对齐版，向量层预留接口）
输入：个人能力图谱 + 359 份岗位能力图谱（graph_cache 目录）
输出：每份简历的岗位排名、匹配分、差距清单

算法（三步）：
1. 硬过滤：学历门槛 + 负对照隔离（文科简历 vs 硬核理工岗 57 条负对照的
   处理见 hard_gate：按简历图谱专业技能与岗位专业技能的零交集直接出局，
   而不是按“专业名”硬卡——这正是“能力图谱 vs 专业标签”的卖点差异）
2. 清单对齐打分：
   score = 0.5 * 专业技能Jaccard + 0.2 * 工具Jaccard + 0.3 * 软技能Jaccard
   （Jaccard = 交集/并集；权重与 Schema weights 一致）
3. Top-N 输出 + 差距清单（岗位有、简历无的技能按权重排出 Top 缺口）

向量层（⑥）接口已预留：graph_match(resume_graph, jd_graph, embed_fn=None)，
embed_fn 提供后自动启用语义兜底分，加权融合。当前版本 embed_fn=None 走纯清单。
"""
import argparse
import json
import os
import re
from collections import defaultdict

BASE = r"D:\新国赛"
TEMP = os.path.join(BASE, ".temp")
CACHE_DIR = os.path.join(TEMP, "graph_cache")
BGE_SIM_PATH = os.path.join(TEMP, "bge_sim_matrix.json")
LIST_PATH = os.path.join(BASE, r"简历语料\合成样本清单.json")
JD_XLSX = os.path.join(BASE, "jd_data.xlsx")
BOSS_XLSX = os.path.join(BASE, r"简历语料\boss_AIGC补充24条.xlsx")

W_SKILL, W_TOOL, W_SOFT = 0.8, 0.2, 0.0  # ⑤ 组合实验最优：软技能=通用词不区分族归零；技能组主判别+工具组辅助
NEG_FAMS = {"负对照", "硬核"}  # 全部负对照族（含"理工硬核负对照（xxx）"系）出排名池


def load_graphs():
    graphs = {}
    if not os.path.isdir(CACHE_DIR):
        return graphs
    for f in os.listdir(CACHE_DIR):
        if f.endswith(".json"):
            with open(os.path.join(CACHE_DIR, f), encoding="utf-8") as fh:
                g = json.load(fh)
                graphs[g["doc_id"]] = g
    return graphs


def load_jd_meta():
    """jd_id → {族, 岗位名称, 学历}"""
    from openpyxl import load_workbook
    meta = {}
    for path in [JD_XLSX, BOSS_XLSX]:
        wb = load_workbook(path, read_only=True)
        ws = wb[wb.sheetnames[0]]
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
        header_idx = next(i for i, r in enumerate(rows) if r and r[0] == "jd_id")
        col = {h: i for i, h in enumerate(rows[header_idx])}
        for row in rows[header_idx + 1:]:
            if not row or not row[0]:
                continue
            meta[str(row[col["jd_id"]])] = {
                "族": (row[col["岗位类别"]] or "").strip(),
                "岗位名称": row[col["岗位名称"]],
                "学历": (row[col["学历要求"]] or "").strip(),
            }
    return meta


def jd_graph_tags(jd_graph):
    return (set(jd_graph["skill_groups"]["专业技能"]),
            set(jd_graph["skill_groups"]["工具"]),
            set(jd_graph["skill_groups"]["软技能"]))


def resume_graph_tags(r_graph):
    return (set(r_graph["skill_groups"]["专业技能"]),
            set(r_graph["skill_groups"]["工具"]),
            set(r_graph["skill_groups"]["软技能"]))


def edu_gate(r_edu, jd_edu):
    order = {"大专": 0, "本科": 1, "硕士": 2, "博士": 3}
    m = re.search(r"(大专|本科|硕士|博士)", jd_edu or "")
    if not m:
        return True
    return order.get(r_edu, 1) >= order[m.group(1)]


def jaccard(a, b):
    if not a and not b:
        return 1.0  # 两边都空视为中性
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def dice(a, b):
    """F1 覆盖度（Dice 系数）= 2|A∩B| / (|A|+|B|)

    设计动机（⑤ 诊断结论）：
    - 简历图谱词数中位 31 >> JD 中位 13（简历是"我做过的一切"，JD 是"岗位核心要求"）
    - 对称 Jaccard 分母被简历杂词撑大 → 对口简历被稀释（22% << 基线 48%）
    - 纯 JD 覆盖度又让薄 JD（仅 1-2 词）白拿满分 → 排名退化
    - Dice 兼顾：简历词多只罚一次（分母 |r|+|j| 而非 |r|+|j|-|∩|），
      薄 JD 若简历不覆盖其少量要求，2|∩|/(|r|+|j|) 依旧很小
    边界：JD 该组无要求 → 1.0 中性（不罚简历有软技能而 JD 没列）；
          简历该组空但 JD 有要求 → 0.0；双空 → 1.0 中性
    """
    if not j_ok(a, b):
        return 1.0 if not a and not b else 1.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return 2 * inter / (len(a) + len(b))


def j_ok(a, b):
    """Dice 边界判定：JD 侧空 → 中性 1.0；仅简历空 → 0.0"""
    if not a and not b:
        return False  # 双空：中性，外层直接返回 1.0
    if not b:  # JD 侧空：中性（JD 没要求就不罚）
        return False
    return True


def group_score(a, b, metric="dice"):
    if metric == "jaccard":
        return jaccard(a, b)
    if metric == "cover":
        # 纯 JD 覆盖度：JD 要求被简历满足的比例（消融用，非默认）
        if not b:
            return 1.0
        return len(a & b) / len(b)
    # dice（默认）
    if not b:
        return 1.0 if not a else 1.0  # JD 无要求 → 中性
    if not a:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return 2 * inter / (len(a) + len(b))


def make_bge_embed_fn(sim_path=BGE_SIM_PATH):
    """⑥ 向量兜底层：基于 BGE 相似度矩阵的 embed_fn。

    语义分 = 简历技能词与 JD 技能词两两相似度的均值（对称平均）：
      对每个简历词取它与所有 JD 词的最大相似度，再对所有简历词取均值；
      反向同理。两侧取 min，惩罚"简历有但岗位完全不要"的单向匹配。
    """
    with open(sim_path, encoding="utf-8") as f:
        sim = json.load(f)["sim"]

    def embed_fn(r_words, j_words):
        if not r_words or not j_words:
            return 0.0

        def pair(a, b):
            # 矩阵为上三角存储，必须双向查询
            va = sim.get(a, {}).get(b)
            if va is None:
                va = sim.get(b, {}).get(a, 0.0)
            return va

        def one_way(A, B):
            return sum(max(pair(a, b) for b in B) for a in A) / len(A)

        return min(one_way(r_words, j_words), one_way(j_words, r_words))

    return embed_fn


def f1_overlap(a, b):
    """F1 覆盖度：精确率(简历被岗位要求的比例)与召回率(岗位要求被满足的比例)的调和平均。

    比 Jaccard 更抗两侧词数失衡（简历中位 31 词 vs JD 中位 13 词）：
    - Jaccard: |A∩B|/|A∪B|，简历杂词全算分母 → 分数被稀释
    - 单向覆盖: 薄 JD 全覆盖即满分 → 退化
    - F1: 两个方向都约束，且比算术平均更惩罚短板
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    precision = inter / len(a)  # 简历词中多少被岗位认可
    recall = inter / len(b)     # 岗位要求中多少被满足
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def graph_match(resume_graph, jd_graph, embed_fn=None, alpha=0.7):
    """单对匹配打分。返回 (score, detail_dict)

    alpha：清单分权重，向量分权重 = 1 - alpha。None 时走纯清单。
    """
    r_edu = resume_graph.get("education", "本科")
    jd_req = jd_graph.get("hard_requirements", {})
    if not edu_gate(r_edu, jd_req.get("学历", "")):
        return 0.0, {"filtered": "学历门槛"}

    r_skill, r_tool, r_soft = resume_graph_tags(resume_graph)
    j_skill, j_tool, j_soft = jd_graph_tags(jd_graph)
    # 跨组扁平命中（⑤ 诊断）：JD 侧组归属存在系统性错位——
    # AIGC 简历在工具组、JD 在技能组；"沟通/协调/业务理解" JD 在技能组、
    # 简历在软技能组。JD 组词在简历任意组命中即算满足。
    # 权重 0.8/0.2/0：软技能全为通用词（沟通/抗压）不区分族，归零。
    r_all = r_skill | r_tool | r_soft

    s_skill = group_score(r_all, j_skill, metric="cover")
    s_tool = group_score(r_all, j_tool, metric="cover")
    s_soft = group_score(r_all, j_soft, metric="cover")
    list_score = W_SKILL * s_skill + W_TOOL * s_tool + W_SOFT * s_soft

    vec_score = None
    if embed_fn is not None:
        vec_score = 0.7 * embed_fn(r_skill, j_skill) + 0.3 * embed_fn(r_tool, j_tool)
    score = alpha * list_score + (1 - alpha) * vec_score if vec_score is not None else list_score

    # 差距清单：岗位有、简历无（按权重排序专业技能优先）
    gap_skill = sorted(j_skill - r_skill)
    gap_tool = sorted(j_tool - r_tool)
    gap_soft = sorted(j_soft - r_soft)

    detail = {
        "s_skill": round(s_skill, 3), "s_tool": round(s_tool, 3), "s_soft": round(s_soft, 3),
        "score": round(score, 3),
        "gap_专业技能": gap_skill, "gap_工具": gap_tool, "gap_软技能": gap_soft,
        "matched_专业技能": sorted(r_skill & j_skill),
    }
    if vec_score is not None:
        detail["vec_score"] = round(vec_score, 3)
        detail["alpha"] = alpha
    return score, detail


def match_resume_to_all(resume_graph, jd_graphs, jd_meta, embed_fn=None, topn=5, alpha=0.7):
    """一份简历 vs 全部 JD 图谱。返回排序后的 Top-N 列表"""
    scored = []
    for jd_id, jg in jd_graphs.items():
        if jg.get("doc_type") != "jd":
            continue
        meta = jd_meta.get(jd_id, {})
        fam = meta.get("族", "")
        # 负对照隔离：硬核理工负对照族整族出排名池
        # （此前的"零交集才跳过"让弱交集硬核 JD 借薄词表拿满分族中位）
        if any(nf in fam for nf in NEG_FAMS):
            continue
        score, detail = graph_match(resume_graph, jg, embed_fn, alpha=alpha)
        if detail.get("filtered"):
            continue
        scored.append((score, jd_id, fam, meta.get("岗位名称", ""), detail))

    scored.sort(key=lambda t: -t[0])
    return scored[:topn]


def run_eval(jd_graphs, r_graphs, jd_meta, samples, embed_fn=None, alpha=0.7, tag="清单"):
    """统一评测入口：一份代码跑纯清单 / 混合，保证同口径可比"""
    rank_by_layer = defaultdict(lambda: defaultdict(int))
    results = []
    for rid, rg in sorted(r_graphs.items()):
        s = samples.get(rid, {})
        top = match_resume_to_all(rg, jd_graphs, jd_meta, embed_fn=embed_fn, topn=3, alpha=alpha)
        if not top:
            continue
        top1_fam = top[0][2]
        target = s.get("目标族", "")
        # 目标族排名（族级中位分，与基线 baseline_eval.py 口径一致）
        fam_scores = defaultdict(list)
        for score, jd_id, fam, name, detail in match_resume_to_all(
                rg, jd_graphs, jd_meta, embed_fn=embed_fn, topn=len(jd_graphs), alpha=alpha):
            fam_scores[fam].append(score)
        fam_med = {f: sorted(v)[len(v) // 2] for f, v in fam_scores.items()}
        target_score = fam_med.get(target, 0)
        rank = sum(1 for f, v in fam_med.items() if v > target_score) + 1
        rank_by_layer[s.get("层", "?")][rank] += 1
        results.append({
            "id": rid, "层": s.get("层"), "目标族": target, "Top1族": top1_fam,
            "Top3": [{"jd_id": jid, "岗位": name, "族": fam, "score": round(sc, 3)} for sc, jid, fam, name, d in top],
        })
    return rank_by_layer, results


def print_table(title, rank_by_layer):
    print()
    print("=" * 72)
    print(title)
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
    print()
    print("基线（词面重合）: 对口 48% / 迁移 43% / 跨界 20%   ← 要打败的线")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hybrid", action="store_true", help="启用 BGE 向量兜底层（⑥）")
    parser.add_argument("--ablation", action="store_true", help="融合权重 α 消融（1.0/0.7/0.5/0.3）")
    parser.add_argument("--alpha", type=float, default=0.7, help="清单分权重（混合模式用）")
    args = parser.parse_args()

    graphs = load_graphs()
    jd_graphs = {k: v for k, v in graphs.items() if v.get("doc_type") == "jd"}
    r_graphs = {k: v for k, v in graphs.items() if v.get("doc_type") == "resume"}
    print(f"图谱库：JD {len(jd_graphs)} 份，简历 {len(r_graphs)} 份")
    if not jd_graphs or not r_graphs:
        print("图谱库未就绪（需先跑 graph_extractor.py --extract-jd / --extract-resume）")
        return

    jd_meta = load_jd_meta()
    with open(LIST_PATH, encoding="utf-8") as f:
        samples = {s["id"]: s for s in json.load(f)}

    embed_fn = make_bge_embed_fn() if args.hybrid else None
    alpha = 0.7

    if args.ablation and embed_fn is not None:
        ablation = {}
        for a in [1.0, 0.7, 0.5, 0.3]:
            rb, _ = run_eval(jd_graphs, r_graphs, jd_meta, samples, embed_fn, alpha=a)
            n_hit = {L: sum(v for k, v in rb[L].items() if k == 1) for L in rb}
            n_all = {L: sum(rb[L].values()) for L in rb}
            ablation[a] = {L: (n_hit[L] / n_all[L] if n_all[L] else 0) for L in n_all}
            print(f"  α={a}（清单权重） Top1率："
                  + "  ".join(f"{L}{ablation[a][L]:.0%}" for L in ["对口层", "迁移层", "跨界层"] if L in ablation[a]))
        with open(os.path.join(TEMP, "hybrid_ablation.json"), "w", encoding="utf-8") as f:
            json.dump(ablation, f, ensure_ascii=False, indent=1)
        print(f"\n消融已存 {os.path.join(TEMP, 'hybrid_ablation.json')}")
        return

    if embed_fn is not None:
        rank_by_layer, results = run_eval(jd_graphs, r_graphs, jd_meta, samples, embed_fn, args.alpha)
        print_table("⑥ 图谱清单+BGE 向量混合匹配评测（α=%.2f）" % args.alpha, rank_by_layer)
        out_name = "graph_hybrid_report.json"
    else:
        rank_by_layer, results = run_eval(jd_graphs, r_graphs, jd_meta, samples, None)
        print_table("⑤ 图谱清单匹配评测（无向量层）", rank_by_layer)
        out_name = "graph_match_report.json"

    out = {
        "_meta": {"时间": "2026-09-06",
                  "方法": ("混合匹配（清单+向量，α=%.2f）" % args.alpha) if args.hybrid
                          else "图谱清单对齐（Jaccard 加权）",
                  "基线": "对口48%/迁移43%/跨界20%"},
        "分层排名分布": {layer: {f"第{k}名": v for k, v in sorted(c.items())}
                        for layer, c in rank_by_layer.items()},
        "逐份明细": results,
    }
    with open(os.path.join(TEMP, out_name), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"\n明细已存 {os.path.join(TEMP, out_name)}")


if __name__ == "__main__":
    main()
