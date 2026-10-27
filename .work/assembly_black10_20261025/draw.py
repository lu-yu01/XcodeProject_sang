"""Pure white/black solids, target plus two given pieces and one missing piece."""
from pathlib import Path
from itertools import permutations,product
from functools import lru_cache
import math,json
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets';ASSETS.mkdir(exist_ok=True)
FONT='C:/Windows/Fonts/msyh.ttc';INK='#111111';LAYOUTS={}

def text(d,xy,value,size=34,fill=INK,anchor='mm'):
    d.text(xy,str(value),font=ImageFont.truetype(FONT,size),fill=fill,anchor=anchor)

def norm(s):
    cells=list(map(tuple,s['cells']));black=list(map(tuple,s['black']))
    low=[min(p[a] for p in cells) for a in range(3)]
    move=lambda p:tuple(p[a]-low[a] for a in range(3))
    return {'cells':tuple(sorted(map(move,cells))),'black':tuple(sorted(map(move,black)))}

def rotations(s,keep_z=False):
    seen=set()
    for perm in permutations(range(3)):
        parity=(-1)**sum(perm[a]>perm[b] for a in range(3) for b in range(a+1,3))
        for sign in product((-1,1),repeat=3):
            if parity*math.prod(sign)!=1:continue
            if keep_z and (perm[2]!=2 or sign[2]!=1):continue
            tr=lambda p:tuple(sign[a]*p[perm[a]] for a in range(3))
            result=norm({'cells':[tr(p) for p in s['cells']],'black':[tr(p) for p in s['black']]})
            key=(result['cells'],result['black'])
            if key not in seen:seen.add(key);yield result

def hits(origin,direction,cell):
    lo,hi=.00001,1e9
    for a in range(3):
        aa=(cell[a]-origin[a])/direction[a];bb=(cell[a]+1-origin[a])/direction[a]
        lo=max(lo,min(aa,bb));hi=min(hi,max(aa,bb))
    return hi>lo+1e-8

@lru_cache(maxsize=4096)
def visibility(cells,direction=(1,1,1)):
    occupied=set(cells);scores={}
    for p in cells:
        score=0
        for axis in range(3):
            sign=direction[axis]
            neighbor=tuple(p[a]+(sign if a==axis else 0) for a in range(3))
            if neighbor in occupied:continue
            otheraxes=[a for a in range(3) if a!=axis]
            for u,v in product((.2,.5,.8),repeat=2):
                origin=[p[a]+.5 for a in range(3)];origin[axis]=p[axis]+(1 if sign>0 else 0)
                origin[otheraxes[0]]=p[otheraxes[0]]+u;origin[otheraxes[1]]=p[otheraxes[1]]+v
                if not any(hits(origin,direction,other) for other in cells if other!=p):score+=1
        scores[p]=score
    return scores

def choose_pose(shape,target=False):
    best=None
    for s in rotations(shape,keep_z=target):
        score1=visibility(s['cells'])
        score2=visibility(s['cells'],(-1,-1,1)) if target else None
        scores={p:max(score1[p],score2[p]) if target else score1[p] for p in s['cells']}
        black_scores=[scores[p] for p in s['black']]
        hidden=sum(v==0 for v in scores.values())
        dx,dy,dz=[max(p[a] for p in s['cells'])+1 for a in range(3)]
        score=(sum(v==0 for v in black_scores),hidden,-min(black_scores),-sum(black_scores),dx+dy+dz,dz)
        if best is None or score<best[0]:best=(score,s,scores)
    assert best[0][0]==0,('unreadable black cube',shape)
    return best[1],{'hidden_cells':[p for p,v in best[2].items() if not v],
                    'black_visibility_samples':[best[2][p] for p in best[1]['black']]}

def project(p):
    x,y,z=p
    return ((x-y)*math.sqrt(3)/2,(x+y)/2-z)

def projected_size(s):
    points=[project((x+a,y+b,z+c)) for x,y,z in s['cells'] for a,b,c in product((0,1),repeat=3)]
    return max(p[0] for p in points)-min(p[0] for p in points),max(p[1] for p in points)-min(p[1] for p in points)

def back(s):return norm({'cells':[(-x,-y,z) for x,y,z in s['cells']],'black':[(-x,-y,z) for x,y,z in s['black']]})

def solid(d,s,box,scale):
    cells=set(s['cells']);black=set(s['black']);faces=[]
    spec=[((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),
          ((0,1,0),[(0,1,0),(0,1,1),(1,1,1),(1,1,0)]),
          ((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)])]
    allpoints=[]
    for p in cells:
        for direction,vertices in spec:
            if tuple(p[a]+direction[a] for a in range(3)) in cells:continue
            verts=[tuple(p[a]+v[a] for a in range(3)) for v in vertices]
            poly=[project(v) for v in verts];allpoints.extend(poly)
            faces.append((sum(sum(v) for v in verts)/4,poly,p in black))
    minx,maxx=min(p[0] for p in allpoints),max(p[0] for p in allpoints)
    miny,maxy=min(p[1] for p in allpoints),max(p[1] for p in allpoints)
    x0,y0,x1,y1=box;cx,cy=(x0+x1)/2,(y0+y1)/2
    tr=lambda p:(round(cx+(p[0]-(minx+maxx)/2)*scale),round(cy+(p[1]-(miny+maxy)/2)*scale))
    bounds=[]
    for _,poly,isblack in sorted(faces,key=lambda f:f[0]):
        polygon=[tr(p) for p in poly];bounds.extend(polygon)
        d.polygon(polygon,fill=INK if isblack else 'white')
        d.line(polygon+[polygon[0]],fill='#bcbcbc' if isblack else INK,width=3,joint='curve')
    assert all(x0<=x<=x1 and y0<=y<=y1 for x,y in bounds),box

def question(q):
    im=Image.new('RGB',(1800,950),'white');d=ImageDraw.Draw(im)
    target,tmeta=choose_pose(q['target'],True)
    pieces=[];pm=[]
    for p in q['pieces']:
        a,b=choose_pose(p);pieces.append(a);pm.append(b)
    opts=[];om=[]
    for p in q['options']:
        a,b=choose_pose(p);opts.append(a);om.append(b)
    target_box=(20,15,790,495);given_boxes=[(810,15,1285,495),(1305,15,1780,495)]
    option_boxes=[(20+i*445,535,445+i*445,935) for i in range(4)]
    viewboxes=[(35,85,390,427),(410,85,775,427),(825,85,1270,445),(1320,85,1765,445)]
    viewboxes += [(x0+15,y0+60,x1-15,y1-55) for x0,y0,x1,y1 in option_boxes]
    viewshapes=[target,back(target)]+pieces+opts
    scale=min(95,*[min((b[2]-b[0]-22)/projected_size(s)[0],(b[3]-b[1]-22)/projected_size(s)[1]) for s,b in zip(viewshapes,viewboxes)])
    for box in [target_box]+given_boxes+option_boxes:d.rectangle(box,outline=INK,width=3)
    for i,box in enumerate(given_boxes):
        text(d,((box[0]+box[2])/2,47),'①②'[i],33)
    for i,box in enumerate(option_boxes):text(d,((box[0]+box[2])/2,box[1]+32),'ABCD'[i],38)
    for s,b in zip(viewshapes,viewboxes):solid(d,s,b,scale)
    path=ASSETS/f'q{q["n"]:02}.png';im.save(path,dpi=(300,300))
    LAYOUTS[q['n']]={'image_size':im.size,'unit_scale':scale,'format':'target two views + exactly two given pieces; A-D in one horizontal row',
                    'image_labels':['①','②','A','B','C','D'],'explanatory_text_in_question_image':False,
                    'target':target,'target_visibility':tmeta,'pieces':pieces,'pieces_visibility':pm,'options':opts,'options_visibility':om}

def solution(q):
    pieces=q['solution'];allcells=set(map(tuple,q['target']['cells']));black=set(map(tuple,q['target']['black']))
    nx,ny,nz=[max(p[a] for p in allcells)+1 for a in range(3)]
    w,h=1800,max(470,190+ny*80);im=Image.new('RGB',(w,h),'white');d=ImageDraw.Draw(im)
    labels=['①','②',q['answer']]
    for z in range(nz):
        pw=w/nz;unit=min(105,(pw-95)/nx,(h-205)/ny);x0=z*pw+(pw-nx*unit)/2;y0=95
        text(d,(z*pw+pw/2,36),f'第{z+1}层'+(' 底层' if z==0 else ''),34)
        for y in range(ny):
            for x in range(nx):
                p=(x,y,z);box=(x0+x*unit,y0+(ny-1-y)*unit,x0+(x+1)*unit,y0+(ny-y)*unit)
                if p not in allcells:
                    d.rectangle(box,fill='white',outline='#bbbbbb',width=1);text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),'空',27,fill='#777777');continue
                owner=next(i for i,s in enumerate(pieces) if p in set(map(tuple,s['cells'])))
                d.rectangle(box,fill=INK if p in black else 'white',outline=INK,width=3)
                text(d,((box[0]+box[2])/2,(box[1]+box[3])/2),labels[owner],33,fill='white' if p in black else INK)
    text(d,(w/2,h-30),'黑格对应目标中的3个黑块 各层保持同一朝向 由底向上叠放',32)
    im.save(ASSETS/f'q{q["n"]:02}_solution.png',dpi=(300,300))

def draw_all(questions):
    for q in questions:question(q);solution(q)
    (ROOT/'figure_layout.json').write_text(json.dumps(LAYOUTS,ensure_ascii=False,indent=2),encoding='utf-8')

