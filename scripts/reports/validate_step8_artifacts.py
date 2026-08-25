"""第8步实验数据与可视化素材的可重复一致性审计。"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "evidence" / "validated_experiments"
IMAGES = ROOT / "assets" / "reports" / "figures"
ALGORITHMS = {"A*", "ACO", "PSO", "SA", "混合优化算法"}


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


static = read_csv("静态实验逐次结果.csv")
dynamic = read_csv("动态实验逐次结果.csv")
assert len(static) == 900
assert len(dynamic) == 500
assert set(row["algorithm"] for row in static) == ALGORITHMS
assert set(row["algorithm"] for row in dynamic) == ALGORITHMS
assert Counter(row["algorithm"] for row in static) == Counter({name: 180 for name in ALGORITHMS})
assert Counter(row["algorithm"] for row in dynamic) == Counter({name: 100 for name in ALGORITHMS})

all_rows = static + dynamic
false_positive = [row for row in all_rows if row["reported_success"] == "1" and row["valid_success"] != "1"]
unclassified_failure = [row for row in all_rows if row["valid_success"] == "0" and not row["invalid_reason"]]
assert not false_positive
assert not unclassified_failure

for row in static:
    assert abs(float(row["obstacle_actual"]) - float(row["obstacle_target"])) < 1e-12
    assert row["experiment"] == "static"
for row in dynamic:
    assert row["experiment"] == "dynamic"
    assert float(row["dynamic_rate"]) in {0.03, 0.08}

with (DATA / "实验清单与汇总.json").open("r", encoding="utf-8") as handle:
    manifest = json.load(handle)

wb = load_workbook(DATA / "验证后实验结果.xlsx", read_only=True, data_only=False)
expected_sheets = {
    "static_raw": (901, 20),
    "dynamic_raw": (501, 20),
    "static_summary": (31, 13),
    "dynamic_summary": (101, 14),
    "static_by_algorithm": (6, 11),
    "dynamic_by_algorithm": (11, 12),
}
assert wb.sheetnames == list(expected_sheets)
for sheet_name, dimensions in expected_sheets.items():
    ws = wb[sheet_name]
    assert (ws.max_row, ws.max_column) == dimensions
assert any(cell.value == "混合优化算法" for row in wb["static_summary"].iter_rows() for cell in row)

image_files = sorted(IMAGES.glob("*.png"))
assert len(image_files) == 22
image_info = {}
for file in image_files:
    with Image.open(file) as image:
        width, height = image.size
        assert width >= 1200 and height >= 650
        image.verify()
        image_info[file.name] = [width, height]

result = {
    "status": "PASS",
    "static_rows": len(static),
    "dynamic_rows": len(dynamic),
    "total_executions": len(all_rows),
    "false_positive_paths": len(false_positive),
    "unclassified_failures": len(unclassified_failure),
    "xlsx_sheets": expected_sheets,
    "strict_json": True,
    "manifest_top_level_keys": sorted(manifest),
    "png_count": len(image_files),
    "png_dimensions": image_info,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
