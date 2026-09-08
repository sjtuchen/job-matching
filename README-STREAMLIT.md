# Streamlit 部署说明

根目录的 `app.py` 是“智职图谱”的 Streamlit 功能等价版，可以部署到
Streamlit Community Cloud 并获得稳定的 `https://你的用户名-项目名.streamlit.app`。

## 步骤

1. 确保 `app.py`、`requirements.txt`、`backend-integration/`、
   `frontend-prototype/`、`backend-module/` 已推送到 GitHub。
2. 登录 https://share.streamlit.io 或 https://streamlit.io/cloud。
3. 选择仓库 `sjtuchen/job-matching`，分支 `main`。
4. 主文件选择 `app.py`。
5. 部署后打开 Streamlit 应用的 Settings > Secrets，配置：

```text
ZHIPU_API_KEY=你的智谱APIKey
```

没有配置 Key 时，页面仍可用内置示例简历 S031 查看完整流程；
配置后即可上传 `.txt / .pdf / .docx` 简历并调用真实能力抽取。

## 免费版限制

Streamlit Community Cloud 免费版不要求绑定信用卡，但免费应用可能在长时间
闲置后休眠；再次访问会自动唤醒，公网网址不变。
