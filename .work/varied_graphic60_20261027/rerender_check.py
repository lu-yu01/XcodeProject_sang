import json
import pypdfium2 as pdfium
from model import ROOT,sha,dump

old=json.loads((ROOT/'visual_review.json').read_text(encoding='utf8'))
dump(ROOT/'visual_review_before_heading.json',old)
pdf=pdfium.PdfDocument(str(ROOT/'preview.pdf'))
assert len(pdf)==40
changed=[];same=[];pages=[]
for i,page in enumerate(pdf):
    p=ROOT/'render'/f'page-{i+1:02}.png'
    im=page.render(scale=150/72).to_pil().convert('RGB');im.save(p)
    h=sha(p)
    entry={'page':i+1,'path':str(p),'sha256':h,'pixels':list(im.size)}
    if h==old['final_pages'][i]['sha256']:
        same.append(i+1)
        entry.update(actually_opened_at_original_size=True,result='pass',inspection_basis='Byte-identical page to directly inspected preceding export')
    else:
        changed.append(i+1)
        entry.update(actually_opened_at_original_size=False,result='pending')
    pages.append(entry)
dump(ROOT/'page_revision.json',{'change':'Only group15 heading punctuation changed to spaces in two native headings; all source figures unchanged.',
    'preceding_word_sha256':old['word_sha256'],'preceding_pdf_sha256':old['pdf_sha256'],
    'current_pdf_sha256':sha(ROOT/'preview.pdf'),'byte_identical_pages':same,'changed_pages_requiring_actual_reopen':changed,'pages':pages})
print(json.dumps({'identical_pages':len(same),'changed_pages':changed},ensure_ascii=False))
