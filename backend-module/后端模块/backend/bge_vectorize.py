# -*- coding: utf-8 -*-
"""
匹配系统 ⑥ BGE 向量层：锚定词表全量向量化 + 语义相似度矩阵
硅基流动 BAAI/bge-large-zh-v1.5（免费，1024 维）

做什么：
1. 把 106 个锚定词全部向量化（一次 106 词，硅基流动 embeddings 接口支持批量，1 次调用搞定）
2. 计算词×词余弦相似度矩阵，存盘（词义距离表）
3. 匹配算法的 embed_fn 直接读这张表：简历技能词 vs 岗位技能词的语义相似度
   → "爬虫开发"≈"Python" 这类换说法的匹配靠它兜底

不花钱：bge-large-zh-v1.5 在硅基流动免费名单；且结果全量缓存，重跑零调用。
"""
import json
import os
import sys
import urllib.request

BASE = r"D:\新国赛"
CACHE_DIR = os.path.join(BASE, r".temp\graph_cache")
ANCHOR_PATH = os.path.join(BASE, r".temp\anchor_lexicon.json")
VEC_PATH = os.path.join(BASE, r".temp\bge_vectors.json")
SIM_PATH = os.path.join(BASE, r".temp\bge_sim_matrix.json")

API_URL = "https://api.siliconflow.cn/v1/embeddings"
MODEL = "BAAI/bge-large-zh-v1.5"

# key 空白制：环境变量 SILICONFLOW_API_KEY
API_KEY = ""


def get_key():
    key = API_KEY or os.environ.get("SILICONFLOW_API_KEY", "")
    if not key:
        print("✗ 未配置硅基流动 key：环境变量 SILICONFLOW_API_KEY")
        sys.exit(2)
    return key


def embed_batch(texts, key):
    """批量向量化（单批 ≤ 64 词，超出自动分批）"""
    vecs = []
    for i in range(0, len(texts), 64):
        batch = texts[i:i + 64]
        payload = json.dumps({"model": MODEL, "input": batch}).encode("utf-8")
        req = urllib.request.Request(API_URL, data=payload, headers={
            "Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read().decode("utf-8"))
                vecs.extend([d["embedding"] for d in data["data"]])
                break
            except Exception as e:
                if attempt == 2:
                    raise RuntimeError(f"embedding 调用失败: {e}")
    return vecs


def cosine(a, b):
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def main():
    key = get_key()

    with open(ANCHOR_PATH, encoding="utf-8") as f:
        words = json.load(f)["锚定词表"]
    print(f"锚定词表 {len(words)} 词")

    # 1) 向量化（缓存优先）
    if os.path.exists(VEC_PATH):
        with open(VEC_PATH, encoding="utf-8") as f:
            cached = json.load(f)
        if len(cached) == len(words):
            print("向量缓存命中，零 API 调用")
            vec_map = cached
        else:
            vec_map = None
    else:
        vec_map = None
    if vec_map is None:
        print("调用 BGE 批量向量化（1-2 次调用）...")
        vecs = embed_batch(words, key)
        vec_map = {w: v for w, v in zip(words, vecs)}
        with open(VEC_PATH, "w", encoding="utf-8") as f:
            json.dump(vec_map, f, ensure_ascii=False)
        print(f"已缓存到 {VEC_PATH}")

    # 2) 相似度矩阵（纯本地计算）
    print("计算词×词相似度矩阵（本地）...")
    sim = {}
    for i, wa in enumerate(words):
        row = {}
        for wb in words[i + 1:]:
            row[wb] = round(cosine(vec_map[wa], vec_map[wb]), 4)
        sim[wa] = row
    with open(SIM_PATH, "w", encoding="utf-8") as f:
        json.dump({"_meta": {"模型": MODEL, "维度": 1024, "词数": len(words),
                             "生成时间": "2026-09-06"}, "sim": sim}, f, ensure_ascii=False)
    print(f"已存 {SIM_PATH}")

    # 3) 快速体检：抽几对词看语义距离是否符合直觉
    print()
    print("语义体检（应相似的对 vs 应疏远的对）：")
    def s(a, b):
        return sim.get(a, {}).get(b) or sim.get(b, {}).get(a, 0)
    for a, b, expect in [
        ("Python", "Java", "近（都是编程语言）"),
        ("数据分析", "SQL", "近（数据分析常用 SQL）"),
        ("短视频", "剪辑", "近（内容制作链）"),
        ("Excel", "Figma", "远（办公 vs 设计）"),
        ("Python", "ESG", "远（编程 vs 双碳概念）"),
    ]:
        v = s(a, b) if (a in words and b in words) else None
        if v is not None:
            print(f"  {a} × {b}: {v:.3f}  期望:{expect}")
        else:
            print(f"  {a} × {b}: 词表缺词，跳过")

    # 找出与"数据分析"最相似的 8 个词
    if "数据分析" in sim:
        near = sorted(sim["数据分析"].items(), key=lambda kv: -kv[1])[:8]
        print("\n与「数据分析」最相似的词：")
        for w, v in near:
            print(f"  {w}: {v:.3f}")


if __name__ == "__main__":
    main()
