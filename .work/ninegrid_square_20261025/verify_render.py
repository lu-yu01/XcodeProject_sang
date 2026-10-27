"""Verify media-only square-grid edits, bind Word/PDF and render final pages."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
import argparse,json,re
from io import BytesIO
from PIL import Image
from lxml import etree
from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def compact(s):return re.sub(r'\s+','',s)
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def main(key):
    baseline=next(x for x in read(ROOT/'baselines.json') if x['key']==key)
    folder=ROOT/key;before=Path(baseline['before']);word=Path(baseline['output']);pdf=folder/'preview.pdf'
    assert digest(before)==baseline['before_sha256'],'Previous version backup changed'
    assert digest(baseline['original'])==baseline['original_sha256'],'Original file changed'
    assert pdf.exists() and pdf.stat().st_mtime>=word.stat().st_mtime,'PDF predates final Word'
    with ZipFile(before) as za,ZipFile(word) as zb:
        assert set(za.namelist())==set(zb.namelist()),'Package parts changed'
        changed=[n for n in za.namelist() if za.read(n)!=zb.read(n)]
        assert len(changed)=={'doc1':1,'doc2':1,'doc55':4}[key],changed
        assert all(n.startswith('word/media/') for n in changed),'Changes outside images'
        xml=etree.fromstring(zb.read('word/document.xml'))
        relxml=etree.fromstring(zb.read('word/_rels/document.xml.rels'))
        rels={x.get('Id'):x.get('Target').replace('\\','/') for x in relxml}
        image_checks=[]
        for drawing in xml.xpath('//w:drawing',namespaces=NS):
            blips=drawing.xpath('.//a:blip',namespaces=NS)
            if not blips:continue
            target='word/'+rels[blips[0].get('{'+NS['r']+'}embed')]
            if target not in changed:continue
            old=Image.open(BytesIO(za.read(target)));new=Image.open(BytesIO(zb.read(target)))
            assert new.size==old.size,(target,'Unexpected canvas size change')
            ext=drawing.xpath('.//wp:extent',namespaces=NS)[0]
            cx,cy=int(ext.get('cx')),int(ext.get('cy'))
            sx,sy=cx/new.width,cy/new.height
            assert abs(sx/sy-1)<0.00001,(target,'Nonuniform Word scaling')
            image_checks.append({'part':target,'source_canvas':list(new.size),'word_extent_emu':[cx,cy],
                                 'x_emu_per_pixel':sx,'y_emu_per_pixel':sy,'equal_scale':True})
        assert len(image_checks)==len(changed),'Not all changed images displayed'
        media=[n for n in zb.namelist() if n.startswith('word/media/')]
    pages=[p.extract_text() or '' for p in PdfReader(pdf).pages]
    rendered=compact(''.join(pages))
    for p in xml.xpath('//w:body/w:p',namespaces=NS):
        text=''.join(p.xpath('.//w:t/text()',namespaces=NS))
        if compact(text):assert compact(text) in rendered,('Unrendered paragraph',text[:90])
    for text in xml.xpath('//w:tbl//w:t/text()',namespaces=NS):
        if compact(text):assert compact(text) in rendered,('Unrendered table cell',text)
    out=folder/'render';out.mkdir(exist_ok=True)
    assert not list(out.glob('page-*.png')),'Unexpected prior pages; review before replacing'
    document=pdfium.PdfDocument(str(pdf));images=[]
    for i in range(len(document)):
        p=out/f'page-{i+1:02}.png';document[i].render(scale=150/72).to_pil().convert('RGB').save(p)
        images.append({'page':i+1,'path':str(p),'sha256':digest(p)})
    report={'passed':True,'key':key,'pages':len(images),'questions':baseline['questions'],'word':str(word),
            'word_sha256':digest(word),'pdf_sha256':digest(pdf),'before_sha256':digest(before),
            'original_word_unchanged':True,'previous_version_preserved':True,
            'only_target_media_changed':True,'document_xml_and_all_other_parts_byte_identical':True,
            'all_paragraphs_and_table_cells_rendered':True,'changed_images':changed,
            'equal_scale_image_checks':image_checks,'embedded_images':len(media),
            'page_images':images,'preview_png_status':'awaiting_visual_review'}
    write(folder/'render_verification.json',report)
    (folder/'render_text.txt').write_text('\n\n'.join(f'=== PAGE {i+1} ===\n{p}' for i,p in enumerate(pages)),encoding='utf-8')
    print({k:v for k,v in report.items() if k not in ['page_images','equal_scale_image_checks']})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('key',choices=['doc1','doc2','doc55']);main(p.parse_args().key)
