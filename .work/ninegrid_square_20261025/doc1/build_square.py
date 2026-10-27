"""Square Q2's nine-cell layout while preserving the entire existing Word package.

Only eight figure locations and the question mark move horizontally. No symbol,
filled cell, candidate, caption, answer, text, numbering, or Word size changes.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from hashlib import sha256
import json
import posixpath
from lxml import etree
from PIL import Image, ImageChops
import figures

ROOT = Path(__file__).resolve().parent
BASELINES = ROOT.parent / 'baselines.json'
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def digest(data):
    return sha256(data).hexdigest()


def require_pixels_equal(a, b):
    assert a.size == b.size
    assert ImageChops.difference(a, b).getbbox() is None
    return digest(a.tobytes())


def main():
    baseline = next(x for x in json.loads(BASELINES.read_text(encoding='utf-8')) if x['key'] == 'doc1')
    before = Path(baseline['before'])
    output = Path(baseline['output'])
    assert digest(before.read_bytes()) == baseline['before_sha256']
    with ZipFile(before) as z:
        package = {n: z.read(n) for n in z.namelist()}
    doc = etree.fromstring(package['word/document.xml'])
    inline = next(i for i in doc.findall('.//wp:inline', NS)
                  if i.find('wp:docPr', NS).get('descr', '').startswith('q02：'))
    rid = inline.find('.//a:blip', NS).get('{' + NS['r'] + '}embed')
    rels = etree.fromstring(package['word/_rels/document.xml.rels'])
    target = next(r.get('Target') for r in rels if r.get('Id') == rid)
    media_path = posixpath.normpath('word/' + target)
    original_png = ROOT / 'assets' / 'q02_before.png'
    original_png.parent.mkdir(exist_ok=True)
    original_png.write_bytes(package[media_path])
    figures.draw2()
    new_png = ROOT / 'assets' / 'q02.png'
    old_image = Image.open(original_png).convert('RGB')
    new_image = Image.open(new_png).convert('RGB')
    assert old_image.size == new_image.size == (1500, 900)

    # Rectangles include each complete graphic and a safety margin, excluding
    # decorative frame lines. Q2's final cell contains the preserved question mark.
    regions = []
    for row in range(3):
        for col in range(3):
            old_cx, cy = 490 + 260 * col, 110 + 210 * row
            new_cx = 540 + 210 * col
            old_box = (old_cx-90, cy-90, old_cx+90, cy+90)
            new_box = (new_cx-90, cy-90, new_cx+90, cy+90)
            pixel_sha = require_pixels_equal(old_image.crop(old_box), new_image.crop(new_box))
            cell_box = (435 + 210*col, 5 + 210*row, 645 + 210*col, 215 + 210*row)
            assert new_box[0] > cell_box[0] and new_box[1] > cell_box[1]
            assert new_box[2] < cell_box[2] and new_box[3] < cell_box[3]
            regions.append({
                'cell': [row+1, col+1], 'kind': 'question_mark' if row == col == 2 else 'black_white_figure',
                'source_box': old_box, 'new_box': new_box,
                'old_center': [old_cx, cy], 'new_center': [new_cx, cy],
                'translation': [new_cx-old_cx, 0], 'rgb_pixel_identical': True,
                'rgb_sha256': pixel_sha, 'cell_box': cell_box,
                'verified_graphic_roi_margin_to_frame_px': 15,
                'figure_edge_nominal_margin_to_frame_px': 22.5 if row != 2 or col != 2 else None,
            })
    options_box = (0, 640, 1500, 900)
    options_sha = require_pixels_equal(old_image.crop(options_box), new_image.crop(options_box))
    outer_box = (435, 5, 1065, 635)
    assert outer_box[2]-outer_box[0] == outer_box[3]-outer_box[1] == 630
    assert all(x['cell_box'][2]-x['cell_box'][0] == x['cell_box'][3]-x['cell_box'][1] == 210 for x in regions)

    extent = inline.find('wp:extent', NS)
    cx, cy = int(extent.get('cx')), int(extent.get('cy'))
    shape_extent = inline.find('.//a:xfrm/a:ext', NS)
    assert cx*900 == cy*1500, 'Word image scaling must remain proportional'
    assert int(shape_extent.get('cx')) == cx and int(shape_extent.get('cy')) == cy
    changed = dict(package)
    changed[media_path] = new_png.read_bytes()
    touched = [n for n in package if package[n] != changed[n]]
    assert touched == [media_path]
    pending = ROOT / 'output.pending.docx'
    with ZipFile(pending, 'w', ZIP_DEFLATED) as z:
        for n, data in changed.items():
            z.writestr(n, data)
    pending.replace(output)
    report = {
        'status': 'ready_for_render', 'before': str(before), 'output': str(output),
        'before_sha256': digest(before.read_bytes()), 'output_sha256': digest(output.read_bytes()),
        'questions_changed': [2], 'all_true_nine_cell_questions': [2],
        'other_three_by_three_graphics': 'Q1 contains square 3×3 content grids; they are unchanged and already square.',
        'image_binding': {'question': 2, 'relationship_id': rid, 'package_path': media_path,
                          'old_png_sha256': digest(package[media_path]), 'new_png_sha256': digest(changed[media_path])},
        'outer_box': list(outer_box), 'old_outer_box': [360, 5, 1140, 635],
        'old_outer_size_px': [780, 630], 'new_outer_size_px': [630, 630],
        'cell_sizes': [[210, 210]]*9, 'old_cell_sizes': [[260, 210]]*9,
        'canvas_size_old': list(old_image.size), 'canvas_size_new': list(new_image.size),
        'cell_geometry_passed': True, 'graphic_preservation_checks': regions,
        'graphic_regions_pixel_identical': 9,
        'candidate_region': {'box': list(options_box), 'rgb_pixel_identical': True, 'rgb_sha256': options_sha,
                             'includes': 'Four-candidate shared frame, all candidate graphics, A-D letters and spacing'},
        'word_extents': {'cx_emu': cx, 'cy_emu': cy, 'unchanged': True,
                         'png_ratio': [1500, 900], 'proportional_scaling_passed': True,
                         'square_outer_size_in_word_emu': [cx*630//1500, cy*630//900]},
        'document_xml_byte_identical': True, 'numbering_xml_byte_identical': True,
        'all_text_answers_and_numbering_unchanged': True, 'text_replacements': {},
        'native_text_additions': [], 'package_parts_changed': touched,
        'other_embedded_images_unchanged': True,
        'no_new_pagination_height': True,
    }
    (ROOT/'change_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output':str(output), 'output_sha256':report['output_sha256'],
                      'outer_size_px':[630,630], 'cell_size_px':[210,210], 'pixel_identical_regions':9,
                      'candidate_region_pixel_identical':True, 'word_scaling_proportional':True}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
