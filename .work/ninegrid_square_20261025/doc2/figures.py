"""Original, deterministic 2026-style judgment-reasoning figures.

All diagram measurements and answers are generated from the same source data.
The four rule questions have an enclosing stem/options frame, as requested.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
BLACK = "#161616"
GRAY = "#626262"
FONT = "C:/Windows/Fonts/msyh.ttc"


def font(size: int):
    return ImageFont.truetype(FONT, size)


def canvas(w=1800, h=920):
    image = Image.new("RGB", (w, h), "white")
    return image, ImageDraw.Draw(image)


def save(image, name):
    image.save(ASSETS / name, dpi=(300, 300))


def label(draw, x, y, value, size=42):
    draw.text((x, y), str(value), font=font(size), fill=BLACK, anchor="mm")


def outer_row(draw, box, cells, stroke=5):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=BLACK, width=stroke)
    step = (x1 - x0) / cells
    for index in range(1, cells):
        x = round(x0 + index * step)
        draw.line((x, y0, x, y1), fill=BLACK, width=stroke - 1)
    return [(x0 + (i + 0.5) * step, (y0 + y1) / 2) for i in range(cells)]


def outer_matrix(draw, box, rows, columns, stroke=5):
    x0, y0, x1, y1 = box
    draw.rectangle(box, outline=BLACK, width=stroke)
    for col in range(1, columns):
        x = round(x0 + col * (x1 - x0) / columns)
        draw.line((x, y0, x, y1), fill=BLACK, width=stroke - 1)
    for row in range(1, rows):
        y = round(y0 + row * (y1 - y0) / rows)
        draw.line((x0, y, x1, y), fill=BLACK, width=stroke - 1)
    return [[(x0 + (col + .5) * (x1 - x0) / columns,
              y0 + (row + .5) * (y1 - y0) / rows)
             for col in range(columns)] for row in range(rows)]


def options_frame(draw, y0=540, y1=815):
    centers = outer_row(draw, (180, y0, 1620, y1), 4)
    for i, (x, _) in enumerate(centers):
        label(draw, x, y1 + 42, "ABCD"[i], 44)
    return centers


def octagon_points(cx, cy, radius=94):
    return [(cx + radius * math.sin(math.pi * i / 4),
             cy - radius * math.cos(math.pi * i / 4)) for i in range(8)]


def dashed(draw, p, q, width=6):
    length = math.dist(p, q)
    for start in range(0, int(length), 24):
        end = min(start + 12, length)
        p0 = (p[0] + (q[0]-p[0]) * start / length, p[1] + (q[1]-p[1]) * start / length)
        p1 = (p[0] + (q[0]-p[0]) * end / length, p[1] + (q[1]-p[1]) * end / length)
        draw.line((*p0, *p1), fill=GRAY, width=width)


def chord_figure(draw, cx, cy, solid, dotted, radius=94):
    pts = octagon_points(cx, cy, radius)
    draw.line(pts + [pts[0]], fill=GRAY, width=4, joint="curve")
    for x, y in pts:
        draw.ellipse((x-8, y-8, x+8, y+8), fill="white", outline=BLACK, width=3)
    p, q = (pts[solid[0]], pts[solid[1]])
    r, s = (pts[dotted[0]], pts[dotted[1]])
    dashed(draw, r, s)
    draw.line((*p, *q), fill=BLACK, width=9)
    draw.rectangle((p[0]-10, p[1]-10, p[0]+10, p[1]+10), fill=BLACK)
    draw.ellipse((r[0]-11, r[1]-11, r[0]+11, r[1]+11), fill="white", outline=BLACK, width=4)


def chord_state(i):
    return ((i % 8, (i+3) % 8), ((1+2*i) % 8, (4+2*i) % 8))


Q1_OPTIONS = [
    (chord_state(5)[0], chord_state(4)[1]),
    (chord_state(4)[0], chord_state(5)[1]),
    chord_state(5),
    (chord_state(5)[0], ((1-2*5) % 8, (4-2*5) % 8)),
]


def draw1():
    im, d = canvas(h=895)
    centers = outer_row(d, (70, 55, 1730, 365), 6)
    for i in range(5):
        chord_figure(d, *centers[i], *chord_state(i))
    label(d, *centers[5], "?", 105)
    for center, state in zip(options_frame(d, 490, 770), Q1_OPTIONS):
        chord_figure(d, *center, *state, radius=77)
    save(im, "q01.png")


def reflect_x(cells, n):
    return {(r, n-1-c) for r, c in cells}


def rotate_cw(cells, n):
    return {(c, n-1-r) for r, c in cells}


def transform_motif(motif, transform, n=4):
    cells, dot = motif
    fn = reflect_x if transform == "mirror" else rotate_cw
    return fn(cells, n), next(iter(fn({dot}, n)))


Q2_TOP = ({(0,0),(1,0),(2,0),(2,1),(2,2),(3,2)}, (0,3))
Q2_BOTTOM = ({(0,1),(1,1),(2,1),(2,2),(3,1),(3,2)}, (0,3))
Q2_TOP_B = transform_motif(Q2_TOP, "mirror")
Q2_TOP_C = transform_motif(Q2_TOP_B, "rotate")
Q2_BOTTOM_B = transform_motif(Q2_BOTTOM, "mirror")
Q2_CORRECT = transform_motif(Q2_BOTTOM_B, "rotate")
Q2_OPTIONS = [
    transform_motif(Q2_BOTTOM, "rotate"),
    Q2_CORRECT,
    transform_motif(Q2_BOTTOM_B, "mirror"),
    transform_motif(Q2_BOTTOM_B, "rotate", 4)[0],
]
# Replace fourth wrong option with a valid (cells, dot) motif after a counterclockwise turn.
Q2_OPTIONS[3] = transform_motif(transform_motif(transform_motif(Q2_BOTTOM_B, "rotate"), "rotate"), "rotate")
assert len({(frozenset(c), dot) for c, dot in Q2_OPTIONS}) == 4


def motif(draw, cx, cy, state, cell=39):
    cells, dot = state
    x0 = cx - 2*cell
    y0 = cy - 2*cell
    for r in range(4):
        for c in range(4):
            rect = (x0+c*cell, y0+r*cell, x0+(c+1)*cell, y0+(r+1)*cell)
            if (r,c) in cells:
                draw.rectangle(rect, fill=BLACK)
            draw.rectangle(rect, outline=GRAY, width=2)
    r,c = dot
    x = x0 + (c+.5)*cell
    y = y0 + (r+.5)*cell
    draw.ellipse((x-11,y-11,x+11,y+11), fill="white", outline=BLACK, width=5)


def draw2():
    im,d = canvas(h=1100)
    left=outer_row(d,(75,145,855,525),3)
    right=outer_row(d,(945,145,1725,525),3)
    for center,state in zip(left,[Q2_TOP,Q2_TOP_B,Q2_TOP_C]):
        motif(d,*center,state)
    for center,state in zip(right[:2],[Q2_BOTTOM,Q2_BOTTOM_B]):
        motif(d,*center,state)
    label(d,*right[2],"?",105)
    for center,state in zip(options_frame(d,735,1010),Q2_OPTIONS):
        motif(d,*center,state,34)
    save(im,"q02.png")


def network(cells, leaves):
    edges=set()
    for r,c in cells:
        a=(r,c);b=(r,c+1);e=(r+1,c);f=(r+1,c+1)
        for p,q in ((a,b),(b,f),(e,f),(a,e)):
            edges.add(tuple(sorted((p,q))))
    for p,q in leaves:
        edges.add(tuple(sorted((p,q))))
    return edges


Q3_NETWORKS = [
    network({(0,0),(0,1)}, [((0,0),(-1,0)),((0,2),(-1,2)),((1,0),(2,0)),((1,2),(2,2))]),
    network({(0,0),(1,0)}, [((0,0),(0,-1)),((0,1),(0,2)),((2,0),(2,-1)),((2,1),(2,2))]),
    network({(0,0),(1,1)}, [((0,0),(-1,0)),((0,1),(-1,1)),((2,1),(3,1)),((2,2),(3,2))]),
    network({(0,0),(0,1),(0,2)}, [((0,0),(-1,0)),((1,3),(2,3))]),
    network({(0,0),(1,0),(1,1)}, [((0,0),(-1,0)),((2,2),(3,2))]),
]
Q3_OPTIONS = [
    network({(0,0),(1,0),(1,1)}, [((0,0),(-1,0)),((0,1),(0,2)),((2,0),(2,-1)),((2,2),(3,2))]),
    network({(0,0),(1,0)}, [((0,0),(-1,0)),((2,1),(3,1))]),
    network({(0,0),(0,1),(1,1)}, []),
    network({(0,0),(0,1),(1,1)}, [((0,0),(-1,0)),((2,2),(3,2))]),
]


def network_signature(edges):
    vertices={v for e in edges for v in e}
    degree={v:0 for v in vertices}
    for p,q in edges:
        degree[p]+=1;degree[q]+=1
    seen={next(iter(vertices))}; queue=deque(seen)
    while queue:
        v=queue.popleft()
        for e in edges:
            if v in e:
                other=e[0] if e[1]==v else e[1]
                if other not in seen:seen.add(other);queue.append(other)
    assert seen==vertices,"network must be connected"
    return len(edges)-len(vertices)+1,sum(x==1 for x in degree.values())


Q3_SIGNATURES=[network_signature(edges) for edges in Q3_NETWORKS]
Q3_OPTION_SIGNATURES=[network_signature(edges) for edges in Q3_OPTIONS]
assert Q3_SIGNATURES==[(2,4)]*3+[(3,2)]*2
assert Q3_OPTION_SIGNATURES==[(3,4),(2,2),(3,0),(3,2)]


def network_picture(draw,cx,cy,edges,scale=56):
    vertices={v for e in edges for v in e}
    minr=min(r for r,c in vertices);maxr=max(r for r,c in vertices)
    minc=min(c for r,c in vertices);maxc=max(c for r,c in vertices)
    def point(v):
        r,c=v
        return (cx+(c-(minc+maxc)/2)*scale,cy+(r-(minr+maxr)/2)*scale)
    for p,q in edges:
        draw.line((*point(p),*point(q)),fill=BLACK,width=6)
    for v in vertices:
        x,y=point(v)
        draw.ellipse((x-6,y-6,x+6,y+6),fill=BLACK)


def draw3():
    im,d=canvas(h=1100)
    left=outer_row(d,(75,145,855,525),3)
    right=outer_row(d,(945,145,1725,525),3)
    for center,edges in zip(left+right[:2],Q3_NETWORKS):
        network_picture(d,*center,edges,51)
    label(d,*right[2],"?",105)
    for center,edges in zip(options_frame(d,735,1010),Q3_OPTIONS):
        network_picture(d,*center,edges,44)
    save(im,"q03.png")


def rotate_set(cells,n=3):
    return {(c,n-1-r) for r,c in cells}


def operation(a,b):
    return rotate_set(a ^ b)


Q4_ROWS = [
    [{(0,0),(0,1),(1,1),(2,0)}, {(0,1),(1,0),(1,1),(2,2)}],
    [{(0,2),(1,0),(1,2),(2,1)}, {(0,0),(0,2),(1,0),(2,2)}],
    [{(0,0),(1,0),(1,1),(2,1),(2,2)}, {(0,1),(1,1),(1,2),(2,0)}],
]
Q4_CORRECT = operation(*Q4_ROWS[2])
Q4_OPTIONS = [
    Q4_CORRECT,
    rotate_set(Q4_ROWS[2][0] | Q4_ROWS[2][1]),
    Q4_ROWS[2][0] ^ Q4_ROWS[2][1],
    rotate_set(Q4_ROWS[2][0] & Q4_ROWS[2][1]),
]
assert len({frozenset(v) for v in Q4_OPTIONS}) == 4


def tile(draw,cx,cy,cells,size=156,n=3):
    side=size/n
    x0=cx-size/2; y0=cy-size/2
    for r in range(n):
        for c in range(n):
            rect=(x0+c*side,y0+r*side,x0+(c+1)*side,y0+(r+1)*side)
            draw.rectangle(rect,fill=BLACK if (r,c) in cells else "white",outline=GRAY,width=3)


def draw4():
    im,d=canvas(h=1220)
    grid=outer_matrix(d,(450,20,1350,920),3,3)
    for row_no,(a,b) in enumerate(Q4_ROWS):
        tile(d,*grid[row_no][0],a,145)
        tile(d,*grid[row_no][1],b,145)
        if row_no<2:tile(d,*grid[row_no][2],operation(a,b),145)
        else:label(d,*grid[row_no][2],"?",105)
    for center,cells in zip(options_frame(d,950,1130),Q4_OPTIONS):
        tile(d,*center,cells,126)
    save(im,"q04.png")


Q5_U_OUTLINE=[(0,0),(3,0),(3,3),(2,3),(2,1),(1,1),(1,3),(0,3)]
Q5_PLANE=lambda x,z:(x+z)/6
Q5_SECTION=[(x,Q5_PLANE(x,z),z) for x,z in Q5_U_OUTLINE]
assert len(Q5_SECTION)==8 and all(0<=y<=1 for x,y,z in Q5_SECTION)
Q5_OPTIONS=[
    [(-2,-1),(-1,-2),(1,-2),(2,-1),(2,1),(1,2),(-1,2),(-2,1)],
    [(-2,-2),(1,-2),(1,-1),(-1,-1),(-1,2),(-2,2)],
    [(-2,-2),(2,-2),(2,2),(1,2),(1,-1),(-1,-1),(-1,2),(-2,2)],
    [(-2,-2),(-1,-2),(-1,-1),(1,-1),(1,-2),(2,-2),(2,2),(1,2),(1,1),(-1,1),(-1,2),(-2,2)],
]


def projected(x,y,z,ox=620,oy=420,scale=105):
    return(ox+scale*(x+.52*y),oy-scale*(z+.35*y))


def draw_u_solid(draw):
    front=[projected(x,0,z) for x,z in Q5_U_OUTLINE]
    back=[projected(x,1,z) for x,z in Q5_U_OUTLINE]
    draw.line(back+[back[0]],fill=GRAY,width=4,joint="curve")
    for p,q in zip(front,back):
        draw.line((*p,*q),fill=GRAY,width=4)
    draw.line(front+[front[0]],fill=BLACK,width=7,joint="curve")
    for name,p in (("P",(0,0,0)),("Q",(3,.5,0)),("R",(0,.5,3))):
        x,y=projected(*p)
        draw.ellipse((x-9,y-9,x+9,y+9),fill=BLACK)
        dx,dy={"P":(-30,25),"Q":(29,21),"R":(-30,-22)}[name]
        label(draw,x+dx,y+dy,name,34)


def silhouette(draw,cx,cy,coords,scale=46):
    points=[(cx+x*scale,cy-y*scale) for x,y in coords]
    draw.line(points+[points[0]],fill=BLACK,width=8,joint="curve")


def draw5():
    im,d=canvas(h=960)
    d.rectangle((80,45,1720,480),outline=BLACK,width=5)
    draw_u_solid(d)
    for center,shape in zip(options_frame(d,575,850),Q5_OPTIONS):
        silhouette(d,*center,shape,40)
    save(im,"q05.png")


Q6_NET={(0,1),(1,1),(2,1),(3,1),(1,0),(1,2)}


def q6_candidate(circle,triangle,arrow,arrow_up=True):
    return dict(circle=circle,triangle=triangle,arrow=arrow,arrow_up=arrow_up)


Q6_OPTIONS=[
    q6_candidate((0,1),(2,1),(1,2)),
    q6_candidate((0,1),(3,1),(1,2)),
    q6_candidate((0,1),(3,1),(1,0)),
    q6_candidate((0,1),(3,1),(1,2),False),
]


def draw_cube(draw,cx,cy,scale=112):
    top=(cx,cy-1.18*scale)
    left=(cx-scale,cy-.53*scale)
    right=(cx+scale,cy-.53*scale)
    center=(cx,cy+.10*scale)
    bottom=(cx,cy+1.16*scale)
    ll=(cx-scale,cy+.53*scale)
    rr=(cx+scale,cy+.53*scale)
    for points in ((top,left,center,right),(left,ll,bottom,center),(center,bottom,rr,right)):
        draw.polygon(points,fill="white")
        draw.line(list(points)+[points[0]],fill=BLACK,width=5,joint="curve")
    label(draw,cx,cy-.69*scale,"●",53)
    label(draw,cx-.43*scale,cy+.40*scale,"▲",53)
    x=cx+.43*scale;y=cy+.39*scale
    draw.line((x,y+31,x,y-28),fill=BLACK,width=6)
    draw.polygon(((x-15,y-16),(x+15,y-16),(x,y-39)),fill=BLACK)


def draw_net(draw,cx,cy,symbols,cell=51):
    x0=cx-1.5*cell;y0=cy-2*cell
    for r,c in Q6_NET:
        x=x0+c*cell;y=y0+r*cell
        draw.rectangle((x,y,x+cell,y+cell),fill="white",outline=BLACK,width=4)
        center=(x+cell/2,y+cell/2)
        if (r,c)==symbols["circle"]:label(draw,*center,"●",28)
        elif (r,c)==symbols["triangle"]:label(draw,*center,"▲",28)
        elif (r,c)==symbols["arrow"]:label(draw,*center,"↑" if symbols["arrow_up"] else "↓",30)


def draw6():
    im,d=canvas(h=950)
    d.rectangle((90,45,1710,415),outline=BLACK,width=5)
    draw_cube(d,900,238,130)
    for center,symbols in zip(options_frame(d,530,845),Q6_OPTIONS):
        draw_net(d,*center,symbols,62)
    save(im,"q06.png")


from q7_design import POSSIBLE as Q7_POSSIBLE, FRONT as Q7_FRONT, RIGHT as Q7_RIGHT, TOTAL as Q7_TOTAL, witnesses as q7_witnesses
Q7_OPTIONS=[Q7_POSSIBLE[i][0] for i in (14,39,22,13)]
Q7_WITNESSES=[next(q7_witnesses(mask),None) for mask in Q7_OPTIONS]
assert [w is not None for w in Q7_WITNESSES]==[False,False,False,True]


def elevation(draw,cx,baseline,heights,unit=69):
    x0=cx-len(heights)*unit/2
    for c,height in enumerate(heights):
        for level in range(height):
            box=(x0+c*unit,baseline-(level+1)*unit,x0+(c+1)*unit,baseline-level*unit)
            draw.rectangle(box,fill="#eeeeee",outline=BLACK,width=4)


def occupancy(draw,cx,cy,mask,unit=62):
    x0=cx-1.5*unit;y0=cy-1.5*unit
    for r in range(3):
        for c in range(3):
            box=(x0+c*unit,y0+r*unit,x0+(c+1)*unit,y0+(r+1)*unit)
            draw.rectangle(box,fill="#707070" if (r,c) in mask else "white",outline=BLACK,width=3)


def draw7():
    im,d=canvas(h=950)
    centers=outer_row(d,(130,50,1670,405),2)
    elevation(d,centers[0][0],335,Q7_FRONT,76)
    elevation(d,centers[1][0],335,Q7_RIGHT,76)
    for center,mask in zip(options_frame(d,530,845),Q7_OPTIONS):
        occupancy(d,*center,mask,65)
    save(im,"q07.png")


def category_canvas(h=760):
    # Six independent, equal square frames in the 2026 reference's 3×2 pattern.
    # Circled figure numbers sit outside their own boxes.
    im,d=canvas(h=h)
    centers=[(x,y) for y in (200,530) for x in (420,900,1380)]
    for i,(x,y) in enumerate(centers):
        d.rectangle((x-125,y-125,x+125,y+125),outline=BLACK,width=5)
        label(d,x,y+155,"①②③④⑤⑥"[i],43)
    return im,d,centers


Q8_BASE = (
    [((-2,-1),(0,-1)),((0,-1),(0,1)),((0,1),(1,1)),((1,1),(1,2)),((0,-1),(2,-2))],
    (-2,-1),
)


def q8_transform(state, action):
    segments, marker=state
    if action=="rotate": fn=lambda p:(-p[1],p[0])
    else:fn=lambda p:(-p[0],p[1])
    return [(fn(a),fn(b)) for a,b in segments],fn(marker)


def q8_canonical(state):
    edges,marker=state
    return frozenset(frozenset((a,b)) for a,b in edges),marker


def q8_states():
    base=Q8_BASE; mirrored=q8_transform(base,"mirror")
    return [base,mirrored,q8_transform(base,"rotate"),q8_transform(mirrored,"rotate"),
            q8_transform(q8_transform(base,"rotate"),"rotate"),
            q8_transform(q8_transform(mirrored,"rotate"),"rotate")]


Q8_STATES=q8_states()
assert len({q8_canonical(s) for s in Q8_STATES})==6


def line_motif(draw,cx,cy,state,scale=48):
    segments,marker=state
    def pt(p):return(cx+p[0]*scale,cy+p[1]*scale)
    for a,b in segments:
        draw.line((*pt(a),*pt(b)),fill=BLACK,width=9)
    vertices={p for edge in segments for p in edge}
    for v in vertices:
        x,y=pt(v)
        draw.ellipse((x-7,y-7,x+7,y+7),fill="white",outline=BLACK,width=3)
    x,y=pt(marker)
    draw.ellipse((x-12,y-12,x+12,y+12),fill=BLACK)


def draw8():
    im,d,centers=category_canvas()
    for center,state in zip(centers,Q8_STATES):
        line_motif(d,*center,state,49)
    save(im,"q08.png")


Q9_SHAPES = [
    {(1,1),(1,2),(2,1),(2,2),(2,3),(3,3)},
    {(1,0),(1,1),(1,2),(1,3),(1,4),(0,2)},
    {(0,1),(1,1),(1,2),(2,1),(2,2),(2,3)},
    {(0,0),(1,0),(1,1),(2,1),(2,2),(3,2)},
    {(1,1),(1,2),(2,0),(2,1),(2,2),(3,0)},
    {(0,2),(1,2),(2,2),(2,1),(2,3),(3,2)},
]


def perimeter(cells):
    return sum((r+dr,c+dc) not in cells for r,c in cells for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)))


Q9_PERIMETERS=[perimeter(shape) for shape in Q9_SHAPES]


def draw9():
    im,d,centers=category_canvas()
    for center,cells in zip(centers,Q9_SHAPES):
        x,y=center; cell=33
        for r,c in cells:
            d.rectangle((x+(c-2.5)*cell,y+(r-2)*cell,x+(c-1.5)*cell,y+(r-1)*cell),fill=BLACK)
    save(im,"q09.png")


def neg(v):
    return tuple(-x for x in v)


def fold_orientation(cells):
    """Return unique cube-face normals if six square cells make a valid net."""
    if len(cells)!=6:return None
    start=next(iter(cells));orient={start:((0,0,1),(0,-1,0),(1,0,0))}
    queue=deque([start])
    while queue:
        at=queue.popleft(); normal,up,right=orient[at]
        for dr,dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nxt=(at[0]+dr,at[1]+dc)
            if nxt not in cells:continue
            if dr==-1: new=(up,neg(normal),right)
            elif dr==1:new=(neg(up),normal,right)
            elif dc==-1:new=(neg(right),up,normal)
            else:new=(right,up,neg(normal))
            if nxt in orient:
                if orient[nxt]!=new:return None
            else:orient[nxt]=new;queue.append(nxt)
    if len(orient)!=6:return None
    normals=[x[0] for x in orient.values()]
    return orient if len(set(normals))==6 else None


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def q6_works(option):
    orient=fold_orientation(Q6_NET)
    nc=orient[option["circle"]][0]
    nt=orient[option["triangle"]][0]
    na,arrow_up,_=orient[option["arrow"]]
    arrow_direction=arrow_up if option["arrow_up"] else neg(arrow_up)
    return cross(nc,nt)==na and arrow_direction==nc


assert [q6_works(o) for o in Q6_OPTIONS]==[False,True,False,False]


Q10_NETS = [
    {(0,1),(1,1),(2,1),(3,1),(1,0),(1,2)},
    {(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)},
    {(0,1),(1,1),(2,1),(3,1),(2,0),(2,2)},
    {(0,0),(1,0),(1,1),(2,1),(2,2),(3,2)},
    {(0,0),(1,0),(2,0),(2,1),(2,2),(1,2)},
    {(0,0),(0,1),(1,0),(1,1),(2,1),(3,1)},
]
Q10_VALID=[fold_orientation(s) is not None for s in Q10_NETS]
assert Q10_VALID==[True,False,True,True,False,False]


def draw10():
    im,d,centers=category_canvas()
    for center,cells in zip(centers,Q10_NETS):
        x,y=center; cell=47
        minr=min(r for r,c in cells);maxr=max(r for r,c in cells)
        minc=min(c for r,c in cells);maxc=max(c for r,c in cells)
        ox=x-(maxc-minc+1)*cell/2
        oy=y-(maxr-minr+1)*cell/2
        for r,c in cells:
            left=ox+(c-minc)*cell; top=oy+(r-minr)*cell
            d.rectangle((left,top,left+cell,top+cell),fill="white",outline=BLACK,width=4)
    save(im,"q10.png")


def draw_all():
    for number in range(1,11):
        globals()[f"draw{number}"]()


if __name__=="__main__":
    draw_all()
    print("q9 perimeters",Q9_PERIMETERS,"q10 valid",Q10_VALID)
