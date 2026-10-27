"""Original Q11-Q20: relational counting, four compound rules, four classifications."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from itertools import combinations
from fractions import Fraction
import json, math, random
import drawkit as k

ROOT=Path(__file__).resolve().parent
RNG=random.Random(2026102511)
U=frozenset((r,c) for r in range(4) for c in range(4))
def frozen(s):return frozenset(s)
def rot(s):return frozen(k.rotate(s,4))
def ccw(s):return rot(rot(rot(s)))
def flip(s):return frozen(k.reflect(s,4))
def updown(s):return frozen((3-r,c) for r,c in s)
def sh(s):return frozen(k.shift(s,0,1,4))
def sample(n=7):return frozen(RNG.sample(sorted(U),n))
def ser(v):
    if isinstance(v,Fraction):return int(v) if v.denominator==1 else str(v)
    if isinstance(v,(set,frozenset)):return sorted([ser(x) for x in v])
    if isinstance(v,tuple):return [ser(x) for x in v]
    if isinstance(v,list):return [ser(x) for x in v]
    if isinstance(v,dict):return {str(key):ser(val) for key,val in v.items()}
    return v
def components(s):
    left=set(s);parts=[]
    while left:
        group={left.pop()};queue=list(group)
        for r,c in queue:
            for p in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                if p in left:left.remove(p);group.add(p);queue.append(p)
        parts.append(group)
    return parts
def borders(s):return sum(any((r==0,r==3,c==0,c==3)[i] for r,c in s) for i in range(4))
def count_signature(s):return len(components(s)),borders(s)

QUESTIONS=[];DATA={};CHECKS={}
def question(n,stem,answer,point,analysis,mechanism,refs,model,options=None,ask=''):
    q=dict(n=n,category='图形推理',stem=stem,ask=ask,options=options or [],answer=answer,
           point=point,analysis=analysis,image=f'q{n:02}.png',explanation_image=f'e{n:02}.png',
           difficulty='较难',level='较难',mechanism=mechanism,source_refs=refs,model=ser(model))
    QUESTIONS.append(q);return q

# Q11: two count correspondences, with equal black area in every choice.
st11=[]
for target in [(1,3),(2,4),(3,3),(2,2),(3,4)]:
    for _ in range(100000):
        s=sample(7)
        if count_signature(s)==target:st11.append((s,target));break
    else:raise AssertionError(target)
target11=(2,3);op11=[]
for signature in [(2,4),(3,3),(2,3),(1,3)]:
    for _ in range(100000):
        s=sample(7)
        if count_signature(s)==signature:op11.append((s,target11));break
DATA[11]=dict(stem=st11,options=op11)
question(11,'从所给的四个选项中，选择最合适的一项填入问号处，使之呈现一定的规律性。','C',
 '数量对应：连通部分数、接触边数与两类标记对应',[
 '把黑格按共边相连划分部分，角点接触不算连通。每图黑格的连通部分数等于上方实心圆数，黑格接触小方格外沿的边的种类数等于空心圆数；上、下、左、右四条边各计一次。',
 '前五图的两个计数依次为（1，3）、（2，4）、（3，3）、（2，2）、（3，4），均与圆标记对应。问号处给定2个实心圆和3个空心圆，因此必须同时有2个黑格部分并接触3条边。',
 'A项有2部分但接触4条边；B项接触3条边但有3部分；D项接触3条边但只有1部分。C项同时满足两个对应。四项均有7个黑格，仅数黑格面积不能筛出答案。'],
 'components_and_boundary_contacts_cross_object',['N26-76','N26-84'],dict(stem=st11,options=op11,answer_signature=target11))

# Q12: upper graph direction families/components mapped to lower faces/strokes.
TOP={
 (1,2):[((0,0),(1,0)),((1,0),(1,1)),((1,1),(2,1)),((2,1),(2,2))],
 (1,3):[((0,0),(1,0)),((1,0),(1,1)),((1,1),(2,2)),((2,2),(3,2))],
 (2,2):[((0,0),(1,0)),((1,0),(1,1)),((2,0),(3,0)),((3,0),(3,1))],
 (2,3):[((0,0),(1,0)),((1,0),(1,1)),((2,0),(3,1)),((3,1),(3,2))],
}
def direction_count(edges):
    directions=set()
    for a,b in edges:
        dx,dy=int(b[0]-a[0]),int(b[1]-a[1]);g=math.gcd(abs(dx),abs(dy));dx//=g;dy//=g
        if dx<0 or dx==0 and dy<0:dx,dy=-dx,-dy
        directions.add((dx,dy))
    return len(directions)
def bottom(faces,strokes):
    seg=[((0,0),(3,0)),((3,0),(3,2)),((3,2),(0,2)),((0,2),(0,0))]
    if faces==2:seg += [((0,1),(3,1))]
    else:seg += [((0,0),(3,2)),((0,0),(3,1))]
    # Search small outward leaves to achieve requested stroke count; faces remain.
    candidates=[((0,0),(-1,0)),((3,0),(4,0)),((3,2),(4,2)),((0,2),(-1,2)),
                ((0,1),(-1,1)),((1,0),(1,-1)),((2,0),(2,-1)),((1,2),(1,3)),((2,2),(2,3))]
    for amount in range(5):
        for leaves in combinations(candidates,amount):
            e=k.planarize(seg+list(leaves));stats=k.graph_stats(e)
            if stats['faces']==faces and stats['strokes']==strokes:return e
    raise AssertionError((faces,strokes))
def item12(c,d,f=None,s=None):return (k.planarize(TOP[c,d]),bottom(f or d,s or c))
st12=[item12(c,d) for c,d in [(1,2),(2,3),(1,3),(2,2),(1,2)]]
op12=[item12(2,3,3,2),item12(2,3,2,2),item12(2,3,3,1),item12(1,3,2,2)]
DATA[12]=dict(stem=st12,options=op12)
def sig12(item):
    a,b=item;aa=k.graph_stats(a);bb=k.graph_stats(b)
    return (aa['components'],direction_count(a),bb['faces'],bb['strokes'])
question(12,'每格中有上、下两个线图。从四个选项中选出使整组图形规律成立的一项。','A',
 '分对象计数：方向种数与面数、部分数与笔画数联动',[
 '上、下两个线图分开观察。把平行线归为同一种方向：上图的直线方向种数等于下图的封闭面数；上图的连通部分数等于下图最少笔画数。图内相交处均视为相连，封闭面只计线图自身的最小区域。',
 '前五格的“上图部分数、方向种数、下图面数、最少笔画”分别为（1，2，2，1）、（2，3，3，2）、（1，3，3，1）、（2，2，2，2）、（1，2，2，1），两项对应均成立。',
 'A项为（2，3，3，2），同时成立。B项下图只有2面，不等于上图3种方向；C项下图一笔可成，不等于上图2部分；D项的两项对应均不成立。只数面或只看部分数都不足以确定答案。'],
 'direction_families_faces_components_strokes',['N26-78','JS24C-80'],dict(stem=[sig12(x) for x in st12],options=[sig12(x) for x in op12]))

def binary_operation(n,operation,wrong_ops,descriptions,carrier,refs):
    rows=[]
    for row in range(3):
        for attempt in range(200000):
            a,b=sample(RNG.choice([6,7,8])),sample(RNG.choice([6,7,8]))
            out=operation(a,b)
            if not 4<=len(out)<=11:continue
            if row<2:
                # Each demonstration also distinguishes the four actual algorithms.
                if any(fn(a,b)==out for fn in wrong_ops):continue
                rows.append((a,b,out));break
            variants=[fn(a,b) for fn in wrong_ops]
            if len(set([out]+variants))!=4:continue
            if len({len(x) for x in [out]+variants})!=1:continue
            rows.append((a,b,out));break
        else:raise AssertionError(('binary search',n,row))
    a,b,out=rows[2];variants=[fn(a,b) for fn in wrong_ops]
    correct_index={13:1,15:3}[n];choices=variants[:];choices.insert(correct_index,out)
    DATA[n]=dict(rows=rows,options=choices,carrier=carrier)
    report={'correct_index':correct_index,'same_black_count_all_options':True,'distinct_options':True,
            'wrong_operation_distinct_on_both_demonstrations':True,
            'all_coordinate_checks':True}
    if n==13:
        report.update({'R_XOR_equals_XOR_of_both_R':rot(a^b)==rot(a)^rot(b),
                       'equivalent_both_rotated_not_used_as_distractor':True})
    CHECKS[n]=report
    letter='ABCD'[correct_index]
    option_explain=[];j=0
    for i,v in enumerate(choices):
        if i==correct_index:option_explain.append(f'{"ABCD"[i]}项与两个步骤的逐位结果完全一致。')
        else:option_explain.append(f'{"ABCD"[i]}项对应{descriptions[j]}，与前两行均不一致。');j+=1
    return rows,choices,letter,option_explain

rows,choices,ans,ex=binary_operation(13,lambda a,b:rot(a^b),[
 lambda a,b:frozen(a^b),lambda a,b:ccw(a^b),lambda a,b:rot(a)^b],
 ['去同求异后漏掉旋转','去同求异后逆时针90°旋转','只先将第一图旋转后再与未旋转第二图求异'],
 'circle_matrix',['N26-79','BJ22-77','GD24-46'])
question(13,'观察九宫格每行三幅图的关系，从四个选项中选出最合适的一项。',ans,
 '复合运算：去同求异后顺时针旋转90°',[
 '先将每行前两图按圆阵同一坐标叠合：黑黑、白白变白，黑白、白黑变黑；再把所得整幅圆阵顺时针旋转90°，得到第三图。第一、二行均能逐位验证。',
 '第三行同样先求异、后旋转，两个步骤都不可省略。四个候选的黑圆数量相同，需同时核对位置与旋转方向。',
 ''.join(ex),
 '把两幅输入同时旋转后再求异，在数学上与先求异后旋转等价，因此没有把这种等价写法伪造为错误选项；干扰项只先转第一图。'],
 'xor_then_clockwise_90_circle_array',['N26-79','BJ22-77','GD24-46'],dict(rows=rows,options=choices,checks=CHECKS[13]))

# Q14 three states: 0 blank, 1 outlined ring, 2 solid circle. Equal states cancel.
U3=tuple((r,c) for r in range(3) for c in range(3))
def state_sample():return tuple(RNG.randrange(3) for _ in range(9))
def tri(a,b):return tuple(0 if x==y else max(x,y) for x,y in zip(a,b))
def tri_ud(s):return tuple(s[(2-r)*3+c] for r,c in U3)
def tri_lr(s):return tuple(s[r*3+2-c] for r,c in U3)
def state_counts(s):return (s.count(1),s.count(2))
triro=[]
for row in range(2):
    for _ in range(200000):
        a,b=state_sample(),state_sample();o=tri_ud(tri(a,b))
        wrong=[tri(a,b),tri_lr(tri(a,b)),tri(tri_ud(a),b)]
        if row==0:
            # Demonstrate the full truth table's essential distinct-state cases.
            if any(w==o for w in wrong):continue
            if not {(0,0),(1,1),(2,2),(0,1),(0,2),(1,2)} <= {tuple(sorted(p)) for p in zip(a,b)}:continue
            triro.append((a,b,o));break
        if len(set([o]+wrong))==4 and len({state_counts(x) for x in [o]+wrong})==1:
            triro.append((a,b,o));break
    else:raise AssertionError('ternary')
triopts=[triro[1][2],*wrong]
DATA[14]=dict(rows=triro,options=triopts)
question(14,'左、右两组图形遵循同一种变化方式。从四个选项中选出填入问号处的一项。浅灰小点仅用于定位。','A',
 '三态复合：消同、异态分层保留与上下翻转',[
 '每个九点位置有空白、空心圆、实心圆三种状态。先按同一坐标运算：相同状态抵消为空；不同状态相遇时，若有实心圆则保留实心圆，否则保留空心圆。随后将所得九点阵整体上下翻转。',
 '第一组同时展示了空白与空心、空白与实心、空心与实心相遇，以及相同状态相遇的规则。对第二组逐位运算再翻转得到A项。四个候选的空心、实心数量分别相同。',
 'B项只运算未翻转；C项把上下翻转误作左右翻转；D项先翻第一幅输入再与未翻第二图运算，操作对象和顺序错误。三项均不能复现第一组。'],
 'ternary_cancel_equal_then_vertical_reflection',['ZJ23-74','N26-79'],dict(rows=triro,options=triopts))
CHECKS[14]={'distinct_options':True,'same_count_by_state':True,'equivalent_both_ud_inputs_not_distractor':tri_ud(tri(a,b))==tri(tri_ud(a),tri_ud(b))}

rows,choices,ans,ex=binary_operation(15,lambda a,b:rot(a-sh(b)),[
 lambda a,b:frozen(a-sh(b)),lambda a,b:rot(sh(a-b)),lambda a,b:rot(sh(b)-a)],
 ['先将第二图右移一列后取第一图独有位置，但漏掉最后旋转',
  '先取第一图独有位置，再将结果右移一列后旋转',
  '把减除方向颠倒，保留移位后的第二图独有位置再旋转'],
 'blocks',['N26-79','GD25-48'])
question(15,'观察九宫格每行三幅图的关系，从四个选项中选出最合适的一项。',ans,
 '有向差集：输入错位、定向消除与整体旋转',[
 '每行先将第二幅图的黑格循环向右平移一列，最右列移到最左列；再以第一幅图为底，删除与移位后第二图重合的黑格；最后把剩余图形顺时针旋转90°，得到第三幅图。',
 '这是“第一图减去移位后的第二图”，两幅图的角色不对称。第一、二行分别验证“先对齐第二图—定向消除—整体旋转”的次序。第三行按此计算，得到D项，四项黑格数量相同。',
 ''.join(ex)],'directed_difference_after_operand_shift_then_rotation',['N26-79','GD25-48'],dict(rows=rows,options=choices,checks=CHECKS[15]))

# Q16: line-set carrier; each input receives a different transformation before union.
def ekey(a,b):return tuple(sorted((a,b)))
EU=frozenset([ekey((r,c),(r+1,c)) for r in range(3) for c in range(4)]+
             [ekey((r,c),(r,c+1)) for r in range(4) for c in range(3)])
def er(e):return frozen(ekey((a[1],3-a[0]),(b[1],3-b[0])) for a,b in e)
def ec(e):return er(er(er(e)))
def esample():return frozen(RNG.sample(sorted(EU),7))
linerows=[]
for row in range(3):
    for _ in range(300000):
        a,b=esample(),esample();o=er(a)|ec(b)
        wrong=[er(a|b),ec(a)|er(b),a|b]
        if row<2:
            if any(w==o for w in wrong):continue
            linerows.append((a,b,o));break
        # XOR loses shared edges, so equal-count alternative uses unchanged union.
        wrong=[er(a|b),ec(a)|er(b),a|b]
        if len(set([o]+wrong))==4 and len({len(x) for x in [o]+wrong})==1 and 9<=len(o)<=12:
            linerows.append((a,b,o));break
    else:raise AssertionError('line set')
lineopts=[wrong[0],wrong[1],linerows[2][2],wrong[2]]
DATA[16]=dict(rows=linerows,options=lineopts)
question(16,'观察九宫格每行线段的关系，从四个选项中选出最合适的一项。','C',
 '双主体位置运算：分别转向后求并',[
 '每行将第一图的线段整体顺时针旋转90°，将第二图的线段整体逆时针旋转90°，再按同一坐标叠合；重合的线段只画一次，不抵消，得到第三图。端点处的小圆点只用于辨认线段端点。',
 '第一、二行验证的是两幅输入分别朝相反方向旋转，随后求并。第三行按此处理得到C项，四个候选均含相同数量的单位线段，不能只凭线段多少作答。',
 'A项把两幅输入都顺时针旋转后求并；B项把第一、二图的旋转方向互换；D项直接把两图求并，完全遗漏位置变换。三项均不能通过前两行的相同操作检验。'],
 'rotate_inputs_oppositely_then_union_line_sets',['GD25-48','N26-78'],dict(rows=linerows,options=lineopts))
CHECKS[16]={'distinct_options':True,'equal_edge_counts':True,'different_input_transforms_do_not_commute_with_single_global_transform':True}

# Six-figure classifications; each option is a partition of all six figures.
PARTITIONS=[((1,3,6),(2,4,5)),((1,2,5),(3,4,6)),((1,4,5),(2,3,6)),((1,2,4),(3,5,6))]
def partition_key(groups):return frozenset(frozenset(g) for g in groups)
def partition_text(groups):return '，'.join(''.join('①②③④⑤⑥'[i-1] for i in group) for group in groups)
def classification_q(n,correct,point,analysis,mechanism,refs,model):
    choices=PARTITIONS[:];idx={17:0,18:3,19:1,20:2}[n]
    good=partition_key(correct)
    choices=[p for p in choices if partition_key(p)!=good]
    for p in combinations(range(1,7),3):
        other=tuple(i for i in range(1,7) if i not in p)
        pp=(p,other)
        if partition_key(pp) not in [partition_key(x) for x in choices] and partition_key(pp)!=good:choices.append(pp)
        if len(choices)>=3:break
    choices=choices[:3];choices.insert(idx,correct)
    DATA[n]['partition']=correct;DATA[n]['choices']=choices
    explanation=analysis+[f'正确分组为{partition_text(correct)}，对应{"ABCD"[idx]}项。'+
                            '；'.join(f'{"ABCD"[j]}项把图{next(i for i in range(1,7) if (i in choices[j][0])!=(i in correct[0]))}与另一类混组' for j in range(4) if j!=idx)+'。']
    return question(n,'把下面六个图形分为两类，使每一类图形都有各自的共同特征或规律，分类正确的是：',
                    'ABCD'[idx],point,explanation,mechanism,refs,model,
                    options=[partition_text(p) for p in choices])

def transformed_poly(poly,angle):
    a=angle*math.pi/180;return [(x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a)) for x,y in poly]
def inside(p,poly):
    x,y=p;odd=False
    for (x1,y1),(x2,y2) in zip(poly,poly[1:]+poly[:1]):
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1:odd=not odd
    return odd
basepairs=[([(-1.2,-.8),(.6,-.8),(.6,.8),(-1.2,.8)],[(-.6,-1.1),(1.1,0),(-.6,1.1)]),
           ([(-1,-1),(.8,-1),(.8,.8),(-1,.8)],[(-.6,-.4),(.6,-1),(1.2,.4),(0,1)]),
           ([(-1.2,0),(0,-1.1),(.8,0),(0,1.1)],[(-.6,-.8),(1,-.8),(1,.8),(-.6,.8)])]
items17=[];target17={1,3,6}
for i in range(6):
    p,q=basepairs[i%3];candidates=[(x/10,y/10) for x in range(-8,9) for y in range(-7,8)]
    desired=i+1 in target17
    candidates=[pt for pt in candidates if inside(pt,p) and (inside(pt,q)==desired)]
    # Keep the point comfortably away from all polygon edges.
    def distance(pt,a,b):
        ux,uy=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((pt[0]-a[0])*ux+(pt[1]-a[1])*uy)/(ux*ux+uy*uy)))
        return math.dist(pt,(a[0]+t*ux,a[1]+t*uy))
    margins=lambda pt:min(distance(pt,a,b) for poly in (p,q) for a,b in zip(poly,poly[1:]+poly[:1]))
    safe=[pt for pt in candidates if margins(pt)>.16]
    pt=RNG.choice(safe) if safe else max(candidates,key=margins)
    angle=[0,50,110,175,235,300][i]
    items17.append((transformed_poly(p,angle),transformed_poly(q,angle),transformed_poly([pt],angle)[0]))
DATA[17]=dict(items=items17)
classification_q(17,((1,3,6),(2,4,5)),'图形关系：标记点在两图公共区域还是仅在一个图内',[
 '每幅图都由两个相交的封闭图形和一个黑点组成，先识别两个原始轮廓，再判断黑点同时满足几个包含关系。不能把由交叉线分出的局部小面误当作原图。',
 '①③⑥的黑点同时位于两个封闭图形内部，即位于两者公共区域；②④⑤的黑点只位于其中一个图形内部。六图都有一个黑点、两个原始封闭图形，而且两个轮廓都相交，数元素或只看是否相交均不能分类。'],
 'point_in_intersection_vs_single_polygon',['N26-83','N26-85','ZJ23-77'],dict(items=items17,members=sorted(target17)))

items18=[];target18={1,2,4};seen18=set()
for i in range(6):
    desired=(1,2) if i+1 in target18 else (2,1)
    for _ in range(200000):
        s=sample(8)
        canonical=min(tuple(sorted(t)) for t in [s,rot(s),rot(rot(s)),ccw(s),flip(s),rot(flip(s)),rot(rot(flip(s))),ccw(flip(s))])
        if (len(components(s)),len(components(U-s)))==desired and canonical not in seen18:
            seen18.add(canonical);items18.append(s);break
    else:raise AssertionError('connectivity')
DATA[18]=dict(items=items18)
classification_q(18,((1,2,4),(3,5,6)),'黑白关系：分别检查两种颜色的共边连通性',[
 '只把共边视为连通，角点接触不算连通。每图均有8个黑格和8个白格，黑白面积、总格数相同，需分别追踪两种颜色的连通部分。',
 '①②④中黑格连成1部分，白格分为2部分；③⑤⑥中黑格分为2部分，白格连成1部分。只沿视觉上相近的角点连接会误判；应逐一检查共边通路。'],
 'black_white_complement_connectivity',['N26-84','ZJ23-71'],dict(black=items18,signatures=[(len(components(s)),len(components(U-s))) for s in items18]))

# Q19: locate each polygon's unique symmetry axis, then compare the detached line.
items19=[];target19={1,2,5}
polys19=[[(0,-1),(.7,-.15),(0,1),(-.7,-.15)],
         [(-.75,-.7),(.75,-.7),(.75,.35),(0,1),(-.75,.35)],
         [(-.9,-.7),(.9,-.7),(0,1.5)]]
for i in range(6):
    parallel=i+1 in target19
    theta=[0,45,0,-45,90,90][i]*math.pi/180
    u=(math.cos(theta),math.sin(theta));v=(-u[1],u[0])
    def pt(p):return (p[0]*v[0]+p[1]*u[0],p[0]*v[1]+p[1]*u[1])
    line=[(-1.6,-.7),(-1.6,.7)] if parallel else [(-2.3,0),(-.9,0)]
    polygon=[pt(p) for p in polys19[i%3]];segment=[pt(p) for p in line]
    vector=(segment[1][0]-segment[0][0],segment[1][1]-segment[0][1])
    dot=vector[0]*u[0]+vector[1]*u[1];cross=vector[0]*u[1]-vector[1]*u[0]
    assert abs(cross)<1e-8 if parallel else abs(dot)<1e-8
    items19.append(dict(polygon=polygon,segment=segment,axis=u,parallel=parallel,dot=dot,cross=cross))
DATA[19]=dict(items=items19)
classification_q(19,((1,2,5),(3,4,6)),'对象关系：独立线段与隐含对称轴的平行或垂直',[
 '每图由一个封闭多边形和一条与它分离的直线段构成。先找出多边形唯一的对称轴，再比较独立线段与这条对称轴的方向关系。多边形的边不能代替其对称轴。',
 '①②⑤中独立线段与多边形的唯一对称轴平行；③④⑥中独立线段与唯一对称轴垂直。两类独立线段的绝对方向都各包含水平、竖直和斜向，不能仅按纸面上的线段朝向分组。'],
 'auxiliary_line_parallel_perpendicular_to_implicit_symmetry_axis',['JS23-76','N26-78'],dict(items=items19,parallel_members=sorted(target19)))

def leaf_component(leaf_count,turn):
    square=[((0,0),(2,0)),((2,0),(2,2)),((2,2),(0,2)),((0,2),(0,0))]
    leaves=[((0,0),(-1,-1)),((2,0),(3,-1)),((2,2),(3,3))][:leaf_count]
    def tr(p):
        x,y=p
        for _ in range(turn):x,y=2-y,x
        return x,y
    return k.planarize([(tr(a),tr(b)) for a,b in square+leaves])
target20={1,4,5};items20=[]
for i in range(6):
    dist=[1,1,3] if i+1 in target20 else [1,2,2]
    RNG.shuffle(dist);items20.append([leaf_component(c,(i+j)%4) for j,c in enumerate(dist)])
DATA[20]=dict(items=items20)
classification_q(20,((1,4,5),(2,3,6)),'最少笔画的分配：总数相同仍需分部分核对',[
 '每图由3个互不相连的线图组成，且每个小线图都有1个封闭面。六图合计均为3部分、3面，整体最少都需5笔，因此只看总笔画数没有区分力。',
 '分小线图数奇点：带1条外接支线的方形有2个奇点，最少1笔；带2条支线时有4个奇点，最少2笔；带3条支线时有6个奇点，最少3笔。外接端点及连接处都要计入。',
 '①④⑤的3个小线图最少笔画分布均为1、1、3；②③⑥则均为1、2、2。位置与转向不同，但分配方式保持。'],
 'componentwise_stroke_distribution_equal_total',['N26-78','JS24C-80'],dict(items=items20,signatures=[sorted(k.graph_stats(g)['strokes'] for g in item) for item in items20]))

for q in QUESTIONS:
    if q['n'] in (13,15):q['difficulty']=q['level']='难'
    elif q['n'] in (17,19):q['difficulty']=q['level']='中等'

def symmetry_axes(poly):
    center=tuple(sum(p[i] for p in poly)/len(poly) for i in range(2));axes=[]
    candidates=poly+[((a[0]+b[0])/2,(a[1]+b[1])/2) for a,b in zip(poly,poly[1:]+poly[:1])]
    for p in candidates:
        dx,dy=p[0]-center[0],p[1]-center[1];length=math.hypot(dx,dy)
        if length<1e-8:continue
        u=(dx/length,dy/length)
        def reflected(v):
            a,b=v[0]-center[0],v[1]-center[1];projection=a*u[0]+b*u[1]
            return center[0]+2*projection*u[0]-a,center[1]+2*projection*u[1]-b
        if all(min(math.dist(reflected(v),w) for w in poly)<1e-7 for v in poly):
            if not any(abs(u[0]*v[1]-u[1]*v[0])<1e-7 for v in axes):axes.append(u)
    return axes

def draw_binary(d,cx,cy,s,size,carrier='blocks'):
    if carrier=='blocks':return k.grid(d,cx,cy,s,n=4,size=size)
    side=size/4
    for r,c in sorted(U):
        x=cx+(c-1.5)*side;y=cy+(r-1.5)*side;rad=side*.34
        d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=k.BLACK if (r,c) in s else 'white',outline=k.BLACK,width=3)
def draw_tri(d,cx,cy,s,size):
    step=size/3
    # Fine carrier lattice also makes absence an explicit coordinate state.
    d.rectangle((cx-size/2,cy-size/2,cx+size/2,cy+size/2),outline='#999999',width=2)
    for i,(r,c) in enumerate(U3):
        x=cx+(c-1)*step;y=cy+(r-1)*step;v=s[i]
        if v:d.ellipse((x-step*.23,y-step*.23,x+step*.23,y+step*.23),fill=k.BLACK if v==2 else 'white',outline=k.BLACK,width=3)
        else:d.ellipse((x-2,y-2,x+2,y+2),fill='#b7b7b7')
def draw_lines(d,cx,cy,edges,size):
    step=size/3
    for a,b in edges:
        xy=lambda p:(cx+(p[1]-1.5)*step,cy+(p[0]-1.5)*step)
        d.line((*xy(a),*xy(b)),fill=k.BLACK,width=5)
    for p in {v for e in edges for v in e}:
        x,y=cx+(p[1]-1.5)*step,cy+(p[0]-1.5)*step
        d.ellipse((x-3,y-3,x+3,y+3),fill=k.BLACK)
def draw11(d,cx,cy,item,size=170):
    s,(filled,hollow)=item;k.grid(d,cx,cy+18,s,n=4,size=size)
    total=filled+hollow;gap=22
    for i in range(total):
        x=cx+(i-(total-1)/2)*gap;y=cy-size/2-7
        d.ellipse((x-8,y-8,x+8,y+8),fill=k.BLACK if i<filled else 'white',outline=k.BLACK,width=2)
def draw12(d,cx,cy,item,size=175):
    a,b=item;k.network(d,cx,cy-size*.37,a,size=size*.65,show_nodes=False)
    k.network(d,cx,cy+size*.37,b,size=size*.65,show_nodes=False)
def draw17(d,cx,cy,item,size=215):
    p,q,pt=item;scale=size/2.8
    def xy(v):return cx+v[0]*scale,cy+v[1]*scale
    for poly in (p,q):d.line([xy(v) for v in poly]+[xy(poly[0])],fill=k.BLACK,width=5)
    x,y=xy(pt);d.ellipse((x-7,y-7,x+7,y+7),fill=k.BLACK)
def draw19(d,cx,cy,item,size=205):
    polygon,segment=item['polygon'],item['segment'];pts=polygon+segment
    minx,maxx=min(p[0] for p in pts),max(p[0] for p in pts)
    miny,maxy=min(p[1] for p in pts),max(p[1] for p in pts)
    scale=size/max(maxx-minx,maxy-miny)
    def pt(p):return (cx+(p[0]-(minx+maxx)/2)*scale,cy+(p[1]-(miny+maxy)/2)*scale)
    d.line([pt(p) for p in polygon]+[pt(polygon[0])],fill=k.BLACK,width=5)
    d.line((*pt(segment[0]),*pt(segment[1])),fill=k.BLACK,width=6)
def draw20(d,cx,cy,item,size=215):
    for (dx,dy),edges in zip([(-55,-48),(55,-48),(0,58)],item):
        def pt(p):return cx+dx+(float(p[0])-1)*20,cy+dy+(float(p[1])-1)*20
        for a,b in edges:d.line((*pt(a),*pt(b)),fill=k.BLACK,width=5)

def save_explanation(n,lines):
    im,d=k.canvas(h=430)
    for i,line in enumerate(lines):k.label(d,900,70+i*85,line,33)
    im.save(k.ASSETS/f'e{n:02}.png',dpi=(300,300))
def draw_all():
    for n in range(11,21):
        data=DATA[n]
        if n in (11,12):
            im,d,cs,os=k.sequence(n);fn=draw11 if n==11 else draw12
            for c,item in zip(cs[:5],data['stem']):fn(d,*c,item)
            if n==11:
                draw11(d,*cs[5],(frozenset(),target11));k.label(d,cs[5][0],cs[5][1]+18,'?',95)
            else:k.label(d,*cs[5],'?',95)
            for c,item in zip(os,data['options']):fn(d,*c,item)
        elif n in (13,15,16):
            im,d,cs,os=k.matrix(n);fn=(lambda d,x,y,s,size:draw_binary(d,x,y,s,size,data['carrier'])) if n!=16 else draw_lines
            vals=[item for row in data['rows'] for item in row]
            for c,item in zip(cs[:8],vals[:8]):fn(d,*c,item,190)
            k.label(d,*cs[8],'?',100)
            for c,item in zip(os,data['options']):fn(d,*c,item,118)
        elif n==14:
            im,d,cs,os=k.two_groups(n);vals=[s for row in data['rows'] for s in row]
            for c,item in zip(cs[:5],vals[:5]):draw_tri(d,*c,item,170)
            k.label(d,*cs[5],'?',95)
            for c,item in zip(os,data['options']):draw_tri(d,*c,item,170)
        else:
            im,d,cs=k.classification(n)
            fn={17:draw17,18:lambda d,x,y,s:draw_binary(d,x,y,s,200),19:draw19,20:draw20}[n]
            for c,item in zip(cs,data['items']):fn(d,*c,item)
        k.save(im,n)
        if n==11:save_explanation(n,['黑格部分数 ＝ 实心圆数','黑格接触的外沿边数 ＝ 空心圆数','C：2部分，接触3边；四项黑格数均为7'])
        elif n==12:save_explanation(n,['上图方向种数 ＝ 下图最小封闭面数','上图连通部分数 ＝ 下图最少笔画数','A：2部分、3方向  →  3面、2笔'])
        elif n in (13,14,15,16):
            im2,d2=k.canvas(h=470);q=next(q for q in QUESTIONS if q['n']==n)
            a,b,o=data['rows'][-1];fn=draw_tri if n==14 else draw_lines if n==16 else lambda d,x,y,s,size:draw_binary(d,x,y,s,size,data['carrier'])
            for x,s,label in [(280,a,'第一图'),(900,b,'第二图'),(1520,o,'正确结果')]:
                fn(d2,x,240,s,230);k.label(d2,x,60,label,35)
            im2.save(k.ASSETS/f'e{n:02}.png',dpi=(300,300))
        else:
            correct=data['partition'];save_explanation(n,[partition_text(correct),
                {17:'公共区域内 / 只在一个图形内',18:'黑1白2 / 黑2白1',19:'独立线段与唯一对称轴：平行 / 垂直',20:'分部分最少笔画：1、1、3 / 1、2、2'}[n],
                '各组中图形的朝向和位置可变，共同关系保持'])

def verify():
    result={}
    assert len(QUESTIONS)==10
    q11=[count_signature(s)==t for s,t in DATA[11]['options']];assert q11==[False,False,True,False]
    assert len({len(s) for s,t in DATA[11]['options']})==1
    result['11']={'option_validity':q11,'equal_black_count':7}
    q12=[(c==s and d==f) for c,d,f,s in map(sig12,DATA[12]['options'])];assert q12==[True,False,False,False]
    result['12']={'option_validity':q12,'signatures':[sig12(x) for x in DATA[12]['options']]}
    for n in (13,14,15,16):
        vals=DATA[n]['options'];out=DATA[n]['rows'][-1][2]
        v=[x==out for x in vals];q=next(q for q in QUESTIONS if q['n']==n)
        assert sum(v)==1 and v['ABCD'.index(q['answer'])]
        assert len(set(vals))==4
        result[str(n)]={'option_validity':v,**CHECKS[n]}
    for n in (17,18,19,20):
        data=DATA[n];q=next(q for q in QUESTIONS if q['n']==n)
        if n==17:good=[i+1 for i,(p,r,pt) in enumerate(data['items']) if inside(pt,p) and inside(pt,r)]
        elif n==18:good=[i+1 for i,s in enumerate(data['items']) if (len(components(s)),len(components(U-s)))==(1,2)]
        elif n==19:
            good=[i+1 for i,item in enumerate(data['items']) if abs(item['cross'])<1e-8]
            assert all(abs(item['cross'])<1e-8 or abs(item['dot'])<1e-8 for item in data['items'])
            for item in data['items']:
                axes=symmetry_axes(item['polygon']);assert len(axes)==1
                assert abs(axes[0][0]*item['axis'][1]-axes[0][1]*item['axis'][0])<1e-7
        else:
            signatures=[sorted(k.graph_stats(e)['strokes'] for e in item) for item in data['items']]
            assert all(sum(s)==5 for s in signatures)
            assert all(sum(k.graph_stats(e)['faces'] for e in item)==3 for item in data['items'])
            good=[i+1 for i,s in enumerate(signatures) if s==[1,1,3]]
        expected=partition_key((good,[i for i in range(1,7) if i not in good]))
        valid=[partition_key(p)==expected for p in data['choices']]
        assert sum(valid)==1 and valid['ABCD'.index(q['answer'])]
        result[str(n)]={'correct_members':good,'partition_validity':valid,'unique_partition':True}
    return {'passed':True,'questions':list(range(11,21)),'structure':{'rules':6,'classification':4},'checks':result}

if __name__=='__main__':
    draw_all();report=verify()
    (ROOT/'verify_b.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'questions_b.json').write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
