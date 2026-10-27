from pathlib import Path
import pypdfium2 as pdfium
import json,hashlib
ROOT=Path(__file__).resolve().parent
pdf=pdfium.PdfDocument(str(ROOT/'preview.pdf'));pages=[]
for i,page in enumerate(pdf):
    path=ROOT/'render'/f'page-{i+1:02}.png';im=page.render(scale=150/72).to_pil();im.save(path)
    pages.append({'page':i+1,'path':str(path),'pixels':list(im.size),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(ROOT/'render_manifest.json').write_text(json.dumps({'pdf_sha256':hashlib.sha256((ROOT/'preview.pdf').read_bytes()).hexdigest(),'pages':pages,'renderer':'Read-only native Word PDF, PDFium at150dpi; packaged renderer missing soffice.exe'},ensure_ascii=False,indent=2),encoding='utf8')
print('Rendered',len(pages),'pages')
