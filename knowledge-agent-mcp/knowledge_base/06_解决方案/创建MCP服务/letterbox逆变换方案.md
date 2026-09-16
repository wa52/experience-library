---
id: solution-halcon-letterbox-inverse-transform
title: HALCON语义分割 letterbox 逆变换方案
category: solution
knowledge_type: solution
domain: technology/halcon/semantic-segmentation
tags: [letterbox, inverse-transform, segmentation]
technologies: [HALCON]
languages: [HDevelop, CSharp]
versions:
  applicable: ["20.11", "24.11"]
status: verified
confidence: 0.9
source_ids: [project-csharp-halcon-overview]
related_items:
  related_to: [bug-halcon-segmentation-offset, code-halcon-segmentation-restore]
created_at: 2026-07-12
updated_at: 2026-07-12
---

# HALCON语义分割 letterbox 逆变换方案

先记录缩放比例和 padding，再在后处理阶段对轮廓或 mask 坐标做逆变换。
