# Flutter 领域经验

> Flutter 是 Google 的跨平台 UI 框架，一套代码同时运行在 Android/iOS/Web/Desktop。

## 关键要点

### 开发环境

| 组件 | 说明 |
|------|------|
| Flutter SDK | >= 3.16 推荐 |
| Dart SDK | >= 3.2 推荐 |
| Android Studio / VS Code | IDE 选择 |
| Xcode (macOS) | iOS 构建必需 |

### 项目结构推荐

```
lib/
├── main.dart             # 入口
├── app.dart              # App 配置
├── core/
│   ├── constants/        # 常量
│   ├── theme/            # 主题
│   └── utils/            # 工具函数
├── data/
│   ├── models/           # 数据模型
│   ├── repositories/     # 数据仓库
│   └── services/         # API 服务
├── presentation/
│   ├── pages/            # 页面
│   ├── widgets/          # 可复用组件
│   └── providers/        # 状态管理
└── routes/               # 路由配置
```

### 状态管理选型

| 方案 | 学习曲线 | 性能 | 推荐场景 |
|------|---------|------|---------|
| Provider | 低 | 中 | 中小项目 |
| Riverpod | 中 | 好 | 中大型项目 |
| Bloc | 高 | 好 | 大型项目，团队协作 |
| GetX | 低 | 中 | 快速开发 |

### 常见坑点

1. **Hot Reload 限制**：修改 `main()` 函数或全局变量需要 Hot Restart
2. **平台通道**：与原生交互用 MethodChannel，注意线程
3. **包体积**：Flutter 应用基础体积较大（~10MB），可用 `--split-debug-info` 减小
4. **Web 兼容性**：`dart:io` 不能在 Web 平台使用
5. **Android 原生混淆**：发布时需配置混淆规则
