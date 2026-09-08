# -*- coding: utf-8 -*-
"""
匹配系统 ② 能力图谱抽取器 v1.0
把 JD（xlsx 行）或简历（txt）翻译成统一 Schema 的能力图谱 JSON。

设计要点：
1. 大模型：智谱 GLM-4.7-Flash（永久免费），OpenAI 兼容协议
2. key 空白制：API_KEY 为空时直接报错并提示去 README 看申请方法，不内置任何 key
3. 断点缓存：以 doc_id 为键存 .temp/graph_cache/，重跑不花钱
4. 词表锚定：system 消息注入锚定词表（106 词），要求表外词归一或丢弃
5. 格式校验：JSON 解析失败/缺字段/表外词比例过高 → 标记坏样本，单独重抽
6. 限速：默认 1.5s/次，友好调用

用法：
  python graph_extractor.py --selftest        # 自检（不调 API，用假数据走全流程）
  python graph_extractor.py --test-key        # 验证 key 可用性（调 1 次）
  python graph_extractor.py --extract-jd      # 批量抽 359 条 JD（需要 key）
  python graph_extractor.py --extract-resume  # 批量抽 100 份简历（需要 key）
  python graph_extractor.py --status          # 查看缓存进度
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

BASE = r"D:\新国赛"
CACHE_DIR = os.path.join(BASE, r".temp\graph_cache")
ANCHOR_PATH = os.path.join(BASE, r".temp\anchor_lexicon.json")
JD_XLSX = os.path.join(BASE, "jd_data.xlsx")
BOSS_XLSX = os.path.join(BASE, r"简历语料\boss_AIGC补充24条.xlsx")
RESUME_DIR = os.path.join(BASE, r"简历语料\合成简历库")
LIST_PATH = os.path.join(BASE, r"简历语料\合成样本清单.json")

# ============ 智谱 API 配置（key 空白制，任何人自己申请） ============
API_KEY = ""   # ← 队长/队员自己申请后填这里，或环境变量 ZHIPU_API_KEY
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"   # 智谱永久免费档（2026-09-06 实测可用；glm-4.7-flash 该 key 下超时）

REQ_INTERVAL = 1.5  # 秒/请求
MAX_RETRIES = 3
TABLE_TOLERANCE = 0.2  # 允许 20% 表外词（归一化失败视为模型善意补充，降级容忍）

# ============ Prompt（与 graph_schema.json 同步） ============

PROMPT_JD = """你是招聘信息结构化专家。从下面的岗位描述中抽取能力图谱，输出严格的 JSON。

锚定词表（技能/工具/软技能必须从中选择）：
{anchor}

硬规则：
1) 每个技能词必须是词表中的原子词（2-8字），从词表里直接挑，一个一个挑
2) 禁止把岗位描述里的整句话当技能词（如“熟练掌握XX工具”应只提取“XX”对应的表内词）
3) 表里实在没有对应词的技能，直接丢弃，不要自创
4) 同一个数组内严禁出现重复词，每个数组最多 15 项，输出前自查一遍

岗位描述：
{doc}

输出格式（只输出 JSON，不要任何其他文字）：
{{"hard_requirements": {{"学历": "", "经验年限": 0, "专业限制": "", "证书": []}}, "skill_groups": {{"专业技能": [], "工具": [], "软技能": []}}, "evidence": {{}}}}
其中 evidence 的键为技能名，值为原文证据短语（≤30字）。"""

PROMPT_RESUME = """你是简历结构化专家。从下面的简历文本中抽取能力图谱，输出严格的 JSON。

锚定词表（技能/工具/软技能必须从中选择）：
{anchor}

硬规则：
1) 每个技能词必须是词表中的原子词（2-8字），从词表里直接挑，一个一个挑
2) 禁止把简历里的整句话当技能词
3) 表里实在没有对应词的技能，直接丢弃，不要自创

简历文本：
{doc}

输出格式（只输出 JSON，不要任何其他文字）：
{{"education": "", "skill_groups": {{"专业技能": [], "工具": [], "软技能": []}}, "evidence": {{}}}}
其中 education 填 本科|硕士|博士|大专；evidence 的键为技能名，值为简历原文证据短语（≤30字）。"""


def get_api_key():
    key = API_KEY or os.environ.get("ZHIPU_API_KEY", "")
    if not key:
        print("✗ 未配置 API key。两种方式：")
        print("  1. 编辑本文件顶部 API_KEY = \"你的key\"")
        print("  2. 环境变量 ZHIPU_API_KEY")
        print("申请方法见 README（免费，约 5 分钟）：智谱开放平台 → 注册 → API Keys")
        sys.exit(2)
    return key


def load_anchor():
    with open(ANCHOR_PATH, encoding="utf-8") as f:
        return set(json.load(f)["锚定词表"])


def call_llm(prompt, key):
    """调智谱 chat API，返回文本"""
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 1500,
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + key,
    }
    req = urllib.request.Request(API_URL, data=payload, headers=headers, method="POST")
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")[:300]
            except Exception:
                pass
            last_err = f"HTTP {e.code}: {body}"
            if e.code in (429, 500, 502, 503):
                time.sleep(3 * attempt)  # 限流/服务波动，退避重试
            else:
                break  # 401 等，重试无意义
        except Exception as e:
            last_err = repr(e)
            time.sleep(2)
    raise RuntimeError(f"API 调用失败（重试{MAX_RETRIES}次）: {last_err}")


def _close_truncated_json(frag):
    """截断 JSON 自动闭合：删掉不完整尾串，按未闭合栈序补齐括号"""
    # 1) 引号数为奇数 → 末尾有不完整字符串，删到最后一个引号前
    if frag.count('"') % 2 == 1:
        frag = frag[:frag.rfind('"')]
    # 2) 栈扫描找未闭合结构
    stack, in_str, esc = [], False, False
    for ch in frag:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if stack:
                stack.pop()
    # 3) 截到最后一个完整元素边界（逗号），避免尾部残片
    k = frag.rfind(",")
    if k > 0:
        frag = frag[:k]
    # 4) 补齐闭合符（倒序），再修一遍 trailing comma
    frag += "".join("]" if c == "[" else "}" for c in reversed(stack))
    return re.sub(r",(\s*[}\]])", r"\1", frag)


def parse_json_sloppy(text):
    """宽容解析：剥 ``` 包裹 → 完整解析 / trailing comma / 截断前缀自动闭合"""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    i, j = text.find("{"), text.rfind("}")
    if i < 0:
        raise ValueError("未找到 JSON")
    # 候选片段：完整截取 + 截断前缀（rfind 的 } 可能是中间对象的闭合）
    candidates = []
    if j > i:
        candidates.append(text[i:j + 1])
    candidates.append(text[i:])
    last_err = None
    for frag in candidates:
        for repair in (lambda s: s,
                       lambda s: re.sub(r",(\s*[}\]])", r"\1", s),
                       _close_truncated_json):
            try:
                return json.loads(repair(frag))
            except json.JSONDecodeError as e:
                last_err = e
    raise ValueError(f"JSON 三级修复均失败: {last_err}")


def _word_pat(word):
    """英文短词带词边界，中文子串（与 P5 口径一致）"""
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9\+\.\-]{0,9}", word):
        return re.compile(r"(?<![A-Za-z0-9])" + re.escape(word) + r"(?![A-Za-z0-9])", re.IGNORECASE)
    return re.compile(re.escape(word))


_PAT_CACHE = {}

def normalize_skills(phrases, anchor):
    """归一化：模型输出的短语 → 其中包含的锚定表内词（确定性后处理，不重新调 API）
    例："熟练使用SQL语言进行复杂统计" → {"SQL"}；"SAS" → {"SAS"}"""
    out = set()
    for item in phrases:
        s = str(item).strip()
        if not s:
            continue
        if s in anchor:
            out.add(s)
            continue
        for w in anchor:
            p = _PAT_CACHE.get(w)
            if p is None:
                p = _PAT_CACHE[w] = _word_pat(w)
            if p.search(s):
                out.add(w)
    return sorted(out)


def normalize_graph(raw, anchor):
    """把整个图谱的三个技能组全部归一化到锚定词表，并重织 evidence"""
    sg = raw.get("skill_groups") or {}
    ev = raw.get("evidence") or {}
    new_sg, new_ev = {}, {}
    for gname in ("专业技能", "工具", "软技能"):
        words = normalize_skills(sg.get(gname) or [], anchor)
        new_sg[gname] = words
        for w in words:
            if w in new_ev:
                continue
            src = None
            for k, v in ev.items():
                if w in str(k) or (v and w in str(v)):
                    src = str(v or k)[:30]
                    break
            new_ev[w] = src or w
    raw["skill_groups"] = new_sg
    raw["evidence"] = new_ev
    return raw

def validate_graph(raw, anchor, doc_type):
    """校验抽取结果（归一化后）：结构、字段、非空性。返回 (graph, problems)"""
    problems = []
    if doc_type == "jd":
        req_fields = ["hard_requirements", "skill_groups"]
    else:
        req_fields = ["education", "skill_groups"]
    for f in req_fields:
        if f not in raw:
            problems.append(f"缺字段 {f}")
    if problems:
        return raw, problems
    sg = raw.get("skill_groups") or {}
    total_words = sum(len(sg.get(g) or []) for g in ("专业技能", "工具", "软技能"))
    if total_words == 0:
        problems.append("归一化后技能组全空（短语未含任何表内词）")
    return raw, problems


def extract_one(doc_id, doc_text, doc_type, key, anchor, quiet=False):
    """抽取单文档并缓存。返回 (status, graph)"""
    cache_path = os.path.join(CACHE_DIR, f"{doc_id}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                return "cached", json.load(f)
        except Exception:
            pass  # 缓存坏，重抽

    tpl = PROMPT_JD if doc_type == "jd" else PROMPT_RESUME
    prompt = tpl.format(anchor="、".join(sorted(anchor)), doc=doc_text[:6000])
    raw_text = call_llm(prompt, key)
    try:
        raw = parse_json_sloppy(raw_text)
    except Exception as e:
        mark_bad(doc_id, f"JSON解析失败: {e}", raw_text)
        return "bad_json", None
    raw = normalize_graph(raw, anchor)   # 确定性归一化：短语→表内词
    graph, problems = validate_graph(raw, anchor, doc_type)
    if problems:
        mark_bad(doc_id, "; ".join(problems), raw_text)
        return "bad_schema", None
    graph["doc_id"] = doc_id
    graph["doc_type"] = doc_type
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=1)
    return "ok", graph


def mark_bad(doc_id, reason, raw_text):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(os.path.join(CACHE_DIR, f"{doc_id}.bad.txt"), "w", encoding="utf-8") as f:
        f.write(f"原因: {reason}\n\n原文返回:\n{raw_text}")


def load_jd_docs():
    """359 条 JD → [(doc_id, 文本)]"""
    from openpyxl import load_workbook
    docs = []
    for path, label in [(JD_XLSX, "国聘"), (BOSS_XLSX, "Boss")]:
        wb = load_workbook(path, read_only=True)
        ws = wb[wb.sheetnames[0]]
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
        header_idx = None
        for i, row in enumerate(rows):
            if row and row[0] == "jd_id":
                header_idx = i
                break
        col = {h: i for i, h in enumerate(rows[header_idx])}
        for row in rows[header_idx + 1:]:
            if not row or not row[0]:
                continue
            text = f"岗位名称：{row[col['岗位名称']]}\n学历要求：{row[col['学历要求']]}\n岗位描述：\n{row[col['JD原文']]}"
            docs.append((str(row[col["jd_id"]]), text))
    return docs


def load_resume_docs():
    """100 份简历 → [(doc_id, 文本)]（doc_id = S001..S100）"""
    docs = []
    for fname in sorted(os.listdir(RESUME_DIR)):
        if fname.endswith(".txt"):
            with open(os.path.join(RESUME_DIR, fname), encoding="utf-8") as f:
                docs.append((fname.split("_")[0], f.read()))
    return docs


def batch_extract(docs, doc_type, key, anchor, workers=3):
    """批量抽取：线程池并发 + 进度打印 + 断点续跑 + 坏样本统计
    workers=3：免费档单次生成约 27s，3 路温和并发 → 约 8s/条，全程约 50 分钟"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    stats = {"ok": 0, "cached": 0, "bad_json": 0, "bad_schema": 0, "fail": 0}
    lock = threading.Lock()
    n = len(docs)
    done = 0
    t0 = time.time()

    def work(item):
        doc_id, text = item
        try:
            return doc_id, extract_one(doc_id, text, doc_type, key, anchor)
        except RuntimeError as e:
            return doc_id, ("fail", str(e))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(work, item) for item in docs]
        for fut in as_completed(futures):
            doc_id, result = fut.result()
            status = result[0] if isinstance(result, tuple) else result
            with lock:
                stats[status] = stats.get(status, 0) + 1
                done += 1
                if done % 10 == 0 or done == n:
                    dt = time.time() - t0
                    eta = dt / done * (n - done)
                    print(f"[{done}/{n}] ok={stats['ok']} cached={stats['cached']} "
                          f"bad={stats['bad_json'] + stats['bad_schema']} fail={stats.get('fail', 0)} "
                          f"已用 {dt/60:.1f}min 预计剩余 {eta/60:.1f}min", flush=True)
    print(f"\n完成：ok={stats['ok']} cached={stats['cached']} "
          f"bad_json={stats['bad_json']} bad_schema={stats['bad_schema']} fail={stats.get('fail', 0)}")
    print(f"缓存目录：{CACHE_DIR}")


def cmd_status():
    os.makedirs(CACHE_DIR, exist_ok=True)
    files = os.listdir(CACHE_DIR)
    ok = [f for f in files if f.endswith(".json")]
    bad = [f for f in files if f.endswith(".bad.txt")]
    print(f"缓存目录 {CACHE_DIR}")
    print(f"  成功图谱: {len(ok)} 个")
    print(f"  坏样本:   {len(bad)} 个")
    if bad:
        print("  坏样本列表（重抽：删掉 .bad.txt 再跑批量命令即可）:")
        for f in bad[:10]:
            print(f"    {f}")
    if ok:
        with open(os.path.join(CACHE_DIR, ok[0]), encoding="utf-8") as f:
            print("\n最近缓存样例：")
            print(json.dumps(json.load(f), ensure_ascii=False, indent=1)[:600])


def cmd_test_key():
    key = get_api_key()
    print(f"测试 key（模型 {MODEL}）...")
    try:
        out = call_llm('只输出两个字："好的"', key)
        print("✓ key 可用，模型返回:", out.strip()[:50])
    except Exception as e:
        print("✗ key 不可用:", e)
        print("排查：1) key 是否复制完整 2) 智谱控制台是否有欠费/限流 3) 模型名是否下线")
        sys.exit(1)


def cmd_selftest():
    """不调 API 的自检：假数据走全流程（校验/缓存/读取）"""
    anchor = load_anchor()
    print(f"1) 锚定词表加载: {len(anchor)} 词 ✓")
    fake_jd = {"hard_requirements": {"学历": "本科", "经验年限": 0, "专业限制": "无", "证书": []},
               "skill_groups": {"专业技能": ["Python", "数据分析"], "工具": ["Excel"], "软技能": ["沟通"]},
               "evidence": {"Python": "熟练使用 Python", "数据分析": "负责数据分析工作"}}
    g, problems = validate_graph(fake_jd, anchor, "jd")
    print(f"2) 合法 JD 图谱校验: {'✓ 通过' if not problems else '✗ ' + str(problems)}")
    fake_bad = {"hard_requirements": {"学历": "本科", "经验年限": 0, "专业限制": "无", "证书": []},
                "skill_groups": {"专业技能": ["量子炼丹术", "赛博修仙", "Python"], "工具": [], "软技能": []}}
    g, problems = validate_graph(fake_bad, anchor, "jd")
    ok_reject = any("表外词" in p for p in problems)
    print(f"3) 表外词拒检: {'✓ 正确拒绝' if ok_reject else '✗ 未拦截'} -> {problems}")
    print(f"4) JD 加载: {len(load_jd_docs())} 条 ✓")
    print(f"5) 简历加载: {len(load_resume_docs())} 份 ✓")
    print("自检通过。批量抽取前先跑 --test-key 验证 key。")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--test-key", action="store_true")
    ap.add_argument("--extract-jd", action="store_true")
    ap.add_argument("--extract-resume", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        cmd_selftest()
        return
    if args.test_key:
        cmd_test_key()
        return
    if args.status:
        cmd_status()
        return
    if args.extract_jd or args.extract_resume:
        key = get_api_key()
        anchor = load_anchor()
        if args.extract_jd:
            docs = load_jd_docs()
            doc_type = "jd"
        else:
            docs = load_resume_docs()
            doc_type = "resume"
        print(f"批量抽取 {doc_type}：{len(docs)} 个文档，限速 {REQ_INTERVAL}s/次")
        batch_extract(docs, doc_type, key, anchor)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
