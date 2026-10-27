"""Exact coloured polycube assembly using proper rotations only."""
from itertools import permutations,product

def parity(p):return (-1)**sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))
ROTATIONS=tuple((p,s) for p in permutations(range(3)) for s in product((-1,1),repeat=3) if parity(p)*s[0]*s[1]*s[2]==1)
assert len(ROTATIONS)==24

def norm(cells):
 cells=tuple(cells);lo=tuple(min(c[i] for c in cells) for i in range(3))
 return tuple(sorted(tuple(c[i]-lo[i] for i in range(3)) for c in cells))

def normalize(part):
 cells=tuple(part['cells']);lo=tuple(min(c[i] for c in cells) for i in range(3))
 return {'cells':tuple(sorted(tuple(c[i]-lo[i] for i in range(3)) for c in cells)), 'black':tuple(sorted(tuple(c[i]-lo[i] for i in range(3)) for c in part['black']))}

def rotate(part,r):
 p,s=r
 return normalize({k:tuple(tuple(s[i]*c[p[i]] for i in range(3)) for c in part[k]) for k in ('cells','black')})

def orientations(part,coloured=True):
 seen={}
 for r in ROTATIONS:
  q=rotate(part,r);key=(q['cells'],q['black']) if coloured else q['cells']
  seen.setdefault(key,q)
 return tuple(seen.values())

def canonical(part,coloured=True):
 return min((p['cells'],p['black']) if coloured else p['cells'] for p in orientations(part,coloured))

def dims(cells):
 return tuple(max(c[i] for c in cells)-min(c[i] for c in cells)+1 for i in range(3))

def neighbors(c):
 for i in range(3):
  for d in (-1,1):
   q=list(c);q[i]+=d;yield tuple(q)

def connected(cells):
 unseen=set(cells);todo=[unseen.pop()]
 while todo:
  for q in neighbors(todo.pop()):
   if q in unseen:unseen.remove(q);todo.append(q)
 return not unseen

def edges(cells):
 s=set(cells);return sum(n in s for c in s for n in neighbors(c))//2

def placements(part,target,coloured=True):
 target=normalize(target);ts=set(target['cells']);tb=set(target['black']);td=dims(ts);found={}
 for o in orientations(part,coloured):
  pd=dims(o['cells'])
  for shift in product(*(range(td[i]-pd[i]+1) for i in range(3))):
   q={k:tuple(sorted(tuple(c[i]+shift[i] for i in range(3)) for c in o[k])) for k in ('cells','black')}
   qs=set(q['cells']);qb=set(q['black'])
   if not qs<=ts:continue
   if coloured and qb!=qs&tb:continue
   key=(q['cells'],q['black']) if coloured else q['cells'];found.setdefault(key,q)
 return tuple(found.values())

def solve(parts,target,coloured=True,limit=1):
 target=normalize(target)
 if sum(len(p['cells']) for p in parts)!=len(target['cells']):return []
 if coloured and sum(len(p['black']) for p in parts)!=len(target['black']):return []
 ids={c:i for i,c in enumerate(target['cells'])};full=(1<<len(ids))-1
 pp=[]
 for part in parts:
  options=tuple((sum(1<<ids[c] for c in q['cells']),q) for q in placements(part,target,coloured))
  if not options:return []
  pp.append(options)
 out=[];chosen=[None]*len(parts)
 def dfs(rem,used):
  if len(out)>=limit:return
  if not rem:
   if used==full:out.append(list(chosen))
   return
  valid={i:[(m,q) for m,q in pp[i] if not m&used] for i in rem}
  if any(not v for v in valid.values()):return
  holes=[j for j in range(len(ids)) if not used>>j&1]
  options=min(([(i,m,q) for i in rem for m,q in valid[i] if m>>j&1] for j in holes),key=len)
  for i,m,q in options:
   chosen[i]=q;dfs(tuple(k for k in rem if k!=i),used|m)
 dfs(tuple(range(len(parts))),0)
 return out

def mirror(part):return normalize({k:tuple((-c[0],c[1],c[2]) for c in part[k]) for k in ('cells','black')})

def layer_rows(part):
 q=normalize(part);dx,dy,dz=dims(q['cells']);s=set(q['cells']);b=set(q['black'])
 return ['/'.join(''.join('黑' if (x,y,z) in b else '白' if (x,y,z) in s else '·' for x in range(dx)) for y in range(dy)) for z in range(dz)]
