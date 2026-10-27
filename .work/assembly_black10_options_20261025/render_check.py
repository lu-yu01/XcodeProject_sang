"""Final document structural checks and temporary page rendering."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,sys
import pypdfium2 as pdfium
from pypdf import PdfReader
from lxml import etree
from puzzles import QUESTIONS
from build import ROOT,DOCX,sha

PDF=ROOT/'preview.pdf'

def compact(t):return re.sub(r'\s+','',t)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert DOCX.exists() and PDF.exists()
    assert PDF.stat().st_mtime>=DOCX.stat().st_mtime
    with ZipFile(DOCX) as z:
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
        xml=etree.fromstring(z.read('word/document.xml'))
        assert len(xml.findall('.//a:blip',ns))==20
        assert len([n for n in z.namelist() if n.startswith('word/media/')])==20
        rel=etree.fromstring(z.read('word/_rels/document.xml.rels'))
        assert not [el for el in rel if el.get('TargetMode')=='External' and el.get('Type','').endswith('/image')]
        numbering=etree.fromstring(z.read('word/numbering.xml'))
        qids={}
        for para in xml.findall('.//w:body/w:p',ns):
            nid=para.find('./w:pPr/w:numPr/w:numId',ns)
            if nid is not None:qids.setdefault(nid.get('{'+ns['w']+'}val'),[]).append(''.join(para.itertext()))
        assert sorted(map(len,qids.values()))==[10,10]
        paras=[''.join(p.itertext()) for p in xml.findall('.//w:body/w:p',ns)]
        xmltext=compact(''.join(paras))
        for q in QUESTIONS:
            for value in [q['stem'],'答案：'+q['answer'],'考点：'+q['point']]+q['analysis']:
                assert compact(value) in xmltext,(q['n'],value)
    texts=[p.extract_text() or '' for p in PdfReader(PDF).pages]
    combined=compact(''.join(texts))
    for q in QUESTIONS:
        for value in [q['stem'],'考点：'+q['point']]+q['analysis']:
            assert compact(value) in combined,(q['n'],value)
    assert 10<=len(texts)<=12,len(texts)
    for i,q in enumerate(QUESTIONS):
        assert compact(q['stem']) in compact(texts[i//2]),('question moved page',q['n'])
    numbers=[]
    for page in texts:numbers.extend(int(n) for n in re.findall(r'(?m)^\s*(\d{1,2})\.\s*',page))
    assert numbers==list(range(1,11))*2,numbers
    output=ROOT/'render';output.mkdir(exist_ok=True)
    for old in output.glob('page-*.png'):
        assert old.resolve().parent==output.resolve() and not old.is_symlink()
        old.unlink()
    pdf=pdfium.PdfDocument(str(PDF))
    pages=[]
    for i in range(len(pdf)):
        path=output/f'page-{i+1:02}.png'
        pdf[i].render(scale=150/72).to_pil().convert('RGB').save(path)
        pages.append({'page':i+1,'path':str(path),'sha256':sha(path)})
    (ROOT/'render_text.txt').write_text('\n\n'.join(f'=== PAGE {i+1} ===\n{t}' for i,t in enumerate(texts)),encoding='utf-8')
    report={'passed':True,'pages':len(texts),'question_count':10,'embedded_images':20,'word_sha256':sha(DOCX),'pdf_sha256':sha(PDF),
            'all_stems_and_analyses_present':True,'two_questions_per_page':True,'question_and_answer_numbers':numbers,'page_images':pages,'preview_png_status':'present_for_visual_review'}
    (ROOT/'render_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='page_images'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
