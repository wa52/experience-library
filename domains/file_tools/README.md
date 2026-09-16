# 文件工具 领域经验

> 涉及文件搜索、批量重命名、格式转换、内容匹配等工具开发经验。

## 关键要点

### 常用技术栈

| 需求 | 推荐方案 |
|------|---------|
| 文件名模糊搜索 | `glob` / `pathlib` / `fnmatch` |
| 文件内容搜索 | `grep` / 正则 / 全文索引 |
| 批量重命名 | `os.rename` / `pathlib.rename` |
| 文件类型转换 | `Pillow`(图像) / `pandas`(表格) / `ffmpeg`(视频) |
| 大文件处理 | 分块读取 / mmap / 多线程 |
| 文件监控 | `watchdog` 库 |

### 多线程文件处理模板

```python
import concurrent.futures
import pathlib

def process_file(file_path: pathlib.Path) -> bool:
    """处理单个文件，返回是否成功"""
    try:
        # 文件处理逻辑
        return True
    except Exception:
        return False

def batch_process(root_dir: str, pattern: str = "**/*.txt", max_workers: int = 8):
    root = pathlib.Path(root_dir)
    files = list(root.glob(pattern))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_file, f): f for f in files}
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                success = future.result()
                if not success:
                    print(f"失败: {file_path}")
            except Exception as e:
                print(f"异常: {file_path}: {e}")
```

### 性能优化

1. **I/O 密集型**：使用多线程（`ThreadPoolExecutor`），不用多进程
2. **CPU 密集型**：使用多进程（`ProcessPoolExecutor`）
3. **大文件逐行读取**：`with open(f) as f: for line in f:` 按行迭代，不加载全文件
4. **批量小文件**：合并读写操作，减少系统调用
5. **SSD vs HDD**：SSD 适合并发读写，HDD 适合顺序读写

### 常见坑点

1. **路径编码**：Windows 下中文路径用 `pathlib.Path` 处理避免编码问题
2. **权限不足**：部分系统目录没有读取权限，需捕获 `PermissionError`
3. **文件被占用**：Windows 下文件被其他进程占用时无法删除/重命名
4. **符号链接**：递归遍历时注意处理符号链接，避免死循环
5. **超长路径**：Windows MAX_PATH 限制（260 字符），用 `\\?\` 前缀绕过
