# -*- coding: utf-8 -*-
"""智职图谱一体化演示服务

把后端模块（图谱缓存 + graph_match.py 匹配算法）包装为 HTTP API，
同时托管 frontend-prototype 静态页面。启动后访问 http://127.0.0.1:8000

运行方式：
    python backend-integration/server.py

不依赖 FastAPI/Flask，只使用 Python 标准库 + openpyxl。
"""
import json
import io
import mimetypes
import os
import re
import sys
import time
import urllib.parse
from xml.sax.saxutils import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

INTEGRATION_DIR = Path(__file__).resolve().parent
ROOT_DIR = INTEGRATION_DIR.parent
MODULE_DIR = ROOT_DIR / "backend-module" / "后端模块"
BACKEND_DIR = MODULE_DIR / "backend"
CACHE_DIR = BACKEND_DIR / "graph_cache"
FRONTEND_DIR = ROOT_DIR / "frontend-prototype"
SAMPLE_PATH = MODULE_DIR / "简历语料" / "合成样本清单.json"


def load_local_env():
    """读取 backend-integration/.env，不打印 Key 内容。"""
    env_path = INTEGRATION_DIR / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


load_local_env()

sys.path.insert(0, str(BACKEND_DIR))
from graph_match import graph_match  # noqa: E402
import graph_extractor as extractor  # noqa: E402


def configure_extractor_paths():
    extractor.BASE = str(MODULE_DIR)
    extractor.CACHE_DIR = str(CACHE_DIR)
    extractor.ANCHOR_PATH = str(BACKEND_DIR / "anchor_lexicon.json")
    extractor.JD_XLSX = str(MODULE_DIR / "jd_data.xlsx")
    extractor.BOSS_XLSX = str(MODULE_DIR / "简历语料" / "boss_AIGC补充24条.xlsx")
    extractor.RESUME_DIR = str(MODULE_DIR / "简历语料" / "合成简历库")
    extractor.LIST_PATH = str(MODULE_DIR / "简历语料" / "合成样本清单.json")

HOST = os.environ.get("INTEGRATION_HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT") or os.environ.get("INTEGRATION_PORT") or "8000")
CHINESE_FONT_NAME = "SimHei"


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_cache_graphs():
    graphs = {}
    if not CACHE_DIR.is_dir():
        return graphs
    for path in CACHE_DIR.glob("*.json"):
        try:
            graph = read_json(path)
        except Exception:
            continue
        graphs[graph.get("doc_id")] = graph
    return graphs


def xlsx_rows(path):
    from openpyxl import load_workbook
    workbook = load_workbook(path, read_only=True)
    sheet = workbook[workbook.sheetnames[0]]
    rows = list(sheet.iter_rows(values_only=True))
    workbook.close()
    return rows


def load_jd_meta():
    meta = {}
    targets = [
        MODULE_DIR / "jd_data.xlsx",
        MODULE_DIR / "简历语料" / "boss_AIGC补充24条.xlsx",
    ]
    for path in targets:
        if not path.exists():
            continue
        rows = xlsx_rows(path)
        if not rows:
            continue
        header = rows[0]
        indexes = {str(name): i for i, name in enumerate(header)}
        for row in rows[1:]:
            if not row or not row[0]:
                continue
            doc_id = str(row[0])
            item = {
                "title": row[indexes.get("岗位名称", 1)] or "",
                "company": row[indexes.get("公司全称", 2)] or "",
                "industry": row[indexes.get("行业", 3)] or "",
                "nature": row[indexes.get("企业性质", 4)] or "",
                "family": row[indexes.get("岗位类别", 5)] or "",
                "city_salary": row[indexes.get("城市与薪资", 6)] or "",
                "education": row[indexes.get("学历要求", 7)] or "",
            }
            meta[doc_id] = item
    return meta


def load_samples():
    if not SAMPLE_PATH.exists():
        return {}
    return {str(item["id"]): item for item in read_json(SAMPLE_PATH)}


GRAPHS = load_cache_graphs()
JD_META = load_jd_meta()
SAMPLES = load_samples()


def split_city_salary(raw):
    raw = str(raw or "")
    if "|" in raw:
        parts = raw.split("|", 1)
        return parts[0].strip(), parts[1].strip()
    if "·" in raw:
        parts = raw.rsplit("·", 1)
        return parts[0].strip(), parts[1].strip()
    if " " in raw:
        parts = raw.rsplit(" ", 1)
        if parts[1].strip():
            return parts[0].strip(), parts[1].strip()
    if raw:
        return raw, "面议"
    return "", "面议"


def graph_skill_union(graph):
    groups = graph.get("skill_groups", {})
    professional = list(dict.fromkeys(groups.get("专业技能") or []))
    tools = list(dict.fromkeys(groups.get("工具") or []))
    soft = list(dict.fromkeys(groups.get("软技能") or []))
    return professional, tools, soft


def find_resume_file(resume_id):
    candidates = []
    for folder in [MODULE_DIR / "简历语料" / "合成简历库",
                   MODULE_DIR / "简历语料" / "试点简历"]:
        if not folder.exists():
            continue
        candidates.extend(sorted(folder.glob(f"{resume_id}_*.txt")))
    return candidates[0] if candidates else None


def resume_profile(resume_id):
    graph = GRAPHS.get(resume_id)
    sample = SAMPLES.get(resume_id, {})
    resume_file = find_resume_file(resume_id)
    text = ""
    if resume_file:
        with open(resume_file, encoding="utf-8") as f:
            text = f.read()

    def line_value(key):
        match = re.search(rf"^{key}：(.+)$", text, re.M)
        return match.group(1).strip() if match else ""

    name = line_value("姓名") or f"示例简历 {resume_id}"
    goal = line_value("求职意向") or sample.get("目标族", "新质岗位")
    personal = line_value("个人信息") or ""
    city = ""
    match = re.search(r"^([\u4e00-\u9fa5A-Za-z]+)\s*\|", personal)
    if match:
        city = match.group(1)
    degree = graph.get("education") if graph else sample.get("院校层次", "")
    school = sample.get("院校", "")
    major = sample.get("专业", "")
    layer = sample.get("层", "")
    target_family = sample.get("目标族", "")
    return {
        "id": resume_id,
        "name": name,
        "school": school,
        "major": major,
        "degree": degree,
        "city": city,
        "goal": goal,
        "layer": layer,
        "target_family": target_family,
        "source_file": str(resume_file) if resume_file else "",
        "summary": (
            f"{school} {major}方向，求职意向为{goal}。"
            "能力图谱已由后端抽取器完成结构化，可用于岗位匹配与差距分析。"
        ),
    }


def parse_projects_from_text(text, graph, resume_id):
    headings = [
        ("项目经历", "project"),
        ("实习经历", "experience"),
        ("校园经历", "campus"),
        ("竞赛经历", "competition"),
        ("技能证书", "cert"),
        ("教育背景", "education"),
        ("自我评价", "self"),
    ]
    found = []
    for heading, kind in headings:
        start = text.find(heading)
        if start < 0:
            continue
        ends = [text.find(h, start + len(heading)) for h, _ in headings]
        ends = [end for end in ends if end > start]
        end = min(ends) if ends else len(text)
        section = text[start + len(heading):end]
        bullets = [line.strip().lstrip("·-•").strip()
                   for line in section.splitlines()
                   if line.strip().startswith(("·", "-", "•"))]
        bullets = [b for b in bullets if len(b) > 8][:4]
        if not bullets:
            continue
        joined = " ".join(bullets)
        name = joined[:34]
        all_skills = []
        for group in (graph.get("skill_groups") or {}).values():
            all_skills.extend(group or [])
        matched = [skill for skill in all_skills if skill and skill.lower() in joined.lower()]
        time = ""
        mtime = re.search(r"(\d{4}\.\d{2}(?:-\d{4}\.\d{2})?)", joined)
        if mtime:
            time = mtime.group(1)
        found.append({
            "id": f"{kind}-{resume_id}-{len(found) + 1}",
            "name": f"{heading}·{name}",
            "time": time,
            "summary": joined,
            "kind": kind,
            "skills": matched,
        })
    return found[:4]


def parse_project_sections(resume_id, graph):
    resume_file = find_resume_file(resume_id)
    if not resume_file:
        return []
    with open(resume_file, encoding="utf-8") as f:
        text = f.read()
    return parse_projects_from_text(text, graph, resume_id)


def resume_skill_nodes(resume_id, graph):
    professional, tools, soft = graph_skill_union(graph)
    evidence = graph.get("evidence") or {}
    nodes = []
    seen = set()
    index = 0

    def push(name, group_name, skill_type):
        nonlocal index
        if not name or name in seen:
            return
        seen.add(name)
        index += 1
        evidence_text = evidence.get(name, "")
        level = max(60, min(96, 78 + (6 if len(evidence_text) > 8 else 0) - (index % 3) * 3))
        nodes.append({
            "id": f"s{index}",
            "name": name,
            "type": skill_type,
            "group": group_name,
            "level": level,
            "desc": evidence_text[:70] or f"能力图谱抽取项：{name}",
            "evidence": evidence_text,
        })

    for name in professional:
        push(name, "专业技能", "professional")
    for name in tools:
        push(name, "工具", "tool")
    for name in soft:
        push(name, "软技能", "soft")
    return nodes


class UploadError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def file_to_text(data, filename):
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        for encoding in ("utf-8", "gb18030"):
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages = [(page.extract_text() or "") for page in pdf.pages]
            return "\n".join(pages).strip()
        except Exception as exc:
            raise UploadError("PDF_PARSE_FAILED", f"PDF解析失败：{exc}") from exc
    if suffix in (".doc", ".docx"):
        if suffix == ".doc":
            raise UploadError(
                "OLD_DOC_NOT_SUPPORTED",
                "旧版 .doc 暂不支持，请另存为 .docx 后上传。",
            )
        try:
            import docx
            document = docx.Document(io.BytesIO(data))
            parts = [p.text for p in document.paragraphs if p.text.strip()]
            for table in document.tables:
                for row in table.rows:
                    parts.extend(cell.text for cell in row.cells if cell.text.strip())
            return "\n".join(parts).strip()
        except Exception as exc:
            raise UploadError("DOCX_PARSE_FAILED", f"Word解析失败：{exc}") from exc
    if suffix in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
        raise UploadError(
            "OCR_NOT_CONFIGURED",
            "图片OCR尚未配置，请上传PDF、Word或txt格式的简历文本。",
        )
    if suffix in (".mp3", ".wav", ".mp4", ".mov", ".webm"):
        raise UploadError(
            "ASR_NOT_CONFIGURED",
            "音视频转写尚未配置，请上传PDF、Word或txt格式的简历文本。",
        )
    raise UploadError(
        "FORMAT_NOT_SUPPORTED",
        f"暂不支持 {suffix or '该'} 格式，请上传PDF、Word或txt。",
    )


def uploaded_profile(doc_id, graph, text, filename):
    def line_value(key):
        match = re.search(rf"^{key}：(.+)$", text, re.M)
        return match.group(1).strip() if match else ""

    name = line_value("姓名") or Path(filename).stem
    goal = line_value("求职意向") or "新质岗位"
    school = ""
    major = ""
    edu_line = ""
    match = re.search(r"教育背景\s*(.+)", text)
    if match:
        edu_line = match.group(1)
    pieces = [part for part in re.split(r"\s+", edu_line) if part]
    if len(pieces) >= 2:
        school, major = pieces[0], pieces[1]
    return {
        "id": doc_id,
        "name": name,
        "school": school or "上传简历",
        "major": major or "未识别专业",
        "degree": graph.get("education", "本科"),
        "city": "",
        "goal": goal,
        "layer": "上传简历",
        "target_family": goal,
        "source_file": filename,
        "summary": f"已上传并解析{filename}，后端抽取器已生成能力图谱，可用于岗位匹配。",
    }


def extract_uploaded_resume(data, filename):
    api_key = os.environ.get("ZHIPU_API_KEY", "").strip()
    if not api_key:
        raise UploadError(
            "NO_API_KEY",
            "未配置ZHIPU_API_KEY，请先运行 configure_key.py 并重启服务。",
        )
    text = file_to_text(data, filename)
    if len(text.strip()) < 20:
        raise UploadError("RESUME_TOO_SHORT", "文件内容过短，未能识别为简历文本。")
    configure_extractor_paths()
    doc_id = f"U{int(time.time() * 1000)}"
    anchor = extractor.load_anchor()
    try:
        status, graph = extractor.extract_one(
            doc_id,
            text[:6000],
            "resume",
            api_key,
            anchor,
            quiet=False,
        )
    except Exception as exc:
        raise UploadError("LLM_CALL_FAILED", f"能力抽取失败：{exc}") from exc
    if status != "ok" or not graph:
        raise UploadError(
            "EXTRACTION_FAILED",
            "后端抽取未返回有效图谱，请查看服务日志或重试。",
        )
    graph["doc_type"] = "resume"
    graph["doc_title"] = filename
    GRAPHS[doc_id] = graph
    profile = uploaded_profile(doc_id, graph, text, filename)
    skills = resume_skill_nodes(doc_id, graph)
    projects = parse_projects_from_text(text, graph, doc_id)
    jobs = []
    for _, jd_id, jd_graph, meta, detail in recommendation_jobs(doc_id, top=3):
        jobs.append(job_payload(jd_id, jd_graph, meta, detail, graph))
    return {
        "source": "backend",
        "doc_id": doc_id,
        "profile": profile,
        "skills": skills,
        "projects": projects,
        "jobs": jobs,
        "extraction_text": text[:300],
    }


def recommendation_jobs(resume_id, top=3):
    resume_graph = GRAPHS.get(resume_id)
    if not resume_graph:
        return []
    scored = []
    for jd_id, jd_graph in GRAPHS.items():
        if jd_graph.get("doc_type") != "jd":
            continue
        meta = JD_META.get(jd_id, {})
        family = meta.get("family", "")
        if "负对照" in family or "硬核" in family:
            continue
        try:
            score, detail = graph_match(resume_graph, jd_graph)
        except Exception:
            continue
        if detail.get("filtered") or score <= 0:
            continue
        scored.append((score, jd_id, jd_graph, meta, detail))
    scored.sort(key=lambda item: -item[0])
    return scored[:top]


def path_from_gaps(gaps):
    path = []
    for index, gap in enumerate(gaps[:4]):
        skill = gap["name"]
        path.append({
            "stage": f"阶段 {index + 1}",
            "title": f"补齐「{skill}」",
            "weeks": f"{1 + index}周",
            "goal": f"系统补充{skill}，并通过一个与目标岗位相关的实践任务检验掌握程度。",
            "resources": [
                {"name": f"{skill}系统课程", "type": "课程", "meta": "1周 · 基础与进阶"},
                {"name": f"{skill}岗位实战案例", "type": "项目", "meta": "1周 · 场景实践"},
                {"name": "岗位JD复盘清单", "type": "资料", "meta": "边做边对照"},
            ],
        })
    if gaps:
        path.append({
            "stage": f"阶段 {len(path) + 1}",
            "title": "综合项目与成果复盘",
            "weeks": "2-3周",
            "goal": "把补齐能力组合成一个可写进简历的完整项目，并形成可复述的项目成果。",
            "resources": [
                {"name": "端到端项目实践", "type": "项目", "meta": "2-3周 · 完整闭环"},
                {"name": "简历项目复盘模板", "type": "资料", "meta": "按结果整理"},
            ],
        })
    return path


def job_payload(jd_id, jd_graph, meta, detail, resume_graph):
    title = meta.get("title") or jd_id
    company = meta.get("company") or "示例企业"
    city, salary = split_city_salary(meta.get("city_salary"))
    required = []
    required_seen = set()
    for skill in (jd_graph.get("skill_groups", {}).get("专业技能") or []):
        if skill not in required_seen:
            required.append({"name": skill, "level": 92})
            required_seen.add(skill)
    for skill in (jd_graph.get("skill_groups", {}).get("工具") or []):
        if skill not in required_seen:
            required.append({"name": skill, "level": 86})
            required_seen.add(skill)
    preferred = [
        {"name": skill, "level": 78}
        for skill in (jd_graph.get("skill_groups", {}).get("软技能") or [])[:6]
    ]

    gaps = []
    gap_order = [
        (name, "专业技能") for name in detail.get("gap_专业技能", [])
    ] + [
        (name, "工具") for name in detail.get("gap_工具", [])
    ] + [
        (name, "软技能") for name in detail.get("gap_软技能", [])
    ]
    soft_names = set(jd_graph.get("skill_groups", {}).get("软技能") or [])
    for name, group in gap_order:
        evidence = jd_graph.get("evidence", {}).get(name, "")
        gaps.append({
            "name": name,
            "group": group,
            "kind": "weak" if name in soft_names else "required",
            "reason": evidence or f"目标岗位要求具备{name}，个人能力图谱中未检测到该能力。",
            "action": "",
        })
    for i, gap in enumerate(gaps):
        gap["action"] = f"阶段 {i + 1}：补齐「{gap['name']}」"

    raw_score = detail.get("score", 0)
    score = max(1, min(99, round(raw_score * 100)))
    grade = "较匹配" if score >= 55 else ("可尝试" if score >= 30 else "需提升")
    s_skill = detail.get("s_skill", 0)
    s_tool = detail.get("s_tool", 0)
    s_soft = detail.get("s_soft", 0)
    dims = [
        {"label": "硬技能", "mine": round(min(96, 55 + 45 * s_skill)), "target": 90},
        {"label": "软技能", "mine": round(min(96, 50 + 45 * s_soft)), "target": 82},
        {"label": "项目经历", "mine": 70, "target": 84},
        {"label": "学历证书", "mine": 78, "target": 86},
        {"label": "行业知识", "mine": 72, "target": 88},
        {"label": "岗位契合", "mine": score, "target": 100},
    ]
    tags = [skill["name"] for skill in required[:3]]
    if not tags:
        tags = [meta.get("family", "新质岗位")]

    return {
        "key": jd_id,
        "id": jd_id,
        "title": title,
        "company": company,
        "city": city,
        "salary": salary,
        "industry": meta.get("industry") or meta.get("family") or "",
        "tags": tags,
        "summary": (
            f"{company}发布的{title}岗位。后端已抽取岗位能力图谱，"
            "匹配结果基于专业技能、工具与软技能清单对齐计算。"
        ),
        "score": score,
        "grade": grade,
        "dims": dims,
        "skill_groups": jd_graph.get("skill_groups", {}),
        "requirements": {"required": required, "preferred": preferred},
        "match": {
            **detail,
            "score_raw": raw_score,
            "weights": {"专业技能": 0.8, "工具": 0.2, "软技能": 0.0},
            "hard_filter_passed": True,
        },
        "gaps": gaps,
        "path": path_from_gaps(gaps),
        "evidence": jd_graph.get("evidence", {}),
    }


def bootstrap_payload(resume_id="S031", top=3):
    profile = resume_profile(resume_id)
    graph = GRAPHS.get(resume_id) or {}
    skills = resume_skill_nodes(resume_id, graph)
    projects = parse_project_sections(resume_id, graph)
    jobs = []
    for _, jd_id, jd_graph, meta, detail in recommendation_jobs(resume_id, top=top):
        jobs.append(job_payload(jd_id, jd_graph, meta, detail, graph))
    return {
        "source": "backend",
        "profile": profile,
        "skills": skills,
        "projects": projects,
        "jobs": jobs,
        "counts": {
            "resume_graphs": sum(1 for g in GRAPHS.values() if g.get("doc_type") == "resume"),
            "jd_graphs": sum(1 for g in GRAPHS.values() if g.get("doc_type") == "jd"),
            "samples": len(SAMPLES),
        },
    }


def resume_list():
    items = []
    for resume_id in sorted(GRAPHS.keys()):
        graph = GRAPHS[resume_id]
        if graph.get("doc_type") != "resume":
            continue
        sample = SAMPLES.get(resume_id, {})
        items.append({
            "id": resume_id,
            "major": sample.get("专业", ""),
            "school": sample.get("院校", ""),
            "layer": sample.get("层", ""),
            "target": sample.get("目标族", ""),
            "education": graph.get("education", ""),
            "skills": sum(len(graph.get("skill_groups", {}).get(group) or [])
                          for group in ("专业技能", "工具", "软技能")),
        })
    return items


def json_response(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def serve_static(handler, route):
    if route == "/" or route == "":
        route = "index.html"
    file_path = (FRONTEND_DIR / route.lstrip("/")).resolve()
    try:
        file_path.relative_to(FRONTEND_DIR.resolve())
    except ValueError:
        json_response(handler, {"error": "forbidden"}, 403)
        return
    if not file_path.is_file():
        json_response(handler, {"error": "not found"}, 404)
        return
    content = file_path.read_bytes()
    mime_type, _ = mimetypes.guess_type(file_path.name)
    handler.send_response(200)
    handler.send_header("Content-Type", mime_type or "application/octet-stream")
    handler.send_header("Content-Length", str(len(content)))
    handler.send_header("Cache-Control", "no-cache")
    handler.end_headers()
    handler.wfile.write(content)


def register_chinese_font():
    global CHINESE_FONT_NAME
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    if os.path.exists("C:/Windows/Fonts/simhei.ttf"):
        if "SimHei" not in pdfmetrics.getRegisteredFontNames():
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(
                TTFont("SimHei", "C:/Windows/Fonts/simhei.ttf")
            )
        CHINESE_FONT_NAME = "SimHei"
        return
    if "STSong-Light" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    CHINESE_FONT_NAME = "STSong-Light"


def build_report_pdf(payload):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    register_chinese_font()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="求职适配诊断报告",
    )

    base = ParagraphStyle(
        "cn-body",
        fontName=CHINESE_FONT_NAME,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#26312f"),
    )
    title_style = ParagraphStyle(
        "cn-title",
        parent=base,
        fontSize=20,
        leading=28,
        textColor=colors.HexColor("#0f766e"),
        spaceAfter=3,
    )
    sub_style = ParagraphStyle(
        "cn-sub",
        parent=base,
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#7a8885"),
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "cn-h2",
        parent=base,
        fontSize=12,
        leading=17,
        textColor=colors.HexColor("#17211f"),
        spaceBefore=10,
        spaceAfter=5,
    )
    small = ParagraphStyle(
        "cn-small",
        parent=base,
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#5d6a67"),
    )

    profile = payload.get("profile") or {}
    job = payload.get("job") or {}
    coverage = payload.get("coverage") or []
    gaps = payload.get("gaps") or []
    path = payload.get("path") or []
    skills = payload.get("skills") or []

    def cell(text, style=base):
        return Paragraph(escape(str(text if text is not None else "")), style)

    width = doc.width
    elements = [
        Paragraph("求职适配诊断报告", title_style),
        Paragraph(
            f"姓名：{escape(str(profile.get('name', '')))} · "
            f"{escape(str(profile.get('school', '') or ''))} · "
            f"目标岗位：{escape(str(job.get('title', '')))}",
            sub_style,
        ),
    ]

    summary_rows = [
        [cell("候选人", small), cell(profile.get("name", "")),
         cell("目标岗位", small), cell(job.get("title", ""))],
        [cell("院校方向", small), cell(profile.get("school", "")),
         cell("企业/城市", small), cell(f"{job.get('company', '')} · {job.get('city', '')}")],
        [cell("适配得分", small), cell(f"{job.get('score', '-')} · {job.get('grade', '')}"),
         cell("薪资", small), cell(job.get("salary", ""))],
    ]
    summary_table = Table(summary_rows, colWidths=[28 * mm, width / 2 - 28 * mm, 28 * mm, width / 2 - 28 * mm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f9f8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dce8e5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements += [summary_table, Spacer(1, 6 * mm)]

    elements.append(Paragraph("能力覆盖得分", h2_style))
    coverage_rows = [[cell("维度", small), cell("得分/说明", small), cell("权重", small)]]
    coverage_rows += [
        [cell(item.get("label", "")), cell(item.get("value", "")), cell(item.get("note", ""))]
        for item in coverage
    ]
    coverage_table = Table(coverage_rows, colWidths=[50 * mm, width - 90 * mm, 40 * mm])
    coverage_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dce8e5")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5f3f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(coverage_table)

    elements.append(Paragraph("能力差距", h2_style))
    if gaps:
        gap_rows = [[cell("能力", small), cell("能力组", small), cell("说明", small)]]
        gap_rows += [
            [cell(item.get("name", "")), cell(item.get("group", "")), cell(item.get("reason", ""))]
            for item in gaps
        ]
        gap_table = Table(gap_rows, colWidths=[42 * mm, 24 * mm, width - 66 * mm])
        gap_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dce8e5")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef4f2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(gap_table)
    else:
        elements.append(Paragraph("未发现明显能力差距。", base))

    elements.append(Paragraph("学习计划", h2_style))
    if path:
        for phase in path:
            title_text = f"{phase.get('stage', '')} · {phase.get('title', '')} · {phase.get('weeks', '')}"
            elements.append(Paragraph(escape(title_text), base))
            elements.append(Paragraph(escape(phase.get("goal", "")), small))
            resources = phase.get("resources") or []
            if resources:
                resource_text = "；".join(
                    f"{item.get('name', '')}（{item.get('type', '')} / {item.get('meta', '')}）"
                    for item in resources
                )
                elements.append(Paragraph("资源：" + escape(resource_text), small))
            elements.append(Spacer(1, 2.5 * mm))
    else:
        elements.append(Paragraph("暂无学习计划，请在页面内完成岗位匹配后重新导出。", base))

    if skills:
        skill_text = " / ".join(str(skill.get("name", "")) for skill in skills[:12])
        elements.append(Paragraph("核心能力：" + escape(skill_text), small))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        "本报告由个人能力图谱与岗位能力图谱自动匹配生成，结果供求职规划参考。",
        small,
    ))
    doc.build(elements)
    return buffer.getvalue()


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "ZhipuGraphIntegration/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {fmt % args}\n")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-File-Name")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/api/delete-resume":
            doc_id = (query.get("doc_id") or [""])[0]
            if not doc_id.startswith("U"):
                json_response(self, {"error": "仅可删除本次上传生成的简历图谱"}, 400)
                return
            cache_file = CACHE_DIR / f"{doc_id}.json"
            deleted = False
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    deleted = True
                except OSError:
                    json_response(self, {"error": "图谱缓存文件被占用，删除失败"}, 500)
                    return
            if doc_id in GRAPHS:
                GRAPHS.pop(doc_id, None)
                deleted = True
            json_response(self, {"ok": True, "deleted": deleted, "doc_id": doc_id})
            return
        if parsed.path == "/api/export-report":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                json_response(self, {"error": "invalid report payload"}, 400)
                return
            try:
                pdf_data = build_report_pdf(payload)
            except Exception as exc:
                json_response(self, {"code": "PDF_GENERATE_FAILED", "error": repr(exc)}, 500)
                return
            profile = payload.get("profile") or {}
            filename = f"求职适配诊断报告-{profile.get('name', '用户')}.pdf"
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header(
                "Content-Disposition",
                f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}",
            )
            self.send_header("Content-Length", str(len(pdf_data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(pdf_data)
            return
        if parsed.path != "/api/upload-resume":
            json_response(self, {"error": "unknown api"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0:
            json_response(self, {"error": "empty request"}, 400)
            return
        if length > 25 * 1024 * 1024:
            json_response(self, {"error": "file too large, max 25MB"}, 413)
            return
        data = self.rfile.read(length)
        filename = urllib.parse.unquote(
            self.headers.get("X-File-Name", "上传简历.txt")
        )
        try:
            payload = extract_uploaded_resume(data, filename)
        except UploadError as exc:
            json_response(self, {
                "code": exc.code,
                "error": exc.message,
            }, 400)
            return
        except Exception as exc:
            json_response(self, {"code": "INTERNAL_ERROR", "error": repr(exc)}, 500)
            return
        json_response(self, payload, 200)

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        route = parsed.path
        if route == "/api/health":
            json_response(self, {
                "ok": True,
                "service": "backend-integration",
                "counts": {
                    "jd": sum(1 for g in GRAPHS.values() if g.get("doc_type") == "jd"),
                    "resume": sum(1 for g in GRAPHS.values() if g.get("doc_type") == "resume"),
                },
            })
            return
        if route == "/api/resumes":
            json_response(self, {"items": resume_list()})
            return
        if route == "/api/bootstrap":
            resume_id = (query.get("resume_id") or ["S031"])[0]
            top = int((query.get("top") or ["3"])[0])
            payload = bootstrap_payload(resume_id, top=top)
            if payload["jobs"]:
                json_response(self, payload)
            else:
                json_response(self, {"error": f"resume {resume_id} not found"}, 404)
            return
        if route == "/api/match":
            resume_id = (query.get("resume_id") or ["S031"])[0]
            jd_id = (query.get("job_id") or [""])[0]
            resume_graph = GRAPHS.get(resume_id)
            jd_graph = GRAPHS.get(jd_id)
            if not resume_graph or not jd_graph:
                json_response(self, {"error": "missing resume or job"}, 404)
                return
            score, detail = graph_match(resume_graph, jd_graph)
            json_response(self, {
                "resume_id": resume_id,
                "job_id": jd_id,
                "score": score,
                "detail": detail,
                "meta": JD_META.get(jd_id, {}),
            })
            return
        if route.startswith("/api/"):
            json_response(self, {"error": "unknown api"}, 404)
            return
        serve_static(self, route)


if __name__ == "__main__":
    print("智职图谱一体化演示服务启动中...")
    print(f"缓存：JD {sum(1 for g in GRAPHS.values() if g.get('doc_type') == 'jd')} 份，"
          f"简历 {sum(1 for g in GRAPHS.values() if g.get('doc_type') == 'resume')} 份")
    print(f"访问地址：http://{HOST}:{PORT}")
    server = ThreadingHTTPServer((HOST, PORT), ApiHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()
