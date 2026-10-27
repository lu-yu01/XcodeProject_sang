import json
from model import ROOT,sha,dump
groups=json.loads((ROOT/'groups.json').read_text(encoding='utf-8'))
questions=json.loads((ROOT/'questions.json').read_text(encoding='utf-8'))
public=[]
for g in groups:
 d={k:g[k] for k in ['id','title','intro','rules','question_numbers']}
 d['questions']=[{'n':q['n'],'chain':[next(r['code'] for r in g['rules'] if r['id']==c) for c in q['chain']],
 'image':str(ROOT/'assets'/f'question-{q["n"]:02}.png'),'image_sha256':sha(ROOT/'assets'/f'question-{q["n"]:02}.png')}
 for q in questions if q['group']==g['id'] and (ROOT/'assets'/f'question-{q["n"]:02}.png').exists()]
 public.append(d)
dump(ROOT/'public_questions.json',{'instructions':'本组规则只限本组。三问独立起算，从左到右依次操作，外框和A—D不参与操作。','groups':public})
for g in groups:print(g['id'],g['title'],g['intro'],[(r['code'],r['text']) for r in g['rules']])
