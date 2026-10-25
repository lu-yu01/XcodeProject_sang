"""Render the final Word-exported PDF and record page-level checks."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw
from pypdf import PdfReader

from suite_record import PDF, ROOT, sha256
from content import QUESTIONS


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    doc = pdfium.PdfDocument(str(PDF))
    pages = []
    output = ROOT / "render"
    output.mkdir(exist_ok=True)
    for number in range(len(doc)):
        page = doc[number]
        image = page.render(scale=130 / 72).to_pil().convert("RGB")
        image.save(output / f"page-{number+1:02}.png")
        pages.append(image)

    for start in range(0, len(pages), 2):
        pair = pages[start : start + 2]
        width = sum(x.width for x in pair)
        height = max(x.height for x in pair)
        sheet = Image.new("RGB", (width, height), "#d7d7d7")
        x = 0
        for page in pair:
            sheet.paste(page, (x, 0))
            x += page.width
        sheet.save(output / f"pair-{start//2+1:02}.png")

    reader = PdfReader(PDF)
    extracted = [p.extract_text() or "" for p in reader.pages]
    compact = re.sub(r"\s+", "", "\n".join(extracted))
    for question in QUESTIONS:
        for value in [question["stem"], question["ask"]] + question["options"] + question["analysis"]:
            if value:
                assert re.sub(r"\s+", "", value) in compact, (question["n"], value)
    checks = {
        "passed": len(pages) >= 15 and all(len(t) > 60 for t in extracted),
        "pages": len(pages),
        "nonempty_text_pages": sum(len(t) > 60 for t in extracted),
        "page_pngs": len(pages),
        "pdf_sha256": sha256(PDF),
        "all_stems_options_analyses_present": True,
        "note": "UTF-8输出下中文提取正常，35题题干、文字选项和解析全部匹配；先前终端乱码来自输出编码，不能据此认定PDF缺少ToUnicode映射。",
    }
    (ROOT / "render_verification.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
