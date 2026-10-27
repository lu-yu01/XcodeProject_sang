from pathlib import Path
from itertools import product, combinations
import random,json,pprint
from collections import Counter
from solver import *
ROOT=Path(__file__).resolve().parent
R=random.Random(20261025)

def box(d):return tuple(product(*(range(a) for a in d)))
def profile(p):
 s=set(p)
 ds=sorted(sum(q in s for q in neighbors(c)) for c in s)
 runs=[]
 for i in range(3):
  best=0
  for c in s:
   n=0;q=list(c)
   while tuple(q) in s:n+=1;q[i]+=1
   best=max(best,n)
  runs.append(best)
 faces=0
 for p0 in s:
  for i,j in combinations(range(3),2):
   q=list(p0);q[i]+=1;r=list(p0);r[j]+=1;t=list(q);t[j]+=1
   if tuple(q) in s and tuple(r) in s and tuple(t) in s:faces+=1
 return {'volume':len(p),'edges':edges(p),'degrees':ds,'runs':sorted(runs),'squares':faces}

def acceptable(p):
 s=set(p)
 return connected(s) and not any(all(tuple(c[j]+(d if j==i else 0) for j in range(3)) in s for i,d in ((0,1),(0,-1),(1,1),(1,-1),(2,1))) for c in s)

def all_catalog(target,n):
 d={}
 for co in combinations(target,n):
  if acceptable(co):d.setdefault(canonical(co),norm(co))
 return list(d.values())

T12=box((3,2,2))
C6=[p for p in all_catalog(T12,6) if is_3d(p)]
print('catalog6',len(C6),flush=True)

def grow(target,n):
 s={R.choice(tuple(target))};ts=set(target)
 while len(s)<n:
  frontier={q for p in s for q in neighbors(p) if q in ts and q not in s}
  if not frontier:return None
  s.add(R.choice(sorted(frontier)))
 return norm(s)

def partition(target,sizes):
 for _ in range(10000):
  rem=set(target);parts=[]
  for sz in sizes[:-1]:
   p=grow(rem,sz)
   # grow returns normalised coords, so grow in original coordinates here.
   start=R.choice(sorted(rem));s={start}
   while len(s)<sz:
    fs={q for c in s for q in neighbors(c) if q in rem and q not in s}
    if not fs:break
    s.add(R.choice(sorted(fs)))
   if len(s)!=sz:break
   parts.append(tuple(sorted(s)));rem-=s
  if len(parts)==len(sizes)-1 and len(rem)==sizes[-1] and connected(rem):
   parts.append(tuple(sorted(rem)))
   if all(acceptable(p) for p in parts):return [norm(p) for p in parts]
 raise RuntimeError('partition failed')

def mutate(p,bounds=None):
 s=set(p);bound=box(bounds) if bounds else None
 for _ in range(2000):
  a=R.choice(sorted(s));rest=s-{a}
  frontier={q for c in rest for q in neighbors(c) if q not in s and (bound is None or q in bound)}
  if not frontier:continue
  q=norm(rest|{R.choice(sorted(frontier))})
  if acceptable(q):return q
 return None

def candidate_pool(shape,count=350,bounds=None):
 d={canonical(shape):norm(shape)};current=norm(shape)
 for _ in range(count*6):
  p=mutate(current,bounds)
  if p:
   if R.random()<.7:current=p
   d.setdefault(canonical(p),p)
  if len(d)>=count:break
 return list(d.values())

def fill(n,target,known,answer,hard=False,identical=False):
 comps=[]
 need=len(target)-sum(map(len,known))
 if need==6:pool=C6
 else:
  # Enumerate residuals of known pieces to construct a valid candidate.
  occupied=set()
  def rec(i,used):
   if i==len(known):
    rem=set(target)-used
    if len(rem)==need and acceptable(rem):comps.append(norm(rem))
    return
   for p in placements(known[i],target):
    if not set(p)&used:rec(i+1,used|set(p))
  rec(0,set())
  assert comps
  good=R.choice(comps)
  pool=candidate_pool(good,count=200,bounds=dims(target))
 valid=[p for p in pool if len(p)==need and solve(known+[p],target)]
 assert valid, (n,'no valid')
 # Prefer chiral answer so a mirror distractor genuinely tests handedness.
 chiral=[p for p in valid if canonical(p)!=canonical(mirror(p)) and not solve(known+[mirror(p)],target)]
 good=R.choice(chiral or valid)
 dims_good=sorted(dims(good));prof=profile(good)
 wrong=[p for p in pool if len(p)==need and canonical(p)!=canonical(good) and (need==4 or sorted(dims(p))==dims_good) and not solve(known+[p],target)]
 R.shuffle(wrong)
 wrong.sort(key=lambda p:(abs(profile(p)['edges']-prof['edges']),abs(profile(p)['squares']-prof['squares']),sum(a!=b for a,b in zip(profile(p)['degrees'],prof['degrees']))))
 m=mirror(good)
 if canonical(m)!=canonical(good) and not solve(known+[m],target):wrong=[m]+[p for p in wrong if canonical(p)!=canonical(m)]
 selected=[]
 for p in wrong:
  if canonical(p) not in {canonical(a) for a in selected}:selected.append(p)
  if len(selected)==3:break
 assert len(selected)==3,(n,'few wrong')
 options=selected[:];options.insert('ABCD'.index(answer),good)
 sol=solve(known+[good],target)[0]
 return {'n':n,'mode':'fill','pieces':known,'options':options,'target':norm(target),'except':False,'answer':answer,'solution':sol,'difficulty':'较难' if hard else '中等','point':'多部件补形' if len(known)>1 else '凹凸互补与空间旋转'}

def union_shapes(parts,bounds=(3,3,2),count=18):
 base=norm(parts[0]);d={}
 for _ in range(40000):
  placed=[base];used=set(base)
  for piece in parts[1:]:
   o=R.choice(orientations(piece))
   # Choose one target contact face to force connected union.
   anchor=R.choice(sorted(used));pc=R.choice(o);axis=R.randrange(3);sg=R.choice((-1,1))
   shift=tuple(anchor[i]+(sg if i==axis else 0)-pc[i] for i in range(3))
   moved=tuple(tuple(c[i]+shift[i] for i in range(3)) for c in o)
   if set(moved)&used:break
   used|=set(moved);placed.append(moved)
  if len(placed)!=len(parts):continue
  t=norm(used)
  if sorted(dims(t))!=sorted(bounds) or not acceptable(t):continue
  d.setdefault(canonical(t),t)
  if len(d)>=count:break
 return list(d.values())

def assemble(n,parts,answer,exc=False,hard=False,bounds=(3,3,2)):
 good=union_shapes(parts,bounds,count=6 if exc else 1)
 assert len(good)>=(3 if exc else 1),(n,'few unions',len(good))
 seed=good[0];pool=candidate_pool(seed,count=250,bounds=dims(seed))
 wrong=[p for p in pool if sorted(dims(p))==sorted(bounds) and not solve(parts,p)]
 R.shuffle(wrong)
 pr=profile(seed)
 wrong.sort(key=lambda p:(abs(profile(p)['edges']-pr['edges']),abs(profile(p)['squares']-pr['squares'])))
 assert len(wrong)>=3
 if exc:
  opts=good[:3];opts.insert('ABCD'.index(answer),wrong[0]);valididx=next(i for i in range(4) if i!='ABCD'.index(answer))
  sol=solve(parts,opts[valididx])[0];solution_for='ABCD'[valididx]
 else:
  opts=wrong[:3];opts.insert('ABCD'.index(answer),seed);sol=solve(parts,seed)[0];solution_for=answer
 return {'n':n,'mode':'assemble','pieces':parts,'options':opts,'except':exc,'answer':answer,'solution':sol,'solution_for':solution_for,'difficulty':'较难' if hard else '中等','point':'多部件相互制约' if len(parts)>2 else ('相同部件的旋转拼合' if canonical(parts[0])==canonical(parts[1]) else '组合轮廓与内部贴合')}

def find_known(target,sizes,seedid=0):
 return partition(target,sizes)[:-1]

Q=[]
Q.append(fill(1,T12,[C6[3]],'C'))
T16=box((4,2,2));known=partition(T16,[8,8])[:-1]
Q.append(fill(2,T16,known,'A'))
Q.append(assemble(3,[C6[7],C6[14]],'D'))
S4=all_catalog(box((2,2,2)),4)
chiral4=next(p for p in S4 if canonical(p)!=canonical(mirror(p)))
Q.append(assemble(4,[chiral4,chiral4],'B',bounds=(3,2,2)))
# Three-piece completion: use 4-cube options, one may be flat; all known parts are genuinely spatial.
for _ in range(100):
 ps=partition(T12,[4,4,4])
 try:
  Q.append(fill(5,T12,ps[:-1],'A'));break
 except (AssertionError,RuntimeError):continue
else:raise RuntimeError('q5')
Q.append(assemble(6,[chiral4,mirror(chiral4),next(p for p in S4 if canonical(p)!=canonical(chiral4) and canonical(p)!=canonical(mirror(chiral4)) and is_3d(p))],'C'))
T18=box((3,3,2));Q.append(fill(7,T18,partition(T18,[9,9])[:-1],'B',hard=True))
Q.append(assemble(8,[C6[20],C6[24]],'D',exc=True,hard=True,bounds=(3,3,2)))
Q.append(fill(9,T18,partition(T18,[6,6,6])[:-1],'C',hard=True))
P15=tuple(c for c in T18 if c[2]==0 or c[0]<2)
parts=partition(P15,[5,5,5]);Q.append(assemble(10,parts,'A',exc=True,hard=True,bounds=(4,3,2)))

for q in Q:
 q['stem']=('从A—D中选出一个部件，与已给部件拼成右侧完整长方体。' if q['mode']=='fill' else ('下列哪项不能由所给全部部件拼成？' if q['except'] else '下列哪项能由所给全部部件拼成？'))
 if q['mode']=='fill':q['stem']+='目标尺寸为'+ '×'.join(map(str,dims(q['target'])))+'个单位格。'
 q['analysis']=[]
 q['option_profiles']=[profile(p) for p in q['options']]
 q['piece_profiles']=[profile(p) for p in q['pieces']]

(ROOT/'puzzles.py').write_text('"""Original spatial assembly models; integer cells, proper rotations only."""\nQUESTIONS = '+pprint.pformat(Q,width=120,sort_dicts=False)+'\n',encoding='utf-8')
print('DONE',[(q['n'],q['mode'],q['answer'],[len(p) for p in q['pieces']]) for q in Q],flush=True)
