from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'public_rules_and_questions.json').read_text(encoding='utf-8'))
first=json.loads((ROOT/'first_answers_22_42.json').read_text(encoding='utf-8'))
defs={r['id']:r['definition'] for r in manifest['rules']}
def act(a,name):
 b=a.copy();h,w=a.shape;hh=h//2;hw=w//2
 if name=='CW':return np.rot90(a,-1)
 if name=='CCW':return np.rot90(a,1)
 if name=='R180':return np.rot90(a,2)
 if name=='LR':return np.fliplr(a)
 if name=='UD':return np.flipud(a)
 if name=='SX':return np.concatenate([a[:,hw:],a[:,:hw]],axis=1)
 if name=='SY':return np.concatenate([a[hh:,:],a[:hh,:]],axis=0)
 if name=='IA':return ~a
 if name=='IT':b[:hh,:]=~a[:hh,:]
 elif name=='IB':b[hh:,:]=~a[hh:,:]
 elif name=='IL':b[:,:hw]=~a[:,:hw]
 elif name=='IR':b[:,hw:]=~a[:,hw:]
 elif name=='MT':b[:hh,:]=np.fliplr(a[:hh,:])
 elif name=='MB':b[hh:,:]=np.fliplr(a[hh:,:])
 elif name=='ML':b[:,:hw]=np.flipud(a[:,:hw])
 elif name=='MR':b[:,hw:]=np.flipud(a[:,hw:])
 elif name=='CL':b[:,hw:]=np.fliplr(a[:,:hw])
 elif name=='CR':b[:,:hw]=np.fliplr(a[:,hw:])
 elif name=='CT':b[hh:,:]=np.flipud(a[:hh,:])
 elif name=='CB':b[:hh,:]=np.flipud(a[hh:,:])
 elif name=='DL':b[:,hw:]=a[:,:hw]
 elif name=='DR':b[:,:hw]=a[:,hw:]
 elif name=='DT':b[hh:,:]=a[:hh,:]
 elif name=='DB':b[:hh,:]=a[hh:,:]
 elif name in ('PCW','PCCW'):
  blocks=[a[:hh,:hw],a[:hh,hw:],a[hh:,hw:],a[hh:,:hw]]
  new=[blocks[-1],blocks[0],blocks[1],blocks[2]] if name=='PCW' else [blocks[1],blocks[2],blocks[3],blocks[0]]
  b[:hh,:hw],b[:hh,hw:],b[hh:,hw:],b[hh:,:hw]=new
 elif name in ('QCW','QCCW'):
  for y in (0,hh):
   for x in (0,hw):b[y:y+hh,x:x+hw]=np.rot90(a[y:y+hh,x:x+hw],-1 if name=='QCW' else 1)
 elif name in ('KCW','KCCW'):
  s=h//4
  for y in (0,3*s):
   for x in (0,3*s):b[y:y+s,x:x+s]=np.rot90(a[y:y+s,x:x+s],-1 if name=='KCW' else 1)
 elif name=='DM':return a.T
 elif name=='DA':return np.flip(a.T,axis=(0,1))
 else:raise ValueError(name)
 return b
sample=[]
for r in range(4):
 for c in range(4):
  for x,y in [(30,10),(50,30),(30,50),(10,30)]:
   for dx,dy in [(-2,-2),(2,-2),(-2,2),(2,2)]:sample.append((r*60+y+dy,c*60+x+dx))
def signature(a):return ''.join('1' if a[y,x] else '0' for y,x in sample)
def summarize(a):
 # Four points per cell in N/E/S/W order for a compact independently observed intermediate state.
 return [[sum((1<<i) for i,(x,y) in enumerate([(30,10),(50,30),(30,50),(10,30)]) if a[r*60+y,c*60+x]) for c in range(4)] for r in range(4)]
items=[];answers={}
for group in manifest['groups']:
 for item in group['items']:
  n=item['n']
  if not 22<=n<=42:continue
  p=Path(item['image']);im=Image.open(p).convert('L');a=np.asarray(im.crop((25,30,265,270)))<128
  steps=[]
  for name in item['seq']:
   a=act(a,name);steps.append({'operation':name,'definition':defs[name],'observed_cells_NESW':summarize(a)})
  comparisons=[]
  for j,l in enumerate('ABCD'):
   candidate=np.asarray(im.crop((713+j*265,30,953+j*265,270)))<128
   differences=sum(bool(a[y,x])!=bool(candidate[y,x]) for y,x in sample)
   comparisons.append({'option':l,'different_samples':differences,'matches':differences==0})
  matches=[c['option'] for c in comparisons if c['matches']]
  answer=matches[0] if len(matches)==1 else None
  answers[str(n)]=answer
  items.append({'n':n,'group':group['group'],'input_image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
   'image_actually_opened':True,'first_answer':first['answers'][str(n)],'first_answer_confirmed':first['answers'][str(n)]==answer,
   'selected':answer,'unique':len(matches)==1,'steps':steps,'candidate_comparisons':comparisons,'visible_layout_issues':[]})
report={'reviewer':'blind22_42独立代理','answers':answers,'items':items,
 'author_model_or_answer_read':False,'all_images_actually_opened':True,
 'actual_scope':'第8—14组，即题22—42；只读公开规则manifest与指定21张题图。未读作者模型、题库答案、解析或Word。',
 'method':'先实际查看题图并保存首次目视初选，再独立以240×240像素数组执行公开操作规则。在每个格子四扇区重心附近各选4点，每个选项256个内点避开格线/斜线比较。',
 'all_unique':all(i['unique'] for i in items),
 'initial_answer_corrections':[i['n'] for i in items if not i['first_answer_confirmed']],
 'visual_review':'21张图均原始尺寸实际打开；4×4方形网格、同框四选项、下方ABCD、符号与数字均可辨。未见裁切或重叠。',
 'limitations':['首次目视初选含低置信度答案，纠正记录如实保留。','像素复算检查的是给定规则的几何执行与候选唯一性，不代替教师盲审、学员试测或全Word逐页排版检查。']}
(ROOT/'blind_review_22_42.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'answers':answers,'all_unique':report['all_unique'],'initial_answer_corrections':report['initial_answer_corrections']},ensure_ascii=False))
