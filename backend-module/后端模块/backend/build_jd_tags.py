# -*- coding: utf-8 -*-
"""
P1-3: 从 299 条 JD 提取能力标签体系
1) 按族统计技能词出现率（硬技能词表 + 软技能词表）
2) 学历/经验要求分布
3) 输出: JD能力标签体系.json —— 族×技能 出现率矩阵
"""
import json
import re
from collections import defaultdict
from pathlib import Path

# xlsx 读取用 openpyxl
import openpyxl

WB = Path(r"D:\新国赛\jd_data.xlsx")
OUT = Path(r"D:\新国赛\简历语料\JD能力标签体系.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

wb = openpyxl.load_workbook(WB, read_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0])
print("字段:", header)

# AIGC 水印行过滤 + 列定位
data = []
for r in rows[1:]:
    if r[0] and str(r[0]).startswith("AIGC"):
        continue
    data.append(dict(zip(header, r)))
print(f"JD 条数: {len(data)}")

# 硬技能词表（按域分组，从 JD 高频词汇聚）
SKILL_GROUPS = {
    "编程/数据": ["Python", "SQL", "Java", "C++", "R语言", "SPSS", "MATLAB", "Scala",
               "数据分析", "数据挖掘", "数据清洗", "数据可视化", "统计分析", "机器学习",
               "深度学习", "大模型", "LLM", "Prompt", "提示词", "AIGC", "NLP", "算法",
               "数据建模", "ETL", "Hive", "Spark", "Hadoop", "Tableau", "Power BI"],
    "办公/协同": ["Excel", "PPT", "Office", "Word", "WPS", "Visio", "Axure", "飞书", "钉钉", "数据分析能力"],
    "营销/运营": ["新媒体运营", "内容运营", "用户运营", "社群运营", "私域", "抖音", "小红书", "视频号",
               "直播", "短视频", "文案", "创意", "投放", "信息流", "SEO", "SEM", "ROI",
               "GMV", "转化率", "用户增长", "品牌", "营销策划", "亚马逊", "TikTok", "跨境电商",
               "选品", "Listing", "店铺运营", "海外社媒", "KOL", "KOC"],
    "设计/内容": ["Photoshop", "PS", "AI绘画", "Midjourney", "Stable Diffusion", "Canva", "剪辑",
               "Premiere", "AE", "Figma", "Sketch", "视觉设计", "平面设计", "视频剪辑"],
    "制造/工程": ["CAD", "SolidWorks", "CATIA", "UG", "Pro/E", "PLC", "自动化产线", "工业机器人",
               "MES", "ERP", "精益生产", "六西格玛", "IE", "工艺", "工装", "数控", "仿真",
               "ANSYS", "数字孪生", "MES系统", "产线设计", "设备管理"],
    "能源/双碳": ["碳中和", "碳达峰", "碳管理", "碳核算", "ESG", "双碳", "光伏", "风电", "储能",
               "锂电池", "氢能", "新能源汽车", "充电桩", "电池", "能源管理", "节能", "绿色", "可持续发展", "环保"],
    "管理/通用": ["项目管理", "PMP", "敏捷", "OKR", "跨部门", "沟通", "协调", "抗压", "执行力",
               "学习能力", "责任心", "团队合作", "英语", "英语四级", "英语六级", "CET", "六级",
               "数据分析", "报告撰写", "PPT制作", "流程优化", "业务理解", "0-1"],
}
ALL_SKILLS = {w: g for g, ws_ in SKILL_GROUPS.items() for w in ws_}

# 族名（采集时的 8 族）
FAMILY_COL = "岗位类别"  # 采集时设计的 8 族字段
assert FAMILY_COL in header, f"找不到族字段: {header}"

family_stats = defaultdict(lambda: {"n": 0, "skills": defaultdict(int), "edu": defaultdict(int)})
# 英文短词需词边界匹配（IE/PS/AE 会误匹配在英文单词内部）
SHORT_EN = {"IE", "PS", "AE", "CAD", "ETL", "ERP", "MES", "LLM", "NLP", "ROI", "GMV", "SEO", "SEM", "KOL", "KOC", "CET", "0-1"}
import re as _re
for d in data:
    fam = str(d.get(FAMILY_COL) or "未知")
    # 只用岗位名称+JD原文；不拼行业/公司字段（行业词会造成系统性误匹配）
    text = str(d.get("岗位名称") or "") + "\n" + str(d.get("JD原文") or "")
    family_stats[fam]["n"] += 1
    for w in ALL_SKILLS:
        if w in SHORT_EN:
            hit = bool(_re.search(rf"(?<![A-Za-z0-9]){_re.escape(w)}(?![A-Za-z0-9])", text))
        else:
            hit = w in text
        if hit:
            family_stats[fam]["skills"][w] += 1
    edu = str(d.get("学历要求") or "")
    for e in ["本科", "硕士", "大专", "不限", "博士"]:
        if e in edu:
            family_stats[fam]["edu"][e] += 1
            break

# 出现率矩阵
result = {
    "_meta": {
        "来源": "D:\\新国赛\\jd_data.xlsx 299 条 JD 全文扫描",
        "用途": "① 简历合成时保证技能词与 JD 同词空间 ② 匹配系统的岗位能力图谱基线",
        "技能分组": {g: len(ws_) for g, ws_ in SKILL_GROUPS.items()},
        "生成时间": "2026-09-05",
    },
    "族×技能出现率": {},
}
for fam, st in sorted(family_stats.items()):
    rates = {w: round(n / st["n"], 3) for w, n in st["skills"].items()}
    top = dict(sorted(rates.items(), key=lambda t: -t[1])[:25])
    result["族×技能出现率"][fam] = {
        "JD数": st["n"],
        "TOP25技能(出现率)": top,
        "学历要求": dict(st["edu"]),
    }
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

# 摘要
for fam, st in sorted(family_stats.items()):
    top = sorted(st["skills"].items(), key=lambda t: -t[1])[:10]
    top_s = ", ".join(f"{w}({n/st['n']:.0%})" for w, n in top)
    print(f"\n【{fam}】{st['n']}条 | 学历: {dict(st['edu'])}")
    print(f"  TOP技能: {top_s}")
