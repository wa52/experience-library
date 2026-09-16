# HALCON hdict → YOLO Format Converter

## 项目概述
将 HALCON `.hdict` 数据集文件转换为 YOLO 格式（label files + classes.txt + dataset.yaml），通过 `.hdvp` 过程文件供 C# HDevEngine 调用。

## 目录结构
```
D:\AiProjects\halcon_yolo_converter\
├── procedures\
│   ├── convert_hdict_to_yolo.hdvp    # 主转换过程
│   └── analyze_hdict_structure.hdvp  # 数据集分析过程
├── output\                            # YOLO 输出目录
├── test_convert.hdev                  # 转换测试脚本
└── test_analyze.hdev                  # 分析测试脚本
```

## 关键发现

### 1. hrun.exe 环境下的特殊行为
- `set_check('~give_error')` 在 hrun 模式下**不生效** — 大多数运算符错误仍会终止脚本
- `make_dir` 在目录已存在时抛出错误 #5282 并终止
- 解决方案：使用 `system_call('cmd.exe /c mkdir "path" 2>nul')` 替代 `make_dir`
- 所有运算符错误都会向上传播到 C# HDevEngine 调用方

### 2. 图像对象检测
- `|Image|` 对 HALCON 图像对象（iconic）使用后会导致后续 `get_image_size` 失败
- **必须使用** `count_obj(Image, NumObj)` + `if (NumObj > 0)` 替代 `if (|Image| > 0)`

### 3. JSON 字段提取模式
- `tuple_regexp_match` 无捕获组时返回空元组 — **不适用于子串匹配**
- `tuple_regexp_replace` 只替换第一个匹配项 — 可用于两步骤提取
- 两步提取模式：
  ```
  tuple_regexp_replace(JSONStr, '.*"key_name":', '', Temp)     # 去掉 key 前缀
  tuple_regexp_replace(Temp, ',.*', '', Result)                 # 去掉尾部后缀
  ```
- 紧凑 JSON 格式（单行无空格），`.` 匹配所有字符（包括跨行）

### 4. 字符串操作
- `tuple_strstr` 返回 0-indexed 位置
- `tuple_substr(Str, Start, End)` 两端包含（inclusive）

### 5. hdvp 过程文件接口参数
- **`dimension="1"` 输出参数在 hrun 下会破坏所有输出绑定** — 必须使用 `dimension="0"`（接受标量和元组）

### 6. 数据集特征
- 单类数据集（1 class: "泡棉"）
- 98 samples
- 所有样本 bbox 近似相同：row≈[87.1, 373.3], col≈[93.3, 655.6]
- 图像尺寸：727 × 456

## 使用的文件
```
hdict ← D:\codex\AutoLabelPlatform\数据集.hdict (32956 bytes, 98 samples)
images ← D:\AiProjects\...\12\P1\*.png (98 PNGs, 727×456)
output ← D:\AiProjects\halcon_yolo_converter\output\
```

## 参考
- HALCON 24.11, HDevEngine (.NET), hrun.exe (batch mode)
- YOLO 格式：`class_id x_center y_center width height` (归一化 0-1)
