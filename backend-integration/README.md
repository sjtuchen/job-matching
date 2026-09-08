# 智职图谱一体化演示

该目录把后端模块与前端原型连接为一个本地可运行服务：

- 后端模块：读取 `backend-module/后端模块/backend/graph_cache/` 中的
  359 份岗位能力图谱和 100 份个人能力图谱；
- 匹配算法：直接调用后端模块 `graph_match.py`；
- API：暴露 `/api/bootstrap`、`/api/resumes`、`/api/health` 等接口；
- 静态托管：同端口托管 `frontend-prototype/`，前后端同源运行。

## 配置智谱 API Key

真实上传并抽取新简历需要智谱 API Key，申请地址：

```text
https://open.bigmodel.cn
```

获取 Key 后，在 `backend-integration/` 目录双击 `configure_key.bat`，
或在终端运行：

```powershell
python configure_key.py
```

脚本会把 Key 写入本地 `backend-integration/.env`，不会打印到屏幕，
该文件已被 `.gitignore` 忽略，不会提交到 GitHub。

## 真实上传简历

一体化页面已接入真实上传接口：

```text
POST /api/upload-resume
POST /api/delete-resume?doc_id=Uxxxx
POST /api/export-report
```

当前支持 `.txt`、`.pdf`、`.docx`。上传成功后，服务会：

1. 把文件解析成简历文本；
2. 调用 `graph_extractor.py` 生成能力图谱；
3. 把新图谱加入内存缓存；
4. 返回个人图谱与推荐岗位，前端自动刷新并跳转能力图谱页。

图片OCR与音视频转写暂未接入。

## 匹配算法口径

页面展示的匹配分直接来自压缩包 `backend/graph_match.py`：

```text
score = 0.8 × 专业技能覆盖率 + 0.2 × 工具覆盖率 + 0.0 × 软技能覆盖率
```

- 专业技能、工具使用 JD 侧要求覆盖度计算；
- 软技能因词表通用性不进入总分，仅作为提示展示；
- 岗位图谱按 `专业技能 / 工具 / 软技能` 三组返回；
- 差距清单同样按后端三组输出，不把软技能强称为硬性缺口。

## 启动

需要 Python 3.10+ 和 openpyxl。

```powershell
python backend-integration/server.py
```

打开：

```text
http://127.0.0.1:8000
```

前端会先显示内置演示数据，然后自动请求后端 `/api/bootstrap`。
请求成功后会显示：

- 后端真实简历：默认 S031（杨晓晴）；
- 后端真实岗位推荐：前3名岗位；
- 后端 `graph_match.py` 计算出的匹配得分与能力缺口；
- 由个人图谱与岗位图谱生成的可视化页面。

## 主要API

```text
GET /api/health
GET /api/resumes
GET /api/bootstrap?resume_id=S031&top=3
GET /api/match?resume_id=S031&job_id=JD-008
```

## 前后端两种运行模式

- GitHub Pages 只托管静态前端。无法运行 Python 后端，因此线上页面会自动
  保留内置示例数据作为兜底。
- 本地一体化服务由 `server.py` 同时提供 API 与页面，演示时需要保持
  该 Python 服务运行。

## 目录依赖

```text
backend-integration/server.py
backend-module/后端模块/backend/graph_cache/
backend-module/后端模块/backend/graph_match.py
frontend-prototype/
```
