from pathlib import Path
import json
import pypdfium2 as pdfium
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parent;render=ROOT/'render';render.mkdir(exist_ok=True)
pdf=pdfium.PdfDocument(ROOT/'preview.pdf')
for i,p in enumerate(pdf):p.render(scale=150/72).to_pil().save(render/f'page-{i+1:02}.png',dpi=(150,150))
texts=[p.extract_text() for p in PdfReader(ROOT/'preview.pdf').pages]
(ROOT/'pdf_text.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'pages':len(texts),'page_starts':[t[:55] for t in texts]},ensure_ascii=False))
