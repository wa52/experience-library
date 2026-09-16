# Label Studio 插件模板

## 适用场景
开发 Label Studio 的自定义标注界面、导出格式或 ML 后端。

## 类型

### 1. 自定义标注界面 (Labeling Config)
```xml
<View>
  <Image name="img" value="$image"/>
  <RectangleLabels name="label" toName="img">
    <Label value="缺陷" background="#FF0000"/>
  </RectangleLabels>
</View>
```

### 2. 自定义导出格式
编写 Python 脚本解析 Label Studio JSON 输出为目标格式。

### 3. ML 后端
基于 label-studio-ml-backend 搭建自动标注服务。

## 参考
- patterns/label_studio_converter.md
- domains/label_studio/README.md
