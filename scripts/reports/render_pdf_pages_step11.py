"""使用 bundled pypdfium2 将Word导出的PDF渲染为逐页PNG与联系表。"""

from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont


def render(pdf_path: Path, out_dir: Path, scale: float = 2.0) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    page_paths: list[Path] = []
    for index in range(len(pdf)):
        page = pdf[index]
        bitmap = page.render(scale=scale, rotation=0)
        image = bitmap.to_pil().convert("RGB")
        path = out_dir / f"page-{index + 1:03d}.png"
        image.save(path, "PNG", optimize=True)
        page_paths.append(path)

    font = ImageFont.load_default()
    per_sheet = 12
    thumb_w, thumb_h = 300, 424
    gutter, label_h = 18, 24
    cols, rows = 4, 3
    for start in range(0, len(page_paths), per_sheet):
        subset = page_paths[start:start + per_sheet]
        sheet = Image.new(
            "RGB",
            (cols * (thumb_w + gutter) + gutter, rows * (thumb_h + label_h + gutter) + gutter),
            "#D9D9D9",
        )
        draw = ImageDraw.Draw(sheet)
        for local, path in enumerate(subset):
            with Image.open(path) as original:
                thumb = original.copy()
                thumb.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            x = gutter + (local % cols) * (thumb_w + gutter)
            y = gutter + (local // cols) * (thumb_h + label_h + gutter)
            page_no = start + local + 1
            draw.text((x, y), f"Page {page_no}", fill="black", font=font)
            y_img = y + label_h
            sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y_img))
        end = start + len(subset)
        sheet.save(out_dir / f"contact-{start + 1:03d}-{end:03d}.png", "PNG")
    return len(page_paths)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("out_dir")
    parser.add_argument("--scale", type=float, default=2.0)
    args = parser.parse_args()
    count = render(Path(args.pdf), Path(args.out_dir), args.scale)
    print(f"rendered_pages={count}")
