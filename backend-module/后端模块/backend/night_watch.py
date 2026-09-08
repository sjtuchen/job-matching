# -*- coding: utf-8 -*-
"""
守夜脚本：等 JD 抽取完成 → 处理坏样本 → 简历抽取 → ⑤ 图谱匹配评测
单进程顺序执行，全流程日志写 night_watch.log
"""
import json
import os
import subprocess
import sys
import time

BASE = r"D:\新国赛"
TEMP = os.path.join(BASE, ".temp")
CACHE = os.path.join(TEMP, "graph_cache")
PY = sys.executable
EXTRACTOR = os.path.join(TEMP, "graph_extractor.py")
MATCH = os.path.join(TEMP, "graph_match.py")

LOG = open(os.path.join(TEMP, "night_watch.log"), "a", encoding="utf-8")

def log(msg):
    line = time.strftime("[%H:%M:%S] ") + msg
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()

def count(cache_dir):
    ok = len([f for f in os.listdir(cache_dir) if f.endswith(".json")])
    bad = len([f for f in os.listdir(cache_dir) if f.endswith(".bad.txt")])
    return ok, bad

def wait_extractor_done(timeout_min=90):
    """等待所有 graph_extractor 进程退出"""
    t0 = time.time()
    while time.time() - t0 < timeout_min * 60:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             "Where-Object { $_.CommandLine -match 'graph_extractor' }).Count"],
            capture_output=True, text=True)
        n = (out.stdout or "0").strip()
        if n in ("", "0"):
            return True
        time.sleep(60)
    return False

def run(cmd, timeout_min=40):
    log(f"RUN: {' '.join(cmd[1:])}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_min * 60)
        for line in (r.stdout or "").splitlines()[-15:]:
            log(f"  | {line}")
        if r.returncode != 0:
            for line in (r.stderr or "").splitlines()[-8:]:
                log(f"  ! {line}")
        return r.returncode
    except subprocess.TimeoutExpired:
        log("  ! 超时")
        return 99

def main():
    log("===== 守夜开始 =====")

    # 1) 等 JD 抽取进程结束
    log("等待 JD 抽取进程退出（每 60s 查一次）...")
    done = wait_extractor_done()
    ok, bad = count(CACHE)
    log(f"JD 抽取进程已退出（自然结束={done}）：成功 {ok}，坏 {bad}")

    # 2) 坏样本重抽一轮（删 .bad.txt 后重跑；JD 图谱里 resume 型不会有）
    if bad:
        for f in os.listdir(CACHE):
            if f.endswith(".bad.txt"):
                os.remove(os.path.join(CACHE, f))
        log(f"已删除 {bad} 个坏样本标记，重抽一轮 JD...")
        run([PY, EXTRACTOR, "--extract-jd"], timeout_min=60)
        ok, bad = count(CACHE)
        log(f"重抽后：成功 {ok}，坏 {bad}")

    # 3) 不足 359 继续补
    if ok < 359:
        log(f"JD 还缺 {359 - ok} 条，续跑...")
        run([PY, EXTRACTOR, "--extract-jd"], timeout_min=60)
        ok, bad = count(CACHE)
        log(f"补跑后：成功 {ok}，坏 {bad}")

    # 4) 简历抽取
    ok, bad = count(CACHE)
    resume_ok = len([f for f in os.listdir(CACHE)
                     if f.endswith(".json") and f.startswith("S")])
    log(f"简历图谱已有 {resume_ok}/100")
    if resume_ok < 100:
        run([PY, EXTRACTOR, "--extract-resume"], timeout_min=40)
        resume_ok = len([f for f in os.listdir(CACHE)
                         if f.endswith(".json") and f.startswith("S")])
        log(f"简历抽取后：{resume_ok}/100")
        if resume_ok < 100:  # 坏样本重抽
            for f in os.listdir(CACHE):
                if f.endswith(".bad.txt"):
                    os.remove(os.path.join(CACHE, f))
            run([PY, EXTRACTOR, "--extract-resume"], timeout_min=40)
            resume_ok = len([f for f in os.listdir(CACHE)
                             if f.endswith(".json") and f.startswith("S")])
            log(f"简历重抽后：{resume_ok}/100")

    # 5) 匹配评测
    log("运行 ⑤ 图谱匹配评测...")
    run([PY, MATCH], timeout_min=20)

    log("===== 守夜结束 =====")

if __name__ == "__main__":
    main()
