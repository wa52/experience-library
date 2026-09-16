# 自由文本路径提取器模式

## 适用场景
从 AI 生成的自由文本消息中提取文件/目录路径，使其可点击打开。

## 挑战
AI 输出的路径格式多样：
- 反引号包裹：`` `C:\path\to\file` ``
- 引号包裹：`"C:\path\to\file"`
- 裸路径：`C:\Users\xxx\file.txt`
- 相对路径：`./src/main.ts`
- 路径跨行截断

## 核心策略

### 1. 候选路径提取
按优先级匹配：
1. 反引号包裹的文本
2. 引号包裹的文本
3. 行中 Windows 盘符开头的路径 `[A-Za-z]:\`
4. 行中 Unix 根路径 `/`
5. 通过正则匹配常见的路径模式

### 2. 存在性验证
```javascript
function longestExistingPath(raw, workspace) {
  for (let attempt = 0; attempt < 20; attempt++) {
    const target = isAbsolute(candidate) ? normalize(candidate) : resolve(workspace, candidate);
    if (existsSync(target)) return candidate;
    candidate = candidate.slice(0, candidate.lastIndexOf(" ")); // 去掉末尾单词
  }
  return "";
}
```

### 3. 去重
```javascript
const seen = new Set();
for (const label of candidates) {
  const key = `${label.toLowerCase()}\0${target.toLowerCase()}`;
  if (seen.has(key)) continue;
  seen.add(key);
  output.push({ label, path: target, type });
}
```

## 验收标准
- [ ] 支持 Windows `C:\xxx` 绝对路径
- [ ] 支持 Unix `/xxx` 绝对路径
- [ ] 支持相对路径 `./` `../`
- [ ] 支持反引号/引号包裹
- [ ] 不存在的路径静默忽略
- [ ] 单条消息最多提取 40 个路径
- [ ] 不触发路径遍历攻击