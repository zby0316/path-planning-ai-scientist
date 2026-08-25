"""将第9步Markdown源稿转换为符合论文规则的DOCX（第10步）。"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from PIL import Image
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "docs" / "reports" / "路径规划虚拟仿真闭环AI科学家系统技术报告_正文源稿.md"
OUTPUT = REPO_ROOT / "assets" / "reports" / "final" / "路径规划虚拟仿真闭环AI科学家系统技术报告_比赛项目版.docx"

# 学校格式覆盖 narrative_proposal 预设。
A4_WIDTH_CM = 21.0
A4_HEIGHT_CM = 29.7
TOP_CM = 2.6
BOTTOM_CM = 2.6
LEFT_CM = 2.5
RIGHT_CM = 2.0
GUTTER_CM = 1.0
HEADER_CM = 1.5
FOOTER_CM = 1.5
CONTENT_CM = A4_WIDTH_CM - LEFT_CM - RIGHT_CM - GUTTER_CM
TABLE_TOTAL_DXA = 8667
TABLE_INDENT_DXA = 120

FONT_CN_BODY = "宋体"
FONT_CN_HEAD = "黑体"
FONT_LATIN = "Times New Roman"
FONT_MATH = "Cambria Math"


FORMULA_TEXT = {
    "2-1": "Sₖ₊₁ = Aₖ(Sₖ),    Aₖ: 𝒮 → 𝒮",
    "2-2": "C_env = 0.45rₒ + 0.25(1 − c) + 0.20t + 0.10d",
    "3-1": "J(P) = ∑ᵢ₌₀ᵐ⁻¹ c(vᵢ, vᵢ₊₁) + λₜN_turn + λᵣR(P)",
    "3-2": "f(n) = g(n) + h(n),    h(n) = |xₙ − x_g| + |yₙ − y_g|",
    "3-3": "pᵏᵢⱼ = τᵢⱼᵅηᵢⱼᵝ / ∑ₗ∈𝒩ᵏᵢ τᵢₗᵅηᵢₗᵝ",
    "3-4": "τᵢⱼ ← (1 − ρ)τᵢⱼ + ∑ₖ Δτᵏᵢⱼ",
    "3-5": "vᵗ⁺¹ᵢ = ωvᵗᵢ + c₁r₁(pᵢ − xᵗᵢ) + c₂r₂(g − xᵗᵢ);    xᵗ⁺¹ᵢ = xᵗᵢ + vᵗ⁺¹ᵢ",
    "3-6": "P(accept) = exp(−ΔE / T)",
    "3-7": "Scoreᵢ = max(0, min(1, ∑ⱼ₌₁⁹ wⱼzᵢⱼ − qᵢ))",
    "4-1": "sim(q, dᵢ) = qᵀdᵢ / (‖q‖₂ ‖dᵢ‖₂)",
    "4-2": "H_support = r_b − r_s",
    "4-3": "C_reflection ≥ 0.7    或达到最大迭代次数",
    "5-1": "H = −∑ᵢ:pᵢ>0 pᵢ log₂pᵢ",
    "5-2": "Safety(P) = (1/(m+1)) ∑ᵢ₌₀ᵐ [minₒ∈O ‖vᵢ−o‖₂ / D_map]",
    "6-1": "SRₐ = (Nᵛᵃˡⁱᵈₐ / Nᵗᵒᵗᵃˡₐ) × 100%",
    "6-2": "Stabilityₐ = max(0, 1 − σ(tₐ)/(μ(tₐ)+ε))",
    "6-3": "χ²_F = [12N/(k(k+1))] [∑ⱼ₌₁ᵏ R̄²ⱼ − k(k+1)²/4]",
}


def set_run_font(run, cn: str, latin: str, size_pt: float, *, bold=None, italic=None):
    run.font.name = latin
    run.font.size = Pt(size_pt)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)
    rfonts.set(qn("w:eastAsia"), cn)
    rfonts.set(qn("w:cs"), latin)


def set_style_font(style, cn: str, latin: str, size_pt: float, bold: bool = False):
    style.font.name = latin
    style.font.size = Pt(size_pt)
    style.font.bold = bold
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)
    rfonts.set(qn("w:eastAsia"), cn)
    rfonts.set(qn("w:cs"), latin)
    color = rpr.find(qn("w:color"))
    if color is None:
        color = OxmlElement("w:color")
        rpr.append(color)
    color.set(qn("w:val"), "000000")
    # Word's built-in heading styles can retain a theme color even when w:val is
    # black; remove theme attributes so the school-required black is authoritative.
    for attr in ("themeColor", "themeTint", "themeShade"):
        color.attrib.pop(qn(f"w:{attr}"), None)


def set_keep_with_next(paragraph, enabled: bool = True):
    ppr = paragraph._p.get_or_add_pPr()
    node = ppr.find(qn("w:keepNext"))
    if enabled and node is None:
        ppr.append(OxmlElement("w:keepNext"))
    elif not enabled and node is not None:
        ppr.remove(node)


def set_keep_together(paragraph, enabled: bool = True):
    ppr = paragraph._p.get_or_add_pPr()
    node = ppr.find(qn("w:keepLines"))
    if enabled and node is None:
        ppr.append(OxmlElement("w:keepLines"))


def set_page_break_before(paragraph, enabled: bool = True):
    ppr = paragraph._p.get_or_add_pPr()
    node = ppr.find(qn("w:pageBreakBefore"))
    if enabled and node is None:
        ppr.append(OxmlElement("w:pageBreakBefore"))


def set_paragraph_bottom_border(paragraph, color="000000", size="6"):
    ppr = paragraph._p.get_or_add_pPr()
    pbdr = ppr.find(qn("w:pBdr"))
    if pbdr is None:
        pbdr = OxmlElement("w:pBdr")
        ppr.append(pbdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)


def configure_section_geometry(section):
    section.page_width = Cm(A4_WIDTH_CM)
    section.page_height = Cm(A4_HEIGHT_CM)
    section.top_margin = Cm(TOP_CM)
    section.bottom_margin = Cm(BOTTOM_CM)
    section.left_margin = Cm(LEFT_CM)
    section.right_margin = Cm(RIGHT_CM)
    try:
        section.gutter = Cm(GUTTER_CM)
    except AttributeError:
        pgmar = section._sectPr.get_or_add_pgMar()
        pgmar.set(qn("w:gutter"), str(round(Cm(GUTTER_CM).twips)))
    section.header_distance = Cm(HEADER_CM)
    section.footer_distance = Cm(FOOTER_CM)


def set_page_number_format(section, fmt: str, start: int = 1):
    sectpr = section._sectPr
    old = sectpr.find(qn("w:pgNumType"))
    if old is not None:
        sectpr.remove(old)
    node = OxmlElement("w:pgNumType")
    node.set(qn("w:fmt"), fmt)
    node.set(qn("w:start"), str(start))
    sectpr.append(node)


def add_field(paragraph, instruction: str, placeholder: str = "1"):
    run = paragraph.add_run()
    set_run_font(run, FONT_CN_BODY, FONT_LATIN, 9)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    return run


def clear_paragraph(paragraph):
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)


def configure_front_header_footer(section):
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    hp = section.header.paragraphs[0]
    clear_paragraph(hp)
    fp = section.footer.paragraphs[0]
    clear_paragraph(fp)
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(fp, " PAGE ", "i")
    set_page_number_format(section, "lowerRoman", 1)


def configure_body_header_footer(section):
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    hp = section.header.paragraphs[0]
    clear_paragraph(hp)
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hp.paragraph_format.space_after = Pt(0)
    run = hp.add_run("路径规划虚拟仿真闭环 AI 科学家系统技术报告")
    set_run_font(run, FONT_CN_HEAD, FONT_LATIN, 9, bold=True)
    set_paragraph_bottom_border(hp)
    fp = section.footer.paragraphs[0]
    clear_paragraph(fp)
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = fp.add_run("第 ")
    set_run_font(r1, FONT_CN_BODY, FONT_LATIN, 9)
    add_field(fp, " PAGE ", "1")
    r2 = fp.add_run(" 页")
    set_run_font(r2, FONT_CN_BODY, FONT_LATIN, 9)
    set_page_number_format(section, "decimal", 1)


def configure_styles(doc: Document):
    styles = doc.styles
    normal = styles["Normal"]
    set_style_font(normal, FONT_CN_BODY, FONT_LATIN, 12)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.first_line_indent = Pt(24)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.widow_control = True

    h1 = styles["Heading 1"]
    set_style_font(h1, FONT_CN_HEAD, FONT_LATIN, 18, True)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1.paragraph_format.first_line_indent = Pt(0)
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(18)
    h1.paragraph_format.line_spacing = 1.0
    h1.paragraph_format.keep_with_next = True

    h2 = styles["Heading 2"]
    set_style_font(h2, FONT_CN_HEAD, FONT_LATIN, 15, True)
    h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h2.paragraph_format.first_line_indent = Pt(0)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.line_spacing = 1.0
    h2.paragraph_format.keep_with_next = True

    h3 = styles["Heading 3"]
    set_style_font(h3, FONT_CN_HEAD, FONT_LATIN, 14, True)
    h3.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h3.paragraph_format.first_line_indent = Pt(0)
    h3.paragraph_format.left_indent = Pt(24)
    h3.paragraph_format.space_before = Pt(9)
    h3.paragraph_format.space_after = Pt(4)
    h3.paragraph_format.line_spacing = 1.0
    h3.paragraph_format.keep_with_next = True

    for name, cn, latin, size, bold in [
        ("摘要标题", FONT_CN_HEAD, FONT_LATIN, 18, True),
        ("目录标题", FONT_CN_HEAD, FONT_LATIN, 18, True),
        ("图题", FONT_CN_BODY, FONT_LATIN, 10.5, False),
        ("表题", FONT_CN_BODY, FONT_LATIN, 10.5, False),
        ("参考文献条目", FONT_CN_BODY, FONT_LATIN, 10.5, False),
        ("公式", FONT_CN_BODY, FONT_MATH, 10.5, False),
    ]:
        if name not in styles:
            style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        else:
            style = styles[name]
        set_style_font(style, cn, latin, size, bold)

    summary = styles["摘要标题"]
    summary.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    summary.paragraph_format.first_line_indent = Pt(0)
    summary.paragraph_format.space_after = Pt(18)
    toc_title = styles["目录标题"]
    toc_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc_title.paragraph_format.first_line_indent = Pt(0)
    toc_title.paragraph_format.space_after = Pt(18)
    for cap_name in ("图题", "表题"):
        cap = styles[cap_name]
        cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.first_line_indent = Pt(0)
        cap.paragraph_format.line_spacing = 1.0
        cap.paragraph_format.space_before = Pt(3)
        cap.paragraph_format.space_after = Pt(6)
        cap.paragraph_format.keep_with_next = cap_name == "表题"
    ref = styles["参考文献条目"]
    ref.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ref.paragraph_format.left_indent = Pt(24)
    ref.paragraph_format.first_line_indent = Pt(-24)
    ref.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    ref.paragraph_format.space_after = Pt(0)
    eq = styles["公式"]
    eq.paragraph_format.first_line_indent = Pt(0)
    eq.paragraph_format.space_before = Pt(3)
    eq.paragraph_format.space_after = Pt(3)

    # TOC field materialization uses built-in TOC 1-3 styles.
    for idx, size, left in [(1, 15, 0), (2, 14, 24), (3, 12, 48)]:
        name = f"TOC {idx}"
        st = styles[name] if name in styles else styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        set_style_font(st, FONT_CN_HEAD if idx < 3 else FONT_CN_BODY, FONT_LATIN, size, idx < 3)
        st.paragraph_format.left_indent = Pt(left)
        st.paragraph_format.first_line_indent = Pt(0)
        st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        st.paragraph_format.space_before = Pt(0)
        st.paragraph_format.space_after = Pt(0)


def add_update_fields_setting(doc: Document):
    settings = doc.settings._element
    node = settings.find(qn("w:updateFields"))
    if node is None:
        node = OxmlElement("w:updateFields")
        settings.append(node)
    node.set(qn("w:val"), "true")


def add_toc(doc: Document):
    doc.add_page_break()
    title = doc.add_paragraph("目　　录", style="目录标题")
    set_keep_with_next(title, True)
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(0)
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    begin.set(qn("w:dirty"), "true")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "目录将在打开文档时自动更新"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, sep, text, end])
    set_run_font(run, FONT_CN_BODY, FONT_LATIN, 12)


def normalize_inline_math(value: str) -> str:
    replacements = {
        r"\subseteq": "⊆", r"\in": "∈", r"\ge": "≥", r"\le": "≤",
        r"\rightarrow": "→", r"\ldots": "…", r"\times": "×",
        r"\mathcal{S}": "𝒮", r"\mathsf{T}": "ᵀ", r"\varepsilon": "ε",
        r"\lambda": "λ", r"\sigma": "σ", r"\mu": "μ", r"\rho": "ρ",
        r"\alpha": "α", r"\beta": "β", r"\tau": "τ", r"\eta": "η", r"\bar": "",
        r"\Delta": "Δ", r"\sum": "∑", r"\exp": "exp", r"\min": "min",
        r"\max": "max", r"\text": "",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    value = value.replace("{", "").replace("}", "")
    value = value.replace("\\", "")
    return value


INLINE_TOKEN = re.compile(
    r"(\*\*.*?\*\*|`[^`]+`|\\\(.*?\\\)|\[[0-9]+(?:\s*[-—,，]\s*[0-9]+)*\])"
)


def normalize_plain_fragment(value: str) -> str:
    """Clean leaked inline-math markup without damaging API paths such as {run_id}."""
    if "\\" in value:
        value = normalize_inline_math(value)
    value = re.sub(r"([A-Za-z])_\{([^{}]+)\}", r"\1_\2", value)
    value = value.replace("(eta_ij)", "(η_ij)")
    value = value.replace("(alpha)", "(α)")
    value = value.replace("(Delta E>0)", "(ΔE>0)")
    value = value.replace("(t_ij)", "(τ_ij)")
    return value


def add_inline_runs(paragraph, text: str, *, ref_mode: bool = False):
    pos = 0
    for match in INLINE_TOKEN.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(normalize_plain_fragment(text[pos:match.start()]))
            set_run_font(run, FONT_CN_BODY, FONT_LATIN, 12)
        token = match.group(0)
        if token.startswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, FONT_CN_HEAD, FONT_LATIN, 12, bold=True)
        elif token.startswith("`"):
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, FONT_CN_BODY, FONT_LATIN, 11)
        elif token.startswith(r"\("):
            run = paragraph.add_run(normalize_inline_math(token[2:-2]))
            set_run_font(run, FONT_CN_BODY, FONT_MATH, 12)
        else:
            run = paragraph.add_run(token)
            numeric_parts = [int(x) for x in re.findall(r"\d+", token)]
            is_citation = (not ref_mode) and bool(numeric_parts) and min(numeric_parts) >= 1
            set_run_font(
                run,
                FONT_CN_BODY,
                FONT_LATIN if is_citation or ref_mode else FONT_MATH,
                9 if is_citation else 12,
            )
            if is_citation:
                run.font.superscript = True
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(normalize_plain_fragment(text[pos:]))
        set_run_font(run, FONT_CN_BODY, FONT_LATIN, 12)


def add_body_paragraph(doc: Document, text: str):
    p = doc.add_paragraph(style="Normal")
    add_inline_runs(p, text)
    return p


def add_reference_paragraph(doc: Document, text: str):
    p = doc.add_paragraph(style="参考文献条目")
    # 参考文献条目开头的 [n] 不使用上标。
    add_inline_runs(p, text, ref_mode=True)
    for run in p.runs:
        set_run_font(run, FONT_CN_BODY, FONT_LATIN, 10.5, bold=run.bold)
        run.font.superscript = False
    return p


def add_image(doc: Document, rel_path: str):
    path = (SOURCE.parent / rel_path).resolve()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    set_keep_with_next(p, True)
    set_keep_together(p, True)
    with Image.open(path) as im:
        width_px, height_px = im.size
    width_overrides = {
        "图1-1_路径规划算法自适应选型问题示意图.png": 13.2,
        "图1-2_路径规划与AI_Scientist技术演进图.png": 13.2,
        "图3-2_五类路径规划算法处理流程对比图.png": 12.2,
        "图4-4_假设实验反思人在回路闭环图.png": 10.8,
        "图6-4_综合指标与失败分布.png": 12.5,
    }
    width_cm = width_overrides.get(path.name, 14.5)
    height_cm = width_cm * height_px / width_px
    if height_cm > 19.5:
        height_cm = 19.5
        width_cm = height_cm * width_px / height_px
    run = p.add_run()
    inline = run.add_picture(str(path), width=Cm(width_cm), height=Cm(height_cm))
    # Alt text for accessibility and auditability.
    docpr = inline._inline.docPr
    docpr.set("descr", path.stem)
    return p


def add_caption(doc: Document, text: str, kind: str):
    p = doc.add_paragraph(text, style="图题" if kind == "图" else "表题")
    set_keep_together(p, True)
    if kind == "表":
        set_keep_with_next(p, True)
    return p


def weighted_len(text: str) -> int:
    return sum(2 if "\u3400" <= ch <= "\u9fff" else 1 for ch in text)


def distribute_widths(rows: list[list[str]], total: int) -> list[int]:
    cols = len(rows[0])
    scores = []
    for c in range(cols):
        max_len = max(weighted_len(row[c]) if c < len(row) else 0 for row in rows)
        scores.append(max(6, min(max_len, 32)))
    min_width = 720
    remaining = total - min_width * cols
    if remaining <= 0:
        return [total // cols] * cols
    score_sum = sum(scores)
    widths = [min_width + int(remaining * s / score_sum) for s in scores]
    widths[-1] += total - sum(widths)
    return widths


def set_cell_margins(cell, top=80, start=100, bottom=80, end=100):
    tc = cell._tc
    tcpr = tc.get_or_add_tcPr()
    old = tcpr.find(qn("w:tcMar"))
    if old is not None:
        tcpr.remove(old)
    tcmar = OxmlElement("w:tcMar")
    for name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = OxmlElement(f"w:{name}")
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        tcmar.append(node)
    tcpr.append(tcmar)


def set_table_geometry(table, widths: list[int]):
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl = table._tbl
    tblpr = tbl.tblPr
    layout = tblpr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tblpr.append(layout)
    layout.set(qn("w:type"), "fixed")
    tblw = tblpr.find(qn("w:tblW"))
    if tblw is None:
        tblw = OxmlElement("w:tblW")
        tblpr.append(tblw)
    tblw.set(qn("w:w"), str(sum(widths)))
    tblw.set(qn("w:type"), "dxa")
    tblind = tblpr.find(qn("w:tblInd"))
    if tblind is None:
        tblind = OxmlElement("w:tblInd")
        tblpr.append(tblind)
    tblind.set(qn("w:w"), str(TABLE_INDENT_DXA))
    tblind.set(qn("w:type"), "dxa")

    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)

    for row in table.rows:
        trpr = row._tr.get_or_add_trPr()
        if trpr.find(qn("w:cantSplit")) is None:
            trpr.append(OxmlElement("w:cantSplit"))
        for idx, cell in enumerate(row.cells):
            width = widths[idx]
            cell.width = width
            tcpr = cell._tc.get_or_add_tcPr()
            tcw = tcpr.find(qn("w:tcW"))
            if tcw is None:
                tcw = OxmlElement("w:tcW")
                tcpr.append(tcw)
            tcw.set(qn("w:w"), str(width))
            tcw.set(qn("w:type"), "dxa")
            set_cell_margins(cell)


def shade_cell(cell, fill: str):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = tcpr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcpr.append(shd)
    shd.set(qn("w:fill"), fill)


def add_markdown_table(doc: Document, rows: list[list[str]]):
    widths = distribute_widths(rows, TABLE_TOTAL_DXA)
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    set_table_geometry(table, widths)
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx]
        if r_idx == 0:
            trpr = row._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:tblHeader"))
        for c_idx, value in enumerate(row_data):
            value = value.replace("`", "")
            cell = row.cells[c_idx]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            if r_idx == 0:
                set_keep_with_next(p, True)
            short_value = weighted_len(value) <= 18 or bool(re.fullmatch(r"[\d.%—×*+/\- ]+", value))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (r_idx == 0 or short_value) else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(value)
            set_run_font(run, FONT_CN_BODY, FONT_LATIN, 9, bold=(r_idx == 0))
            if r_idx == 0:
                shade_cell(cell, "F2F2F2")
    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(0)
    after.paragraph_format.first_line_indent = Pt(0)
    return table


def add_math_object(paragraph, text: str):
    omath = OxmlElement("m:oMath")
    mr = OxmlElement("m:r")
    mrpr = OxmlElement("m:rPr")
    sty = OxmlElement("m:sty")
    sty.set(qn("m:val"), "p")
    mrpr.append(sty)
    mr.append(mrpr)
    wt = OxmlElement("m:t")
    wt.text = text
    mr.append(wt)
    omath.append(mr)
    paragraph._p.append(omath)


def add_formula(doc: Document, tag: str):
    p = doc.add_paragraph(style="公式")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.tab_stops.add_tab_stop(Cm(CONTENT_CM / 2), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(CONTENT_CM), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run("\t")
    add_math_object(p, FORMULA_TEXT[tag])
    p.add_run("\t")
    num = p.add_run(f"（{tag}）")
    set_run_font(num, FONT_CN_BODY, FONT_LATIN, 10.5)
    set_keep_together(p, True)
    return p


def parse_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(line: str) -> bool:
    cells = parse_table_row(line)
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def build_document():
    doc = Document()
    doc.core_properties.title = "路径规划虚拟仿真闭环AI科学家系统技术报告"
    doc.core_properties.subject = "比赛项目技术报告"
    doc.core_properties.author = ""
    doc.core_properties.last_modified_by = ""
    configure_styles(doc)
    configure_section_geometry(doc.sections[0])
    configure_front_header_footer(doc.sections[0])
    add_update_fields_setting(doc)

    source_text = SOURCE.read_text(encoding="utf-8")
    # 修复Markdown中由转义写入遗留的两个退格控制字符，并移除其余XML非法控制符。
    source_text = source_text.replace("\x08eta", r"\beta").replace("\x08ar", r"\bar")
    source_text = source_text.replace("\tau_", r"\tau_")
    source_text = re.sub(r"[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]", "", source_text)
    lines = source_text.splitlines()
    i = 0
    body_section_created = False
    in_references = False
    formula_buffer: list[str] = []

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line:
            i += 1
            continue
        if line.startswith("<!--"):
            if "DOCX_STEP" in line:
                add_toc(doc)
            i += 1
            continue

        if line == "$$":
            formula_buffer = []
            i += 1
            while i < len(lines) and lines[i].strip() != "$$":
                formula_buffer.append(lines[i])
                i += 1
            formula_src = "\n".join(formula_buffer)
            tag_match = re.search(r"\\tag\{(\d+-\d+)\}", formula_src)
            if not tag_match:
                raise ValueError(f"公式缺少编号: {formula_src[:80]}")
            add_formula(doc, tag_match.group(1))
            i += 1
            continue

        image_match = re.fullmatch(r"!\[[^\]]+\]\(([^)]+\.png)\)", line)
        if image_match:
            add_image(doc, image_match.group(1))
            i += 1
            continue

        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            parsed = [parse_table_row(x) for x in table_lines if not is_separator_row(x)]
            if parsed:
                col_count = len(parsed[0])
                parsed = [(row + [""] * col_count)[:col_count] for row in parsed]
                add_markdown_table(doc, parsed)
            continue

        if line.startswith("# "):
            text = line[2:].strip()
            if text == "摘　　要":
                p = doc.add_paragraph("摘　　要", style="摘要标题")
                set_keep_with_next(p, True)
            elif re.match(r"第\d+章", text):
                if not body_section_created:
                    sec = doc.add_section(WD_SECTION.NEW_PAGE)
                    configure_section_geometry(sec)
                    configure_body_header_footer(sec)
                    body_section_created = True
                else:
                    # 后续章标题由段前分页控制。
                    pass
                p = doc.add_paragraph(text, style="Heading 1")
                if body_section_created:
                    set_page_break_before(p, not re.match(r"第1章", text))
                set_keep_with_next(p, True)
            elif text == "参 考 文 献":
                in_references = True
                p = doc.add_paragraph(text, style="Heading 1")
                set_page_break_before(p, True)
                set_keep_with_next(p, True)
            else:
                p = doc.add_paragraph(text, style="Heading 1")
                set_page_break_before(p, True)
                set_keep_with_next(p, True)
            i += 1
            continue

        if line.startswith("### "):
            p = doc.add_paragraph(line[4:].strip(), style="Heading 3")
            set_keep_with_next(p, True)
            i += 1
            continue
        if line.startswith("## "):
            p = doc.add_paragraph(line[3:].strip(), style="Heading 2")
            set_keep_with_next(p, True)
            i += 1
            continue

        cap_match = re.fullmatch(r"\*\*([图表])(\d+-\d+)[　 ]*(.*?)\*\*", line)
        if cap_match:
            kind, number, title = cap_match.groups()
            add_caption(doc, f"{kind}{number}　{title}", kind)
            i += 1
            continue

        if in_references and re.match(r"^\[\d+\]\s+", line):
            add_reference_paragraph(doc, line)
        else:
            p = add_body_paragraph(doc, line)
            if line.startswith("**关键词：**"):
                p.paragraph_format.first_line_indent = Pt(0)
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(0)
        i += 1

    # Remove the initial empty paragraph if it stayed empty.
    if doc.paragraphs and not doc.paragraphs[0].text and len(doc.paragraphs[0]._p) <= 1:
        p = doc.paragraphs[0]._element
        p.getparent().remove(p)

    # Ensure no accidental tracked-change/comments modes and save.
    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    path = build_document()
    print(path)
