"""Original Q1--10. Models are specified before their deterministic drawings."""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction
from collections import Counter
import math, random, json
from PIL import ImageDraw
import drawkit as D

ROOT=Path(__file__).resolve().parent
BLACK=D.BLACK
CHOICE='ABCD'
CIRC='①②③④⑤⑥'
OUTER=[(0,0),(0,1),(0,2),(0,3),(1,3),(2,3),(3,3),(3,2),(3,1),(3,0),(2,0),(1,0)]
INNER=[(1,1),(1,2),(2,2),(2,1)]
def q(n,stem,answer,point,analysis,model,refs,kind,difficulty='中高'):
    return dict(n=n,category='图形推理',stem=stem,ask='从所给的四个选项中，选择最合适的一项。' if kind!='classification' else '将六幅图形分成两类，分类正确的是哪一项？',
                options=[],answer=answer,point=point,analysis=analysis,image=f'q{n:02}.png',explanation_image=None,
                difficulty=difficulty,level=difficulty,mechanism=point,source_refs=refs,model=model,layout_kind=kind)
def rotpt(p,a):
    c,s=math.cos(a),math.sin(a)
    return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
def path(d,pts,width=5,close=False):d.line(pts+([pts[0]] if close else []),fill=BLACK,width=width,joint='curve')
def poly(d,pts,width=5):path(d,pts,width,True)
def coords(d,cx,cy,pts,scale=1,angle=0):
    pp=[rotpt(p,angle) for p in pts]
    return [(cx+x*scale,cy+y*scale) for x,y in pp]
def marker(d,cx,cy,p,size=13):
    x,y=p;d.ellipse((cx+x-size,cy+y-size,cx+x+size,cy+y+size),fill=BLACK)
def count_angles(points):
    """Only convex polygon interior angles equal to 90 degrees are counted."""
    out=0;crosses=[]
    for i,b in enumerate(points):
        a,c=points[i-1],points[(i+1)%len(points)]
        u=(a[0]-b[0],a[1]-b[1]);v=(c[0]-b[0],c[1]-b[1])
        cross=u[0]*v[1]-u[1]*v[0];crosses.append(cross)
        if abs(u[0]*v[0]+u[1]*v[1])<1e-8:out+=1
    assert all(x>0 for x in crosses) or all(x<0 for x in crosses),'Only convex test polygons'
    return out
def area(pts):return abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(pts,pts[1:]+pts[:1])))/2
def equalset(a,b):return {tuple(round(x,7) for x in p) for p in a}=={tuple(round(x,7) for x in p) for p in b}
def polygon_symmetries(pts):
    center=(sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts))
    pp=[(p[0]-center[0],p[1]-center[1]) for p in pts]
    central=equalset(pp,[(-x,-y) for x,y in pp]);axes=[]
    candidates=[math.atan2(y,x) for x,y in pp]
    candidates += [math.atan2(a[1]+b[1],a[0]+b[0]) for a,b in zip(pp,pp[1:]+pp[:1])]
    for theta in candidates:
        c,s=math.cos(2*theta),math.sin(2*theta)
        if equalset(pp,[(c*x+s*y,s*x-c*y) for x,y in pp]):
            val=round(theta%math.pi,6)
            if not any(abs(val-v)<1e-5 for v in axes):axes.append(val)
    return {'central':central,'axis_count':len(axes)}

# Q1: three subjects on two tracks, with equal marker counts in every candidate.
def motion(t):return {OUTER[t%12],OUTER[(6+2*t)%12],INNER[(1-t)%4]}
M1_STEM=[motion(t) for t in range(5)]
M1_RIGHT=motion(5)
M1_OPTS=[{OUTER[5],OUTER[4],INNER[2]},M1_RIGHT,{OUTER[5],OUTER[5+1],INNER[0]},{OUTER[4],OUTER[4+1],INNER[1]}]
def draw_lattice(d,cx,cy,cells):
    step=51;x0=cx-1.5*step;y0=cy-1.5*step
    for r in range(4):
        for c in range(3):path(d,[(x0+c*step,y0+r*step),(x0+(c+1)*step,y0+r*step)],3)
    for c in range(4):
        for r in range(3):path(d,[(x0+c*step,y0+r*step),(x0+c*step,y0+(r+1)*step)],3)
    for r in range(4):
        for c in range(4):
            x,y=x0+c*step,y0+r*step
            d.ellipse((x-12,y-12,x+12,y+12),fill=BLACK if (r,c) in cells else 'white',outline=BLACK,width=4)

# Q2: property carriers vary, so motion must be read from their axes rather than outlines.
OUTLINES=[[(0,-100),(85,75),(-85,75)],[(0,-105),(82,10),(0,85),(-82,10)],[(0,-105),(82,-20),(35,-20),(35,85),(-35,85),(-35,-20),(-82,-20)]]
Z=[(-22,-14),(22,-14),(-22,14),(22,14)]
M2_STEM=[(0,0,0),(1,45,-45),(2,90,-90),(1,45,45),(0,90,0)]
M2_OPTS=[(2,135,45),(2,90,-45),(2,135,0),(2,135,-45)]
def draw_property(d,cx,cy,item):
    kind,outer,inner=item
    poly(d,coords(d,cx,cy,OUTLINES[kind],angle=math.radians(outer)),5)
    path(d,coords(d,cx,cy,Z,angle=math.radians(inner)),5)

# Q3: all four candidates have equal numbers of black cells.
def r90(s):return {(c,3-r) for r,c in s}
def r270(s):return {(3-c,r) for r,c in s}
def make_matrix():
    rng=random.Random(30261025);rows=[]
    universe=[(r,c) for r in range(4) for c in range(4)]
    while len(rows)<3:
        a=set(rng.sample(universe,6));b=set(rng.sample(universe,6));c=r90(a)^b
        variants=[c,a^b,r90(a^b),r270(a)^b]
        if len(c)==8 and (len(rows)<2 or (len({tuple(sorted(x)) for x in variants})==4 and all(len(x)==8 for x in variants))):rows.append((a,b,c))
    return rows
M3_ROWS=make_matrix();aa,bb,cc=M3_ROWS[2];M3_OPTS=[cc,aa^bb,r90(aa^bb),r270(aa)^bb]

# Convex five-sided faces: every option uses the same face and side totals.
PENTS={
    0:[(0,-3),(2.853,-.927),(1.763,2.427),(-1.763,2.427),(-2.853,-.927)],
    1:[(0,0),(3,0),(2.7,1.7),(1.5,3),(0,2)],
    2:[(-2,2),(2,2),(2,-.5),(.4,-2),(-2,-.5)],
    3:[(0,0),(3,0),(3,1.5),(1.1,3),(0,3)],
}
for k,v in PENTS.items():assert count_angles(v)==k,(k,count_angles(v))
def draw_pent(d,cx,cy,k,size=78,angle=0):
    pts=PENTS[k];lo=[min(p[j] for p in pts) for j in (0,1)];hi=[max(p[j] for p in pts) for j in (0,1)]
    center=[(lo[j]+hi[j])/2 for j in (0,1)];pp=[(p[0]-center[0],p[1]-center[1]) for p in pts]
    # Keep rotated glyphs within their allocated square.
    radius=max(math.hypot(*p) for p in pp);scale=size/2/radius
    poly(d,coords(d,cx,cy,pp,scale,math.radians(angle)),4)
def point_face_model(parts,turn=0):return {'face_right_angles':parts,'faces':len(parts),'right_angles':sum(parts),'dots':sum(parts)-len(parts),'turn':turn}
M4_STEM=[point_face_model([3,2]),point_face_model([3,2,2],1),point_face_model([1,3],2),point_face_model([2,2,2],3),point_face_model([3,3],1)]
M4_OPTS=[point_face_model([3,2,1]),point_face_model([3,3,2]),point_face_model([3,3,1]),point_face_model([2,2,1])]
for m in M4_OPTS:m['dots']=4
def draw_point_faces(d,cx,cy,m):
    loc=[(-62,-25),(62,-25)] if m['faces']==2 else [(-62,-52),(62,-52),(0,52)]
    for i,(x,y) in enumerate(loc):draw_pent(d,cx+x,cy+y,m['face_right_angles'][i],90,(m['turn']*23+i*29)%360)
    dot_y=cy+115 if m['faces']==3 else cy+82
    D.dots(d,cx,dot_y,m['dots'],22)

# Q5: six internal segments in each glyph. Topological face counts are computed.
FRAME=[((-3,-3),(3,-3)),((3,-3),(3,3)),((3,3),(-3,3)),((-3,3),(-3,-3))]
NETS={
 3:[((-1,-3),(-1,3)),((-1,-1),(3,-1)),((-3,1),(-2,1)),((1,-3),(1,-2)),((3,1),(2,1)),((-1,2),(0,2))],
 4:[((-1,-3),(-1,3)),((1,-3),(1,3)),((-1,-1),(1,-1)),((-3,1),(-2,1)),((3,1),(2,1)),((0,3),(0,2))],
 5:[((0,-3),(0,3)),((-3,0),(3,0)),((0,-1),(3,-1)),((-3,-2),(-2,-2)),((1,3),(1,2)),((-1,0),(-1,1))],
 6:[((-1,-3),(-1,3)),((1,-3),(1,3)),((-3,0),(3,0)),((-3,-2),(-2,-2)),((0,3),(0,2)),((3,2),(2,2))],
 7:[((-1,-3),(-1,3)),((1,-3),(1,3)),((-3,0),(3,0)),((-1,-1),(1,-1)),((-3,-2),(-2,-2)),((3,2),(2,2))],
}
def nfaces(raw):return D.graph_stats(D.planarize(raw))['faces']
for f,segs in NETS.items():assert nfaces(FRAME+segs)==f,(f,nfaces(FRAME+segs))
M5_STEM=[(3,3,0),(6,6,1),(4,4,2),(7,7,3),(5,5,1)]
M5_OPTS=[(4,5,2),(6,5,3),(5,6,0),(5,5,2)]
TICK_SPOTS=[(-2,-3),(-.5,-3),(1,-3),(3,-2),(3,.5),(2,3),(-1,3),(-3,1),(-3,-1)]
def draw_framed(d,cx,cy,m):
    faces,ticks,turn=m;angle=turn*math.pi/2;s=25
    for a,b in FRAME+NETS[faces]:path(d,coords(d,cx,cy,[a,b],s,angle),4)
    for x,y in TICK_SPOTS[:ticks]:
        if y==-3:a,b=(x,-3),(x,-3.65)
        elif y==3:a,b=(x,3),(x,3.65)
        elif x==3:a,b=(3,y),(3.65,y)
        else:a,b=(-3,y),(-3.65,y)
        path(d,coords(d,cx,cy,[a,b],s,angle),5)

# Q6: zero-odd-degree components still require a stroke.
def cycle_with_tails(x,k,phase=0):
    vs=[(x,0),(x+3,0),(x+1,3)];ends=[(x-1,-1),(x+4,-1),(x+1,4)]
    edges=[(vs[i],vs[(i+1)%3]) for i in range(3)]
    for j in range(k):i=(j+phase)%3;edges.append((vs[i],ends[i]))
    return edges
def stroke_model(a,b,phase=0):return {'tails':[a,b],'phase':phase,'segments':cycle_with_tails(0,a,phase)+cycle_with_tails(6,b,(phase+1)%3)}
M6_STEM=[stroke_model(1,1),stroke_model(1,2,1),stroke_model(0,3,2),stroke_model(1,1,2),stroke_model(2,1,1)]
M6_OPTS=[stroke_model(1,2,2),stroke_model(3,0,1),stroke_model(2,1),stroke_model(1,2)]
def graph_summary(m):
    g=D.graph_stats(D.planarize(m['segments']))
    return {k:g[k] for k in ('faces','components','strokes')}|{'odd_vertices':sum(v%2 for v in g['degrees'].values()),'segments':len(m['segments'])}
def draw_strokes(d,cx,cy,m):D.network(d,cx,cy,D.planarize(m['segments']),size=220,show_nodes=False)

# Four classification items use the same answer form, not four image candidates.
PARTITIONS=[((1,3,6),(2,4,5)),((1,2,4),(3,5,6)),((1,4,5),(2,3,6)),((1,2,5),(3,4,6))]
def partition_key(p):return tuple(sorted(tuple(sorted(g)) for g in p))
def options_for(correct,answer):
    bad=[p for p in PARTITIONS if partition_key(p)!=partition_key(correct)]
    if len(bad)<3:bad.append(((1,2,3),(4,5,6)))
    out=bad[:3];out.insert(CHOICE.index(answer),correct);return out
def option_text(p):return '、'.join(CIRC[i-1] for i in p[0])+'，'+'、'.join(CIRC[i-1] for i in p[1])
def classification_analysis(intro,classes,metrics,opts,answer):
    texts=[intro]
    for letter,p in zip(CHOICE,opts):
        if letter==answer:texts.append(f'{letter}项：两组内部的性质分别一致，分类成立。')
        else:
            bad=next(g for g in p if len({classes[i-1] for i in g})>1)
            a=bad[0];b=next(i for i in bad if classes[i-1]!=classes[a-1])
            texts.append(f'{letter}项：将{CIRC[a-1]}与{CIRC[b-1]}同组，但前者{metrics[a-1]}，后者{metrics[b-1]}，分类不成立。')
    return '\n'.join(texts)

# Q7: all maximum faces are six-sided and greater than half the outer area.
MAX_OUT=[(-5,-5),(5,-5),(5,4),(3,5),(-5,5)]
MAX_FACES=[
 [(-4,-4),(2,-4),(4,-1),(4,4),(-2,4),(-4,1)],
 [(-4,4),(4,4),(4,-2),(2,-4),(-2,-4),(-4,-2)],
 [(-4,-4),(1.5,-4),(4,-2),(4,4),(-1.5,4),(-4,2)],
 [(-4,4),(4,4),(4,-1),(1,-4),(-1,-4),(-4,-1)],
 [(-4,4),(4,4),(4,-2.5),(1.5,-4),(-1.5,-4),(-4,-2.5)],
 [(-4,-4),(2.5,-4),(4,-.5),(4,4),(-2.5,4),(-4,.5)],
]
M7_CLASSES=[int(polygon_symmetries(p)['central']) for p in MAX_FACES]
assert M7_CLASSES==[1,0,1,0,0,1],M7_CLASSES
def draw_maxface(d,cx,cy,i):
    turn=(i%4)*math.pi/2;scale=21
    poly(d,coords(d,cx,cy,MAX_OUT,scale,turn),4)
    poly(d,coords(d,cx,cy,MAX_FACES[i],scale,turn),4)
    p=MAX_FACES[i]
    path(d,coords(d,cx,cy,[p[0],(-5,5) if i in (1,3,4) else (-5,-5)],scale,turn),4)
    # One bridge joins the nested boundaries; the maximum face remains unchanged.

# Q8: equal black counts and identical grids; only the black subset is classified.
def mask_sym(s):
    def tf(fn):return {fn(r,c) for r,c in s}
    central=tf(lambda r,c:(4-r,4-c))==s
    axes=sum(tf(fn)==s for fn in [lambda r,c:(r,4-c),lambda r,c:(4-r,c),lambda r,c:(c,r),lambda r,c:(4-c,4-r)])
    return central,axes
def make_masks():
    rng=random.Random(81025);C=[];A=[];u=[(r,c) for r in range(5) for c in range(5)]
    while len(C)<3 or len(A)<3:
        if len(C)<3:
            seeds=rng.sample(u,4);s=set(seeds)|{(4-r,4-c) for r,c in seeds}
            if len(s)==8 and mask_sym(s)==(True,0) and s not in C:C.append(s)
        if len(A)<3:
            seeds=rng.sample(u,4);s=set(seeds)|{(r,4-c) for r,c in seeds}
            if len(s)==8 and mask_sym(s)==(False,1) and s not in A:A.append(s)
    return [C[0],A[0],A[1],C[1],C[2],A[2]]
M8_MASKS=make_masks();M8_CLASSES=[int(mask_sym(s)[0]) for s in M8_MASKS]

# Q9: all totals equal; the allocation of convex right angles differs.
M9_PARTS=[(2,2),(1,3),(1,3),(2,2),(1,3),(2,2)]
M9_CLASSES=[int(a==b) for a,b in M9_PARTS]
def draw_anglepair(d,cx,cy,i):
    for j,k in enumerate(M9_PARTS[i]):draw_pent(d,cx+(-61 if j==0 else 61),cy,k,110,(i*37+j*71)%360)

# Q10: both dashed polylines traverse the same outline; their mutual crossing is local.
def crosspoint(seg1,seg2):
    a,b=seg1;c,d=seg2
    ux,uy=b[0]-a[0],b[1]-a[1];vx,vy=d[0]-c[0],d[1]-c[1]
    den=ux*vy-uy*vx
    if abs(den)<1e-9:return None
    t=((c[0]-a[0])*vy-(c[1]-a[1])*vx)/den;u=((c[0]-a[0])*uy-(c[1]-a[1])*ux)/den
    if 1e-8<t<1-1e-8 and 1e-8<u<1-1e-8:return (a[0]+t*ux,a[1]+t*uy)
def inside(p,polygon):
    x,y=p;flag=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:flag=not flag
    return flag
OUT10=[(-1,-1),(1,-1),(.9,1),(-1,1)]
def relation_model(yes,turn):
    a=[(-1.8,-.6),(1.4,.6 if yes else -.6),(1.8,1.5)]
    b=[(-1.8,.6),(1.4,-.6 if yes else .6),(1.8,-1.5)]
    intersections=[crosspoint(x,y) for x in zip(a,a[1:]) for y in zip(b,b[1:])];intersections=[p for p in intersections if p is not None]
    assert len(intersections)==1
    boundary=[(x,y) for x,y in zip(OUT10,OUT10[1:]+OUT10[:1])]
    hits=[crosspoint(s,e) for p in [a,b] for s in zip(p,p[1:]) for e in boundary];hits=[p for p in hits if p is not None]
    assert len(hits)==4 and inside(intersections[0],OUT10)==yes
    return {'inside':yes,'turn':turn,'outline':OUT10,'lines':[a,b],'crossing':intersections[0],'boundary_crossings':len(hits)}
M10=[relation_model(bool(k),turn) for k,turn in [(0,0),(1,1),(1,2),(0,1),(0,2),(1,3)]]
M10_CLASSES=[int(m['inside']) for m in M10]
def dashed(d,pts,width=4):
    for a,b in zip(pts,pts[1:]):
        dist=math.dist(a,b)
        for s in range(0,math.ceil(dist),15):
            e=min(s+10,dist);p=(a[0]+(b[0]-a[0])*s/dist,a[1]+(b[1]-a[1])*s/dist);q=(a[0]+(b[0]-a[0])*e/dist,a[1]+(b[1]-a[1])*e/dist)
            path(d,[p,q],width)
def draw_relation(d,cx,cy,m):
    a=m['turn']*math.pi/2;s=57
    poly(d,coords(d,cx,cy,m['outline'],s,a),5)
    for pts in m['lines']:dashed(d,coords(d,cx,cy,pts,s,a),4)
    # Keep the actual crossing visible even when a dash gap falls there.
    p=m['crossing']
    for pts in m['lines']:
        seg=next((x,y) for x,y in zip(pts,pts[1:]) if abs(math.dist(x,p)+math.dist(p,y)-math.dist(x,y))<1e-6)
        dx,dy=seg[1][0]-seg[0][0],seg[1][1]-seg[0][1];r=math.hypot(dx,dy);u=(dx/r*.12,dy/r*.12)
        path(d,coords(d,cx,cy,[(p[0]-u[0],p[1]-u[1]),(p[0]+u[0],p[1]+u[1])],s,a),4)

QUESTIONS=[]
QUESTIONS.append(q(1,'从所给的四个选项中，选择最合适的一项填入问号处，使图形呈现一定的规律性。','B','多主体位置规律 外圈不同步与内圈反向',
 '将外圈12个球按左上角起顺时针编号0—11，内圈4个球从左上角起顺时针编号0—3。外圈两黑球分别每次顺时针走1格、2格；内圈黑球每次逆时针走1格。第六幅外圈应为5、4号，内圈为0号。\nA项：外圈正确，内圈错到2号。B项：三条轨迹均符合。C项：内圈正确，外圈第二黑球错到6号。D项：外圈正确，内圈错到1号。',
 {'outer_cycle':OUTER,'inner_cycle':INNER,'stem':[sorted(s) for s in M1_STEM],'candidates':[sorted(s) for s in M1_OPTS]},['A13','A14'],'sequence'))
QUESTIONS.append(q(2,'左边三幅图形呈现一定的规律。将同样的规律应用到右边一组，问号处应选择哪一项？','D','属性载体与位置 外部对称轴和内部折线分开观察',
 '每幅图的外轮廓均只有一条对称轴，不能比较外轮廓的具体形状。第一组外轮廓的对称轴依次顺时针转45°；内部Z形仅中心对称，每次逆时针转45°。第二组应继续各自的方向变化。问号处外轮廓应转至135°，内部折线应为−45°方向。\nA项：外轴正确，内部折线与所需方向相差90°。B项：内部正确，外部对称轴停在90°。C项：外轴正确，内部折线未完成逆时针45°。D项：内外两层均正确。',
 {'stem':M2_STEM,'candidates':M2_OPTS,'outer_axis_step_degrees':45,'inner_step_degrees':-45},['A01','A04','A15'],'two_groups'))
QUESTIONS.append(q(3,'从所给的四个选项中，选择最合适的一项填入问号处，使九宫格呈现一定的规律性。','A','位置与样式 先旋转再黑白求异',
 '按行观察：先把第一幅图顺时针旋转90°，再与第二幅按对应格求异，得到第三幅。即两格同色得白，异色得黑。前两行均可验证，第三行应用同样的规则。四项均为8个黑格，单数黑格无法确定答案。\nA项：完整满足“旋转第一幅后求异”。B项：直接求异，漏掉旋转。C项：把求异结果整体旋转，等于误把第二幅也旋转。D项：把第一幅逆时针旋转90°后求异，方向错误。',
 {'rows':[[sorted(x) for x in row] for row in M3_ROWS],'candidates':[sorted(x) for x in M3_OPTS]},['A16','A05'],'matrix'))
QUESTIONS.append(q(4,'左边三幅图形呈现一定的规律。将同样的规律应用到右边一组，问号处应选择哪一项？','C','点角面联动 直角总数减黑点数等于面数',
 '每个封闭五边形各算一个面，只统计它自身的90°内角。左组三幅的“直角总数−黑点数”分别为5−3=2、7−4=3、4−2=2，均等于封闭面数；右组前两幅分别为6−3=3、6−4=2，也符合。问号处四项均有3个面、4个黑点，应有7个直角。\nA项：直角为3+2+1=6，6−4=2，不等于3。B项：直角为3+3+2=8，8−4=4，不等于3。C项：直角为3+3+1=7，7−4=3，符合。D项：直角为2+2+1=5，5−4=1，不等于3。',
 {'stem':M4_STEM,'candidates':M4_OPTS,'counting_convention':'凸五边形自身的90度内角；黑点单独计数'},['A15','A11','A06'],'two_groups'))
QUESTIONS.append(q(5,'从所给的四个选项中，选择最合适的一项填入问号处，使图形呈现一定的规律。图内连接短线的方框属于题目图形；最外层排版框不参与判断。','D','内外数量联动 内部封闭面与图形参考框短线',
 '观察小方框内部被线条分出的最小封闭面，再数从该图形框向外伸出的短线。五幅题干的两种数量依次为(3,3)、(6,6)、(4,4)、(7,7)、(5,5)，始终相等。框内未围成新区域的支线不增加面数。\nA项：4个面、5条框外短线，不等。B项：6个面、5条短线，不等。C项：5个面、6条短线，不等。D项：5个面、5条短线，相等。图形整体的线段数不能代替封闭面数。',
 {'stem':M5_STEM,'candidates':M5_OPTS,'internal_raw_segment_count':6,'frame_counts_as_graphic':True},['A06','A13','A21'],'sequence'))
QUESTIONS.append(q(6,'从所给的四个选项中，选择最合适的一项填入问号处，使图形呈现一定的规律性。','B','最少笔画 多连通部分分别计算',
 '每幅均有两个互不连通的部分，最少笔画必须分别计算后相加。有奇点的部分需“奇点数÷2”笔；没有奇点但存在边的部分仍需1笔。题干最少笔画依次为2、3、4、2、3，故下一幅应为4。四项均有2个封闭面、2个连通部分、6个奇点，不能将整图6个奇点直接除以2。\nA项：两部分奇点分别为2、4，需1+2=3笔。B项：两部分奇点分别为6、0，需3+1=4笔。C项：两部分奇点分别为4、2，需2+1=3笔。D项：两部分奇点分别为2、4，需1+2=3笔。',
 {'stem':M6_STEM,'candidates':M6_OPTS},['A15','A05'],'sequence'))

def add_class(n,answer,point,classes,correct,metrics,intro,model,refs):
    opts=options_for(correct,answer)
    obj=q(n,'将下面六幅图形分成两类，使每类图形各有共同特征或规律。',answer,point,classification_analysis(intro,classes,metrics,opts,answer),model,refs,'classification')
    obj['options']=[option_text(p) for p in opts];obj['model']['partitions']=opts;obj['model']['class_values']=classes
    QUESTIONS.append(obj)
add_class(7,'A','局部属性 唯一最大面的中心与轴对称',M7_CLASSES,((1,3,6),(2,4,5)),
 ['最大面仅中心对称' if x else '最大面仅轴对称' for x in M7_CLASSES],
 '先找每幅图唯一的最大面，最外排版框不计。六个最大面均为六边形，不能用边数分类；图形外边界也相同。①③⑥最大面仅中心对称，②④⑤最大面仅轴对称。各最大面面积均大于图形外边界面积的一半，故其余任何单面都不可能更大。',
 {'maximum_faces':MAX_FACES,'outer':MAX_OUT},['A09','A21','A07'])
add_class(8,'C','筛选子集 黑块整体对称与轮廓排除',M8_CLASSES,((1,4,5),(2,3,6)),
 ['黑块整体仅中心对称' if x else '黑块整体仅轴对称' for x in M8_CLASSES],
 '只将黑色小方块的整体作为观察对象，不能使用每幅都相同的5×5正方形外轮廓。六图均有8个黑格。①④⑤的黑格集合旋转180°重合，且无对称轴；②③⑥只有一条对称轴，旋转180°不重合。',
 {'masks':[sorted(s) for s in M8_MASKS],'black_counts':[len(s) for s in M8_MASKS]},['A04','A08','A20'])
add_class(9,'D','局部直角分配 同总量下比较各面',M9_CLASSES,((1,4,6),(2,3,5)),
 [f'两面的直角数为{a}+{b}' for a,b in M9_PARTS],
 '六图均有两个五边形面、共10条边、共4个直角，整体数量不能分类。分别数两个凸五边形自身的90°内角：①④⑥为2+2，两面相等；②③⑤为1+3，两面不等。图形转动不改变内角性质。',
 {'face_right_angles':M9_PARTS},['A15','A21','A11'])
add_class(10,'B','图形与线条关系 两折线交点的内外位置',M10_CLASSES,((1,4,5),(2,3,6)),
 ['两条虚线折线的交点在实线闭合图形内部' if x else '两条虚线折线的交点在实线闭合图形外部' for x in M10_CLASSES],
 '将虚线视为连续折线，只找两条虚线之间唯一的交点，再判断其与实线闭合四边形的位置关系。①④⑤的交点在四边形外，②③⑥在四边形内。每图两条虚线与实线边界合计均相交4次，不能用穿边次数分类。',
 {'figures':M10},['A22','A20'])

# Explanation-only aid: the question figures and models above are unchanged.
_q2=next(item for item in QUESTIONS if item['n']==2)
_q2['explanation_image']='e02.png'
_q2['analysis']+='\n外部唯一对称轴的方向及内部折线转向见下图。风筝的轴线连接上下两个顶点，不能把它误读成竖直或水平轴。'

def draw_explanation2():
    im,d=D.canvas(440,1800)
    red='#bb2222';blue='#185f9f'
    centers=[170,455,740,1025,1310,1595]
    items=M2_STEM+[M2_OPTS[3]]
    for i,(x,item) in enumerate(zip(centers,items)):
        kind,outer,inner=item;cy=168
        draw_property(d,x,cy,item)
        # Red dashed line is the unique symmetry axis of the outer carrier.
        a,b=coords(d,x,cy,[(0,-115),(0,115)],angle=math.radians(outer))
        length=math.dist(a,b)
        for t in range(0,math.ceil(length),16):
            e=min(t+10,length)
            p=(a[0]+(b[0]-a[0])*t/length,a[1]+(b[1]-a[1])*t/length)
            end=(a[0]+(b[0]-a[0])*e/length,a[1]+(b[1]-a[1])*e/length)
            d.line([p,end],fill=red,width=4)
        # Blue overwrites only the explanation copy of the inner Z motif.
        d.line(coords(d,x,cy,Z,angle=math.radians(inner)),fill=blue,width=6,joint='curve')
        D.label(d,x,20,('第一组' if i<3 else '第二组')+CIRC[i%3],25)
        d.text((x,308),f'外轴 {outer:+d}°',font=D.font(29),fill=red,anchor='mm')
        d.text((x,348),f'内线 {inner:+d}°',font=D.font(29),fill=blue,anchor='mm')
    d.text((900,405),'外轴以竖直为0°，内线以第一幅为0°；顺时针为正。每组外轴+45°、内线−45°。',font=D.font(29),fill=BLACK,anchor='mm')
    im.save(D.ASSETS/'e02.png',dpi=(300,300))

def draw_all():
    im,d,cs,os=D.sequence(1)
    for p,s in zip(cs,M1_STEM):draw_lattice(d,*p,s)
    D.label(d,*cs[5],'?',92)
    for p,s in zip(os,M1_OPTS):draw_lattice(d,*p,s)
    D.save(im,1)
    im,d,cs,os=D.two_groups(2)
    for p,m in zip(cs,M2_STEM):draw_property(d,*p,m)
    D.label(d,*cs[5],'?',92)
    for p,m in zip(os,M2_OPTS):draw_property(d,*p,m)
    D.save(im,2)
    im,d,cs,os=D.matrix(3)
    for p,s in zip(cs,[s for row in M3_ROWS for s in row][:8]):D.grid(d,*p,s,size=190)
    D.label(d,*cs[8],'?',85)
    for p,s in zip(os,M3_OPTS):D.grid(d,*p,s,size=125)
    D.save(im,3)
    im,d,cs,os=D.two_groups(4)
    for p,m in zip(cs,M4_STEM):draw_point_faces(d,*p,m)
    D.label(d,*cs[5],'?',92)
    for p,m in zip(os,M4_OPTS):draw_point_faces(d,*p,m)
    D.save(im,4)
    im,d,cs,os=D.sequence(5)
    for p,m in zip(cs,M5_STEM):draw_framed(d,*p,m)
    D.label(d,*cs[5],'?',92)
    for p,m in zip(os,M5_OPTS):draw_framed(d,*p,m)
    D.save(im,5)
    im,d,cs,os=D.sequence(6)
    for p,m in zip(cs,M6_STEM):draw_strokes(d,*p,m)
    D.label(d,*cs[5],'?',92)
    for p,m in zip(os,M6_OPTS):draw_strokes(d,*p,m)
    D.save(im,6)
    for n,drawer,models in [(7,draw_maxface,range(6)),(8,lambda d,x,y,m:D.grid(d,x,y,m,n=5,size=200),M8_MASKS),(9,draw_anglepair,range(6)),(10,draw_relation,M10)]:
        im,d,cs=D.classification(n)
        for p,m in zip(cs,models):drawer(d,*p,m)
        D.save(im,n)
    draw_explanation2()

def verify():
    results=[]
    vals=[s==M1_RIGHT for s in M1_OPTS];assert vals==[False,True,False,False]
    assert all(len(s)==3 for s in M1_STEM+M1_OPTS)
    results.append({'n':1,'candidate_pass':vals,'all_black_count':3,'trajectories_independent':True})
    vals=[(a==135 and (b+45)%180==0) for _,a,b in M2_OPTS];assert vals==[False,False,False,True]
    assert all(polygon_symmetries(p)['axis_count']==1 and not polygon_symmetries(p)['central'] for p in OUTLINES)
    results.append({'n':2,'candidate_pass':vals,'outer_each_one_axis':True})
    vals=[s==cc for s in M3_OPTS];assert vals==[True,False,False,False];assert all(len(x)==8 for x in M3_OPTS)
    results.append({'n':3,'candidate_pass':vals,'candidate_black_counts':[len(x) for x in M3_OPTS],'matrix_outer_square':[840,840],'cell_square':[280,280],'option_graphic_size':125})
    vals=[m['right_angles']-m['dots']==m['faces'] for m in M4_OPTS];assert vals==[False,False,True,False]
    results.append({'n':4,'candidate_pass':vals,'candidate_face_count':3,'candidate_dots':4,'all_candidate_total_sides':15,'convex_interior_angle_counts':{str(k):count_angles(p) for k,p in PENTS.items()}})
    vals=[f==t for f,t,r in M5_OPTS];assert vals==[False,False,False,True]
    results.append({'n':5,'candidate_pass':vals,'face_counts_verified_by_euler':{str(f):nfaces(FRAME+s) for f,s in NETS.items()},'raw_internal_segments_each':6,'graphic_frame_counted':True})
    summaries=[graph_summary(m) for m in M6_OPTS];vals=[s['strokes']==4 for s in summaries];assert vals==[False,True,False,False]
    assert all(s['odd_vertices']==6 and s['faces']==2 and s['segments']==9 for s in summaries)
    results.append({'n':6,'candidate_pass':vals,'candidate_stats':summaries,'stem_stats':[graph_summary(m) for m in M6_STEM]})
    maxstats=[polygon_symmetries(p)|{'largest_area':area(p),'total_area':area(MAX_OUT),'other_face_total_area':area(MAX_OUT)-area(p)} for p in MAX_FACES]
    assert all(s['largest_area']>s['other_face_total_area'] for s in maxstats)
    assert all((s['central'] and s['axis_count']==0) or (not s['central'] and s['axis_count']==1) for s in maxstats)
    results.append({'n':7,'faces':maxstats,'maximum_unique_by_area_bound':True,'each_maximum_sides':6})
    assert all(len(s)==8 and mask_sym(s) in [(True,0),(False,1)] for s in M8_MASKS)
    results.append({'n':8,'black_counts':[8]*6,'properties':[{'central':mask_sym(s)[0],'axes':mask_sym(s)[1]} for s in M8_MASKS],'outer_contours_identical':True})
    assert all(sum(x)==4 for x in M9_PARTS)
    assert all(polygon_symmetries(PENTS[k])['axis_count']==0 for k in (1,2,3))
    results.append({'n':9,'per_face_right_angles':M9_PARTS,'total_right_angles':[4]*6,'total_faces':[2]*6,'total_sides':[10]*6,'no_reflex_angles':True,'all_individual_pentagons_asymmetric':True})
    results.append({'n':10,'crossings':[{'point':m['crossing'],'inside':m['inside'],'boundary_crossings':m['boundary_crossings']} for m in M10]})
    for obj in QUESTIONS[6:]:
        model=obj['model'];good=[]
        for partition in model['partitions']:
            good.append(all(len({model['class_values'][i-1] for i in group})==1 for group in partition))
        assert sum(good)==1 and good[CHOICE.index(obj['answer'])]
        next(x for x in results if x['n']==obj['n'])['candidate_pass']=good
    assert [q['n'] for q in QUESTIONS]==list(range(1,11))
    return {'passed':True,'questions':results,'originality':'Original coordinates and distractors; abilities informed by cited local question examples.','layout_rules':{'two_groups_same_horizontal_line':True,'matrix_square':True,'classification_six_stem_figures_native_text_options':True,'image_titles':False}}

if __name__=='__main__':
    draw_all()
    report=verify();(ROOT/'verification_a.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'questions_a.json').write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'questions':len(QUESTIONS),'passed':report['passed']},ensure_ascii=False))
