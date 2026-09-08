@echo off
cd /d "%~dp0"
python jd_collector.py
echo.
echo 采集已结束，按任意键关闭窗口。
pause >nul
