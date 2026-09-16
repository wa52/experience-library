# PowerShell 向 curl.exe 传中文/JSON 参数被破坏

## 问题现象
PowerShell 里 `curl.exe -X POST ... -d '{"query":"中文问题"}'` 服务端报
`JSON decode error: Expecting property name enclosed in double quotes`；
用 `curl -s` 输出去 `Select-String "^event:"` 也取不到（流式行被吞）。

## 影响项目
- langchain-kb（API 冒烟/E2E 验证时用 curl 测 SSE 流）

## 原因
PowerShell 5.1 把参数按 GBK 编码传给 curl.exe，且对引号/方括号的解析方式与 bash 不同，
内联 JSON 里的 `"` 会被剥离或编码错乱，中文乱码，JSON 直接非法。

## 解决方案（推荐）
**不要把内联 JSON 传给 curl，改用 `--data-binary @文件`**：

```powershell
# 1. 用 UTF-8 写 body 文件（用编辑工具而非 PowerShell 字符串）
# 2. 传文件，避免所有引号/编码问题
curl.exe -s -N -X POST "http://127.0.0.1:8000/api/v1/chat/stream" `
  -H "Content-Type: application/json" `
  --data-binary "@C:\Temp\req.json" `
  --max-time 90 -o out.txt
```

其他规避：
- 输出用 `-o 文件` 落地再 `Get-Content -Raw` 解析（管道逐行会截断 SSE）。
- 读响应头/`mcp-session-id` 用 `curl -D -` 再正则抓 header。
- 想内联时优先 `Invoke-RestMethod`/`Invoke-WebRequest`（它们对 UTF-8 处理可靠）。

## 教训
Windows PowerShell + 原生 exe 传参是编码重灾区；凡是含非 ASCII/复杂 JSON 的请求一律走文件体。
