# PolyXRD Family Software User Manual (PolyXRD Manual)

This repository collects the Chinese PDF user manuals, UI screenshots and license files of all **PolyXRD Family** software in one place.
The source code and distributions (exe installer / Release) of each software are stored in their own separate repositories.

<div align="center"><img src="logo-horizontal.png" alt="PolyXRD Family" width="480"></div>

## Family Members at a Glance

| Software | Positioning | Current Version | User Manual (PDF) | Repository / Release |
|---|---|---|---|---|
| **PolyXRD** | Comprehensive analysis suite for polycrystalline X-ray diffraction (XRD) patterns: data loading → preprocessing → peak detection → phase identification (FoM scoring / four-state element filtering / candidate deduplication / multi-database external support including XinMatch format databases) → Rietveld structure refinement (GSAS-II / MAUD / FullProf bridging) → report | v3.2.0 | [PolyXRD user manual v3.2.0 (PDF, Chinese)](manuals/PolyXRD/PolyXRD使用手册-v3.2.0.pdf) | [PolyXRD/PolyXRD](https://github.com/PolyXRD/PolyXRD) |
| **PolyXRD-Converter** | XRD pattern format converter: 30+ formats for reading, 8 formats for writing, automatic identification of multi-vendor RAW binary data (Shimadzu / Rigaku / Scintag / Bruker / MDI), batch conversion, angle-axis guardrails | v1.4.1 | [PolyXRD-Converter user manual v1.4.1 (PDF, Chinese)](manuals/PolyXRD-Converter/PolyXRD-Converter使用手册-v1.4.1.pdf) | [PolyXRD/PolyXRD-Converter](https://github.com/PolyXRD/PolyXRD-Converter) |
| **PolyXRD-CifCalc** | A CIF crystal-structure retrieval and generation tool for XRD: online COD / local database / extended-source search, CIF derivation and synthesis, structure fine-tuning, pymatgen validation, VESTA integration, trilingual UI | v1.6.0 | [PolyXRD-CifCalc user manual v1.6.0 (PDF, Chinese)](manuals/PolyXRD-CifCalc/PolyXRD-CifCalc使用手册-v1.6.0.pdf) | [PolyXRD/PolyXRD-CifCalc](https://github.com/PolyXRD/PolyXRD-CifCalc) |
| **PolyXRD-GetCIF** | A lightweight CIF retrieval and acquisition tool (the lightweight sister edition of CifCalc): five data sources — COD / local database / AMCSD / Materials Project / Atomly — Standard and Plus editions (with 3D preview) | v1.0.0 | [PolyXRD-GetCIF user manual v1.0.0 (PDF, Chinese)](manuals/PolyXRD-GetCIF/PolyXRD-GetCIF使用手册-v1.0.0.pdf) | [PolyXRD/PolyXRD-GetCIF](https://github.com/PolyXRD/PolyXRD-GetCIF) |
| **PolyXRD-SynthPattern** | XRD pattern synthesis: generates simulated diffraction patterns with realistic instrumental features from CIF structure factors (pseudo-Voigt peak shape, Kα2 doublet, preferred orientation, crystallite size / microstrain broadening, etc.); used for validating search methods and teaching | v1.3.1 | [PolyXRD-SynthPattern user manual v1.3.1 (PDF, Chinese)](manuals/PolyXRD-SynthPattern/PolyXRD-SynthPattern使用手册-v1.3.1.pdf) | [PolyXRD/PolyXRD-SynthPattern](https://github.com/PolyXRD/PolyXRD-SynthPattern) |
| **PolyXRD-RutAna** | Determines the anatase/rutile ratio in TiO₂ pigments per GB/T 30793—2014: a dual route of Method A (intensity-ratio method, on-site K calibration + duplicate-pair acceptance decision) and Method B (Rietveld full-pattern fitting, Hill–Howard quantification, Rwp ≤ 10%) | v1.5.0 | [PolyXRD-RutAna user manual v1.5.0 (PDF, Chinese)](manuals/PolyXRD-RutAna/PolyXRD-RutAna使用手册-v1.5.0.pdf) | [PolyXRD/PolyXRD-RutAna](https://github.com/PolyXRD/PolyXRD-RutAna) |

> The source-code repositories of all software are currently **private**; for public downloads please go to the **GitHub Releases** page of each repository (Releases and installers are publicly visible).

## Typical Workflow

```
Instrument raw data (.RAW / .brml / .xrdml / .xy …)
        │
        ▼
PolyXRD-Converter ──format conversion──► two-column text / xrdml / json …
        │
        ▼
PolyXRD ──preprocessing → peak detection → phase identification → Rietveld refinement──► analysis report
        │                    │
        │ identified phases   │ need a CIF initial model?
        ▼                    ▼
PolyXRD-CifCalc / GetCIF ──CIF──► GSAS-II / FullProf / MAUD / VESTA
        │
        ▼
PolyXRD-SynthPattern ──simulated pattern──► search algorithm validation / teaching demonstration

Dedicated determination line (GB/T 30793—2014 · TiO₂ pigment crystal-form ratio)
        │
        ▼
PolyXRD-RutAna ──Method A (intensity ratio / K calibration + duplicate pairs)──► anatase : rutile ratio + test report
              └──Method B (Rietveld full-pattern fitting / Hill–Howard)──┘
```

- **Getting an unfamiliar diffraction pattern**: first use Converter to identify the format and convert it to standard text, then run the full analysis workflow in PolyXRD.
- **Refinement lacks a CIF initial model**: use CifCalc (full chain: retrieval + generation + fine-tuning + validation) or GetCIF (just one CIF) to search and download.
- **Validating search algorithms / preparing lessons**: use SynthPattern to synthesize a simulated pattern with a "known answer" from a known CIF.
- **TiO₂ pigment crystal-form ratio determination**: use RutAna to produce results per GB/T 30793—2014; Method A first calibrates K on site with your own standard sample, Method B performs direct full-pattern fitting, and both can export an archivable HTML report.

## Manual Contents

Each manual (about 15~27 pages) contains:

- **Software introduction and capability overview** — positioning, core modules, system requirements
- **Installation and startup** — distribution form, notes for first run
- **UI tour and operation workflow** — illustrated side by side, all screenshots taken from the actual running software
- **Principles** — search scoring, peak-shape functions, Rietveld, RAW parsing, pattern-synthesis pipeline, etc.
- **Tips, notes and FAQ** — troubleshooting paths for common errors
- **Contact and licensing** — key points of the academic / commercial dual license

## License

All software in the family uniformly adopts an **academic / commercial dual license**:

- **Academic research and teaching**: free to use (please retain the copyright and license notice);
- **Commercial use**: you must contact the copyright holder to obtain written commercial authorization before use.

The full terms of each software are in the [`licenses/`](licenses/) directory (`LICENSE` in English / `LICENSE-CN` in Chinese), consistent with the files bundled in each software repository.

Copyright © 2026 PolyXRD Team · Contact email: **sshztx@outlook.com**

### Third-Party Acknowledgments

- **Data sources**: COD (Crystallography Open Database) · AMCSD/RRUFF · Materials Project · public data services of Atomly
- **Open-source dependencies**: PySide6 (LGPL/GPL), numpy (BSD), reportlab, pymatgen, PyInstaller, etc.
- **Reference implementation**: GSAS-II (open source from Argonne) used as an oracle in format validation

---

<div align="right"><i>PolyXRD Team · 2025 — 2026</i></div>
