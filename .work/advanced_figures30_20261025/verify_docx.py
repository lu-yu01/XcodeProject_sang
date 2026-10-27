"""Validate the final question/answer/image binding and actual rendered text."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from hashlib import sha256
from PIL import Image
from io import BytesIO
from pypdf import PdfReader
import pypdfium2 as pdfium
import json,re
from build import ROOT,DOCX,INDEX,data

def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def compact(s):return re.sub(r'\s+','',s)
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def main():
    questions,reports=data(draw=False);pdf=ROOT/'preview.pdf'
    assert pdf.exists() and pdf.stat().st_mtime>=DOCX.stat().st_mtime,'Stale or missing PDF'
    assert INDEX.exists(),'No suite index'
    with ZipFile(DOCX) as z:
        xml=etree.fromstring(z.read('word/document.xml'))
        paragraphs=xml.xpath('//w:body/w:p',namespaces=NS)
        texts=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in paragraphs]
        stem_paras=[p for p in paragraphs if p.xpath('./w:pPr/w:pStyle[@w:val="Question"]',namespaces=NS)]
        answer_paras=[p for p in paragraphs if p.xpath('./w:pPr/w:pStyle[@w:val="AnswerTitle"]',namespaces=NS)]
        assert len(stem_paras)==len(answer_paras)==30
        assert [''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in stem_paras]==[q['stem'] for q in questions]
        stem_ids=[p.xpath('./w:pPr/w:numPr/w:numId/@w:val',namespaces=NS)[0] for p in stem_paras]
        answer_ids=[p.xpath('./w:pPr/w:numPr/w:numId/@w:val',namespaces=NS)[0] for p in answer_paras]
        assert len(set(stem_ids))==len(set(answer_ids))==1 and stem_ids[0]!=answer_ids[0]
        # Exactly 30 numbered stems and 30 independently numbered answer headings.
        assert sum(t.startswith('答案：') for t in texts)==30
        for q in questions:
            assert q['stem'] in texts,(q['n'],'missing stem')
        answers=[t.split('：',1)[1] for t in texts if t.startswith('答案：')]
        assert answers==[q['answer'] for q in questions]
        relroot=etree.fromstring(z.read('word/_rels/document.xml.rels'))
        rels={r.get('Id'):'word/'+r.get('Target').replace('\\','/') for r in relroot}
        expected=[]
        for q in questions:expected.append((q['n'],'题图',q['image']))
        for q in questions:
            if q.get('explanation_image'):expected.append((q['n'],'解析',q['explanation_image']))
        drawings=xml.xpath('//w:drawing',namespaces=NS);assert len(drawings)==len(expected)
        bindings=[]
        for drawing,(n,role,name) in zip(drawings,expected):
            rid=drawing.xpath('.//a:blip/@r:embed',namespaces=NS)[0];raw=z.read(rels[rid]);source=ROOT/'assets'/name
            assert sha256(raw).hexdigest()==digest(source),(n,role,'wrong embedded image')
            im=Image.open(BytesIO(raw));ext=drawing.xpath('.//wp:extent',namespaces=NS)[0]
            cx,cy=int(ext.get('cx')),int(ext.get('cy'))
            assert abs((cx/im.width)/(cy/im.height)-1)<.00001,(n,'unequal image scaling')
            bindings.append({'question':n,'role':role,'image':name,'sha256':digest(source),'canvas':list(im.size),'extent_emu':[cx,cy]})
    pages=[p.extract_text() or '' for p in PdfReader(pdf).pages];alltext=compact(''.join(pages))
    for t in texts:
        if compact(t):assert compact(t) in alltext,('Unrendered paragraph',t[:90])
    for t in xml.xpath('//w:tbl//w:t/text()',namespaces=NS):
        if compact(t):assert compact(t) in alltext,('Unrendered table text',t)
    positions=[]
    for q in questions:
        # Stem text and text group options must remain fully rendered.
        assert compact(q['stem']) in alltext
        for i,t in enumerate(q['analysis']):
            assert compact(t) in alltext,(q['n'],'unrendered analysis')
        for t in q.get('options',[]) or []:assert compact(t) in alltext,(q['n'],'unrendered option')
        hits=[i+1 for i,p in enumerate(pages) if compact(q['stem']) in compact(p)]
        positions.append({'question':q['n'],'stem_pages':hits})
    out=ROOT/'render';out.mkdir(exist_ok=True)
    # Keep page generation tied to the latest Word/PDF; review and cleanup are separate.
    old=list(out.glob('page-*.png'))
    for p in old:
        assert p.resolve().parent==out.resolve() and not p.is_symlink();p.unlink()
    doc=pdfium.PdfDocument(str(pdf));imgs=[]
    for i in range(len(doc)):
        p=out/f'page-{i+1:02}.png';doc[i].render(scale=150/72).to_pil().convert('RGB').save(p)
        imgs.append({'page':i+1,'path':str(p),'sha256':digest(p)})
    result={'passed':True,'word':str(DOCX),'word_sha256':digest(DOCX),'pdf_sha256':digest(pdf),
            'pages':len(imgs),'questions':30,'answer_headings':30,'all_paragraphs_and_table_cells_rendered':True,
            'image_bindings':bindings,'stem_locations':positions,'page_images':imgs,'preview_png_status':'awaiting_actual_visual_review'}
    write(ROOT/'render_verification.json',result)
    (ROOT/'render_text.txt').write_text('\n\n'.join(f'=== PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)),encoding='utf-8')
    print({k:v for k,v in result.items() if k not in ['page_images','image_bindings','stem_locations']})

if __name__=='__main__':main()
