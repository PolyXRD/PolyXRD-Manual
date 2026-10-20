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
| `gen_polyxrd.py` | PolyXRD v3.2.0 手册内容（26 页，含 v3.0 WPSM / v3.1 XinMatch 四表库与任意位置挂载 / v3.2 超大库可用性修复） |
| `gen_rutana.py` | RutAna v1.5.0 手册内容（35 页详细版：Setup 安装向导、注册与版次、批量计算、协议对齐、择优取向） |
| `capture_all.py` | 四款软件的 GUI 自动抓图脚本（真实 Windows 平台短暂弹窗 + `widget.grab()`；离屏模式中文会变豆腐块，勿用） |
| `capture_rutana.py` | RutAna v1.5.0 GUI 抓图脚本：由**真实 core 计算**驱动（A 法测峰 / K 标定 / B 法 Rietveld / 批量），真实数据取自 PolyXRD-RutAna `tests/data/real/`（岛津 TiO₂ 数据集）；注册码截图自动打码 |
| `capture_setup_wizard.ps1` | RutAna Setup 安装包（Inno Setup）向导抓图：Win32 BM_CLICK 驱动真实安装流程（无需前台焦点），PrintWindow 截图；需 UTF-8 BOM 保存 |
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
3. **中文不能靠 Qt 默认字体**：`QT_QPA_PLATFORM=offscreen` 下 Qt 会回退 DejaVu，中文变豆腐块。两条路都可行——① 真实 Windows 平台（`capture_all.py` / `capture_rutana.py` 走这条）；② 仍用 offscreen 但**先注入系统字体**（`QFontDatabase.addApplicationFont(msyh.ttc…)`）+ 强制浅色 Palette（PolyXRD 的抓图脚本走这条）。
4. **表格整体不拆页**（v3.2.0 起 `make_table` 设 `splitByRow=0`）：拆页只剩两三行时，后面紧跟章节分页会让整页几乎空白（v3.2.0 手册第一版第 10 页只剩「谱图交互」表两行）。本套手册最长的表 6 行，一页放得下。
5. **目录后不要再多写 `("pagebreak",)`**：`manual_lib.build` 在目录之后已经自带一次 `PageBreak()`，再写一个会多出**整张空白页**（v2.9.0 手册的空白第 3 页就是这么来的）。
6. **对话框截图先裁掉纯色空带**：Qt 对话框常有成片的空白背景（如快速精修向导顶部 93 px），原样放进 PDF 会把 16 cm 宽拉到 20 cm 高上限、独占一页。用 PIL 按"与角点同色"的行列范围裁一次即可。
7. **抓整窗，别抓子 widget**：离屏模式下**非当前标签页**的子 widget 只有 640×480 的默认尺寸，`widget.grab()` 出来控件互相压字（v2.9.0 手册图 7-1 就是这样，字叠在一起）。截图前先 `tab_widget.setCurrentIndex(...)` 再抓主窗口。
8. **PolyXRD 主程序配图来自主程序仓库**：`PolyXRD/tests/smoke_manual_shots_v270.py`（离屏 + 注入系统字体 + 强制浅色 Palette，19 个步骤全自动）。改动 UI 后重跑它，再把产物拷回 `manuals/PolyXRD/img/`。

## archive/ 说明

`../archive/PolyXRD-docs-manual/` 收录 PolyXRD 主程序的历史版手册（v2.0.1 / v2.5.0 / v2.7.0 的 PDF、md、html 及配图，另含 v2.9.0 PDF），已从主程序仓库 `docs/manual/` 转移至此集中管理。最新版手册见 `../manuals/`。
