"""Original spatial and classification diagrams Q13–27, with exact models."""
from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
from itertools import combinations, permutations, product
import math
import random

import drawkit as k

QUESTIONS = []
CHECKS = {}


def neg(v): return tuple(-x for x in v)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b): return sum(x*y for x,y in zip(a,b))


def fold(cells):
    """Normals and two in-face axes after folding the printed side outward."""
    cells=set(cells)
    start=min(cells); out={start:((0,0,1),(0,-1,0),(1,0,0))};queue=deque([start])
    while queue:
        r,c=queue.popleft();n,u,v=out[r,c]
        for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nxt=r+dr,c+dc
            if nxt not in cells:continue
            if dr==-1:new=(u,neg(n),v)
            elif dr==1:new=(neg(u),n,v)
            elif dc==-1:new=(neg(v),u,n)
            else:new=(v,u,neg(n))
            if nxt in out:
                if out[nxt]!=new:return None
            else:out[nxt]=new;queue.append(nxt)
    return out if len(out)==6 and len({a[0] for a in out.values()})==6 else None


def spatial(n,height=920):
    im,d=k.canvas(height)
    d.rectangle((70,35,1730,435),outline=k.BLACK,width=5)
    opts=k.options(d,525,height-95)
    k.LAYOUTS[n]={'kind':'spatial_framed','stem_box':(70,35,1730,435),'option_centers':opts}
    return im,d,opts


def cube(d,cx,cy,labels,scale=95,arrow=None):
    """The displayed left lower face is front; right lower face is right."""
    top=(cx,cy-1.12*scale);left=(cx-scale,cy-.51*scale)
    right=(cx+scale,cy-.51*scale);center=(cx,cy+.10*scale)
    ll=(cx-scale,cy+.51*scale);rr=(cx+scale,cy+.51*scale);bottom=(cx,cy+1.12*scale)
    faces=[(top,left,center,right),(left,ll,bottom,center),(center,bottom,rr,right)]
    for points in faces:
        d.polygon(points,fill='white');d.line(list(points)+[points[0]],fill=k.BLACK,width=5,joint='curve')
    centers=[(cx,cy-.51*scale),(cx-.45*scale,cy+.37*scale),(cx+.45*scale,cy+.37*scale)]
    for center_,s in zip(centers,labels):
        if s:k.label(d,*center_,s,42)
    if arrow is not None:
        # Direction along the top face, towards front/right/back/left edge.
        vx,vy=[(-.77,.47),(.77,.47),(.77,-.47),(-.77,-.47)][arrow]
        x,y=centers[0];length=scale*.70
        a=(x-vx*length*.45,y-vy*length*.45);b=(x+vx*length*.45,y+vy*length*.45)
        d.line((*a,*b),fill=k.BLACK,width=6)
        norm=math.hypot(vx,vy);vx/=norm;vy/=norm;px,py=-vy,vx
        d.polygon([(b[0]+vx*9,b[1]+vy*9),(b[0]-vx*18+px*11,b[1]-vy*18+py*11),(b[0]-vx*18-px*11,b[1]-vy*18-py*11)],fill=k.BLACK)


def net(d,cx,cy,cells,labels=None,marks=None,unit=65,arrow_cell=None,arrow_angle=0):
    lo_r=min(r for r,c in cells);hi_r=max(r for r,c in cells)
    lo_c=min(c for r,c in cells);hi_c=max(c for r,c in cells)
    x0=cx-(hi_c-lo_c+1)*unit/2;y0=cy-(hi_r-lo_r+1)*unit/2
    for r,c in cells:
        x=x0+(c-lo_c)*unit;y=y0+(r-lo_r)*unit
        d.rectangle((x,y,x+unit,y+unit),fill='white',outline=k.BLACK,width=4)
        px,py=x+unit/2,y+unit/2
        if labels and (r,c) in labels:k.label(d,px,py,labels[r,c],int(unit*.48))
        if marks and (r,c) in marks:d.ellipse((px-9,py-9,px+9,py+9),fill=k.BLACK)
        if (r,c)==arrow_cell:k.arrow(d,px,py,arrow_angle,unit*.62,5)


NET13={(1,0):'1',(1,1):'2',(1,2):'3',(1,3):'4',(0,1):'5',(2,2):'6'}
OR13=fold(NET13)
N13={value:OR13[cell][0] for cell,value in NET13.items()}
def view_valid(triple,normals):return cross(normals[triple[0]],normals[triple[1]])==normals[triple[2]]
GOOD13=next(t for t in permutations('123456',3) if view_valid(t,N13))
BAD13=[t for t in permutations('123456',3) if not view_valid(t,N13) and t!=GOOD13][:3]
# Explicitly mix an opposite-face error with mirror-order errors.
OP13=[GOOD13,BAD13[2],BAD13[0],BAD13[1]]


def draw13():
    im,d,opts=spatial(13)
    net(d,850,235,NET13,NET13,unit=78)
    for center,t in zip(opts,OP13):cube(d,*center,t,94)
    k.save(im,13)


NORMALS=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
VIEWS14=[('1','2','3'),('1','4','5')]
CASES14=[]
for values in permutations('123456'):
    normals=dict(zip(values,NORMALS))
    if all(view_valid(v,normals) for v in VIEWS14):CASES14.append(normals)
OP14=[('2','3'),('3','4'),('1','6'),('2','5')]
FLAGS14=[all(case[a]==neg(case[b]) for case in CASES14) for a,b in OP14]


def draw14():
    im,d,opts=spatial(14,870)
    cube(d,650,235,VIEWS14[0],115);cube(d,1150,235,VIEWS14[1],115)
    for center,pair in zip(opts,OP14):
        x,y=center
        for j,s in enumerate(pair):
            xx=x+(j-.5)*115
            d.rectangle((xx-45,y-45,xx+45,y+45),outline=k.BLACK,width=5)
            k.label(d,xx,y,s,48)
        k.label(d,x,y+78,'相对',31)
    k.save(im,14)


NET15={(0,0),(1,0),(2,0),(2,1),(3,1),(4,1)}
OR15=fold(NET15)
if OR15 is None: # Alternate 6-square net with two different side attachments.
    NET15={(0,1),(1,1),(2,1),(3,1),(1,0),(2,2)};OR15=fold(NET15)
AR15=min(NET15)
NA15,UP15,_=OR15[AR15]
FR15=next(cell for cell,value in OR15.items() if value[0]==UP15)
RI15=next(cell for cell,value in OR15.items() if value[0]==cross(NA15,UP15))
LAB15={FR15:'●',RI15:'◇'}
OP15=[1,2,3,0]


def draw15():
    im,d,opts=spatial(15,980)
    net(d,850,235,NET15,LAB15,unit=65,arrow_cell=AR15)
    for center,a in zip(opts,OP15):cube(d,*center,('', '●','◇'),96,arrow=a)
    k.save(im,15)


CUBE_VERTS=list(product((Fraction(0),Fraction(1)),repeat=3))
CUBE_EDGES=[(a,b) for a,b in combinations(CUBE_VERTS,2) if sum(x!=y for x,y in zip(a,b))==1]
def section_points(normal,constant):
    result=set()
    for a,b in CUBE_EDGES:
        va=dot(a,normal)-constant;vb=dot(b,normal)-constant
        if va==0:result.add(a)
        if vb==0:result.add(b)
        if va*vb<0:
            t=va/(va-vb);result.add(tuple(x+t*(y-x) for x,y in zip(a,b)))
    return result
SEC16=section_points((2,1,1),Fraction(3,2))


def cube_wire(d,cx,cy,scale=240):
    def p(v):
        x,y,z=v;return(cx+scale*(float(x)+.43*float(y)-.65),cy-scale*(float(z)+.35*float(y)-.65))
    labels={'A':(0,0,0),'B':(1,0,0),'C':(1,1,0),'D':(0,1,0),'E':(0,0,1),'F':(1,0,1),'G':(1,1,1),'H':(0,1,1)}
    for a,b in CUBE_EDGES:d.line((*p(a),*p(b)),fill=k.GRAY,width=4)
    for name,v in labels.items():
        x,y=p(v);dx=-17 if v[0]==0 else 18;dy=18 if v[2]==0 else -18
        if name=='F':dy=14
        k.label(d,x+dx,y+dy,name,29)
    for name,v in [('P',(Fraction(3,4),0,0)),('Q',(0,1,Fraction(1,2))),('R',(0,Fraction(1,2),1))]:
        x,y=p(v);d.ellipse((x-8,y-8,x+8,y+8),fill=k.BLACK)
        dx,dy={'P':(4,30),'Q':(-28,0),'R':(-18,-27)}[name];k.label(d,x+dx,y+dy,name,34)


def draw16():
    im,d,opts=spatial(16,900)
    cube_wire(d,850,235,220)
    for center,sides in zip(opts,(3,4,5,6)):k.polygon(d,*center,sides,82)
    k.save(im,16)


def paper_grid(d,cx,cy,rows,cols,cuts=(),unit=28,outer=4):
    x0=cx-cols*unit/2;y0=cy-rows*unit/2
    for r in range(rows):
        for c in range(cols):
            d.rectangle((x0+c*unit,y0+r*unit,x0+(c+1)*unit,y0+(r+1)*unit),fill='#777777' if (r,c) in cuts else 'white',outline='#bbbbbb',width=1)
    d.rectangle((x0,y0,x0+cols*unit,y0+rows*unit),outline=k.BLACK,width=outer)


CUT17={(2,2),(2,3),(3,2),(3,3)}
OP17=[{(0,0),(0,5),(5,0),(5,5)},CUT17,{(1,2),(1,3),(4,2),(4,3)},{(2,0),(3,0),(2,5),(3,5)}]


def draw17():
    im,d,opts=spatial(17,900)
    for cx,rows,cols,cuts,txt in [(450,6,6,set(),'原纸'),(900,6,3,set(),'左半向右折'),(1330,3,3,{(2,0)},'下半向上折后剪去灰格')]:
        paper_grid(d,cx,215,rows,cols,cuts,unit=36)
        k.label(d,cx,385,txt,31)
    k.arrow(d,675,210,1,85);k.arrow(d,1115,210,1,85)
    for center,cuts in zip(opts,OP17):paper_grid(d,*center,6,6,cuts,unit=30)
    k.save(im,17)


FR18=(3,2,3);RI18=(2,3,1)
MASK18={(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,2)}
def stack_cases(mask,front,right):
    cells=sorted(mask)
    for values in product(*(range(1,min(front[c],right[r])+1) for r,c in cells)):
        h=dict(zip(cells,values))
        if tuple(max((h.get((r,c),0) for r in range(3)),default=0) for c in range(3))!=tuple(front):continue
        if tuple(max((h.get((r,c),0) for c in range(3)),default=0) for r in range(3))!=tuple(right):continue
        yield h
CASES18=list(stack_cases(MASK18,FR18,RI18));MIN18=min(sum(x.values()) for x in CASES18)
WIT18=next(x for x in CASES18 if sum(x.values())==MIN18)
OP18=[MIN18-2,MIN18-1,MIN18+1,MIN18]


def elevation(d,cx,cy,heights,unit=48):
    x0=cx-len(heights)*unit/2;baseline=cy+max(heights)*unit/2
    for c,h in enumerate(heights):
        for z in range(h):
            d.rectangle((x0+c*unit,baseline-(z+1)*unit,x0+(c+1)*unit,baseline-z*unit),fill='#dddddd',outline=k.BLACK,width=3)


def draw18():
    im,d,opts=spatial(18,850)
    elevation(d,470,215,FR18,57);elevation(d,900,215,RI18,57)
    k.grid(d,1350,215,MASK18,n=3,size=180)
    for x,t in [(470,'正视图'),(900,'右视图'),(1350,'俯视占位图')]:k.label(d,x,380,t,32)
    for center,value in zip(opts,OP18):k.label(d,*center,f'{value}个',56)
    k.save(im,18)


HEIGHT19=((3,1,2),(0,1,0),(2,2,0))
LAYERS19=[{(r,c) for r in range(3) for c in range(3) if HEIGHT19[r][c]>=level} for level in (1,2,3)]
RIGHT19=tuple(max(row) for row in HEIGHT19)
OP19=[(3,2,1),(1,2,3),RIGHT19,(2,1,3)]


def draw19():
    im,d,opts=spatial(19,900)
    for i,cells in enumerate(LAYERS19):
        x=460+i*440;k.grid(d,x,215,cells,n=3,size=190)
        k.label(d,x,370,f'第{i+1}层',33)
        k.label(d,x,81,'前',26)
    for center,heights in zip(opts,OP19):elevation(d,*center,heights,52)
    k.save(im,19)


PIECE20_A={(0,0),(1,0),(2,0),(2,1)}
PIECE20_B={(0,0),(0,1),(1,1),(1,2)}
def normalize(cells):
    mr=min(r for r,c in cells);mc=min(c for r,c in cells)
    return frozenset((r-mr,c-mc) for r,c in cells)
def rotate_poly(cells):return normalize({(c,-r) for r,c in cells})
def rotations_poly(cells):
    out=set();cells=normalize(cells)
    for _ in range(4):out.add(cells);cells=rotate_poly(cells)
    return out
def tilings20(target):
    target=set(target)
    for a in rotations_poly(PIECE20_A):
        for dr in range(3):
            for dc in range(4):
                placed={(r+dr,c+dc) for r,c in a}
                if placed<=target and normalize(target-placed) in rotations_poly(PIECE20_B):
                    yield placed,target-placed
def connected(cells):
    seen={next(iter(cells))};queue=list(seen)
    for r,c in queue:
        for nxt in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
            if nxt in cells and nxt not in seen:seen.add(nxt);queue.append(nxt)
    return len(seen)==len(cells)
ALL20=[]
for comb in combinations(product(range(3),range(4)),8):
    cells=set(comb)
    if connected(cells) and normalize(cells)==frozenset(cells):ALL20.append(cells)
GOOD20=[x for x in ALL20 if next(tilings20(x),None)]
BAD20=[x for x in ALL20 if not next(tilings20(x),None)]
OP20=[GOOD20[len(GOOD20)//2],BAD20[7],BAD20[len(BAD20)//2],BAD20[-8]]
WIT20=next(tilings20(OP20[0]))


def poly_cells(d,cx,cy,cells,unit=45):
    lo_r=min(r for r,c in cells);hi_r=max(r for r,c in cells);lo_c=min(c for r,c in cells);hi_c=max(c for r,c in cells)
    x0=cx-(hi_c-lo_c+1)*unit/2;y0=cy-(hi_r-lo_r+1)*unit/2
    for r,c in cells:
        x=x0+(c-lo_c)*unit;y=y0+(r-lo_r)*unit
        d.rectangle((x,y,x+unit,y+unit),fill='#d4d4d4',outline=k.BLACK,width=3)


def draw20():
    im,d,opts=spatial(20,900)
    poly_cells(d,650,225,PIECE20_A,65);poly_cells(d,1150,225,PIECE20_B,65)
    k.label(d,650,385,'部件甲',33);k.label(d,1150,385,'部件乙',33)
    for center,cells in zip(opts,OP20):poly_cells(d,*center,cells,65)
    k.save(im,20)


HOLE21={(sx*a,sy*b) for a,b in ((1,2),(2,1)) for sx,sy in product((-1,1),repeat=2)}
OP21=[{(sx*1,sy*2) for sx,sy in product((-1,1),repeat=2)},HOLE21,
      {(sx*a,sy*b) for a,b in ((1,1),(2,2)) for sx,sy in product((-1,1),repeat=2)},
      {(sx*a,sy*b) for a,b in ((1,2),(2,2)) for sx,sy in product((-1,1),repeat=2)}]


def holed_square(d,cx,cy,holes,unit=27):
    d.rectangle((cx-3*unit,cy-3*unit,cx+3*unit,cy+3*unit),outline=k.BLACK,width=4)
    for x,y in holes:
        px=cx+x*unit;py=cy-y*unit
        d.ellipse((px-7,py-7,px+7,py+7),fill='white',outline=k.BLACK,width=3)


def draw21():
    im,d,opts=spatial(21,930)
    # Three folds: right to left, upper to lower, then the part below y=x to its left.
    starts=[350,720,1090,1450]
    shapes=[((-120,-120),(120,-120),(120,120),(-120,120)),((-120,-120),(0,-120),(0,120),(-120,120)),((-120,0),(0,0),(0,120),(-120,120)),((-120,0),(-120,120),(0,0))]
    for i,(cx,shape) in enumerate(zip(starts,shapes)):
        d.polygon([(cx+x,210+y) for x,y in shape],fill='white',outline=k.BLACK,width=4)
        if i<3:k.arrow(d,cx+185,215,1,75)
    k.label(d,350,385,'原纸',29);k.label(d,720,385,'右半向左折',29);k.label(d,1090,385,'上半向下折',29);k.label(d,1450,385,'沿斜线再对折',29)
    d.line((970,330,1090,210),fill=k.GRAY,width=3)
    # Last triangle point corresponds to x=-2,y=-1 in original centred coordinates.
    px,py=1450-80,210+40
    d.ellipse((px-8,py-8,px+8,py+8),fill='white',outline=k.BLACK,width=3)
    for center,holes in zip(opts,OP21):holed_square(d,*center,holes,29)
    k.save(im,21)


def symmetry_flags(cells,n=5):
    t=[{(r,n-1-c) for r,c in cells},{(n-1-r,c) for r,c in cells},
       {(c,r) for r,c in cells},{(n-1-c,n-1-r) for r,c in cells}]
    return tuple(x==cells for x in t),{(n-1-r,n-1-c) for r,c in cells}==cells
def make_symmetry_patterns():
    rng=random.Random(22026);axis=[];central=[];seen=set()
    while len(axis)<3 or len(central)<3:
        cells=set(rng.sample(list(product(range(5),repeat=2)),10))
        flags,centre=symmetry_flags(cells)
        key=frozenset(cells)
        if key in seen:continue
        if sum(flags)==1 and not centre and len(axis)<3:axis.append(cells);seen.add(key)
        if not any(flags) and centre and len(central)<3:central.append(cells);seen.add(key)
    return [axis[0],central[0],axis[1],central[1],central[2],axis[2]]
PAT22=make_symmetry_patterns()
PART22=({0,2,5},{1,3,4})


def draw22():
    im,d,centers=k.classification(22)
    for center,cells in zip(centers,PAT22):k.grid(d,*center,cells,n=5,size=210)
    k.save(im,22)


BASE23=({(0,0),(0,1),(1,1),(1,3),(2,1),(2,2),(3,2),(4,2)},(4,4))
def motif_rot(state):return k.rotate(state[0],5),next(iter(k.rotate({state[1]},5)))
def motif_mirror(state):return k.reflect(state[0],5),next(iter(k.reflect({state[1]},5)))
def motif_key(state):return frozenset(state[0]),state[1]
MIR23=motif_mirror(BASE23)
STATES23=[BASE23,MIR23,motif_rot(MIR23),motif_rot(BASE23),motif_rot(motif_rot(BASE23)),motif_rot(motif_rot(MIR23))]
PART23=({0,3,4},{1,2,5})


def draw23():
    im,d,centers=k.classification(23)
    for center,state in zip(centers,STATES23):k.grid(d,*center,state[0],n=5,size=210,dots={state[1]})
    k.save(im,23)


POLY24_A=[(-1.15,-.75),(.35,-.75),(.35,.75),(-1.15,.75)]
POLY24_B=[(.35,-1.05),(1.4,0),(.35,1.05),(-.7,0)]
DOT24_IN=(0,0);DOT24_OUT=(-.95,.45)
FLAGS24=[True,True,False,False,True,False]
PART24=({0,1,4},{2,3,5})
def contains(poly,p):
    x,y=p;inside=False
    for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:inside=not inside
    return inside


def draw24():
    im,d,centers=k.classification(24)
    for i,((cx,cy),flag) in enumerate(zip(centers,FLAGS24)):
        angle=i*math.pi/3
        def p(point):
            x,y=point;return(cx+(x*math.cos(angle)-y*math.sin(angle))*76,cy+(x*math.sin(angle)+y*math.cos(angle))*76)
        for poly in (POLY24_A,POLY24_B):
            points=[p(v) for v in poly];d.line(points+[points[0]],fill=k.BLACK,width=5)
        for point,solid in [(DOT24_IN,flag),(DOT24_OUT,not flag)]:
            x,y=p(point);d.ellipse((x-9,y-9,x+9,y+9),fill=k.BLACK if solid else 'white',outline=k.BLACK,width=3)
    k.save(im,24)


def component_sizes(cells):
    unseen=set(cells);result=[]
    while unseen:
        start=unseen.pop();queue=[start];size=1
        for r,c in queue:
            for nxt in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if nxt in unseen:unseen.remove(nxt);queue.append(nxt);size+=1
        result.append(size)
    return sorted(result)
def make_components():
    rng=random.Random(25026);pools={2:[],3:[]}
    while any(len(v)<3 for v in pools.values()):
        cells=set(rng.sample(list(product(range(5),repeat=2)),8));sizes=component_sizes(cells)
        if len(sizes) in pools and min(sizes)>=2 and len(pools[len(sizes)])<3:pools[len(sizes)].append(cells)
    return [pools[2][0],pools[3][0],pools[3][1],pools[2][1],pools[2][2],pools[3][2]]
PAT25=make_components();PART25=({0,3,4},{1,2,5})


def draw25():
    im,d,centers=k.classification(25)
    for center,cells in zip(centers,PAT25):k.grid(d,*center,cells,n=5,size=210)
    k.save(im,25)


def canonical_poly(cells):
    keys=[]
    for mirror in (False,True):
        base={(r,-c) if mirror else (r,c) for r,c in cells}
        keys.extend(tuple(sorted(x)) for x in rotations_poly(base))
    return min(keys)
def cube_nets():
    shapes={((0,0),)}
    for length in range(2,7):
        grown=set()
        for shape in shapes:
            cells=set(shape)
            for r,c in cells:
                for p in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                    if p not in cells:grown.add(canonical_poly(cells|{p}))
        shapes=grown
    return [set(x) for x in sorted(shapes) if fold(x)]
NETS26=cube_nets()[:6]
OPPOSITE26=[True,False,True,True,False,False]
MARKS26=[]
for cells,want in zip(NETS26,OPPOSITE26):
    ori=fold(cells)
    MARKS26.append(next(set(pair) for pair in combinations(sorted(cells),2)
                        if (ori[pair[0]][0]==neg(ori[pair[1]][0]))==want
                        and (want or sum(abs(a-b) for a,b in zip(*pair))>1)))
PART26=({0,2,3},{1,4,5})


def draw26():
    im,d,centers=k.classification(26)
    for center,cells,marks in zip(centers,NETS26,MARKS26):net(d,*center,cells,marks=marks,unit=45)
    k.save(im,26)


TRIPLES27=[('1','2','3'),('1','3','2'),('2','3','1'),('2','1','3'),('3','2','1'),('3','1','2')]
PART27=({0,2,5},{1,3,4})


def draw27():
    im,d,centers=k.classification(27)
    for center,triple in zip(centers,TRIPLES27):cube(d,*center,triple,93)
    k.save(im,27)


def add(n,stem,answer,point,analysis,options=None,level='中等'):
    QUESTIONS.append(k.question(n,stem,answer,point,analysis,options=options,level=level))


add(13,'图示为某立方体的外表面展开图，数字仅作为面标签，不考查数字自身朝向。下列哪一立方体可以由它折成？','A','展开图：相对面与三面绕序',[
    '先沿共边折起展开图，确定六个面朝向；再核对选项中上、前、右三个面的邻接和绕序。两面相邻只是必要条件，三面若形成镜像次序也不能靠转动实现。',
    f'相对面为1与3、2与4、5与6。由展开图可构造上面{GOOD13[0]}、前面{GOOD13[1]}、右面{GOOD13[2]}的实体，即A项。B项三面绕序相反；C项把1与3画成相邻；D项把2与4画成相邻。故正确答案为A。'])
add(14,'图示为同一只立方体从两个方向看到的状态，六个面分别标有1至6，数字仅作面标签。下列哪对面一定相对？','C','两视图：公共面周围四个邻面',[
    '两图中1都作为上面，第一图显示其相邻的2、3，第二图显示其相邻的4、5。因此2、3、4、5都是1的邻面，剩余的6只能与1相对。',
    '按面1周围的侧面绕序进一步核对，可知相对面配对为1与6、2与4、3与5。A、B、D所示配对均为相邻面，只有C项相对。故正确答案为C。'])
add(15,'图示为外表面展开图。折叠时不得翻面，箭头方向须随所在面一起保持。下列哪项能由它折成？','D','面内方向：顶面箭头指向哪条棱',[
    '先把圆点面和菱形面分别定位为选项的前面、右面，此时箭头所在面的位置和朝向就被共同固定，不能再单独转动箭头。',
    '把展开图逐面折起，可见箭头所指的顶面边界正与圆点面相接。圆点面在前，故顶面箭头必须指向前侧棱，即图中左下方向。D项满足；A、B、C分别指向右侧、后侧和左侧。故正确答案为D。'])
add(16,'正方体ABCDEFGH中，P在AB上且AP∶PB＝3∶1，Q、R分别是DH、EH的中点。经过P、Q、R截正方体，截面有几条边？各选项只比较边数。','C','三点定面：求平面与棱的全部交点',[
    '令A为(0,0,0)，AB、AD、AE分别为三个单位坐标轴。P=(3/4,0,0)，Q=(0,1,1/2)，R=(0,1/2,1)，三点确定平面2x+y+z=3/2。',
    '该平面除经过DH、EH外，还分别与AB、EF、DC相交，共得到五个不同的棱交点，且没有相邻三点共线，截面为五边形。不能只把题给三点连成三角形。故正确答案为C。'],level='较难')
add(17,'方格纸先将左半向右折，再将下半向上折，图中每步都以当前纸张的中线对折。最后剪去灰色一格并穿透全部纸层。完全展开后，剪去区域的位置是哪一项？灰格表示缺失部分。','B','折纸剪切：两次对折的镜像还原',[
    '最后灰格紧贴两条折边的交会角。先还原上下对折，灰格沿横折边镜像；再还原左右对折，两个缺口再沿竖折边镜像，四个缺格合成原纸中央2×2区域。',
    'B项准确给出中央四格；A项把折边误当成原纸外边，C项把横向镜像位置错开一格，D项把竖折边位置误放到外侧。故正确答案为B。'])
add(18,'小正方体自下而上连续堆放，不得悬空。三种视图如图，俯视占位图的上方为前方；右视图从左到右依次表示前、中、后排。至少需要多少个小正方体？黑格表示该处至少有一块。','D','三视图：最低占位与行列最高层的联合约束',[
    '俯视图有7个占位，先各放1块。正视图要求左、右两列达到3层，而只有中排允许达到3层，因此中排左、右两处都必须堆3层；中列只在前排占位，需堆2层。',
    f'其余四处保留1层即可满足右视图各排最高层2、3、1，合计3+3+2+1+1+1+1={MIN18}块，并给出了实际可行构造。故正确答案为D。'],level='较难')
add(19,'图示为同一堆叠体从底到顶的第1至第3层平面图，各层同格对齐，深色格表示该层有小正方体。各小图上方均为前方。哪项是它的右视图？右视图从左到右对应前、中、后排。','C','分层重构：合并各层后取每排最高层',[
    '把三层按同格叠合：前排最高3层，中排最高1层，后排最高2层。右视图只保留每排的最高轮廓，不把一排内各列高度相加。',
    '应依次为3、1、2层，对应C项。A交换了中、后排，B把前、后排的最高层数错读为1和3，D则把前后方向颠倒。故正确答案为C。'])
add(20,'甲、乙各由4个同样大小的方格组成。只允许在纸面内旋转和平移，不得翻面。哪项可以由两个部件拼成，且不重叠、不留空？所有图格边长相同。','A','部件拼合：旋转放置与剩余形状',[
    '先用甲的连续三格长边定位，遍历它在候选图中的可放位置，再看余下四格能否仅靠旋转与乙重合。面积相等仅是必要条件，缺口的转折次序也须吻合。',
    'A项左侧竖向三格及其右下方相邻一格可以放甲，右侧剩余四格恰好是乙旋转90°后的形状，八格完整覆盖。B、C、D逐一尝试甲的可放位置，余下四格均不符合乙的转折次序。故正确答案为A。'],level='较难')
add(21,'正方形纸按图从左到右依次对折：右半向左，上半向下，最后把右下三角区域沿所示斜线折到左上三角区域。在最后的三角形内打一个小孔并穿透全部纸层。完全展开后，孔的位置是哪一项？','B','三次折纸打孔：斜线交换与两条中线镜像',[
    '先撤销斜折，小孔关于该斜线成对，两个孔到两条中折线的距离互换。再撤销上下和左右对折，对这两个位置分别作两次镜像。',
    '最后得到八孔，形成四组互换远近距离的位置：每个象限两个孔，到两条中线的距离分别为1份、2份。B项满足。A漏掉斜折产生的一半孔，C把距离误读为相等，D把第二组距离误设为2份、2份。故正确答案为B。'],level='较难')
add(22,'将六幅黑白方格图分为两类，使每类图形都有各自的共同特征或规律。分类正确的是：','D','黑白图案：一条对称轴与仅有中心对称',[
    '对称性针对完整黑白图案判断，不能只看外层正方形。①、③、⑥分别恰有一条对称轴，但不具有中心对称；②、④、⑤旋转180°可重合，且均没有对称轴。',
    '两类为①③⑥与②④⑤。逐幅比较对应黑格，不能用黑格总数分类，因为六图黑格数相同。故正确答案为D。'],options=['①②③，④⑤⑥','①③④，②⑤⑥','①②⑥，③④⑤','①③⑥，②④⑤'])
add(23,'将六幅带空心圆标记的黑白方格图分为两类，使每类中的图只通过平面旋转就能完全重合。不得翻面，分类正确的是：','B','同形分类：黑格图案与标记共同旋转',[
    '应把黑格和空心圆作为一个整体。①、④、⑤互相旋转可重合；②、③、⑥互相旋转也可重合。两类之间需要镜像翻转，单纯旋转不能同时对齐黑格的拐折与空心圆。',
    '只比较黑格数量或忽略空心圆，会把关键位置差异漏掉。正确分组为①④⑤与②③⑥。故正确答案为B。'],options=['①②④，③⑤⑥','①④⑤，②③⑥','①③⑤，②④⑥','①⑤⑥，②③④'])
add(24,'将六幅带有实心点和空心点的图分为两类，使每类图形都有各自的共同特征或规律。分类正确的是：','A','位置关系：两个标记与公共区域',[
    '①、②、⑤的实心点在两轮廓共同包围的区域内，空心点只在其中一个图形内；③、④、⑥则交换了这两种标记的位置。',
    '旋转不改变“同时在两个图形内”的关系。分组应为①②⑤与③④⑥。故正确答案为A。'],options=['①②⑤，③④⑥','①③④，②⑤⑥','①②③，④⑤⑥','①④⑤，②③⑥'])
add(25,'黑格之间仅共用完整边时才视为连通，只有角相接不算连通。将六图分为两类，使每类图形都有各自的共同特征或规律。分类正确的是：','C','数量分类：等黑格数下的连通块',[
    '六图均有8个黑格。按共边关系追踪，①、④、⑤各有2块连通区域；②、③、⑥各有3块。角接触不把两块合并。',
    '因此分组为①④⑤与②③⑥。面积相等不能替代连通性核对，正确答案为C。'],options=['①②③，④⑤⑥','①③⑤，②④⑥','①④⑤，②③⑥','①②⑤，③④⑥'])
add(26,'六图均为可折成立方体的展开图，每图两面各有一个黑点。将它们分为两类，使折叠后的立体各有共同特征。分类正确的是：','B','空间分类：不同展开图中的相对面',[
    '逐图折起后核对黑点所在面的朝向：①、③、④的两点落在相对面；②、⑤、⑥的两点落在相邻面。不能用展开图中的平面距离直接判断。',
    '六图都可折成立方体；标记面在展开图中不直接共边，也可能折后相邻，不能用平面是否接触代替折叠。应分①③④与②⑤⑥，故正确答案为B。'],options=['①②④，③⑤⑥','①③④，②⑤⑥','①③⑥，②④⑤','①②⑤，③④⑥'])
add(27,'每个立方体仅有相交于同一顶点的三面分别标为1、2、3，其余三面空白，数字不考查自身朝向。把只需转动就能相互重合的立方体分为一类，分类正确的是：','D','立体同形：三面绕序的手性',[
    '只转动立方体时，围绕共同顶点的1、2、3循环次序保持不变。①的上、前、右为1、2、3，③为2、3、1，⑥为3、1、2，三者为同一循环次序。',
    '②、④、⑤为反向循环，三者可互相旋转重合，却与前一组互为镜像。应分①③⑥与②④⑤。故正确答案为D。'],options=['①②④，③⑤⑥','①③⑤，②④⑥','①④⑥，②③⑤','①③⑥，②④⑤'])


def draw_all():
    for n in range(13,28):globals()[f'draw{n}']()


def verify():
    assert OR13 and OR15
    assert [view_valid(x,N13) for x in OP13]==[True,False,False,False]
    assert CASES14 and FLAGS14==[False,False,True,False]
    assert UP15==OR15[FR15][0] and cross(NA15,OR15[FR15][0])==OR15[RI15][0]
    assert [x==0 for x in OP15]==[False,False,False,True]
    assert len(SEC16)==5
    assert all(cross(tuple(y-x for x,y in zip(a,b)),tuple(y-x for x,y in zip(a,c)))!=(0,0,0) for a,b,c in combinations(SEC16,3))
    cut17_derived={(r,c) for r in (2,5-2) for c in (3,5-3)}
    assert cut17_derived==CUT17
    assert [x==cut17_derived for x in OP17]==[False,True,False,False]
    assert CASES18 and MIN18==12 and OP18.index(MIN18)==3
    assert RIGHT19==(3,1,2) and len(set(OP19))==4
    assert [next(tilings20(x),None) is not None for x in OP20]==[True,False,False,False]
    hole21_derived={(sx*x,sy*y) for x,y in ((2,1),(1,2)) for sx,sy in product((-1,1),repeat=2)}
    assert len(hole21_derived)==8 and hole21_derived==HOLE21
    assert [x==hole21_derived for x in OP21]==[False,True,False,False]
    assert [sum(symmetry_flags(x)[0]) for x in PAT22]==[1,0,1,0,0,1]
    assert [symmetry_flags(x)[1] for x in PAT22]==[False,True,False,True,True,False]
    orbits=[]
    for state in (BASE23,MIR23):
        orbit=set()
        for _ in range(4):orbit.add(motif_key(state));state=motif_rot(state)
        orbits.append(orbit)
    assert not orbits[0]&orbits[1] and [motif_key(x) in orbits[0] for x in STATES23]==[True,False,False,True,True,False]
    assert contains(POLY24_A,DOT24_IN) and contains(POLY24_B,DOT24_IN)
    assert contains(POLY24_A,DOT24_OUT) and not contains(POLY24_B,DOT24_OUT)
    assert [len(component_sizes(x)) for x in PAT25]==[2,3,3,2,2,3]
    assert len(cube_nets())==11
    assert [fold(cells)[a][0]==neg(fold(cells)[b][0]) for cells,marks in zip(NETS26,MARKS26) for a,b in [tuple(marks)]]==OPPOSITE26
    assert all(sum(abs(x-y) for x,y in zip(a,b))>1 for marks in MARKS26 for a,b in [tuple(marks)])
    base_normals={'1':(0,0,1),'2':(0,-1,0),'3':(1,0,0)}
    assert [view_valid(t,base_normals) for t in TRIPLES27]==[True,False,True,False,False,True]
    assert [q['n'] for q in QUESTIONS]==list(range(13,28))
    unique_flags={
        13:[view_valid(x,N13) for x in OP13],14:FLAGS14,15:[x==0 for x in OP15],
        16:[n==len(SEC16) for n in (3,4,5,6)],17:[x==cut17_derived for x in OP17],
        18:[n==MIN18 for n in OP18],19:[x==RIGHT19 for x in OP19],
        20:[next(tilings20(x),None) is not None for x in OP20],21:[x==hole21_derived for x in OP21],
    }
    def part_key(groups):return frozenset(frozenset(x) for x in groups)
    def option_partition(text):
        return part_key([{i for i,ch in enumerate('①②③④⑤⑥') if ch in side} for side in text.split('，')])
    parts={22:PART22,23:PART23,24:PART24,25:PART25,26:PART26,27:PART27}
    for q in QUESTIONS:
        if q['n'] in parts:unique_flags[q['n']]=[option_partition(s)==part_key(parts[q['n']]) for s in q['options']]
        flags=unique_flags[q['n']]
        assert sum(flags)==1 and q['answer']=='ABCD'[flags.index(True)],(q['n'],flags,q['answer'])
    return {'spatial':9,'classification':6,'q14_models':len(CASES14),'q16_section_vertices':[list(map(str,p)) for p in sorted(SEC16)],'q18_models':len(CASES18),'q18_minimum':MIN18,'q18_witness':{str(key):v for key,v in WIT18.items()},'q20_witness':[sorted(x) for x in WIT20],'cube_nets_available':11,'passed':True}


if __name__=='__main__':
    import json
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
    draw_all()
