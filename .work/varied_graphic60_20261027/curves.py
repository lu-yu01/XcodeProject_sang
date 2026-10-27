"""Seven black-and-white curve operation families; deterministic data and dual solvers."""
from copy import deepcopy
import hashlib
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageFont


def _roll(a, n):
    n %= len(a)
    return a[-n:] + a[:-n] if n else list(a)


def _rid(g, j):
    return f'C{g}_{j}'


def apply(scene, opid):
    s = deepcopy(scene)
    g, j = (int(v) for v in opid[1:].split('_'))
    assert g == s['kind']
    if g == 8:
        a, b = s['outer'], s['inner']
        if j == 1: s['outer'] = _roll(a, 1)
        elif j == 2: s['inner'] = _roll(b, -1)
        elif j == 3: s['outer'], s['inner'] = b, a
        elif j == 4: s['inner'] = [x ^ y for x, y in zip(a, b)]
        elif j == 5: s['outer'] = [1-x for x in a]
        elif j == 6: s['inner'] = [b[(-k) % 8] for k in range(8)]
    elif g == 9:
        a, b = s['long'], s['black']
        if j == 1: s['black'] = _roll(b, 1)
        elif j == 2: s['long'] = _roll(a, -1)
        elif j == 3: s['long'] = [1-x for x in a]
        elif j == 4: s['black'] = [x ^ y for x, y in zip(b, a)]
        elif j == 5: s['long'], s['black'] = b, a
        elif j == 6:
            s['long'] = [a[k ^ 1] for k in range(6)]
            s['black'] = [b[k ^ 1] for k in range(6)]
    elif g == 10:
        a = list(s['regions'])
        if j in (1, 2):
            order = [1, 2, 4] if j == 1 else [6, 5, 3]
            for k in range(3): s['regions'][order[(k+1)%3]-1] = a[order[k]-1]
        elif j == 3:
            for k in (1, 2, 4): s['regions'][k-1], s['regions'][6-k] = a[6-k], a[k-1]
        elif j == 4: s['regions'][6] ^= 1
        elif j == 5:
            for k in (3, 5, 6): s['regions'][k-1] ^= 1
        elif j == 6:
            # Exchange membership bits of the two upper circles.
            for k in range(1, 8):
                dest = ((k & 1) << 1) | ((k & 2) >> 1) | (k & 4)
                s['regions'][dest-1] = a[k-1]
    elif g == 11:
        a, b = s['upper'], s['lower']
        if j == 1: s['upper'], s['lower'] = b, a
        elif j == 2: s['upper'] = _roll(a, 1)
        elif j == 3: s['lower'] = _roll(b, -1)
        elif j == 4: s['lower'] = [x ^ y for x, y in zip(a, b)]
        elif j == 5: s['upper'] = a[::-1]
        elif j == 6:
            s['upper'] = [a[k ^ 1] for k in range(6)]
            s['lower'] = [b[k ^ 1] for k in range(6)]
    elif g == 12:
        a, b = s['gaps'], s['dots']
        if j == 1: s['gaps'] = [(x+1)%4 for x in a]
        elif j == 2: s['dots'] = [(x-1)%4 for x in b]
        elif j == 3: s['gaps'][0], s['gaps'][2] = a[2], a[0]
        elif j == 4: s['dots'] = _roll(b, 1)
        elif j == 5:
            s['gaps'] = [(-x)%4 for x in a]
            s['dots'] = [(3-x)%4 for x in b]
        elif j == 6: s['gaps'] = _roll(a, 1)
    elif g == 13:
        a, b = s['tips'], s['black']
        if j == 1: s['tips'] = [(x+1)%4 for x in a]
        elif j in (2, 3):
            perm = [1,0,3,2] if j == 2 else [2,3,0,1]
            s['tips'] = [a[k] for k in perm]
            s['black'] = [b[k] for k in perm]
        elif j == 4: s['tips'] = [(x-y)%4 for x,y in zip(a,b)]
        elif j == 5: s['black'] = [y ^ (x == 0) for x,y in zip(a,b)]
        elif j == 6:
            s['tips'] = a[::-1]
            s['black'] = b[::-1]
    elif g == 14:
        a, b = s['up'], s['solid']
        if j == 1: s['up'] = _roll(a, 1)
        elif j == 2: s['solid'] = _roll(b, -1)
        elif j == 3:
            s['up'] = [a[k ^ 1] for k in range(6)]
            s['solid'] = [b[k ^ 1] for k in range(6)]
        elif j == 4: s['up'] = [x ^ (1-y) for x,y in zip(a,b)]
        elif j == 5: s['solid'] = [x ^ y for x,y in zip(b,a)]
        elif j == 6: s['up'], s['solid'] = b, a
    else: raise ValueError(g)
    return s


def independent_apply(scene, opid):
    """Separate destination-index / bit-mask implementation; never calls apply."""
    g, j = map(int, opid[1:].split('_'))
    assert scene['kind'] == g
    out = {'kind': g}
    arrays = {k:tuple(v) for k,v in scene.items() if k != 'kind'}
    out.update({k:list(v) for k,v in arrays.items()})
    def map_src(field, indices): out[field] = [arrays[field][i] for i in indices]
    def turn(field, delta, mod): out[field] = [(v+delta) % mod for v in arrays[field]]
    def swap_fields(a,b): out[a],out[b] = list(arrays[b]),list(arrays[a])
    def xor_field(dest, other):
        # Work on packed integer masks, independently of the list-wise solver.
        x = sum(v << i for i,v in enumerate(arrays[dest]))
        y = sum(v << i for i,v in enumerate(arrays[other]))
        out[dest] = [((x ^ y) >> i) & 1 for i in range(len(arrays[dest]))]
    if g == 8:
        if j == 1: map_src('outer', [7,0,1,2,3,4,5,6])
        elif j == 2: map_src('inner', [1,2,3,4,5,6,7,0])
        elif j == 3: swap_fields('outer','inner')
        elif j == 4: xor_field('inner','outer')
        elif j == 5: out['outer'] = [int(not v) for v in arrays['outer']]
        elif j == 6: map_src('inner', [0,7,6,5,4,3,2,1])
    elif g == 9:
        if j == 1: map_src('black', [5,0,1,2,3,4])
        elif j == 2: map_src('long', [1,2,3,4,5,0])
        elif j == 3: out['long'] = [int(not v) for v in arrays['long']]
        elif j == 4: xor_field('black','long')
        elif j == 5: swap_fields('long','black')
        elif j == 6:
            for f in ('long','black'): map_src(f,[1,0,3,2,5,4])
    elif g == 10:
        a=arrays['regions']
        if j == 1:
            for dest, src in ((2,1),(4,2),(1,4)): out['regions'][dest-1]=a[src-1]
        elif j == 2:
            for dest,src in ((5,6),(3,5),(6,3)): out['regions'][dest-1]=a[src-1]
        elif j == 3: out['regions'] = [a[5],a[4],a[3],a[2],a[1],a[0],a[6]]
        elif j == 4: out['regions'][6]=int(not a[6])
        elif j == 5:
            mask=sum(v<<i for i,v in enumerate(a)) ^ ((1<<2)|(1<<4)|(1<<5))
            out['regions']=[(mask>>i)&1 for i in range(7)]
        elif j == 6: map_src('regions',[1,0,2,3,5,4,6])
    elif g == 11:
        if j == 1: swap_fields('upper','lower')
        elif j == 2: map_src('upper',[5,0,1,2,3,4])
        elif j == 3: map_src('lower',[1,2,3,4,5,0])
        elif j == 4: xor_field('lower','upper')
        elif j == 5: map_src('upper',[5,4,3,2,1,0])
        elif j == 6:
            for f in ('upper','lower'):map_src(f,[1,0,3,2,5,4])
    elif g == 12:
        if j == 1: turn('gaps',1,4)
        elif j == 2: turn('dots',3,4)
        elif j == 3: map_src('gaps',[2,1,0])
        elif j == 4: map_src('dots',[2,0,1])
        elif j == 5:
            out['gaps']=[[0,3,2,1][v] for v in arrays['gaps']]
            out['dots']=[[3,2,1,0][v] for v in arrays['dots']]
        elif j == 6: map_src('gaps',[2,0,1])
    elif g == 13:
        if j == 1: turn('tips',1,4)
        elif j in (2,3,6):
            p={2:[1,0,3,2],3:[2,3,0,1],6:[3,2,1,0]}[j]
            for f in ('tips','black'):map_src(f,p)
        elif j == 4:
            out['tips']=[({0:3,1:0,2:1,3:2}[v] if arrays['black'][i] else v) for i,v in enumerate(arrays['tips'])]
        elif j == 5:
            out['black']=[int(not v) if arrays['tips'][i]==0 else v for i,v in enumerate(arrays['black'])]
    elif g == 14:
        if j == 1: map_src('up',[5,0,1,2,3,4])
        elif j == 2: map_src('solid',[1,2,3,4,5,0])
        elif j == 3:
            for f in ('up','solid'):map_src(f,[1,0,3,2,5,4])
        elif j == 4: out['up']=[int(not v) if arrays['solid'][i]==0 else v for i,v in enumerate(arrays['up'])]
        elif j == 5: xor_field('solid','up')
        elif j == 6: swap_fields('up','solid')
    return out


def scene_key(scene):
    return json.dumps(scene,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def _font(n=20):
    return ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',n)


def _annular(draw, center, r0, r1, start, end, fill):
    pts=[]
    for r, angs in ((r1,range(start,end+1,2)),(r0,range(end,start-1,-2))):
        pts.extend((center[0]+r*math.sin(math.radians(a)),center[1]-r*math.cos(math.radians(a))) for a in angs)
    draw.polygon(pts, fill=fill,outline='black',width=2)


def _teardrop(draw,cx,cy,length,width,angle,fill):
    # Two smooth cubic Beziers, with one unmistakably pointed end.
    def bez(p0,p1,p2,p3,t):
        u=1-t
        return (u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1])
    tip=(0,-length/2); bottom=(0,length/2)
    base=[bez(tip,(-width*.7,-length*.05),(-width*.7,length*.45),bottom,k/28) for k in range(29)]
    base += [bez(bottom,(width*.7,length*.45),(width*.7,-length*.05),tip,k/28) for k in range(1,29)]
    c,s=math.cos(angle),math.sin(angle)
    pts=[(cx+x*c-y*s,cy+x*s+y*c) for x,y in base]
    draw.polygon(pts,fill=fill,outline='black',width=3)


def render_panel(scene,size=280):
    # All coordinates below are in a 280px square, with print-safe stroke widths.
    g=scene['kind']; im=Image.new('RGB',(280,280),'white'); d=ImageDraw.Draw(im)
    if g == 8:
        for f,r0,r1 in (('outer',84,121),('inner',38,75)):
            for k,v in enumerate(scene[f]):_annular(d,(140,140),r0,r1,k*45-22,k*45+22,'black' if v else 'white')
        d.line((140,10,140,16),fill='black',width=4)
    elif g == 9:
        for k,(long,black) in enumerate(zip(scene['long'],scene['black'])):
            a=k*math.pi/3; length=65 if long else 43; rad=47+length/2
            _teardrop(d,140+rad*math.sin(a),140-rad*math.cos(a),length,35,a,'black' if black else 'white')
        d.ellipse((130,130,150,150),outline='black',width=3)
    elif g == 10:
        masks=[]; boxes=[(31,33,177,179),(103,33,249,179),(67,96,213,242)]
        for box in boxes:
            m=Image.new('L',(280,280));ImageDraw.Draw(m).ellipse(box,fill=255);masks.append(m)
        canvas=Image.new('L',(280,280),0)
        for k,v in enumerate(scene['regions'],1):
            if not v: continue
            m=Image.new('L',(280,280),255)
            for b,c in enumerate(masks):m=ImageChops.multiply(m,c if k&(1<<b) else ImageChops.invert(c))
            canvas=ImageChops.lighter(canvas,m)
        im.paste((0,0,0),(0,0,280,280),canvas)
        for box in boxes:d.ellipse(box,outline='black',width=3)
        for txt,xy in [('①',(20,20)),('②',(239,20)),('③',(130,246))]:d.text(xy,txt,font=_font(21),fill='black')
    elif g == 11:
        for row,field in enumerate(('upper','lower')):
            y0=83+row*112
            pts=[(25+i*2.3,y0+17*math.sin(i*math.pi/20)) for i in range(101)]
            d.line(pts,fill='black',width=4)
            for k,v in enumerate(scene[field]):
                x=25+46*k;y=y0+17*math.sin(k*math.pi)
                d.ellipse((x-10,y-10,x+10,y+10),fill='black' if v else 'white',outline='black',width=3)
    elif g == 12:
        for r,gap,dot in zip((115,78,41),scene['gaps'],scene['dots']):
            d.rounded_rectangle((140-r,140-r,140+r,140+r),radius=15,outline='black',width=4)
            cuts=[(127,136-r,153,145-r),(135+r,127,145+r,153),(127,135+r,153,145+r),(135-r,127,145-r,153)]
            d.rectangle(cuts[gap],fill='white')
            pts=[(140+r-5,140-r+5),(140+r-5,140+r-5),(140-r+5,140+r-5),(140-r+5,140-r+5)]
            x,y=pts[dot];d.ellipse((x-8,y-8,x+8,y+8),fill='black')
    elif g == 13:
        for k,(tip,black) in enumerate(zip(scene['tips'],scene['black'])):
            x=75+130*(k%2);y=75+130*(k//2)
            _teardrop(d,x,y,88,68,tip*math.pi/2,'black' if black else 'white')
    elif g == 14:
        for k,(up,solid) in enumerate(zip(scene['up'],scene['solid'])):
            pts=[]
            for j in range(31):
                t=j/30;pts.append((20+(k+t)*40,140+(1-2*up)*47*4*t*(1-t)))
            if solid:d.line(pts,fill='black',width=4)
            else:
                for a in (0,8,16,24):d.line(pts[a:min(a+5,30)+1],fill='black',width=4)
        for k in range(7):
            x=20+k*40;d.ellipse((x-4,136,x+4,144),fill='black')
        d.ellipse((10,130,30,150),outline='black',width=3)
        d.rectangle((251,131,269,149),outline='black',width=3)
    if size != 280:im=im.resize((size,size),Image.Resampling.LANCZOS)
    return im


SPEC={
8:('双环弧的层间变换','两环均分为8个槽。上方短线为固定参照；“一格”为45°。规则仅改变所指环，另一环保持不变。',[
('↻外','外环黑白状态顺时针移一格。'),('↶内','内环黑白状态逆时针移一格。'),('C8甲','内、外环同方位槽的黑白状态互换。'),('C8乙','内环同方位异色变黑、同色变白；外环不变。'),('C8丙','仅外环各槽黑白互换。'),('C8丁','仅内环以竖直直径为轴左右翻转。')]),
9:('长短花瓣的属性联动','六瓣花从正上方起顺时针编号1—6；编号仅用于说明。每瓣有长短、黑白两属性，中心小圆保持不变。',[
('C9甲','仅黑白属性顺时针移一瓣，长短位置不变。'),('C9乙','仅长短属性逆时针移一瓣，黑白位置不变。'),('C9丙','每瓣长短互换，黑白不变。'),('C9丁','仅长瓣黑白互换，短瓣不变。'),('C9戊','各瓣属性互换：长黑、短白不变；长白↔短黑。'),('C9己','1、2瓣互换，3、4瓣互换，5、6瓣互换。')]),
10:('三圆交叠区域重配','圆①在左上、②在右上、③在下。单独区仅属于该圆；双叠区恰属于两圆；中央三叠区单列，圆框和标号固定。',[
('C10甲','三个单独区黑白状态按①→②→③→①轮换。'),('C10乙','双叠区状态按②③→①③→①②→②③轮换。'),('C10丙','每个单独区与不含该圆的双叠区交换状态。'),('C10丁','仅中央三叠区黑白互换。'),('C10戊','仅三个双叠区黑白互换。'),('C10己','所有区域中圆①、②的归属对调，圆框固定。')]),
11:('波线双轨的珠点迁移','上下两条波线各有6颗珠，从左向右编号1—6。轨道形状固定；循环移动越过末端即回到另一端。',[
('C11甲','上下轨对应珠的黑白状态互换。'),('C11乙','仅上轨黑白状态向右循环移一珠。'),('C11丙','仅下轨黑白状态向左循环移一珠。'),('C11丁','下轨对应珠异色变黑、同色变白；上轨不变。'),('C11戊','仅上轨六珠的黑白次序左右倒置。'),('C11己','两轨均将1、2珠，3、4珠，5、6珠分别互换。')]),
12:('嵌套开口与角点的双系统','三个圆角方框从外至内为外、中、内层，每层有一侧开口及一枚角点。框的大小固定；属性轮换不改变框。',[
('C12甲','每层开口沿上→右→下→左移动一侧。'),('C12乙','每层黑角点沿逆时针方向移动一个角。'),('C12丙','仅交换外、内层的开口方向，中层不变。'),('C12丁','黑角点位置属性按外→中→内→外轮换。'),('⇆','三层开口和黑角点同时左右翻转。'),('C12戊','开口方向属性按外→中→内→外轮换。')]),
13:('四枚水滴的方向与颜色','四枚水滴按左上、右上、左下、右下排列。交换水滴时连同方向和黑白一起移动，不做镜像。',[
('↻滴','四枚水滴各自顺时针转90°，位置不变。'),('C13甲','左上↔右上、左下↔右下，水滴方向不变。'),('C13乙','左上↔左下、右上↔右下，水滴方向不变。'),('C13丙','仅黑水滴各自逆时针转90°，位置不变。'),('C13丁','仅尖端朝上的水滴黑白互换。'),('C13戊','左上↔右下、右上↔左下，水滴方向不变。')]),
14:('弯带的曲向与线型耦合','圆端至方端共有6段弯带，从左至右编号1—6。节点和两端标记固定；上弯、下弯以页面方向为准。',[
('C14甲','仅上、下弯属性向右循环移动一段。'),('C14乙','仅虚、实线属性向左循环移动一段。'),('C14丙','1、2段，3、4段，5、6段分别整体互换。'),('C14丁','仅虚线段的上、下弯互换。'),('C14戊','仅上弯段的虚、实线互换。'),('C14己','逐段改换：上弯虚线↔下弯实线，其余不变。')]),
}

# Codes are local to each shared rule table; short glyphs remain legible in four-step chains.
SHORT_CODES={
8:['↻','↶','S','⊕','N','⇆'],
9:['P','Q','N','X','S','J'],
10:['A','B','S','T','N','⇆'],
11:['S','R','L','⊕','⇆','J'],
12:['↻','↶','S','P','⇆','Q'],
13:['↻','H','V','↶','N','D'],
14:['P','Q','J','U','N','S'],
}


def _source(g,rng):
    def bits(n):return [rng.randrange(2) for _ in range(n)]
    s={'kind':g}
    if g==8:s.update(outer=bits(8),inner=bits(8))
    elif g==9:s.update(long=bits(6),black=bits(6))
    elif g==10:s.update(regions=bits(7))
    elif g==11:s.update(upper=bits(6),lower=bits(6))
    elif g==12:s.update(gaps=[rng.randrange(4) for _ in range(3)],dots=[rng.randrange(4) for _ in range(3)])
    elif g==13:s.update(tips=[rng.randrange(4) for _ in range(4)],black=bits(4))
    elif g==14:s.update(up=bits(6),solid=bits(6))
    return s


def _run(s,chain,solver=apply):
    for op in chain:s=solver(s,op)
    return s


def _valid(s,chain):
    start=scene_key(s);cur=s
    for op in chain:
        new=apply(cur,op)
        if scene_key(new)==scene_key(cur):return False
        if scene_key(new)!=scene_key(independent_apply(cur,op)):raise AssertionError((cur,op))
        cur=new
    key=scene_key(cur)
    if key==start:return False
    if any(scene_key(_run(s,chain[:i]+chain[i+1:]))==key for i in range(len(chain))):return False
    return True


def get_groups():
    result=[]
    # All six operations are covered; chain lengths are 2,3,4 rather than uniform.
    chains=[[1,2],[3,4,5],[6,2,4,1]]
    for g,(title,intro,ruledata) in SPEC.items():
        rng=random.Random(2026102700+g)
        rules=[{'id':_rid(g,j),'code':SHORT_CODES[g][j-1],'text':text} for j,(_,text) in enumerate(ruledata,1)]
        questions=[]
        selected_chains = deepcopy(chains)
        if g == 12: selected_chains[2] = [6,2,5,1]
        for ids in selected_chains:
            chain=[_rid(g,j) for j in ids]
            for attempt in range(20000):
                s=_source(g,rng)
                if _valid(s,chain):
                    finals={scene_key(_run(s,chain))}
                    for i in range(len(chain)):
                        for rule in rules:
                            alt=chain[:];alt[i]=rule['id'];finals.add(scene_key(_run(s,alt)))
                    if len(finals)>=8:break
            else:raise RuntimeError(('No valid question',g,ids))
            questions.append({'source':s,'chain':chain})
        # Root integration check: keep the other two sources stable while
        # rejecting an accidental source-specific single-rule shortcut.
        for q in questions:
            target=scene_key(_run(q['source'],q['chain']))
            if any(scene_key(apply(q['source'],r['id']))==target for r in rules):
                for attempt in range(20000):
                    s=_source(g,rng)
                    if not _valid(s,q['chain']):continue
                    target=scene_key(_run(s,q['chain']))
                    if any(scene_key(apply(s,r['id']))==target for r in rules):continue
                    if any(scene_key(s)==scene_key(other['source']) for other in questions):continue
                    q['source']=s;break
                else:raise RuntimeError(('single-rule shortcut',g))
        result.append({'id':g,'title':title,'intro':intro,'rules':rules,'questions':questions})
    return result


def self_check():
    groups=get_groups(); report={'groups':7,'questions':21,'operator_checks':0,'render_checks':0,'details':[]}
    for group in groups:
        seen=set(); g=group['id']; rng=random.Random(6080+g)
        # Broad equivalence test, beyond the selected question states.
        for _ in range(200):
            s=_source(g,rng)
            for rule in group['rules']:
                assert scene_key(apply(s,rule['id']))==scene_key(independent_apply(s,rule['id'])),(g,rule,s)
                report['operator_checks']+=1
        info={'id':g,'title':group['title'],'chains':[],'unique_candidate_results':[],'noncommuting_questions':[]}
        for q in group['questions']:
            assert _valid(q['source'],q['chain'])
            seen.update(q['chain']); info['chains'].append(q['chain'])
            correct=scene_key(_run(q['source'],q['chain']))
            swaps=[]
            for i in range(len(q['chain'])-1):
                alt=q['chain'][:];alt[i],alt[i+1]=alt[i+1],alt[i]
                if scene_key(_run(q['source'],alt)) != correct:swaps.append(i)
            info['noncommuting_questions'].append(bool(swaps))
            outcomes={}
            for i in range(len(q['chain'])):
                for rule in group['rules']:
                    alt=q['chain'][:];alt[i]=rule['id']
                    state=_run(q['source'],alt)
                    k=scene_key(state);png=hashlib.sha256(render_panel(state).tobytes()).hexdigest()
                    assert png not in outcomes or outcomes[png]==k,(g,'render collision')
                    outcomes[png]=k; report['render_checks']+=1
            info['unique_candidate_results'].append(len(outcomes))
        assert seen=={r['id'] for r in group['rules']}
        assert any(info['noncommuting_questions']),(g,'No noncommuting chain')
        report['details'].append(info)
    return report


if __name__=='__main__':
    folder=Path(__file__).resolve().parent
    report=self_check()
    (folder/'curves_self_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
