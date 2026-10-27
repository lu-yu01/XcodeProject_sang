from pathlib import Path
import json,hashlib,zipfile
import pypdfium2 as pdfium
from docx import Document
from model import ROOT,PROJECT,REF
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=ROOT/'baseline_docx.json'
if not baseline.exists():baseline.write_text(json.dumps({str(p.relative_to(PROJECT)):sha(p) for p in (PROJECT/'模式题').glob('*.docx')},ensure_ascii=False,indent=2),encoding='utf-8')
doc=Document(REF)
evidence={'reference':str(REF),'reference_sha256':sha(REF),'sections':[s._sectPr.xml for s in doc.sections],
 'styles':{name:doc.styles[name].element.xml for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Stem','Figure','Explanation']}}
with zipfile.ZipFile(REF) as z:
 evidence['parts']=[{'part':n,'bytes':len(z.read(n)),'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in z.namelist()]
(ROOT/'template_reference.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
folder=ROOT/'template_render';folder.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(ROOT.parent/'beijing_graphic3_20261027'/'preview.pdf')
assert len(pdf)==2
for i,p in enumerate(pdf):p.render(scale=150/72).to_pil().save(folder/f'page-{i+1:02}.png')
print(json.dumps({'baseline_words':len(json.loads(baseline.read_text(encoding='utf-8'))),'reference_pages':len(pdf),'reference_sha256':sha(REF)}))
