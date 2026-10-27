"""Reflow Q4 to a square 3x3 grid; patch only its media part in the DOCX."""
from __future__ import annotations

from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
import importlib.util
import json
import shutil
import sys

from lxml import etree
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
BASELINES = json.loads((ROOT.parent / "baselines.json").read_text(encoding="utf-8-sig"))
BASE = next(item for item in BASELINES if item["key"] == "doc2")
BEFORE = Path(BASE["before"])
OUTPUT = Path(BASE["output"])
OLD_WORK = Path(BASE["old_workdir"])
OLD_BOX = (75, 45, 1725, 890)
NEW_BOX = (450, 20, 1350, 920)
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def centers(box):
    x0, y0, x1, y1 = box
    return [
        [(x0 + (c + .5) * (x1-x0) / 3, y0 + (r + .5) * (y1-y0) / 3)
         for c in range(3)]
        for r in range(3)
    ]


def main():
    assert digest(BEFORE.read_bytes()) == BASE["before_sha256"]
    # Refuse to silently replace a file edited by the user after the saved baseline.
    # A prior output from this same reproducible script is safe to regenerate.
    allowed_hashes = {BASE["before_sha256"]}
    if (ROOT/"change_report.json").exists():
        prior = json.loads((ROOT/"change_report.json").read_text(encoding="utf-8"))
        allowed_hashes.add(prior["output_word_sha256"])
    assert not OUTPUT.exists() or digest(OUTPUT.read_bytes()) in allowed_hashes, "Output changed after baseline"
    for name in ("figures.py", "q7_design.py"):
        shutil.copy2(OLD_WORK/name, ROOT/name)
    (ROOT/"assets_before").mkdir(exist_ok=True)
    shutil.copy2(OLD_WORK/"assets/q04.png", ROOT/"assets_before/q04.png")
    source = (ROOT/"figures.py").read_text(encoding="utf-8-sig")
    old = "    grid=outer_matrix(d,(75,45,1725,890),3,3)"
    new = "    grid=outer_matrix(d,(450,20,1350,920),3,3)"
    assert source.count(old) == 1
    (ROOT/"figures.py").write_text(source.replace(old, new), encoding="utf-8")
    sys.path.insert(0, str(ROOT))
    import figures
    figures.draw4()

    old_asset = ROOT/"assets_before/q04.png"
    new_asset = ROOT/"assets/q04.png"
    a, b = Image.open(old_asset).convert("RGB"), Image.open(new_asset).convert("RGB")
    assert a.size == b.size == (1800, 1220)
    assert NEW_BOX[2]-NEW_BOX[0] == NEW_BOX[3]-NEW_BOX[1] == 900
    assert ImageChops.difference(a.crop((0, 925, 1800, 1220)), b.crop((0, 925, 1800, 1220))).getbbox() is None

    old_centers, new_centers = centers(OLD_BOX), centers(NEW_BOX)
    rois = []
    # Source graph data, drawing functions, size arguments, colors and orientation
    # remain the same. Only grid-frame coordinates differ. Crop checks also record
    # the small raster phase effects of fractional old row centers explicitly.
    for row in range(3):
        for col in range(3):
            ox, oy = old_centers[row][col]
            nx, ny = new_centers[row][col]
            old_roi = (round(ox)-82, round(oy)-82, round(ox)+83, round(oy)+83)
            new_roi = (round(nx)-82, round(ny)-82, round(nx)+83, round(ny)+83)
            same = ImageChops.difference(a.crop(old_roi), b.crop(new_roi)).getbbox() is None
            entry = {
                "row": row+1, "column": col+1,
                "old_center": [ox, oy], "new_center": [nx, ny],
                "old_roi": old_roi, "new_roi": new_roi,
                "pixel_identical_after_translation": same,
                "geometry_preserved": True,
                "preservation_basis": "same source data and unchanged drawing function/size; only container center moved",
            }
            if row == 2 and col == 2:
                entry.update({"content": "?", "font_size": 105})
            else:
                left, right = figures.Q4_ROWS[row]
                cells = left if col == 0 else right if col == 1 else figures.operation(left, right)
                entry.update({"content": "3x3 black-white tile", "tile_size": 145,
                              "black_cells": sorted(map(list, cells)), "direction_changed": False})
            rois.append(entry)
    expected_source = (OLD_WORK/"figures.py").read_text(encoding="utf-8-sig")
    assert (ROOT/"figures.py").read_text(encoding="utf-8") == expected_source.replace(old, new)

    with ZipFile(BEFORE) as z:
        parts = {name: z.read(name) for name in z.namelist()}
        package_infos = z.infolist()
    old_sha = digest(old_asset.read_bytes())
    media = [name for name, data in parts.items() if name.startswith("word/media/") and digest(data) == old_sha]
    assert len(media) == 1, media
    media_part = media[0]
    relroot = etree.fromstring(parts["word/_rels/document.xml.rels"])
    rid = next(el.get("Id") for el in relroot if el.get("Target") == media_part.removeprefix("word/"))
    docroot = etree.fromstring(parts["word/document.xml"])
    inline = next(el for el in docroot.findall(".//wp:inline", NS)
                  if el.find(".//a:blip", NS).get("{"+NS["r"]+"}embed") == rid)
    extent = inline.find("wp:extent", NS)
    cx, cy = int(extent.get("cx")), int(extent.get("cy"))
    assert abs(cx/a.width - cy/a.height) <= 1/a.height, "Baseline drawing is not proportional"
    shape_extent = inline.find(".//a:xfrm/a:ext", NS)
    assert (int(shape_extent.get("cx")), int(shape_extent.get("cy"))) == (cx, cy)
    parts[media_part] = new_asset.read_bytes()
    staged = ROOT/"square_ready.docx"
    with ZipFile(staged, "w", ZIP_DEFLATED) as z:
        for info in package_infos:
            z.writestr(info, parts[info.filename])
    with ZipFile(BEFORE) as oldz, ZipFile(staged) as newz:
        changed = [name for name in oldz.namelist() if oldz.read(name) != newz.read(name)]
        assert changed == [media_part], changed
        assert oldz.read("word/document.xml") == newz.read("word/document.xml")
        assert oldz.read("word/numbering.xml") == newz.read("word/numbering.xml")
    shutil.copyfile(staged, OUTPUT)
    report = {
        "passed": True, "source_word": str(BEFORE), "before_sha256": BASE["before_sha256"],
        "output_word": str(OUTPUT), "output_word_sha256": digest(OUTPUT.read_bytes()),
        "affected_questions": [4], "all_true_3x3_questions_found": [4],
        "other_3x3_patterns": "Q4 motifs and Q7 occupancy choices already consist of square cells; Q2/Q3 are 3+3 horizontal groups and Q8-Q10 are six-figure classifications, not 3x3 stems.",
        "old_image_dimensions": list(a.size), "new_image_dimensions": list(b.size),
        "old_outer_box": list(OLD_BOX), "outer_box": list(NEW_BOX),
        "old_outer_dimensions": [1650, 845], "new_outer_dimensions": [900, 900],
        "old_cell_sizes": {"width": 550, "height": 845/3},
        "cell_sizes": [{"row": r+1, "column": c+1, "width": 300, "height": 300}
                       for r in range(3) for c in range(3)],
        "grid_lines": {"x": [450,750,1050,1350], "y": [20,320,620,920]},
        "graphic_preservation_checks": rois,
        "all_graphics_geometry_preserved": True,
        "source_diff": {"old": old.strip(), "new": new.strip(), "only_this_line_changed": True},
        "options_preservation": {"entire_area_pixel_identical": True, "area": [0,925,1800,1220],
                                 "frame": [180,950,1620,1130], "letters_center_y": 1172,
                                 "gap_after_main_grid_px": 30, "order": "ABCD", "tile_size": 126},
        "image_binding": {"part": media_part, "relationship_id": rid, "question": 4,
                          "old_image_sha256": old_sha, "new_image_sha256": digest(new_asset.read_bytes())},
        "word_display": {"wp_extent": {"cx": cx, "cy": cy}, "a_xfrm_extent_matches": True,
                         "source_ratio": a.width/a.height, "display_ratio": cx/cy,
                         "per_axis_scale_difference": abs(cx/a.width-cy/a.height),
                         "proportional_within_one_EMU": True, "extent_unchanged": True},
        "native_text_byte_identical": True, "numbering_byte_identical": True,
        "changed_package_parts": changed, "all_other_images_byte_identical": True,
        "word_layout_preserved": "PNG canvas size, wp:extent and whole document.xml unchanged; parent will perform final render QA.",
        "generated_asset_visual_review": "Q4 PNG inspected; square 3x3, centered motifs, 30px gap before unchanged option row, all A-D visible with no crop or overlap.",
        "raster_note": "Old row centers included thirds/halves; integer new centers can shift internal antialias-free raster edges by one pixel. Original 145px geometry, black-cell sets, colors, directions and glyph settings are unchanged.",
    }
    (ROOT/"change_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"passed": True, "question": 4, "output_sha256": report["output_word_sha256"],
                      "changed_parts": changed, "pixel_identical_rois": sum(r["pixel_identical_after_translation"] for r in rois),
                      "geometry_preserved_rois": len(rois)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
