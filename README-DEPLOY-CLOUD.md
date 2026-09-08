# 云端部署说明

本项目是“Python 后端 + 静态前端”的一体化服务，不能像 GitHub Pages 那样只部署
前端，也不能靠 trycloudflare.com 的临时链接获得长期稳定的公网地址。

要和 Streamlit 云端应用一样长期访问，需要把 `backend-integration/server.py`
部署到能持续运行 Python 的云平台。

## 推荐平台：Render

仓库根目录已经准备好 `render.yaml` 和 `requirements.txt`。

1. 把本项目上传到 GitHub 仓库。
2. 打开 https://render.com 并注册。
3. 点击 New > Blueprint，选择这个 GitHub 仓库。
4. Render 会自动读取 `render.yaml`，创建 Python Web Service。
5. 在服务环境变量中填写 `ZHIPU_API_KEY`。
6. 服务启动后，`https://<服务名>.onrender.com` 就是固定公网地址。

免费版 Render Web Service 空闲 15 分钟后会休眠，网址不变，但第一次访问可能
需要等十几秒重新唤醒。需要 24 小时不睡眠时，应选择付费实例或部署到自己的
云服务器。

## 本项目启动方式

云端启动命令：

```text
python backend-integration/server.py
```

需要设置的环境变量：

```text
INTEGRATION_HOST=0.0.0.0
ZHIPU_API_KEY=你的智谱Key
```

Render 会自动注入 `PORT`，服务会监听该端口。

## 其他可选平台

- Railway：类似 Render，读取根目录 `requirements.txt`，设置相同环境变量。
- Fly.io：需要额外 `fly.toml` 和 Dockerfile。
- Hugging Face Spaces：可以运行 Python Web 应用，但免费 Space 会休眠。
- 腾讯云/阿里云轻量服务器：最接近“一直可访问”，适合决赛长期演示。

无论选择哪个平台，请务必不要把 `backend-integration/.env` 提交到仓库，
智谱 Key 只填在云平台的环境变量中。
