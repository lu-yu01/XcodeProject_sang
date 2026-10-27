"""Original plane-rule items 1–12 and classification items 28–30."""
from __future__ import annotations
from collections import Counter
from itertools import combinations
import math
import random
import drawkit as k

QUESTIONS=[]
def add(*args,**kwargs):
    q=k.question(*args,**kwargs);QUESTIONS.append(q);return q

# 1. The outer jump grows; the inner arrow has a constant turn.
Q1_POS=[0,1,3,6,2,7]
Q1_OPTIONS=[(6,1),(7,1),(7,3),(3,1)]
def ring_arrow(d,x,y,state):
    pos,angle=state
    d.ellipse((x-88,y-88,x+88,y+88),outline=k.GRAY,width=3)
    for i in range(8):
        a=i*math.pi/4;px=x+88*math.sin(a);py=y-88*math.cos(a)
        d.ellipse((px-7,py-7,px+7,py+7),fill=k.BLACK if i==pos else 'white',outline=k.BLACK,width=3)
    k.arrow(d,x,y,angle,78,6)
def draw1():
    im,d,stem,opts=k.sequence(1)
    for i,center in enumerate(stem[:5]):ring_arrow(d,*center,(Q1_POS[i],i%4))
    k.label(d,*stem[5],'?',100)
    for center,state in zip(opts,Q1_OPTIONS):ring_arrow(d,*center,state)
    k.save(im,1)
add(1,'从所给的五幅图形中观察规律，选择最合适的一项填入问号处。','B','位置规律 递增位移与固定角度旋转',[
    '把外圆八个等距位置看作八个站位。黑点依次顺时针前进1、2、3、4格，所以下一步应前进5格，由右侧位置到左上方。',
    '内部箭头每幅顺时针转90°，第五幅向上，下一幅应向右。B项同时满足黑点位置与箭头方向；A、D项的黑点位置不对，C项箭头向左。故正确答案为B。'])

# 2. Flip all cells, then cyclically shift one column to the right.
Q2_SEED={(0,0),(0,2),(1,0),(1,1),(2,3),(3,1),(3,4),(4,0),(4,3)}
def q2_step(s):return k.shift(k.complement(s,5),dc=1,n=5)
Q2_STATES=[Q2_SEED]
for _ in range(5):Q2_STATES.append(q2_step(Q2_STATES[-1]))
Q2_OPTIONS=[k.complement(Q2_STATES[4],5),k.shift(Q2_STATES[4],n=5),Q2_STATES[5],k.shift(k.complement(Q2_STATES[4],5),dc=-1,n=5)]
def draw2():
    im,d,stem,opts=k.sequence(2)
    for center,s in zip(stem[:5],Q2_STATES):k.grid(d,*center,s,n=5,size=195)
    k.label(d,*stem[5],'?',100)
    for center,s in zip(opts,Q2_OPTIONS):k.grid(d,*center,s,n=5,size=190)
    k.save(im,2)
add(2,'从所给的五幅方格图中选择最合适的一项，填入问号处。','C','样式与位置 黑白翻转后循环平移',[
    '相邻两图按同一规则变化：先把每个小格黑白互换，再把整幅5×5图向右循环平移一列，最右列移至最左列。可用第一幅第一行以及第三幅的边列检验，不能只比较黑格总数。',
    '对第五幅执行两步得到C项。A项只翻转，B项只平移，D项翻转后向左平移；只有C项同时符合。故正确答案为C。'],level='较难')

# 3. Exact planar face counts are related to the separate black dots.
RECT=[((0,0),(4,0)),((4,0),(4,3)),((4,3),(0,3)),((0,3),(0,0))]
Q3_INTERNAL=[
    [((2,0),(2,3))],
    [((0,0),(4,3)),((0,3),(4,0))],
    [((1,0),(1,3)),((3,0),(3,3)),((0,1),(4,1))],
    [((1,0),(1,3)),((3,0),(3,3))],
    [((0,1),(4,1)),((0,2),(4,2)),((0,0),(4,3))],
]
Q3_EDGES=[k.planarize(RECT+s) for s in Q3_INTERNAL]
Q3_FACES=[k.graph_stats(s)['faces'] for s in Q3_EDGES]
Q3_OPTION_EDGE=k.planarize(RECT+[((1,0),(1,3)),((0,2),(4,2)),((0,0),(4,3))])
Q3_TARGET=k.graph_stats(Q3_OPTION_EDGE)['faces']-1
Q3_OPTIONS=[Q3_TARGET,Q3_TARGET+1,Q3_TARGET-1,Q3_TARGET+2]
def face_and_dots(d,x,y,edges,n):
    k.network(d,x,y-30,edges,172,False);k.dots(d,x,y+110,n,22)
def draw3():
    im,d,stem,opts=k.sequence(3)
    for center,edges,faces in zip(stem[:5],Q3_EDGES,Q3_FACES):face_and_dots(d,*center,edges,faces-1)
    k.label(d,*stem[5],'?',100)
    for center,count in zip(opts,Q3_OPTIONS):face_and_dots(d,*center,Q3_OPTION_EDGE,count)
    k.save(im,3)
add(3,'选择最合适的一项填入问号处。每幅图下方的黑点均在线图外，不参与线图的分割。','A','数量关系 最小封闭面与外部点数',[
    '分别数线图中的最小封闭面及其下方黑点。前五幅的封闭面数依次为2、4、6、3、6，黑点数为1、3、5、2、5，始终满足封闭面数比黑点数多1。',
    f'四个候选的线图相同，均有{Q3_TARGET+1}个最小封闭面，故须配{Q3_TARGET}个黑点。只有A项满足；其余项黑点数与封闭面数的差不为1。故正确答案为A。'])

# 4. Two alternating subsequences turn in opposite directions.
FLAG=[(-.85,-.85),(.70,-.85),(.70,-.25),(.10,-.25),(.10,.80),(-.85,.80)]
Q4_STATES=[(0,False),(0,True),(1,False),(3,True),(2,False)]
Q4_OPTIONS=[(3,True),(2,False),(1,True),(2,True)]
def turn_xy(p,r):
    x,y=p
    for _ in range(r%4):x,y=-y,x
    return x,y
def flag(d,x,y,state):
    r,filled=state
    pts=[(x+a*90,y+b*90) for a,b in (turn_xy(p,r) for p in FLAG)]
    d.line(pts+[pts[0]],fill=k.BLACK,width=6,joint='curve')
    a,b=turn_xy((-.42,.30),r);px=x+a*90;py=y+b*90
    d.ellipse((px-11,py-11,px+11,py+11),fill=k.BLACK if filled else 'white',outline=k.BLACK,width=4)
def draw4():
    im,d,stem,opts=k.sequence(4)
    for center,s in zip(stem[:5],Q4_STATES):flag(d,*center,s)
    k.label(d,*stem[5],'?',100)
    for center,s in zip(opts,Q4_OPTIONS):flag(d,*center,s)
    k.save(im,4)
add(4,'从所给的五幅图形中观察规律，选择最合适的一项填入问号处。','D','间隔规律 按空心与实心标记拆分子列',[
    '空心圆出现在第1、3、5幅，它们的轮廓每隔一幅顺时针转90°；实心圆出现在第2、4幅，其轮廓每隔一幅逆时针转90°。',
    '第6幅应沿实心圆子列继续，在第4幅基础上逆时针转90°，得到D项。A、C项方向不对；B项轮廓方向虽对，但标记仍为空心圆。故正确答案为D。'])

# 5. Directed difference of aligned line segments.
EDGE_UNIVERSE=[((x,y),(x+1,y)) for y in range(3) for x in range(2)]+[((x,y),(x,y+1)) for x in range(3) for y in range(2)]
Q5_A={0,1,2,3,5,6,9};Q5_B={1,3,4,6,7}
Q5_C={0,2,4,5,6,8,10,11};Q5_D={0,1,4,8,9,11}
Q5_OPTIONS=[Q5_C-Q5_D,Q5_D-Q5_C,Q5_C^Q5_D,Q5_C&Q5_D]
def matchsticks(d,x,y,indices):
    for idx in indices:
        a,b=EDGE_UNIVERSE[idx]
        d.line((x+(a[0]-1)*76,y+(a[1]-1)*76,x+(b[0]-1)*76,y+(b[1]-1)*76),fill=k.BLACK,width=8)
    for a in {p for i in indices for p in EDGE_UNIVERSE[i]}:
        px=x+(a[0]-1)*76;py=y+(a[1]-1)*76;d.ellipse((px-5,py-5,px+5,py+5),fill=k.BLACK)
def draw5():
    im,d,stem,opts=k.two_groups(5)
    for center,s in zip(stem[:5],[Q5_A,Q5_B,Q5_A-Q5_B,Q5_C,Q5_D]):matchsticks(d,*center,s)
    k.label(d,*stem[5],'?',100)
    for center,s in zip(opts,Q5_OPTIONS):matchsticks(d,*center,s)
    k.save(im,5)
add(5,'两组图形遵循相同的组合规律，选择最合适的一项填入问号处。','A','样式运算 定向删除重合线段',[
    '把每组三幅图放在相同位置比较：第三幅保留第一幅中存在、第二幅中不存在的线段。共同线段被删除；只在第二幅出现的线段不会被补入。',
    '将此规则用于第二组，得到A项。B项把删除方向颠倒；C项把两图的全部非共同线段都保留；D项只保留共同线段。故正确答案为A。'])

# 6. Same-size connected grid networks with different Euler stroke counts.
def choose_stroke_graphs():
    result={i:[] for i in range(1,5)}
    universe=[((x,y),(x+1,y)) for y in range(3) for x in range(3)]+[((x,y),(x,y+1)) for x in range(4) for y in range(2)]
    for combo in combinations(range(len(universe)),14):
        edges={tuple(sorted(universe[i])) for i in combo}
        stats=k.graph_stats(edges)
        if stats['components']==1 and len(stats['degrees'])==12 and stats['strokes'] in result:
            result[stats['strokes']].append(edges)
    return result
Q6_POOL=choose_stroke_graphs()
Q6_STEM=[Q6_POOL[1][0],Q6_POOL[2][1],Q6_POOL[3][0],Q6_POOL[2][3],Q6_POOL[3][2]]
Q6_OPTIONS=[Q6_POOL[1][-1],Q6_POOL[3][-1],Q6_POOL[2][-1],Q6_POOL[4][0]]
def draw6():
    im,d,stem,opts=k.two_groups(6)
    for center,edges in zip(stem[:5],Q6_STEM):k.network(d,*center,edges,198)
    k.label(d,*stem[5],'?',100)
    for center,edges in zip(opts,Q6_OPTIONS):k.network(d,*center,edges,198)
    k.save(im,6)
add(6,'两组线图遵循相同的数量变化，选择最合适的一项填入问号处。图中圆点均为实际连接点，作图时每条线段只能经过一次。','D','数量规律 连通线图的最少笔画数',[
    '所有图均连通。连通线图的最少笔画数可由奇数度顶点数判断：有2、4、6、8个奇点时分别需1、2、3、4笔。第一组的奇点数依次为2、4、6，即最少笔画数为1、2、3。',
    '第二组已给两图分别有4、6个奇点，问号处应有8个奇点，最少4笔。A、B、C、D的最少笔画数依次为1、3、2、4，只有D项符合。故正确答案为D。'],level='较难')

# 7. A cyclic three-tone state transition plus a quarter turn.
Q7_BASE=(0,1,2,0,2,1,1,0,2)
Q7_BOTTOM=(2,0,1,1,2,0,0,1,2)
def tone_rotate(s):return tuple(s[(2-c)*3+r] for r in range(3) for c in range(3))
def tone_step(s):return tone_rotate(tuple((v+1)%3 for v in s))
Q7_B=tone_step(Q7_BASE);Q7_C=tone_step(Q7_B)
Q7_E=tone_step(Q7_BOTTOM);Q7_CORRECT=tone_step(Q7_E)
Q7_OPTIONS=[tuple((v+1)%3 for v in Q7_E),Q7_CORRECT,tone_rotate(tuple((v-1)%3 for v in Q7_E)),tone_rotate(tone_rotate(tone_rotate(tuple((v+1)%3 for v in Q7_E))))]
def tones(d,x,y,s,size=180):
    cell=size/3
    for r in range(3):
        for c in range(3):
            rect=(x-size/2+c*cell,y-size/2+r*cell,x-size/2+(c+1)*cell,y-size/2+(r+1)*cell)
            d.rectangle(rect,fill=['white','#999999',k.BLACK][s[r*3+c]],outline=k.GRAY,width=2)
def draw7():
    im,d,stem,opts=k.two_groups(7)
    for center,s in zip(stem[:5],[Q7_BASE,Q7_B,Q7_C,Q7_BOTTOM,Q7_E]):tones(d,*center,s)
    k.label(d,*stem[5],'?',100)
    for center,s in zip(opts,Q7_OPTIONS):tones(d,*center,s)
    k.save(im,7)
add(7,'两组方格图遵循相同的变化，选择最合适的一项填入问号处。小格只有白、灰、黑三种状态。','B','样式与方向 三色循环和整体旋转',[
    '每一步均先将颜色按白→灰→黑→白循环一次，再把整个3×3图顺时针旋转90°。第一组两次变化都满足；跟踪左上格的位置与颜色可作交叉验证。',
    '第二组第二幅经过同样操作得到B项。A项只改变颜色而未旋转；C项按相反的颜色循环变化；D项逆时针旋转。故正确答案为B。'],level='较难')

# 8. Face adjacency, instead of merely counting faces.
def square_at(x,y):return[(x,y),(x+1,y),(x+1,y+1),(x,y+1)]
def fan(vertices,center):return[[center,vertices[i],vertices[(i+1)%len(vertices)]] for i in range(len(vertices))]
PENT=[(0,0),(3,0),(4,2),(2,4),(0,3)]
CHAIN_TRI=[[(0,0),(4,0),(3,1),(0,1)],[(0,1),(3,1),(2,2),(0,2)],[(0,2),(2,2),(0,4)]]
Q8_REGIONS=[
    [square_at(0,0),square_at(1,0),square_at(2,0)],
    [square_at(0,0),square_at(1,0),square_at(1,1)],
    CHAIN_TRI,
    fan([(0,0),(4,0),(2,4)],(2,1)),
    fan([(0,0),(4,1),(1,4)],(1,1)),
]
Q8_OPTIONS=[
    [[turn_xy(p,1) for p in region] for region in CHAIN_TRI],
    [[(0,0),(3,0),(3,2)],[(0,0),(3,2),(0,2)]],
    fan([(0,0),(4,0),(0,4)],(1,1)),
    fan([(0,0),(3,0),(3,3),(0,3)],(1,1)),
]
def region_edges(regions):
    return [{tuple(sorted((a,b))) for a,b in zip(r,r[1:]+r[:1])} for r in regions]
def adjacency_signature(regions):
    es=region_edges(regions)
    return len(regions),sum(bool(a&b) for a,b in combinations(es,2))
def region_picture(d,x,y,regions,size=180):
    edges=set().union(*region_edges(regions));k.network(d,x,y,edges,size,False)
def draw8():
    im,d,stem,opts=k.two_groups(8)
    for center,s in zip(stem[:5],Q8_REGIONS):region_picture(d,*center,s)
    k.label(d,*stem[5],'?',100)
    for center,s in zip(opts,Q8_OPTIONS):region_picture(d,*center,s)
    k.save(im,8)
add(8,'两组图形各有共同特征，选择同时符合第二组特征的一项填入问号处。','C','拓扑关系 最小封闭面的共边关系',[
    '五幅已知图都包含3个最小封闭面，单数封闭面无法区分两组。第一组每图只有两对小面共享一段边，三个小面形成一条相邻链；第二组中三个小面两两共边，共有三对。只在一个点接触不算共边。',
    'C项有3个最小封闭面且两两共边。A项仍是相邻链；B项仅2个小面；D项是4个小面。故正确答案为C。'],level='较难')

# 9. Cellwise equivalence (XNOR), with neither reflection nor rotation.
Q9_ROWS=[
    [{(0,0),(0,1),(1,1),(2,0)},{(0,1),(1,0),(1,1),(2,2)}],
    [{(0,2),(1,0),(1,2),(2,1)},{(0,0),(0,2),(1,0),(2,2)}],
    [{(0,0),(1,0),(1,1),(2,2)},{(0,1),(1,1),(1,2),(2,0)}],
]
def xnor(a,b):return k.complement(a^b,3)
Q9_A,Q9_B=Q9_ROWS[2]
Q9_OPTIONS=[Q9_A^Q9_B,Q9_A|Q9_B,Q9_A&Q9_B,xnor(Q9_A,Q9_B)]
def draw9():
    im,d,stem,opts=k.matrix(9)
    for r,(a,b) in enumerate(Q9_ROWS):
        k.grid(d,*stem[r*3],a,3,178);k.grid(d,*stem[r*3+1],b,3,178)
        if r<2:k.grid(d,*stem[r*3+2],xnor(a,b),3,178)
        else:k.label(d,*stem[r*3+2],'?',100)
    for center,s in zip(opts,Q9_OPTIONS):k.grid(d,*center,s,3,120)
    k.save(im,9)
add(9,'观察九宫格中图形的规律，选择最合适的一项填入问号处。','D','黑白运算 相同保黑与不同留白',[
    '按行比较前两图同一位置的小格：颜色相同，不论同黑还是同白，第三图对应格为黑；颜色不同则为白。这是逐格“同色保黑”的运算，前两行均能逐格验证。',
    '第三行结果为D项。A项恰好取了相反的黑白结果；B项保留任一图的黑格；C项只保留两图共同的黑格，漏掉了同白也应变黑的位置。故正确答案为D。'])

# 10. Two independent regularities within each matrix cell.
Q10_OPTIONS=[(2,8),(0,9),(2,9),(1,9)]
def arrow_dots(d,x,y,state,size=1):
    angle,count=state;k.arrow(d,x,y-25*size,angle,90*size,6)
    cols=3
    for i in range(count):
        r,c=divmod(i,cols);px=x+(c-1)*23*size;py=y+45*size+r*23*size
        d.ellipse((px-5,py-5,px+5,py+5),fill=k.BLACK)
def draw10():
    im,d,stem,opts=k.matrix(10)
    for r in range(3):
        for c in range(3):
            at=stem[r*3+c]
            if r==c==2:k.label(d,*at,'?',100)
            else:arrow_dots(d,*at,((r+2*c)%4,(r+1)*(c+1)))
    for center,s in zip(opts,Q10_OPTIONS):arrow_dots(d,*center,s,.70)
    k.save(im,10)
add(10,'观察九宫格中图形的规律，选择最合适的一项填入问号处。','C','数量与方向 行列倍数和双向旋转',[
    '黑点按行分别为1、2、3；2、4、6；3、6、问号，即每行前两组数量之和等于第三组，按列也成立，因此缺9个黑点。',
    '箭头沿每行依次转180°，沿每列向下转90°。第三行方向应依次向下、向上、向下，故缺图箭头向下。C项同时满足；A项少1个点，B、D项箭头方向不对。故正确答案为C。'])

# 11. Polygon-side addition with dot subtraction.
Q11_ROWS=[[(3,3),(3,1),(6,2)],[(4,4),(3,1),(7,3)],[(5,3),(3,2),(8,1)]]
Q11_OPTIONS=[(6,1),(8,1),(8,5),(7,1)]
def polygon_dots(d,x,y,state,size=1):
    sides,count=state;k.polygon(d,x,y-10*size,sides,85*size,width=5)
    k.dots(d,x,y+6*size,count,20*size)
def draw11():
    im,d,stem,opts=k.matrix(11)
    for r,row in enumerate(Q11_ROWS):
        for c,s in enumerate(row):
            if r==c==2:k.label(d,*stem[r*3+c],'?',100)
            else:polygon_dots(d,*stem[r*3+c],s)
    for center,s in zip(opts,Q11_OPTIONS):polygon_dots(d,*center,s,.68)
    k.save(im,11)
add(11,'观察九宫格中每行图形的关系，选择最合适的一项填入问号处。','B','数量关系 外轮廓边数相加与内部点数相减',[
    '按行观察，第三图外轮廓边数等于前两图边数之和：3+3=6，4+3=7，所以第三行应为5+3=8边形。内部黑点数则等于前两图点数之差：3-1=2，4-1=3，所以第三行应为3-2=1。',
    'B项是内部1点的八边形。A、D项边数不足；C项把点数也相加为5。故正确答案为B。'])

# 12. Overlay on eight possible rays, then reflect left/right.
Q12_ROWS=[[{0,1,3,6},{1,2,3,5}],[{0,2,4,7},{2,3,5,7}],[{1,2,5,7},{0,2,3,6}]]
def ray_mirror(s):return {(-i)%8 for i in s}
def ray_step(a,b):return ray_mirror(a^b)
Q12_A,Q12_B=Q12_ROWS[2]
Q12_OPTIONS=[ray_step(Q12_A,Q12_B),Q12_A^Q12_B,ray_mirror(Q12_A|Q12_B),ray_mirror(Q12_A&Q12_B)]
def rays(d,x,y,s,r=85):
    d.ellipse((x-r,y-r,x+r,y+r),outline='#999999',width=2)
    for i in range(8):
        a=i*math.pi/4;px=x+r*math.sin(a);py=y-r*math.cos(a)
        d.ellipse((px-4,py-4,px+4,py+4),fill=k.GRAY)
        if i in s:d.line((x,y,px,py),fill=k.BLACK,width=7)
    d.ellipse((x-6,y-6,x+6,y+6),fill=k.BLACK)
def draw12():
    im,d,stem,opts=k.matrix(12)
    for r,(a,b) in enumerate(Q12_ROWS):
        rays(d,*stem[r*3],a);rays(d,*stem[r*3+1],b)
        if r<2:rays(d,*stem[r*3+2],ray_step(a,b))
        else:k.label(d,*stem[r*3+2],'?',100)
    for center,s in zip(opts,Q12_OPTIONS):rays(d,*center,s,61)
    k.save(im,12)
add(12,'观察九宫格中每行的图形，选择最合适的一项填入问号处。细圆及其八个等距点只作位置参照。','A','样式与方向 射线去同后左右翻转',[
    '前两图叠加时，同一方向两图都有的粗线删除，只有一图有的粗线保留；随后把结果左右翻转，形成第三图。细圆和八个定位点始终不变，不参与运算。',
    '第三行依次完成去同和翻转，得到A项。B项只去同未翻转；C项把粗线求并后翻转；D项只保留共同粗线再翻转。故正确答案为A。'],level='较难')

# 28. Two degree-three junctions are adjacent or separated by degree-two nodes.
def theta(paths):
    return {tuple(sorted((a,b))) for p in paths for a,b in zip(p,p[1:])}
THETA_A=theta([[(0,0),(4,0)],[(0,0),(2,-2),(4,0)],[(0,0),(0,2),(2,2),(4,2),(4,0)]])
THETA_B=theta([[(0,0),(2,0),(4,0)],[(0,0),(2,-2),(4,0)],[(0,0),(1,2),(3,2),(4,0)]])
def transform_edges(edges,turn=0,shear=0):
    def fn(p):
        x,y=turn_xy(p,turn);return(x+shear*y,y)
    return {tuple(sorted((fn(a),fn(b)))) for a,b in edges}
Q28_GRAPHS=[THETA_A,THETA_B,transform_edges(THETA_B,1),transform_edges(THETA_A,1),transform_edges(THETA_A,2,.3),transform_edges(THETA_B,2,.2)]
Q28_OPTIONS=['①②④，③⑤⑥','①④⑤，②③⑥','①③⑤，②④⑥','①④⑥，②③⑤']
def junctions_adjacent(edges):
    st=k.graph_stats(edges);junctions=[v for v,n in st['degrees'].items() if n==3]
    return len(junctions)==2 and junctions[1] in st['adjacency'][junctions[0]]
def draw28():
    im,d,centers=k.classification(28)
    for center,edges in zip(centers,Q28_GRAPHS):k.network(d,*center,edges,218)
    k.save(im,28)
add(28,'将下列六幅线图分为两类，使每类具有共同特征。图中小圆点均为实际连接点。分类正确的是：','B','拓扑分类 三线连接点的直接邻接',[
    '六图都是连通线图，均有两个三线连接点和四个二线连接点，封闭面数也相同，单纯数点、数线或数面不能区分。',
    '①④⑤的两个三线连接点由一条未经过其他圆点的线段直接相连；②③⑥的两个三线连接点之间，每条连接路径都经过至少一个二线连接点。因此应分①④⑤与②③⑥。故正确答案为B。'],options=Q28_OPTIONS,level='较难')

# 29. Equal-area polyomino outlines with two or three reentrant right angles.
def poly_edges(cells):
    edges=Counter()
    for x,y in cells:
        corners=[(x,y),(x+1,y),(x+1,y+1),(x,y+1)]
        edges.update(tuple(sorted((a,b))) for a,b in zip(corners,corners[1:]+corners[:1]))
    return {e for e,n in edges.items() if n==1}
def concave_count(cells):
    vertices={(x+dx,y+dy) for x,y in cells for dx,dy in ((0,0),(1,0),(0,1),(1,1))}
    return sum(sum((x+dx,y+dy) in cells for dx,dy in ((-1,-1),(-1,0),(0,-1),(0,0)))==3 for x,y in vertices)
def canonical_poly(cells):
    variants=[]
    for reflect in (False,True):
        for turn in range(4):
            pts=[turn_xy((-x if reflect else x,y),turn) for x,y in cells]
            mx=min(x for x,y in pts);my=min(y for x,y in pts)
            variants.append(tuple(sorted((x-mx,y-my) for x,y in pts)))
    return min(variants)
def select_polys():
    rng=random.Random(281025);chosen={2:[],3:[]};seen=set()
    for _ in range(10000):
        cells={(0,0)}
        while len(cells)<8:
            x,y=rng.choice(sorted(cells));dx,dy=rng.choice([(1,0),(-1,0),(0,1),(0,-1)]);cells.add((x+dx,y+dy))
        key=canonical_poly(cells);count=concave_count(cells)
        if key in seen or count not in chosen:continue
        edges=poly_edges(cells)
        # Hole-free outlines, and no diagonally touching self-pinched boundary.
        degrees=Counter(v for e in edges for v in e)
        if any(v!=2 for v in degrees.values()) or k.graph_stats(edges)['components']!=1:continue
        if len(chosen[count])<3:chosen[count].append(set(key));seen.add(key)
        if all(len(v)==3 for v in chosen.values()):break
    assert all(len(v)==3 for v in chosen.values())
    return [chosen[2][0],chosen[3][0],chosen[3][1],chosen[2][1],chosen[3][2],chosen[2][2]]
Q29_SHAPES=select_polys()
Q29_OPTIONS=['①②④，③⑤⑥','①③⑥，②④⑤','①④⑤，②③⑥','①④⑥，②③⑤']
def draw29():
    im,d,centers=k.classification(29)
    for center,cells in zip(centers,Q29_SHAPES):k.network(d,*center,poly_edges(cells),218,False)
    k.save(im,29)
add(29,'将下列六幅轮廓图分为两类，使每类具有共同特征，分类正确的是：','D','属性与数量分类 内凹拐点的数量',[
    '沿轮廓逐个检查向图形内部凹入的拐点，这些位置的多边形内角为270°，不能把向外凸出的90°内角混入。①④⑥均有2个内凹拐点；②③⑤均有3个内凹拐点。',
    '六图均为单一闭合轮廓，外观的长短、朝向和面积不是本题的分类依据。正确分法为①④⑥与②③⑤。故正确答案为D。'],options=Q29_OPTIONS)

# 30. Cyclic order of three distinct symbols, preserved under rotation.
Q30_STATES=[((3,4,5),0),((3,5,4),1),((4,3,5),2),((5,3,4),1),((5,4,3),0),((4,5,3),2)]
Q30_OPTIONS=['①②⑥，③④⑤','①③④，②⑤⑥','①④⑥，②③⑤','①⑤⑥，②③④']
def clockwise_signature(state):
    seq,_=state;at=seq.index(3);return tuple(seq[(at+i)%3] for i in range(3))
def triple_symbols(d,x,y,state):
    seq,rotation=state
    for i,sides in enumerate(seq):
        a=-math.pi/2+i*2*math.pi/3+rotation*math.pi/3
        px=x+79*math.cos(a);py=y+79*math.sin(a)
        k.polygon(d,px,py,sides,30,angle=-math.pi/2+(i+rotation)*.2,width=4)
    d.ellipse((x-4,y-4,x+4,y+4),fill=k.BLACK)
def draw30():
    im,d,centers=k.classification(30)
    for center,state in zip(centers,Q30_STATES):triple_symbols(d,*center,state)
    k.save(im,30)
add(30,'将下列六幅图分为两类，使每类具有共同的相对位置关系，分类正确的是：','C','位置分类 三种轮廓的顺时针绕序',[
    '每幅都包含三角形、四边形、五边形各一个，数量相同。以三角形为起点沿中心点顺时针观察，①④⑥均依次遇到三角形、四边形、五边形；②③⑤均依次遇到三角形、五边形、四边形。',
    '整幅旋转或单个小图形改变朝向，不会改变三者围绕中心点的绕序。因此正确分法为①④⑥与②③⑤。故正确答案为C。'],options=Q30_OPTIONS)

def draw_all():
    for n in list(range(1,13))+[28,29,30]:globals()[f'draw{n}']()

def verify():
    assert [i for i,s in enumerate(Q1_OPTIONS) if s==(7,1)]==[1]
    assert len({frozenset(s) for s in Q2_OPTIONS})==4 and Q2_OPTIONS[2]==q2_step(Q2_STATES[4])
    assert Q3_FACES==[2,4,6,3,6],Q3_FACES
    assert [c==Q3_TARGET for c in Q3_OPTIONS]==[True,False,False,False]
    assert Q4_OPTIONS.count((2,True))==1 and Q4_OPTIONS[3]==(2,True)
    assert len({frozenset(x) for x in Q5_OPTIONS})==4 and Q5_OPTIONS[0]==Q5_C-Q5_D
    assert [k.graph_stats(s)['strokes'] for s in Q6_STEM]==[1,2,3,2,3]
    assert [k.graph_stats(s)['strokes'] for s in Q6_OPTIONS]==[1,3,2,4]
    assert len(set(Q7_OPTIONS))==4 and Q7_OPTIONS[1]==tone_step(Q7_E)
    assert [adjacency_signature(s) for s in Q8_REGIONS]==[(3,2)]*3+[(3,3)]*2
    assert [adjacency_signature(s) for s in Q8_OPTIONS]==[(3,2),(2,1),(3,3),(4,4)]
    assert len({frozenset(s) for s in Q9_OPTIONS})==4 and Q9_OPTIONS[3]==xnor(Q9_A,Q9_B)
    assert Q10_OPTIONS.count((2,9))==1 and Q10_OPTIONS[2]==(2,9)
    assert all(row[2]==(row[0][0]+row[1][0],row[0][1]-row[1][1]) for row in Q11_ROWS)
    assert Q11_OPTIONS[1]==(8,1) and len(set(Q11_OPTIONS))==4
    assert len({frozenset(s) for s in Q12_OPTIONS})==4 and Q12_OPTIONS[0]==ray_step(Q12_A,Q12_B)
    assert [junctions_adjacent(e) for e in Q28_GRAPHS]==[True,False,False,True,True,False]
    assert all(sorted(k.graph_stats(e)['degrees'].values())==[2,2,2,2,3,3] for e in Q28_GRAPHS)
    assert [concave_count(s) for s in Q29_SHAPES]==[2,3,3,2,3,2]
    assert [clockwise_signature(s) for s in Q30_STATES]==[(3,4,5),(3,5,4),(3,5,4),(3,4,5),(3,5,4),(3,4,5)]
    return {'items':list(range(1,13))+[28,29,30],'q3_faces':Q3_FACES,'q6_strokes':[1,2,3,2,3,4],
            'q28_adjacent':[1,4,5],'q29_concave':[2,3,3,2,3,2],'q30_clockwise':[1,4,6]}

if __name__=='__main__':
    print(verify());draw_all()
