@echo off
set "HTTP_PROXY=http://127.0.0.1:7892"
set "HTTPS_PROXY=http://127.0.0.1:7892"
set "ALL_PROXY=http://127.0.0.1:7892"

cd /d "%~dp0"

echo OpenCode project: %CD%
echo Proxy: %HTTPS_PROXY%

opencode
