@echo off
title 智职图谱 Cloudflare Tunnel (keep alive)
echo Local service: http://127.0.0.1:8000
echo This window must stay open. Close it only when you want to stop sharing.
echo.
:restart
echo [%date% %time%] Starting cloudflared...
"C:\Users\15485\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:8000 --no-autoupdate --protocol http2
echo.
echo cloudflared stopped unexpectedly. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto restart
