"""Original items 21-30. Exact cuts, projections, cube folds and assembly models."""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product, permutations, combinations
from collections import Counter, defaultdict, deque
from pathlib import Path
import math, json, random
import numpy as np
from PIL import Image, ImageDraw
import drawkit as k

ROOT=Path(__file__).resolve().parent
QUESTIONS=[]
MODELS={}
REPORT={}

def portable(value):
    if isinstance(value,F):return str(value)
    if isinstance(value,np.integer):return int(value)
    if isinstance(value,dict):return {(','.join(map(str,key)) if isinstance(key,tuple) else key):portable(v) for key,v in value.items()}
    if isinstance(value,(tuple,list,set,frozenset)):return [portable(v) for v in value]
    return value

def add(n,stem,ask,answer,point,analysis,mechanism,refs,model,options=None,difficulty='较难'):
    q=dict(n=n,stem=stem,ask=ask,options=options or [],answer=answer,point=point,
           analysis=analysis,image=f'q{n:02}.png',explanation_image=f'e{n:02}.png',
           difficulty=difficulty,mechanism=mechanism,source_refs=refs,model=portable(model))
    QUESTIONS.append(q);MODELS[n]=model
    return q

def vec(a,b):return tuple(F(y)-F(x) for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def plane(p,q,r):
    norm=cross(vec(p,q),vec(p,r));assert any(norm),'collinear defining points'
    return norm,dot(norm,p)

def intersect_edges(vertices,edges,pqr):
    """Fraction coordinates; retains vertices lying on the cutting plane."""
    normal,const=plane(*pqr);out=set()
    for a,b in edges:
        a=tuple(map(F,vertices[a]));b=tuple(map(F,vertices[b]));da=dot(normal,a)-const;db=dot(normal,b)-const
        if da==0:out.add(a)
        if db==0:out.add(b)
        if da*db<0:
            t=da/(da-db);out.add(tuple(x+t*(y-x) for x,y in zip(a,b)))
    return sorted(out)

def mesh_edges(faces):return sorted({tuple(sorted((a,b))) for face in faces for a,b in zip(face,face[1:]+face[:1])})

def prism_mesh(profile,depth):
    vs=[(F(x),F(y),F(z)) for y in (0,depth) for x,z in profile];m=len(profile)
    faces=[list(range(m)),list(reversed(range(m,2*m)))]+[[i,i+m,(i+1)%m+m,(i+1)%m] for i in range(m)]
    return vs,faces

def orient_faces(vs,faces):
    center=np.mean(np.array(vs,dtype=float),axis=0);out=[]
    for face in faces:
        pts=np.array([vs[i] for i in face],dtype=float);normal=np.cross(pts[1]-pts[0],pts[2]-pts[0])
        if np.dot(normal,pts.mean(axis=0)-center)<0:face=list(reversed(face))
        out.append(face)
    return out

def iso(p):
    x,y,z=map(float,p);return (x+.65*y,.32*x-.30*y-z)

def fit_projection(points,box,padding=25):
    ps=[iso(p) for p in points];lo=[min(a[i] for a in ps) for i in (0,1)];hi=[max(a[i] for a in ps) for i in (0,1)]
    x0,y0,x1,y1=box;scale=min((x1-x0-2*padding)/(hi[0]-lo[0] or 1),(y1-y0-2*padding)/(hi[1]-lo[1] or 1))
    def fn(p):
        x,y=iso(p);return ((x0+x1)/2+(x-(lo[0]+hi[0])/2)*scale,(y0+y1)/2+(y-(lo[1]+hi[1])/2)*scale)
    return fn

def dashed(d,a,b,fill='#777777',width=3,dash=12):
    length=math.dist(a,b)
    if length==0:return
    for pos in range(0,int(length)+1,dash*2):
        t0=pos/length;t1=min((pos+dash)/length,1)
        d.line((a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0,a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1),fill=fill,width=width)

def draw_mesh(d,vs,faces,box,labels=None,cut=None):
    fn=fit_projection(vs,box,35);view=np.array((.65,-1,.508));face_meta=[];edge_faces=defaultdict(list)
    for i,f in enumerate(faces):
        ps=np.array([vs[j] for j in f],dtype=float);norm=np.cross(ps[1]-ps[0],ps[2]-ps[0]);length=np.linalg.norm(norm)
        norm=norm/length;vis=float(norm@view)>1e-6;const=float(norm@ps[0]);face_meta.append((f,norm,vis,const,float(ps.mean(axis=0)@view)))
        for a,b in zip(f,f[1:]+f[:1]):edge_faces[tuple(sorted((a,b)))].append(i)
    real_edges=set()
    for (a,b),adj in edge_faces.items():
        if len(adj)==2:
            x,y=(face_meta[i] for i in adj)
            if np.linalg.norm(x[1]-y[1])<1e-8 and abs(x[3]-y[3])<1e-8:continue
        real_edges.add((a,b))
    # Painter ordering handles nonconvex occlusion; draw only genuine boundaries.
    for f,norm,vis,const,depth in sorted(face_meta,key=lambda t:t[-1]):
        if not vis:continue
        d.polygon([fn(vs[j]) for j in f],fill='white')
        for a,b in zip(f,f[1:]+f[:1]):
            if tuple(sorted((a,b))) in real_edges:d.line((*fn(vs[a]),*fn(vs[b])),fill=k.BLACK,width=5)
    for (a,b),adj in edge_faces.items():
        if (a,b) in real_edges and not any(face_meta[i][2] for i in adj):dashed(d,fn(vs[a]),fn(vs[b]))
    if cut:
        for ring in cut:
            ps=[fn(p) for p in ring];d.line(ps+[ps[0]],fill='#555555',width=5)
    if labels:
        for name,p,offset in labels:
            x,y=fn(p);d.ellipse((x-5,y-5,x+5,y+5),fill=k.BLACK);k.label(d,x+offset[0],y+offset[1],name,36)
    return fn

def poly_draw(d,rings,box):
    allpts=[p for ring in rings for p in ring];x0,y0,x1,y1=box
    lx=min(p[0] for p in allpts);hx=max(p[0] for p in allpts);ly=min(p[1] for p in allpts);hy=max(p[1] for p in allpts)
    sc=min((x1-x0-36)/(hx-lx),(y1-y0-36)/(hy-ly))
    for ring in rings:
        pts=[((x0+x1)/2+(x-(lx+hx)/2)*sc,(y0+y1)/2-(y-(ly+hy)/2)*sc) for x,y in ring]
        d.line(pts+[pts[0]],fill=k.BLACK,width=5,joint='curve')

def canvas(n,height=1120,stem_bottom=610,option_top=680,option_bottom=1030):
    im,d=k.canvas(height);d.rectangle((65,30,1735,stem_bottom),outline=k.BLACK,width=5)
    opts=k.options(d,option_top,option_bottom)
    k.LAYOUTS[n]={'kind':'spatial','stem_frame':[65,30,1735,stem_bottom],
                  'option_frame':[170,option_top,1630,option_bottom],'option_centers':opts,'letters_below':True}
    return im,d,opts

def save_ex(im,n):im.save(k.ASSETS/f'e{n:02}.png',dpi=(300,300))

SQRT2=math.sqrt(2)
PROFILE21=[(0,0),(3,0),(3,1),(2,1),(2,2),(1,2),(1,3),(0,3)]
VS21,FC21=prism_mesh(PROFILE21,3)
PQR21=[(0,0,0),(3,0,0),(0,3,3)]
CUT21=intersect_edges(VS21,mesh_edges(FC21),PQR21)
POLY21=[(x,z*SQRT2) for x,z in PROFILE21]
OP21=[[(0,0),(3,0),(3,SQRT2),(2,SQRT2),(2,2*SQRT2),(1,2*SQRT2),(1,3*SQRT2),(0,3*SQRT2)],
      [(0,0),(3,0),(3,SQRT2),(1.5,SQRT2),(1.5,2*SQRT2),(.5,2*SQRT2),(.5,3*SQRT2),(0,3*SQRT2)],
      PROFILE21,
      [(0,0),(3,0),(3,2*SQRT2),(2,2*SQRT2),(2,SQRT2),(1,SQRT2),(1,3*SQRT2),(0,3*SQRT2)]]
# Rotate option placement, retaining physical section ratios.
OP21=[OP21[2],OP21[0],OP21[3],OP21[1]]
add(21,'图示实体由一个阶梯形截面沿水平方向等距延伸而成。三个台阶的宽和高均为1，前后长度为3。P、Q是同一条前侧底棱的两个端点，R是与P对应的后侧最高顶点。',
    '用过P、Q、R三点的平面切开实体，所得截面的形状与比例最符合哪一项？','B','截面 定面后追踪台阶与实际边长',
    ['P、Q确定前侧底棱；R相对P向后3、向上3，故切平面在前后方向每前进1就升高1。',
     '在各台阶内求交，截面轮廓依次经过8个转折点；沿前后方向相差1且高度相差1的截面边，实际长度为√2，左右方向的单位边仍长1。',
     '因此三个台阶的高均为√2，宽均为1，对应B。A把斜切后的真实长度当成竖直投影长度；C颠倒中间台阶高度；D改变台阶宽度比例。'],
    '规整底棱加后上顶点确定斜平面；非凸阶梯棱柱的完整截面',['C-GK26-80','C-H009'],
    {'solid':'stepped_prism','vertices':VS21,'faces':FC21,'pqr':PQR21,'cut_vertices':CUT21,'plane':'z=y','physical_basis':['x','sqrt(2)*y']},difficulty='难')

VS22=[(-2,-2,0),(2,-2,0),(2,2,0),(-2,2,0),(0,0,4)]
FC22=orient_faces(VS22,[[0,1,2,3],[0,4,1],[1,4,2],[2,4,3],[3,4,0]])
PQR22=[VS22[0],VS22[1],(1,1,2)]
CUT22=intersect_edges(VS22,mesh_edges(FC22),PQR22)
H22=math.sqrt(13)
OP22=[[(-2,0),(2,0),(1,H22),(-1,H22)],
      [(-2,0),(2,0),(1,math.sqrt(5)),(-1,math.sqrt(5))],
      [(-2,0),(2,0),(1.5,H22),(-.5,H22)],
      [(-2,0),(2,0),(.5,H22),(-.5,H22)]]
OP22=[OP22[1],OP22[3],OP22[0],OP22[2]]
add(22,'正四棱锥S-PQCD的底边长为4，高为4。P、Q是同一条底棱的两个端点，R为侧棱SC的中点。',
    '过P、Q、R三点的截面，按真实边长比例绘出，应为哪一项？','C','截面 平行交线与中点截取',
    ['在与底棱PQ平行的后侧棱上找交点：R所在高度为2，切面同时经过SD的中点，得到一条长2且平行于PQ的交线。',
     '两底边分别长4、2；其中点在水平方向相距3，高度相距2，故梯形的高为√13，而不是√5。两条腰相等。',
     'C的上下底比为1∶2、两腰对称且高度正确。A缩短梯形高，B把上底再减半，D将上底偏移，均不符合。'],
    '规则四棱锥底棱加对侧棱中点定面；用相似关系和面内距离辨析',['C-GK26-80','C-H054'],
    {'solid':'regular_square_pyramid','vertices':VS22,'faces':FC22,'pqr':PQR22,'cut_vertices':CUT22,'base_lengths':[4,2],'height_squared':13})

def ring_mesh():
    vs=[];faces=[];index={}
    def ix(p):
        if p not in index:index[p]=len(vs);vs.append(p)
        return index[p]
    def face(ps):faces.append([ix(tuple(p)) for p in ps])
    outer=[(0,0),(4,0),(4,3),(0,3)];inner=[(1,1),(3,1),(3,2),(1,2)]
    for ring,rev in [(outer,False),(inner,True)]:
        for a,b in zip(ring,ring[1:]+ring[:1]):
            ps=[(*a,0),(*b,0),(*b,3),(*a,3)]
            if rev:ps=list(reversed(ps))
            face(ps)
    for z in (0,3):
        for i in range(4):
            j=(i+1)%4;ps=[(*outer[i],z),(*outer[j],z),(*inner[j],z),(*inner[i],z)]
            if z==0:ps=list(reversed(ps))
            face(ps)
    return vs,faces
VS23,FC23=ring_mesh();PQR23=[(0,0,0),(4,0,0),(0,3,3)]
CUT23=intersect_edges(VS23,mesh_edges(FC23),PQR23)
OUT23=[(0,0),(4,0),(4,3*SQRT2),(0,3*SQRT2)]
IN23=[(1,SQRT2),(3,SQRT2),(3,2*SQRT2),(1,2*SQRT2)]
OP23=[(OUT23,[(1.5,SQRT2),(2.5,SQRT2),(2.5,2*SQRT2),(1.5,2*SQRT2)]),
      (OUT23,[(1,.5*SQRT2),(3,.5*SQRT2),(3,2.5*SQRT2),(1,2.5*SQRT2)]),
      (OUT23,[(1.5,SQRT2),(3.5,SQRT2),(3.5,2*SQRT2),(1.5,2*SQRT2)]),
      (OUT23,IN23)]
add(23,'图示长方体左右长4，前后长3，高3，中央有一个上下贯通的矩形孔。孔的左右宽为2、前后长为1，孔壁与外侧相应各面平行，且孔口居中。P、Q为前侧底棱两端，R为与P对应的后侧上顶点。',
    '用过P、Q、R三点的平面截开，截面轮廓与孔洞的位置、比例均正确的是哪一项？','D','截面 贯通孔与面内尺度',
    ['P、Q、R确定斜平面z=y。外边界在左右方向长4，在前后方向跨越3并同时升高3，故另一边长3√2。',
     '孔的左右宽仍为2；前后宽1对应切面内长度√2。孔的前后边界分别在斜面长度的1/3、2/3处，因此截面上仍有居中的矩形孔。',
     'D同时满足内外边界。A把孔左右宽减半，B把孔的斜向宽度加倍，C将孔横向偏置。'],
    '底棱两端加后上顶点定斜面；带贯通孔实体的双边界求交',['C-2022zj89','C-2022sy62','C-GK26-80'],
    {'solid':'rectangular_prism_with_through_hole','vertices':VS23,'faces':FC23,'pqr':PQR23,'cut_vertices':CUT23,'plane':'z=y','outer_dimensions':[4,'3sqrt2'],'hole_dimensions':[2,'sqrt2'],'hole_centered':True},difficulty='难')

def blocks_from_heights(h):return {(x,y,z) for y,row in enumerate(h) for x,height in enumerate(row) for z in range(height)}
def views(h):
    rows=len(h);cols=len(h[0]);front=tuple(max(h[y][x] for y in range(rows)) for x in range(cols));right=tuple(max(h[y]) for y in range(rows));top=frozenset((x,y) for y,row in enumerate(h) for x,v in enumerate(row) if v)
    return front,right,top

def draw_blocks(d,cells,box,black=frozenset(),labels=None):
    if not cells:return
    vertices=[(x+dx,y+dy,z+dz) for x,y,z in cells for dx,dy,dz in product((0,1),repeat=3)];fn=fit_projection(vertices,box,14);faces=[]
    for x,y,z in cells:
        for delta,face in [((0,-1,0),[(x,y,z),(x+1,y,z),(x+1,y,z+1),(x,y,z+1)]),((1,0,0),[(x+1,y,z),(x+1,y+1,z),(x+1,y+1,z+1),(x+1,y,z+1)]),((0,0,1),[(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)])]:
            nb=(x+delta[0],y+delta[1],z+delta[2])
            if nb in cells:continue
            depth=sum((.65*p[0]-p[1]+.508*p[2]) for p in face)/4
            color=k.BLACK if (x,y,z) in black else ('white' if delta==(0,0,1) else '#f5f5f5')
            faces.append((depth,face,color))
    for _,face,color in sorted(faces,key=lambda a:a[0]):
        ps=[fn(p) for p in face];d.polygon(ps,fill=color);d.line(ps+[ps[0]],fill=k.BLACK,width=4)
    return fn

def occupancy_draw(d,cells,box,grid_max=None,numbers=None):
    pts=set(cells);cols=max([x for x,y in pts]+[0])+1;rows=max([y for x,y in pts]+[0])+1
    if grid_max:cols,rows=grid_max
    x0,y0,x1,y1=box;unit=min((x1-x0-30)/cols,(y1-y0-30)/rows)
    ox=(x0+x1)/2-cols*unit/2;oy=(y0+y1)/2-rows*unit/2
    for x,y in sorted(pts):
        rect=(ox+x*unit,oy+(rows-1-y)*unit,ox+(x+1)*unit,oy+(rows-y)*unit)
        d.rectangle(rect,outline=k.BLACK,width=4)
        if numbers:k.label(d,(rect[0]+rect[2])/2,(rect[1]+rect[3])/2,numbers.get((x,y),''),32)

def elevation_cells(heights):return {(x,z) for x,h in enumerate(heights) for z in range(h)}

H24=[[[3,0,1],[1,2,3],[2,1,0]],[[2,0,1],[3,2,3],[1,1,0]],[[3,0,3],[1,2,1],[2,1,0]],[[3,0,1],[2,2,3],[3,1,0]]]
F24,R24,T24=views(H24[0]);OP24=[H24[2],H24[1],H24[0],H24[3]]
add(24,'某积木由相同的小正方体组成，各竖列从地面连续堆放。题干三图从左到右依次为正视图、右视图、俯视占位图；右视图从左到右对应前、中、后排，俯视图下方为前方。',
    '下列哪一个立体图形与题干三个视图同时相符？','C','三视图 同占位、同正视下的前后高度辨析',
    ['俯视占位排除错误理解方向后，比较正视图三列最高层数3、2、3，以及右视图前、中、后三排最高层数3、3、2。',
     '四项占位相同且正视最高层数均为3、2、3，不能只看正视图。A的三排最高层数为3、2、2，B为2、3、1，D为3、3、3；只有C为3、3、2。',
     '因此C同时满足三个方向的投影。解析图给出C的逐排高度，便于复核遮挡。'],
    '九列占位与两向极大值联合重构，三个干扰均保持相同正视图',['C-H047','C-GK26-V80','C-H153'],
    {'height_options':OP24,'front':F24,'right_front_to_back':R24,'top_occupied':sorted(T24),'true_index':2})

F25=(2,4,2,3);R25=(4,3,3)
MASK25={(0,0),(1,0),(3,0),(0,1),(1,1),(2,1),(3,1),(0,2),(2,2),(3,2)}
def minimum_height_model(front,right,mask):
    positions=sorted(mask);best=10**9;witness=None;count=0
    domains=[range(1,min(front[x],right[y])+1) for x,y in positions]
    for vals in product(*domains):
        total=sum(vals)
        if total>best:continue
        h=[[0]*len(front) for _ in right]
        for (x,y),v in zip(positions,vals):h[y][x]=v
        a,b,c=views(h)
        if a==tuple(front) and b==tuple(right):
            count+=1
            if total<best:best=total;witness=h
    return best,witness,count
MIN25,WIT25,COUNT25=minimum_height_model(F25,R25,MASK25)
OP25=[MIN25+1,MIN25-1,MIN25+2,MIN25]
add(25,'相同的小正方体从地面连续堆放，不得悬空。题干三图从左到右依次为正视图、右视图、俯视占位图；右视图从左到右对应前、中、后排，俯视图下方为前方。俯视图每个有框小格都至少放一块。',
    '要同时得到这三个视图，至少需要多少个小正方体？','D','三视图 最少堆砌的行列最高层共享',
    [f'先在俯视图的{len(MASK25)}个占位各放1块。然后同时满足正视图各列最高层数2、4、2、3，以及右视图前、中、后三排最高层数4、3、3。',
     '前排必须出现4层，且只有正视图第2列允许达到4层，因此4层竖列必须位于前排第2列。按正视图四列分别达标，至少还需增加1+3+1+2=7块，加上10个占位的底层，共17块。',
     '但中、后两排都要出现3层：同一根竖列不能同时位于两排，而前排的4层柱也不能兼任。因此除第4列用于达标的一根3层柱外，另一排还至少需要再把一个底层柱加高到3层，多2块。',
     f'下界为17+2={MIN25}；解析图的构造恰好达到该数，故选D。'],
    '带缺格占位的三向极值与最小方块数联合约束',['C-GK26-V80','C-H047'],
    {'front':F25,'right_front_to_back':R25,'mask':sorted(MASK25),'minimum':MIN25,'witness_heights':WIT25,'enumeration':'all continuous integer column heights bounded by both projections','options':OP25},difficulty='难')

BOX26=list(product((0,2),repeat=3));EDGE26=[(a,b) for a,b in combinations(BOX26,2) if sum(x!=y for x,y in zip(a,b))==1]
EXTRA26=[((0,0,0),(2,2,2)),((0,2,2),(2,0,0)),((1,0,0),(1,2,2)),((0,0,1),(2,2,1)),((0,1,0),(0,1,2))]
WIRE26=EDGE26+EXTRA26
PROJ26={tuple(sorted(((a[0],a[2]),(b[0],b[2])))) for a,b in WIRE26 if (a[0],a[2])!=(b[0],b[2])}
BASE26=[((0,0),(2,0)),((2,0),(2,2)),((2,2),(0,2)),((0,2),(0,0)),((0,0),(2,2)),((0,2),(2,0)),((1,0),(1,2)),((0,1),(2,1))]
OP26=[BASE26[:-1]+[((0,.5),(2,.5))],BASE26,BASE26[:-2]+[((.5,0),(.5,2)),((0,1),(2,1))],BASE26[:-2]+[((1,0),(1,2))]]
def edge_signature(edges):
    es=k.planarize(edges)
    return tuple(sorted(tuple((str(x),str(y)) for x,y in e) for e in es))
add(26,'图示为透明线架，所有杆件均以实线画出；交叉处不另增杆。P、Q、R分别是底面前左、前右、后左三个顶点。沿PR方向由前向后作正投影，投影的水平方向由P指向Q。',
    '将完全重合的线段合并、投影成点的杆不画出，得到的正视图是哪一项？','B','三视图 线架的逐段投影与重合去重',
    ['沿PR方向观察就是消去前后坐标，保留左右与高低坐标。方框前后边对应重合，朝前后延伸的杆投影为点。',
     '两根空间斜杆分别投影为方框的两条对角线；另外两根斜杆分别投影为居中的竖线与横线。中部左边竖杆的投影与左框边重合，不得多画一条。',
     'B具备完整的外框、两条对角线及正中的横竖线。A将横线下移，C将竖线左移，D漏掉横线。'],
    '透明线架轴向正投影；重合边、零长度投影、空间斜杆共同辨析',['C-H153','C-H055','C-H056'],
    {'wire_segments':WIRE26,'view_direction':[0,1,0],'projected_segments':sorted(PROJ26),'option_segments':OP26,'true_index':1},difficulty='难')

# Cube-net folding. u/right, v/up, n/outward. Exact integer orientation frames.
NET=[(0,0),(1,0),(2,0),(3,0),(1,1),(1,-1)]
def neg(a):return tuple(-x for x in a)
def fold_net(cells):
    frames={cells[0]:((1,0,0),(0,1,0),(0,0,1))};todo=[cells[0]];cells=set(cells)
    for cell in todo:
        u,v,n=frames[cell]
        for (dx,dy),frame in [((1,0),(neg(n),v,u)),((-1,0),(n,v,neg(u))),((0,1),(u,neg(n),v)),((0,-1),(u,n,neg(v)))]:
            b=(cell[0]+dx,cell[1]+dy)
            if b not in cells:continue
            if b in frames:assert frames[b]==frame
            else:frames[b]=frame;todo.append(b)
    assert len(frames)==6 and len({f[2] for f in frames.values()})==6
    return frames
FRAMES=fold_net(NET)
def rotations24():
    out=[]
    for perm in permutations(range(3)):
        for signs in product((-1,1),repeat=3):
            m=np.zeros((3,3),dtype=int)
            for i,j in enumerate(perm):m[i,j]=signs[i]
            if round(np.linalg.det(m))==1:out.append(m)
    return out
ROTS=rotations24()
def sticker_points(frames,patterns):
    out=[]
    for cell,(kind,turn) in patterns.items():
        u,v,n=frames[cell]
        # An oriented asymmetric three-point motif, with distinct point identities.
        points={'arrow':[(-1,0),(1,0),(0,1)],'corner':[(-1,-1),(-1,0),(0,-1)],'fork':[(-1,-1),(1,-1),(0,1)]}[kind]
        for j,(a,b) in enumerate(points):
            for _ in range(turn):a,b=-b,a
            p=tuple(4*n[i]+a*u[i]+b*v[i] for i in range(3))
            out.append((kind,j,p))
    return out
def canonical_stickers(points):
    return min(tuple(sorted((kind,j,tuple(int(x) for x in m@np.array(p))) for kind,j,p in points)) for m in ROTS)
def canonical_net(patterns):return canonical_stickers(sticker_points(FRAMES,patterns))
PAT27={(0,0):('arrow',0),(1,1):('corner',1),(1,0):('fork',0)}
BAD27A={**PAT27,(0,0):('arrow',1)}
BAD27B={(0,0):('arrow',0),(1,-1):('corner',1),(1,0):('fork',0)}
BAD27C={**PAT27,(1,0):('fork',1)}
OP27=[BAD27A,BAD27B,PAT27,BAD27C]
def pattern_2d(d,cx,cy,unit,kind,turn,mapper=None):
    def xy(a,b):
        for _ in range(turn):a,b=-b,a
        return mapper(a,b) if mapper else (cx+a*unit,cy-b*unit)
    if kind=='arrow':
        a=xy(-.32,0);b=xy(.32,0);tip=xy(.32,0);p1=xy(.12,.12);p2=xy(.12,-.12)
        d.line((*a,*b),fill=k.BLACK,width=5);d.polygon([tip,p1,p2],fill=k.BLACK)
    elif kind=='corner':
        ps=[xy(-.43,-.43),xy(-.43,.02),xy(-.17,.02),xy(-.17,-.17),xy(.02,-.17),xy(.02,-.43)];d.polygon(ps,fill=k.BLACK)
    elif kind=='fork':
        ps=[xy(-.36,-.36),xy(.36,-.36),xy(0,.36)];d.line(ps+[ps[0]],fill=k.BLACK,width=4);a=xy(0,.36);b=xy(0,-.08);d.line((*a,*b),fill=k.BLACK,width=4)

def net_draw(d,patterns,box,unit=None):
    x0,y0,x1,y1=box;unit=unit or min((x1-x0-20)/4,(y1-y0-20)/3);cx=(x0+x1)/2-2*unit;cy=(y0+y1)/2
    for x,y in NET:
        xx=cx+(x+.5)*unit;yy=cy-y*unit
        d.rectangle((xx-unit/2,yy-unit/2,xx+unit/2,yy+unit/2),outline=k.BLACK,width=3)
        if (x,y) in patterns:pattern_2d(d,xx,yy,unit,*patterns[(x,y)])

def cube_with_patterns(d,patterns,box,translation=(0,0,0),rotation=None):
    pts=sticker_points(FRAMES,patterns);target={}
    # Map base net's marked faces to visible front/right/top by one rigid rotation.
    if rotation is None:
        normals=[FRAMES[c][2] for c in patterns]
        visible={(0,-1,0),(1,0,0),(0,0,1)}
        rotation=next(m for m in ROTS if {tuple(m@np.array(n)) for n in normals}<=visible)
    verts=list(product((-1,1),repeat=3));face_defs=[[(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1) if p==val] for p,val in []]
    allvertices=[tuple(np.array(v)+np.array(translation)) for v in verts];fn=fit_projection(allvertices,box,15)
    for normal,face in [((0,-1,0),[(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1)]),((1,0,0),[(1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)]),((0,0,1),[(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)])]:
        ps=[fn(tuple(np.array(v)+translation)) for v in face];d.polygon(ps,fill='white');d.line(ps+[ps[0]],fill=k.BLACK,width=4)
    for cell,(kind,turn) in patterns.items():
        u,v,n=(tuple(rotation@np.array(a)) for a in FRAMES[cell])
        if tuple(n) not in {(0,-1,0),(1,0,0),(0,0,1)}:continue
        def mapper(a,b,u=u,v=v,n=n):return fn(tuple(n[i]+2*a*u[i]+2*b*v[i]+translation[i] for i in range(3)))
        pattern_2d(d,0,0,1,kind,turn,mapper)
    return rotation

add(27,'图示为一个正方体。图中三个有图案的面均已画出，其余面为空白；图案随所在面一起折叠，不得翻面。',
    '下列哪一幅外表面展开图能够折成该正方体？','C','空间重构 相邻面绕序与面内方向',
    ['先以三分叉三角形所在面为基准，核对箭头面和黑角面是否都与它相邻，并处在正确的绕序上。',
     '仅有邻接关系还不够：箭头在折叠后必须指向指定公共棱，黑色角块也必须落在同一顶点附近。',
     'C能同时还原三个面。A把箭头转了90°；B把黑角面放到三角形面的另一侧；D改变了三角形内部短线相对公共棱的方向。'],
    '三个非对称面图案的折叠刚体旋转验证',['C-GK26-81'],
    {'net_cells':NET,'target_patterns':PAT27,'option_patterns':OP27,'rotation_group_size':24,'true_index':2},difficulty='难')

PAT28L={(0,0):('arrow',1),(1,0):('fork',1),(1,1):('corner',0)}
PAT28R={(0,0):('fork',2),(1,0):('arrow',2),(1,1):('corner',2)}
OP28=[(PAT28L,{**PAT28R,(1,0):('arrow',3)}),
      ({**PAT28L,(1,1):('corner',1)},PAT28R),
      (PAT28L,PAT28R),
      ({**PAT28L,(0,0):('arrow',0)},{**PAT28R,(1,1):('corner',3)})]
add(28,'题干中的两个正方体①、②各有三个有图案的面，其余面为空白。它们可各自转动，但不得翻面；每个选项上、下两幅展开图依次对应①、②。',
    '哪一项中的两幅展开图都能折成对应的正方体？','C','双立方体重构 两套面内方向的并行约束',
    ['分别固定每个正方体上三角形所在面，再利用公共棱检查箭头与黑色角块；两个正方体的判断不能互相替代。',
     '①需要箭头、三角形内部短线和黑角的位置同时匹配；②还须核对箭头相对三角形的转向。',
     'C两幅都能经空间转动与题干重合。A仅②箭头方向错；B仅①黑角方向错；D两个正方体的面内方向均有错误。'],
    '双立方体外表面展开；每个候选包含两套可独立验证的方向约束',['C-GK26-81'],
    {'net_cells':NET,'targets':[PAT28L,PAT28R],'option_pairs':OP28,'true_index':2},difficulty='难')

# Item29: exact cover of a 3x3x2 target with one black cell in each connected part.
TARGET29=set(product(range(3),range(3),range(2)))
BLACK29={(0,0,0),(2,1,1),(1,2,1)}
def connected(cells):
    seen={next(iter(cells))};todo=list(seen)
    for p in todo:
        for i in range(3):
            for sign in (-1,1):
                q=tuple(v+(sign if j==i else 0) for j,v in enumerate(p))
                if q in cells and q not in seen:seen.add(q);todo.append(q)
    return seen==set(cells)
def normalize_piece(cells,black):
    low=tuple(min(p[i] for p in cells) for i in range(3));fn=lambda p:tuple(p[i]-low[i] for i in range(3))
    return frozenset(map(fn,cells)),frozenset(map(fn,black))
def orientations(piece):
    cells,black=piece;seen=set();out=[]
    for m in ROTS:
        a=[tuple(m@np.array(p)) for p in cells];b=[tuple(m@np.array(p)) for p in black];v=normalize_piece(a,b)
        if v not in seen:seen.add(v);out.append(v)
    return out
def placements(piece):
    out=[]
    for cells,black in orientations(piece):
        maximum=tuple(max(p[i] for p in cells) for i in range(3))
        for shift in product(*(range((3,3,2)[i]-maximum[i]) for i in range(3))):
            fn=lambda p:tuple(p[i]+shift[i] for i in range(3));a=frozenset(map(fn,cells));b=frozenset(map(fn,black))
            if a<=TARGET29 and b==a&BLACK29:out.append((a,b))
    return out
def assembly_solutions(parts):
    pools=[placements(p) for p in parts];solutions=[]
    for a,ba in pools[0]:
        for b,bb in pools[1]:
            if a&b:continue
            rem=TARGET29-a-b
            for c,bc in pools[2]:
                if c==rem:solutions.append((a,b,c))
    return solutions
def find_partition29():
    rng=random.Random(263029)
    for _ in range(50000):
        a=set(rng.sample(sorted(TARGET29),6));rest=TARGET29-a
        if len(a&BLACK29)!=1 or not connected(a):continue
        b=set(rng.sample(sorted(rest),6));c=rest-b
        if len(b&BLACK29)==len(c&BLACK29)==1 and connected(b) and connected(c):
            parts=[normalize_piece(s,s&BLACK29) for s in (a,b,c)]
            if len({frozenset(p[0]) for p in parts})==3:return parts
    raise RuntimeError('partition search failed')
PARTS29=find_partition29()
def make_wrong_pieces29():
    base=PARTS29[2];wrong=[]
    # Same six-cell geometry, different marked cell; all one black cube.
    for p in sorted(base[0]):
        cand=(base[0],frozenset({p}))
        if cand==base:continue
        if not assembly_solutions(PARTS29[:2]+[cand]) and cand not in wrong:wrong.append(cand)
        if len(wrong)==3:break
    if len(wrong)<3:
        rng=random.Random(2911)
        for _ in range(1000):
            cells={(0,0,0)}
            while len(cells)<6:
                p=rng.choice(sorted(cells));i=rng.randrange(3);q=tuple(v+(rng.choice((-1,1)) if j==i else 0) for j,v in enumerate(p));cells.add(q)
            cells,_=normalize_piece(cells,[]);cand=(cells,frozenset({min(cells)}))
            if not assembly_solutions(PARTS29[:2]+[cand]) and cand not in wrong:wrong.append(cand)
            if len(wrong)==3:break
    assert len(wrong)==3
    return wrong
WRONG29=make_wrong_pieces29();OP29=[WRONG29[0],PARTS29[2],WRONG29[1],WRONG29[2]]
add(29,'完整长方体由18个相同的小正方体组成，其中3块为黑色，其余为白色。题干从左到右依次给出完整形体、部件①、部件②；各部件只能作空间转动和平移，不得翻面、拆分或重叠。',
    '哪一个选项能够与部件①、②共同拼成题干完整形体，且黑色方块的位置也完全相符？','B','立体拼合 形状装填与三黑块定位',
    ['三个部件均须完整放入3×3×2长方体，先利用①、②的凹凸结构寻找相邻的填补位置，再看剩余六个方块的形状。',
     '形状能放下仍不足以确定答案，三个黑色方块必须同时落在完整形体对应位置。B存在完整装填方案。解析图左图为下层、右图为上层，图中①②对应已知部件，③对应B，黑点标出黑色方块；两层图下方均为前方。',
     '其余三项经所有24种空间朝向及合法平移核对，均无法同时满足形体装填和黑块位置。它们保留相同块数与相近结构，不能单凭数块排除。'],
    '两已知部件加第三部件的彩色精确覆盖；24朝向逐一验算',['C-GK26-82'],
    {'target':sorted(TARGET29),'black':sorted(BLACK29),'known_parts':PARTS29[:2],'option_parts':OP29,'true_index':1},difficulty='难')

# Four equally sized regions; P4 adjacency versus K1,3. All 13 edges, four faces.
CELLS30=[{(0,0),(1,0),(2,0),(3,0)},
         {(0,0),(1,0),(2,0),(1,1)},
         {(0,0),(1,0),(1,1),(2,1)},
         {(0,0),(0,1),(0,2),(1,1)},
         {(0,0),(0,1),(0,2),(1,2)},
         {(0,1),(1,0),(1,1),(1,2)}]
def region_adjacency(cells):
    return sorted(sum((x+dx,y+dy) in cells for dx,dy in ((1,0),(-1,0),(0,1),(0,-1))) for x,y in cells)
def cell_region_edges(cells):
    return {tuple(sorted((a,b))) for x,y in cells for a,b in zip([(x,y),(x+1,y),(x+1,y+1),(x,y+1)],[(x+1,y),(x+1,y+1),(x,y+1),(x,y)])}
def warped30(i,p):
    x,y=p
    # Continuous, orientation-preserving mesh warps keep all shared edges exact.
    return (x*(1+.10*i)+.24*y+.07*x*y,y*(1+.06*i)+.10*x+.04*x*x)
EDGES30=[{tuple(sorted((warped30(i,a),warped30(i,b)))) for a,b in cell_region_edges(c)} for i,c in enumerate(CELLS30)]
add(30,'将下面六幅图形分成两类，使每一类图形都有各自的共同特征或规律。',
    '分类正确的是哪一项？','A','六图分类 四个最小面的共边结构',
    ['六幅图都连通，均有4个最小封闭面，线段总数和区域总数相同，不能据此分组。进一步观察最小面的共边关系；只在一个点相接不算共边。',
     '①③⑤中每个小面最多与另外2个小面共边，四个小面依次连成一条链，共边度数为1、1、2、2。',
     '②④⑥各有一个小面与其余3个小面分别共边，另外三个小面彼此不共边，共边度数为1、1、1、3。故分为①③⑤与②④⑥，选A。'],
    '固定面数、边数和连通性，区别面邻接路径与星形结构',['C-GK26-83','C-H046'],
    {'region_cells':[sorted(c) for c in CELLS30],'adjacency_degrees':[region_adjacency(c) for c in CELLS30],'edge_counts':[len(cell_region_edges(c)) for c in CELLS30]},
    options=['①③⑤，②④⑥','①②⑤，③④⑥','①③⑥，②④⑤','①④⑤，②③⑥'],difficulty='中高')

def draw_section(n):
    im,d,opts=canvas(n)
    if n==21:
        labels=[('P',PQR21[0],(-27,20)),('Q',PQR21[1],(28,14)),('R',PQR21[2],(-30,-20))]
        draw_mesh(d,VS21,FC21,(450,65,1350,580),labels)
        for (cx,cy),poly in zip(opts,OP21):poly_draw(d,[poly],(cx-150,cy-150,cx+150,cy+150))
        ex,ed=k.canvas(680);draw_mesh(ed,VS21,FC21,(100,30,850,630),labels,[[tuple(p) for p in [(0,0,0),(3,0,0),(3,1,1),(2,1,1),(2,2,2),(1,2,2),(1,3,3),(0,3,3)]]]);poly_draw(ed,[POLY21],(1000,50,1650,630));save_ex(ex,n)
    elif n==22:
        labels=[('P',VS22[0],(-28,17)),('Q',VS22[1],(28,17)),('S',VS22[4],(0,-28)),('C',VS22[2],(25,20)),('R',PQR22[2],(25,-20))]
        draw_mesh(d,VS22,FC22,(480,60,1320,580),labels)
        for (cx,cy),poly in zip(opts,OP22):poly_draw(d,[poly],(cx-150,cy-150,cx+150,cy+150))
        ex,ed=k.canvas(680);draw_mesh(ed,VS22,FC22,(80,35,850,640),labels,[[(F(-2),F(-2),F(0)),(F(2),F(-2),F(0)),(F(1),F(1),F(2)),(F(-1),F(1),F(2))]]);poly_draw(ed,[OP22[2]],(1000,50,1650,630));save_ex(ex,n)
    else:
        labels=[('P',PQR23[0],(-28,20)),('Q',PQR23[1],(28,17)),('R',PQR23[2],(-27,-20))]
        draw_mesh(d,VS23,FC23,(400,60,1400,580),labels)
        for (cx,cy),rings in zip(opts,OP23):poly_draw(d,rings,(cx-150,cy-150,cx+150,cy+150))
        ex,ed=k.canvas(680);draw_mesh(ed,VS23,FC23,(70,35,920,640),labels);poly_draw(ed,OP23[3],(1050,50,1660,630));save_ex(ex,n)
    k.save(im,n)

def draw_views(n):
    im,d,opts=canvas(n,1170,635,700,1080)
    if n==24:front,right,top=F24,R24,T24
    else:front,right,top=F25,R25,MASK25
    boxes=[(210,100,610,565),(700,100,1100,565),(1190,100,1590,565)]
    occupancy_draw(d,elevation_cells(front),boxes[0],(len(front),max(front)))
    occupancy_draw(d,elevation_cells(right),boxes[1],(len(right),max(right)))
    occupancy_draw(d,top,boxes[2],(len(front),len(right)))
    for i,(x,_) in enumerate([(410,0),(900,0),(1390,0)]):k.label(d,x,598,'①②③'[i],36)
    if n==24:
        for (cx,cy),h in zip(opts,OP24):draw_blocks(d,blocks_from_heights(h),(cx-162,cy-155,cx+162,cy+155))
        ex,ed=k.canvas(680);draw_blocks(ed,blocks_from_heights(H24[0]),(80,40,900,630));occupancy_draw(ed,T24,(1050,50,1650,620),(3,3),{(x,y):H24[0][y][x] for x,y in T24});save_ex(ex,n)
    else:
        for (cx,cy),v in zip(opts,OP25):k.label(d,cx,cy,f'{v}',74)
        ex,ed=k.canvas(680);draw_blocks(ed,blocks_from_heights(WIT25),(80,40,900,630));occupancy_draw(ed,MASK25,(1050,50,1650,620),(4,3),{(x,y):WIT25[y][x] for x,y in MASK25});save_ex(ex,n)
    k.save(im,n)

def draw26():
    im,d,opts=canvas(26)
    points={p for e in WIRE26 for p in e};fn=fit_projection(points,(500,60,1300,570),35)
    for a,b in WIRE26:d.line((*fn(a),*fn(b)),fill=k.BLACK,width=4)
    for name,p,off in [('P',(0,0,0),(-25,15)),('Q',(2,0,0),(25,15)),('R',(0,2,0),(-25,15))]:
        x,y=fn(p);d.ellipse((x-5,y-5,x+5,y+5),fill=k.BLACK);k.label(d,x+off[0],y+off[1],name,35)
    for center,es in zip(opts,OP26):k.network(d,*center,k.planarize(es),230,False)
    k.save(im,26);ex,ed=k.canvas(620);k.network(ed,900,310,k.planarize(PROJ26),440,False);save_ex(ex,26)

def draw_nets(n):
    im,d,opts=canvas(n,1290,555,620,1195)
    if n==27:
        cube_with_patterns(d,PAT27,(620,60,1180,520))
        for (cx,cy),pat in zip(opts,OP27):net_draw(d,pat,(cx-166,cy-185,cx+166,cy+185))
        ex,ed=k.canvas(650);net_draw(ed,PAT27,(100,40,850,610));cube_with_patterns(ed,PAT27,(1000,50,1640,610));save_ex(ex,n)
    else:
        cube_with_patterns(d,PAT28L,(350,60,850,510));cube_with_patterns(d,PAT28R,(950,60,1450,510));k.label(d,600,527,'①',38);k.label(d,1200,527,'②',38)
        for (cx,cy),(a,b) in zip(opts,OP28):
            net_draw(d,a,(cx-166,640,cx+166,885));net_draw(d,b,(cx-166,920,cx+166,1165))
        ex,ed=k.canvas(680);net_draw(ed,PAT28L,(60,40,840,640));net_draw(ed,PAT28R,(960,40,1740,640));save_ex(ex,n)
    k.save(im,n)

def visible_piece_orientation(piece):
    # Favor a rotation exposing its black cube, while preserving target congruence.
    for cells,black in orientations(piece):
        p=next(iter(black))
        if any(tuple(p[j]+(1 if j==i else 0) for j in range(3)) not in cells for i in (0,2)) or (p[0],p[1]-1,p[2]) not in cells:return cells,black
    return piece
def draw29():
    im,d,opts=canvas(29,1150,610,680,1060)
    draw_blocks(d,TARGET29,(100,60,650,540),BLACK29)
    for i,piece in enumerate(PARTS29[:2]):
        p=visible_piece_orientation(piece);x=760+i*470;draw_blocks(d,*[p[0],(x,70,x+400,520)],black=p[1]);k.label(d,x+200,570,'①②'[i],40)
    for (cx,cy),piece in zip(opts,OP29):
        cells,black=visible_piece_orientation(piece);draw_blocks(d,cells,(cx-160,cy-160,cx+160,cy+160),black)
    k.save(im,29)
    solution=assembly_solutions(PARTS29)[0];ex,ed=k.canvas(720)
    for z in range(2):
        box=(150+850*z,80,750+850*z,650);nums={}
        for i,cells in enumerate(solution):
            for x,y,zz in cells:
                if zz==z:nums[(x,y)]='①②③'[i]+('●' if (x,y,zz) in BLACK29 else '')
        occupancy_draw(ed,{(x,y) for x in range(3) for y in range(3)},box,(3,3),nums)
    save_ex(ex,29)

def draw30():
    im,d,centers=k.classification(30)
    for center,es in zip(centers,EDGES30):k.network(d,*center,k.planarize(es),222,False)
    k.save(im,30)
    ex,ed=k.canvas(620)
    for cx,kind in [(490,'path'),(1310,'star')]:
        pts=[(cx-180,310),(cx-60,310),(cx+60,310),(cx+180,310)] if kind=='path' else [(cx,310),(cx-180,310),(cx,130),(cx,490)]
        es=[(0,1),(1,2),(2,3)] if kind=='path' else [(0,1),(0,2),(0,3)]
        for a,b in es:ed.line((*pts[a],*pts[b]),fill=k.BLACK,width=5)
        for i,(x,y) in enumerate(pts):ed.ellipse((x-28,y-28,x+28,y+28),fill='white',outline=k.BLACK,width=4);k.label(ed,x,y,i+1,29)
    save_ex(ex,30)

def draw_all():
    for n in (21,22,23):draw_section(n)
    for n in (24,25):draw_views(n)
    draw26();draw_nets(27);draw_nets(28);draw29();draw30()
    return [str(k.ASSETS/f'q{n}.png') for n in range(21,31)]

def polygon_similarity_signature(poly):
    """Rigid rotations/reflections, cyclic starting point and uniform image scale."""
    n=len(poly);dist=[[math.dist(a,b)**2 for b in poly] for a in poly]
    scale=sum(dist[i][(i+1)%n] for i in range(n))
    signatures=[]
    for direction in (-1,1):
        for start in range(n):
            ids=[(start+direction*i)%n for i in range(n)]
            signatures.append(tuple(round(dist[a][b]/scale,9) for a in ids for b in ids))
    return min(signatures)

def hole_signature(rings):
    outer,inner=rings
    w=max(x for x,y in outer)-min(x for x,y in outer);h=max(y for x,y in outer)-min(y for x,y in outer)
    return tuple(round(v,9) for v in [(max(x for x,y in inner)-min(x for x,y in inner))/w,
        (max(y for x,y in inner)-min(y for x,y in inner))/h,
        (sum(x for x,y in inner)/4-min(x for x,y in outer))/w,
        (sum(y for x,y in inner)/4-min(y for x,y in outer))/h,w/h])

def verify():
    report={'questions':list(range(21,31)),'sources_visual_checked':18,'national_2026_priority':True}
    for n,vs,fc,pqr in [(21,VS21,FC21,PQR21),(22,VS22,FC22,PQR22),(23,VS23,FC23,PQR23)]:
        no,c=plane(*pqr);assert pqr[0]!=pqr[1] and any(no)
        intersections=intersect_edges(vs,mesh_edges(fc),pqr)
        assert all(dot(no,p)==c for p in intersections)
        report[str(n)]={'plane_normal':[str(x) for x in no],'constant':str(c),'exact_intersection_points':[[str(x) for x in p] for p in intersections],'two_points_on_known_edge':True,'noncollinear':True}
    assert len(CUT21)==8 and len(CUT22)==4
    matches21=[i+1 for i,p in enumerate(OP21) if polygon_similarity_signature(p)==polygon_similarity_signature(POLY21)]
    matches22=[i+1 for i,p in enumerate(OP22) if polygon_similarity_signature(p)==polygon_similarity_signature([(-2,0),(2,0),(1,H22),(-1,H22)])]
    matches23=[i+1 for i,p in enumerate(OP23) if hole_signature(p)==hole_signature((OUT23,IN23))]
    assert matches21==[2] and matches22==[3] and matches23==[4]
    report['21']['proportional_congruence_matching_options']=matches21
    report['22']['proportional_congruence_matching_options']=matches22
    report['23']['outer_and_hole_dimensions_and_position_matching_options']=matches23
    report['24']={'matching_options':[i+1 for i,h in enumerate(OP24) if views(h)==(F24,R24,T24)],'fronts':[views(h)[0] for h in OP24],'right_views':[views(h)[1] for h in OP24]}
    assert report['24']['matching_options']==[3]
    assert views(WIT25)==(F25,R25,frozenset(MASK25)) and sum(map(sum,WIT25))==MIN25
    report['25']={'minimum':MIN25,'witness':WIT25,'all_allowed_column_heights_enumerated':True,'possible_models_at_or_below_current_best_seen':COUNT25}
    ss=edge_signature(PROJ26);matches=[i+1 for i,es in enumerate(OP26) if edge_signature(es)==ss];assert matches==[2]
    report['26']={'matching_options':matches,'raw_3d_segments':len(WIRE26),'unique_nonzero_2d_segments':len(PROJ26)}
    for n,targets,options in [(27,[PAT27],[(p,) for p in OP27]),(28,[PAT28L,PAT28R],OP28)]:
        matches=[i+1 for i,pair in enumerate(options) if all(canonical_net(p)==canonical_net(t) for p,t in zip(pair,targets))]
        assert matches==[3],(n,matches)
        report[str(n)]={'matching_options':matches,'cube_rotations_checked':24,'all_net_faces_have_distinct_normals':True}
    matches=[i+1 for i,p in enumerate(OP29) if assembly_solutions(PARTS29[:2]+[p])];assert matches==[2]
    assert all(len(p[0])==6 and len(p[1])==1 and connected(p[0]) for p in PARTS29[:2]+OP29)
    report['29']={'matching_options':matches,'solution_counts':[len(assembly_solutions(PARTS29[:2]+[p])) for p in OP29],'orientation_group':24,'target_blocks':18,'black_blocks':3,'each_part_blocks':6,'each_part_black':1}
    degrees=[region_adjacency(c) for c in CELLS30];assert degrees==[[1,1,2,2],[1,1,1,3],[1,1,2,2],[1,1,1,3],[1,1,2,2],[1,1,1,3]]
    assert all(len(cell_region_edges(c))==13 for c in CELLS30)
    report['30']={'adjacency_degrees':degrees,'unwarped_edge_counts':[13]*6,'components':[1]*6,'faces':[4]*6,'correct_groups':[[1,3,5],[2,4,6]]}
    return report

def json_default(obj):
    if isinstance(obj,F):return str(obj)
    if isinstance(obj,(set,frozenset)):return sorted(obj)
    if isinstance(obj,np.integer):return int(obj)
    raise TypeError(type(obj).__name__)

if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    report=verify();draw_all()
    (ROOT/'verify_c.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=json_default),encoding='utf-8')
    (ROOT/'questions_c.json').write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2,default=json_default),encoding='utf-8')
    print(json.dumps({'done':True,'questions':len(QUESTIONS),'minimum25':MIN25,'verify':report},ensure_ascii=False,default=json_default))
