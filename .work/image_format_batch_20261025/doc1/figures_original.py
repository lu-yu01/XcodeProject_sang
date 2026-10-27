"""精确几何题图；不依赖生成式图片。"""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
FONT = 'C:/Windows/Fonts/msyh.ttc'
BLACK = '#161616'
RED = '#c52d2d'
BLUE = '#2573b8'


def font(size):
    return ImageFont.truetype(FONT, size)


def canvas(h, w=1500):
    im = Image.new('RGB', (w, h), 'white')
    return im, ImageDraw.Draw(im)


def text(d, xy, s, size=35, fill=BLACK):
    d.text(xy, s, font=font(size), fill=fill, anchor='mm')


def line(d, pts, width=4, fill=BLACK):
    d.line(pts, fill=fill, width=width, joint='curve')


def polygon(d, pts, fill=None, width=4):
    if fill:
        d.polygon(pts, fill=fill)
    line(d, pts + [pts[0]], width)


def regular(cx, cy, r, n, a=-math.pi/2):
    return [(cx+r*math.cos(a+2*math.pi*k/n), cy+r*math.sin(a+2*math.pi*k/n)) for k in range(n)]


def save(im, name):
    im.save(ASSETS/name, dpi=(300,300))


def grid(d, cx, cy, size, n=4, filled=(), outline=True):
    left, top = cx-size/2, cy-size/2
    cell = size/n
    for k in filled:
        row,col=divmod(k,n)
        d.rectangle([left+col*cell,top+row*cell,left+(col+1)*cell,top+(row+1)*cell],fill=BLACK)
    if outline:
        for k in range(n+1):
            line(d,[(left+k*cell,top),(left+k*cell,top+size)],3)
            line(d,[(left,top+k*cell),(left+size,top+k*cell)],3)


OUTER = [(0,0),(0,1),(0,2),(1,2),(2,2),(2,1),(2,0),(1,0)]
Q1_OPTIONS = [(5,3),(6,1),(5,1),(3,1)]
Q2_A = {0,1,4,6,9,14}
Q2_B = {1,3,4,7,10,15}
Q2_C = Q2_A ^ Q2_B
Q2_OPTIONS = [Q2_C, Q2_A|Q2_B, Q2_A&Q2_B, set(range(16))-Q2_C]
Q4_SOURCE = [{0,1,2,4,5,8},{3,6,7,9,10,13},{0,3,5,10,12,15},{1,4,7,8,11,14}]
Q4_OPTIONS = [{0,5,10,15},{1,3,4,6,9,14},{0,1,4,5,10,11,14,15},{0,2,4,7,8,10,13}]
CUBE_OPTIONS = [(4,1,2),(1,6,3),(4,1,3),(5,1,4)]
# Occupancy stored front row first, then back row. Display reverses it.
VIEW_OPTIONS = [[[1,0,0],[0,1,1]], [[1,1,0],[0,0,1]], [[0,1,1],[0,1,0]], [[0,1,1],[1,0,0]]]
AREA_FACES = [3,2,4,5,3,4]
AREA_DOTS = [2,2,4,4,3,3]


def movement(d,cx,cy,pos,orient,size=170):
    grid(d,cx,cy,size,3)
    r,c=OUTER[pos]
    x=cx-size/2+(c+.5)*size/3
    y=cy-size/2+(r+.5)*size/3
    d.ellipse((x-13,y-13,x+13,y+13),fill=BLACK)
    # Direction order: up, right, down, left.
    angle=orient*math.pi/2
    local=[(-6,18),(6,18),(6,-2),(16,-2),(0,-21),(-16,-2),(-6,-2)]
    pts=[(cx+x*math.cos(angle)-y*math.sin(angle),cy+x*math.sin(angle)+y*math.cos(angle)) for x,y in local]
    polygon(d,pts,BLACK,2)


def draw1():
    im,d=canvas(520)
    for k,x in enumerate([140,384,628,872,1116]):
        movement(d,x,125,k,k%4)
    text(d,(1360,125),'?',78)
    for k,(pos,a) in enumerate(Q1_OPTIONS):
        movement(d,300+300*k,355,pos,a)
        text(d,(300+300*k,475),'ABCD'[k],38)
    save(im,'q01.png')


def draw2():
    im,d=canvas(840)
    a={0,2,5,8,12,15}; b={1,2,4,8,10,15}
    c={0,3,5,6,9,12}; e={0,2,6,7,10,12}
    rows=[[a,b,a^b],[c,e,c^e],[Q2_A,Q2_B,None]]
    for r,row in enumerate(rows):
        for col,filled in enumerate(row):
            cx,cy=490+260*col,110+210*r
            if filled is None:
                text(d,(cx,cy),'?',75)
            else:
                grid(d,cx,cy,165,4,filled)
    for k,filled in enumerate(Q2_OPTIONS):
        grid(d,300+300*k,700,140,4,filled)
        text(d,(300+300*k,805),'ABCD'[k],32)
    save(im,'q02.png')


def symshape(d,cx,cy,kind,size=155):
    r=size/2
    if kind=='iso': polygon(d,[(cx,cy-r),(cx-r*.67,cy+r),(cx+r*.67,cy+r)])
    elif kind=='rect': polygon(d,[(cx-r,cy-r*.62),(cx+r,cy-r*.62),(cx+r,cy+r*.62),(cx-r,cy+r*.62)])
    elif kind=='triangle': polygon(d,regular(cx,cy,r,3))
    elif kind=='square': polygon(d,[(cx-r*.8,cy-r*.8),(cx+r*.8,cy-r*.8),(cx+r*.8,cy+r*.8),(cx-r*.8,cy+r*.8)])
    elif kind=='para': polygon(d,[(cx-r*.55,cy-r*.6),(cx+r,cy-r*.6),(cx+r*.55,cy+r*.6),(cx-r,cy+r*.6)])
    elif kind=='hex': polygon(d,regular(cx,cy,r,6))
    elif kind=='pent': polygon(d,regular(cx,cy,r,5))


def draw3():
    im,d=canvas(440)
    for i,kind in enumerate(['iso','rect','triangle','square']):symshape(d,170+i*285,100,kind)
    text(d,(1310,100),'?',75)
    for i,kind in enumerate(['para','hex','rect','pent']):
        symshape(d,300+i*300,305,kind)
        text(d,(300+i*300,415),'ABCD'[i],33)
    save(im,'q03.png')


def draw4():
    im,d=canvas(450)
    for i,filled in enumerate(Q4_SOURCE):grid(d,170+i*285,105,160,4,filled)
    text(d,(1310,105),'?',75)
    for i,filled in enumerate(Q4_OPTIONS):
        grid(d,300+i*300,320,155,4,filled)
        text(d,(300+i*300,430),'ABCD'[i],33)
    save(im,'q04.png')


def cube(d,cx,cy,labels,s=70):
    a=(cx,cy); b=(cx-s,cy-s*.55); c=(cx,cy-s*1.1); e=(cx+s,cy-s*.55)
    f=(cx-s,cy+s*.6); g=(cx,cy+s*1.15); h=(cx+s,cy+s*.6)
    for pts in [[a,b,c,e],[a,b,f,g],[a,e,h,g]]:polygon(d,pts)
    for p,v in zip([(cx,cy-s*.53),(cx-s*.48,cy+s*.28),(cx+s*.48,cy+s*.28)],labels): text(d,p,str(v),32)


def draw5():
    im,d=canvas(440)
    s=85; ox=160; oy=120
    cells={1:(0,0),2:(-1,0),3:(1,0),4:(0,-1),5:(0,1),6:(0,2)}
    for val,(x,y) in cells.items():
        px,py=ox+x*s,oy+y*s
        d.rectangle((px,py,px+s,py+s),outline=BLACK,width=4)
        text(d,(px+s/2,py+s/2),str(val),34)
    for i,vals in enumerate(CUBE_OPTIONS):
        cube(d,560+i*265,185,vals,86)
        text(d,(560+i*265,355),'ABCD'[i],35)
    save(im,'q05.png')
    im,d=canvas(300)
    for i,(a,b) in enumerate([(1,6),(2,3),(4,5)]):
        text(d,(220+i*420,60),f'{a} 与 {b} 相对',37)
    cube(d,750,185,(4,1,3),75)
    text(d,(1100,185),'上4 · 前1 · 右3',37,RED)
    save(im,'q05_explain.png')


def projection(p,ox=260,oy=320,scale=170):
    x,y,z=p
    return ox+scale*(x+.65*y),oy-scale*(z+.4*y)


def section_projection(p,ox,oy,scale):
    # Look along (1,1,1), normal to the cutting plane, so all six edges are visible.
    x,y,z=p
    return ox+scale*math.sqrt(3)/2*(x-y),oy+scale*((x+y)/2-z)


VERTS=[(x,y,z) for x in (0,1) for y in (0,1) for z in (0,1)]
MIDPOINTS=[(1,.5,0),(.5,1,0),(0,1,.5),(0,.5,1),(.5,0,1),(1,0,.5)]


def dashed(d,p1,p2,fill='#777777',width=3):
    length=math.dist(p1,p2)
    for start in range(0,int(length),15):
        end=min(start+8,length)
        a=tuple(p1[i]+(p2[i]-p1[i])*start/length for i in (0,1))
        b=tuple(p1[i]+(p2[i]-p1[i])*end/length for i in (0,1))
        line(d,[a,b],width,fill)


def cutcube(d,ox,oy,scale,section=False):
    project=section_projection if section else projection
    hidden=(0,0,0) if section else (0,1,0)
    for i,v in enumerate(VERTS):
        for w in VERTS[i+1:]:
            if sum(a!=b for a,b in zip(v,w))==1:
                p1,p2=project(v,ox,oy,scale),project(w,ox,oy,scale)
                # Three edges incident to the far corner are hidden.
                if v==hidden or w==hidden:dashed(d,p1,p2)
                else:line(d,[p1,p2],4)
    if section:
        line(d,[project(p,ox,oy,scale) for p in MIDPOINTS+[MIDPOINTS[0]]],6,RED)
    for label,p,delta in [('P',(1,.5,0),(25,18)),('Q',(0,1,.5),(34,4)),('R',(.5,0,1),(0,-25))]:
        if section and label=='Q':delta=(-28,0)
        x,y=project(p,ox,oy,scale)
        d.ellipse((x-6,y-6,x+6,y+6),fill=RED if section else BLACK)
        text(d,(x+delta[0],y+delta[1]),label,33,RED if section else BLACK)


def draw6():
    im,d=canvas(440)
    cutcube(d,70,330,190)
    for i,kind in enumerate(['hex','rect','pent','triangle']):
        symshape(d,610+i*240,200,kind,165)
        text(d,(610+i*240,355),'ABCD'[i],36)
    save(im,'q06.png')
    im,d=canvas(430)
    cutcube(d,450,190,170,True)
    text(d,(450,400),'旋转视角显示截面',29)
    polygon(d,regular(1050,200,130,6),None,5)
    text(d,(1050,380),'六个交点均为棱的中点',33)
    save(im,'q06_explain.png')


def elevation(d,cx,base,heights,size=57):
    left=cx-len(heights)*size/2
    for c,h in enumerate(heights):
        for row in range(h):
            d.rectangle((left+c*size,base-(row+1)*size,left+(c+1)*size,base-row*size),outline=BLACK,width=3)


def occupancy(d,cx,cy,rows,heights=False):
    size=60; left=cx-90;top=cy-60
    for display_row,row in enumerate(reversed(rows)):
        for col,v in enumerate(row):
            box=(left+col*size,top+display_row*size,left+(col+1)*size,top+(display_row+1)*size)
            d.rectangle(box,fill='#dedede' if v and not heights else 'white',outline=BLACK,width=3)
            if heights: text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),str(v) if v else '—',26)
    text(d,(cx,cy+89),'前',26)
    text(d,(cx,cy-87),'后',26)


def draw7():
    im,d=canvas(520)
    elevation(d,560,210,[2,3,1]);text(d,(560,250),'正视图',34)
    elevation(d,960,210,[3,2]);text(d,(960,250),'右视图',34)
    for i,rows in enumerate(VIEW_OPTIONS):
        occupancy(d,300+i*300,380,rows)
        text(d,(300+i*300,500),'ABCD'[i],32)
    save(im,'q07.png')
    im,d=canvas(300)
    occupancy(d,450,140,[[0,3,1],[2,0,0]],True)
    text(d,(990,105),'数字表示各位置堆放高度',34)
    text(d,(990,175),'正面：2、3、1；右面：3、2',33)
    save(im,'q07_explain.png')


def draw8():
    im,d=canvas(520)
    positions=[(320,120),(750,120),(1180,120),(320,370),(750,370),(1180,370)]
    for i,(cx,cy) in enumerate(positions):
        r=85
        if i==0: polygon(d,[(cx-r,cy-r),(cx-r,cy+r),(cx+r,cy+r)])
        if i==1: symshape(d,cx,cy,'para',180)
        if i==2:
            pts=[]
            for k in range(10):
                a=-math.pi/2+k*math.pi/5;rr=r if k%2==0 else r*.43
                pts.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
            polygon(d,pts)
        if i==3:
            pts=[(-1,-.8),(1,-.8),(1,-.5),(-.4,.5),(1,.5),(1,.8),(-1,.8),(-1,.5),(.4,-.5),(-1,-.5)]
            polygon(d,[(cx+x*r,cy+y*r) for x,y in pts])
        if i==4:polygon(d,[(cx-r*.5,cy-r*.7),(cx+r*.5,cy-r*.7),(cx+r,cy+r*.7),(cx-r,cy+r*.7)])
        if i==5:
            pts=[(1,0),(3,0),(3,1),(2,1),(2,2),(0,2),(0,1),(1,1)]
            polygon(d,[(cx+(x-1.5)*60,cy+(y-1)*60) for x,y in pts])
        text(d,(cx,cy+115),'①②③④⑤⑥'[i],32)
    save(im,'q08.png')


def draw9():
    im,d=canvas(520)
    positions=[(320,120),(750,120),(1180,120),(320,370),(750,370),(1180,370)]
    for i,(cx,cy) in enumerate(positions):
        r=77
        if i==0:line(d,[(cx-r,cy+r*.6),(cx-r*.4,cy-r*.8),(cx+r*.4,cy+r*.6),(cx+r,cy-r*.8)],5)
        if i==1:
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=BLACK,width=5)
            line(d,[(cx-r,cy),(cx+r,cy)],5)
        if i==2:
            line(d,[(cx-r,cy),(cx+r,cy)],5);line(d,[(cx,cy-r),(cx,cy+r)],5)
        if i==3:
            rr=46
            d.ellipse((cx-2*rr,cy-rr,cx,cy+rr),outline=BLACK,width=5)
            d.ellipse((cx,cy-rr,cx+2*rr,cy+rr),outline=BLACK,width=5)
            d.ellipse((cx-2,cy-2,cx+2,cy+2),fill=BLACK)
        if i==4:
            polygon(d,[(cx-r,cy-r),(cx+r,cy-r),(cx+r,cy+r),(cx-r,cy+r)],width=5)
            line(d,[(cx-r,cy-r),(cx+r,cy+r)],5);line(d,[(cx+r,cy-r),(cx-r,cy+r)],5)
        if i==5:
            line(d,[(cx-r,cy-r*.65),(cx+r,cy-r*.65)],5)
            line(d,[(cx,cy-r*.65),(cx,cy+r)],5)
        text(d,(cx,cy+115),'①②③④⑤⑥'[i],32)
    save(im,'q09.png')


def draw10():
    im,d=canvas(520)
    positions=[(320,120),(750,120),(1180,120),(320,370),(750,370),(1180,370)]
    for i,(cx,cy) in enumerate(positions):
        n=AREA_FACES[i];dots=AREA_DOTS[i];r=85
        polygon(d,[(cx-r,cy-r),(cx+r,cy-r),(cx+r,cy+r),(cx-r,cy+r)])
        for k in range(1,n):
            if i%2==0:line(d,[(cx-r+2*r*k/n,cy-r),(cx-r+2*r*k/n,cy+r)],3)
            else:line(d,[(cx-r,cy-r+2*r*k/n),(cx+r,cy-r+2*r*k/n)],3)
        for k in range(dots):
            if i%2==0:x,y=cx-r+2*r*(k+.5)/n,cy+(-1)**k*28
            else:x,y=cx+(-1)**k*28,cy-r+2*r*(k+.5)/n
            d.ellipse((x-8,y-8,x+8,y+8),fill=BLACK)
        text(d,(cx,cy+115),'①②③④⑤⑥'[i],32)
    save(im,'q10.png')


def main():
    for f in [draw1,draw2,draw3,draw4,draw5,draw6,draw7,draw8,draw9,draw10]:f()
    return ASSETS


if __name__=='__main__':
    main()
    print('Generated 13 figures:', ASSETS)
