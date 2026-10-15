# -*- coding: utf-8 -*-
"""PolyXRD RutAna（GB/T 30793—2014 晶型比率测定）GUI 抓图。

必须用**真实 Windows 显示平台**运行（离屏模式下中文字体回退成豆腐块）::

    D:/Project/XRD/python310/python.exe tools/capture_rutana.py

截图内容全部由 **真实 core 计算** 驱动（A 法测峰 / K 标定 / B 法 Rietveld 精修），
不使用桩数据；虚拟标准样取自 PolyXRD-RutAna 仓库 ``tests/data/virtual/``
（seed=20260701，可复现）。

输出：``tools/shots/rutana/*.png``
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

RUTANA = Path("D:/Project/XRD/PolyXRD-RutAna")
OUT = Path("D:/Project/XRD/PolyXRD-Manual/tools/shots/rutana")
VIRTUAL = RUTANA / "tests" / "data" / "virtual"

sys.path.insert(0, str(RUTANA))


def _pump(app, n=30, delay=0.01):
    for _ in range(n):
        app.processEvents()
        time.sleep(delay)


def snap(widget, path: Path, app, delay=12):
    widget.show()
    _pump(app, delay)
    path.parent.mkdir(parents=True, exist_ok=True)
    widget.grab().save(str(path), "PNG")
    print("saved:", path.name, widget.width(), "x", widget.height())


def main() -> int:
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])

    from rutana.core import peakmeasure
    from rutana.gui import services
    from rutana.gui.busy import BusyDialog
    from rutana.gui.dialogs import AboutDialog
    from rutana.gui.khelp import KHelpDialog
    from rutana.gui.kwizard import KCalibWizardDialog
    from rutana.gui.main_window import MainWindow
    from rutana.i18n import set_language, tr

    set_language("zh_CN")
    print("core protocol in use:", peakmeasure.PROTOCOL_V100.name)

    # ---------------------------------------------------------------- 1) 初始界面
    win = MainWindow()
    win.resize(1280, 800)
    win.tabs.a_panel.clear_result_a()
    snap(win, OUT / "01_main_empty.png", app)

    # ---------------------------------------------------------------- 2) 导入谱图
    # 一份窄窗谱（A 法 24.5–28.5°）+ 一份宽扫全谱（B 法 5–90°），同为 w(锐钛)=50% 虚拟样
    for name in ("v50.xy", "v50_wide.xy"):
        p = str(VIRTUAL / name)
        win._patterns[p] = services.load_pattern(p)
        win.file_list.addItem(name)
    win.file_list.setCurrentRow(0)
    _pump(app, 20)
    snap(win, OUT / "02_main_loaded.png", app)

    # ---------------------------------------------------------------- 3) K 标定向导
    # 三个标准混合样：w(金红石型) = 75 / 50 / 25 %（对应 v25 / v50 / v75）
    specs = [
        {"file": str(VIRTUAL / "v25.xy"), "wr": 75.0},
        {"file": str(VIRTUAL / "v50.xy"), "wr": 50.0},
        {"file": str(VIRTUAL / "v75.xy"), "wr": 25.0},
    ]
    wizard = KCalibWizardDialog(win, win_a=(24.5, 26.5), win_r=(26.5, 28.5))
    for spec in specs:
        wizard.add_row(spec["file"], spec["wr"])
    measured = services.measure_calib_rows(
        specs, (24.5, 26.5), (26.5, 28.5))
    wizard._apply_measure(measured)
    for row in measured:
        print(f"  calib {Path(row['file']).name}: wr={row['wr']}% "
              f"Ia/Ir={row['ratio_i']:.4f} ok={row['ok']}")
    fit = wizard.fit_result()
    print("  fit:", fit)
    _pump(app, 20)
    snap(wizard, OUT / "04_k_wizard.png", app)

    # 采用此 K 回填 A 法面板（与用户点「采用此 K」等价）
    win.tabs.a_panel.set_k(fit["K"], fit["r2"])
    wizard.close()

    # ---------------------------------------------------------------- 4) K 值说明
    khelp = KHelpDialog(win)
    _pump(app, 15)
    snap(khelp, OUT / "05_k_help.png", app)
    khelp.close()

    # ---------------------------------------------------------------- 5) A 法结果
    # 主窗口切回窄窗谱；已导入两份谱 -> 自动做双平行合并
    win.file_list.setCurrentRow(0)
    _pump(app, 10)
    win.tabs.setCurrentIndex(0)
    win.tabs.a_panel.chk_ref.setChecked(True)
    win.tabs.a_panel.sp_ref.setValue(50.0)
    data = services.run_method_a(
        win._patterns[str(VIRTUAL / "v50.xy")],
        (24.5, 26.5), (26.5, 28.5), win.tabs.a_panel.current_k(),
        second_pat=win._patterns[str(VIRTUAL / "v50_wide.xy")])
    win._apply_a_result(data)
    res, dup = data["result"], data["dup"]
    print(f"  A: wa={res.wa:.2f} wr={res.wr:.2f} K={res.K:.4f} "
          f"Ia/Ir={res.ia / res.ir:.4f} dup_diff={dup['abs_diff']:.3f} "
          f"within={dup['within_limit']}")
    _pump(app, 20)
    snap(win, OUT / "03_a_result.png", app)

    # ---------------------------------------------------------------- 6) B 法结果
    # 切到宽扫全谱，跑真实 Rietveld 精修（realdata 推荐配置）
    win.file_list.setCurrentRow(1)
    _pump(app, 10)
    win.tabs.setCurrentIndex(1)
    _pump(app, 10)
    t0 = time.time()
    bdata = services.run_method_b(
        win._patterns[str(VIRTUAL / "v50_wide.xy")],
        refine_zero=True, refine_uvw=True, refine_eta=True, n_bg=3)
    print(f"  B: refine {time.time() - t0:.1f}s  "
          f"Rwp={bdata['result'].rf.rwp:.2f} Rp={bdata['result'].rf.rp:.2f} "
          f"chi2={bdata['result'].rf.chi2:.3f}")
    win._apply_b_result(bdata)
    _pump(app, 20)
    snap(win, OUT / "06_b_result.png", app)

    # ---------------------------------------------------------------- 7) 忙对话框
    busy = BusyDialog(win, title=tr("busy.title_refine"), cancellable=False)
    busy.start_timer()
    busy.set_message(tr("busy.refine", gen=12, rwp=bdata["result"].rf.rwp), 63)
    busy.set_iteration(12, bdata["result"].rf.rwp)
    _pump(app, 25, 0.05)
    snap(busy, OUT / "07_busy.png", app)
    busy.finish()
    busy.close()

    # ---------------------------------------------------------------- 8) 关于对话框
    about = AboutDialog(win)
    _pump(app, 15)
    snap(about, OUT / "08_about.png", app)
    about.close()

    win.close()
    print("DONE rutana")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
