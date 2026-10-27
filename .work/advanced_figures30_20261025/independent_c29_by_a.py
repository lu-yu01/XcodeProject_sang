"""Independent visual reconstruction for C29 blind review.

Coordinates below were read from q29.png, without opening the author's code,
answer, or model. This solver is separately written by reviewer A.
"""
from itertools import permutations,product
from math import prod
import json
from pathlib import Path

T={(x,y,z) for x in range(3) for y in range(3) for z in range(2)}
TB={(0,0,0),(2,1,1),(1,2,1)}
P1={(0,0,0),(0,1,0),(2,1,0),(0,1,1),(1,1,1),(2,1,1)}
B1={(2,1,0)}
P2={(0,0,0),(1,0,0),(1,1,0),(1,2,0),(0,1,1),(1,1,1)}
B2={(0,1,1)}
P3={(0,0,1),(1,0,1),(2,0,1),(2,1,1),(2,0,0),(2,1,0)}
OPTIONS=[{(2,1,0)},{(1,0,1)},{(2,1,1)},{(2,0,0)}]
def parity(p):return (-1)**sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))
ROTS=[(p,s) for p in permutations(range(3)) for s in product([-1,1],repeat=3) if parity(p)*prod(s)==1]
assert len(ROTS)==24
def placements(P,B):
    out={}
    for p,s in ROTS:
        rotate=lambda q:tuple(q[p[i]]*s[i] for i in range(3))
        Q={rotate(q) for q in P};C={rotate(q) for q in B}
        lo=tuple(min(q[i] for q in Q) for i in range(3))
        Q={tuple(q[i]-lo[i] for i in range(3)) for q in Q}
        C={tuple(q[i]-lo[i] for i in range(3)) for q in C}
        hi=tuple(max(q[i] for q in Q) for i in range(3))
        for sh in product(range(3-hi[0]),range(3-hi[1]),range(2-hi[2])):
            R={tuple(q[i]+sh[i] for i in range(3)) for q in Q}
            D={tuple(q[i]+sh[i] for i in range(3)) for q in C}
            if R<=T and (R&TB)==D:out[tuple(sorted(R))]=R
    return list(out.values())
def solve():
    first=placements(P1,B1);second=placements(P2,B2);report={}
    for letter,black in zip('ABCD',OPTIONS):
        third=placements(P3,black);solutions=[]
        for a in first:
            for b in second:
                if a&b:continue
                for c in third:
                    if not (a|b)&c and (a|b|c)==T:solutions.append([sorted(a),sorted(b),sorted(c)])
        report[letter]={'solution_count':len(solutions),'placements':len(third),'example':solutions[0] if solutions else None}
    return report
if __name__=='__main__':
    result=solve()
    (Path(__file__).parent/'independent_c29_by_a.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v['solution_count'] for k,v in result.items()}))
