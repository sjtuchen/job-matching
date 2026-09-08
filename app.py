# -*- coding: utf-8 -*-
"""智职图谱 Streamlit 版

与本地一体化页面功能等价：上传简历 -> 能力抽取 -> 图谱查看 ->
岗位匹配 -> 学习路线 -> PDF 诊断报告。
"""

import os
import math
import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent


def _secret(name):
    try:
        value = st.secrets.get(name, "")
        return value or ""
    except Exception:
        return ""


api_key = _secret("ZHIPU_API_KEY")
if api_key:
    os.environ.setdefault("ZHIPU_API_KEY", api_key)

sys.path.insert(0, str(ROOT_DIR / "backend-integration"))


@st.cache_resource(show_spinner=False)
def load_backend():
    import server as backend_server
    return backend_server


backend = load_backend()

st.set_page_config(
    page_title="智职图谱 · 求职适配诊断",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding: 1.1rem 2rem 2rem; max-width: 1400px;}
    .stApp {background: #eef2f1;}
    [data-testid="stHeader"] {background: transparent;}
    [data-testid="stSidebar"] {
        background: #18201f; min-width: 250px; width: 250px;
        border-right: 1px solid rgba(255,255,255,.08);
    }
    [data-testid="stSidebar"] > div:first-child {padding: 22px 14px 16px;}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {color: #f3f7f6;}
    [data-testid="stSidebar"] hr {border-color: rgba(255,255,255,.12);}
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {gap: 4px;}
    [data-testid="stSidebar"] .stRadio label {
        display: flex; align-items: center; width: 100%;
        padding: 10px 12px; border-radius: 8px; color: #bfcac7;
        background: transparent; transition: background .18s ease, color .18s ease;
    }
    [data-testid="stSidebar"] .stRadio label:hover {background: rgba(255,255,255,.07); color: #fff;}
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: #0f766e; color: #fff;
    }
    [data-testid="stSidebar"] .stRadio label p {font-weight: 600; margin: 0;}
    .brand-lockup {display:flex; align-items:center; gap:11px; padding:2px 6px 18px;}
    .brand-mark {
        width:40px; height:40px; border-radius:10px; display:grid;
        place-items:center; background:linear-gradient(135deg,#14b8a6,#0f766e);
        color:white; font-size:19px; font-weight:800;
    }
    .brand-text {display:flex; flex-direction:column; line-height:1.2;}
    .brand-text strong {font-size:17px; color:#fff; letter-spacing:.04em;}
    .brand-text span {color:#aebbb8; font-size:11px; margin-top:4px;}
    .top-progress {
        display:flex; align-items:center; justify-content:flex-end;
        gap:7px; color:#93a09d; font-size:12px; padding:8px 0;
    }
    .top-progress .step {padding:3px 8px; border-radius:999px;}
    .top-progress .step.on {background:#dff2ed; color:#0f766e; font-weight:600;}
    .top-progress .line {width:18px; height:1px; background:#d9e2df;}
    .page-head {
        display:flex; align-items:flex-end; justify-content:space-between;
        gap:20px; margin:2px 0 18px;
    }
    .page-head h1 {font-size:27px; line-height:1.15; margin:0; color:#17211f; letter-spacing:0;}
    .page-head p {color:#687472; margin:8px 0 0; font-size:14px;}
    .ghost-btn, .primary-btn {
        display:inline-flex; align-items:center; justify-content:center; gap:7px;
        border-radius:8px; padding:9px 14px; font-weight:600; border:1px solid #b8cfca;
        background:#fff; color:#0b5d57; cursor:pointer;
    }
    .primary-btn {
        background:#0f766e; border-color:#0f766e; color:#fff;
        box-shadow:0 6px 16px rgba(15,118,110,.18);
    }
    [data-testid="stButton"] button {
        border-radius:8px; border:1px solid #b8cfca; background:#fff;
        color:#0b5d57; font-weight:600;
    }
    [data-testid="stButton"] button[kind="primary"] {
        background:#0f766e; border-color:#0f766e; color:#fff;
        box-shadow:0 6px 16px rgba(15,118,110,.18);
    }
    [data-testid="stMetric"] {
        background:#fff; border:1px solid #dfe7e4; border-radius:8px;
        padding:13px 14px; box-shadow:0 8px 20px rgba(25,43,39,.04);
    }
    [data-testid="stMetricLabel"] {color:#687472;}
    [data-testid="stMetricValue"] {color:#17211f;}
    [data-testid="stVerticalBlockBorderWrapper"] {
        background:#fff; border:1px solid #dfe7e4; border-radius:8px;
        box-shadow:0 8px 22px rgba(25,43,39,.04);
    }
    [data-testid="stExpander"] {
        background:#fff; border:1px solid #dfe7e4; border-radius:8px;
    }
    .skill-chip {
        display:inline-block; border:1px solid #d6e2df; border-radius:6px;
        padding:3px 9px; margin:2px 5px 2px 0; background:#f7f9f8;
        color:#26312f; font-size:13px;
    }
    .report-kv {display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px;}
    .kv-item {background:#f7f9f8; border:1px solid #e4ebe8; border-radius:8px; padding:9px 11px;}
    .kv-item small {color:#87938f;}
    .kv-item strong {color:#17211f; display:block; margin-top:2px;}
    h1,h2,h3 {letter-spacing:0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    defaults = {
        "payload": None,
        "resume_id": "S031",
        "selected_job_id": None,
        "uploaded_name": None,
        "report_pdf": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    if st.session_state.payload is None:
        with st.spinner("正在加载真实岗位与能力图谱..."):
            payload = backend.bootstrap_payload("S031", top=6)
        st.session_state.payload = payload
        st.session_state.resume_id = payload["profile"]["id"]
        if payload["jobs"]:
            st.session_state.selected_job_id = payload["jobs"][0]["id"]


init_state()

PAGE_NAMES = [
    "材料导入",
    "能力图谱",
    "岗位匹配",
    "学习路线",
    "诊断报告",
]

st.sidebar.markdown(
    """
    <div class="brand-lockup">
      <div class="brand-mark">图</div>
      <div class="brand-text"><strong>智职图谱</strong><span>求职适配诊断平台</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)
page = st.sidebar.radio("工作台", PAGE_NAMES)


def page_header(title, lead):
    page_index = PAGE_NAMES.index(page)
    step_labels = ["1 导入", "2 图谱", "3 匹配", "4 路线", "5 报告"]
    progress = []
    for index, label in enumerate(step_labels):
        css = "step on" if index == page_index else "step"
        progress.append(f'<span class="{css}">{label}</span>')
        if index < len(step_labels) - 1:
            progress.append('<span class="line"></span>')
    st.markdown(
        f'<div class="top-progress">{"".join(progress)}</div>'
        f'<div class="page-head"><div><h1>{title}</h1><p>{lead}</p></div></div>',
        unsafe_allow_html=True,
    )


def current_payload():
    return st.session_state.payload


def current_job():
    payload = current_payload()
    if not payload:
        return None
    for job in payload.get("jobs", []):
        if job["id"] == st.session_state.selected_job_id:
            return job
    return payload.get("jobs", [None])[0]


def render_sidebar_profile():
    payload = current_payload()
    if not payload:
        return
    profile = payload.get("profile", {})
    job = current_job() or {}
    st.sidebar.markdown("---")
    st.sidebar.markdown("**当前候选人**")
    st.sidebar.write(f"{profile.get('name', '示例简历')} · {profile.get('school', '')}")
    if job:
        st.sidebar.write(f"{job.get('title', '')} · {job.get('score', '-')}分")
    if st.sidebar.button("重置为示例简历", use_container_width=True):
        with st.spinner("正在切换回内置示例简历..."):
            payload = backend.bootstrap_payload("S031", top=6)
        st.session_state.payload = payload
        st.session_state.resume_id = "S031"
        st.session_state.selected_job_id = payload["jobs"][0]["id"] if payload["jobs"] else None
        st.session_state.report_pdf = None
        st.rerun()


render_sidebar_profile()


def show_score_card(job):
    title = job.get("title", "未命名岗位")
    company = job.get("company", "")
    city = job.get("city", "")
    salary = job.get("salary", "面议")
    grade = job.get("grade", "")
    score = job.get("score", 0)
    left, right = st.columns([3, 1])
    with left:
        st.subheader(title)
        st.write(f"{company} · {city} · {salary}")
        tags = job.get("tags") or []
        if tags:
            st.markdown("".join(
                f'<span class="skill-chip">{str(tag)}</span>' for tag in tags[:6]
            ), unsafe_allow_html=True)
    with right:
        st.metric("适配度", score, help="满分100")
        if grade:
            st.markdown(f'<span class="score-pill">{grade}</span>', unsafe_allow_html=True)


def render_upload_page():
    page_header(
        "个人材料导入",
        "简历、成绩单、自我介绍已就绪，可直接进入能力分析。",
    )

    profile = current_payload().get("profile", {})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("当前候选人", profile.get("name", "-"))
    col2.metric("学校", profile.get("school", "-") or "-")
    col3.metric("专业方向", profile.get("major", "-") or "-")
    col4.metric("已接入岗位图谱", current_payload().get("counts", {}).get("jd_graphs", 359))

    st.markdown("---")
    left, right = st.columns([1, 1])
    with left:
        st.subheader("上传真实简历")
        uploaded = st.file_uploader(
            "支持 .txt / .pdf / .docx",
            type=["txt", "pdf", "docx"],
            key="streamlit_resume_uploader",
        )
        if st.button("解析并生成个人图谱", type="primary", use_container_width=True, disabled=uploaded is None):
            if not uploaded:
                st.warning("请先选择简历文件。")
            elif not api_key:
                st.error("尚未配置 ZHIPU_API_KEY，请在 Streamlit Secrets 中填写。")
            else:
                with st.spinner("后端正在调用智谱 GLM-4-Flash 抽取能力图谱..."):
                    try:
                        payload = backend.extract_uploaded_resume(
                            uploaded.getvalue(),
                            uploaded.name,
                        )
                    except backend.UploadError as exc:
                        st.error(exc.message)
                        payload = None
                    except Exception as exc:
                        st.error(f"解析失败：{exc}")
                        payload = None
                if payload:
                    st.session_state.payload = payload
                    st.session_state.resume_id = payload["profile"]["id"]
                    st.session_state.uploaded_name = uploaded.name
                    if payload["jobs"]:
                        st.session_state.selected_job_id = payload["jobs"][0]["id"]
                    st.session_state.report_pdf = None
                    st.success(f"解析完成：{payload['profile'].get('name', '用户')}")
                    st.rerun()
    with right:
        st.subheader("当前可演示简历")
        st.write("未上传时使用内置真实示例简历 S031，仍可查看完整匹配流程。")
        jobs = current_payload().get("jobs", [])
        st.markdown("**推荐岗位预览**")
        for job in jobs[:3]:
            st.markdown(
                f'<div class="metric-card"><b>{job.get("title", "")}</b><br/>'
                f'{job.get("company", "")} · {job.get("city", "")} · '
                f'{job.get("salary", "")} · <b>{job.get("score", "-")}分</b></div>',
                unsafe_allow_html=True,
            )


def graph_figure(skills, center_name=None):
    if not skills:
        return None
    if center_name is None:
        center_name = current_payload().get("profile", {}).get("name", "用户")
    color_map = {
        "professional": "#0f766e",
        "tool": "#2563eb",
        "soft": "#c2410c",
    }
    labels = [skill["name"] for skill in skills]
    x = []
    y = []
    texts = []
    colors = []
    n = len(skills)
    for index, skill in enumerate(skills):
        angle = 360 * index / max(n, 1)
        radius = 88
        x.append(radius * math.cos(math.radians(angle)))
        y.append(radius * math.sin(math.radians(angle)))
        texts.append(skill["name"])
        colors.append(color_map.get(skill.get("type", ""), "#64748b"))

    edge_x = []
    edge_y = []
    for index in range(n):
        edge_x += [0, x[index], None]
        edge_y += [0, y[index], None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(color="rgba(100,116,139,0.22)", width=1.2),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="markers+text",
        marker=dict(size=13, color=colors, opacity=0.95),
        text=texts,
        textposition="top center",
        textfont=dict(size=11, color="#1e293b"),
        hoverinfo="text",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=[0],
        y=[0],
        mode="markers+text",
        marker=dict(size=22, color="#10302b"),
        text=[center_name],
        textposition="bottom center",
        textfont=dict(size=13, color="#10302b"),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False, range=[-125, 125]),
        yaxis=dict(visible=False, range=[-125, 125]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_graph_page():
    page_header("能力图谱", "点击节点查看能力来源，支持类别筛选与图谱对比。")
    mode = st.radio(
        "图谱模式",
        ["个人能力图谱", "岗位能力图谱"],
        horizontal=True,
        label_visibility="collapsed",
        key="streamlit_graph_mode",
    )
    profile = current_payload().get("profile", {})
    job = current_job() or {}
    if mode == "个人能力图谱":
        skills = current_payload().get("skills", [])
        center_name = profile.get("name", "用户")
    else:
        required = []
        for item in (job.get("requirements") or {}).get("required", []):
            required.append({
                "name": item.get("name", ""),
                "type": "professional",
                "group": "专业技能",
            })
        for item in (job.get("requirements") or {}).get("preferred", []):
            required.append({
                "name": item.get("name", ""),
                "type": "soft",
                "group": "软技能",
            })
        skills = required
        center_name = job.get("title") or "目标岗位"
    projects = current_payload().get("projects", [])
    c1, c2, c3 = st.columns(3)
    c1.metric("候选人", profile.get("name", "-"))
    c2.metric("技能节点", len(skills))
    c3.metric("项目经历", len(projects))

    left, right = st.columns([3, 2])
    with left:
        fig = graph_figure(skills, center_name=center_name)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("当前简历尚未抽取到技能节点。")
    with right:
        st.subheader("能力证据")
        groups = {}
        for skill in skills:
            groups.setdefault(skill.get("group", "其他"), []).append(skill)
        for group, items in groups.items():
            with st.expander(f"{group} · {len(items)} 项", expanded=True):
                for item in items[:8]:
                    st.markdown(
                        f"**{item['name']}** · {item.get('level', '-')}分",
                        help=item.get("evidence") or item.get("desc", ""),
                    )
        st.markdown("---")
        st.subheader("项目经历")
        if projects:
            for project in projects[:5]:
                st.markdown(f"**{project.get('title', project.get('name', ''))}**")
                st.caption(project.get("summary") or project.get("desc", ""))
        else:
            st.write("无项目经历记录。")


def radar_figure(job):
    dims = job.get("dims", [])
    if not dims:
        return None
    labels = [dim["label"] for dim in dims]
    mine = [dim["mine"] for dim in dims]
    target = [dim["target"] for dim in dims]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=mine + [mine[0]],
        theta=labels + [labels[0]],
        fill="toself",
        name="个人水平",
        line_color="#0f766e",
        fillcolor="rgba(15,118,110,0.16)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=target + [target[0]],
        theta=labels + [labels[0]],
        fill="toself",
        name="岗位目标",
        line_color="#c2410c",
        fillcolor="rgba(194,65,12,0.08)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=480,
        margin=dict(l=40, r=40, t=20, b=20),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def match_rows(job):
    match = job.get("match") or {}
    weights = match.get("weights") or {"专业技能": 0.8, "工具": 0.2, "软技能": 0.0}
    return [
        {
            "维度": "专业技能覆盖率",
            "得分": f"{round((match.get('s_skill') or 0) * 100)}%",
            "权重/说明": f"权重 {weights.get('专业技能', 0.8)}",
        },
        {
            "维度": "工具覆盖率",
            "得分": f"{round((match.get('s_tool') or 0) * 100)}%",
            "权重/说明": f"权重 {weights.get('工具', 0.2)}",
        },
        {
            "维度": "软技能覆盖率",
            "得分": f"{round((match.get('s_soft') or 0) * 100)}%",
            "权重/说明": "通用词提示，不计总分",
        },
        {
            "维度": "学历门槛",
            "得分": "通过" if match.get("hard_filter_passed") is not False else "未通过",
            "权重/说明": "graph_match hard_gate",
        },
    ]


def render_match_page():
    page_header("岗位匹配", "选择目标岗位，查看总分、能力覆盖、六维雷达与差距。")
    payload = current_payload()
    jobs = payload.get("jobs", [])
    if not jobs:
        st.warning("当前没有可推荐的岗位。")
        return
    job_ids = [job["id"] for job in jobs]
    selected_id = st.selectbox(
        "选择目标岗位",
        job_ids,
        format_func=lambda jid: next(
            (f"{job.get('title', jid)} · {job.get('company', '')}" for job in jobs if job["id"] == jid),
            jid,
        ),
        key="match_job_selector",
    )
    st.session_state.selected_job_id = selected_id
    job = current_job()
    show_score_card(job)
    st.markdown("---")
    left, right = st.columns([3, 2])
    with left:
        st.subheader("六维能力雷达")
        fig = radar_figure(job)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无维度数据。")
    with right:
        st.subheader("图谱覆盖得分")
        st.table(match_rows(job))
        st.subheader("岗位技能要求")
        skill_groups = job.get("skill_groups") or {}
        for group, names in skill_groups.items():
            if names:
                st.markdown(f"**{group}**")
                st.markdown("".join(
                    f'<span class="skill-chip">{str(name)}</span>' for name in names[:14]
                ), unsafe_allow_html=True)


def render_learning_page():
    page_header("学习路线", "围绕能力缺口生成由浅入深的学习计划。")
    job = current_job()
    if not job:
        st.info("请先在岗位匹配页选择一个岗位。")
        return
    st.caption(f"{job.get('title', '')} · {job.get('company', '')} · {job.get('grade', '')}")
    gaps = job.get("gaps") or []
    if gaps:
        st.markdown("**当前能力缺口**")
        st.markdown("".join(
            f'<span class="skill-chip" style="border-color:#f5c7c7;color:#b91c1c;">{str(gap["name"])}</span>'
            for gap in gaps[:10]
        ), unsafe_allow_html=True)
    else:
        st.success("未发现明显能力差距。")
    st.markdown("---")
    path = job.get("path") or []
    if not path:
        st.info("暂无学习计划。")
        return
    for phase in path:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.subheader(f"{phase.get('stage', '')} · {phase.get('title', '')}")
            c2.metric("周期", phase.get("weeks", "-"))
            st.write(phase.get("goal", ""))
            resources = phase.get("resources") or []
            for resource in resources:
                st.markdown(
                    f"<span class='skill-chip'>{resource.get('name', '')} "
                    f"· {resource.get('type', '')} · {resource.get('meta', '')}</span>",
                    unsafe_allow_html=True,
                )


def report_payload_for(job):
    profile = current_payload().get("profile", {})
    match = job.get("match") or {}
    return {
        "profile": {
            "name": profile.get("name", ""),
            "school": profile.get("school", ""),
            "focus": profile.get("goal", ""),
            "summary": profile.get("summary", ""),
        },
        "job": {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "city": job.get("city", ""),
            "salary": job.get("salary", ""),
            "score": job.get("score", ""),
            "grade": job.get("grade", ""),
            "summary": job.get("summary", ""),
        },
        "skills": current_payload().get("skills", [])[:14],
        "coverage": [
            {
                "label": row["维度"],
                "value": row["得分"],
                "note": row["权重/说明"],
            }
            for row in match_rows(job)
        ],
        "gaps": job.get("gaps") or [],
        "path": job.get("path") or [],
    }


def render_report_page():
    page_header("诊断报告", "查看完整诊断结果，并导出与页面一致的 PDF。")
    payload = current_payload()
    profile = payload.get("profile", {})
    job = current_job()
    if not job:
        st.info("请先完成岗位匹配。")
        return
    st.subheader("报告预览")
    left, right = st.columns([3, 1])
    with left:
        st.write(
            f"**{profile.get('name', '')}** · {profile.get('school', '')} · "
            f"目标岗位：{job.get('title', '')}"
        )
        st.write(f"{job.get('company', '')} · {job.get('city', '')} · {job.get('salary', '')}")
    with right:
        st.metric("适配得分", job.get("score", "-"))

    st.markdown("---")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**能力覆盖**")
        st.table(match_rows(job))
    with t2:
        st.markdown("**能力差距**")
        gaps = job.get("gaps") or []
        st.write("、".join(gap["name"] for gap in gaps[:12]) if gaps else "无明显差距")

    st.markdown("**学习计划摘要**")
    path = job.get("path") or []
    if path:
        rows = [
            {
                "阶段": phase.get("stage", ""),
                "主题": phase.get("title", ""),
                "周期": phase.get("weeks", ""),
                "目标": phase.get("goal", ""),
            }
            for phase in path
        ]
        st.table(rows)

    st.markdown("---")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("生成 PDF", type="primary", use_container_width=True):
            with st.spinner("正在生成诊断报告..."):
                try:
                    pdf = backend.build_report_pdf(report_payload_for(job))
                    st.session_state.report_pdf = pdf
                    st.success("PDF 已生成，可下载。")
                except Exception as exc:
                    st.error(f"PDF 生成失败：{exc}")
    with c2:
        if st.session_state.report_pdf:
            st.download_button(
                "下载 PDF 报告",
                data=st.session_state.report_pdf,
                file_name=f"求职适配诊断报告-{profile.get('name', '用户')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.caption("报告预览中的姓名、岗位与匹配结果与当前页面一致。")


if page == PAGE_NAMES[0]:
    render_upload_page()
elif page == PAGE_NAMES[1]:
    render_graph_page()
elif page == PAGE_NAMES[2]:
    render_match_page()
elif page == PAGE_NAMES[3]:
    render_learning_page()
elif page == PAGE_NAMES[4]:
    render_report_page()
