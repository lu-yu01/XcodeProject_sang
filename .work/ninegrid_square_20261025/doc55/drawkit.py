"""Deterministic black-and-white diagram primitives for the 55-item workbook."""
from __future__ import annotations
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
BLACK = '#111111'
GRAY = '#666666'
FONT = 'C:/Windows/Fonts/msyh.ttc'
LAYOUTS = {}

def font(size): return ImageFont.truetype(FONT, size)
def canvas(h=820, w=1800):
    im=Image.new('RGB',(w,h),'white')
    return im, ImageDraw.Draw(im)
def label(d,x,y,s,size=42): d.text((x,y),str(s),font=font(size),fill=BLACK,anchor='mm')
def save(im,n): im.save(ASSETS/f'q{n:02}.png',dpi=(300,300))

def frame_row(d,box,n):
    x0,y0,x1,y1=box
    d.rectangle(box,outline=BLACK,width=5)
    for i in range(1,n):
        x=round(x0+(x1-x0)*i/n)
        d.line((x,y0,x,y1),fill=BLACK,width=4)
    return [(x0+(i+.5)*(x1-x0)/n,(y0+y1)/2) for i in range(n)]

def options(d,y0=470,y1=740):
    centers=frame_row(d,(170,y0,1630,y1),4)
    for i,(x,_) in enumerate(centers):label(d,x,y1+36,'ABCD'[i],41)
    return centers

def sequence(n):
    im,d=canvas(820)
    centers=frame_row(d,(55,50,1745,355),6)
    choices=options(d)
    LAYOUTS[n]={'kind':'sequence','stem_centers':centers,'option_centers':choices}
    return im,d,centers,choices

def two_groups(n):
    im,d=canvas(820)
    left=frame_row(d,(55,50,855,355),3)
    right=frame_row(d,(945,50,1745,355),3)
    choices=options(d)
    centers=left+right
    assert len({y for x,y in centers})==1
    LAYOUTS[n]={'kind':'two_groups_horizontal','stem_centers':centers,'option_centers':choices}
    return im,d,centers,choices

def matrix(n):
    im,d=canvas(1170)
    # A true 3x3 matrix: equal outer dimensions and equal square cells.
    # Keep height, canvas and option row unchanged; translate stem artwork only.
    x0,y0,x1,y1=480,40,1320,880
    d.rectangle((x0,y0,x1,y1),outline=BLACK,width=5)
    for i in (1,2):
        x=x0+i*(x1-x0)/3;y=y0+i*(y1-y0)/3
        d.line((x,y0,x,y1),fill=BLACK,width=4)
        d.line((x0,y,x1,y),fill=BLACK,width=4)
    centers=[(x0+(c+.5)*(x1-x0)/3,y0+(r+.5)*(y1-y0)/3) for r in range(3) for c in range(3)]
    choices=options(d,930,1080)
    LAYOUTS[n]={'kind':'matrix','outer_box':[x0,y0,x1,y1],
                'cell_sizes':[[280,280]]*9,
                'stem_centers':centers,'option_centers':choices}
    return im,d,centers,choices

def classification(n):
    im,d=canvas(810)
    centers=[(x,y) for y in (210,565) for x in (420,900,1380)]
    for i,(x,y) in enumerate(centers):
        d.rectangle((x-137,y-137,x+137,y+137),outline=BLACK,width=5)
        label(d,x,y+167,'①②③④⑤⑥'[i],41)
    LAYOUTS[n]={'kind':'classification_3x2','stem_centers':centers}
    return im,d,centers

def grid(d,cx,cy,cells,n=4,size=190,dots=None):
    side=size/n;x0=cx-size/2;y0=cy-size/2
    for r in range(n):
        for c in range(n):
            rect=(x0+c*side,y0+r*side,x0+(c+1)*side,y0+(r+1)*side)
            d.rectangle(rect,fill=BLACK if (r,c) in cells else 'white',outline=GRAY,width=2)
    if dots:
        for r,c in dots:
            x=x0+(c+.5)*side;y=y0+(r+.5)*side
            d.ellipse((x-10,y-10,x+10,y+10),fill='white',outline=BLACK,width=4)

def rotate(cells,n=4): return {(c,n-1-r) for r,c in cells}
def reflect(cells,n=4): return {(r,n-1-c) for r,c in cells}
def shift(cells,dr=0,dc=1,n=4): return {((r+dr)%n,(c+dc)%n) for r,c in cells}
def complement(cells,n=4): return {(r,c) for r in range(n) for c in range(n)}-set(cells)

def arrow(d,cx,cy,angle,length=95,width=7):
    # 0 points up, 1 right, 2 down, 3 left.
    a=angle*math.pi/2;vx=math.sin(a);vy=-math.cos(a)
    x0=cx-vx*length*.45;y0=cy-vy*length*.45
    x1=cx+vx*length*.45;y1=cy+vy*length*.45
    d.line((x0,y0,x1,y1),fill=BLACK,width=width)
    px,py=-vy,vx
    d.polygon([(x1+vx*9,y1+vy*9),(x1-vx*20+px*13,y1-vy*20+py*13),(x1-vx*20-px*13,y1-vy*20-py*13)],fill=BLACK)

def dots(d,cx,cy,count,spacing=23):
    for i in range(count):
        x=cx+(i-(count-1)/2)*spacing
        d.ellipse((x-6,cy-6,x+6,cy+6),fill=BLACK)

def polygon(d,cx,cy,sides,radius=80,angle=-math.pi/2,fill=None,width=6):
    pts=[(cx+radius*math.cos(angle+2*math.pi*i/sides),cy+radius*math.sin(angle+2*math.pi*i/sides)) for i in range(sides)]
    if fill:d.polygon(pts,fill=fill)
    d.line(pts+[pts[0]],fill=BLACK,width=width,joint='curve')
    return pts

def planarize(segments):
    """Split straight segments at all exact intersections; return undirected edges."""
    segs=[(tuple(map(Fraction,a)),tuple(map(Fraction,b))) for a,b in segments]
    nodes=[{a,b} for a,b in segs]
    def cross(a,b):return a[0]*b[1]-a[1]*b[0]
    def sub(a,b):return(a[0]-b[0],a[1]-b[1])
    for i,(a,b) in enumerate(segs):
        u=sub(b,a)
        for j in range(i+1,len(segs)):
            c,e=segs[j];v=sub(e,c);den=cross(u,v)
            if den:
                t=cross(sub(c,a),v)/den;s=cross(sub(c,a),u)/den
                if 0<=t<=1 and 0<=s<=1:
                    p=(a[0]+t*u[0],a[1]+t*u[1]);nodes[i].add(p);nodes[j].add(p)
            else:
                for p in (a,b,c,e):
                    if cross(sub(p,a),u)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1]):nodes[i].add(p)
                    if cross(sub(p,c),v)==0 and min(c[0],e[0])<=p[0]<=max(c[0],e[0]) and min(c[1],e[1])<=p[1]<=max(c[1],e[1]):nodes[j].add(p)
    edges=set()
    for (a,b),pts in zip(segs,nodes):
        pts=sorted(pts,key=lambda p:(p[0]-a[0])**2+(p[1]-a[1])**2)
        edges.update(tuple(sorted((x,y))) for x,y in zip(pts,pts[1:]) if x!=y)
    return edges

def graph_stats(edges):
    degrees=Counter(v for e in edges for v in e);seen=set();components=0
    adjacency={v:set() for v in degrees}
    for a,b in edges:adjacency[a].add(b);adjacency[b].add(a)
    for v in degrees:
        if v in seen:continue
        components+=1;queue=[v];seen.add(v)
        for at in queue:
            for nxt in adjacency[at]:
                if nxt not in seen:seen.add(nxt);queue.append(nxt)
    faces=len(edges)-len(degrees)+components
    strokes=sum(max(1,sum(degrees[v]%2 for v in part)//2) for part in graph_components(adjacency))
    return dict(faces=faces,components=components,strokes=strokes,degrees=degrees,adjacency=adjacency)

def graph_components(adj):
    seen=set();result=[]
    for v in adj:
        if v in seen:continue
        group={v};queue=[v];seen.add(v)
        for a in queue:
            for b in adj[a]:
                if b not in seen:seen.add(b);group.add(b);queue.append(b)
        result.append(group)
    return result

def network(d,cx,cy,edges,size=180,show_nodes=True):
    points={v for edge in edges for v in edge}
    lo_x=min(p[0] for p in points);hi_x=max(p[0] for p in points)
    lo_y=min(p[1] for p in points);hi_y=max(p[1] for p in points)
    scale=size/max(float(hi_x-lo_x),float(hi_y-lo_y),1)
    def pt(p):return(cx+float(p[0]-(lo_x+hi_x)/2)*scale,cy+float(p[1]-(lo_y+hi_y)/2)*scale)
    for a,b in edges:d.line((*pt(a),*pt(b)),fill=BLACK,width=6)
    if show_nodes:
        for v in points:
            x,y=pt(v);d.ellipse((x-5,y-5,x+5,y+5),fill=BLACK)

def question(n,stem,answer,point,analysis,options=None,level='中等',ask=''):
    return dict(n=n,category='图形推理',stem=stem,ask=ask,options=options or [],answer=answer,
                point=point,analysis=analysis,image=f'q{n:02}.png',explanation_image=None,level=level)
