# Hugging Face Spaces 部署说明（保留原界面）

如果需要完整保留“智职图谱”原有网页界面，不把页面改成 Streamlit，
请部署原始 `backend-integration/server.py`，并配合根目录的 `Dockerfile`。

Hugging Face Spaces 的免费 Docker Space 不需要绑定信用卡，公网地址形如：

```text
https://你的用户名-项目名.hf.space
```

## 创建 Space

1. 登录 https://huggingface.co
2. 点击头像旁的 `New Space`
3. Space name 例如：`job-matching`
4. License 随意；Visibility 选 `Public`
5. SDK 选择 `Docker`
6. Hardware 选择免费 `CPU basic`
7. 点击 `Create Space`

## 上传文件

Space 创建后，在该 Space 的 Files 页面选择 `Add file > Upload files`，
把整个项目上传，结构为：

```text
Dockerfile
requirements-server.txt
backend-integration/
backend-module/
frontend-prototype/
```

也可以使用 Git：

```bash
git clone https://huggingface.co/spaces/你的用户名/job-matching
cd job-matching
```

把上述项目目录复制进去，然后：

```bash
git add .
git commit -m "deploy job matching app"
git push
```

## 设置智谱 Key

Hugging Face Space 页面点击 `Settings > Variables and secrets`，添加：

```text
ZHIPU_API_KEY=你的智谱APIKey
```

设置完成后保存并重启 Space，原页面即可在公网使用真实上传与能力抽取。
