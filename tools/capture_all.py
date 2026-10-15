# -*- coding: utf-8 -*-
"""PolyXRD 家族软件离屏/真机抓图（真实 Windows 平台，中文字体正确）。

用法：python capture_all.py <app>   # app: cifcalc | converter | getcif | synth
输出：D:/Project/XRD/_manual_build/shots/<app>/*.png
"""
import sys
from pathlib import Path

OUT = Path("D:/Project/XRD/_manual_build/shots")
OUT.mkdir(parents=True, exist_ok=True)


def snap(widget, path, app, delay=8):
    widget.show()
    for _ in range(delay):
        app.processEvents()
    widget.grab().save(str(path))
    widget.close()
    print("saved:", path.name)


def shot_cifcalc():
    sys.path.insert(0, "D:/Project/XRD/PolyXRD-CifCalc/src")
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    from cifcalc.core.schema import (
        AdapterStatus, CandidateStructure, LatticeParams, QueryResult, SourceType,
    )
    from cifcalc.ui.main_window import MainWindow
    from cifcalc.ui.search_progress import SearchProgressDialog
    from cifcalc.ui.settings_dialog import SettingsDialog

    out = OUT / "cifcalc"
    out.mkdir(exist_ok=True)

    win = MainWindow()
    win.resize(1280, 800)
    snap(win, out / "01_main_empty.png", app)

    # 注入候选 + 生成 CIF 预览
    def cand(cid, source, formula, sg, a, c):
        return CandidateStructure(
            candidate_id=cid, source=SourceType(source), source_id=cid.split(":")[-1],
            formula=formula, elements={"Si", "O"}, space_group=sg,
            lattice=LatticeParams(a=a, b=a, c=c, alpha=90.0, beta=90.0, gamma=120.0),
        )
    cands = [
        cand("cod:1010921", "cod", "O2 Si", "P 31 2 1", 4.913, 5.405),
        cand("cod:9004263", "cod", "O4 Si2", "P 21/c", 4.958, 6.021),
        cand("amcsd:2451", "amcsd", "O2 Si", "P 31 2 1", 4.910, 5.402),
        cand("pcod_local:0007", "pcod_local", "O8 Si4", "P 1", 4.921, 5.411),
    ]
    result = QueryResult()
    result.candidates = cands
    result.statuses = [
        AdapterStatus(name="cod", available=True, result_count=2),
        AdapterStatus(name="amcsd", available=True, result_count=1),
    ]
    win.candidate_list.set_candidates(cands)
    win.routing_indicator.update_result(result)
    demo_cif = """data_quartz
_chemical_formula_sum         'O2 Si'
_space_group_name_H-M_alt     'P 1'
_cell_length_a                4.9130
_cell_length_b                4.9130
_cell_length_c                5.4050
_cell_angle_alpha             90.0
_cell_angle_beta              90.0
_cell_angle_gamma             120.0
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
  Si1  Si  0.4697  0.0000  0.0000
  O1   O   0.4135  0.2669  0.1191
  O2   O   0.2669  0.4135  0.1191
"""
    win._on_candidate_selected(cands[0])
    win.cif_preview.set_candidate(cands[0], demo_cif, "按化学式/晶胞合成 · 校验通过 · CIF 解析正常")
    app.processEvents()
    snap(win, out / "02_main_candidates.png", app)

    dlg = SearchProgressDialog(["cod", "amcsd"], query_summary="化学式 SiO2")
    dlg.resize(520, 420)
    dlg.mark_started("cod")
    dlg.mark_done("cod", 5)
    dlg.mark_started("amcsd")
    for _ in range(8):
        app.processEvents()
    dlg.show()
    for _ in range(8):
        app.processEvents()
    dlg.grab().save(str(out / "03_search_progress.png"))
    dlg.close()
    print("saved: 03_search_progress.png")

    sd = SettingsDialog(config=win.config, parent=None)
    sd.resize(640, 560)
    snap(sd, out / "04_settings.png", app)
    win.close()


def shot_converter():
    sys.path.insert(0, "D:/Project/XRD/PolyXRD-Converter/src")
    from pathlib import Path as P
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    from polyxrd_converter.ui_main import MainWindow

    out = OUT / "converter"
    out.mkdir(exist_ok=True)
    win = MainWindow()
    win.resize(1280, 800)
    snap(win, out / "01_main_empty.png", app)

    files = [
        P("D:/Project/XRD/test_xrd/raw/1-2.raw"),
        P("D:/Project/XRD/test_xrd/raw/2-1.raw"),
        P("D:/Project/XRD/test_xrd/geshi/4-1.xy"),
    ]
    files = [f for f in files if f.is_file()]
    win.add_paths(files)
    for _ in range(10):
        app.processEvents()
    # 选中第一行触发预览
    try:
        table = win.table if hasattr(win, "table") else None
        if table is not None:
            table.selectRow(0)
    except Exception as exc:
        print("select row skipped:", exc)
    for _ in range(10):
        app.processEvents()
    snap(win, out / "02_main_files.png", app)
    win.close()


def shot_getcif():
    sys.path.insert(0, "D:/Project/XRD/PolyXRD-GetCIF/src")
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    from getcif.core.schema import Candidate, LatticeParams
    from getcif.ui.main_window import MainWindow

    out = OUT / "getcif"
    out.mkdir(exist_ok=True)
    win = MainWindow()
    win.resize(1280, 800)
    snap(win, out / "01_main_empty.png", app)

    cands = [
        Candidate(source="cod", source_id="1010921", formula="O2 Si",
                  mineral_name="Quartz", space_group="P 31 2 1",
                  lattice=LatticeParams(a=4.913, b=4.913, c=5.405,
                                        alpha=90, beta=90, gamma=120),
                  elements={"Si", "O"},
                  cif_url="https://www.crystallography.net/cod/1010921.cif"),
        Candidate(source="cod", source_id="9004263", formula="O4 Si2",
                  mineral_name="Cristobalite", space_group="P 4 21 2",
                  lattice=LatticeParams(a=4.9782, b=4.9782, c=6.9494,
                                        alpha=90, beta=90, gamma=90),
                  elements={"Si", "O"},
                  cif_url="https://www.crystallography.net/cod/9004263.cif"),
        Candidate(source="amcsd", source_id="2451", formula="O2 Si",
                  mineral_name="Quartz", space_group="P 31 2 1",
                  lattice=LatticeParams(a=4.910, b=4.910, c=5.402,
                                        alpha=90, beta=90, gamma=120),
                  elements={"Si", "O"}),
    ]
    win.result_table.set_results(cands, partial=False)
    app.processEvents()
    snap(win, out / "02_main_results.png", app)
    win.close()

    # 预览窗
    from getcif.ui.preview_dialog import PreviewDialog
    demo_cif = """data_quartz
_chemical_formula_sum 'O2 Si'
_cell_length_a 4.9130
_cell_length_b 4.9130
_cell_length_c 5.4050
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
  Si1 Si 0.4697 0.0000 0.0000
  O1  O  0.4135 0.2669 0.1191
"""
    c = cands[0]
    c.cif_content = demo_cif
    pv = PreviewDialog(c)
    pv.resize(900, 700)
    snap(pv, out / "03_preview.png", app)


def shot_synth():
    sys.path.insert(0, "D:/Project/XRD/PolyXRD-SynthPattern")
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    import xrd_synth_app as xapp

    out = OUT / "synthpattern"
    out.mkdir(exist_ok=True)
    win = xapp.MainWindow()
    win.resize(1280, 860)
    snap(win, out / "01_main_empty.png", app)

    cif = Path("D:/Project/XRD/PolyXRD-SynthPattern/tests/data/si_diamond_p1.cif")
    try:
        win._add_phase_row(str(cif))
        app.processEvents()
        win._generate_method1()
        for _ in range(20):
            app.processEvents()
        snap(win, out / "02_main_synth.png", app)
    except Exception as exc:
        print("synth skipped:", exc)
    win.close()


def shot_rutana():
    """RutAna（GB/T 30793—2014 晶型比率测定）—— 抓图逻辑独立成 capture_rutana.py。"""
    import capture_rutana
    capture_rutana.main()


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    {"cifcalc": shot_cifcalc, "converter": shot_converter,
     "getcif": shot_getcif, "synth": shot_synth,
     "rutana": shot_rutana}[name]()
    print("DONE", name)
