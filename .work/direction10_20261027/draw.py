from pathlib import Path
import math,json
from PIL import Image,ImageDraw,ImageFont
from model import *
ASSETS=ROOT/'assets';ASSETS.mkdir(exist_ok=True)
W=1800
def font(s,b=False):return ImageFont.truetype('C:/Windows/Fonts/simhei.ttf' if b else 'C:/Windows/Fonts/simsun.ttc',s)
def text(d,p,t,s=31,b=False,anchor='mm',fill='black'):d.text(p,t,font=font(s,b),anchor=anchor,fill=fill)
def line(d,a,b,width=3,fill='black'):d.line([tuple(a),tuple(b)],fill=fill,width=width)
def arrow(d,a,b,width=3,fill='black',head=13):
 line(d,a,b,width,fill);v=unit(sub(b,a));r=(-v[1],v[0])
 d.polygon([b,(b[0]-head*v[0]+head*.5*r[0],b[1]-head*v[1]+head*.5*r[1]),(b[0]-head*v[0]-head*.5*r[0],b[1]-head*v[1]-head*.5*r[1])],fill=fill)
def hull(points):
 p=sorted(set(points))
 if len(p)<3:return p
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];up=[]
 for a in p:
  while len(lo)>=2 and cross(lo[-2],lo[-1],a)<=0:lo.pop()
  lo.append(a)
 for a in reversed(p):
  while len(up)>=2 and cross(up[-2],up[-1],a)<=0:up.pop()
  up.append(a)
 return lo[:-1]+up[:-1]
def scene(objects,cam,forward,size=(420,340),eye=1.6,focal=250,horizon=130,shadows=None,grid=False):
 """Ground XY and vertical Z; camera screen-right is (forward_y,-forward_x)."""
 w,h=size;scale=2
 im=Image.new('RGB',(w*scale,h*scale),'white');d=ImageDraw.Draw(im)
 def p(v):
  q=project(v,cam,forward,w,h,focal,eye,horizon)
  return None if q is None else (q[0]*scale,q[1]*scale,q[2])
 def polygon(pts,fill,outline='black',width=2):
  ps=[p(v) for v in pts]
  if any(v is None for v in ps):return
  xy=[v[:2] for v in ps];d.polygon(xy,fill=fill)
  if outline:d.line(xy+[xy[0]],fill=outline,width=width*scale,joint='curve')
 # Ground geometry is drawn before solids; solid faces hide shadows correctly.
 if grid:
  for y in [-4,0,4,8]:
   a=p((-6,y,0));b=p((6,y,0))
   if a and b:line(d,a[:2],b[:2],1*scale,'#dddddd')
 if shadows:
  for obj,offset in zip(objects,shadows):
   x,y=obj['xy'];radius=obj.get('radius',.35);height=obj['height']
   if 'box' in obj:
    bw,bd=obj['box'];base=[(x+u*bw/2,y+v*bd/2) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
   else:base=[(x+radius*math.cos(i*math.tau/24),y+radius*math.sin(i*math.tau/24)) for i in range(24)]
   if isinstance(offset,dict):
    L=offset['light'];top=[shadow_point(pt,L,height) for pt in base]
   else:top=[(a+offset[0],b+offset[1]) for a,b in base]
   polygon([(a,b,0) for a,b in hull(base+top)],'#929292',None)
 faces=[];details=[]
 for obj in objects:
  x,y=obj['xy'];height=obj['height'];kind=obj.get('kind','box')
  if kind in ('pole','column','tree'):
   radius=obj.get('radius',.13 if kind=='pole' else .28)
   n=16;base=[(x+radius*math.cos(i*math.tau/n),y+radius*math.sin(i*math.tau/n),0) for i in range(n)]
   top=[(a,b,height) for a,b,_ in base]
   for i in range(n):
    j=(i+1)%n;poly=[base[i],base[j],top[j],top[i]]
    ps=[p(v) for v in poly]
    if all(v for v in ps):faces.append((sum(v[2] for v in ps)/4,poly,'#eeeeee',0))
   faces.append((sum(p(v)[2] for v in top)/n,top,'white',1))
   # Only the two tangent contours are drawn, avoiding false vertical grooves.
   f,r=screen_axes(forward)
   for side in [-1,1]:
    v0=(x+side*r[0]*radius,y+side*r[1]*radius,0)
    v1=(v0[0],v0[1],height)
    faces.append((p(v0)[2]-.01,[v0,v1],None,1))
   if kind=='tree':
    # An opaque crown, rendered as a compact polygonal ellipsoid.
    rr=obj.get('crown',1.5);z0=height*.58;z1=height+rr*.35
    verts=[(x+rr*math.cos(i*math.tau/14),y+rr*math.sin(i*math.tau/14),z0) for i in range(14)]
    for i in range(14):
     poly=[verts[i],verts[(i+1)%14],(x,y,z1)]
     faces.append((sum(p(v)[2] for v in poly)/3,poly,'#c2c2c2',2))
   if kind=='pole' and obj.get('sign'):
    # A small road sign remains perpendicular to the viewing direction.
    f,r=screen_axes(forward);s=.65
    poly=[(x-r[0]*s,y-r[1]*s,height*.78),(x+r[0]*s,y+r[1]*s,height*.78),(x+r[0]*s,y+r[1]*s,height),(x-r[0]*s,y-r[1]*s,height)]
    faces.append((sum(p(v)[2] for v in poly)/4,poly,'white',2))
   continue
  bw,bd=obj.get('box',(1.5,1.5));zroof=height
  pts=[(x-bw/2,y-bd/2,0),(x+bw/2,y-bd/2,0),(x+bw/2,y+bd/2,0),(x-bw/2,y+bd/2,0)]
  verts=pts+[(a,b,zroof) for a,b,_ in pts]
  for ids,fill in [([0,1,5,4],'white'),([1,2,6,5],'#e6e6e6'),([2,3,7,6],'white'),([3,0,4,7],'#ededed'),([4,5,6,7],'#f5f5f5')]:
   poly=[verts[i] for i in ids];ps=[p(v) for v in poly]
   if all(v for v in ps):faces.append((sum(v[2] for v in ps)/len(ps),poly,fill,2))
  if kind=='gabled':
   peak=(x,y,height+1.0)
   for i in range(4):
    poly=[verts[4+i],verts[4+(i+1)%4],peak]
    faces.append((sum(p(v)[2] for v in poly)/3,poly,'#dddddd',2))
  if kind=='antenna':
   for a,b in [((x,y,height),(x,y,height+1.7)),((x-.6,y,height+1.2),(x+.6,y,height+1.2))]:
    details.append((a,b))
  if kind=='clock':
   # Four clock faces, one on each side of the tower.
   for axis,side in [(0,-1),(0,1),(1,-1),(1,1)]:
    center=(x+side*bw/2 if axis==0 else x,y+side*bd/2 if axis==1 else y,height*.76)
    normal=(side,0) if axis==0 else (0,side)
    if dot(normal,sub(cam,center[:2]))<=0:continue
    r=.38;circle=[]
    for i in range(41):
     t=math.tau*i/40
     circle.append((center[0]+(0 if axis==0 else r*math.cos(t)),center[1]+(r*math.cos(t) if axis==0 else 0),center[2]+r*math.sin(t)))
    faces.append((p(center)[2]-.005,circle,'white',1))
    details.append((center,(center[0],center[1],center[2]+r*.7)))
    details.append((center,(center[0]+(0 if axis==0 else r*.65),center[1]+(r*.65 if axis==0 else 0),center[2])))
 for depth,poly,fill,width in sorted(faces,key=lambda x:-x[0]):
  if len(poly)==2:
   a,b=map(p,poly)
   if a and b:line(d,a[:2],b[:2],scale*width)
  else:polygon(poly,fill,outline=None if width==0 else 'black',width=width)
 for a,b in details:
  aa=p(a);bb=p(b)
  if aa and bb:line(d,aa[:2],bb[:2],2*scale)
 # Smooth round pillars have two silhouette contours, not a bundle of mesh edges.
 # These isolated pillars do not overlap in the two shadow questions.
 for obj in objects:
  if obj.get('kind')!='column':continue
  x,y=obj['xy'];radius=obj.get('radius',.30);height=obj['height'];f,r=screen_axes(forward)
  for side in [-1,1]:
   a=p((x+side*r[0]*radius,y+side*r[1]*radius,0));b=p((x+side*r[0]*radius,y+side*r[1]*radius,height))
   if a and b:line(d,a[:2],b[:2],2*scale)
 return im.resize((w,h),Image.Resampling.LANCZOS)

def north(d,x,y,size=55,angle=0):
 v=(math.sin(angle),-math.cos(angle));arrow(d,(x,y),(x+v[0]*size,y+v[1]*size),head=14)
 text(d,(x+v[0]*(size+22),y+v[1]*(size+22)),'北',29)
def common_frame(im,tiles,y,labels='ABCD',height=None):
 d=ImageDraw.Draw(im);left=20;col=440;top=y;height=height or tiles[0].height+16
 d.rectangle((left,top,left+4*col,top+height),outline='black',width=3)
 for j,tile in enumerate(tiles):
  im.paste(tile,(left+j*col+(col-tile.width)//2,top+8))
  if j:line(d,(left+j*col,top),(left+j*col,top+height),3)
  text(d,(left+j*col+col/2,top+height+37),labels[j],38,True)
 return top+height+75
def map_tile(mapping,size=(420,300),observer=None,heading=None,compass=True,labels=True,observer_label='摄影者'):
 w,h=size;im=Image.new('RGB',size,'white');d=ImageDraw.Draw(im)
 pts=list(mapping.values())+([observer] if observer else [])
 xmin=min(p[0] for p in pts)-1.0;xmax=max(p[0] for p in pts)+1.0
 ymin=min(p[1] for p in pts)-1.0;ymax=max(p[1] for p in pts)+1.0
 scale=min((w-100)/(xmax-xmin),(h-70)/(ymax-ymin))
 def xy(p):return (w/2+(p[0]-(xmin+xmax)/2)*scale,h/2-(p[1]-(ymin+ymax)/2)*scale)
 for name,point in mapping.items():
  x,y=xy(point);d.ellipse((x-5,y-5,x+5,y+5),fill='black');text(d,(x,y+25 if name=='商店' else y-23),name,29)
 if observer is not None:
  x,y=xy(observer);d.ellipse((x-7,y-7,x+7,y+7),fill='white',outline='black',width=2)
  text(d,(x,y+24),observer_label if not heading else '小周',28)
  if heading:arrow(d,(x,y-10),(x+heading[0]*28,y-heading[1]*28),head=9)
 if compass:north(d,38,100,43)
 return im

def save(im,n,kind='question'):
 path=ASSETS/f'{kind}-{n:02}.png';im.save(path,dpi=(300,300));return path
def motion(n):
 q=Q[n-1];im=Image.new('RGB',(W,470),'white')
 objects=[{'xy':(.3,4.8),'height':3.1,'kind':'pole','sign':True},
  {'xy':(1.8,9),'height':4.0,'kind':'pole'},
  {'xy':(-3,20),'height':7,'kind':'gabled','box':(3,3)},
  {'xy':(2.3,18),'height':7.5,'kind':'clock','box':(2.8,2.8)},
  {'xy':(6,25),'height':7,'kind':'box','box':(3,3)}]
 if n==2:
  # Rotate the whole environment so the camera looks west.
  for obj in objects:
   x,y=obj['xy'];obj['xy']=(-y,x)
  objects[0]['sign']=False;objects[0]['radius']=.18
 tiles=[]
 for t in q['display_times']:
  tile=scene(objects,q['positions'][t],q['forward'],size=(420,360),horizon=155,focal=260)
  # Horizon remains visible as a reference; no background layer is mechanically shifted.
  tiles.append(tile)
 common_frame(im,tiles,15,'①②③④');save(im,n)

PLAZA=[{'xy':(-2,1),'height':4.2,'kind':'clock','box':(1.3,1.3)},
 {'xy':(2,2),'height':2.6,'kind':'gabled','box':(1.8,1.6)},
 {'xy':(0,-2),'height':3.3,'kind':'box','box':(.5,.5)}]
def plaza():
 im=Image.new('RGB',(W,875),'white');d=ImageDraw.Draw(im)
 cx,cy,s=900,200,17
 def xy(p):return (cx+p[0]*s,cy-p[1]*s)
 d.rectangle((cx-7*s,cy-7*s,cx+7*s,cy+7*s),outline='#999999',width=3)
 for o,name in zip(PLAZA,['钟楼','尖顶馆','纪念柱']):
  x,y=xy(o['xy']);d.rectangle((x-9,y-9,x+9,y+9),fill='white',outline='black',width=2)
  dx,dy={'钟楼':(-48,-26),'尖顶馆':(45,-26),'纪念柱':(0,30)}[name];text(d,(x+dx,y+dy),name,29)
 for p,name in [((9,0),'东'),((0,-9),'南'),((-9,0),'西'),((0,9),'北')]:
  x,y=xy(p);d.ellipse((x-6,y-6,x+6,y+6),fill='black');text(d,(x+(33 if p[0] else 0),y+(-25 if p[1]>0 else 28 if p[1]<0 else 0)),name,29)
 north(d,1160,145,50)
 q=Q[2];tiles=[]
 for t in q['display_times']:
  cam=q['positions'][t];tiles.append(scene(PLAZA,cam,(-cam[0],-cam[1]),size=(420,340),horizon=130,focal=225))
 common_frame(im,tiles,410,'①②③④');save(im,3)

def panorama():
 im=Image.new('RGB',(W,465),'white');objs=[]
 for a,h,k in [(0,6.0,'clock'),(25,4,'gabled'),(50,5.3,'antenna'),(75,3,'box')]:
  a=math.radians(a);objs.append({'xy':(16*math.sin(a),16*math.cos(a)),'height':h,'kind':k,'box':(2.3,2.3)})
 tiles=[]
 for t in Q[3]['display_times']:
  a=math.radians(t*20);tiles.append(scene(objs,(0,0),(math.sin(a),math.cos(a)),size=(420,355),focal=240,horizon=180,eye=1.7))
 common_frame(im,tiles,15,'①②③④');save(im,4)

def sun_observer():
 objects=[{'xy':(0,0),'height':3.1,'kind':'box','box':(2.6,2.0)}]
 tile=scene(objects,(-8,-10),(8,10),size=(1000,530),eye=4.2,focal=700,horizon=75,shadows=[(0,-4)])
 im=Image.new('RGB',(W,560),'white');im.paste(tile,(400,0));save(im,5)

def posts(observations,kind):
 return [{'xy':p,'height':1.8,'kind':'column','radius':.30} for p in observations]
def post_plan(points,cam,light=None,reference=None):
 im=Image.new('RGB',(750,330),'white');d=ImageDraw.Draw(im)
 # A common world scale keeps the observer and light in their true relative positions.
 allp=points+[cam]+([light[:2]] if light else [])
 xmin,xmax=min(p[0] for p in allp)-1,max(p[0] for p in allp)+1
 ymin,ymax=min(p[1] for p in allp)-1,max(p[1] for p in allp)+1
 s=min(570/(xmax-xmin),220/(ymax-ymin));cx=(xmin+xmax)/2;cy=(ymin+ymax)/2
 def xy(p):return (375+(p[0]-cx)*s,155-(p[1]-cy)*s)
 for p in points:
  x,y=xy(p);r=max(11,.30*s);d.ellipse((x-r,y-r,x+r,y+r),fill='white',outline='black',width=3)
 x,y=xy(cam);d.ellipse((x-7,y-7,x+7,y+7),fill='black');text(d,(x,y+26),'观察者',28)
 mid=(sum(p[0] for p in points)/len(points),sum(p[1] for p in points)/len(points));v=unit(sub(mid,cam));arrow(d,(x+v[0]*13,y-v[1]*13),(x+v[0]*45,y-v[1]*45),head=11)
 if light:
  x,y=xy(light);d.ellipse((x-11,y-11,x+11,y+11),fill='white',outline='black',width=2)
  line(d,(x-16,y),(x+16,y),2);line(d,(x,y-16),(x,y+16),2);text(d,(x,y-35),'光源',28)
 if reference:
  start=(100,215);end=(start[0]-60,start[1]-60);arrow(d,start,end,4,head=15);text(d,(112,252),'参照影向',27)
 north(d,665,160,53)
 return im
def sun_posts():
 im=Image.new('RGB',(W,815),'white');im.paste(post_plan(POSTS6,CAM6,reference=True),(525,0))
 obj=posts(POSTS6,'sun');vectors=[(-2.2,2.2),(2.2,-2.2),(-2.2,-2.2)]
 groups=[[v,v] for v in vectors]+[[(-2.2,2.2),(2.2,2.2)]]
 tiles=[scene(obj,CAM6,(-CAM6[0],-CAM6[1]),size=(420,360),eye=3.8,focal=480,horizon=-10,shadows=s) for s in groups]
 common_frame(im,tiles,365);save(im,6)
def point_light():
 im=Image.new('RGB',(W,815),'white');im.paste(post_plan(POSTS7,CAM7,light=LIGHT),(525,0))
 obj=posts(POSTS7,'point');correct=[{'light':LIGHT}]*3
 wrong_parallel=[(2.3,-.2)]*3
 inward=[];mirrored=[]
 f,r=screen_axes((-CAM7[0],-CAM7[1]))
 for p in POSTS7:
  e=shadow_point(p,LIGHT,1.8);v=sub(e,p);inward.append((-v[0],-v[1]))
  # Reflect the shadow displacement horizontally in this viewing frame.
  along=dot(v,f);side=dot(v,r);mirrored.append((along*f[0]-side*r[0],along*f[1]-side*r[1]))
 tiles=[scene(obj,CAM7,(-CAM7[0],-CAM7[1]),size=(420,360),eye=3.8,focal=440,horizon=-10,shadows=s) for s in [wrong_parallel,inward,mirrored,correct]]
 common_frame(im,tiles,365);save(im,7)

def local_view(mapping,origin,forward,observer,size=(720,300)):
 im=Image.new('RGB',size,'white');d=ImageDraw.Draw(im);cx,cy=size[0]/2,235
 d.ellipse((cx-7,cy-7,cx+7,cy+7),fill='black');text(d,(cx,cy+29),observer,28)
 arrow(d,(cx,cy-15),(cx,cy-70),head=12);text(d,(cx,cy-90),'前',28)
 for name,p in mapping.items():
  x,y=relative(p,origin,forward);x=cx+x*55;y=cy-y*48
  d.rectangle((x-7,y-7,x+7,y+7),outline='black',width=2);text(d,(x,y-24),name,30)
 return im
def home_views():
 im=Image.new('RGB',(W,770),'white');d=ImageDraw.Draw(im)
 im.paste(local_view({k:HOME[k] for k in ['影院','商店']},HOME['家'],(0,1),'家门口 朝北'),(90,0))
 im.paste(local_view({k:HOME[k] for k in ['家','图书馆']},HOME['影院'],(-1,0),'影院门口 朝西'),(990,0))
 tiles=[map_tile(m,size=(420,330)) for m in HOME_OPTIONS];common_frame(im,tiles,360);save(im,8)

def route_picture():
 im=Image.new('RGB',(W,805),'white');d=ImageDraw.Draw(im);ang=math.radians(28);s=56;cx,cy=900,180
 def xy(p):
  x,y=p[0]-2,p[1]-2;return (cx+s*(x*math.cos(ang)+y*math.sin(ang)),cy+s*(x*math.sin(ang)-y*math.cos(ang)))
 for a,b in zip(ROUTE[:-1],ROUTE[1:]):
  x1,y1=xy(a);x2,y2=xy(b);line(d,(x1,y1),(x2,y2),5)
  arrow(d,(x1+(x2-x1)*.35,y1+(y2-y1)*.35),(x1+(x2-x1)*.65,y1+(y2-y1)*.65),4,head=16)
 for p,t in [(ROUTE[0],'家'),(ROUTE[-1],'影院'),(ROUTE_STORE,'书店')]:
  x,y=xy(p);d.ellipse((x-6,y-6,x+6,y+6),fill='black');text(d,(x+(-30 if t=='家' else 32),y-22),t,31)
 north(d,1200,160,65,ang)
 tiles=[]
 for f in [(0,-1),(1,0),(-1,0),(-1,0)]:
  mapping={k:relative(p,ROUTE[-1],f) for k,p in [('家',ROUTE[0]),('书店',ROUTE_STORE)]}
  if len(tiles)==3:mapping={k:(-p[0],p[1]) for k,p in mapping.items()}
  t=map_tile(mapping,size=(420,330),observer=(0,0),compass=False,observer_label='小周')
  td=ImageDraw.Draw(t);arrow(td,(52,110),(52,55),head=12);text(td,(52,32),'前',27)
  tiles.append(t)
 common_frame(im,tiles,385);save(im,9)

def occlusion():
 obj=[{'xy':(1.5,3),'height':6.5,'kind':'box','box':(2.2,2.0)},
 {'xy':(0,1),'height':3.6,'kind':'tree','radius':.18,'crown':1.65},
 {'xy':(-1.15,-1),'height':3.1,'kind':'box','box':(2.4,1.7)}]
 im=Image.new('RGB',(W,845),'white')
 tile=scene(obj,(0,-10),(0,1),size=(800,380),eye=1.4,focal=575,horizon=280)
 im.paste(tile,(500,0));d=ImageDraw.Draw(im)
 # Labels identify the two towers; no label obscures an occlusion boundary.
 text(d,(710,35),'矮塔',30);text(d,(1030,30),'高塔',30)
 arrow(d,(730,55),(790,190),2,head=10);arrow(d,(1020,50),(1010,90),2,head=10)
 tiles=[map_tile(m,size=(420,340),observer=(0,-4),compass=False) for m in TOWER_PLANS]
 common_frame(im,tiles,415);save(im,10)

def solution(n):
 """An independent schematic used to explain the direction, rather than repeat choices."""
 im=Image.new('RGB',(1800,410),'white');d=ImageDraw.Draw(im)
 if n in [1,2]:
  q=Q[n-1];order=[q['display_times'].index(i)+1 for i in range(4)]
  for i,l in enumerate(order):
   x=270+i*420;text(d,(x,110),'①②③④'[l-1],58,True)
   if i<3:arrow(d,(x+60,110),(x+325,110),4,head=19)
  text(d,(900,220),'近景相对远景的位移更大',42)
  text(d,(900,310),'倒车 左窗向北 景物向右' if n==1 else '前进 左窗向西 景物向左',40)
 elif n==3:
  for i,(p,l) in enumerate(zip(['东侧 向西看','南侧 向北看','西侧 向东看','北侧 向南看'],['②','④','③','①'])):
   x=250+i*430;text(d,(x,100),p,36);text(d,(x,210),l,56,True)
   if i<3:arrow(d,(x+110,210),(x+320,210),3,head=16)
 elif n==4:
  for i,l in enumerate(['④','②','①','③']):
   x=250+i*430;text(d,(x,115),l,56,True)
   if i<3:arrow(d,(x+70,115),(x+350,115),3,head=16)
  text(d,(900,245),'人向右转 固定景物向画面左侧退出',40)
 elif n in [5,6,7]:
  if n==5:
   tile=map_tile({'建筑':(0,0),'南影':(0,-3)},size=(800,360),observer=(-4,-5),compass=True)
   im.paste(tile,(90,15));text(d,(1270,130),'北侧太阳 → 南向影子',40);text(d,(1270,240),'观察者在西南',43,True)
  elif n==6:
   p=post_plan(POSTS6,CAM6,reference=True);im.paste(p,(50,30))
   text(d,(1280,120),'日影 地面同向',43,True);text(d,(1280,235),'从西南向东北看',39)
  else:
   cx,cy=850,195;sc=50
   def xy(p):return (cx+p[0]*sc,cy-p[1]*sc)
   for p in POSTS7:
    e=shadow_point(p,LIGHT,1.8);a=xy(LIGHT);b=xy(p);c=xy(e)
    line(d,a,b,2,'#aaaaaa');arrow(d,b,c,4,head=15);d.ellipse((b[0]-10,b[1]-10,b[0]+10,b[1]+10),fill='white',outline='black',width=3)
   text(d,xy(LIGHT),'光源',31);text(d,(1400,105),'各柱背光发散',39,True)
 elif n==8:
  im.paste(map_tile(HOME,size=(800,380)),(100,0));text(d,(1300,130),'家朝北 右为东',40);text(d,(1300,240),'影院朝西 右为北',40)
 elif n==9:
  text(d,(900,70),'向北 → 向东 → 向南 → 右转后向西',43,True)
  text(d,(600,210),'家 在左前',42);text(d,(1250,210),'书店 在右前',42)
 else:
  for i,t in enumerate(['摄影者','矮塔','树','高塔']):
   x=230+i*440;text(d,(x,150),t,45,True)
   if i<3:arrow(d,(x+90,150),(x+345,150),3,head=16)
  text(d,(900,275),'由近到远按遮挡链确定',39)
 return save(im,n,'solution')

if __name__=='__main__':
 motion(1);motion(2);plaza();panorama();sun_observer();sun_posts();point_light();home_views();route_picture();occlusion()
 for i in range(1,11):solution(i)
 print('20 final question and solution images created')
