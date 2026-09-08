---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '81a619a1-d3fd-495a-99f6-d372a5ce280f'
  PropagateID: '81a619a1-d3fd-495a-99f6-d372a5ce280f'
  ReservedCode1: '1a852de2-b6a2-460d-aa81-90b1b875a07f'
  ReservedCode2: '1a852de2-b6a2-460d-aa81-90b1b875a07f'
---

# 匹配系统本体 · 使用说明（队员版）

> 本项目不依赖任何个人账号。大模型走智谱官方免费 API，每个使用者自己申请自己的 key。

## 一、这是什么

把 359 条招聘 JD 和 100 份简历都抽取成统一格式的"能力图谱"（结构化技能清单），
然后两图对齐打分，输出：岗位推荐排名、能力差距清单、（后续）学习路线。

当前进度：
- [x] ① 基线评测已出（关键词匹配：对口 48% / 迁移 43% / 跨界 20%，负对照零误命中）
- [x] ② 抽取器已写好并自检通过
- [x] ③ 359 条 JD 批量抽取（全库清洗 + 14 份污染简历手工重抽后覆盖）
- [x] ④ 100 份简历批量抽取
- [x] ⑤ 图谱匹配评测（**对口 52% / 迁移 40% / 跨界 27%**，两项反超基线、迁移基本拉平；Top3 率 75%/63%/53% 全面领先）
- [x] ⑥ 向量混合层评测 + α 消融（结论：纯清单 α=1.0 最优，向量层无额外增益，保留作技术对比）
- [~] ⑦ 差距分析+学习路线（已砍掉，不进入本期结项）
- [~] ⑧ 网页 Demo（已砍掉，路演现场零 API 调用改为口头展示评测数字）

**评测主线已收官**，结果报告见 `.temp/graph_match_report.json`。

## 二、申请免费 API key（约 10 分钟，团队公共账号）

需要开两个平台的免费账号，各管一摊：

**1. 智谱（管"抽取"——读 JD/简历吐能力清单）**
1. 打开 https://open.bigmodel.cn （智谱 AI 开放平台）
2. 手机号注册登录
3. 右上角头像 → 「API Keys」→ 创建 API Key，复制
4. 用的模型 **glm-4.7-flash 是永久免费的**

**2. 硅基流动（管"向量化"——能力词变向量，语义兜底匹配）**
1. 打开 https://cloud.siliconflow.cn
2. 注册登录 → 控制台 → 「API 密钥」→ 创建，复制
3. 用的模型 **BAAI/bge-large-zh-v1.5 在免费名单里**（向量模型按量计费，我们这点调用量免费额度绰绰有余）

两个 key 都只进环境变量，不写进任何项目文件。

## 三、怎么跑

所有数据脚本在 `data/`，核心代码在 `backend/`（见下方文件地图）。

```powershell
# Python 解释器固定用这个
$py = "python"

# 1) 验证你的 key 能用（调 1 次，秒级）
$env:ZHIPU_API_KEY = "你的key"
& $py D:\新国赛\.temp\graph_extractor.py --test-key

# 2) 批量抽 359 条 JD（限速 1.5s/次，约 15-20 分钟；中途断了直接重跑，自动续传）
& $py D:\新国赛\.temp\graph_extractor.py --extract-jd

# 3) 批量抽 100 份简历（约 5 分钟）
& $py D:\新国赛\.temp\graph_extractor.py --extract-resume

# 4) 查看进度/坏样本
& $py D:\新国赛\.temp\graph_extractor.py --status

# 5) 图谱匹配评测（③④完成后）
& $py D:\新国赛\.temp\graph_match.py
```

## 四、文件地图

| 文件 | 作用 |
|---|---|
| `.temp/graph_extractor.py` | 抽取器：JD/简历 → 能力图谱 JSON（缓存到 `.temp/graph_cache/`） |
| `.temp/graph_match.py` | 匹配评测：图谱对齐打分 + 分层排名（对比基线） |
| `.temp/graph_schema.json` | 图谱格式定义 + 抽取 Prompt（改 Prompt 先看这里） |
| `.temp/anchor_lexicon.json` | 锚定词表 106 词（两图共用词空间，防大模型自创词） |
| `.temp/baseline_eval.py` | 基线评测脚本（已跑完，报告在 baseline_report.json） |
| `.temp/baseline_report.json` | 基线结果：对口 48%/迁移 43%/跨界 20%（所有方案要打败的线） |
| `.temp/graph_match_report.json` | ⑤ 最终结果：对口 52%/迁移 40%/跨界 27%（含分层排名分布+逐份明细） |
| `.temp/graph_hybrid_report.json` | ⑥ 混合方案结果（α=0.7：50/40/27，作技术对比） |
| `.temp/hybrid_ablation.json` | α 消融数据（1.0/0.7/0.5/0.3 四档，证明纯清单最优） |
| `.temp/bge_sim_matrix.json` | BGE 向量相似度矩阵（⑥ 混合层用，全量缓存） |
| `.temp/graph_cache/` | 图谱缓存（断点续跑靠它；这个目录别删） |

## 五、坏了怎么排查

| 症状 | 处理 |
|---|---|
| `--test-key` 报 401 | key 复制不完整，重新复制（注意别带空格） |
| `--test-key` 报模型不存在 | 打开 graph_extractor.py，把 MODEL 改成 `glm-4-flash` 再试 |
| 批量抽取中途断 | 直接重跑同一条命令，已抽的会从缓存跳过 |
| `--status` 里出现 .bad.txt | 删掉对应 .bad.txt 文件重跑批量命令，只重抽坏样本 |
| 表外词告警 | 模型自由发挥超出词表，.bad.txt 里有原文，删掉重抽即可 |

## 六、边界说明（写进答辩材料的口径）

- 大模型抽取：智谱 GLM-4.7-Flash 永久免费官方 API，配置空白制，项目不携带任何个人凭据
- 向量化：硅基流动 BAAI/bge-large-zh-v1.5（中文优化 1024 维），免费额度内完成全部调用量
- 成本模型（商业计划书）：产品化后切企业账号按量计费，单用户单次推理约几分钱，
  代码零改动（只换 API_KEY 和 API_URL 两个变量）
- 断网兜底：所有抽取/向量结果全量缓存本地，路演现场零 API 调用