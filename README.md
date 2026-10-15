# PolyXRD 家族软件使用手册（PolyXRD Manual）

本仓库集中收录 **PolyXRD 家族** 全部软件的中文 PDF 使用手册、界面截图与许可文件。
各软件的源代码与发行版（exe 安装包 / Release）分别存放在各自的独立仓库中。

<div align="center"><img src="logo-horizontal.png" alt="PolyXRD Family" width="480"></div>

## 家族成员一览

| 软件 | 定位 | 当前版本 | 使用手册（PDF） | 仓库 / 发行版 |
|---|---|---|---|---|
| **PolyXRD** | 多晶 X 射线衍射（XRD）图谱综合分析套件：数据加载 → 预处理 → 峰检测 → 物相检索（FoM 打分 / 四态元素过滤 / 候选去重）→ Rietveld 结构精修（GSAS-II / MAUD / FullProf 桥接）→ 报告 | v2.9.0 | [manuals/PolyXRD/PolyXRD使用手册-v2.9.0.pdf](manuals/PolyXRD/PolyXRD使用手册-v2.9.0.pdf) | [PolyXRD/PolyXRD](https://github.com/PolyXRD/PolyXRD) |
| **PolyXRD-Converter** | XRD 谱图格式转换器：30+ 格式读入、8 种格式写出、多厂商 RAW 二进制自动识别（岛津 / 理学 / Scintag / Bruker / MDI）、批量转换、角度轴护栏 | v1.4.1 | [manuals/PolyXRD-Converter/PolyXRD-Converter使用手册-v1.4.1.pdf](manuals/PolyXRD-Converter/PolyXRD-Converter使用手册-v1.4.1.pdf) | [PolyXRD/PolyXRD-Converter](https://github.com/PolyXRD/PolyXRD-Converter) |
| **PolyXRD-CifCalc** | 面向 XRD 的 CIF 晶体结构检索与生成工具：联网 COD / 本地数据库 / 扩展源检索，CIF 派生与合成、结构微调、pymatgen 校验、VESTA 联动、三语界面 | v1.6.0 | [manuals/PolyXRD-CifCalc/PolyXRD-CifCalc使用手册-v1.6.0.pdf](manuals/PolyXRD-CifCalc/PolyXRD-CifCalc使用手册-v1.6.0.pdf) | [PolyXRD/PolyXRD-CifCalc](https://github.com/PolyXRD/PolyXRD-CifCalc) |
| **PolyXRD-GetCIF** | CIF 检索与获取小工具（CifCalc 的轻量姊妹版）：COD / 本地库 / AMCSD / Materials Project / Atomly 五数据源，标准版与 Plus 版（含 3D 预览） | v1.0.0 | [manuals/PolyXRD-GetCIF/PolyXRD-GetCIF使用手册-v1.0.0.pdf](manuals/PolyXRD-GetCIF/PolyXRD-GetCIF使用手册-v1.0.0.pdf) | [PolyXRD/PolyXRD-GetCIF](https://github.com/PolyXRD/PolyXRD-GetCIF) |
| **PolyXRD-SynthPattern** | XRD 谱图合成：从 CIF 结构因子出发生成带真实仪器特征的模拟衍射谱（pseudo-Voigt 峰形、Kα2 双线、择优取向、晶粒尺寸 / 微应变展宽等），用于检索方法验证与教学 | v1.3.1 | [manuals/PolyXRD-SynthPattern/PolyXRD-SynthPattern使用手册-v1.3.1.pdf](manuals/PolyXRD-SynthPattern/PolyXRD-SynthPattern使用手册-v1.3.1.pdf) | [PolyXRD/PolyXRD-SynthPattern](https://github.com/PolyXRD/PolyXRD-SynthPattern) |

> 各软件的源代码仓库当前为**私有**；公开下载请前往各仓库的 **GitHub Releases** 页面（Release 与安装包公开可见）。

## 典型工作流

```
仪器原始数据 (.RAW / .brml / .xrdml / .xy …)
        │
        ▼
PolyXRD-Converter ──格式转换──► 两列文本 / xrdml / json …
        │
        ▼
PolyXRD ──预处理 → 峰检测 → 物相检索 → Rietveld 精修──► 分析报告
        │                    │
        │ 检索到的物相        │ 需要 CIF 初始模型？
        ▼                    ▼
PolyXRD-CifCalc / GetCIF ──CIF──► GSAS-II / FullProf / MAUD / VESTA
        │
        ▼
PolyXRD-SynthPattern ──模拟谱──► 检索算法验证 / 教学演示
```

- **拿到一份陌生谱图**：先用 Converter 认格式、转成标准文本，再进 PolyXRD 走完整分析流程。
- **精修缺 CIF 初始模型**：用 CifCalc（全链路：检索 + 生成 + 微调 + 校验）或 GetCIF（只要一份 CIF）检索下载。
- **验证检索算法 / 备课**：用 SynthPattern 从已知 CIF 合成「已知答案」的模拟谱。

## 手册内容说明

每份手册（约 15~27 页）均包含：

- **软件介绍与能力一览**——定位、核心模块、系统要求
- **安装与启动**——发行形态、首次运行注意事项
- **界面导览与操作流程**——图文对照，截图全部取自软件实际运行画面
- **原理介绍**——检索打分、峰形函数、Rietveld、RAW 解析、谱图合成管线等
- **使用技巧、注意事项与 FAQ**——常见错误的排查路径
- **联系与许可**——学术 / 商业双许可要点

## 许可（License）

家族全部软件统一采用**学术 / 商业双许可**：

- **学术研究与教学**：可免费使用（请保留版权与许可声明）；
- **商业用途**：须在使用前联系版权持有人取得书面商业授权。

各软件的完整条款见 [`licenses/`](licenses/) 目录（`LICENSE` 英文 / `LICENSE-CN` 中文），与各软件仓库内随附文件一致。

版权所有 © 2026 PolyXRD Team · 联系邮箱：**sshztx@outlook.com**

### 第三方致谢

- **数据源**：COD（Crystallography Open Database）· AMCSD/RRUFF · Materials Project · Atomly 的公开数据服务
- **开源依赖**：PySide6 (LGPL/GPL)、numpy (BSD)、reportlab、pymatgen、PyInstaller 等
- **参考实现**：GSAS-II（Argonne 开源）在格式验证中作为 oracle 使用

---

<div align="right"><i>PolyXRD Team · 2025 — 2026</i></div>
