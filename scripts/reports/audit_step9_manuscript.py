"""审计第9步Markdown正文的字数、图表公式与数字引用覆盖。"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO_ROOT / "docs" / "reports" / "路径规划虚拟仿真闭环AI科学家系统技术报告_正文源稿.md"
text = MANUSCRIPT.read_text(encoding="utf-8")

ref_marker = "# 参 考 文 献"
assert ref_marker in text
body, references = text.split(ref_marker, 1)

abstract_match = re.search(r"# 摘　　要\s*(.*?)\s*\*\*关键词", body, re.S)
assert abstract_match
abstract = re.sub(r"\s+", "", abstract_match.group(1))

body_no_markup = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
body_no_markup = re.sub(r"[`*_#$|>\-]", "", body_no_markup)
body_nonspace_chars = len(re.sub(r"\s+", "", body_no_markup))
body_cjk_chars = len(re.findall(r"[\u3400-\u9fff]", body_no_markup))
body_latin_numeric_tokens = len(
    re.findall(r"[A-Za-z]+(?:[-_][A-Za-z]+)*|\d+(?:\.\d+)*", body_no_markup)
)

image_links = re.findall(r"!\[([^\]]+)\]\(([^)]+\.png)\)", body)
figure_captions = re.findall(r"^\*\*图\d+-\d+[^\n]*\*\*$", body, re.M)
table_captions = re.findall(r"^\*\*表\d+-\d+[^\n]*\*\*$", body, re.M)
formula_tags = re.findall(r"\\tag\{(\d+-\d+)\}", body)
reference_entries = re.findall(r"^\[(\d+)\]\s+", references, re.M)


def expand_citation_group(group: str) -> set[int]:
    nums: set[int] = set()
    for part in re.split(r"[,，]", group):
        part = part.strip()
        if re.fullmatch(r"\d+", part):
            nums.add(int(part))
        elif re.fullmatch(r"\d+\s*[-—]\s*\d+", part):
            start, end = map(int, re.split(r"\s*[-—]\s*", part))
            nums.update(range(start, end + 1))
    return nums


citations: set[int] = set()
for match in re.finditer(r"\[([0-9]+(?:\s*[-—,，]\s*[0-9]+)*)\]", body):
    expanded = expand_citation_group(match.group(1))
    # 数学区间如 [0,1] 不是参考文献；数字引用从1开始。
    if expanded and min(expanded) >= 1:
        citations.update(expanded)

missing_image_paths = []
for _, rel in image_links:
    path = MANUSCRIPT.parent / rel
    if not path.exists():
        missing_image_paths.append(rel)

expected_refs = set(range(1, 43))
result = {
    "status": "PASS",
    "abstract_nonspace_chars": len(abstract),
    "body_nonspace_chars": body_nonspace_chars,
    "body_cjk_chars": body_cjk_chars,
    "body_latin_numeric_tokens": body_latin_numeric_tokens,
    "word_like_total": body_cjk_chars + body_latin_numeric_tokens,
    "figures": len(figure_captions),
    "image_links": len(image_links),
    "tables": len(table_captions),
    "formulas": len(formula_tags),
    "formula_tags": formula_tags,
    "references": len(reference_entries),
    "reference_numbers": [int(x) for x in reference_entries],
    "unique_body_citations": len(citations),
    "missing_citations": sorted(expected_refs - citations),
    "out_of_range_citations": sorted(citations - expected_refs),
    "uncited_references": sorted(expected_refs - citations),
    "missing_image_paths": missing_image_paths,
    "chapter_headings": len(re.findall(r"^# 第\d+章", body, re.M)),
    "has_conclusion": "# 结论与展望" in body,
}

checks = [
    len(abstract) <= 500,
    body_cjk_chars >= 10000,
    len(figure_captions) == 22,
    len(image_links) == 22,
    len(table_captions) == 18,
    len(formula_tags) == 17,
    formula_tags == ["2-1", "2-2", "3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7", "4-1", "4-2", "4-3", "5-1", "5-2", "6-1", "6-2", "6-3"],
    [int(x) for x in reference_entries] == list(range(1, 43)),
    citations == expected_refs,
    not missing_image_paths,
    result["chapter_headings"] == 6,
    result["has_conclusion"],
]
result["status"] = "PASS" if all(checks) else "FAIL"
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if result["status"] == "PASS" else 1)
