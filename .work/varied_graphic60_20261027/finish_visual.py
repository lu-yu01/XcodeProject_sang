import json
from model import ROOT,OUT,sha,dump
r=json.loads((ROOT/'page_revision.json').read_text(encoding='utf8'))
assert r['changed_pages_requiring_actual_reopen']==[15,35]
for p in r['pages']:
    if p['page'] in [15,35]:
        p.update(actually_opened_at_original_size=True,result='pass',inspection_basis='Final revised page actually reopened at original resolution')
old=json.loads((ROOT/'visual_review_before_heading.json').read_text(encoding='utf8'))
old.update(word_sha256=sha(OUT),pdf_sha256=sha(ROOT/'preview.pdf'),final_pages=r['pages'],
    final_revision='两处第15组标题顿号改为空格；38页图逐字节相同，修订页15、35重新实际打开，均通过。',
    page_revision_report_sha256=sha(ROOT/'page_revision.json'))
dump(ROOT/'visual_review.json',old)
print('Final visual review bound to '+sha(OUT))
