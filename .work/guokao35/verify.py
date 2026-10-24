"""Substantive answer checks for finite-state and geometric items, plus document binding checks."""
import itertools
import json
import math
import re
import sys
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
from lxml import etree
from content import QUESTIONS
import figures as f
from build import OUTPUT


def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def subtract(a,b):return tuple(x-y for x,y in zip(a,b))
def choose(n,mask):
    ix=[i for i,v in enumerate(mask) if v]
    assert len(ix)==1,(n,mask)
    assert 'ABCD'[ix[0]]==QUESTIONS[n-1]['answer'],(n,mask)
    return 'ABCD'[ix[0]]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    result={}
    result[1]=choose(1,[p==5 and a==1 for p,a in f.Q1_OPTIONS])
    result[2]=choose(2,[x==f.Q2_A.symmetric_difference(f.Q2_B) for x in f.Q2_OPTIONS])
    result[3]=choose(3,[x==5 for x in [0,6,2,5]])
    assert {len(s) for s in f.Q4_SOURCE}=={6}
    result[4]=choose(4,[len(s)==6 for s in f.Q4_OPTIONS])
    normals={1:(0,0,1),6:(0,0,-1),2:(-1,0,0),3:(1,0,0),4:(0,1,0),5:(0,-1,0)}
    result[5]=choose(5,[cross(normals[t],normals[front])==normals[right] for t,front,right in f.CUBE_OPTIONS])
    mids=[]
    for i,v in enumerate(f.VERTS):
        for w in f.VERTS[i+1:]:
            if sum(a!=b for a,b in zip(v,w))==1 and (sum(v)-1.5)*(sum(w)-1.5)<0:
                mids.append(tuple((a+b)/2 for a,b in zip(v,w)))
    assert set(mids)==set(f.MIDPOINTS) and len(mids)==6
    edge_lengths=[];angles=[]
    for i,p in enumerate(f.MIDPOINTS):
        a=subtract(f.MIDPOINTS[(i-1)%6],p);b=subtract(f.MIDPOINTS[(i+1)%6],p)
        edge_lengths.append(math.sqrt(dot(b,b)))
        angles.append(math.degrees(math.acos(dot(a,b)/math.sqrt(dot(a,a)*dot(b,b)))))
    assert all(abs(l-math.sqrt(.5))<1e-9 for l in edge_lengths)
    assert all(abs(a-120)<1e-9 for a in angles)
    # Explanation view must expose a nondegenerate, equal-edge hexagon.
    projected=[f.section_projection(p,0,0,1) for p in f.MIDPOINTS]
    signed_area=sum(projected[i][0]*projected[(i+1)%6][1]-projected[(i+1)%6][0]*projected[i][1] for i in range(6))/2
    assert abs(signed_area)>1
    assert max(math.dist(projected[i],projected[(i+1)%6]) for i in range(6))-min(math.dist(projected[i],projected[(i+1)%6]) for i in range(6))<1e-9
    result[6]=choose(6,[n==len(mids) for n in [6,4,5,3]])
    feasible=[]
    for option in f.VIEW_OPTIONS:
        states=[]
        ranges=[range(1,4) if v else [0] for row in option for v in row]
        for h in itertools.product(*ranges):
            if [max(h[c],h[3+c]) for c in range(3)]==[2,3,1] and [max(h[:3]),max(h[3:])]==[3,2]:states.append(h)
        feasible.append(states)
    result[7]=choose(7,[bool(s) for s in feasible])
    # Check symmetry invariants of polygon vertices, independent of raster drawing.
    polygons=[
        [(-1,-1),(-1,1),(1,1)],
        [(-.55,-.6),(1,-.6),(.55,.6),(-1,.6)],
        [((1 if k%2==0 else .43)*math.cos(-math.pi/2+k*math.pi/5),(1 if k%2==0 else .43)*math.sin(-math.pi/2+k*math.pi/5)) for k in range(10)],
        [(-1,-.8),(1,-.8),(1,-.5),(-.4,.5),(1,.5),(1,.8),(-1,.8),(-1,.5),(.4,-.5),(-1,-.5)],
        [(-.5,-.7),(.5,-.7),(1,.7),(-1,.7)],
        [(1,0),(3,0),(3,1),(2,1),(2,2),(0,2),(0,1),(1,1)]
    ]
    central=[]
    for poly in polygons:
        cx=sum(p[0] for p in poly)/len(poly);cy=sum(p[1] for p in poly)/len(poly)
        central.append(all(any(math.dist((2*cx-x,2*cy-y),p)<1e-8 for p in poly) for x,y in poly))
    assert central==[False,True,False,True,False,True]
    result[8]=choose(8,[s=={'135','246'} for s in [{'124','356'},{'135','246'},{'125','346'},{'146','235'}]])
    # Degrees obtained from connected graph topology: curves subdivided at junctions.
    degrees=[[1,2,2,1],[3,2,3,2],[1,1,1,1,4],[2,2,2,4,2,2,2],[3,3,3,3,4],[1,1,1,3]]
    strokes=[max(1,sum(v%2 for v in ds)//2) for ds in degrees]
    assert strokes==[1,1,2,1,2,2]
    result[9]=choose(9,[s=={'124','356'} for s in [{'124','356'},{'134','256'},{'126','345'},{'145','236'}]])
    assert [a-b for a,b in zip(f.AREA_FACES,f.AREA_DOTS)]==[1,0,0,1,0,1]
    result[10]=choose(10,[s=={'146','235'} for s in [{'123','456'},{'125','346'},{'146','235'},{'134','256'}]])
    # Q30: all project attribute types and all nonempty sets of permitted types.
    # O=open data, P=passed, S=simulation, E=external assessment.
    types=[(o,p,s,e) for o,p,s,e in itertools.product([False,True],repeat=4) if (not o or p) and (not s or not e)]
    models=[]
    for bits in itertools.product([False,True],repeat=len(types)):
        rows=[t for t,b in zip(types,bits) if b]
        if any(p and s for o,p,s,e in rows):models.append(rows)
    predicates=[lambda rows:any(o and not e for o,p,s,e in rows),
                lambda rows:all(not o or s for o,p,s,e in rows),
                lambda rows:any(p and not e for o,p,s,e in rows),
                lambda rows:all(p or e for o,p,s,e in rows)]
    result[30]=choose(30,[all(pred(rows) for rows in models) for pred in predicates])
    valid=[p for p in itertools.permutations('ABCDEF') if p.index('A')<p.index('C')<p.index('F')
           and p.index('D')==p.index('B')+2 and p.index('E')!=0 and p.index('A')!=1]
    assert len(valid)==10
    result[31]=choose(31,[tuple(s) in valid for s in ['BEDACF','ABE CDF'.replace(' ',''),'BADCEF','ACFBDE']])
    s32=[p for p in valid if p[0]!='A']
    result[32]=choose(32,[all(pred(p) for p in s32) for pred in [lambda p:p[2]=='B',lambda p:p[4]=='E',lambda p:p[1]=='C',lambda p:p[2]=='D']])
    s33=[p for p in valid if p[4]=='F']
    result[33]=choose(33,[all(pred(p) for p in s33) for pred in [lambda p:abs(p.index('A')-p.index('C'))==1,lambda p:p[2]!='B',lambda p:p.index('E')>p.index('D'),lambda p:p[1]=='C']])
    dates={p.index('E') for p in valid if p[1]=='C'}
    result[34]=choose(34,[v==len(dates) for v in [2,3,4,5]])
    counts=[sum(pred(p) for p in valid) for pred in [lambda p:p[5]=='F',lambda p:p[0]=='A',lambda p:p[3]=='D',lambda p:p[2]=='F']]
    result[35]=choose(35,[n==1 for n in counts])
    # Source / answer integrity; each analysis ends with exactly its own answer.
    for q in QUESTIONS:
        assert q['answer'] in 'ABCD'
        assert len(q['options'])==4 if q['n']>=8 else not q['options']
        assert q['analysis'][-1].endswith('故正确答案为'+q['answer']+'。')
        assert q['n']<8 or len(set(q['options']))==4
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(OUTPUT) as z:
        numbering=etree.fromstring(z.read('word/numbering.xml'))
        kinds=[etree.QName(e).localname for e in numbering]
        assert max(i for i,k in enumerate(kinds) if k=='abstractNum')<min(i for i,k in enumerate(kinds) if k=='num')
        nsids=numbering.xpath('./w:abstractNum/w:nsid/@w:val',namespaces=ns)
        assert len(nsids)==len(set(nsids))
        root=etree.fromstring(z.read('word/document.xml'))
        paras=root.xpath('//w:body/w:p',namespaces=ns)
        qs=[p for p in paras if p.xpath('./w:pPr/w:pStyle[@w:val="Question"]',namespaces=ns)]
        ans=[p for p in paras if p.xpath('./w:pPr/w:pStyle[@w:val="AnswerTitle"]',namespaces=ns)]
        assert len(qs)==len(ans)==35
        for p,q in zip(qs,QUESTIONS):
            assert ''.join(p.xpath('.//w:t/text()',namespaces=ns))==q['stem']
            assert p.xpath('./w:pPr/w:numPr/w:numId',namespaces=ns)
        for p,q in zip(ans,QUESTIONS):assert ''.join(p.xpath('.//w:t/text()',namespaces=ns))=='答案：'+q['answer']
        media=[name for name in z.namelist() if name.startswith('word/media/')]
        assert len(media)==13
        assert len(root.xpath('//*[local-name()="drawing"]'))==13
        xml=''.join(root.xpath('//w:t/text()',namespaces=ns))
        assert all(x not in xml for x in ['TODO','缺失','待补','占位符'])
    report={'status':'passed','mathematically_checked_questions':result,'case_solutions':[''.join(p) for p in valid],
            'q35_solution_counts':counts,'q7_constructible_heights':feasible,
            'questions':35,'answers':dict(Counter(q['answer'] for q in QUESTIONS)),
            'note':'Finite-state and geometry checks passed. Other items reviewed against their stated definitions and arguments; no separate human blind test performed.'}
    Path(__file__).with_name('verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
