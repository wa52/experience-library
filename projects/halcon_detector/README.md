# HALCON 检测器

## 项目概述
基于 HALCON + C# WinForms 的工业视觉检测系统，用于产品外观缺陷检测。

## 技术栈
- HALCON 24.11 — 视觉算法库
- C# / WinForms — 桌面应用
- 海康威视 GigE 相机 — 图像采集

## 架构要点
- 相机采集与检测分离在不同线程
- HSmartWindowControl 实时显示
- 检测结果（OK/NG）记录到本地数据库

## 关键经验
1. HALCON .NET 必须在配置中设置 useLegacyV2RuntimeActivationPolicy
2. 目标平台必须是 x64，不能使用 AnyCPU
3. 每帧采集后必须 Dispose HImage，否则内存泄漏
4. 网卡需配置巨型帧避免丢包

## 当前状态
- 进行中：检测算法仍在优化
