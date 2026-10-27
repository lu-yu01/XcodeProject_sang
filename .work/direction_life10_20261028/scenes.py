"""Deterministic living scenes; shared world coordinates produce every view."""
import math,json
from model import *
from svgkit import *

SCENE_RECORDS=[]
def scene(objects,cam,forward,size=(420,340),eye=1.6,focal=250,horizon=130,shadows=None,paving=False):
    w,h=size
    def p(v):
        q=project(v,cam,forward,w,h,focal,eye,horizon)
        return None if q is None else q[:2]
    def pg(vs,fill='white',width=1.5):
        ps=[p(v) for v in vs]
        return '' if any(a is None for a in ps) else poly(ps,fill,width)
    def ln(a,b,width=1.4,color='#333'):
        a,b=p(a),p(b)
        return '' if a is None or b is None else line(a,b,width,color)
    out=''
    # A quiet ground plane makes the objects a continuous place, not floating blocks.
    if paving:
        for y in [3,5,8,12,18,25,35]:out+=ln((-40,y,0),(40,y,0),.6,'#ccc')
        for x in range(-30,31,5):out+=ln((x,3,0),(x,40,0),.6,'#d2d2d2')
    if shadows:
        from importlib.util import spec_from_file_location,module_from_spec
        spec=spec_from_file_location('old_draw_hull',ROOT.parent/'direction10_20261027'/'draw.py');old=module_from_spec(spec);spec.loader.exec_module(old)
        for obj,offset in zip(objects,shadows):
            x,y=obj['xy'];r=obj.get('radius',.30);hh=obj['height']
            if 'box' in obj:
                bw,bd=obj['box'];base=[(x+u*bw/2,y+v*bd/2) for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
            else:base=[(x+r*math.cos(i*math.tau/32),y+r*math.sin(i*math.tau/32)) for i in range(32)]
            top=[shadow_point(pt,offset['light'],hh) for pt in base] if isinstance(offset,dict) else [(a+offset[0],b+offset[1]) for a,b in base]
            out+=pg([(a,b,0) for a,b in old.hull(base+top)],'#969696',0)
    fwd,right=screen_axes(forward)
    def depth(o):return dot(sub(o['xy'],cam),fwd)
    for obj in sorted(objects,key=depth,reverse=True):
        x,y=obj['xy'];height=obj['height'];kind=obj.get('kind','box')
        base=p((x,y,0));top=p((x,y,height))
        if not base or not top:continue
        if kind in ['tree','lamp']:
            name='tree' if kind=='tree' else 'lamp'
            hh=base[1]-top[1];ww=hh*(1.0 if kind=='tree' else .43)
            out+=icon(name,base[0],base[1],ww,hh)
            continue
        if kind in ['pole','column','monument']:
            r=obj.get('radius',.13 if kind=='pole' else .30)
            if kind=='monument':
                # The plinth, tapering shaft and cap are a recognisable memorial.
                for lo,hi,rr in [(0,.16,r*1.8),(.16,.35,r*1.35),(.35,height-.2,r), (height-.2,height,r*1.15)]:
                    v=[(x-rr,y-rr,lo),(x+rr,y-rr,lo),(x+rr,y+rr,lo),(x-rr,y+rr,lo)]
                    for i in range(4):out+=pg([v[i],v[(i+1)%4],(v[(i+1)%4][0],v[(i+1)%4][1],hi),(v[i][0],v[i][1],hi)],'#eee',1)
                continue
            # Round stone posts have a smooth side, elliptical top and foot.
            half=max(2,focal*r/depth(obj));hh=base[1]-top[1]
            out+=f'<path d="M {f(base[0]-half)} {f(base[1])} L {f(top[0]-half)} {f(top[1])} Q {f(top[0])} {f(top[1]-half*.7)} {f(top[0]+half)} {f(top[1])} L {f(base[0]+half)} {f(base[1])} Q {f(base[0])} {f(base[1]+half*.6)} {f(base[0]-half)} {f(base[1])} Z" fill="#eee" stroke="#222" stroke-width="1.7"/>'
            out+=el('ellipse',cx=f(top[0]),cy=f(top[1]),rx=f(half),ry=f(max(1.5,half*.35)),fill='white',stroke='#222',stroke_width=1.4)
            if kind=='column':
                # Etched rim, not a new cast shadow or a change to cylinder geometry.
                out+=line((top[0]-half,top[1]+hh*.1),(top[0]+half,top[1]+hh*.1),.7,'#777')
            if kind=='pole':
                if obj.get('sign'):
                    z=height*.88;middle=p((x,y,z));s=focal*.64/depth(obj)
                    out+=rect(middle[0]-s,middle[1]-s*.62,2*s,s*1.24,'white',1.8,3)
                    out+=rect(middle[0]-s*.85,middle[1]-s*.47,s*1.7,s*.94,'none',.8,1)
                    # A bus-stop pictogram makes the road sign a familiar object.
                    a,b=middle[0],middle[1]
                    out+=rect(a-s*.43,b-s*.29,s*.86,s*.48,'white',1.3,2)+line((a-s*.28,b-s*.06),(a+s*.28,b-s*.06),1)
                    out+=circle(a-s*.24,b+s*.24,s*.08,'#222',0)+circle(a+s*.24,b+s*.24,s*.08,'#222',0)
                else:
                    for z in [height*.83,height*.95]:
                        a=p((x-right[0]*.55,y-right[1]*.55,z));b=p((x+right[0]*.55,y+right[1]*.55,z))
                        out+=line(a,b,2)
                        for s in [-.45,.45]:
                            q=p((x+right[0]*s,y+right[1]*s,z));out+=circle(q[0],q[1],2.3,'white',1)
            continue
        bw,bd=obj.get('box',(1.5,1.5))
        # Every visible facade receives projected doors/windows on its actual world plane.
        faces=[]
        for axis,side in [(0,-1),(0,1),(1,-1),(1,1)]:
            normal=(side,0) if axis==0 else (0,side)
            center=(x+side*bw/2 if axis==0 else x,y+side*bd/2 if axis==1 else y)
            if dot(normal,sub(cam,center))<=0:continue
            span=bd if axis==0 else bw
            def world(u,z,axis=axis,center=center):
                return (center[0] if axis==0 else center[0]+u,center[1]+u if axis==0 else center[1],z)
            b=pg([world(-span/2,0),world(span/2,0),world(span/2,height),world(-span/2,height)],'white',1.7)
            # Subtle horizontal masonry courses, clear cornice and recessed doorway.
            for z in [height*.06,height*.9,height*.94]:b+=ln(world(-span/2,z),world(span/2,z),.9)
            cols=max(1,min(3,int(span/.8)));rows=max(1,min(4,int(height/1.45)))
            for row in range(rows):
                z=.65+(height*.72-.65)*(row+.5)/rows
                for col in range(cols):
                    u=span*((col+.5)/cols-.5);ww=span/cols*.40;hh=min(.85,height*.13)
                    if row==0 and abs(u)<span*.18:continue
                    b+=pg([world(u-ww/2,z-hh/2),world(u+ww/2,z-hh/2),world(u+ww/2,z+hh/2),world(u-ww/2,z+hh/2)],'#eee',.95)
                    b+=ln(world(u,z-hh/2),world(u,z+hh/2),.65)+ln(world(u-ww/2,z),world(u+ww/2,z),.65)
            doorw=min(.7,span*.25);doorh=min(1.25,height*.34)
            b+=pg([world(-doorw/2,.06),world(doorw/2,.06),world(doorw/2,doorh),world(-doorw/2,doorh)],'#ddd',1)
            b+=ln(world(0,.06),world(0,doorh),.65)
            if kind=='clock':
                z=height*.77;r=min(span*.32,height*.13)
                ps=[world(r*math.cos(i*math.tau/60),z+r*math.sin(i*math.tau/60)) for i in range(60)]
                b+=pg(ps,'white',1.4)
                b+=ln(world(0,z),world(0,z+r*.72),1.5)+ln(world(0,z),world(r*.55,z),1.3)
                for a in [0,math.pi/2,math.pi,math.pi*1.5]:b+=ln(world(r*.83*math.cos(a),z+r*.83*math.sin(a)),world(r*.96*math.cos(a),z+r*.96*math.sin(a)),.7)
            faces.append((dot(sub(center,cam),fwd),b))
        for _,b in sorted(faces,reverse=True):out+=b
        roof=[(x-bw/2,y-bd/2,height),(x+bw/2,y-bd/2,height),(x+bw/2,y+bd/2,height),(x-bw/2,y+bd/2,height)]
        out+=pg(roof,'#f4f4f4',1.4)
        if kind in ['gabled','clock']:
            peak=(x,y,height+(.8 if kind=='gabled' else .55))
            for i in [0,1,2,3]:
                a,b=roof[i],roof[(i+1)%4]
                # Only near-facing roof planes are visible.
                mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
                if dot(sub(mid,(x,y)),sub(cam,mid))>0:out+=pg([a,b,peak],'#eee',1.2)
        if kind=='antenna':
            out+=ln((x,y,height),(x,y,height+1.4),1.8)
            for z in [height+.7,height+1.15]:out+=ln((x-.5,y,z),(x+.5,y,z),1.2)
    SCENE_RECORDS.append({'cam':cam,'forward':forward,'size':size,'eye':eye,'focal':focal,'horizon':horizon,'objects':objects,'shadows':shadows})
    return f'<g clip-path="url(#sceneclip{len(SCENE_RECORDS)})"><defs><clipPath id="sceneclip{len(SCENE_RECORDS)}"><rect width="{w}" height="{h}"/></clipPath></defs>{out}</g>'

PLAZA=[{'xy':(-2,1),'height':4.2,'kind':'clock','box':(1.3,1.3)}, {'xy':(2,2),'height':2.6,'kind':'gabled','box':(1.8,1.6)}, {'xy':(0,-2),'height':3.3,'kind':'monument','radius':.22}]
def motion(n):
    q=Q[n-1]
    objects=[{'xy':(.3,4.8),'height':3.1,'kind':'pole','sign':True}, {'xy':(1.8,9),'height':4,'kind':'pole'}, {'xy':(-3,20),'height':8.0,'kind':'gabled','box':(5.5,4)}, {'xy':(2.3,18),'height':8.5,'kind':'clock','box':(3.5,3.5)}, {'xy':(7,25),'height':7.8,'kind':'box','box':(5.0,4)}]
    if n==2:
        for o in objects:o['xy']=(-o['xy'][1],o['xy'][0])
        objects[0]['sign']=False;objects[1]['kind']='lamp'
    tiles=[scene(objects,q['positions'][t],q['forward'],(420,360),focal=270,horizon=215,paving=n==1) for t in q['display_times']]
    save(frame(tiles,15,376,'①②③④'),n,470)
def plaza():
    from maps import plaza_plan
    tiles=[scene(PLAZA,Q[2]['positions'][t],tuple(-a for a in Q[2]['positions'][t]),(420,340),focal=250,horizon=190) for t in Q[2]['display_times']]
    save(plaza_plan()+frame(tiles,410,356,'①②③④'),3,875)
def panorama():
    objects=[]
    for a,h,k in [(0,6.0,'clock'),(25,4,'gabled'),(50,5.3,'antenna'),(75,3,'box')]:
        a=math.radians(a);objects.append({'xy':(16*math.sin(a),16*math.cos(a)),'height':h,'kind':k,'box':(3.2,3.2)})
    tiles=[]
    for t in Q[3]['display_times']:
        a=math.radians(t*20);tiles.append(scene(objects,(0,0),(math.sin(a),math.cos(a)),(420,355),focal=265,horizon=240,eye=1.7))
    save(frame(tiles,15,371,'①②③④'),4,465)
def sun_observer():
    tile=scene([{'xy':(0,0),'height':3.1,'kind':'box','box':(2.6,2.0)}],(-8,-10),(8,10),(1000,530),eye=4.2,focal=700,horizon=75,shadows=[(0,-4)])
    save(group(tile,400,0),5,560)
def columns(points):return [{'xy':p,'height':1.8,'kind':'column','radius':.3} for p in points]
def sun_posts():
    from maps import post_plan
    vectors=[(-2.2,2.2),(2.2,-2.2),(-2.2,-2.2)]
    groups=[[v,v] for v in vectors]+[[(-2.2,2.2),(2.2,2.2)]]
    tiles=[scene(columns(POSTS6),CAM6,tuple(-a for a in CAM6),(420,360),eye=3.8,focal=480,horizon=-10,shadows=s) for s in groups]
    save(group(post_plan(POSTS6,CAM6,reference=True),525,0)+frame(tiles,365,376),6,815)
def point_light():
    from maps import post_plan
    inward=[];mirrored=[];f,r=screen_axes(tuple(-a for a in CAM7))
    for p in POSTS7:
        v=sub(shadow_point(p,LIGHT,1.8),p);inward.append(tuple(-a for a in v));a=dot(v,f);b=dot(v,r);mirrored.append((a*f[0]-b*r[0],a*f[1]-b*r[1]))
    groups=[[(2.3,-.2)]*3,inward,mirrored,[{'light':LIGHT}]*3]
    tiles=[scene(columns(POSTS7),CAM7,tuple(-a for a in CAM7),(420,360),eye=3.8,focal=440,horizon=-10,shadows=s) for s in groups]
    save(group(post_plan(POSTS7,CAM7,light=LIGHT),525,0)+frame(tiles,365,376),7,815)
def occlusion():
    from maps import map_tile
    objects=[{'xy':(1.5,3),'height':6.5,'kind':'box','box':(2.2,2.0)}, {'xy':(0,1),'height':3.8,'kind':'tree'}, {'xy':(-1.15,-1),'height':3.1,'kind':'box','box':(2.4,1.7)}]
    tile=scene(objects,(0,-10),(0,1),(800,380),eye=1.4,focal=575,horizon=280)
    body=group(tile,500,0)+text(710,30,'矮塔',29)+text(1030,30,'高塔',29)
    body+=arrow((730,50),(790,190),2,9)+arrow((1020,50),(1010,90),2,9)
    tiles=[map_tile(m,size=(420,500),observer=(0,-4),compass=False) for m in TOWER_PLANS]
    save(body+frame(tiles,415,516),10,1010)
def main():
    from maps import home_views,route_picture,solution
    motion(1);motion(2);plaza();panorama();sun_observer();sun_posts();point_light();home_views();route_picture();occlusion()
    for n in range(1,11):solution(n)
    (ROOT/'scene_geometry.json').write_text(json.dumps(SCENE_RECORDS,ensure_ascii=False,indent=2),encoding='utf8')
    (ROOT/'verification.json').write_text(json.dumps(verify(),ensure_ascii=False,indent=2),encoding='utf8')
    export_public();write_usage()
    print('20 native SVG illustrations authored from shared world coordinates')
if __name__=='__main__':main()
