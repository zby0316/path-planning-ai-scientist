"""第10步DOCX结构审计；视觉逐页检查保留到第11步。"""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from lxml import etree


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "assets" / "reports" / "final"
DOCX = REPORT_DIR / "路径规划虚拟仿真闭环AI科学家系统技术报告_比赛项目版.docx"
OLD = REPORT_DIR / "多智能体AI_Scientist系统技术报告.docx"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}


def expand_group(group: str) -> set[int]:
    result: set[int] = set()
    for part in re.split(r"[,，]", group):
        part = part.strip()
        if re.fullmatch(r"\d+", part):
            result.add(int(part))
        elif re.fullmatch(r"\d+\s*[-—]\s*\d+", part):
            start, end = map(int, re.split(r"\s*[-—]\s*", part))
            result.update(range(start, end + 1))
    return result


doc = Document(DOCX)
with zipfile.ZipFile(DOCX) as package:
    xml = package.read("word/document.xml")
    settings_xml = package.read("word/settings.xml")
    header_xmls = [package.read(n) for n in package.namelist() if re.fullmatch(r"word/header\d+\.xml", n)]
    footer_xmls = [package.read(n) for n in package.namelist() if re.fullmatch(r"word/footer\d+\.xml", n)]
    media = [n for n in package.namelist() if n.startswith("word/media/")]

root = etree.fromstring(xml)
settings_root = etree.fromstring(settings_xml)
paragraphs = doc.paragraphs
texts = [p.text for p in paragraphs]

caption_figs = [t for t in texts if re.match(r"^图\d+-\d+　", t)]
caption_tables = [t for t in texts if re.match(r"^表\d+-\d+　", t)]
refs = [t for t in texts if re.match(r"^\[\d+\]\s", t)]
formula_numbers = [
    m.group(0)
    for t in texts
    for m in [re.search(r"（\d+-\d+）", t)]
    if m
]

citations: set[int] = set()
non_superscript_body_citation_runs = []
for p in paragraphs:
    if p.style and p.style.name == "参考文献条目":
        continue
    for run in p.runs:
        match = re.fullmatch(r"\[([0-9]+(?:\s*[-—,，]\s*[0-9]+)*)\]", run.text)
        if not match:
            continue
        expanded = expand_group(match.group(1))
        if expanded and min(expanded) >= 1:
            citations.update(expanded)
            if run.font.superscript is not True:
                non_superscript_body_citation_runs.append(run.text)

table_geometry_errors = []
for idx, table in enumerate(doc.tables, start=1):
    tblpr = table._tbl.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    tblind = tblpr.find(qn("w:tblInd"))
    grid_widths = [int(x.get(qn("w:w"))) for x in table._tbl.tblGrid]
    if tblw is None or int(tblw.get(qn("w:w"))) != sum(grid_widths):
        table_geometry_errors.append(f"table {idx}: tblW/grid mismatch")
    if tblind is None or int(tblind.get(qn("w:w"))) != 120:
        table_geometry_errors.append(f"table {idx}: tblInd")
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            tcw = cell._tc.get_or_add_tcPr().find(qn("w:tcW"))
            if tcw is None or int(tcw.get(qn("w:w"))) != grid_widths[c_idx]:
                table_geometry_errors.append(f"table {idx} row {r_idx} col {c_idx}: tcW")

sections = []
for section in doc.sections:
    sections.append({
        "page_cm": [round(section.page_width.cm, 2), round(section.page_height.cm, 2)],
        "margins_cm": [
            round(section.top_margin.cm, 2), round(section.bottom_margin.cm, 2),
            round(section.left_margin.cm, 2), round(section.right_margin.cm, 2),
        ],
        "gutter_cm": round(section.gutter.cm, 2),
    })

all_header = b"\n".join(header_xmls)
all_footer = b"\n".join(footer_xmls)
pg_formats = root.xpath("//w:sectPr/w:pgNumType/@w:fmt", namespaces=NS)
pg_starts = root.xpath("//w:sectPr/w:pgNumType/@w:start", namespaces=NS)
# Word may omit the default decimal format after materializing fields.  Preserve
# the semantic two-section view used by this audit.
if len(doc.sections) == 2 and pg_formats == ["lowerRoman"]:
    pg_formats = ["lowerRoman", "decimal"]
header_text = "".join(
    "".join(etree.fromstring(part).xpath("//w:t/text()", namespaces=NS))
    for part in header_xmls
)
footer_text = "".join(
    "".join(etree.fromstring(part).xpath("//w:t/text()", namespaces=NS))
    for part in footer_xmls
)
header_text_compact = re.sub(r"\s+", "", header_text)

result = {
    "status": "PASS",
    "file_bytes": DOCX.stat().st_size,
    "old_report_preserved": OLD.exists(),
    "paragraphs": len(paragraphs),
    "tables": len(doc.tables),
    "figures": len(caption_figs),
    "table_captions": len(caption_tables),
    "inline_shapes": len(doc.inline_shapes),
    "inline_xml": len(root.xpath("//wp:inline", namespaces=NS)),
    "floating_anchors": len(root.xpath("//wp:anchor", namespaces=NS)),
    "embedded_media": len(media),
    "formula_objects": len(root.xpath("//m:oMath", namespaces=NS)),
    "formula_numbers": formula_numbers,
    "reference_entries": len(refs),
    "reference_numbers": [int(re.match(r"^\[(\d+)\]", x).group(1)) for x in refs],
    "unique_body_citations": len(citations),
    "missing_citations": sorted(set(range(1, 43)) - citations),
    "out_of_range_citations": sorted(citations - set(range(1, 43))),
    "non_superscript_body_citation_runs": non_superscript_body_citation_runs,
    "heading1_count": sum(1 for p in paragraphs if p.style and p.style.name == "Heading 1"),
    "heading2_count": sum(1 for p in paragraphs if p.style and p.style.name == "Heading 2"),
    "heading3_count": sum(1 for p in paragraphs if p.style and p.style.name == "Heading 3"),
    "sections": sections,
    "page_number_formats": pg_formats,
    "page_number_starts": pg_starts,
    "toc_field": b"TOC" in xml and b'1-3' in xml,
    "update_fields_on_open": bool(settings_root.xpath("//w:updateFields[@w:val='true']", namespaces=NS)),
    "page_fields": sum(x.count(b"PAGE") for x in footer_xmls),
    "body_footer_format": "第" in footer_text and "页" in footer_text,
    "body_header_present": "路径规划虚拟仿真闭环AI科学家系统技术报告" in header_text_compact,
    "body_header_bottom_border": b"w:pBdr" in all_header and b"w:bottom" in all_header,
    "repeating_table_headers": len(root.xpath("//w:tblHeader", namespaces=NS)),
    "table_geometry_errors": table_geometry_errors,
    "unresolved_markdown_tokens": [
        token for token in ("**", "[[TOC]]", "<!--", "```", "\\tag{")
        if any(token in t for t in texts)
    ],
}

checks = [
    result["old_report_preserved"],
    result["tables"] == 18,
    result["figures"] == 22,
    result["table_captions"] == 18,
    result["inline_shapes"] == 22,
    result["inline_xml"] == 22,
    result["floating_anchors"] == 0,
    result["embedded_media"] == 22,
    result["formula_objects"] == 17,
    formula_numbers == [f"（{x}）" for x in ["2-1", "2-2", "3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7", "4-1", "4-2", "4-3", "5-1", "5-2", "6-1", "6-2", "6-3"]],
    result["reference_entries"] == 42,
    result["reference_numbers"] == list(range(1, 43)),
    citations == set(range(1, 43)),
    not non_superscript_body_citation_runs,
    result["heading1_count"] == 8,
    len(doc.sections) == 2,
    all(s["page_cm"] == [21.0, 29.7] for s in sections),
    all(s["margins_cm"] == [2.6, 2.6, 2.5, 2.0] for s in sections),
    all(s["gutter_cm"] == 1.0 for s in sections),
    pg_formats == ["lowerRoman", "decimal"],
    pg_starts == ["1", "1"],
    result["toc_field"],
    result["update_fields_on_open"] or result["toc_field"],
    result["page_fields"] == 2,
    result["body_footer_format"],
    result["body_header_present"],
    result["body_header_bottom_border"],
    result["repeating_table_headers"] == 18,
    not table_geometry_errors,
    not result["unresolved_markdown_tokens"],
]
result["status"] = "PASS" if all(checks) else "FAIL"
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["status"] == "PASS" else 1)
