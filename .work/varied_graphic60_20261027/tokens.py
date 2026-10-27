"""Original groups 15--20: varied glyph and symbolic graphic operations.

Discrete visible scenes; independent pull-back/matrix implementation included.
No document generation or knowledge-base mutations in this module.
"""
from __future__ import annotations
import copy
import hashlib
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw


RULES = {
15: [
 ('orbit','↻','四个箭头沿圆周顺时针移一站，指向不变。'),
 ('turn','↷','每个箭头的指向均顺时针转90°，位置不变。'),
 ('black','B','仅实心箭头原地调转180°。'),
 ('fill','◇','所有箭头的实心、空心互换。'),
 ('vertical','↕','仅交换上、下两站的箭头。'),
 ('horizontal','↔','仅交换左、右两站的箭头。'),
],
16: [
 ('cycle','C','所有字母按F→P→R→F替换，朝向保留。'),
 ('orbit','△','三个字母沿三角形顺时针移一站，朝向不变。'),
 ('turn','↷','每个字母原地顺时针旋转90°。'),
 ('mirror','⇆','每个字母仅在原位左右镜像。'),
 ('select','F²','仅当前的F原地旋转180°。'),
 ('base','↔','仅交换下方两个字母，朝向不变。'),
],
17: [
 ('orbit','↻','六个图形沿环形轨道顺时针移一站。'),
 ('reverse','⇆','以竖直直径为轴交换左右站位，图形自身不变。'),
 ('shape','S','所有形状按圆→三角→方→圆替换，空实保留。'),
 ('fill','◇','所有图形的实心、空心互换。'),
 ('opposite','↕','仅交换最上、最下两站的图形。'),
 ('black','B','仅实心图形按圆→三角→方→圆替换。'),
],
18: [
 ('branches','⇄','交换根节点下的两个整分支，各分支内部次序不变。'),
 ('siblings','↔','左右分支内部的两个末端图形分别互换。'),
 ('middle','M','仅交换从左到右第2、3个末端图形。'),
 ('left','L','仅左分支图形按圆→三角→方→圆替换。'),
 ('fill','◇','四个末端图形的实心、空心互换。'),
 ('black','B','仅实心末端按圆→三角→方→圆替换。'),
],
19: [
 ('reverse','⇆','四个完整图形的左右次序颠倒。'),
 ('outlines','E','仅外轮廓依次左移一位，最左轮廓移至最右。'),
 ('marks','K','仅内部标记依次右移一位，最右标记移至最左。'),
 ('markcycle','T','所有内标记按点→叉→横杠→点替换。'),
 ('shapecycle','S','所有外轮廓按圆→方→三角→六边形→圆替换。'),
 ('middle','M','仅交换中间两个图形的内部标记。'),
],
20: [
 ('xor','⊕','左图改为左右图的异或；右图不变。'),
 ('and','∩','右图改为左右图的交集；左图不变。'),
 ('or','∪','左图改为左右图的并集；右图不变。'),
 ('swap','⇄','左右两图互换。'),
 ('half','↶','左右两图分别在原位旋转180°。'),
 ('complement','¬','右图八条射线取补：黑段变白，白段变黑。'),
]}
TITLES={15:'箭头的站位、指向与空实',16:'字母替换与字形操作',17:'环形轨道上的选择性变换',18:'树形末端与分支操作',19:'外轮廓与内部标记分离',20:'双输入八辐射线形运算'}
INTROS={
15:'四站固定在上、右、下、左，圆周细线仅用于定位，不参与操作。空心与实心以整个箭头是否填黑区分。移站不会改变箭头指向。',
16:'三站依次为上、右下、左下。字母可旋转、镜像；字母替换保留已有的旋转和镜像状态。三角形细线仅定位。',
17:'六站自最上方起顺时针排列。轨道只定位；三角形均尖端朝上。形状替换只改形状，保留空实。',
18:'树形连线固定不变，只操作四个末端图形。末端从左到右计数；形状替换保留空实，新三角形均尖端朝上。',
19:'四个图形均由外轮廓和内标记组成。轮廓与标记可分别移动；未提到的另一层及位置均不变。',
20:'两图各有八条射线位置，自正上方起顺时针排列；黑段为集合元素，空白细框为未选段。集合运算逐段进行，均使用该步操作前的左右图。',
}
KINDS={15:'arrows',16:'letters',17:'orbit',18:'tree',19:'containers',20:'rays'}


def _rule_id(g,n): return f'T{g}_{n}'
def _decode(opid):
    head, op=opid.split('_',1)
    return int(head[1:]), op


def apply(scene, opid):
    s=copy.deepcopy(scene)
    g, op=_decode(opid)
    assert s['kind']==KINDS[g]
    v=s['items']
    if g==15:
        if op=='orbit': s['items']=[v[-1]]+v[:-1]
        elif op=='turn':
            for q in v:q[0]=(q[0]+1)%4
        elif op=='black':
            for q in v:
                if q[1]:q[0]=(q[0]+2)%4
        elif op=='fill':
            for q in v:q[1]=1-q[1]
        elif op=='vertical': v[0],v[2]=v[2],v[0]
        elif op=='horizontal': v[1],v[3]=v[3],v[1]
        else:raise ValueError(opid)
    elif g==16:
        if op=='cycle':
            for q in v:q[0]=(q[0]+1)%3
        elif op=='orbit':s['items']=[v[-1]]+v[:-1]
        elif op=='turn':
            for q in v:q[1]=(q[1]+1)%4
        elif op=='mirror':
            for q in v:q[1]=(-q[1])%4;q[2]=1-q[2]
        elif op=='select':
            for q in v:
                if q[0]==0:q[1]=(q[1]+2)%4
        elif op=='base':v[1],v[2]=v[2],v[1]
        else:raise ValueError(opid)
    elif g in (17,18):
        if g==17 and op=='orbit':s['items']=[v[-1]]+v[:-1]
        elif g==17 and op=='reverse':s['items']=[v[-i%6] for i in range(6)]
        elif g==17 and op=='opposite':v[0],v[3]=v[3],v[0]
        elif g==18 and op=='branches':s['items']=v[2:]+v[:2]
        elif g==18 and op=='siblings':s['items']=[v[1],v[0],v[3],v[2]]
        elif g==18 and op=='middle':v[1],v[2]=v[2],v[1]
        elif g==18 and op=='left':
            for q in v[:2]:q[0]=(q[0]+1)%3
        elif op=='shape':
            for q in v:q[0]=(q[0]+1)%3
        elif op=='fill':
            for q in v:q[1]=1-q[1]
        elif op=='black':
            for q in v:
                if q[1]:q[0]=(q[0]+1)%3
        else:raise ValueError(opid)
    elif g==19:
        if op=='reverse':s['items']=list(reversed(v))
        elif op=='outlines':
            sh=[q[0] for q in v]
            for i,q in enumerate(v):q[0]=sh[(i+1)%4]
        elif op=='marks':
            marks=[q[1] for q in v]
            for i,q in enumerate(v):q[1]=marks[(i-1)%4]
        elif op=='markcycle':
            for q in v:q[1]=(q[1]+1)%3
        elif op=='shapecycle':
            for q in v:q[0]=(q[0]+1)%4
        elif op=='middle':v[1][1],v[2][1]=v[2][1],v[1][1]
        else:raise ValueError(opid)
    elif g==20:
        l,r=map(set,v)
        if op=='xor':l=l^r
        elif op=='and':r=l&r
        elif op=='or':l=l|r
        elif op=='swap':l,r=r,l
        elif op=='half':
            lut={i:(i+4)%8 for i in range(8)}
            l={lut[x] for x in l};r={lut[x] for x in r}
        elif op=='complement':r=set(range(8))-r
        else:raise ValueError(opid)
        s['items']=[sorted(l),sorted(r)]
    return s


def independent_apply(scene,opid):
    """Pull visible values into output slots; letters use Cartesian matrices.

    This intentionally does not call apply or its transformation helpers.
    """
    g,op=_decode(opid)
    old=scene['items'];n=len(old)
    fresh=[list(q) for q in old]
    if g in (15,16,17,18,19):
        mapping=list(range(n))
        if op=='orbit':mapping=[(i+n-1)%n for i in range(n)]
        if (g==15 and op=='vertical') or (g==17 and op=='opposite'):
            j=2 if g==15 else 3;mapping[0],mapping[j]=mapping[j],mapping[0]
        if g==15 and op=='horizontal':mapping[1],mapping[3]=mapping[3],mapping[1]
        if g==16 and op=='base':mapping=[0,2,1]
        if g==17 and op=='reverse':mapping=[0,5,4,3,2,1]
        if g==18 and op=='branches':mapping=[2,3,0,1]
        if g==18 and op=='siblings':mapping=[1,0,3,2]
        if g==18 and op=='middle':mapping=[0,2,1,3]
        if g==19 and op=='reverse':mapping=[3,2,1,0]
        fresh=[list(old[j]) for j in mapping]
    if g==15:
        vectors=[(0,-1),(1,0),(0,1),(-1,0)]
        for q in fresh:
            x,y=vectors[q[0]]
            if op=='turn':x,y=-y,x
            if op=='black' and q[1]:x,y=-x,-y
            q[0]=vectors.index((x,y))
            if op=='fill':q[1]=int(not q[1])
    elif g==16:
        rots=[((1,0),(0,1)),((0,-1),(1,0)),((-1,0),(0,-1)),((0,1),(-1,0))]
        def matrix(r,m):
            a,b=rots[r][0];c,d=rots[r][1]
            return ((-a if m else a,b),(-c if m else c,d))
        def mult(a,b):return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))
        for q in fresh:
            if op=='cycle':q[0]={0:1,1:2,2:0}[q[0]]
            mat=matrix(q[1],q[2])
            if op=='turn':mat=mult(rots[1],mat)
            if op=='mirror':mat=mult(((-1,0),(0,1)),mat)
            if op=='select' and q[0]==0:mat=mult(rots[2],mat)
            q[1],q[2]=next((r,m) for r in range(4) for m in (0,1) if matrix(r,m)==mat)
    elif g in (17,18):
        next_shape={0:1,1:2,2:0}
        for i,q in enumerate(fresh):
            if op=='shape' or (op=='black' and q[1]) or (op=='left' and i in (0,1)):q[0]=next_shape[q[0]]
            if op=='fill':q[1]=int(not q[1])
    elif g==19:
        if op=='outlines':
            for i in range(4):fresh[(i-1)%4][0]=old[i][0]
        elif op=='marks':
            for i in range(4):fresh[(i+1)%4][1]=old[i][1]
        elif op=='markcycle':
            for q in fresh:q[1]={0:1,1:2,2:0}[q[1]]
        elif op=='shapecycle':
            for q in fresh:q[0]={0:1,1:2,2:3,3:0}[q[0]]
        elif op=='middle':fresh[1][1]=old[2][1];fresh[2][1]=old[1][1]
    elif g==20:
        bools=[[int(i in old[j]) for i in range(8)] for j in range(2)]
        out=[row[:] for row in bools]
        for i in range(8):
            a,b=bools[0][i],bools[1][i]
            if op=='xor':out[0][i]=int(a!=b)
            elif op=='and':out[1][i]=a*b
            elif op=='or':out[0][i]=max(a,b)
            elif op=='swap':out[0][i],out[1][i]=b,a
            elif op=='complement':out[1][i]=1-b
        if op=='half':
            # Visible segment coordinates after an upside-down turn.
            coords=[(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
            out=[[bools[j][coords.index((-x,-y))] for x,y in coords] for j in range(2)]
        fresh=[[i for i,b in enumerate(row) if b] for row in out]
    return {'kind':scene['kind'],'items':fresh}


def scene_key(scene):
    s=copy.deepcopy(scene)
    if s['kind']=='rays':s['items']=[sorted(set(q)) for q in s['items']]
    return json.dumps(s,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def _polygon(d, pts, fill, width=4):
    d.polygon(pts,fill='black' if fill else 'white')
    d.line(pts+[pts[0]],fill='black',width=width,joint='curve')


def _shape(d,xy,r,typ,fill,width=4):
    x,y=xy
    if typ==0:d.ellipse((x-r,y-r,x+r,y+r),fill='black' if fill else 'white',outline='black',width=width)
    elif typ==1:_polygon(d,[(x,y-r),(x+r,y+r),(x-r,y+r)],fill,width)
    elif typ==2:d.rectangle((x-r,y-r,x+r,y+r),fill='black' if fill else 'white',outline='black',width=width)


def render_panel(scene,size=280):
    # Render supersampled, then reduce; source and choices use identical scales.
    sc=3;im=Image.new('RGB',(280*sc,280*sc),'white');d=ImageDraw.Draw(im)
    def line(points,fill='black',width=2):d.line([(round(x*sc),round(y*sc)) for x,y in points],fill=fill,width=width*sc,joint='curve')
    def shape(xy,r,typ,fill,width=3):_shape(d,(xy[0]*sc,xy[1]*sc),r*sc,typ,fill,width*sc)
    def poly(pts,fill,width=3):_polygon(d,[(x*sc,y*sc) for x,y in pts],fill,width*sc)
    k=scene['kind'];v=scene['items']
    if k=='arrows':
        d.ellipse((51*sc,51*sc,229*sc,229*sc),outline='black',width=sc)
        positions=[(140,50),(230,140),(140,230),(50,140)]
        arrow=[(-7,23),(7,23),(7,0),(20,0),(0,-25),(-20,0),(-7,0)]
        for (x,y),(r,f) in zip(positions,v):
            pts=[]
            for a,b in arrow:
                for _ in range(r):a,b=-b,a
                pts.append((x+a,y+b))
            poly(pts,f,3)
    elif k=='letters':
        positions=[(140,63),(219,207),(61,207)]
        line([(140,63),(219,207),(61,207),(140,63)],width=1)
        # White backing removes fixed guide lines inside letter glyphs.
        paths={0:[[(-18,-24),(-18,24)],[(-18,-24),(18,-24)],[(-18,-2),(10,-2)]],
               1:[[(-18,24),(-18,-24),(17,-24),(21,-16),(21,-3),(14,3),(-18,3)]],
               2:[[(-18,24),(-18,-24),(17,-24),(21,-16),(21,-3),(14,3),(-18,3)],[(0,3),(23,24)]]}
        for (x,y),(typ,r,m) in zip(positions,v):
            d.rectangle(((x-33)*sc,(y-33)*sc,(x+33)*sc,(y+33)*sc),fill='white')
            for path in paths[typ]:
                pts=[]
                for a,b in path:
                    if m:a=-a
                    for _ in range(r):a,b=-b,a
                    pts.append((x+a,y+b))
                line(pts,width=5)
    elif k=='orbit':
        d.ellipse((48*sc,48*sc,232*sc,232*sc),outline='black',width=sc)
        positions=[(140+92*math.sin(i*math.pi/3),140-92*math.cos(i*math.pi/3)) for i in range(6)]
        for xy,(typ,f) in zip(positions,v):shape(xy,21,typ,f)
    elif k=='tree':
        line([(140,33),(140,65),(76,99),(76,131)],width=3)
        line([(140,65),(204,99),(204,131)],width=3)
        for branch,xs in [(76,(42,110)),(204,(170,238))]:
            for x in xs:line([(branch,131),(x,171),(x,195)],width=3)
        d.ellipse((133*sc,26*sc,147*sc,40*sc),fill='black')
        for x,(typ,f) in zip((42,110,170,238),v):shape((x,220),21,typ,f)
    elif k=='containers':
        for x,(typ,mark) in zip((36,105,174,243),v):
            r=28;y=140
            if typ==0:d.ellipse(((x-r)*sc,(y-r)*sc,(x+r)*sc,(y+r)*sc),outline='black',width=3*sc)
            elif typ==1:d.rectangle(((x-r)*sc,(y-r)*sc,(x+r)*sc,(y+r)*sc),outline='black',width=3*sc)
            elif typ==2:poly([(x,y-32),(x+30,y+25),(x-30,y+25)],False)
            elif typ==3:poly([(x+30*math.cos(a*math.pi/3),y+30*math.sin(a*math.pi/3)) for a in range(6)],False)
            if mark==0:d.ellipse(((x-5)*sc,(y-5)*sc,(x+5)*sc,(y+5)*sc),fill='black')
            elif mark==1:
                line([(x-7,y-7),(x+7,y+7)],width=3);line([(x-7,y+7),(x+7,y-7)],width=3)
            else:line([(x-10,y),(x+10,y)],width=4)
    elif k=='rays':
        for x,active in zip((72,208),v):
            for j in range(8):
                a=-math.pi/2+j*math.pi/4
                ux,uy=math.cos(a),math.sin(a)
                px,py=-uy,ux
                pts=[(x+radius*ux+side*px,140+radius*uy+side*py)
                     for radius,side in ((15,-4),(55,-4),(55,4),(15,4))]
                poly(pts,j in active,1)
    else:raise ValueError(k)
    return im.resize((size,size),Image.Resampling.LANCZOS)


CHAINS={
15:[['fill','black'],['orbit','vertical','turn'],['horizontal','orbit','black','fill']],
16:[['cycle','select'],['orbit','base','mirror'],['turn','select','cycle','mirror']],
17:[['fill','black'],['orbit','opposite','shape'],['reverse','orbit','black','fill']],
18:[['branches','left'],['siblings','middle','black'],['fill','left','branches','black']],
19:[['marks','middle'],['outlines','reverse','markcycle'],['shapecycle','outlines','marks','middle']],
20:[['xor','complement'],['swap','and','half'],['complement','or','swap','xor']],
}


def _source(rng,g):
    if g==15:
        fills=[0,0,1,1];rng.shuffle(fills)
        return {'kind':KINDS[g],'items':[[rng.randrange(4),f] for f in fills]}
    if g==16:
        typ=list(range(3));rng.shuffle(typ)
        return {'kind':KINDS[g],'items':[[t,rng.randrange(4),rng.randrange(2)] for t in typ]}
    if g==17:
        vals=[[t,f] for t in range(3) for f in range(2)];rng.shuffle(vals)
        return {'kind':KINDS[g],'items':vals}
    if g==18:
        shapes=[0,1,2,rng.randrange(3)];rng.shuffle(shapes)
        fills=[0,0,1,1];rng.shuffle(fills)
        return {'kind':KINDS[g],'items':[[t,f] for t,f in zip(shapes,fills)]}
    if g==19:
        typ=list(range(4));rng.shuffle(typ)
        marks=[0,1,2,rng.randrange(3)];rng.shuffle(marks)
        return {'kind':KINDS[g],'items':[[t,m] for t,m in zip(typ,marks)]}
    if g==20:
        return {'kind':KINDS[g],'items':[sorted(rng.sample(range(8),rng.randrange(3,7))) for _ in range(2)]}


def _run(s,chain,fn=apply):
    for op in chain:s=fn(s,op)
    return s


def _acceptable(s,chain,g):
    seen={scene_key(s)};cur=s
    for op in chain:
        nex=apply(cur,op)
        if scene_key(nex) in seen:return False
        if scene_key(nex)!=scene_key(independent_apply(cur,op)):raise AssertionError(op)
        if g==20 and any(not 1<=len(q)<=7 for q in nex['items']):return False
        seen.add(scene_key(nex));cur=nex
    target=scene_key(cur)
    if any(scene_key(_run(s,chain[:j]+chain[j+1:]))==target for j in range(len(chain))):return False
    # Actual noncommuting pair present somewhere in the chain.
    if not any(scene_key(_run(s,[a,b]))!=scene_key(_run(s,[b,a])) for a,b in zip(chain,chain[1:])):return False
    # More than 3 plausible, visibly different one-step substitutions exist.
    wrong=set()
    for j in range(len(chain)):
        for op,_,_ in RULES[g]:
            alt=chain[:j]+[_rule_id(g,op)]+chain[j+1:]
            key=scene_key(_run(s,alt))
            if key!=target:wrong.add(key)
    return len(wrong)>=5


def get_groups():
    out=[]
    for g in range(15,21):
        rng=random.Random(9017+g*317)
        qs=[]
        for names in CHAINS[g]:
            chain=[_rule_id(g,n) for n in names]
            for _ in range(20000):
                s=_source(rng,g)
                if _acceptable(s,chain,g):break
            else:raise RuntimeError(('no source',g,chain))
            qs.append({'source':s,'chain':chain})
        out.append({'id':g,'title':TITLES[g],'intro':INTROS[g],
                    'rules':[{'id':_rule_id(g,n),'code':c,'text':t} for n,c,t in RULES[g]],'questions':qs})
    return out


def self_check(output_dir=None):
    groups=get_groups();checks=[]
    for group in groups:
        covered=set()
        for qi,q in enumerate(group['questions'],1):
            s=q['source'];chain=q['chain'];covered.update(chain)
            assert _acceptable(s,chain,group['id'])
            a=s;b=s
            image_hashes=[]
            for op in chain:
                before=copy.deepcopy(a)
                a=apply(a,op);b=independent_apply(b,op)
                assert scene_key(a)==scene_key(b)
                assert before!=a
                image_hashes.append(hashlib.sha256(render_panel(a).tobytes()).hexdigest())
            target=scene_key(a)
            assert len(set(image_hashes))==len(chain)
            # Every alternative is checked by both implementations.
            wrong=[]
            for j in range(len(chain)):
                for rule in group['rules']:
                    alt=chain[:j]+[rule['id']]+chain[j+1:]
                    x=_run(s,alt);y=_run(s,alt,independent_apply)
                    assert scene_key(x)==scene_key(y)
                    if scene_key(x)!=target:wrong.append(x)
            assert len({scene_key(x) for x in wrong})>=5
            rendered={}
            for x in [s,a]+wrong:
                key=scene_key(x);h=hashlib.sha256(render_panel(x).tobytes()).hexdigest()
                assert h not in rendered or rendered[h]==key,('visual collision',group['id'],qi)
                rendered[h]=key
            checks.append({'group':group['id'],'question':qi,'length':len(chain),'every_step_effective':True,'every_deletion_changes_answer':True,'independent_path_equal':True,'wrong_distinct':len({scene_key(x) for x in wrong}),'render_collision':False})
        assert covered=={r['id'] for r in group['rules']}
    report={'groups':6,'questions':18,'all_passed':True,'checks':checks,
            'carrier_families':TITLES,'scope':'精确离散场景与八射线逐位集合/矩阵复算；不代替Word实际排版和外部盲解。'}
    if output_dir:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
        (p/'tokens_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        # Review contact sheet shows source and each intermediate for all items.
        canvas=Image.new('RGB',(1400,18*300),'white');dr=ImageDraw.Draw(canvas)
        row=0
        for gr in groups:
            for qi,q in enumerate(gr['questions'],1):
                scenes=[q['source']];cur=q['source']
                for op in q['chain']:cur=apply(cur,op);scenes.append(cur)
                for col,x in enumerate(scenes):canvas.paste(render_panel(x,260),(col*280+10,row*300+25))
                dr.text((5,row*300+5),f"Group {gr['id']}, item {qi}",fill='black')
                row+=1
        canvas.save(p/'tokens_contact.png')
    return report


if __name__=='__main__':
    r=self_check(Path(__file__).parent)
    print(json.dumps({'groups':r['groups'],'questions':r['questions'],'all_passed':r['all_passed']},ensure_ascii=False))
