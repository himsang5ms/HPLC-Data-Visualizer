from __future__ import annotations

import io
from pathlib import Path

from PIL import Image as PILImage, ImageEnhance
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "manual"
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT_ZH = OUTPUT_DIR / "HPLC-Data-Visualizer-v1.3.0-Quick-Guide-ZH.pdf"
OUTPUT_EN = OUTPUT_DIR / "HPLC-Data-Visualizer-v1.3.0-Quick-Guide-EN.pdf"

RED = colors.HexColor("#FF4B4B")
INK = colors.HexColor("#2F3440")
MUTED = colors.HexColor("#6B7280")
PALE = colors.HexColor("#F3F5F8")
LINE = colors.HexColor("#D9DEE8")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))
    pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
    pdfmetrics.registerFontFamily("SimHei", normal="SimHei", bold="SimHei")
    pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")


def image_flowable(path: Path, max_width: float, max_height: float, crop=None, contrast=1.0) -> Image:
    source = PILImage.open(path).convert("RGB")
    if crop is not None:
        source = source.crop(crop)
    if contrast != 1.0:
        source = ImageEnhance.Contrast(source).enhance(contrast)
    width, height = source.size
    scale = min(max_width / width, max_height / height)
    buffer = io.BytesIO()
    source.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    result = Image(buffer, width=width * scale, height=height * scale)
    result._buffer_ref = buffer
    return result


def page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Arial", 8)
    canvas.drawString(18 * mm, 9 * mm, "HPLC Data Visualizer v1.3.0")
    canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, str(doc.page))
    canvas.restoreState()


def build_styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover", parent=base["Title"], fontName="SimHei", fontSize=27,
            leading=36, textColor=INK, alignment=TA_CENTER, spaceAfter=10 * mm,
        ),
        "cover_title_en": ParagraphStyle(
            "cover_title_en", parent=base["Title"], fontName="Arial-Bold", fontSize=27,
            leading=36, textColor=INK, alignment=TA_CENTER, spaceAfter=10 * mm,
        ),
        "cover_en": ParagraphStyle(
            "cover_en", parent=base["Title"], fontName="Arial-Bold", fontSize=17,
            leading=23, textColor=MUTED, alignment=TA_CENTER, spaceAfter=8 * mm,
        ),
        "cover_bilingual": ParagraphStyle(
            "cover_bilingual", parent=base["BodyText"], fontName="SimHei", fontSize=16,
            leading=22, textColor=MUTED, alignment=TA_CENTER, spaceAfter=4 * mm,
        ),
        "h1_zh": ParagraphStyle(
            "h1_zh", parent=base["Heading1"], fontName="SimHei", fontSize=20,
            leading=27, textColor=INK, spaceAfter=5 * mm,
        ),
        "h2_zh": ParagraphStyle(
            "h2_zh", parent=base["Heading2"], fontName="SimHei", fontSize=12.5,
            leading=18, textColor=RED, spaceBefore=2.5 * mm, spaceAfter=2 * mm,
        ),
        "body_zh": ParagraphStyle(
            "body_zh", parent=base["BodyText"], fontName="SimHei", fontSize=9.2,
            leading=15, textColor=INK, spaceAfter=1.6 * mm,
        ),
        "small_zh": ParagraphStyle(
            "small_zh", parent=base["BodyText"], fontName="SimHei", fontSize=8,
            leading=12, textColor=MUTED,
        ),
        "h1_en": ParagraphStyle(
            "h1_en", parent=base["Heading1"], fontName="Arial-Bold", fontSize=20,
            leading=25, textColor=INK, spaceAfter=5 * mm,
        ),
        "h2_en": ParagraphStyle(
            "h2_en", parent=base["Heading2"], fontName="Arial-Bold", fontSize=12.5,
            leading=17, textColor=RED, spaceBefore=2.5 * mm, spaceAfter=2 * mm,
        ),
        "body_en": ParagraphStyle(
            "body_en", parent=base["BodyText"], fontName="Arial", fontSize=9.2,
            leading=14, textColor=INK, spaceAfter=1.6 * mm,
        ),
        "small_en": ParagraphStyle(
            "small_en", parent=base["BodyText"], fontName="Arial", fontSize=8,
            leading=11.5, textColor=MUTED,
        ),
        "callout_zh": ParagraphStyle(
            "callout_zh", parent=base["BodyText"], fontName="SimHei", fontSize=9.2,
            leading=15, textColor=INK, backColor=PALE, borderColor=LINE,
            borderWidth=0.7, borderPadding=7, spaceAfter=3 * mm,
        ),
        "callout_en": ParagraphStyle(
            "callout_en", parent=base["BodyText"], fontName="Arial", fontSize=9.2,
            leading=14, textColor=INK, backColor=PALE, borderColor=LINE,
            borderWidth=0.7, borderPadding=7, spaceAfter=3 * mm,
        ),
    }


def bullet(text: str, style) -> Paragraph:
    return Paragraph(f"- {text}", style)


def toolbar_table(styles, lang: str) -> Table:
    source = ASSET_DIR / "toolbar_en.png"
    boxes = [
        (633, 435, 660, 470),
        (659, 435, 684, 470),
        (683, 435, 709, 470),
        (708, 435, 737, 470),
        (738, 435, 769, 470),
    ]
    if lang == "zh":
        entries = [
            ("Zoom 框选缩放", "点击后拖出矩形，可精确放大指定区域。滚轮缩放不需要先点这个按钮。"),
            ("Pan 平移", "恢复按住图表拖动的模式。完成框选染色后，可点它回到普通拖动。"),
            ("Box Select 矩形框选", "点击后框住峰区域，程序会添加峰面积染色。"),
            ("Reset axes 恢复坐标轴", "回到侧边栏设定的时间范围。双击图表也可以恢复缩放。"),
            ("Download plot 下载", "直接下载当前图表的 SVG 文件。页面上方的大按钮也可导出 SVG。"),
        ]
        style = styles["body_zh"]
    else:
        entries = [
            ("Zoom", "Drag a rectangle for a precise zoom. Mouse-wheel zoom works without selecting this button."),
            ("Pan", "Return to normal click-and-drag panning after using a selection tool."),
            ("Box Select", "Drag across a peak region to add peak-area highlighting."),
            ("Reset axes", "Restore the range set in the sidebar. Double-clicking the chart also restores the zoom."),
            ("Download plot", "Download the current chart as SVG. The large button above the chart also exports SVG."),
        ]
        style = styles["body_en"]

    rows = []
    for box, (name, description) in zip(boxes, entries):
        icon = image_flowable(source, 9 * mm, 9 * mm, crop=box, contrast=1.25)
        rows.append([icon, Paragraph(f"<b>{name}</b><br/>{description}", style)])
    table = Table(rows, colWidths=[14 * mm, 151 * mm], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.5, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, LINE),
        ("BACKGROUND", (0, 0), (0, -1), PALE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def build_pdf(output: Path, lang: str) -> None:
    register_fonts()
    styles = build_styles()
    output.parent.mkdir(parents=True, exist_ok=True)
    is_zh = lang == "zh"
    doc = SimpleDocTemplate(
        str(output), pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=19 * mm,
        title=(
            "HPLC Data Visualizer v1.3.0 快速使用说明"
            if is_zh else
            "HPLC Data Visualizer v1.3.0 Quick Guide"
        ),
        author="HPLC Data Visualizer",
    )
    story = []

    # Cover
    if is_zh:
        story.extend([
            Spacer(1, 22 * mm),
            Paragraph("HPLC Data Visualizer", styles["cover_title_en"]),
            Paragraph("v1.3.0 快速使用说明", styles["cover"]),
            image_flowable(ASSET_DIR / "toolbar_en.png", 155 * mm, 78 * mm, crop=(300, 350, 780, 720)),
            Spacer(1, 9 * mm),
            Paragraph("Windows 便携版", styles["cover_bilingual"]),
            PageBreak(),
        ])
    else:
        story.extend([
            Spacer(1, 22 * mm),
            Paragraph("HPLC Data Visualizer", styles["cover_title_en"]),
            Paragraph("v1.3.0 Quick Guide", styles["cover_en"]),
            image_flowable(ASSET_DIR / "toolbar_en.png", 155 * mm, 78 * mm, crop=(300, 350, 780, 720)),
            Spacer(1, 9 * mm),
            Paragraph("Windows portable edition", styles["cover_en"]),
            PageBreak(),
        ])

    # Chinese: start and import
    if is_zh:
        story.extend([
        Paragraph("1. 启动与导入", styles["h1_zh"]),
        Paragraph("Windows 便携版", styles["h2_zh"]),
        bullet("完整解压 ZIP 后，双击 HPLC Data Visualizer.exe。无需安装 Python。", styles["body_zh"]),
        bullet("首次启动若出现 SmartScreen，点击“更多信息”，确认文件来源后选择“仍要运行”。", styles["body_zh"]),
        bullet("关闭最后一个浏览器页面后，程序约 10 秒内自动退出；也可使用侧边栏底部的“关闭本地程序”。", styles["body_zh"]),
        Paragraph("支持的数据格式", styles["h2_zh"]),
        bullet("CSV：第一列为时间，第二列为信号值；支持逗号、分号、制表符，以及 UTF-8、UTF-16、GB18030。", styles["body_zh"]),
        bullet("一个 CSV 可以顺序包含多组两列曲线。列名含 Intensity 时提示为 UV/DAD，含 Counts 时提示为质谱 TIC/EIC。", styles["body_zh"]),
        bullet("CTX：支持从第一行开始的 时间;信号值; 数据，也支持 [Chromatogram Data] 数据区。", styles["body_zh"]),
        Paragraph("多信号 CSV", styles["h2_zh"]),
        Paragraph("上方三个按钮只改变勾选状态。检查勾选结果后，点击 Confirm and plot 才会真正导入。检测器类型由列名推测，仅供选择时参考。", styles["callout_zh"]),
        image_flowable(ASSET_DIR / "signal_selection_en.png", 165 * mm, 80 * mm),
        PageBreak(),
        ])

    # Chinese: organize and width
        story.extend([
        Paragraph("2. 整理曲线与图幅宽度", styles["h1_zh"]),
        Paragraph("曲线顺序、名称和诊断", styles["h2_zh"]),
        bullet("按住样品卡片上下拖动，可直接调整曲线顺序。", styles["body_zh"]),
        bullet("展开“重命名或移除曲线”修改名称。新名称会用于图例、曲线标签和 SVG。", styles["body_zh"]),
        bullet("展开“导入诊断信息”检查列名、信号类型、点数、时间范围、跳过行、重复时间点、编码和分隔符。", styles["body_zh"]),
        image_flowable(ASSET_DIR / "figure_width_zh.png", 165 * mm, 86 * mm, crop=(0, 0, 808, 690)),
        Paragraph("Figure width / 图幅宽度", styles["h2_zh"]),
        bullet("按时间范围自动调整：根据当前 X 轴跨度生成宽度。时间范围较短时，导出图不会被拉得过长。", styles["body_zh"]),
        bullet("铺满页面：预览图跟随浏览器可用宽度，导出时采用当前显示尺寸。", styles["body_zh"]),
        bullet("自定义：手动输入像素宽度。程序会限制最小宽度，给曲线和样品名保留空间。", styles["body_zh"]),
        PageBreak(),
        ])

    # Chinese: interactions
        story.extend([
        Paragraph("3. 图表操作与导出", styles["h1_zh"]),
        Paragraph("先用最直接的操作", styles["h2_zh"]),
        Paragraph("鼠标滚轮缩放；按住图表拖动；点击曲线添加或取消保留时间；双击图表恢复初始缩放。以上操作不需要先点击灰色工具栏按钮。", styles["callout_zh"]),
        Paragraph("右上角灰色工具栏", styles["h2_zh"]),
        toolbar_table(styles, "zh"),
        Spacer(1, 3 * mm),
        Paragraph("染色步骤", styles["h2_zh"]),
        bullet("点击 Box Select，再框住需要高亮的峰区。", styles["body_zh"]),
        bullet("完成后点击 Pan，回到普通拖动模式。侧边栏可修改染色目标或清除全部染色。", styles["body_zh"]),
        Paragraph("导出", styles["h2_zh"]),
        bullet("页面上的“下载 SVG 矢量图”和工具栏下载按钮都会导出 SVG。", styles["body_zh"]),
        bullet("导出前建议确认时间范围、图幅宽度、样品名位置和字号。", styles["body_zh"]),
        ])

    # English: start and import
    else:
        story.extend([
        Paragraph("1. Start and import", styles["h1_en"]),
        Paragraph("Windows portable edition", styles["h2_en"]),
        bullet("Fully extract the ZIP, then double-click HPLC Data Visualizer.exe. Python is not required.", styles["body_en"]),
        bullet("If SmartScreen appears on first launch, choose More info, verify the file source, and select Run anyway.", styles["body_en"]),
        bullet("Closing the final browser page exits the app after about 10 seconds. You can also use Close local app in the sidebar.", styles["body_en"]),
        Paragraph("Supported data", styles["h2_en"]),
        bullet("CSV: time in the first column and signal in the second; comma, semicolon, and tab delimiters; UTF-8, UTF-16, and GB18030.", styles["body_en"]),
        bullet("A CSV may contain several sequential two-column signals. Intensity is shown as likely UV/DAD and Counts as likely MS TIC/EIC.", styles["body_en"]),
        bullet("CTX: time;signal; numeric data from the first line, or data inside a [Chromatogram Data] section.", styles["body_en"]),
        Paragraph("Multi-signal CSV", styles["h2_en"]),
        Paragraph("The three preset buttons only change the checkboxes. Review the selection and click Confirm and plot to import. Detector labels are inferred from column names and are provided as hints.", styles["callout_en"]),
        image_flowable(ASSET_DIR / "signal_selection_en.png", 165 * mm, 80 * mm),
        PageBreak(),
        ])

    # English: organize and width
        story.extend([
        Paragraph("2. Organize curves and set figure width", styles["h1_en"]),
        Paragraph("Order, names, and diagnostics", styles["h2_en"]),
        bullet("Drag sample cards up or down to reorder curves.", styles["body_en"]),
        bullet("Expand Rename or remove curves to edit display names used by legends, curve labels, and SVG exports.", styles["body_en"]),
        bullet("Expand Import diagnostics to review columns, signal type, point count, time range, skipped rows, duplicate times, encoding, and delimiter.", styles["body_en"]),
        image_flowable(ASSET_DIR / "figure_width_en.png", 165 * mm, 86 * mm, crop=(0, 0, 808, 690)),
        Paragraph("Figure width", styles["h2_en"]),
        bullet("Auto by time range sizes the output from the current X-axis span and keeps short ranges compact.", styles["body_en"]),
        bullet("Fill page width follows the available browser width and exports at the current rendered size.", styles["body_en"]),
        bullet("Custom uses an explicit pixel width. A minimum width is retained for the chart and sample labels.", styles["body_en"]),
        PageBreak(),
        ])

    # English: interactions
        story.extend([
        Paragraph("3. Chart interaction and export", styles["h1_en"]),
        Paragraph("Start with direct mouse controls", styles["h2_en"]),
        Paragraph("Use the mouse wheel to zoom, drag the chart to pan, click a curve to add or remove a retention-time marker, and double-click to restore the initial zoom. These actions do not require a toolbar button first.", styles["callout_en"]),
        Paragraph("Gray toolbar buttons", styles["h2_en"]),
        toolbar_table(styles, "en"),
        Spacer(1, 3 * mm),
        Paragraph("Peak highlighting", styles["h2_en"]),
        bullet("Select Box Select, then drag across the peak region to highlight it.", styles["body_en"]),
        bullet("Select Pan when finished to return to normal dragging. Highlight targets can be changed or cleared from the sidebar.", styles["body_en"]),
        Spacer(1, 3 * mm),
        Paragraph("Export", styles["h2_en"]),
        bullet("The large Download SVG figure button and the toolbar download button both export SVG.", styles["body_en"]),
        bullet("Before exporting, check the time range, figure width, sample-name position, and font size.", styles["body_en"]),
        ])

    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    print(output)


if __name__ == "__main__":
    build_pdf(OUTPUT_ZH, "zh")
    build_pdf(OUTPUT_EN, "en")
