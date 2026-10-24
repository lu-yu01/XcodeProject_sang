"""Check the actual Word-rendered numbering, answers and all text options."""
import json
import re
import sys
from pathlib import Path
from pypdf import PdfReader
from content import QUESTIONS

sys.stdout.reconfigure(encoding='utf-8')
root=Path(__file__).resolve().parent
pdf=PdfReader(root/'preview.pdf')
texts=[p.extract_text() for p in pdf.pages]
full='\n'.join(texts)
question_text,answer_text=full.split('参考答案与解析',1)
qn=[int(n) for n in re.findall(r'^\s*(\d+)\.\s',question_text,re.M)]
an=re.findall(r'^\s*(\d+)\.\s*答案：\s*([ABCD])',answer_text,re.M)
assert qn==list(range(1,36)),qn
assert an==[(str(q['n']),q['answer']) for q in QUESTIONS],an
assert re.findall(r'^\s*([A-Z])\.\s',question_text,re.M)==list('ABCD')*28
def compact(t):return re.sub(r'\s+','',t)
question_compact=compact(question_text)
answer_compact=compact(answer_text)
for q in QUESTIONS:
    assert compact(q['stem']) in question_compact,('stem',q['n'])
    for s in q['options']:assert compact(s) in question_compact,('option',q['n'],s)
    for s in q['analysis']:assert compact(s) in answer_compact,('analysis',q['n'],s)
report={'status':'passed','pages':len(pdf.pages),'question_numbers':qn,
        'answer_count':len(an),'text_option_blocks':28,
        'all_stems_options_and_analyses_present':True}
(root/'render_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
