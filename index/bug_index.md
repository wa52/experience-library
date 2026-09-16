# Bug 索引

> 自动生成时间：2026-09-16 14:01:22
> 由 tools/build_index.py 自动生成，请勿手动编辑

共 26 条记录

| # | 标题 | 文件 |
|---|------|------|
| 1 | 404 中间件吞掉业务 404 | `failure_database/404_middleware_swallows_business_404.md` |
| 2 | 异步运行终态分多次写库导致的轮询竞态（open_risks 为 None 抖动） | `failure_database/async_terminal_write_polling_race.md` |
| 3 | Start-Process 启动的服务被命令超时连带杀掉（端口反复"起不来"） | `failure_database/detached_server_killed_by_command_timeout.md` |
| 4 | .env 文件 UTF-8 BOM 导致 python-dotenv 读不到变量 | `failure_database/dotenv_bom_issue.md` |
| 5 | FTS5 召回遗漏元数据导致咨询类别补齐失败 | `failure_database/fts_metadata_regression.md` |
| 6 | git add -A 误把先前会话未跟踪的文档整批提交 | `failure_database/git_add_dot_A_scope_leak.md` |
| 7 | 全局 CLI 命令的 config 模块被其他项目抢占 | `failure_database/global_cli_config_module_hijack.md` |
| 8 | HALCON 24.11 `apply_dl_model` 后 bbox/置信度字段为空 | `failure_database/halcon_dlresultbatch_bbox_empty.md` |
| 9 | hrun.exe 下 hdvp dimension="1" 输出参数破坏所有输出绑定 | `failure_database/hdvp_dimension1_hrun_bug.md` |
| 10 | 海康硬触发取图超时误报 + 状态机锁死丢弃后续触发 | `failure_database/hik_hard_trigger_grab_timeout_false_alarm.md` |
| 11 | lock_file_race_condition | `failure_database/lock_file_race_condition.md` |
| 12 | 海康 MVS GigE 相机枚举失败 MV_E_SUPPORT | `failure_database/mvs_gige_enum_mv_e_support.md` |
| 13 | opencode_sdk_api_fallback | `failure_database/opencode_sdk_api_fallback.md` |
| 14 | PaddleOCR 3.7 CPU oneDNN 推理报 ConvertPirAttribute2RuntimeAttribute | `failure_database/paddleocr_cpu_onednn_pir_attribute.md` |
| 15 | 两个项目默认端口冲突（8000） | `failure_database/port_conflict_two_services.md` |
| 16 | PowerShell 向 curl.exe 传中文/JSON 参数被破坏 | `failure_database/powershell_curl_json_mangling.md` |
| 17 | Pydantic 宽松模式把 "yes" 强转成 bool，422 测试误判 | `failure_database/pydantic_bool_coercion_422.md` |
| 18 | PyInstaller 打包后 SSL 模块加载失败（libcrypto-3.dll 缺失） | `failure_database/pyinstaller_ssl_dll_missing.md` |
| 19 | PySide6 QThread worker + torch CPU 模型退出崩溃（0xC0000409） | `failure_database/pyside6_qthread_torch_exit_crash.md` |
| 20 | Python 三重引号模板字符串吃掉 JS 的 \n，整段脚本语法错误 | `failure_database/python_template_string_swallows_js_escape.md` |
| 21 | Windows Python 默认编码导致中文 Skill 校验失败 | `failure_database/python_windows_default_encoding_skill_validation.md` |
| 22 | 内存缓存"已加载即跳过"导致数据变更后索引不刷新（BM25） | `failure_database/stale_inmemory_cache_after_data_change.md` |
| 23 | VisionInspection 测量节点性能测试误报 | `failure_database/visioninspection_measure_performance_false_failure.md` |
| 24 | Windows 下 npm 子进程 FileNotFoundError | `failure_database/windows_npm_cmd_shim_subprocess.md` |
| 25 | windows_path_parsing | `failure_database/windows_path_parsing.md` |
| 26 | Windows 下 python -c 子进程偶发挂起（DLL 初始化失败） | `failure_database/windows_python_child_dll_init_flake.md` |
