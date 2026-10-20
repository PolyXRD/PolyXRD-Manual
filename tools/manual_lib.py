# -*- coding: utf-8 -*-
"""PolyXRD 家族手册生成共享库（reportlab，A4，微软雅黑）。

每个手册脚本定义 CONTENT = {title, subtitle, version, date, footer, chapters}
并调用 build(CONTENT, OUT_PDF, IMG_DIR, LOGO_PNG)。

章节结构（list）::
    ("h1", "第 1 章　xxx")
    ("h2", "1.1 xxx")
    ("h3", "xxx")
    ("p", "正文……支持 <b> <i> <code> <sub> <br/>")
    ("table", [[表头...], [行...], ...], [列宽比例...])   # 列宽比例可选
    ("tip", "提示框")
    ("warn", "注意框")
    ("shot", "文件名.png", "图 X-Y　说明")
    ("pagebreak",)
    ("toc", ["第 1 章　xxx", ...])
    ("contact",)   # 末尾联系与许可块（自动生成）
"""
import os
from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Image, Table, TableStyle, PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("YaHei", "C:/Windows/Fonts/msyh.ttc"))
pdfmetrics.registerFont(TTFont("YaHeiBold", "C:/Windows/Fonts/msyhbd.ttc"))
pdfmetrics.registerFont(TTFont("SimHei", "C:/Windows/Fonts/simhei.ttf"))

_ACCENT = colors.HexColor("#1a4f8b")


def _styles():
    base = ParagraphStyle(
        "base", fontName="YaHei", fontSize=10.5, leading=16,
        textColor=colors.HexColor("#222222"), alignment=TA_LEFT, spaceAfter=6,
    )
    return {
        "title": ParagraphStyle("title", parent=base, fontName="YaHeiBold", fontSize=26,
                                leading=34, alignment=TA_CENTER, spaceAfter=14,
                                textColor=_ACCENT),
        "subtitle": ParagraphStyle("subtitle", parent=base, fontSize=13, leading=20,
                                   alignment=TA_CENTER, textColor=colors.HexColor("#555555"),
                                   spaceAfter=24),
        "h1": ParagraphStyle("h1", parent=base, fontName="YaHeiBold", fontSize=18,
                             leading=26, textColor=_ACCENT, spaceBefore=22, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base, fontName="YaHeiBold", fontSize=14,
                             leading=22, textColor=colors.HexColor("#2a6db5"),
                             spaceBefore=16, spaceAfter=8),
        "h3": ParagraphStyle("h3", parent=base, fontName="YaHeiBold", fontSize=11.5,
                             leading=18, textColor=colors.HexColor("#333333"),
                             spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("body", parent=base, alignment=TA_LEFT, spaceAfter=6),
        "caption": ParagraphStyle("caption", parent=base, fontSize=9, leading=13,
                                  textColor=colors.HexColor("#666666"),
                                  alignment=TA_CENTER, spaceAfter=14),
        "tip": ParagraphStyle("tip", parent=base, fontSize=9.5, leading=14,
                              textColor=colors.HexColor("#1a4f8b"),
                              leftIndent=8, rightIndent=8, spaceBefore=6, spaceAfter=8),
        "warn": ParagraphStyle("warn", parent=base, fontSize=9.5, leading=14,
                               textColor=colors.HexColor("#a04000"),
                               leftIndent=8, rightIndent=8, spaceBefore=6, spaceAfter=8),
        "toc": ParagraphStyle("toc", parent=base, fontSize=11, leading=19,
                              leftIndent=12, spaceAfter=2),
        "toc1": ParagraphStyle("toc1", parent=base, fontName="YaHeiBold", fontSize=12,
                               leading=21, spaceAfter=2),
        "cellh": ParagraphStyle("cellh", parent=base, fontName="YaHeiBold", fontSize=9,
                                leading=13, textColor=colors.white, spaceAfter=0),
        "cell": ParagraphStyle("cell", parent=base, fontSize=9, leading=13, spaceAfter=0),
    }


S = _styles()


def P(text, style="body"):
    return Paragraph(text.replace("\n", "<br/>"), S[style])


def _callout(text, bg, line, style):
    return Table(
        [[Paragraph(text, S[style])]],
        colWidths=[16 * cm],
        style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, -1), 3, colors.HexColor(line)),
        ]),
    )


def make_table(data, ratios=None):
    total = 16 * cm
    if ratios:
        s = sum(ratios)
        widths = [total * r / s for r in ratios]
    else:
        widths = [total / len(data[0])] * len(data[0])
    # 单元格包装为 Paragraph：支持 <b> 标签 + 自动换行
    wrapped = []
    for r, row in enumerate(data):
        style = "cellh" if r == 0 else "cell"
        wrapped.append([Paragraph(str(c), S[style]) for c in row])
    t = Table(wrapped, colWidths=widths, repeatRows=1)
    # 表格整体不拆页: 拆到下一页只剩两三行会让整页几乎空白(实测 v3.2.0
    # 手册第 10 页只剩「谱图交互」表的两行)。本套手册最长的表也就 6 行,
    # 一页放得下, 整表挪到下一页反而好看。
    t.splitByRow = 0
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, 0), _ACCENT),
    ]))
    return t


def _shot(story, img_dir, filename, caption, max_width=16 * cm):
    path = os.path.join(img_dir, filename)
    if not os.path.exists(path):
        story.append(P(f"[截图缺失: {filename}]", "caption"))
        return
    with PILImage.open(path) as im:
        w, h = im.size
    aspect = h / w
    img_w, img_h = max_width, max_width * aspect
    max_h = 20 * cm
    if img_h > max_h:
        img_h = max_h
        img_w = img_h / aspect
    story.append(Spacer(1, 0.2 * cm))
    story.append(Image(path, width=img_w, height=img_h))
    story.append(P(f"图 {caption}", "caption"))


def _contact_block(app_name):
    return (
        "<b>联系与许可</b><br/>"
        f"{app_name} 采用学术 / 商业双许可：学术研究与教学可免费使用"
        "（保留版权与许可声明）；商业用途需在使用前联系版权持有人取得书面商业授权。"
        "完整条款见随附 LICENSE（英文）/ LICENSE-CN（中文）。<br/>"
        "版权所有 (c) 2026 PolyXRD Team　·　联系邮箱：sshztx@outlook.com"
    )


def build(content, out_pdf, img_dir, logo=None):
    """按 CONTENT 结构生成 PDF。"""
    story = []
    fig_no = 0

    # ---- 封面 ----
    story.append(Spacer(1, 2.2 * cm))
    if logo and os.path.exists(logo):
        story.append(Image(logo, width=3.6 * cm, height=3.6 * cm))
        story.append(Spacer(1, 0.6 * cm))
    story.append(P(content["title"], "title"))
    story.append(P(content["subtitle"], "subtitle"))
    story.append(P(f"版本 v{content['version']}　|　{content['date']}", "subtitle"))
    story.append(Spacer(1, 1.2 * cm))
    story.append(_callout(content.get("cover_note", "本手册基于当前最新版本撰写，截图取自实际运行界面。"),
                          "#eef5fd", "#2a6db5", "tip"))
    story.append(PageBreak())

    # ---- 目录 ----
    story.append(P("目录", "h1"))
    for item in content["toc"]:
        story.append(P(item, "toc1"))
    story.append(PageBreak())

    # ---- 正文 ----
    for item in content["chapters"]:
        kind = item[0]
        if kind == "h1":
            story.append(P(item[1], "h1"))
        elif kind == "h2":
            story.append(P(item[1], "h2"))
        elif kind == "h3":
            story.append(P(item[1], "h3"))
        elif kind == "p":
            story.append(P(item[1], "body"))
        elif kind == "table":
            story.append(make_table(item[1], item[2] if len(item) > 2 else None))
            story.append(Spacer(1, 0.3 * cm))
        elif kind == "tip":
            story.append(_callout(item[1], "#eef5fd", "#2a6db5", "tip"))
        elif kind == "warn":
            story.append(_callout(item[1], "#fdf3ee", "#d35400", "warn"))
        elif kind == "shot":
            fig_no += 1
            _shot(story, img_dir, item[1], item[2])
        elif kind == "pagebreak":
            story.append(PageBreak())
        elif kind == "contact":
            story.append(Spacer(1, 0.8 * cm))
            story.append(P(_contact_block(content["app_name"]), "body"))
        elif kind == "end":
            story.append(Spacer(1, 0.8 * cm))
            story.append(P(f"— 手册结束 · {content['app_name']} v{content['version']} —", "caption"))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("YaHei", 9)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(doc.page))
        canvas.drawString(2 * cm, 1.2 * cm, content["footer"])
        canvas.restoreState()

    doc = BaseDocTemplate(
        out_pdf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin + 1 * cm,
                  doc.width, doc.height - 1.2 * cm, id="normal")
    doc.addPageTemplates([PageTemplate(id="all", frames=frame, onPage=footer)])
    doc.build(story)
    print("Generated:", out_pdf)
