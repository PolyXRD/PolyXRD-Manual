# -*- coding: utf-8 -*-
"""PolyXRD RutAna v1.5.0 GUI 抓图（注册版 Setup / 内部评估版双版次）。

必须用**真实 Windows 显示平台**运行（离屏模式下中文字体回退成豆腐块）::

    D:/Project/XRD/python310/python.exe tools/capture_rutana.py

画面全部由 **真实 core 计算** 驱动（A 法测峰 / K 标定 / B 法 Rietveld 精修 /
批量计算），不使用桩数据。数据源：

* A 法、K 标定、批量 —— 岛津 TiO₂ 真实数据集（RutAna 仓 ``tests/data/real/a/``）；
* B 法全谱拟合 —— 同一数据集的 FullProf pd 全谱 ``pd/18%实测谱.txt``（20–120°）。

计算前把谱图复制到临时目录，避免把批量结果 CSV 写回软件仓库。

隐私处理：注册码一律**打码**（像素化 + 高斯模糊），见 :func:`censor`；
状态栏展示的「已注册」演示单位由本脚本现场生成
（``registration.generate_code("示例科技有限公司")``），不触碰真实注册状态文件。

输出：``tools/shots/rutana/*.png``
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

RUTANA = Path("D:/Project/XRD/PolyXRD-RutAna")
OUT = Path("D:/Project/XRD/PolyXRD-Manual/tools/shots/rutana")
SCRATCH = Path("D:/Project/XRD/_manual_build/rutana_v150")
SAMPLES = SCRATCH / "samples"
STATE = SCRATCH / "state"

REAL = RUTANA / "tests" / "data" / "real" / "a"

#: 演示用注册单位（出现在状态栏，避免手册泄露真实注册信息）
DEMO_UNIT = "示例科技有限公司"

#: 真实注册码（仅用于「输入注册码」对话框演示，截图时打码）
REAL_CODE = ("PXRD1-4WZJ-XZVU-UXSL-RLPF-TO6S-BZFY-RLTL-LN7F-RCDO-NHUQ-"
             "4S4K-3ZN7-QMAA-N6EK-Y3WW-KMWQ")

#: 批量完成提示里展示的（示意）结果路径——真实落盘在临时目录
DISPLAY_CSV = r"D:\XRD数据\TiO2-20261017批次\TiO2-20261017批次.csv"

#: 导入清单：(源文件相对路径, 在列表里的显示名)
FILES = [
    ("15percent24-29.txt", "15percent24-29.txt"),
    ("20percent24-29.txt", "20percent24-29.txt"),
    ("50percent24-29.txt", "50percent24-29.txt"),
    ("8percent24-29.txt", "8percent24-29.txt"),
    ("18percent24-29.txt", "18percent24-29.txt"),
    ("36percent24-29.txt", "36percent24-29.txt"),
    ("pd/18%实测谱.txt", "18%实测谱(pd全谱).txt"),
]

#: K 标定用的三个标准混合样：(文件, w(金红石型) %)
CALIB = [("15percent24-29.txt", 15.0),
         ("20percent24-29.txt", 20.0),
         ("50percent24-29.txt", 50.0)]

#: 待测样 + 平行样 + 真值（w(金红石型) %）
#: 注意：谱图复制到 SAMPLES 后一律用**显示名**（FILES 的第二列）引用
SAMPLE = "18percent24-29.txt"
PARALLEL = "18%实测谱(pd全谱).txt"
TRUTH_WR = 18.0

#: B 法全谱拟合用的宽扫全谱
WIDE = "18%实测谱(pd全谱).txt"

sys.path.insert(0, str(RUTANA))


# --------------------------------------------------------------------------- #
# 工具
# --------------------------------------------------------------------------- #
def _pump(app, n=30, delay=0.01):
    for _ in range(n):
        app.processEvents()
        time.sleep(delay)


def snap(widget, path: Path, app, delay=12) -> Path:
    """显示 → 刷新事件 → 抓图 → 存 PNG。"""
    widget.show()
    _pump(app, delay)
    path.parent.mkdir(parents=True, exist_ok=True)
    widget.grab().save(str(path), "PNG")
    print("saved:", path.name, f"{widget.width()}x{widget.height()}")
    return path


def censor(path: Path, rect, host_w: int) -> None:
    """把截图里 ``rect``（host 逻辑坐标 x, y, w, h）区域打码。

    先像素化（降采样再 NEAREST 放大）再高斯模糊，得到典型的「马赛克」效果；
    ``host_w`` 为宿主控件逻辑宽度，用于把逻辑坐标换算到抓图像素
    （125% 缩放下 grab 尺寸 ≠ 逻辑尺寸）。
    """
    from PIL import Image, ImageFilter

    im = Image.open(path).convert("RGB")
    scale = im.width / float(host_w)
    x, y, w, h = (v * scale for v in rect)
    if w <= 0 or h <= 0:
        return
    box = (max(0, round(x)), max(0, round(y)),
           min(im.width, round(x + w)), min(im.height, round(y + h)))
    region = im.crop(box)
    rw, rh = region.size
    small = region.resize((max(2, rw // 14), max(2, rh // 5)), Image.BILINEAR)
    mosaic = small.resize((rw, rh), Image.NEAREST).filter(
        ImageFilter.GaussianBlur(radius=3))
    im.paste(mosaic, box)
    im.save(path)
    print("  censored:", path.name, box)


def _reg_rect(win) -> tuple:
    """主窗口状态栏「注册标签」矩形（相对主窗口的逻辑坐标；窗口须已布局）。"""
    from PySide6.QtCore import QPoint

    label = win._reg._label
    pos = label.mapTo(win, QPoint(0, 0))
    return (pos.x(), pos.y() - 4, label.width(), label.height() + 8)


def _prepare_samples() -> None:
    """把真实数据集谱图复制到临时目录（批量 CSV 不写回软件仓库）。"""
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SAMPLES.mkdir(parents=True)
    STATE.mkdir(parents=True)
    for src_rel, name in FILES:
        src = REAL / src_rel
        if src.exists():
            shutil.copy2(src, SAMPLES / name)
        else:
            print("  !! 缺失:", src)
    print("samples:", sorted(p.name for p in SAMPLES.iterdir()))


def _demo_state():
    """生成一份**演示**注册状态（示例单位），仅用于截图。"""
    from rutana.gui import registration

    path = STATE / "PolyXRD_RutAna.json"
    registration.save_state(path, registration.generate_code(DEMO_UNIT))
    return path


def _grab_modal(app, out_path: Path, delay=500, censor_cb=None) -> None:
    """在 ``exec()`` 期间经定时器抓取当前模态窗口（注册相关弹窗用）。

    关闭方式：QMessageBox 点默认按钮（直接 ``close()`` 不会退出 exec 循环，
    会挂住进程），QDialog 直接 ``close()``。
    """
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox

    def _fire() -> None:
        widget = QApplication.activeModalWidget()
        if widget is None:
            print("  !! 未捕获到模态窗口:", out_path.name)
            return
        out_path.parent.mkdir(parents=True, exist_ok=True)
        widget.grab().save(str(out_path), "PNG")
        if censor_cb is not None:
            censor_cb(out_path, widget)
        if isinstance(widget, QMessageBox):
            btn = widget.defaultButton()
            if btn is None and widget.buttons():
                btn = widget.buttons()[0]
            if btn is not None:
                btn.click()
                return
        widget.close()

    QTimer.singleShot(delay, _fire)


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def main() -> int:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QLineEdit

    app = QApplication.instance() or QApplication([])

    from rutana import edition
    from rutana.gui import batch, registration, services
    from rutana.gui.busy import BusyDialog
    from rutana.gui.dialogs import AboutDialog
    from rutana.gui.khelp import KHelpDialog
    from rutana.gui.kwizard import KCalibWizardDialog
    from rutana.gui.main_window import MainWindow
    from rutana.i18n import set_language, tr
    from rutana.version import APP_NAME

    set_language("zh_CN")
    registration.set_language("zh")
    _prepare_samples()

    def path_of(name: str) -> str:
        return str(SAMPLES / name)

    # ------------------------------------------------------ A) 注册版（Setup）
    win = MainWindow()
    # 换成演示注册状态（真实状态文件不动）
    win._reg.state_path = _demo_state()
    win._reg.refresh()
    win.resize(1280, 800)

    # 1) 主界面初始（状态栏右端注册单位 → 打码）
    snap(win, OUT / "01_main_empty.png", app)
    reg_rect = _reg_rect(win)          # 窗口已布局后再取坐标
    censor(OUT / "01_main_empty.png", reg_rect, win.width())

    # 2) 导入谱图（3 个标准混合样 + 3 个待测样 + 1 份 pd 全谱）
    for _src_rel, name in FILES:
        p = path_of(name)
        win._patterns[p] = services.load_pattern(p)
        win.file_list.addItem(name)
    win.file_list.setCurrentRow(4)      # 当前谱 = 18percent24-29.txt
    _pump(app, 20)
    snap(win, OUT / "02_main_loaded.png", app)
    censor(OUT / "02_main_loaded.png", reg_rect, win.width())

    # 3) K 标定向导（v1.3.0 默认 V100 不对称窗；v1.1.0 起可选峰强口径）
    panel = win.tabs.a_panel
    win_a, win_r = panel.params()["win_a"], panel.params()["win_r"]
    specs = [{"file": path_of(f), "wr": w} for f, w in CALIB]
    wizard = KCalibWizardDialog(win, win_a=win_a, win_r=win_r)
    for spec in specs:
        wizard.add_row(spec["file"], spec["wr"])
    measured = services.measure_calib_rows(specs, win_a, win_r)
    wizard._apply_measure(measured)
    for row in measured:
        print(f"  calib {Path(row['file']).name}: w(R)={row['wr']}% "
              f"I(A)/I(R)={row['ratio_i']:.4f} ok={row['ok']}")
    fit = wizard.fit_result()
    print(f"  fit: K={fit['K']:.5f} intercept={fit['intercept']:.4f} "
          f"R2={fit['r2']:.6f} n={fit['n']}")
    _pump(app, 20)
    snap(wizard, OUT / "03_k_wizard.png", app)
    panel.set_k(fit["K"], fit["r2"])
    panel.set_quantity("area")
    wizard.close()

    # 4) A 法结果（待测样 + pd 全谱作平行样；参考真值 w(R)=18.00%）
    win.file_list.setCurrentRow(4)
    _pump(app, 10)
    win.tabs.setCurrentIndex(0)
    panel.chk_ref.setChecked(True)
    panel.sp_ref.setValue(TRUTH_WR)
    data = services.run_method_a(
        win._patterns[path_of(SAMPLE)], win_a, win_r, panel.current_k(),
        second_pat=win._patterns[path_of(PARALLEL)])
    win._apply_a_result(data)
    res, dup = data["result"], data["dup"]
    print(f"  A: w(A)={res.wa:.2f} w(R)={res.wr:.2f} K={res.K:.4f} "
          f"I(A)/I(R)={res.ia / res.ir:.4f} dup={dup['abs_diff']:.3f} "
          f"(限 {dup['limit']}) within={dup['within_limit']} "
          f"相对误差={(res.wr - TRUTH_WR) / TRUTH_WR * 100:+.2f}%")
    _pump(app, 20)
    snap(win, OUT / "04_a_result.png", app)
    censor(OUT / "04_a_result.png", reg_rect, win.width())

    # 5) K 值说明
    khelp = KHelpDialog(win)
    _pump(app, 15)
    snap(khelp, OUT / "05_k_help.png", app)
    khelp.close()

    # 6) B 法（v1.4.0 择优取向默认开启；v1.1.0 定量分列；v1.2.0 新画布样式）
    win.file_list.setCurrentRow(6)      # 18%实测谱(pd全谱).txt（20–120°）
    _pump(app, 12)
    win.tabs.setCurrentIndex(1)
    _pump(app, 10)
    bpanel = win.tabs.b_panel
    t0 = time.time()
    bdata = services.run_method_b(
        win._patterns[path_of(WIDE)], **bpanel.params())
    print(f"  B: {time.time() - t0:.1f}s Rwp={bdata['result'].rf.rwp:.2f} "
          f"Rp={bdata['result'].rf.rp:.2f} chi2={bdata['result'].rf.chi2:.3f} "
          f"w(A)={bdata['wa']:.2f} w(R)={bdata['wr']:.2f} po={bdata['po_r']}")
    win._apply_b_result(bdata)
    _pump(app, 20)
    snap(win, OUT / "06_b_result.png", app)
    censor(OUT / "06_b_result.png", reg_rect, win.width())

    # 7) 批量计算（A 法，对已导入谱图逐个计算 → 一个合并 CSV）
    win.tabs.setCurrentIndex(0)
    _pump(app, 10)
    items = list(win._patterns.items())
    t0 = time.time()
    rows = batch.run_method_a_batch(items, win_a=win_a, win_r=win_r,
                                    k=panel.current_k(),
                                    quantity=panel.current_quantity())
    saved = [batch.export_batch_csv(group, dest, method="a")
             for dest, group in batch.batch_save_plan(rows)]
    ok_n = sum(1 for r in rows if r.get("ok"))
    print(f"  batch A: {len(rows)} rows in {time.time() - t0:.1f}s "
          f"（成功 {ok_n}）")
    for row in rows:
        print(f"    {row['sample']}: w(R)={row['wr']:.2f} ok={row['ok']}")

    box_path = OUT / "07_batch_done.png"
    _grab_modal(app, box_path, delay=80)
    win._msg_box(tr("msg.batch_done", ok=ok_n, fail=len(rows) - ok_n,
                    paths=DISPLAY_CSV))
    print("  batch box:", box_path.exists())

    # 8) 计算进度窗
    busy = BusyDialog(win, title=tr("busy.title_refine"), cancellable=False)
    busy.start_timer()
    busy.set_message(tr("busy.refine", gen=12, rwp=9.29), 63)
    busy.set_iteration(12, 9.29)
    _pump(app, 25, 0.05)
    snap(busy, OUT / "08_busy.png", app)
    busy.finish()
    busy.close()

    # 9) 关于（注册版）
    about = AboutDialog(win)
    _pump(app, 15)
    snap(about, OUT / "09_about.png", app)
    about.close()
    win.close()

    # ------------------------------------------------------ B) 注册流程弹窗
    # 10) 「输入注册码」对话框：粘入真实注册码 → 截图 → 注册码打码
    temp_state = STATE / "pending.json"
    if temp_state.exists():
        temp_state.unlink()

    def _censor_code(path: Path, widget) -> None:
        edit = widget.findChild(QLineEdit)
        if edit is None:
            return
        pos = edit.mapTo(widget, edit.rect().topLeft())
        censor(path, (pos.x() - 2, pos.y() - 2, edit.width() + 4,
                      edit.height() + 4), widget.width())

    def _paste_code() -> None:
        widget = QApplication.activeModalWidget()
        if widget is not None:
            edit = widget.findChild(QLineEdit)
            if edit is not None:
                edit.setText(REAL_CODE)

    QTimer.singleShot(40, _paste_code)      # 弹窗出现后先把注册码粘进去
    reg_path = OUT / "10_reg_dialog.png"
    _grab_modal(app, reg_path, delay=800, censor_cb=_censor_code)
    registration.prompt_for_code(None, temp_state, APP_NAME)
    print("  reg dialog:", reg_path.exists())

    # 11) 未注册启动提示（临时状态文件未注册 → 每次启动弹）
    notice_path = OUT / "11_reg_notice.png"
    _grab_modal(app, notice_path, delay=600)
    registration.startup_prompt(None, temp_state, APP_NAME)
    print("  notice:", notice_path.exists())

    # ------------------------------------------------------ C) 内部评估版
    # 12) 状态栏「内部评估版本」（版次构建期定，此处 monkeypatch 复现）
    edition.IS_INTERNAL = True
    try:
        win2 = MainWindow()
        win2.resize(1280, 800)
        snap(win2, OUT / "12_main_internal.png", app)
        win2.close()
    finally:
        edition.IS_INTERNAL = False

    print("DONE rutana v1.5.0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
