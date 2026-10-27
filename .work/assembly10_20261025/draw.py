"""Exact voxel projections and assembly layer diagrams for ten original items."""
from pathlib import Path
import math,json
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
ASSETS.mkdir(exist_ok=True)
INK='#151515'
FONT='C:/Windows/Fonts/msyh.ttc'
LAYOUTS={}

def text(d,xy,value,size=32,anchor='mm',fill=INK):
    d.text(xy,str(value),font=ImageFont.truetype(FONT,size),fill=fill,anchor=anchor)

def normalize(shape):
    mins=[min(p[a] for p in shape) for a in range(3)]
    return sorted(tuple(p[a]-mins[a] for a in range(3)) for p in shape)

def voxel(d,shape,box,view=1,scale_cap=96):
    """Orthographic isometric drawing; only actually exposed faces are painted."""
    shape=normalize(shape)
    if view==-1:shape=normalize([(-x,-y,z) for x,y,z in shape])
    cells=set(shape)
    def project(p):
        x,y,z=p
        return ((x-y)*math.sqrt(3)/2,(x+y)/2-z)
    faces=[]
    spec=[((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)],'#d4d4d4'),
          ((0,1,0),[(0,1,0),(0,1,1),(1,1,1),(1,1,0)],'#ededed'),
          ((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)],'#ffffff')]
    for p in shape:
        for direction,vertices,fill in spec:
            if tuple(p[i]+direction[i] for i in range(3)) in cells:continue
            verts=[tuple(p[i]+v[i] for i in range(3)) for v in vertices]
            faces.append((sum(sum(v) for v in verts)/4,[project(v) for v in verts],fill))
    points=[p for _,poly,_ in faces for p in poly]
    minx,maxx=min(p[0] for p in points),max(p[0] for p in points)
    miny,maxy=min(p[1] for p in points),max(p[1] for p in points)
    x0,y0,x1,y1=box
    scale=min((x1-x0-18)/(maxx-minx),(y1-y0-18)/(maxy-miny),scale_cap)
    cx,cy=(x0+x1)/2,(y0+y1)/2
    def tr(p):return (round(cx+(p[0]-(minx+maxx)/2)*scale),round(cy+(p[1]-(miny+maxy)/2)*scale))
    bounds=[]
    for depth,poly,fill in sorted(faces,key=lambda f:f[0]):
        out=[tr(p) for p in poly]
        d.polygon(out,fill=fill)
        d.line(out+[out[0]],fill=INK,width=3,joint='curve')
        bounds.extend(out)
    assert all(x0<=x<=x1 and y0<=y<=y1 for x,y in bounds)
    return {'cells':shape,'view':view,'scale':scale,'box':box}

def panel(d,shape,box,title,scale_cap=96):
    x0,y0,x1,y1=box
    d.rectangle(box,outline='#555555',width=2)
    text(d,((x0+x1)/2,y0+34),title+f'  共{len(shape)}块',32)
    mid=(x0+x1)/2
    records=[voxel(d,shape,(x0+10,y0+65,mid-5,y1-48),1,scale_cap),voxel(d,shape,(mid+5,y0+65,x1-10,y1-48),-1,scale_cap)]
    text(d,((x0+mid)/2,y1-24),'视角一',30,fill='#444444')
    text(d,((mid+x1)/2,y1-24),'视角二',30,fill='#444444')
    return records

def question(q):
    im=Image.new('RGB',(1800,1400),'white');d=ImageDraw.Draw(im)
    shapes=list(q['pieces']);names=list('甲乙丙丁')[:len(shapes)]
    if q['mode']=='fill':shapes.append(q['target']);names.append('目标')
    panels=[];width=1760/len(shapes)
    specs=[]
    for i,(shape,name) in enumerate(zip(shapes,names)):
        specs.append((shape,(20+i*width,15,20+(i+1)*width-12,405),name))
    for i,shape in enumerate(q['options']):
        col,row=i%2,i//2;x=20+col*890;y=438+row*470
        specs.append((shape,(x,y,x+870,y+445),'ABCD'[i]))
    # One physical unit length per question, shared by every part, target and option.
    common_scale=96
    for shape,(x0,y0,x1,y1),_ in specs:
        for view in (1,-1):
            cells=normalize(shape if view==1 else [(-x,-y,z) for x,y,z in shape])
            points=[((x+a-y-b)*math.sqrt(3)/2,(x+a+y+b)/2-z-c) for x,y,z in cells for a in (0,1) for b in (0,1) for c in (0,1)]
            pw=max(p[0] for p in points)-min(p[0] for p in points)
            ph=max(p[1] for p in points)-min(p[1] for p in points)
            common_scale=min(common_scale,((x1-x0)/2-33)/pw,(y1-y0-131)/ph)
    for shape,box,name in specs[:len(shapes)]:panels.append(panel(d,shape,box,name,common_scale))
    options=[]
    for shape,box,name in specs[len(shapes):]:options.append(panel(d,shape,box,name,common_scale))
    path=ASSETS/f'q{q["n"]:02}.png';im.save(path,dpi=(300,300))
    LAYOUTS[q['n']]={'size':im.size,'common_unit_scale':common_scale,'parts':panels,'options':options,'format':'two opposed views per solid; four options in 2 by 2'}
    return path

def solution(q):
    parts=q['solution']
    allcells=set(tuple(p) for piece in parts for p in piece)
    maxs=[max(p[a] for p in allcells)+1 for a in range(3)]
    nx,ny,nz=maxs
    w=1800;h=max(450,170+ny*85)
    im=Image.new('RGB',(w,h),'white');d=ImageDraw.Draw(im)
    names=list('甲乙丙丁')[:len(parts)]
    if q['mode']=='fill':names[-1]='选'+q['answer']
    shades=['#ffffff','#dddddd','#b9b9b9','#eeeeee']
    for z in range(nz):
        panelw=w/nz;unit=min(100,(panelw-110)/nx,(h-200)/ny)
        x0=z*panelw+(panelw-nx*unit)/2;y0=96
        title=f'第{z+1}层'+(' 底层' if z==0 else '')
        text(d,(z*panelw+panelw/2,40),title,34)
        for y in range(ny):
            for x in range(nx):
                p=(x,y,z);row=ny-1-y
                box=(x0+x*unit,y0+row*unit,x0+(x+1)*unit,y0+(row+1)*unit)
                owner=next((i for i,part in enumerate(parts) if p in set(map(tuple,part))),None)
                if owner is not None:
                    d.rectangle(box,fill=shades[owner],outline=INK,width=2)
                    text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),names[owner],32)
                else:
                    d.rectangle(box,fill='#f6f6f6',outline='#bbbbbb',width=1)
                    text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),'空',32,fill='#777777')
    text(d,(w/2,h-28),'各层保持同一朝向 左右为x方向 上下为y方向 由底向上叠放',32)
    path=ASSETS/f'q{q["n"]:02}_solution.png';im.save(path,dpi=(300,300))
    return path

def draw_all(questions):
    for q in questions:question(q);solution(q)
    (ROOT/'figure_layout.json').write_text(json.dumps(LAYOUTS,ensure_ascii=False,indent=2),encoding='utf-8')

