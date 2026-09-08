# 智职图谱前端原型

一个无后端依赖、可直接运行的求职适配诊断平台原型，覆盖：

- 个人材料上传与解析状态；
- 个人能力图谱、岗位能力图谱；
- 岗位选择、人岗匹配、六维雷达图；
- 能力差距与学习路线；
- PDF报告预览与打印导出。

## 运行方式

需要Node.js环境：

```bash
node server.js
```

然后访问：

```text
http://localhost:4173
```

也可以直接通过任意静态文件服务器托管本目录。原型使用内置示例数据，前端交互无需后端。

## 连接后端一体化模式

运行项目根目录下的 `backend-integration/server.py`，然后访问：

```text
http://127.0.0.1:8000
```

页面会调用后端模块提供的图谱缓存和 `graph_match.py` 匹配算法，自动替换为真实岗位数据。
后端不可用或部署到 GitHub Pages 时，自动回退到内置示例数据。

一体化模式下，材料导入页支持真实上传 `.txt / .pdf / .docx` 简历。
后端完成 LLM 能力抽取后，页面会生成对应的个人能力图谱并更新岗位推荐。

## 部署到 GitHub Pages

GitHub Pages 只能托管静态文件，无法运行 Python 后端。部署前可先打开
`api-config.js`：

- 仅发布静态演示页时保留 `window.ZHIPU_API_BASE = ""`，页面会自动使用内置示例数据；
- 若后端已部署到公网，填写后端地址，例如：

```js
window.ZHIPU_API_BASE = "https://your-api.example.com";
```

需要上传到仓库根目录的静态文件是：

```text
index.html
styles.css
app.js
api-config.js
```

## 页面入口

左侧导航对应五个核心页面：

```text
材料导入
能力图谱
岗位匹配
学习路线
诊断报告
```

岗位匹配页可以切换3个岗位，匹配分、缺口、学习路线和报告会同步更新。
