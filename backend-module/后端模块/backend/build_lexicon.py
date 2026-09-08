# -*- coding: utf-8 -*-
"""
P1-1: 135 份 meta.json → 专业-能力关键词词表 v0
从 seo_keywords / seo_description / roles / tags_cn 提取技能词与专业词，按专业族聚合
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\新国赛\.temp\wondercv-templates")
OUT = Path(r"D:\新国赛\简历语料\专业能力词表v0.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

# 专业归一化规则（从模板名/desc 中识别专业族）
MAJOR_PATTERNS = {
    "汉语言文学": ["汉语言", "中文系", "新闻", "传播学", "广告学", "编辑出版"],
    "市场营销": ["市场营销", "营销策划", "市场推广", "品牌", "销售管理", "网络营销"],
    "财务管理": ["财务管理", "会计", "审计", "金融", "经济学", "财政", "税务", "财务"],
    "电子商务": ["电子商务", "电商", "跨境", "外贸", "国际商务", "国际贸易"],
    "人力资源管理": ["人力资源", "HR", "人事", "薪酬", "绩效管理"],
    "行政管理": ["行政助理", "行政专员", "文秘", "秘书学", "办公室"],
    "视觉传达": ["视觉传达", "平面设计", "美术学", "艺术设计", "UI设计", "美工"],
    "英语/外语": ["英语专业", "翻译", "商务英语", "日语", "韩语", "法语", "小语种"],
    "计算机": ["计算机", "软件工程", "信息管理", "数据科学", "大数据", "人工智能"],
    "护理": ["护理学", "护士", "临床医学", "药学", "卫生"],
    "数学/统计": ["数学", "统计学", "应用统计", "精算", "数理"],
    "法学": ["法律", "法学", "律师", "知识产权"],
    "教育/师范": ["师范", "教育学", "学前教育", "小学教育", "教育技术", "教师"],
    "旅游管理": ["旅游管理", "酒店管理", "会展", "导游"],
    "物流管理": ["物流管理", "供应链", "采购", "仓储"],
}

# 技能词抽取（从 seo_keywords 等文本提取，词表驱动）
SKILL_WORDS = [
    # 通用办公
    "Office", "Word", "Excel", "PPT", "Outlook", "WPS", "Office技能", "办公软件",
    # 语言
    "CET-4", "CET-6", "英语四级", "英语六级", "英语", "普通话", "日语", "韩语", "法语",
    # 数据类
    "Python", "SPSS", "SQL", "MySQL", "Tableau", "Power BI", "数据分析", "数据可视化",
    "Excel VBA", "R语言", "MATLAB", "SAS",
    # 设计类
    "Photoshop", "PS", "Illustrator", "AI", "InDesign", "Premiere", "AE", "After Effects",
    "CorelDRAW", "Sketch", "Figma", "C4D", "CAD", "视频剪辑", "摄影",
    # 营销类
    "新媒体运营", "社群运营", "私域运营", "SEO", "SEM", "信息流投放", "内容营销", "整合营销",
    "品牌策划", "营销策划", "文案", "活动策划", "直播运营", "短视频运营", "电商运营",
    "跨境电商", "亚马逊运营", "TikTok运营", "用户增长", "数据分析能力",
    # 管理类
    "项目管理", "沟通协调能力", "组织协调能力", "问题解决能力", "抗压能力", "团队协作",
    "领导力", "时间管理", "执行力",
    # 财务类
    "会计从业资格", "初级会计", "中级会计", "CPA", "税务", "财务分析", "Excel财务建模",
    "用友", "金蝶", "SAP",
    # 人事行政（“招聘/培训”在 seo_keywords 里是通用话术、无锚定价值，不收）
    "薪酬绩效", "公文写作", "行政管理",
    # 教育类
    "教师资格证", "普通话二级甲等", "教学法", "课件制作",
    # 新质技能（重点——边界样本的核心素材）
    "AIGC", "AI工具", "ChatGPT", "Prompt工程", "大模型", "提示词工程", "Midjourney",
    "Stable Diffusion", "AI绘画", "AI写作", "数据思维",
    "碳管理", "碳中和", "绿色金融", "可持续发展", "新能源",
]

major_stats = defaultdict(lambda: {"count": 0, "skills": defaultdict(int), "sources": []})
misc_skills = defaultdict(int)

metas = list(ROOT.rglob("meta.json"))
for mp in metas:
    try:
        meta = json.loads(mp.read_text(encoding="utf-8"))
    except Exception:
        continue
    text = " ".join(filter(None, [
        meta.get("name", ""), meta.get("desc", ""), meta.get("seo_description", "") or "",
        meta.get("seo_keywords", "") or "",
        " ".join(meta.get("roles") or []), " ".join(meta.get("tags_cn") or []),
    ]))
    # 归专业：只用模板名+desc（强专业信号区），且排除“招聘/简历模板”等通用话术干扰
    name_text = (meta.get("name", "") + " " + (meta.get("desc") or "")[:60])
    name_text = re.sub(r"(社会招聘|校招|招聘经理|招聘|简历模板|简历|大学生|应届生|社招|跳槽|求职|个人简历|经验)", "", name_text)
    matched_major = None
    for major, pats in MAJOR_PATTERNS.items():
        if any(p in name_text for p in pats):
            matched_major = major
            break
    if matched_major is None:
        # 岗位名→专业族的兜底映射（岗位模板的专业信号）
        JOB_MAJOR = {
            "运营": "市场营销", "产品": "电子商务", "市场": "市场营销", "销售": "市场营销",
            "设计": "视觉传达", "插画": "视觉传达", "动画": "视觉传达", "UI": "视觉传达", "UX": "视觉传达",
            "文员": "行政管理", "行政": "行政管理", "秘书": "行政管理",
            "翻译": "英语/外语", "护理": "护理", "前端": "计算机", "开发": "计算机",
            "咨询": "财务管理", "财务": "财务管理", "会计": "财务管理",
        }
        for jk, mv in JOB_MAJOR.items():
            if jk in name_text:
                matched_major = mv
                break
    # 提技能词
    found = []
    for w in SKILL_WORDS:
        if w.lower() in text.lower():
            found.append(w)
    if matched_major:
        major_stats[matched_major]["count"] += 1
        for w in found:
            major_stats[matched_major]["skills"][w] += 1
        major_stats[matched_major]["sources"].append(meta.get("name", "")[:30])
    else:
        for w in found:
            misc_skills[w] += 1

# 输出
result = {
    "_meta": {
        "来源": "WonderCV 135 份模板 meta.json 聚合",
        "用途": "简历合成时按专业注入能力关键词；词频代表该专业模板生态中的常见度",
        "生成时间": "2026-09-05",
        "专业识别数": len(major_stats),
    },
    "专业词表": {
        major: {
            "模板数": v["count"],
            "高频技能(≥3次)": sorted([w for w, n in v["skills"].items() if n >= 3], key=lambda w: -v["skills"][w]),
            "全部技能": sorted(v["skills"].keys(), key=lambda w: -v["skills"][w]),
        }
        for major, v in sorted(major_stats.items(), key=lambda kv: -kv[1]["count"])
    },
    "未归专业通用词池": sorted(misc_skills.items(), key=lambda t: -t[1])[:60],
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

# 摘要打印
print("专业族数:", len(major_stats))
for major, v in sorted(major_stats.items(), key=lambda kv: -kv[1]["count"]):
    top = [f"{w}x{n}" for w, n in sorted(v["skills"].items(), key=lambda t: -t[1])[:6]]
    print(f"  {major}（{v['count']}模板）: {', '.join(top) if top else '无技能词'}")
