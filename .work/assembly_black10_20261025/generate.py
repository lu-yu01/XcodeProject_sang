from pathlib import Path
from itertools import product
import random,pprint,json,hashlib
from datetime import datetime
from solver import *
ROOT=Path(__file__).resolve().parent
R=random.Random(2026102517)

def box(d):return tuple(product(*(range(i) for i in d)))
def part(cells,b):return normalize({'cells':tuple(cells),'black':(b,)})
def partition(target,sizes):
 ts=set(target)
 for _ in range(12000):
  rem=ts.copy();out=[]
  for sz in sizes[:-1]:
   s={R.choice(sorted(rem))}
   while len(s)<sz:
    front={q for c in s for q in neighbors(c) if q in rem and q not in s}
    if not front:break
    s.add(R.choice(sorted(front)))
   if len(s)!=sz:break
   out.append(tuple(sorted(s)));rem-=s
  if len(out)==len(sizes)-1 and len(rem)==sizes[-1] and connected(rem):
   out.append(tuple(sorted(rem)))
   # At least two spatial parts; never turn a complete item into a flat tiling.
   if sum(min(dims(p))>1 for p in out)>=2:return out
 raise RuntimeError('partition failed')

def extreme_cells(cells):
 return [c for c in cells if any(c[i] in (min(p[i] for p in cells),max(p[i] for p in cells)) for i in range(3))]

def present(p):
 # Present black on the global upper boundary, keeping all coordinates faithful.
 os=orientations(p)
 visible=[q for q in os if q['black'][0][2]==max(c[2] for c in q['cells'])]
 return R.choice(visible or os)

def mutate(p):
 s=set(p['cells'])
 for _ in range(200):
  drop=R.choice(sorted(s));rem=s-{drop}
  front={q for c in rem for q in neighbors(c) if q not in s}
  add=R.choice(sorted(front));q=rem|{add}
  if connected(q) and min(dims(q))>1:
   ex=extreme_cells(q)
   return part(q,R.choice(ex))
 return None

def graph_profile(cells):
 s=set(cells)
 return (edges(s),tuple(sorted(sum(q in s for q in neighbors(c)) for c in s)))

TARGETS=[]
TARGETS.append((box((3,2,2)),(4,4,4),'三块补成完整长方体'))
TARGETS.append((tuple(c for c in box((3,3,2)) if not (c[2]==1 and (c[0],c[1]) in ((0,0),(2,0),(2,2)))),(5,5,5),'转角凹口与黑格定位'))
TARGETS.append((box((4,2,2)),(5,5,6),'长边匹配与黑格间距'))
TARGETS.append((tuple(c for c in box((3,3,2)) if c[2]==0 or (c[0],c[1]) in ((0,0),(1,0),(0,1),(1,1),(1,2))),(4,5,5),'阶梯补形与面内黑格'))
TARGETS.append((tuple(c for c in box((4,3,2)) if not (c[2]==1 and (c[0],c[1]) in ((0,0),(3,0),(0,2),(3,2)))),(6,7,7),'两侧凹口与颜色保持'))
TARGETS.append((tuple(c for c in box((3,3,3)) if c[2]==0 or (c[2]==1 and (c[0],c[1])!=(2,2)) or (c[2]==2 and c[0]<2 and c[1]<2)),(7,7,7),'三层台阶与凸块落位'))
TARGETS.append((tuple(c for c in box((3,3,2)) if not (c[2]==1 and (c[0],c[1]) in ((0,0),(2,2)))),(5,5,6),'对角缺口与镜像辨别'))
TARGETS.append((tuple(c for c in box((4,3,2)) if c[2]==0 or (c[0],c[1]) in ((0,0),(1,0),(1,1),(2,1),(2,2),(3,2))),(6,6,6),'错层长臂与黑格顺序'))
TARGETS.append((tuple(c for c in box((3,3,3)) if c[2]==0 or (c[2]==1 and (c[0],c[1]) not in ((0,2),(2,2))) or (c[2]==2 and c[0]<2 and c[1]<2)),(6,7,7),'多重贴合与颜色交叉制约'))
TARGETS.append((tuple(c for c in box((4,3,2)) if not (c[2]==1 and (c[0],c[1]) in ((0,0),(1,0),(3,2)))),(7,7,7),'凹凸互锁与黑格相对位置'))

QUESTIONS=[];used=set()
answers='CADBACBDCA'
for n,(tc,sizes,point) in enumerate(TARGETS,1):
 assert len(tc)==sum(sizes),(n,len(tc),sizes)
 maxz=max(c[2] for c in tc);mx=max(c[0] for c in tc);my=max(c[1] for c in tc)
 eligible={c for c in tc if c[2]==maxz or (c[0] in (0,mx) and c[1] in (0,my))}
 for attempt in range(1000):
  raw=partition(tc,sizes)
  if not all(set(p)&eligible for p in raw):continue
  choices=[]
  for i,p in enumerate(raw):
   ex=list(set(p)&eligible)
   # Spread marks across target; even items also favour a low outer corner.
   R.shuffle(ex)
   ex.sort(key=lambda c:(-sum(sum(abs(c[k]-a[k]) for k in range(3)) for a in choices),c[2] if n%2==0 and i==0 else -c[2]))
   choices.append(ex[0])
  target={'cells':tuple(sorted(tc)),'black':tuple(sorted(choices))}
  original=[part(p,b) for p,b in zip(raw,choices)]
  shown=[present(p) for p in original]
  known=shown[:2];good=shown[2]
  if canonical(good,False) in used:continue
  swaps=[]
  for b in extreme_cells(good['cells']):
   if b==good['black'][0]:continue
   p=present(part(good['cells'],b))
   if canonical(p)==canonical(good):continue
   if not solve(known+[p],target):swaps.append(p)
  if not swaps:continue
  # Best same-shape distractor changes black position meaningfully, not by symmetry.
  swaps.sort(key=lambda p:sum(abs(p['black'][0][i]-good['black'][0][i]) for i in range(3)),reverse=True)
  wrong=[swaps[0]]
  mir=present(mirror(good))
  if canonical(mir,False)!=canonical(good,False) and not solve(known+[mir],target):wrong.append(mir)
  for _ in range(800):
   if len(wrong)==3:break
   p=mutate(good)
   if not p:continue
   p=present(p)
   if canonical(p,False)==canonical(good,False):continue
   if canonical(p) in {canonical(x) for x in wrong}:continue
   if sorted(dims(p['cells']))!=sorted(dims(good['cells'])):continue
   if solve(known+[p],target):continue
   # Keep at least one true shape rejection rather than only changing marks.
   if solve(known+[p],target,coloured=False):continue
   wrong.append(p)
  if len(wrong)!=3:continue
  answer=answers[n-1];options=wrong[:];options.insert('ABCD'.index(answer),good)
  sol=solve(known+[good],target)[0]
  used.add(canonical(good,False))
  q={'n':n,'stem':'完整立体由①、②和第三部分拼成。请选择能够补齐整体、且三枚黑色小正方体位置完全一致的第三部分。','target':target,'pieces':known,'options':options,'answer':answer,'point':point,'difficulty':'中等' if n<=6 else '较难','analysis':[],'solution':sol}
  QUESTIONS.append(q)
  (ROOT/'puzzles.py').write_text('"""Ten original colour-preserving three-part assembly items."""\nQUESTIONS = '+pprint.pformat(QUESTIONS,width=120,sort_dicts=False)+'\n',encoding='utf-8')
  print('saved',n,'attempt',attempt,'sizes',sizes,'answer',answer,flush=True)
  break
 else:raise RuntimeError(('unable to produce question',n))
print('ALL 10 GEOMETRIES READY',flush=True)
