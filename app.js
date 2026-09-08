const ICONS = {
  upload: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 16V4m0 0-4 4m4-4 4 4"/><path d="M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/></svg>',
  graph: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5.5" cy="6" r="2.2"/><circle cx="18.5" cy="5.5" r="2.2"/><circle cx="12.5" cy="18" r="2.2"/><path d="M7.6 6h8.6M6.7 7.9l4.6 8.2M17.3 7.6l-3.7 8.3"/></svg>',
  match: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.6"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/></svg>',
  route: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5.5" cy="18.5" r="2.2"/><circle cx="18.5" cy="5.5" r="2.2"/><path d="M7.7 18.5h6.1a3.5 3.5 0 0 0 0-7H10.2a3.5 3.5 0 0 1 0-7h6.1"/></svg>',
  report: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2.8h8l4 4V21H6z"/><path d="M14 2.8v4h4"/><path d="M9 11.5h6M9 15h6"/></svg>',
  menu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>',
  reset: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 7.5A8 8 0 1 1 4 13"/><path d="M4.5 3.5v4h4"/></svg>',
  refresh: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11a8 8 0 0 0-15-3M4 13a8 8 0 0 0 15 3"/><path d="M4.5 4v5h5M19.5 20v-5h-5"/></svg>',
  cloud: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 18.5a5.2 5.2 0 0 1 .4-10.4 6.2 6.2 0 0 1 11.8 1.2 4.1 4.1 0 0 1-.7 8.2"/></svg>',
  check: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>',
  search: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.8"/><path d="m16.2 16.2 4 4"/></svg>',
  plus: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',
  minus: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14"/></svg>',
  fit: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 3H4v4M16 3h4v4M8 21H4v-4M16 21h4v-4"/></svg>',
  download: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v12m0 0 4-4m-4 4-4-4"/><path d="M4 18v2h16v-2"/></svg>',
  file: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 2.8h8l4 4V21H6z"/><path d="M14 2.8v4h4"/></svg>',
  image: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="4.5" width="17" height="15" rx="2"/><circle cx="8.2" cy="9.5" r="1.5"/><path d="m5 18 4.8-5 3.4 3 2.2-2.4L19 18"/></svg>',
  video: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="13" height="14" rx="2"/><path d="m16.5 10 4-3v10l-4-3"/></svg>',
  audio: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/></svg>',
  target: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.6"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/></svg>'
};

const CANDIDATE = {
  name: '林知夏',
  shortName: '林',
  school: '南方工业大学 · 智能制造工程',
  status: '本科在读',
  focus: '智能制造AI应用与工业数据分析',
  summary: '拥有4段智能制造与数据分析项目经历，熟悉视觉检测、能耗预测与产线数据复盘。'
};

const PERSONAL_SKILLS = [
  { id: 'python', name: 'Python', type: 'hard', level: 90, desc: '熟练进行数据处理、模型训练与自动化脚本开发。' },
  { id: 'ml', name: '机器学习', type: 'hard', level: 88, desc: '掌握监督学习、时序预测与模型评估方法。' },
  { id: 'pytorch', name: 'PyTorch', type: 'hard', level: 85, desc: '可完成模型构建、训练与精度调优。' },
  { id: 'opencv', name: 'OpenCV', type: 'hard', level: 80, desc: '使用图像预处理与视觉特征提取完成项目开发。' },
  { id: 'analysis', name: '数据分析', type: 'hard', level: 86, desc: '能独立完成业务指标拆解、分析并给出结论。' },
  { id: 'sql', name: 'SQL基础', type: 'hard', level: 72, desc: '可进行单表与多表查询，复杂数据建模仍在提升。' },
  { id: 'powerbi', name: 'Power BI', type: 'hard', level: 78, desc: '可制作可交互的产线与能耗分析看板。' },
  { id: 'linux', name: 'Linux基础', type: 'hard', level: 70, desc: '熟悉命令行、文件权限与简单脚本运维。' },
  { id: 'comm', name: '跨部门沟通', type: 'soft', level: 88, desc: '在项目协调中连接算法、生产与设备团队。' },
  { id: 'push', name: '项目推进', type: 'soft', level: 86, desc: '能拆解里程碑，协调资源并推动交付。' },
  { id: 'solve', name: '问题拆解', type: 'soft', level: 89, desc: '习惯把模糊问题转化为可验证的技术子问题。' },
  { id: 'doc', name: '技术文档', type: 'soft', level: 82, desc: '可输出调研、方案与复盘文档。' },
  { id: 'smart', name: '智能制造', type: 'domain', level: 84, desc: '了解离散制造流程与数字化改造场景。' },
  { id: 'iot', name: '工业物联网', type: 'domain', level: 76, desc: '了解数据采集、设备联网与协议基础。' },
  { id: 'energy', name: '新能源基础', type: 'domain', level: 70, desc: '了解动力电池与新能源生产链路。' },
  { id: 'quality', name: '质量管理', type: 'domain', level: 78, desc: '熟悉SPC、FMEA等基础质量管理方法。' },
  { id: 'digital', name: '数字化转型', type: 'domain', level: 82, desc: '参与过数字化项目需求梳理与落地评估。' },
  { id: 'cet6', name: '大学英语六级', type: 'cert', level: 86, desc: '可阅读英文论文与技术文档。' },
  { id: 'ncre3', name: '计算机等级三级', type: 'cert', level: 80, desc: '计算机基础与数据库方向认证。' },
  { id: 'cda', name: '数据分析师认证', type: 'cert', level: 78, desc: '完成数据分析理论、SQL与可视化认证。' }
];

const PERSONAL_PROJECTS = [
  {
    id: 'vision',
    name: '锂电池产线缺陷检测',
    time: '2025.06 - 2025.09',
    summary: '基于YOLOv8与OpenCV完成电芯表面缺陷检测，覆盖样本增强、模型训练与质检结果可视化。',
    skills: ['python', 'pytorch', 'opencv', 'ml', 'push']
  },
  {
    id: 'energy',
    name: '产线能耗预测平台',
    time: '2025.03 - 2025.06',
    summary: '融合历史能耗与排产数据构建时序预测模型，用Power BI输出车间级节能分析看板。',
    skills: ['python', 'ml', 'analysis', 'sql', 'powerbi']
  },
  {
    id: 'twin',
    name: '设备数字孪生实训',
    time: '2024.10 - 2025.01',
    summary: '完成设备三维模型与运行数据的孪生映射，验证工业物联网数据采集到展示的完整链路。',
    skills: ['smart', 'iot', 'linux', 'solve']
  },
  {
    id: 'review',
    name: '跨部门数据复盘机制',
    time: '2024.07 - 2024.09',
    summary: '联合生产、质量与设备部门建立周度数据复盘机制，输出可复用的指标口径文档。',
    skills: ['comm', 'doc', 'push', 'analysis', 'quality']
  }
];

const JOB_GROUPS = [
  {
    key: 'job-a',
    title: 'AI算法工程师（智能制造）',
    company: '星川智造',
    city: '深圳',
    salary: '18-28K · 14薪',
    industry: '智能制造',
    tags: ['深度学习', '机器视觉', '工业AI'],
    summary: '负责锂电池产线视觉质检、能耗预测与AI模型在工业现场的部署落地。',
    score: 78,
    grade: '较匹配',
    dims: [
      { label: '硬技能', mine: 78, target: 92 },
      { label: '软技能', mine: 88, target: 80 },
      { label: '项目经历', mine: 74, target: 90 },
      { label: '学历证书', mine: 82, target: 84 },
      { label: '行业知识', mine: 78, target: 90 },
      { label: '岗位契合', mine: 70, target: 100 }
    ],
    requirements: {
      required: [
        { name: 'Python', level: 96 },
        { name: 'PyTorch', level: 92 },
        { name: '机器学习', level: 90 },
        { name: '计算机视觉', level: 88 },
        { name: '数据分析', level: 86 },
        { name: '模型部署与优化', level: 84 },
        { name: '工业项目落地', level: 86 },
        { name: 'SQL进阶', level: 80 }
      ],
      preferred: [
        { name: 'Docker/Linux', level: 76 },
        { name: '边缘计算', level: 72 },
        { name: '技术文档', level: 72 },
        { name: '跨部门沟通', level: 76 }
      ]
    },
    gaps: [
      { name: '模型部署与优化', kind: 'required', reason: '岗位要求掌握ONNX/TensorRT等部署工具，当前档案缺少端侧部署或模型加速实践。', action: '阶段 1：深度学习模型工程化' },
      { name: 'SQL进阶与数据治理', kind: 'weak', reason: '已有SQL基础，但尚缺少窗口函数、数据建模和产线数据治理场景。', action: '阶段 2：数据能力进阶' },
      { name: '边缘计算与设备联调', kind: 'weak', reason: '有数字孪生实训基础，缺少边缘设备推理与现场联调经验。', action: '阶段 3：边缘侧工业AI实践' },
      { name: '工业视觉量化落地', kind: 'required', reason: '缺陷检测停留在训练阶段，需补充量化、精度验证与产线验证产出。', action: '阶段 4：综合项目与成果复盘' }
    ],
    path: [
      { stage: '阶段 1', title: '深度学习模型工程化', weeks: '2周', goal: '补齐ONNX模型转换、推理部署与精度评估方法。', resources: [{ name: 'PyTorch模型部署实战', type: '课程', meta: '2周 · 模型转换与推理' }, { name: 'ONNX Runtime 官方文档', type: '资料', meta: '1周 · API与量化' }, { name: '边缘端推理部署案例', type: '项目', meta: '2周 · Jetson/工控机' }] },
      { stage: '阶段 2', title: '数据能力进阶', weeks: '2周', goal: '掌握窗口函数、数据建模和基础数据治理。', resources: [{ name: 'SQL进阶训练营', type: '课程', meta: '1周 · 窗口函数与优化' }, { name: '产线数据仓库案例', type: '项目', meta: '1周 · ETL与指标口径' }, { name: '数据治理基础课', type: '课程', meta: '1周 · 质量与血缘' }] },
      { stage: '阶段 3', title: '边缘侧工业AI实践', weeks: '2周', goal: '完成设备数据接入、模型量化与边缘推理验证。', resources: [{ name: 'Docker容器化部署', type: '课程', meta: '1周 · 镜像与容器' }, { name: 'Modbus/OPC UA采集', type: '项目', meta: '1周 · 设备联调' }, { name: '工业AI边缘部署手册', type: '资料', meta: '边看边做' }] },
      { stage: '阶段 4', title: '综合项目与成果复盘', weeks: '3周', goal: '形成一份可写入简历的端到端工业AI项目。', resources: [{ name: '工业质检开源数据集实战', type: '项目', meta: '2周 · 完整pipeline' }, { name: '模型量化与速度优化', type: '课程', meta: '1周 · 指标对比' }, { name: '项目复盘文档模板', type: '资料', meta: '按STAR整理' }] }
    ]
  },
  {
    key: 'job-b',
    title: '新能源数据分析师',
    company: '青穹能源科技',
    city: '上海',
    salary: '15-23K · 13薪',
    industry: '新能源',
    tags: ['数据分析', '商业洞察', '能源业务'],
    summary: '围绕光伏与储能业务开展经营分析、产能预测和业务复盘。',
    score: 72,
    grade: '可尝试',
    dims: [
      { label: '硬技能', mine: 74, target: 88 },
      { label: '软技能', mine: 88, target: 82 },
      { label: '项目经历', mine: 78, target: 82 },
      { label: '学历证书', mine: 84, target: 86 },
      { label: '行业知识', mine: 64, target: 92 },
      { label: '岗位契合', mine: 72, target: 100 }
    ],
    requirements: {
      required: [
        { name: 'Python', level: 92 },
        { name: '数据分析', level: 90 },
        { name: 'SQL进阶', level: 86 },
        { name: '数据可视化', level: 88 },
        { name: '统计学', level: 84 },
        { name: '商业分析', level: 82 },
        { name: 'Power BI', level: 84 }
      ],
      preferred: [
        { name: '数据仓库', level: 78 },
        { name: '能源业务理解', level: 80 },
        { name: 'A/B实验思维', level: 74 },
        { name: '沟通表达', level: 80 }
      ]
    },
    gaps: [
      { name: '能源行业业务知识', kind: 'required', reason: '对光伏、储能、电价机制的理解较浅，需要补行业术语与关键指标。', action: '阶段 2：能源业务学习' },
      { name: 'SQL进阶与数据建模', kind: 'weak', reason: '日常查询可完成，缺少大型数据集查询和指标仓库建模经验。', action: '阶段 1：SQL与数据建模进阶' },
      { name: '商业分析方法', kind: 'required', reason: '需补结构化业务拆解、AB实验和归因分析方法。', action: '阶段 3：商业分析能力' },
      { name: '业务看板落地', kind: 'weak', reason: '已有Power BI基础，需要补齐多业务口径看板搭建。', action: '阶段 4：综合经营分析项目' }
    ],
    path: [
      { stage: '阶段 1', title: 'SQL与数据建模进阶', weeks: '2周', goal: '从查询能力提升到数据建模与口径管理。', resources: [{ name: 'SQL查询性能优化', type: '课程', meta: '1周 · 大表查询' }, { name: '指标口径管理案例', type: '项目', meta: '1周 · 指标字典' }, { name: '数据集市设计', type: '资料', meta: '建模方法' }] },
      { stage: '阶段 2', title: '能源业务学习', weeks: '2周', goal: '建立新能源行业的关键业务指标地图。', resources: [{ name: '光伏行业分析报告', type: '资料', meta: '1周 · 产业链阅读' }, { name: '储能商业模式拆解', type: '课程', meta: '1周 · 商业模式' }, { name: '新能源经营看板案例', type: '项目', meta: '1周 · 指标复现' }] },
      { stage: '阶段 3', title: '商业分析能力', weeks: '1周', goal: '掌握业务问题拆解与AB实验基础。', resources: [{ name: '数据分析思维训练', type: '课程', meta: '3天 · 问题拆解' }, { name: 'AB实验设计入门', type: '课程', meta: '2天 · 假设检验' }, { name: '归因分析方法', type: '资料', meta: '方法框架' }] },
      { stage: '阶段 4', title: '综合经营分析项目', weeks: '3周', goal: '形成一份可复述的经营分析案例。', resources: [{ name: '模拟业务数据仓库', type: '项目', meta: '1周 · 数据准备' }, { name: '经营驾驶舱复刻', type: '项目', meta: '1周 · Power BI' }, { name: '分析报告写作模板', type: '资料', meta: '结论先行' }] }
    ]
  },
  {
    key: 'job-c',
    title: '工业AI解决方案工程师',
    company: '启航工业软件',
    city: '苏州',
    salary: '16-24K · 14薪',
    industry: '工业软件',
    tags: ['工业AI', '方案设计', '项目交付'],
    summary: '面向制造企业提供工业AI方案咨询、系统集成与项目交付。',
    score: 74,
    grade: '较匹配',
    dims: [
      { label: '硬技能', mine: 75, target: 88 },
      { label: '软技能', mine: 90, target: 88 },
      { label: '项目经历', mine: 78, target: 86 },
      { label: '学历证书', mine: 82, target: 84 },
      { label: '行业知识', mine: 84, target: 90 },
      { label: '岗位契合', mine: 72, target: 100 }
    ],
    requirements: {
      required: [
        { name: 'Python', level: 92 },
        { name: '机器学习', level: 88 },
        { name: '工业场景理解', level: 90 },
        { name: '系统集成', level: 82 },
        { name: '方案设计', level: 84 },
        { name: '项目推进', level: 86 },
        { name: '技术方案文档', level: 82 }
      ],
      preferred: [
        { name: '数字孪生', level: 78 },
        { name: 'Docker/K8s', level: 74 },
        { name: '客户沟通', level: 84 },
        { name: 'API接口开发', level: 76 }
      ]
    },
    gaps: [
      { name: '工业系统集成', kind: 'required', reason: '需要理解MES/WMS与算法系统的接口对接，目前缺少系统集成项目。', action: '阶段 1：系统集成与接口' },
      { name: '数字孪生深化', kind: 'weak', reason: '有实训基础，但需要补模型轻量化与业务场景联动。', action: '阶段 2：数字孪生与场景联动' },
      { name: '方案设计与汇报', kind: 'required', reason: '需从技术文档提升到面向客户的方案架构与成本估算。', action: '阶段 3：解决方案能力' },
      { name: '容器化交付', kind: 'weak', reason: '了解Docker基础概念，尚缺完整交付部署经验。', action: '阶段 4：工业AI交付实战' }
    ],
    path: [
      { stage: '阶段 1', title: '系统集成与接口', weeks: '2周', goal: '掌握工业系统API对接和数据同步方式。', resources: [{ name: 'REST API设计', type: '课程', meta: '1周 · 接口规范' }, { name: 'MES系统架构入门', type: '资料', meta: '1周 · 业务理解' }, { name: '数据集成模拟项目', type: '项目', meta: '1周 · ETL对接' }] },
      { stage: '阶段 2', title: '数字孪生与场景联动', weeks: '2周', goal: '把孪生能力落到实际业务场景。', resources: [{ name: '数字孪生案例解析', type: '课程', meta: '1周 · 场景设计' }, { name: '模型轻量化部署', type: '课程', meta: '1周 · 边缘运行' }, { name: '产线孪生小项目', type: '项目', meta: '1周 · 业务联动' }] },
      { stage: '阶段 3', title: '解决方案能力', weeks: '2周', goal: '从写代码扩展到写方案、讲价值。', resources: [{ name: '售前方案结构方法', type: '课程', meta: '1周 · 方案框架' }, { name: '项目成本估算', type: '资料', meta: '2天 · 报价逻辑' }, { name: '客户汇报演练', type: '项目', meta: '1周 · 模拟讲标' }] },
      { stage: '阶段 4', title: '工业AI交付实战', weeks: '3周', goal: '完成一个可演示的端到端方案项目。', resources: [{ name: '容器化交付课程', type: '课程', meta: '1周 · Docker/K8s' }, { name: '工业视觉方案实战', type: '项目', meta: '2周 · 集成部署' }, { name: '项目验收文档模板', type: '资料', meta: '验收闭环' }] }
    ]
  }
];

const TYPE_META = {
  core: { label: '用户画像', color: '#17211f' },
  hard: { label: '硬技能', color: '#0f766e' },
  soft: { label: '软技能', color: '#c77412' },
  domain: { label: '领域知识', color: '#2563eb' },
  cert: { label: '证书', color: '#c4487b' },
  project: { label: '项目经历', color: '#d55445' },
  required: { label: '必需能力', color: '#0f766e' },
  preferred: { label: '偏好能力', color: '#c77412' }
};

const state = {
  currentView: 'upload',
  currentJob: JOB_GROUPS[0],
  graphMode: 'personal',
  graphFilter: 'all',
  graphQuery: '',
  graphZoom: 1,
  graphPan: { x: 0, y: 0 },
  selectedNode: null,
  personalGraph: null,
  jobGraph: null,
  defaultFiles: [
    { name: '林知夏-简历.pdf', size: '1.2 MB', type: 'pdf' },
    { name: '成绩单.png', size: '860 KB', type: 'image' },
    { name: '自我介绍.mp4', size: '48 MB', type: 'video' }
  ]
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

function esc(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[char]));
}

function fileTypeMeta(name) {
  const ext = name.split('.').pop().toLowerCase();
  if (['png', 'jpg', 'jpeg', 'webp'].includes(ext)) return { icon: 'image', className: 'img' };
  if (['mp3', 'wav', 'm4a', 'aac'].includes(ext)) return { icon: 'audio', className: 'audio' };
  if (['mp4', 'mov', 'webm', 'avi'].includes(ext)) return { icon: 'video', className: 'mp4' };
  if (['pdf'].includes(ext)) return { icon: 'file', className: 'pdf' };
  return { icon: 'file', className: 'pdf' };
}

function formatFileSize(size) {
  if (!size || size <= 0) return '0 KB';
  if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function buildPersonalGraphData() {
  const nodes = [
    { id: 'core', label: CANDIDATE.name, type: 'core', level: 100, desc: CANDIDATE.school, evidence: [] }
  ];
  const links = [];
  const certIds = [];

  PERSONAL_SKILLS.forEach((skill) => {
    nodes.push({
      id: `skill-${skill.id}`,
      label: skill.name,
      type: skill.type,
      level: skill.level,
      desc: skill.desc,
      evidence: []
    });
    if (skill.type === 'cert') certIds.push(`skill-${skill.id}`);
  });

  PERSONAL_PROJECTS.forEach((project) => {
    nodes.push({
      id: `project-${project.id}`,
      label: project.name,
      type: 'project',
      level: 86,
      time: project.time,
      desc: project.summary,
      evidence: []
    });
  });

  PERSONAL_SKILLS.forEach((skill) => {
    if (skill.type !== 'cert') links.push({ source: 'core', target: `skill-${skill.id}`, rel: '具备' });
  });
  certIds.forEach((cert) => links.push({ source: 'core', target: cert, rel: '获得' }));

  PERSONAL_PROJECTS.forEach((project) => {
    project.skills.forEach((skillId) => {
      links.push({
        source: `project-${project.id}`,
        target: `skill-${skillId}`,
        rel: '项目体现'
      });
    });
  });

  return { nodes, links };
}

function buildJobGraphData(job) {
  const nodes = [
    { id: 'core', label: job.title, type: 'core', level: 100, desc: `${job.company} · ${job.city}`, evidence: [] }
  ];
  const links = [];
  job.requirements.required.forEach((item) => {
    nodes.push({ id: `req-${item.name}`, label: item.name, type: 'required', level: item.level, desc: '岗位JD任职要求中明确列出，属于必需能力。', evidence: [] });
    links.push({ source: 'core', target: `req-${item.name}`, rel: '必需' });
  });
  job.requirements.preferred.forEach((item) => {
    nodes.push({ id: `pref-${item.name}`, label: item.name, type: 'preferred', level: item.level, desc: '岗位JD标记为加分项，缺失时降低匹配得分但不直接淘汰。', evidence: [] });
    links.push({ source: 'core', target: `pref-${item.name}`, rel: '偏好' });
  });
  return { nodes, links };
}

function layoutGraph(rawNodes, links) {
  const width = 1000;
  const height = 700;
  const centerX = width / 2;
  const centerY = height / 2;
  const nodes = rawNodes.map((node) => ({ ...node }));
  const typeAnchors = {
    core: { angle: 0, spread: 0, radius: 0 },
    hard: { angle: -1.45, spread: 0.85, radius: 265 },
    soft: { angle: -2.55, spread: 0.62, radius: 215 },
    domain: { angle: 0.45, spread: 0.75, radius: 285 },
    cert: { angle: 1.85, spread: 0.42, radius: 270 },
    project: { angle: 2.45, spread: 0.72, radius: 230 },
    required: { angle: -1.2, spread: 1.3, radius: 300 },
    preferred: { angle: 2.1, spread: 1.1, radius: 285 }
  };

  const grouped = {};
  nodes.forEach((node) => {
    if (!grouped[node.type]) grouped[node.type] = [];
    grouped[node.type].push(node);
  });

  Object.keys(grouped).forEach((type) => {
    const config = typeAnchors[type] || { angle: 0, spread: 1, radius: 220 };
    const list = grouped[type];
    list.forEach((node, index) => {
      const offset = list.length > 1 ? ((index - (list.length - 1) / 2) * 0.17) * (config.spread || 1) : 0;
      const angle = config.angle + offset;
      const radius = config.radius || 0;
      node.x = centerX + Math.cos(angle) * radius;
      node.y = centerY + Math.sin(angle) * radius;
      node.fx = node.x;
      node.fy = node.y;
    });
  });

  nodes.forEach((node) => {
    node.x += (Math.random() - 0.5) * 18;
    node.y += (Math.random() - 0.5) * 18;
  });

  const nodeById = Object.fromEntries(nodes.map((node) => [node.id, node]));
  for (let iteration = 0; iteration < 120; iteration += 1) {
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        if (a.id === 'core' || b.id === 'core') continue;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.max(0.01, Math.sqrt(dx * dx + dy * dy));
        const force = dist < 105 ? ((105 - dist) * 0.018) : 0;
        const angle = Math.atan2(dy, dx);
        a.x -= Math.cos(angle) * force;
        a.y -= Math.sin(angle) * force;
        b.x += Math.cos(angle) * force;
        b.y += Math.sin(angle) * force;
      }
    }
    links.forEach((link) => {
      const source = nodeById[link.source];
      const target = nodeById[link.target];
      if (!source || !target || source.id === 'core' || target.id === 'core') return;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const dist = Math.max(0.01, Math.sqrt(dx * dx + dy * dy));
      const expected = 175;
      const force = (dist - expected) * 0.022;
      const angle = Math.atan2(dy, dx);
      source.x += Math.cos(angle) * force * 0.5;
      source.y += Math.sin(angle) * force * 0.5;
      target.x -= Math.cos(angle) * force * 0.5;
      target.y -= Math.sin(angle) * force * 0.5;
    });
    nodes.forEach((node) => {
      if (node.id === 'core') return;
      node.x += (node.fx - node.x) * 0.014;
      node.y += (node.fy - node.y) * 0.014;
      node.x = Math.min(940, Math.max(60, node.x));
      node.y = Math.min(650, Math.max(50, node.y));
    });
  }
  return nodes;
}

function radiusForNode(node) {
  if (node.type === 'core') return 40;
  if (node.type === 'project') return 28;
  if (node.type === 'hard' || node.type === 'required') return 25;
  if (node.type === 'soft' || node.type === 'preferred') return 23;
  if (node.type === 'cert') return 19;
  return 22;
}

function applyIcons() {
  $$('[data-icon]').forEach((el) => {
    const name = el.dataset.icon;
    if (ICONS[name]) el.innerHTML = ICONS[name];
  });
}

function renderGraph() {
  let data;
  if (state.graphMode === 'job') {
    data = buildJobGraphData(state.currentJob);
    state.jobGraph = data;
  } else {
    data = buildPersonalGraphData();
    state.personalGraph = data;
  }
  state.selectedNode = null;
  renderGraphDetail(null);
  renderGraphFilters(data);

  const laidNodes = layoutGraph(data.nodes, data.links);
  const nodeById = Object.fromEntries(laidNodes.map((node) => [node.id, node]));
  const links = data.links
    .map((link) => {
      const source = nodeById[link.source];
      const target = nodeById[link.target];
      if (!source || !target) return null;
      const color = TYPE_META[target.type] ? TYPE_META[target.type].color : '#a7bbb6';
      return {
        ...link,
        source,
        target,
        color,
        rel: link.rel || ''
      };
    })
    .filter(Boolean);

  const nodeMarkup = laidNodes.map((node) => {
    const meta = TYPE_META[node.type] || TYPE_META.hard;
    const radius = radiusForNode(node);
    const textY = node.type === 'core' ? node.y + 54 : node.y + radius + 18;
    return `
      <g class="graph-node" data-node-id="${esc(node.id)}" transform="translate(${node.x}, ${node.y})">
        <circle class="node-ring" r="${radius + 6}" fill="${meta.color}" fill-opacity="0.14"></circle>
        <circle class="node-core" r="${radius}" fill="${meta.color}" stroke="#fff" stroke-width="${node.type === 'core' ? 5 : 2}"></circle>
        ${node.type === 'core' ? `<circle class="pulse-ring" r="${radius + 9}" fill="none" stroke="${meta.color}" stroke-width="2" stroke-opacity="0.35"></circle>` : ''}
        <text class="node-label" x="0" y="${node.type === 'core' ? 6 : textY - node.y}">${esc(node.label.length > 11 ? `${node.label.slice(0, 10)}…` : node.label)}</text>
      </g>
    `;
  }).join('');

  const linkMarkup = links.map((link) => `
    <line class="graph-link" data-source="${esc(link.source.id)}" data-target="${esc(link.target.id)}"
      x1="${link.source.x}" y1="${link.source.y}" x2="${link.target.x}" y2="${link.target.y}"
      stroke="${link.color}" stroke-dasharray="${link.rel === '项目体现' ? '2 6' : ''}"></line>
  `).join('');

  const canvas = $('#graphCanvas');
  canvas.innerHTML = `
    <svg viewBox="0 0 1000 700" aria-label="能力图谱">
      <g class="graph-viewport" transform="translate(${state.graphPan.x}, ${state.graphPan.y}) scale(${state.graphZoom})">
        ${linkMarkup}
        ${nodeMarkup}
      </g>
    </svg>
  `;

  $('#graphNodeCount').textContent = `${laidNodes.length} 个节点`;
  $('#graphLinkCount').textContent = `${links.length} 条关系`;
  $('#graphSearch').value = '';
  state.graphQuery = '';
  state.graphFilter = 'all';

  const svg = $('svg', canvas);
  svg.addEventListener('click', (event) => {
    const node = event.target.closest('.graph-node');
    if (!node) return;
    const nodeId = node.dataset.nodeId;
    const found = laidNodes.find((item) => item.id === nodeId);
    if (found) {
      selectGraphNode(found, data);
      svg.querySelectorAll('.graph-node.selected').forEach((el) => el.classList.remove('selected'));
      node.classList.add('selected');
    }
  });

  $$('.filter-chip', $('#graphFilters')).forEach((button) => {
    button.addEventListener('click', () => {
      state.graphFilter = button.dataset.type;
      $$('.filter-chip', $('#graphFilters')).forEach((item) => item.classList.toggle('active', item === button));
      applyGraphFilter();
    });
  });

  applyGraphFilter();
}

function renderGraphFilters(data) {
  const counts = {};
  data.nodes.forEach((node) => {
    if (node.type === 'core') return;
    counts[node.type] = (counts[node.type] || 0) + 1;
  });
  const types = Object.keys(counts);
  const chips = [
    `<button class="filter-chip active" data-type="all">全部 ${data.nodes.length}</button>`,
    ...types.map((type) => {
      const meta = TYPE_META[type] || TYPE_META.hard;
      return `<button class="filter-chip" data-type="${type}">${meta.label} ${counts[type]}</button>`;
    })
  ];
  $('#graphFilters').innerHTML = chips.join('');
}

function applyGraphFilter() {
  const query = state.graphQuery.trim().toLowerCase();
  const type = state.graphFilter;
  const svg = $('svg', $('#graphCanvas'));
  if (!svg) return;
  $$('.graph-node', svg).forEach((nodeEl) => {
    const nodeId = nodeEl.dataset.nodeId;
    const node = nodeByIdInCurrentGraph(nodeId);
    if (!node) return;
    const typeMatch = type === 'all' || node.type === type;
    const queryMatch = !query || node.label.toLowerCase().includes(query);
    const visible = typeMatch && queryMatch;
    nodeEl.classList.toggle('muted', !visible);
    nodeEl.style.opacity = visible ? '1' : '0.12';
  });
  $$('.graph-link', svg).forEach((link) => {
    const sourceEl = svg.querySelector(`.graph-node[data-node-id="${link.dataset.source}"]`);
    const targetEl = svg.querySelector(`.graph-node[data-node-id="${link.dataset.target}"]`);
    const visible = sourceEl && targetEl && sourceEl.style.opacity !== '0.12' && targetEl.style.opacity !== '0.12';
    link.style.opacity = visible ? '0.7' : '0.06';
  });
}

function nodeByIdInCurrentGraph(id) {
  if (state.graphMode === 'job') return state.jobGraph?.nodes.find((node) => node.id === id);
  return state.personalGraph?.nodes.find((node) => node.id === id);
}

function selectGraphNode(node, data) {
  state.selectedNode = node.id;
  const meta = TYPE_META[node.type] || TYPE_META.hard;
  const extra = data.nodes.find((item) => item.id === node.id) || {};
  let content;
  if (node.type === 'core') {
    content = `
      <div class="detail-card">
        <span class="detail-type" style="background:${meta.color}">${meta.label}</span>
        <h3 class="detail-name">${esc(node.label)}</h3>
        <p class="detail-evidence">${esc(node.desc || '')}</p>
        <div class="detail-block">
          <h4>摘要</h4>
          <p class="detail-desc">${esc(CANDIDATE.summary)}</p>
        </div>
      </div>
    `;
  } else if (node.type === 'project') {
    content = `
      <div class="detail-card">
        <span class="detail-type" style="background:${meta.color}">项目经历</span>
        <h3 class="detail-name">${esc(node.label)}</h3>
        <p class="detail-evidence">${esc(node.time || '')}</p>
        <div class="detail-block">
          <h4>项目描述</h4>
          <p class="detail-desc">${esc(node.desc || '')}</p>
        </div>
        <div class="detail-block">
          <h4>关联技能</h4>
          <div>${(extra.skills || []).map((skill) => `<span class="evidence-tag">${esc(skill)}</span>`).join('') || '项目图谱已关联'}</div>
        </div>
      </div>
    `;
  } else {
    const evidence = (extra.evidence || []).length
      ? extra.evidence
      : relatedProjectNames(node.id);
    content = `
      <div class="detail-card">
        <span class="detail-type" style="background:${meta.color}">${meta.label}</span>
        <h3 class="detail-name">${esc(node.label)}</h3>
        <p class="detail-evidence">${esc(node.desc || '')}</p>
        <div class="detail-block">
          <h4>掌握水平</h4>
          <p>${node.level >= 85 ? '熟练' : node.level >= 72 ? '可独立应用' : '基础入门'} · ${node.level}分</p>
          <div class="level-bar"><i style="width:${node.level}%;background:${meta.color}"></i></div>
        </div>
        ${evidence.length ? `<div class="detail-block"><h4>证据来源</h4><div>${evidence.map((item) => `<span class="evidence-tag">${esc(item)}</span>`).join('')}</div></div>` : ''}
      </div>
    `;
  }
  const panel = $('#graphDetail');
  panel.innerHTML = content;
}

function relatedProjectNames(skillNodeId) {
  if (!state.personalGraph) return [];
  return state.personalGraph.links
    .filter((link) => link.target === skillNodeId && link.source.startsWith('project-'))
    .map((link) => {
      const node = state.personalGraph.nodes.find((item) => item.id === link.source);
      return node ? node.label : '';
    })
    .filter(Boolean);
}

function renderGraphDetail(node) {
  const panel = $('#graphDetail');
  if (!node) {
    panel.innerHTML = `
      <div class="detail-empty">
        <div class="detail-symbol" data-icon="graph"></div>
        <h3>选择节点查看详情</h3>
        <p>硬技能、软技能、项目与证书会在这里展示证据来源。</p>
      </div>
    `;
    applyIcons();
    return;
  }
  selectGraphNode(node, state.graphMode === 'job' ? state.jobGraph : state.personalGraph);
}

function buildPointList(cx, cy, radius, angle, values) {
  return values.map((value) => {
    const x = cx + Math.cos(angle) * (radius * value / 100);
    const y = cy + Math.sin(angle) * (radius * value / 100);
    return `${x},${y}`;
  }).join(' ');
}

function renderRadar(svgElement, dims, compact = false) {
  if (!svgElement) return;
  const width = compact ? 410 : 440;
  const height = compact ? 320 : 380;
  const cx = width / 2;
  const cy = height / 2 + (compact ? 6 : 12);
  const maxRadius = compact ? 112 : 132;
  const angleStep = (Math.PI * 2) / dims.length;
  const startAngle = -Math.PI / 2;
  const ringMarkup = [25, 50, 75, 100].map((level) => {
    const points = dims.map((_, index) => {
      const x = cx + Math.cos(startAngle + angleStep * index) * (maxRadius * level / 100);
      const y = cy + Math.sin(startAngle + angleStep * index) * (maxRadius * level / 100);
      return `${x},${y}`;
    }).join(' ');
    return `<polygon points="${points}" fill="none" stroke="#dce6e3" stroke-width="1"></polygon>`;
  }).join('');
  const axisMarkup = dims.map((dim, index) => {
    const angle = startAngle + angleStep * index;
    const x = cx + Math.cos(angle) * maxRadius;
    const y = cy + Math.sin(angle) * maxRadius;
    const labelX = cx + Math.cos(angle) * (maxRadius + 26);
    const labelY = cy + Math.sin(angle) * (maxRadius + 24);
    const anchor = Math.cos(angle) > 0.3 ? 'start' : (Math.cos(angle) < -0.3 ? 'end' : 'middle');
    return `
      <line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="#e6eeeb"></line>
      <text x="${labelX}" y="${labelY}" text-anchor="${anchor}" dominant-baseline="middle" font-size="11" fill="#556461">${esc(dim.label)}</text>
    `;
  }).join('');
  const minePoints = dims.map((dim, index) => {
    const angle = startAngle + angleStep * index;
    const x = cx + Math.cos(angle) * (maxRadius * dim.mine / 100);
    const y = cy + Math.sin(angle) * (maxRadius * dim.mine / 100);
    return `${x},${y}`;
  }).join(' ');
  const targetPoints = dims.map((dim, index) => {
    const angle = startAngle + angleStep * index;
    const x = cx + Math.cos(angle) * (maxRadius * dim.target / 100);
    const y = cy + Math.sin(angle) * (maxRadius * dim.target / 100);
    return `${x},${y}`;
  }).join(' ');

  svgElement.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svgElement.innerHTML = `
    ${ringMarkup}
    ${axisMarkup}
    <polygon points="${targetPoints}" fill="#c77412" fill-opacity="0.08" stroke="#c77412" stroke-width="2"></polygon>
    <polygon points="${minePoints}" fill="#0f766e" fill-opacity="0.2" stroke="#0f766e" stroke-width="2.4"></polygon>
  `;
}

function renderJobSelector() {
  const cards = JOB_GROUPS.map((job) => {
    const selected = job.key === state.currentJob.key ? ' selected' : '';
    return `
      <button class="job-card${selected}" data-job="${esc(job.key)}">
        <span class="job-card-top">
          <strong>${esc(job.title)}</strong>
          <span class="job-score">${job.score}</span>
        </span>
        <span class="job-company">${esc(job.company)}</span>
        <span class="job-location">${esc(job.city)} · ${esc(job.salary)}</span>
        <span class="job-tags">${job.tags.map((tag) => `<span class="job-tag">${esc(tag)}</span>`).join('')}</span>
      </button>
    `;
  }).join('');
  $('#jobCards').innerHTML = cards;
}

function renderMatchView() {
  const job = state.currentJob;
  $('#scoreGrade').textContent = job.grade;
  $('#scoreGrade').style.background = job.score >= 75 ? 'var(--teal-soft)' : 'var(--amber-soft)';
  $('#scoreGrade').style.color = job.score >= 75 ? 'var(--teal)' : 'var(--amber)';
  $('#matchTotal').textContent = job.score;
  $('#focusJobTitle').textContent = job.title;
  $('#focusJobMeta').textContent = `${job.company} · ${job.city} · ${job.salary}`;
  $('#focusJobDesc').textContent = job.summary;
  $('#focusJobTags').innerHTML = job.tags.map((tag) => `<span>${esc(tag)}</span>`).join('');
  $('#scoreBars').innerHTML = job.dims.map((dim) => `
    <div class="score-row">
      <span>${esc(dim.label)}</span>
      <div class="track"><i style="width:${dim.mine}%;background:${dim.mine >= dim.target ? 'var(--teal)' : 'var(--amber)'}"></i></div>
      <strong>${dim.mine}</strong>
    </div>
  `).join('');
  $('#gapList').innerHTML = job.gaps.map((gap) => {
    const label = gap.kind === 'required' ? '必需能力' : '可提升项';
    const className = gap.kind === 'required' ? 'required' : 'weak';
    return `
      <div class="gap-item">
        <span class="gap-name">
          ${esc(gap.name)}
          <span class="gap-type ${className}">${label}</span>
        </span>
        <span class="gap-arrow">去补齐 →</span>
        <p>${esc(gap.reason)}</p>
      </div>
    `;
  }).join('');
  $('#sideScore').textContent = job.score;
  renderRadar($('#radarChart'), job.dims);
  renderJobSelector();
}

function renderPathView() {
  const job = state.currentJob;
  const totalWeeks = job.path.reduce((sum, phase) => sum + parseInt(phase.weeks, 10), 0);
  $('#pathTarget').innerHTML = `
    <div class="target-icon" data-icon="target"></div>
    <div class="target-info">
      <h2>${esc(job.title)} · 补齐路线</h2>
      <p>${esc(job.company)} · 已按岗位缺口排序：${esc(job.gaps.slice(0, 3).map((gap) => gap.name).join('、'))}</p>
    </div>
    <div class="target-time">
      <strong>约 ${totalWeeks} 周</strong>
      <span>完整学习周期</span>
    </div>
  `;
  $('#pathLayout').innerHTML = job.path.map((phase) => `
    <div class="path-phase">
      <div class="phase-index">
        <strong>${phase.stage.replace('阶段 ', '')}</strong>
        <span>${esc(phase.weeks)}</span>
      </div>
      <div>
        <h3>${esc(phase.title)}</h3>
        <p>${esc(phase.goal)}</p>
        <div class="resource-grid">
          ${phase.resources.map((resource) => {
            const cssClass = resource.type === '证书' ? 'cert' : (resource.type === '项目' ? 'project' : '');
            return `
              <div class="resource-item">
                <strong>${esc(resource.name)}</strong>
                <small>${esc(resource.meta)}</small>
                <span class="resource-type ${cssClass}">${esc(resource.type)}</span>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    </div>
  `).join('');
  applyIcons();
}

function renderReport() {
  const job = state.currentJob;
  const skills = PERSONAL_SKILLS.filter((skill) => skill.level >= 82);
  const report = `
    <div class="report-header">
      <div>
        <h1>求职适配诊断报告</h1>
        <p>${esc(CANDIDATE.name)} · ${esc(CANDIDATE.school)} · 生成于智能分析流水线</p>
      </div>
      <div class="report-score-box">
        <strong>${job.score}</strong>
        <span>${esc(job.grade)} · 适配度</span>
      </div>
    </div>

    <section class="report-section">
      <h2>档案概览</h2>
      <dl class="report-kv">
        <div><dt>姓名</dt><dd>${esc(CANDIDATE.name)}</dd></div>
        <div><dt>求职方向</dt><dd>${esc(CANDIDATE.focus)}</dd></div>
        <div><dt>目标岗位</dt><dd>${esc(job.title)}</dd></div>
        <div><dt>企业岗位</dt><dd>${esc(job.company)} · ${esc(job.city)}</dd></div>
        <div><dt>项目经历</dt><dd>${PERSONAL_PROJECTS.length} 段可展示项目</dd></div>
        <div><dt>材料完整度</dt><dd>简历 / 成绩单 / 自我介绍 已解析</dd></div>
      </dl>
    </section>

    <section class="report-section">
      <h2>核心能力摘要 <span>按置信度与证据筛选</span></h2>
      <div class="report-skills">
        ${skills.slice(0, 9).map((skill, index) => `
          <div class="report-skill ${index % 3 === 1 ? 'coral' : (index % 3 === 2 ? 'blue' : '')}">
            <strong>${esc(skill.name)}</strong>
            <span>${TYPE_META[skill.type].label} · ${skill.level}分</span>
          </div>
        `).join('')}
      </div>
    </section>

    <section class="report-section">
      <h2>六维胜任力对比 <span>个人当前水平 / 岗位目标水平</span></h2>
      <div class="report-mini-grid">
        <svg id="reportRadar" viewBox="0 0 420 320" aria-label="胜任力雷达"></svg>
        <table class="report-table">
          <thead><tr><th>维度</th><th>个人</th><th>岗位</th><th>差距</th></tr></thead>
          <tbody>
            ${job.dims.map((dim) => `
              <tr>
                <td>${esc(dim.label)}</td>
                <td>${dim.mine}</td>
                <td>${dim.target}</td>
                <td>${Math.max(0, dim.target - dim.mine)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>

    <section class="report-section">
      <h2>关键能力差距 <span>由双图谱匹配生成</span></h2>
      <div class="report-chips">
        ${job.gaps.map((gap) => `<span class="report-gap">${esc(gap.name)}</span>`).join('')}
      </div>
      <table class="report-table" style="margin-top:10px">
        <thead><tr><th>差距项</th><th>性质</th><th>建议动作</th></tr></thead>
        <tbody>
          ${job.gaps.map((gap) => `
            <tr>
              <td>${esc(gap.name)}</td>
              <td>${gap.kind === 'required' ? '必需能力' : '可提升项'}</td>
              <td>${gap.action ? `进入${esc(gap.action)}` : '进入学习路线补齐'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </section>

    <section class="report-section">
      <h2>推荐学习计划 <span>从能力缺口到可写进简历的成果</span></h2>
      <table class="report-table">
        <thead><tr><th>阶段</th><th>主题</th><th>周期</th><th>学习目标</th></tr></thead>
        <tbody>
          ${job.path.map((phase) => `
            <tr>
              <td>${esc(phase.stage)}</td>
              <td>${esc(phase.title)}</td>
              <td>${esc(phase.weeks)}</td>
              <td>${esc(phase.goal)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </section>

    <div class="report-footer">本报告由个人能力图谱与岗位能力图谱自动匹配生成，结果供求职规划参考。</div>
  `;
  $('#reportSheet').innerHTML = report;
  renderRadar($('#reportRadar'), job.dims, true);
}

function renderUploadFiles() {
  const list = $('#fileList');
  list.innerHTML = state.defaultFiles.map((file) => fileRow(file)).join('');
  $('#fileCount').textContent = `${state.defaultFiles.length} 个文件`;
}

function fileRow(file, progress = 100, status = '已完成') {
  const meta = fileTypeMeta(file.name);
  return `
    <li class="file-row">
      <span class="file-icon ${meta.className}" data-icon="${meta.icon}"></span>
      <span class="file-row-main">
        <span class="file-name">${esc(file.name)}</span>
        <span class="file-meta">${esc(file.size || '')} · ${esc(file.type === 'pdf' ? 'PDF简历' : file.type === 'image' ? '成绩单图片' : file.type === 'video' ? '自我介绍视频' : '附加材料')}</span>
      </span>
      <span class="file-right">
        <span class="file-status ${status === '已完成' ? 'done' : 'busy'}">${esc(status)}</span>
        <span class="file-progress"><i style="width:${progress}%"></i></span>
      </span>
    </li>
  `;
}

function simulateParsing(fileName, fileSize) {
  const list = $('#fileList');
  const row = document.createElement('li');
  row.className = 'file-row';
  const meta = fileTypeMeta(fileName);
  row.innerHTML = `
    <span class="file-icon ${meta.className}" data-icon="${meta.icon}"></span>
    <span class="file-row-main">
      <span class="file-name">${esc(fileName)}</span>
      <span class="file-meta">${esc(fileSize)} · 上传中</span>
    </span>
    <span class="file-right">
      <span class="file-status busy">上传中</span>
      <span class="file-progress"><i style="width:2%"></i></span>
    </span>
  `;
  list.prepend(row);
  applyIcons();
  const progressBar = $('.file-progress i', row);
  const statusText = $('.file-status', row);
  const metaText = $('.file-meta', row);
  setTimeout(() => {
    progressBar.style.width = '38%';
    statusText.textContent = '解析中';
    metaText.textContent = `${fileSize} · OCR/转写中`;
  }, 350);
  setTimeout(() => {
    progressBar.style.width = '100%';
    statusText.textContent = '已完成';
    statusText.className = 'file-status done';
    metaText.textContent = `${fileSize} · 解析完成`;
    const count = list.children.length;
    $('#fileCount').textContent = `${count} 个文件`;
  }, 1500);
}

function openMobileSidebar(open) {
  $('#sidebar').classList.toggle('open', open);
  $('#scrim').classList.toggle('show', open);
}

function go(view) {
  state.currentView = view;
  const titles = {
    upload: '个人材料',
    graph: '能力图谱',
    match: '岗位匹配',
    path: '学习路线',
    report: '诊断报告'
  };
  $$('.view').forEach((section) => section.classList.toggle('active', section.id === `view-${view}`));
  $$('.nav-item').forEach((item) => {
    item.classList.toggle('active', item.dataset.view === view);
  });
  $('#pageTitle').textContent = titles[view];

  const order = ['upload', 'graph', 'match', 'path', 'report'];
  const currentIndex = order.indexOf(view);
  $$('.flow-step').forEach((step) => {
    const index = order.indexOf(step.dataset.step);
    step.classList.toggle('done', index < currentIndex);
    step.classList.toggle('active', index === currentIndex);
  });

  if (view === 'graph') {
    $('#graphModeTabs .active')?.classList.remove('active');
    const target = state.graphMode === 'job' ? 'job' : 'personal';
    $$('#graphModeTabs button').forEach((button) => button.classList.toggle('active', button.dataset.mode === target));
    renderGraph();
  }
  if (view === 'match') {
    renderJobSelector();
    renderMatchView();
  }
  if (view === 'path') renderPathView();
  if (view === 'report') renderReport();
  openMobileSidebar(false);
  if (location.hash !== `#${view}`) history.replaceState(null, '', `#${view}`);
}

function setJob(job) {
  state.currentJob = job;
  state.selectedNode = null;
  $('#sideScore').textContent = job.score;
  if (state.currentView === 'graph' && state.graphMode === 'job') renderGraph();
  if (state.currentView === 'match') renderMatchView();
  if (state.currentView === 'path') renderPathView();
  if (state.currentView === 'report') renderReport();
}

function resetDemo() {
  state.defaultFiles = [
    { name: '林知夏-简历.pdf', size: '1.2 MB', type: 'pdf' },
    { name: '成绩单.png', size: '860 KB', type: 'image' },
    { name: '自我介绍.mp4', size: '48 MB', type: 'video' }
  ];
  renderUploadFiles();
  $('#metricSkills').textContent = PERSONAL_SKILLS.length;
  $('#metricProjects').textContent = PERSONAL_PROJECTS.length;
  $('#metricJobs').textContent = '8';
  go('upload');
}

function bindEvents() {
  $$('.nav-item').forEach((item) => {
    item.addEventListener('click', () => go(item.dataset.view));
  });
  $$('[data-nav]').forEach((button) => {
    button.addEventListener('click', () => go(button.dataset.nav));
  });
  $('#menuBtn').addEventListener('click', () => openMobileSidebar(true));
  $('#scrim').addEventListener('click', () => openMobileSidebar(false));

  $('#resetDemoBtn').addEventListener('click', resetDemo);
  $('#loadSampleBtn').addEventListener('click', resetDemo);

  const dropZone = $('#dropZone');
  const fileInput = $('#fileInput');
  $('#pickFileBtn').addEventListener('click', (event) => {
    event.stopPropagation();
    fileInput.click();
  });
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('dragover', (event) => {
    event.preventDefault();
    dropZone.classList.add('drag');
  });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag'));
  dropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropZone.classList.remove('drag');
    Array.from(event.dataTransfer.files || []).forEach((file) => simulateParsing(file.name, formatFileSize(file.size)));
  });
  fileInput.addEventListener('change', () => {
    Array.from(fileInput.files || []).forEach((file) => simulateParsing(file.name, formatFileSize(file.size)));
    fileInput.value = '';
  });

  $$('#graphModeTabs button').forEach((button) => {
    button.addEventListener('click', () => {
      state.graphMode = button.dataset.mode;
      $$('#graphModeTabs button').forEach((item) => item.classList.toggle('active', item === button));
      renderGraph();
    });
  });

  $('#graphSearch').addEventListener('input', (event) => {
    state.graphQuery = event.target.value;
    applyGraphFilter();
  });
  $('#zoomInBtn').addEventListener('click', () => {
    state.graphZoom = Math.min(1.8, state.graphZoom + 0.1);
    updateGraphTransform();
  });
  $('#zoomOutBtn').addEventListener('click', () => {
    state.graphZoom = Math.max(0.55, state.graphZoom - 0.1);
    updateGraphTransform();
  });
  $('#fitBtn').addEventListener('click', () => {
    state.graphZoom = 1;
    state.graphPan = { x: 0, y: 0 };
    updateGraphTransform();
  });

  $('#jobCards').addEventListener('click', (event) => {
    const card = event.target.closest('[data-job]');
    if (!card) return;
    const job = JOB_GROUPS.find((item) => item.key === card.dataset.job);
    if (job) setJob(job);
  });

  $('#exportPdfBtn').addEventListener('click', () => {
    renderReport();
    setTimeout(() => window.print(), 80);
  });

  window.addEventListener('hashchange', () => {
    const view = location.hash.replace('#', '');
    if (['upload', 'graph', 'match', 'path', 'report'].includes(view)) go(view);
  });
}

function updateGraphTransform() {
  const viewport = $('.graph-viewport', $('#graphCanvas'));
  if (!viewport) return;
  viewport.setAttribute('transform', `translate(${state.graphPan.x}, ${state.graphPan.y}) scale(${state.graphZoom})`);
}

function init() {
  applyIcons();
  renderUploadFiles();
  const hash = location.hash.replace('#', '');
  const initialView = ['upload', 'graph', 'match', 'path', 'report'].includes(hash) ? hash : 'upload';
  state.personalGraph = buildPersonalGraphData();
  state.jobGraph = buildJobGraphData(state.currentJob);
  go(initialView);
  bindEvents();
  $('#metricSkills').textContent = PERSONAL_SKILLS.length;
  $('#metricProjects').textContent = PERSONAL_PROJECTS.length;
  $('#metricJobs').textContent = '8';
  $('#sideScore').textContent = state.currentJob.score;
}

init();
