from pathlib import Path
import importlib,json,hashlib,random,copy,collections
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
REF=PROJECT/'模式题'/'北京风格图形推理一拖三-1组3题（含答案解析）.docx'
OUT=PROJECT/'模式题'/'北京风格图形操作多样式专项练习-20组60题（含答案解析）.docx'
MODULES=['lines','curves','tokens']
W,H=1900,390
PANEL=280
FONTS=Path('C:/Windows/Fonts')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def font(n,symbol=False):return ImageFont.truetype(str(FONTS/('seguisym.ttf' if symbol else 'simsun.ttc')),n)
def centered(d,xy,text,n=36,symbol=False):
 f=font(n,symbol);b=d.textbbox((0,0),text,font=f)
 d.text((xy[0]-(b[2]-b[0])/2,xy[1]-(b[3]-b[1])/2-b[1]),text,font=f,fill='black')
def arrow(d,x1,y,x2):
 d.line((x1,y,x2,y),fill='black',width=3)
 d.polygon([(x2,y),(x2-10,y-6),(x2-10,y+6)],fill='black')
def apply_chain(m,scene,chain,independent=False):
 s=copy.deepcopy(scene);states=[s]
 for r in chain:
  old=copy.deepcopy(s);s=(m.independent_apply if independent else m.apply)(s,r)
  assert old==states[-1],('input mutated',r)
  states.append(s)
 return states
def pix_key(im):return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
def pixel_distance(a,b):
 diff=ImageChops.difference(a.convert('L'),b.convert('L'))
 return ImageStat.Stat(diff).mean[0]/255

def candidate_paths(m,g,q):
 chain=q['chain'];true=apply_chain(m,q['source'],chain)[-1]
 kt=m.scene_key(true);it=m.render_panel(true,size=PANEL)
 paths=[]
 for i in range(len(chain)-1):
  wrong=chain[:];wrong[i],wrong[i+1]=wrong[i+1],wrong[i]
  paths.append((wrong,f'把第{i+1}、{i+2}步的先后次序颠倒。','order'))
 for i,old in enumerate(chain):
  for r in g['rules']:
   if r['id']==old:continue
   wrong=chain[:];wrong[i]=r['id']
   oldrule=next(x for x in g['rules'] if x['id']==old)
   paths.append((wrong,f'第{i+1}步误用 {r["code"]}（{r["text"].rstrip("。；")}），应使用 {oldrule["code"]}。','replace'))
 # Genuine wrong outputs, canonical visible model and actual pixels both distinct.
 seen={kt};seenpix={pix_key(it)};valid=[]
 for wrong,why,kind in paths:
  s=apply_chain(m,q['source'],wrong)[-1];k=m.scene_key(s)
  if k in seen:continue
  im=m.render_panel(s,size=PANEL);p=pix_key(im)
  if p in seenpix:continue
  distance=pixel_distance(it,im)
  if distance<.004:continue
  seen.add(k);seenpix.add(p)
  valid.append({'scene':s,'chain':wrong,'explanation':why,'kind':kind,'distance':distance})
 assert len(valid)>=3,(g['id'],chain,'insufficient alternatives')
 ordered=sorted(valid,key=lambda c:c['distance'])
 # Include an actual noncommuting order error when one exists, plus nearest
 # distinct rule-substitution errors. No imaginary wrong-order label.
 swaps=[x for x in ordered if x['kind']=='order']
 chosen=swaps[:1]
 for x in ordered:
  if x in chosen:continue
  chosen.append(x)
  if len(chosen)==3:break
 return true,chosen

def make():
 groups=[];questions=[];mods={}
 answers=list('ABCD')*15;random.Random(602028).shuffle(answers)
 for name in MODULES:
  m=importlib.import_module(name);mods[name]=m
  for original in m.get_groups():
   g=copy.deepcopy(original);g['title']=g['title'].replace('：',' ');g['module']=name;g['question_numbers']=[]
   assert len(g['rules']) in [6,7,8] and len(g['questions'])==3
   for raw in g.pop('questions'):
    n=len(questions)+1;true,wrong=candidate_paths(m,g,raw)
    random.Random(20261028+n).shuffle(wrong)
    answer=answers[n-1];options=wrong[:];options.insert('ABCD'.index(answer),{'scene':true,'chain':raw['chain'],'explanation':'依次执行题面规则所得。','kind':'correct','distance':0})
    q={**raw,'n':n,'group':g['id'],'module':name,'answer':answer,'options':options}
    q['states']=apply_chain(m,q['source'],q['chain'])
    questions.append(q);g['question_numbers'].append(n)
   groups.append(g)
 assert [g['id'] for g in groups]==list(range(1,21))
 dump(ROOT/'groups.json',groups);dump(ROOT/'questions.json',questions)
 return groups,questions,mods

def question_image(m,g,q):
 im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
 # Panels have identical 300-pixel square cells with 280-pixel artwork.
 im.paste(m.render_panel(q['source'],size=PANEL),(30,32))
 d.rectangle((20,22,320,322),outline='black',width=3)
 rules={r['id']:r for r in g['rules']}
 codes=[rules[x]['code'] for x in q['chain']]
 text=' → '.join(codes);n=38
 while d.textbbox((0,0),text,font=font(n,True))[2]>285:n-=1
 assert n>=21,(g['id'],codes,n)
 centered(d,(482,161),text,n,True)
 arrow(d,330,215,630)
 for i,opt in enumerate(q['options']):
  im.paste(m.render_panel(opt['scene'],size=PANEL),(660+300*i,32))
  centered(d,(800+300*i,354),'ABCD'[i],40,True)
 d.rectangle((650,22,1850,322),outline='black',width=3)
 for i in range(1,4):d.line((650+300*i,22,650+300*i,322),fill='black',width=2)
 return im

def solution_image(m,g,q):
 im=Image.new('RGB',(W,400),'white');d=ImageDraw.Draw(im);count=len(q['states'])
 centers=[170+i*(1560/(count-1)) for i in range(count)]
 rules={r['id']:r for r in g['rules']}
 for i,(s,x) in enumerate(zip(q['states'],centers)):
  im.paste(m.render_panel(s,size=PANEL),(round(x-140),32))
  d.rectangle((round(x-150),22,round(x+150),322),outline='black',width=2)
  centered(d,(x,360),'原图' if i==0 else f'第{i}步',32)
  if i:
   before=centers[i-1]+155;after=x-155
   arrow(d,round(before),205,round(after))
   code=rules[q['chain'][i-1]]['code']
   centered(d,((before+after)/2,153),code,33,True)
 return im

def render(groups,questions,mods):
 assets=ROOT/'assets';assets.mkdir(exist_ok=True)
 for q in questions:
  m=mods[q['module']];g=groups[q['group']-1]
  question_image(m,g,q).save(assets/f'question-{q["n"]:02}.png')
  solution_image(m,g,q).save(assets/f'solution-{q["n"]:02}.png')
 public=[]
 for g in groups:
  public.append({k:g[k] for k in ['id','title','intro','rules','question_numbers']})
  public[-1]['questions']=[{'n':q['n'],'chain':[next(r['code'] for r in g['rules'] if r['id']==c) for c in q['chain']],
    'image':str(assets/f'question-{q["n"]:02}.png'),'image_sha256':sha(assets/f'question-{q["n"]:02}.png')} for q in questions if q['group']==g['id']]
 dump(ROOT/'public_questions.json',{'instructions':'每组共用本组规则。三个问题独立重置；操作从左到右。外框和候选字母不参加操作。只依据公开规则和题图选择结果。','groups':public})

def verify(groups,questions,mods):
 counts=collections.Counter();sourcepix=set();steps=0;paths=0;coverage={};noncommuting=0
 for g in groups:
  m=mods[g['module']];covered=set()
  for q in (q for q in questions if q['group']==g['id']):
   assert 2<=len(q['chain'])<=4
   states=apply_chain(m,q['source'],q['chain']);ind=apply_chain(m,q['source'],q['chain'],True)
   assert [m.scene_key(s) for s in states]==[m.scene_key(s) for s in ind],('independent',q['n'])
   for a,b in zip(states,states[1:]):
    assert m.scene_key(a)!=m.scene_key(b),(q['n'],'ineffective step')
    assert pix_key(m.render_panel(a,size=PANEL))!=pix_key(m.render_panel(b,size=PANEL)),(q['n'],'invisible step')
    steps+=1
   final=m.scene_key(states[-1]);covered.update(q['chain'])
   assert final!=m.scene_key(q['source']),(q['n'],'identity chain')
   assert all(m.scene_key(m.apply(q['source'],r['id']))!=final for r in g['rules']),(q['n'],'single-rule shortcut')
   for i in range(len(q['chain'])):
    shortened=q['chain'][:i]+q['chain'][i+1:]
    assert m.scene_key(apply_chain(m,q['source'],shortened)[-1])!=final,(q['n'],'redundant',i)
   if any(m.scene_key(apply_chain(m,q['source'],q['chain'][:i]+[q['chain'][i+1],q['chain'][i]]+q['chain'][i+2:])[-1])!=final for i in range(len(q['chain'])-1)):noncommuting+=1
   keys=[];pix=[]
   for opt in q['options']:
    a=apply_chain(m,q['source'],opt['chain'])[-1];b=apply_chain(m,q['source'],opt['chain'],True)[-1]
    assert m.scene_key(a)==m.scene_key(b)==m.scene_key(opt['scene']),(q['n'],'wrongpath')
    keys.append(m.scene_key(a));pix.append(pix_key(m.render_panel(a,size=PANEL)));paths+=1
   assert len(set(keys))==len(set(pix))==4
   assert [i for i,k in enumerate(keys) if k==final]==['ABCD'.index(q['answer'])]
   sourcehash=pix_key(m.render_panel(q['source'],size=PANEL));assert sourcehash not in sourcepix,('duplicate source',q['n']);sourcepix.add(sourcehash)
   counts[q['answer']]+=1
   # Match all input/options and intermediate tiles back to final source assets.
   with Image.open(ROOT/'assets'/f'question-{q["n"]:02}.png') as im:
    assert pix_key(im.crop((30,32,310,312)))==sourcehash
    for i,s in enumerate(q['options']):assert pix_key(im.crop((660+300*i,32,940+300*i,312)))==pix[i]
   with Image.open(ROOT/'assets'/f'solution-{q["n"]:02}.png') as im:
    for i,s in enumerate(states):
     x=170+i*1560/(len(states)-1);assert pix_key(im.crop((round(x-140),32,round(x-140)+280,312)))==pix_key(m.render_panel(s,size=PANEL))
  assert covered=={r['id'] for r in g['rules']},(g['id'],'uncovered',covered)
  coverage[str(g['id'])]=len(covered)
 assert counts==dict.fromkeys('ABCD',15)
 report={'groups':20,'questions':60,'visible_carriers':20,'rules':sum(len(g['rules']) for g in groups),'chain_steps':steps,'candidate_paths_independently_checked':paths,'answer_distribution':dict(counts),'rule_coverage':coverage,'questions_with_noncommuting_adjacent_steps':noncommuting,'distinct_source_images':len(sourcepix),'source_candidate_intermediate_crops_matched':True}
 dump(ROOT/'model_check.json',report);return report

if __name__=='__main__':
 g,q,m=make();render(g,q,m);print(json.dumps(verify(g,q,m),ensure_ascii=False))
