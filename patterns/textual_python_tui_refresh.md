# Textual 8 TUI 动态列表刷新陷阱

## 场景
需要动态刷新列表型页面（Switch/Button 每行一个控件），或后台线程做完后重绘整页。

## 已踩的坑
1. 在 Widget 子类里定义 `refresh()` 覆盖了 Textual 自身的 `refresh(layout=...)`，框架挂载子控件时以 `layout=True` 调用，报 `TypeError`。
2. `container.remove_children()` 返回 `AwaitRemove`，真正摘除节点在消息泵异步执行；不 await 就立即 `mount()` 相同 id 的新控件 → `DuplicateIds`。
3. `App.run_worker(work, thread=True)` 不是协程，直接返回 Worker；用 `await worker.wait()` 等待线程完成。
4. `Content.__contains__` 不做子串匹配，`"重启" in widget.render()` 恒为 False，须 `str(...)` 后再判。

## 正确写法
```python
async def populate(self) -> None:
    container = self.query_one("#rows")
    await container.remove_children()          # 必须 await
    for item in items:
        container.mount(MyRow(item))           # id 唯一

async def _run_service(self, fn):
    def work():
        fn()
    worker = self.app.run_worker(work, thread=True)  # 同步返回 Worker
    await worker.wait()
    await self.app.refresh_all()               # refresh_all 也是 async
```

## 关键点
- 初始 populate 只在 `App.on_mount` 里做一次（用 `call_after_refresh`），子页面 on_mount 阶段不要 populate，否则与 App 级重绘重复挂载。
- 事件 handler 里 await 的任何方法都要保持 async 链完整，否则报 "coroutine never awaited"。
- 测试用 `app.run_test() as pilot` + `await pilot.pause()` 驱动；对渲染断言用 `str(widget.render())`。
