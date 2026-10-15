# tools/ —— 手册构建工具

本目录收录 PolyXRD 家族中文 PDF 手册的**生成代码**（reportlab 数据驱动管线）与**原始截图**。

## 文件说明

| 文件 | 作用 |
|---|---|
| `manual_lib.py` | 共享构建库：A4 版式、微软雅黑字体、封面 / 目录 / 正文 / 表格 / tip·warn 标注框 / 截图（图 X-Y 编号）/ 页脚页码 / 联系许可块。CONTENT 数据驱动，章节项类型：`h1/h2/h3/p/table/tip/warn/shot/pagebreak/toc/contact/end` |
| `gen_cifcalc.py` | CifCalc v1.6.0 手册内容（17 页） |
| `gen_converter.py` | Converter v1.4.1 手册内容（15 页） |
| `gen_getcif.py` | GetCIF v1.0.0 手册内容（14 页） |
| `gen_synthpattern.py` | SynthPattern v1.3.1 手册内容（14 页） |
| `gen_polyxrd.py` | PolyXRD v2.9.0 手册内容（27 页，融合 v2.7.0 手册 + v2.8.0 / v2.9.0 变更） |
| `gen_rutana.py` | RutAna v1.0.0 手册内容（25 页，GB/T 30793—2014 晶型比率测定） |
| `capture_all.py` | 四款软件的 GUI 自动抓图脚本（真实 Windows 平台短暂弹窗 + `widget.grab()`；离屏模式中文会变豆腐块，勿用） |
| `capture_rutana.py` | RutAna GUI 抓图脚本：由**真实 core 计算**驱动（A 法测峰 / K 标定 / B 法 Rietveld 精修），虚拟标准样取自 PolyXRD-RutAna `tests/data/virtual/`（seed=20260701 可复现） |
| `shots/` | capture_all.py / capture_rutana.py 抓取的原始截图（与 `manuals/<App>/img/` 同源） |
| `screenshot-manual-to-pdf.zip` | 手册生成所用 WorkBuddy skill 包（存档） |

## 再生成一份手册

```bash
# 环境依赖：Pillow + reportlab（PolyXRD venv 已齐备）
PYTHONPATH=tools python tools/gen_cifcalc.py
# 产物直接落盘到 manuals/<App>/ 下的 PDF
```

- 抓图脚本需用带 PySide6 的解释器、并在真实 Windows 显示平台运行
  （`D:/Project/XRD/python310/python.exe tools/capture_rutana.py`；勿设 `QT_QPA_PLATFORM=offscreen`）。
- 各 gen 脚本内的输出路径、截图目录均为 `PolyXRD-Manual` 仓库内的绝对路径，移动仓库位置后需相应调整。
- 改动内容只需编辑 gen 脚本里的 `CONTENT`（纯数据结构），无需碰 `manual_lib.py`。

## 排版经验（踩坑记录）

1. **正文左对齐**：reportlab 的 `TA_JUSTIFY` 在中文混排 ASCII（如 `2θ`、`+`）时会拉开巨大空隙，中文手册一律用 `TA_LEFT`。
2. **表格单元格必须包 Paragraph**：`Table` 直接收原始字符串不换行、`<b>` 标签原样显示，长文本会溢出页边；`make_table` 已统一包装为 `Paragraph`。
3. **抓图必须用真实显示平台**：`QT_QPA_PLATFORM=offscreen` 下 Qt 回退 DejaVu 字体，中文变豆腐块。

## archive/ 说明

`../archive/PolyXRD-docs-manual/` 收录 PolyXRD 主程序的历史版手册（v2.0.1 / v2.5.0 / v2.7.0 的 PDF、md、html 及配图），已从主程序仓库 `docs/manual/` 转移至此集中管理。最新版手册见 `../manuals/`。
