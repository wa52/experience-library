# 进程文件锁 + 健康检查模式

## 适用场景
防止同机同程序重复启动，确保单实例运行。

## 推荐架构
```
启动
  ├─ fs.open(lockFile, "wx") → 成功 → 运行
  │
  └─ EEXIST → 读取锁文件 → 健康检查
      ├─ 存活 → 打开已有 → 退出
      └─ 死亡 → 清理 → 自己启动
```

## 核心实现
```javascript
import { open, readFile, unlink } from "node:fs/promises";

async function acquireInstanceLock(lockFile) {
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      return await open(lockFile, "wx");
    } catch (err) {
      if (err.code !== "EEXIST") throw err;
      const existing = await readLockFile(lockFile);
      if (existing && await healthCheck(existing.url)) {
        openBrowser(existing.url);
        return null;  // 已有实例，不启动
      }
      await unlink(lockFile);  // 清理脏锁
    }
  }
  throw new Error("Cannot acquire lock");
}
```

## 常见坑点
- 锁文件最好包含 URL 和 PID，便于调试
- 健康检查超时不要超过 2-3 秒
- 进程退出时必须释放锁文件
- Windows 下锁文件可能被防病毒软件锁定

## 验收标准
- [ ] 同时启动两个实例，只有第一个运行
- [ ] 第一个意外退出后，第二个能接管
- [ ] 锁文件内容可读（JSON 格式）
- [ ] 进程退出时清理锁文件