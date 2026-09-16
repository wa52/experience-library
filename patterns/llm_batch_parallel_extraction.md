# LLM 批量抽取并行化模式（ThreadPoolExecutor）

## 适用场景
对大量 chunk 逐批调用云端 LLM（如知识图谱实体关系抽取），串行循环 1 次 API = 1 批，
数据量大时索引要几分钟，用户体验差。**瓶颈在云端 API 调用次数 × 串行等待，与本地 CPU/GPU 无关。**

## 推荐做法
把批次循环改为 `ThreadPoolExecutor(max_workers=并发数)`，每批独立 `llm.invoke`，
主线程归并结果（确定性去重）。

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_entities_llm_batch(texts, llm):
    batches = [texts[i:i+BATCH] for i in range(0, len(texts), BATCH)]
    done = 0
    with ThreadPoolExecutor(max_workers=max(1, CONCURRENCY)) as pool:
        futures = [pool.submit(_extract_batch, b, llm) for b in batches]
        for fut in as_completed(futures):
            done += 1
            print(f"\r  完成 {done}/{len(batches)} 批 ...", end="")
            merge(*fut.result())   # 只允许主线程改共享集合
    print()
```

要点：
- **每批失败单独降级**（如 jieba 兜底），不要整批失败抛异常。
- 并发数做成配置（`GRAPH_LLM_CONCURRENCY`，默认 5），不要写死。
- 归并（去重 dict/set）只在主线程执行，worker 只返回结果 → 天然线程安全。
- langchain OpenAI 客户端 `invoke` 线程安全（项目内 `retrieve_knowledge` 并发评分已先例）。

## 实测
- 50 chunks / 批 10 / 每批 2s → 并发 5 用时 **2.0s**（串行 ~20s，10×）
- 130 批真实场景 ≈ 4-5× 提速（从几分钟到 ~50s）

## 教训
- 云端 LLM 的慢 = API 调用次数 + 串行，不是本地硬件；先确认瓶颈再优化，别盲目上 GPU。
