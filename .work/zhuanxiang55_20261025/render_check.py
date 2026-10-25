"""Render native Word PDF, check displayed text, then emit every page for QA."""
from pathlib import Path
import json,re,sys
import pypdfium2 as pdfium
from PIL import Image
from pypdf import PdfReader
from content import QUESTIONS,GROUPS
from suite_record import ROOT,DOCX,PDF,sha

def normalize(s):return re.sub(r'\s+','',s)
def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert PDF.stat().st_mtime_ns>=DOCX.stat().st_mtime_ns
    reader=PdfReader(PDF);texts=[p.extract_text() or '' for p in reader.pages]
    text='\n'.join(texts);compact=normalize(text)
    missing=[]
    for q in QUESTIONS:
        for kind,values in [('stem',[q['stem']]),('ask',[q['ask']]),('option',q['options']),('analysis',q['analysis'])]:
            for s in values:
                if s and normalize(s) not in compact:missing.append((q['n'],kind,s[:50]))
    for start,material in GROUPS.items():
        for s in material:
            if normalize(s) not in compact:missing.append((start,'material',s[:50]))
    assert not missing,missing
    answers=re.findall(r'(?m)^\s*(\d+)\.\s*答案[：:]\s*([ABCD])',text)
    assert answers==[(str(q['n']),q['answer']) for q in QUESTIONS],answers
    assert all(len(normalize(t))>30 for t in texts),'空白页'
    output=ROOT/'render'
    output.mkdir(exist_ok=True)
    # Remove only our own prior numbered page outputs, never source files.
    for old in list(output.glob('page-*.png'))+list(output.glob('pair-*.png')):old.unlink()
    document=pdfium.PdfDocument(str(PDF));pages=[]
    for i in range(len(document)):
        im=document[i].render(scale=150/72).to_pil().convert('RGB');im.save(output/f'page-{i+1:02}.png');pages.append(im)
    for i in range(0,len(pages),2):
        part=pages[i:i+2];im=Image.new('RGB',(sum(p.width for p in part),max(p.height for p in part)),'#ddd');x=0
        for p in part:im.paste(p,(x,0));x+=p.width
        im.save(output/f'pair-{i//2+1:02}.png')
    report={'passed':True,'pages':len(pages),'pdf_sha256':sha(PDF),'word_sha256':sha(DOCX),
            'answer_headers':len(answers),'all_stems_options_analyses_present':True,'nonempty_pages':len(texts)}
    (ROOT/'render_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'render_text.txt').write_text(text,encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
