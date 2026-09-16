# 多线程文件匹配工具模式

## 适用场景
需要高效搜索、匹配和操作大量文件的工具，如文件查重、批量重命名、内容搜索等。

## 推荐架构

```
┌─────────────────────────────────────────────────────┐
│  FileScanner (生产者)                                │
│  遍历目录、收集文件清单                                │
│  → 放入 Queue                                        │
├─────────────────────────────────────────────────────┤
│  FileWorker x N (消费者线程池)                        │
│  从 Queue 取文件、处理、输出结果                       │
│  ├── Worker 1 — 读取文件内容                          │
│  ├── Worker 2 — 计算哈希                              │
│  └── Worker 3 — 正则匹配                              │
├─────────────────────────────────────────────────────┤
│  ResultCollector (结果收集)                          │
│  聚合处理结果、去重、排序                               │
├─────────────────────────────────────────────────────┤
│  Exporter                                            │
│  输出结果到文件 / UI / 控制台                          │
└─────────────────────────────────────────────────────┘
```

## 核心代码

### 生产者-消费者模式
```python
import queue
import threading
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

class FileMatcher:
    def __init__(self, root_dir: str, max_workers: int = 8):
        self.root = pathlib.Path(root_dir)
        self.max_workers = max_workers
        self.file_queue: queue.Queue[pathlib.Path] = queue.Queue()
        self.results: list[dict] = []
        self._lock = threading.Lock()

    def scan(self, pattern: str = "**/*") -> int:
        """扫描文件，返回文件数量"""
        count = 0
        for f in self.root.glob(pattern):
            if f.is_file():
                self.file_queue.put(f)
                count += 1
        return count

    def process(self, worker_fn) -> list[dict]:
        """并发处理文件"""
        def wrapper():
            while not self.file_queue.empty():
                try:
                    file_path = self.file_queue.get_nowait()
                    result = worker_fn(file_path)
                    if result:
                        with self._lock:
                            self.results.append(result)
                except queue.Empty:
                    break
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        threads = []
        for _ in range(self.max_workers):
            t = threading.Thread(target=wrapper, daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return self.results
```

### 使用示例：文件查重
```python
def find_duplicates(root_dir: str):
    import hashlib

    matcher = FileMatcher(root_dir)
    total = matcher.scan("**/*.*")
    print(f"扫描到 {total} 个文件")

    def compute_hash(file_path: pathlib.Path):
        h = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return {"path": str(file_path), "md5": h.hexdigest(), "size": file_path.stat().st_size}

    results = matcher.process(compute_hash)

    # 按 md5 分组查找重复
    from collections import defaultdict
    groups = defaultdict(list)
    for r in results:
        groups[r["md5"]].append(r)

    duplicates = {k: v for k, v in groups.items() if len(v) > 1}
    return duplicates
```

## 常见坑点

1. **Queue 阻塞**：`queue.get()` 默认阻塞，用 `get_nowait()` 或超时避免死锁
2. **线程安全**：结果收集用 `threading.Lock` 保护
3. **IO 瓶颈**：HDD 不适合高并发，可将 `max_workers` 设为 2-4
4. **内存爆炸**：文件清单很大时使用迭代器而非全部加载到内存
5. **符号链接**：遍历时需检测 `is_symlink()` 避免死循环

## 验收标准

- [ ] 支持按文件名/内容/扩展名过滤
- [ ] 多线程处理，CPU 利用率达到 70%+
- [ ] 结果收集无竞态条件，无数据丢失
- [ ] 大目录（10 万+ 文件）遍历不超时
- [ ] 支持取消操作
- [ ] 导出结果为 JSON / CSV
