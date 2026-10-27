from pathlib import Path
import json
import pypdfium2 as pdfium
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent
render=ROOT/'render';render.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(ROOT/'preview.pdf')
for i,page in enumerate(pdf):
 im=page.render(scale=150/72).to_pil();im.save(render/f'page-{i+1:02}.png',dpi=(150,150))
texts=[p.extract_text() for p in PdfReader(ROOT/'preview.pdf').pages]
(ROOT/'pdf_text.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(texts),'text':texts},ensure_ascii=False))
