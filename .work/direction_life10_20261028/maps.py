"""Life-like, coordinate-faithful SVG plans and direction explanations.

All icons are anchored by their ground/foot point.  No source coordinates,
choice order, camera heading or answer is changed here.
"""
import math
import svgkit as vk
from svgkit import (ROOT, W, f, el, line, poly, circle, rect, text, arrow,
                    north, group, nested, icon as raw_icon, save, frame)
from model import (Q, HOME, HOME_OPTIONS, ROUTE, ROUTE_STORE, TOWER_PLANS,
                   POSTS6, POSTS7, CAM6, CAM7, LIGHT, relative, unit, sub,
                   shadow_point)

# Bounds measured by rendering each downloaded SVG at 144dpi, flattening to
# white, then reading its visible-content trim box.  Only the native SVG
# viewBox is narrowed here: no source bitmap is edited or re-encoded.
_VISIBLE={
    'house':((342,231),(14,11,317,209)),
    'cinema':((1900,1576),(0,0,1900,1576)),
    'shop':((1600,1600),(0,0,1595,1600)),
    'library':((2640,2640),(79,336,2494,1815)),
    'person':((256,256),(66,7,149,245)),
    'tree':((340,340),(37,0,285,340)),
    'car':((364,250),(11,11,342,228)),
    'clock':((400,1620),(0,0,400,1620)),
    'lamp':((2381,3368),(298,202,1673,3120)),
}

def icon(name,x,y,w=90,h=85):
    """Fit visible source art to a real foot point, preserving its aspect."""
    raw_icon(name,0,0,1,1)  # Prime the shared native-vector cache and usage set.
    view,body=vk._cache[name]
    vx,vy,vw,vh=map(float,view.split())
    if name in _VISIBLE:
        (pw,ph),(bx,by,bw,bh)=_VISIBLE[name]
        # A small vector-space margin protects anti-aliased contour edges.
        left=max(0,bx-pw*.004);top=max(0,by-ph*.004)
        right=min(pw,bx+bw+pw*.004);bottom=min(ph,by+bh+ph*.004)
        vx,vy=vx+vw*left/pw,vy+vh*top/ph
        vw,vh=vw*(right-left)/pw,vh*(bottom-top)/ph
    scale=min(w/vw,h/vh);dw,dh=vw*scale,vh*scale
    vbox=' '.join(f(v) for v in (vx,vy,vw,vh))
    return '<g filter="url(#mono)">'+nested(body,x-dw/2,y-dh,dw,dh,vbox)+'</g>'


def _tower(x, y, w=42, h=62, clock=False, tall=False):
    """A small recognisable tower, not a blank coordinate box."""
    b = rect(x-w*.43, y-h*.82, w*.86, h*.82, '#fafafa', 1.8)
    b += rect(x-w*.50, y-5, w, 5, '#dedede', 1.4)
    b += rect(x-w*.49, y-h*.84, w*.98, 5, '#e7e7e7', 1.5)
    if clock:
        b += poly([(x-w*.5,y-h*.84),(x,y-h),(x+w*.5,y-h*.84)],'#e6e6e6',1.6)
        cy=y-h*.61
        b += circle(x,cy,w*.20,'white',1.3)
        b += line((x,cy),(x,cy-w*.12),1.4)
        b += line((x,cy),(x+w*.11,cy),1.4)
        winlevels=[.29]
    else:
        b += rect(x-w*.50,y-h*.91,w,h*.08,'#dedede',1.5)
        winlevels=[.65,.39] if tall else [.55]
    for level in winlevels:
        for dx in [-.22,.22]:
            wx=x+dx*w
            b += rect(wx-w*.075,y-h*level,w*.15,h*.12,'white',1)
    b += el('path',d=f'M {f(x-w*.115)} {f(y-5)} V {f(y-h*.20)} Q {f(x)} {f(y-h*.31)} {f(x+w*.115)} {f(y-h*.20)} V {f(y-5)}',
            fill='#e2e2e2',stroke='#333',stroke_width='1.2')
    return b


def _monument(x,y,w=29,h=60):
    b=poly([(x-w*.18,y-h),(x+w*.18,y-h),(x+w*.30,y-14),(x-w*.30,y-14)],'#f8f8f8',1.7)
    b+=line((x,y-h+4),(x,y-17),1,'#a4a4a4')
    b+=rect(x-w*.43,y-14,w*.86,7,'#e7e7e7',1.6)
    b+=rect(x-w*.60,y-7,w*1.2,7,'#e0e0e0',1.6)
    return b


def _place(name,x,y,w=62,h=57):
    """Use the same downloaded building/tree illustrations everywhere."""
    names={'家':'house','影院':'cinema','商店':'shop','书店':'library',
           '图书馆':'library','树':'tree','建筑':'house'}
    if name=='矮塔':return _tower(x,y,w*.64,h*.70)
    if name=='高塔':return _tower(x,y,w*.64,h*.97,tall=True)
    if name=='钟楼':return icon('clock',x,y,w*.72,h*1.52)
    if name=='纪念柱':return _monument(x,y,w*.44,h*.93)
    if name=='尖顶馆':return icon('house',x,y,w,h)
    return icon(names.get(name,'house'),x,y,w,h)


def plaza_plan():
    """Return the 1800x400 header plan for question 3."""
    cx,cy,s=900,200,17
    def xy(p):return cx+p[0]*s,cy-p[1]*s
    b=rect(cx-7*s,cy-7*s,14*s,14*s,'#f6f6f6',2,8,stroke='#999')
    # Paving lines establish an everyday plaza without adding causal objects.
    for a in range(-6,7,2):
        b+=line(xy((a,-7)),xy((a,7)),.8,'#dedede')
        b+=line(xy((-7,a)),xy((7,a)),.8,'#dedede')
    x,y=xy((-2,1));b+=_place('钟楼',x,y,59,62)
    b+=text(x-71,y+2,'钟楼',26)
    x,y=xy((2,2));b+=_place('尖顶馆',x,y,58,47)
    b+=text(x+77,y+1,'尖顶馆',26)
    x,y=xy((0,-2));b+=_place('纪念柱',x,y,57,60)
    b+=text(x,y+24,'纪念柱',26)
    for p,name in [((9,0),'东侧'),((0,-9),'南侧'),((-9,0),'西侧'),((0,9),'北侧')]:
        x,y=xy(p);b+=icon('person',x,y,30,45)
        if p[0]:b+=text(x+(49 if p[0]>0 else -49),y-4,name,26)
        else:b+=text(x,y+25,name,26)
    b+=north(1185,165,52)
    return b


def post_plan(points,cam,light=None,reference=False):
    """750x330 top view.  Circle centres are the exact pillar ground axes."""
    allp=list(points)+[cam]+([tuple(light[:2])] if light is not None else [])
    xmin,xmax=min(p[0] for p in allp),max(p[0] for p in allp)
    ymin,ymax=min(p[1] for p in allp),max(p[1] for p in allp)
    s=min(470/max(xmax-xmin,1),180/max(ymax-ymin,1))
    cx,cy=(xmin+xmax)/2,(ymin+ymax)/2
    def xy(p):return 380+(p[0]-cx)*s,180-(p[1]-cy)*s
    b=rect(158,58,470,242,'#fcfcfc',1.2,14,stroke='#c9c9c9')
    # Sparse paving, clipped naturally to the plan's quiet background region.
    for x in range(190,620,43):b+=line((x,65),(x,292),.6,'#e8e8e8')
    for y in range(90,295,40):b+=line((165,y),(620,y),.6,'#e8e8e8')
    for p in points:
        x,y=xy(p)
        b+=circle(x,y,10,'#f8f8f8',2)
        b+=circle(x,y,6.2,'white',.8)
    x,y=xy(cam)
    b+=icon('person',x,y,35,64)
    b+=text(x,y+24,'观察者',28)
    mid=(sum(p[0] for p in points)/len(points),sum(p[1] for p in points)/len(points))
    v=unit(sub(mid,cam));a=(x+v[0]*42,y-v[1]*42);z=(x+v[0]*72,y-v[1]*72)
    b+=arrow(a,z,2.5,10)
    if light is not None:
        x,y=xy(light)
        b+=icon('lamp',x,y,43,69)
        b+=text(x,y+22,'光源',28)
    if reference:
        # A real flagpole and its separate ground-shadow reference.
        px,py=98,226
        b+=line((px,py),(px,py-69),3)
        b+=poly([(px,py-68),(px+33,py-61),(px,py-49)],'#e8e8e8',1.5)
        b+=arrow((px,py),(px-49,py-49),3.5,12)
        b+=text(96,py+27,'旗杆影向',27)
    b+=north(698,148,51)
    return b


def map_tile(mapping,size=(420,500),observer=None,heading=None,compass=True,
             labels=True,observer_label='摄影者'):
    """Illustrated direction plan; monotone rank spacing is not metric scale.

    Equality and the strict ordering on each geographic axis are unchanged.
    The stem expressly excludes distance scale, allowing enough clear space
    for every building instead of overlapping close source points.
    """
    w,h=size
    pts=list(mapping.values())+([observer] if observer is not None else [])
    xs=sorted(set(p[0] for p in pts));ys=sorted(set(p[1] for p in pts))
    def coord(value,values,start,end):
        return (start+end)/2 if len(values)==1 else start+values.index(value)*(end-start)/(len(values)-1)
    def xy(p):return coord(p[0],xs,108,w-82),coord(p[1],ys,h-65,110)
    many=len(ys)>3
    iw,ih=(110,80) if many else (124,100)
    locations={name:xy(p) for name,p in mapping.items()}
    boxes={name:(x-iw/2,y-ih,x+iw/2,y) for name,(x,y) in locations.items()}
    if observer is not None:
        ox,oy=xy(observer);boxes['__observer__']=(ox-30,oy-88,ox+30,oy)
    def intersects(a,z,pad=3):
        return a[0]<z[2]+pad and a[2]>z[0]-pad and a[1]<z[3]+pad and a[3]>z[1]-pad
    b=''
    if compass:
        b+=north(36,114,48)
    elif observer is not None:
        direction=unit(heading or (0,1))
        a=(42,106);z=(42+direction[0]*43,106-direction[1]*43)
        b+=arrow(a,z,2.3,10)
        b+=text(z[0],z[1]-21,'前',27)
    # Footpoints are independently stretched along each axis; no symbols
    # overlap and icon size never implies a geographic distance.
    for name,p in sorted(mapping.items(),key=lambda item:-item[1][1]):
        x,y=xy(p)
        b+=_place(name,x,y,iw,ih)
    if observer is not None:
        x,y=xy(observer)
        b+=icon('person',x,y,59,88)
    occupied=list(boxes.values())
    # Keep the pair closest in the original geography particularly easy to
    # separate: outer cinema caption below/outward, shop caption on the other
    # side with a leader, rather than placing both between their silhouettes.
    close_pair=False
    if '影院' in mapping and '商店' in mapping:
        p,z=mapping['影院'],mapping['商店']
        close_pair=abs(p[0]-z[0])<=1 and abs(p[1]-z[1])<=1
    if labels:
        for name,p in mapping.items():
            x,y=xy(p);width=len(name)*29
            choices=[(x,y+25,False),(x-29,y+25,False),(x+29,y+25,False),
                     (x-88,y-30,True),(x+88,y-30,True),(x,y-ih-24,False)]
            if close_pair and name in ['影院','商店']:
                side=1 if locations['影院'][0]>locations['商店'][0] else -1
                if name=='影院':choices=[(x+side*29,y+25,False)]+choices
                else:choices=[(x-side*88,y-30,True)]+choices
            selected=None
            for lx,ly,leader in choices:
                bb=(lx-width/2,ly-16,lx+width/2,ly+16)
                if bb[0]<8 or bb[2]>w-8 or bb[1]<4 or bb[3]>h-8:continue
                if any(intersects(bb,z) for z in occupied):continue
                selected=(lx,ly,leader,bb);break
            if selected is None:
                # With >=109px rank gaps this is not expected for the current
                # ten questions; fail loudly instead of silently hiding art.
                raise ValueError(('No clear map label slot',name,mapping,size))
            lx,ly,leader,bb=selected
            if leader:
                side=1 if lx>x else -1
                b+=line((x+side*(iw/2+2),ly),(lx-side*(width/2+5),ly),1.2,'#666')
            b+=text(lx,ly,name,29);occupied.append(bb)
        if observer is not None:b+=text(ox,oy+27,observer_label,29)
    return b


def _local_view(mapping,origin,forward,caption,size=(720,420)):
    w,h=size;cx,cy=w/2,330
    b=icon('person',cx,cy,72,110)
    b+=arrow((cx,206),(cx,151),2.7,12)+text(cx,126,'前',29)
    b+=text(cx,395,caption,30)
    for name,p in mapping.items():
        a,bf=relative(p,origin,forward)
        x,y=cx+a*65,cy-bf*70
        b+=_place(name,x,y,135,100)
        b+=text(x,y+26,name,31)
    return b


def home_views():
    b=group(_local_view({k:HOME[k] for k in ['影院','商店']},HOME['家'],(0,1),'家门口 朝北'),90,0)
    b+=group(_local_view({k:HOME[k] for k in ['家','图书馆']},HOME['影院'],(-1,0),'影院门口 朝西'),990,0)
    b+=frame([map_tile(m) for m in HOME_OPTIONS],455,516)
    save(b,8,1060)
    return b


def route_picture():
    ang=math.radians(28);s=56;cx,cy=900,232
    def xy(p):
        x,y=p[0]-2,p[1]-2
        return cx+s*(x*math.cos(ang)+y*math.sin(ang)),cy+s*(x*math.sin(ang)-y*math.cos(ang))
    path=' '.join(f'{f(x)},{f(y)}' for x,y in map(xy,ROUTE))
    b=el('polyline',points=path,fill='none',stroke='#a9a9a9',stroke_width='43',stroke_linecap='round',stroke_linejoin='round')
    b+=el('polyline',points=path,fill='none',stroke='#ededed',stroke_width='37',stroke_linecap='round',stroke_linejoin='round')
    b+=el('polyline',points=path,fill='none',stroke='white',stroke_width='27',stroke_linecap='round',stroke_linejoin='round')
    for a,z in zip(ROUTE[:-1],ROUTE[1:]):
        x1,y1=xy(a);x2,y2=xy(z)
        b+=line((x1,y1),(x2,y2),3.3)
        b+=arrow((x1+(x2-x1)*.34,y1+(y2-y1)*.34),(x1+(x2-x1)*.64,y1+(y2-y1)*.64),3.6,14)
    for p,name in [(ROUTE[0],'家'),(ROUTE_STORE,'书店'),(ROUTE[-1],'影院')]:
        x,y=xy(p)
        b+=_place(name,x,y,112,85)
        b+=text(x,y+25,name,30)
    b+=north(1220,190,64,ang)
    tiles=[]
    for forward in [(0,-1),(1,0),(-1,0),(-1,0)]:
        m={name:relative(p,ROUTE[-1],forward) for name,p in [('家',ROUTE[0]),('书店',ROUTE_STORE)]}
        if len(tiles)==3:m={name:(-p[0],p[1]) for name,p in m.items()}
        tiles.append(map_tile(m,observer=(0,0),heading=(0,1),compass=False,observer_label='小周'))
    b+=frame(tiles,430,516)
    save(b,9,1035)
    return b


def _sequence(labels,subtitle=None):
    b=''
    for i,label in enumerate(labels):
        x=250+i*430
        b+=text(x,112,label,54,True)
        if i<3:b+=arrow((x+64,112),(x+345,112),3.7,17)
    if subtitle:b+=text(900,244,subtitle,38)
    return b


def solution(n):
    """Save one 1800x410 explanatory SVG; never redraw a candidate as proof."""
    if n in [1,2]:
        q=Q[n-1];order=[q['display_times'].index(t)+1 for t in range(4)]
        b=_sequence(['①②③④'[i-1] for i in order],'近景相对远景的位移更大')
        b+=icon('car',280,369,163,105)
        b+=text(1035,336,'倒车 左窗向北 景物向右' if n==1 else '前进 左窗向西 景物向左',36)
    elif n==3:
        b=''
        for i,(caption,label) in enumerate(zip(['东侧 向西看','南侧 向北看','西侧 向东看','北侧 向南看'],['②','④','③','①'])):
            x=250+i*430
            b+=text(x,89,caption,34)+text(x,205,label,54,True)
            if i<3:b+=arrow((x+72,205),(x+345,205),3.2,16)
        b+=icon('clock',530,392,46,137)
        b+=text(1080,331,'以同一地标核对不同朝向的左右',33)
    elif n==4:
        b=_sequence(['④','②','①','③'],'人向右转 固定景物向画面左侧退出')
    elif n==5:
        # The ground shadow is geographic south, independent of the observer.
        cx,cy,s=460,155,39
        b=rect(cx-45,cy-30,90,60,'#f6f6f6',2)
        for x in [-22,0,22]:b+=rect(cx+x-5,cy-15,10,14,'white',1)
        b+=arrow((cx,cy+30),(cx,cy+128),4,17)
        b+=text(cx+91,cy+100,'南影',31)
        b+=icon('person',cx-156,cy+195,50,80)+text(cx-156,cy+224,'观察者',28)
        b+=north(718,145,52)
        b+=text(1230,135,'北侧太阳 → 南向影子',39)
        b+=text(1230,246,'观察者在西南',43,True)
    elif n==6:
        b=group(post_plan(POSTS6,CAM6,reference=True),50,35)
        b+=text(1280,131,'日影在地面上同向',42,True)
        b+=text(1280,245,'从西南向东北看',38)
    elif n==7:
        cx,cy,s=850,190,48
        def xy(p):return cx+p[0]*s,cy-p[1]*s
        b=''
        for p in POSTS7:
            end=shadow_point(p,LIGHT,1.8)
            a,z,e=xy(LIGHT),xy(p),xy(end)
            b+=line(a,z,1.7,'#a6a6a6','6 5')+arrow(z,e,4,14)
            b+=circle(z[0],z[1],11,'white',2)
        x,y=xy(LIGHT)
        b+=icon('lamp',x,y,45,76)+text(x,y+27,'光源投影',28)
        b+=text(1415,125,'各柱背光发散',40,True)
        b+=text(1415,236,'影线回指同一光源',34)
    elif n==8:
        b=group(_local_view({k:HOME[k] for k in ['影院','商店']},HOME['家'],(0,1),'家门口 朝北'),50,-10)
        b+=text(1270,109,'家朝北 右为东',38)
        b+=text(1270,210,'影院朝西 右为北',38)
        b+=text(1270,311,'两次观察分别换算',34)
    elif n==9:
        b=text(900,74,'向北 → 向东 → 向南 → 右转后向西',41,True)
        # Local view after the right turn: geographic west is screen front.
        b+=icon('house',585,274,93,76)+text(585,314,'家 在左前',36)
        b+=icon('library',1235,274,93,76)+text(1235,314,'书店 在右前',36)
        b+=icon('person',900,342,43,68)
        b+=arrow((900,256),(900,191),3,13)+text(900,167,'前',29)
    else:
        b=''
        positions=[225,665,1105,1545]
        b+=icon('person',positions[0],229,45,79)
        b+=_tower(positions[1],229,65,87)
        b+=icon('tree',positions[2],229,92,99)
        b+=_tower(positions[3],229,65,126,tall=True)
        for i,name in enumerate(['摄影者','矮塔','树','高塔']):
            b+=text(positions[i],275,name,36)
            if i<3:b+=arrow((positions[i]+72,179),(positions[i+1]-82,179),3.1,15)
        b+=text(900,358,'由近到远按遮挡链确定',36)
    save(b,n,410,'solution')
    return b


if __name__=='__main__':
    home_views();route_picture()
    for number in range(1,11):solution(number)
