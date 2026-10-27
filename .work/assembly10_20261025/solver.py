"""Exact polycube assembly under the 24 proper rotations of the cube."""
from itertools import permutations, product

def parity(p):
    return (-1)**sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))

ROTATIONS=tuple((p,s) for p in permutations(range(3)) for s in product((-1,1),repeat=3) if parity(p)*s[0]*s[1]*s[2]==1)
assert len(ROTATIONS)==24

def norm(cells):
    cells=tuple(cells)
    lo=tuple(min(c[i] for c in cells) for i in range(3))
    return tuple(sorted(tuple(c[i]-lo[i] for i in range(3)) for c in cells))

def rotate(cells, r):
    p,s=r
    return norm(tuple(tuple(s[i]*c[p[i]] for i in range(3)) for c in cells))

def orientations(cells):
    return tuple(sorted({rotate(cells,r) for r in ROTATIONS}))

def canonical(cells):
    return min(orientations(cells))

def dims(cells):
    q=norm(cells)
    return tuple(max(c[i] for c in q)+1 for i in range(3))

def neighbors(c):
    for i in range(3):
        for d in (-1,1):
            p=list(c);p[i]+=d;yield tuple(p)

def connected(cells):
    unseen=set(cells);todo=[unseen.pop()]
    while todo:
        p=todo.pop()
        for q in neighbors(p):
            if q in unseen:unseen.remove(q);todo.append(q)
    return not unseen

def edges(cells):
    s=set(cells)
    return sum(q in s for p in s for q in neighbors(p))//2

def placements(piece,target):
    target=set(target);td=dims(target)
    result=set()
    for o in orientations(piece):
        pd=dims(o)
        for shift in product(*(range(td[i]-pd[i]+1) for i in range(3))):
            moved=tuple(sorted(tuple(c[i]+shift[i] for i in range(3)) for c in o))
            if set(moved)<=target:result.add(moved)
    return tuple(sorted(result))

def solve(pieces,target,limit=1):
    """Returns exact tilings in original piece order (rotations only, no reflections)."""
    target=norm(target)
    if sum(map(len,pieces))!=len(target):return []
    ids={c:i for i,c in enumerate(target)}
    full=(1<<len(target))-1
    candidates=[]
    for piece in pieces:
        pp=placements(piece,target)
        candidates.append(tuple((sum(1<<ids[c] for c in p),p) for p in pp))
        if not pp:return []
    results=[];chosen=[None]*len(pieces)
    def dfs(rem,used):
        if len(results)>=limit:return
        if not rem:
            if used==full:results.append(list(chosen))
            return
        valid={i:[(m,p) for m,p in candidates[i] if not m&used] for i in rem}
        if any(not v for v in valid.values()):return
        # Choose the uncovered target cell with fewest feasible covering placements.
        holes=[j for j in range(len(target)) if not used>>j&1]
        options=min(([(i,m,p) for i in rem for m,p in valid[i] if m>>j&1] for j in holes),key=len)
        for i,m,p in options:
            chosen[i]=p;dfs(tuple(k for k in rem if k!=i),used|m)
    dfs(tuple(range(len(pieces))),0)
    return results

def layers(cells):
    cells=norm(cells);dx,dy,dz=dims(cells);s=set(cells)
    return ['/'.join(''.join('1' if (x,y,z) in s else '0' for x in range(dx)) for y in range(dy)) for z in range(dz)]

def mirror(cells):
    return norm([(-x,y,z) for x,y,z in cells])

def is_3d(cells):
    return all(min(dims(o))>1 for o in orientations(cells))
