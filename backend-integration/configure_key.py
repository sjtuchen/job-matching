# -*- coding: utf-8 -*-
"""把智谱 API Key 写入 backend-integration/.env

运行方式：
    python configure_key.py

Key 只保存在本地 .env，不打印到屏幕，不提交到 GitHub。
"""
import getpass
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"

print("正在配置 ZHIPU_API_KEY")
print("Key 只写入本地 .env，不会显示在屏幕上。")
key = getpass.getpass("请粘贴智谱API Key后按回车: ").strip()
if not key:
    print("未输入 Key，配置已取消。")
    raise SystemExit(1)

lines = []
if env_path.exists():
    lines = env_path.read_text(encoding="utf-8").splitlines()

filtered = [
    line
    for line in lines
    if not line.strip().startswith("ZHIPU_API_KEY=")
]
filtered.append(f"ZHIPU_API_KEY={key}")

env_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")
print("配置完成：backend-integration/.env 已更新。")
print("下一步：重新运行 backend-integration/server.py，再测试上传抽取。")
