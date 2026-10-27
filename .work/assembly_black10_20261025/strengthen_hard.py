from pathlib import Path
import pprint
from solver import *
from puzzles import QUESTIONS

def rooted_signature(part):
 s=set(part['cells']);b=part['black'][0];ds={b:0};todo=[b]
 for c in todo:
  for q in neighbors(c):
   if q in s and q not in ds:ds[q]=ds[c]+1;todo.append(q)
 return (sum(q in s for q in neighbors(b)),tuple(sorted(ds.values())))

def present(part):
 os=orientations(part)
 top=[p for p in os if p['black'][0][2]==max(c[2] for c in p['cells'])]
 return min(top or os,key=lambda p:(dims(p['cells'])[2],p['cells'],p['black']))

for q in QUESTIONS[6:]:
 ai='ABCD'.index(q['answer']);oldgood=q['options'][ai];raw=q['solution'][2]
 oldblack=raw['black'][0];targetcells=q['target']['cells'];mx,my,mz=(max(c[i] for c in targetcells) for i in range(3))
 eligible=[c for c in raw['cells'] if c[2]==mz or (c[0] in (0,mx) and c[1] in (0,my))]
 best=None
 for gb in eligible:
  good=present(normalize({'cells':raw['cells'],'black':(gb,)}))
  target={'cells':targetcells,'black':tuple(sorted((set(q['target']['black'])-{oldblack})|{gb}))}
  assert len(target['black'])==3
  for b in good['cells']:
   wrong=present({'cells':good['cells'],'black':(b,)})
   if canonical(wrong)==canonical(good):continue
   if rooted_signature(wrong)[0]!=rooted_signature(good)[0]:continue
   if solve(q['pieces']+[wrong],target):continue
   score=(100 if rooted_signature(wrong)==rooted_signature(good) else 0)+(5 if gb==oldblack else 0)
   item=(score,good,wrong,target)
   if best is None or score>best[0]:best=item
 assert best,(q['n'],'no colour-position challenge')
 _,good,wrong,target=best
 wrongidx=next(i for i,p in enumerate(q['options']) if i!=ai and canonical(p,False)==canonical(oldgood,False))
 q['options'][ai]=good;q['options'][wrongidx]=wrong;q['target']=target
 for i,p in enumerate(q['options']):
  if i in (ai,wrongidx):continue
  if solve(q['pieces']+[p],target):
   for b in p['cells']:
    alt=present({'cells':p['cells'],'black':(b,)})
    if not solve(q['pieces']+[alt],target):q['options'][i]=alt;break
   else:raise RuntimeError('unable preserve rejection')
 q['solution']=solve(q['pieces']+[good],target)[0]
 q['same_shape_distractor']='ABCD'[wrongidx]
 q['same_shape_black_rooted_signature']={'correct':rooted_signature(good),'wrong':rooted_signature(wrong)}
 print('q',q['n'],'same-shape distractor',q['same_shape_distractor'],'signature',q['same_shape_black_rooted_signature'],'targetblack',target['black'])

out=Path(__file__).with_name('puzzles.py')
out.write_text('"""Ten original colour-preserving three-part assembly items."""\nQUESTIONS = '+pprint.pformat(QUESTIONS,width=120,sort_dicts=False)+'\n',encoding='utf-8')
