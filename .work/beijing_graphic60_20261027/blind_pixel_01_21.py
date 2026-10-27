"""Independent image-only replay of the public operations. No author model imports."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT/'public_rules_and_questions.json'

def turn(a,clockwise=True):return np.rot90(a,k=-1 if clockwise else 1).copy()
def replay(a,op):
 a=a.copy();h,w=a.shape
 if op=='CW':return turn(a)
 if op=='CCW':return turn(a,False)
 if op=='R180':return np.rot90(a,2).copy()
 if op=='IA':return ~a
 if op=='LR':return np.fliplr(a).copy()
 if op=='UD':return np.flipud(a).copy()
 if op=='SX':return np.hstack((a[:,w//2:],a[:,:w//2]))
 if op=='SY':return np.vstack((a[h//2:,:],a[:h//2,:]))
 if op=='MT':a[:h//2,:]=np.fliplr(a[:h//2,:]);return a
 if op=='MB':a[h//2:,:]=np.fliplr(a[h//2:,:]);return a
 if op=='ML':a[:,:w//2]=np.flipud(a[:,:w//2]);return a
 if op=='MR':a[:,w//2:]=np.flipud(a[:,w//2:]);return a
 if op=='IT':a[:h//2,:]=~a[:h//2,:];return a
 if op=='IB':a[h//2:,:]=~a[h//2:,:];return a
 if op=='IL':a[:,:w//2]=~a[:,:w//2];return a
 if op=='IR':a[:,w//2:]=~a[:,w//2:];return a
 if op=='CL':a[:,w//2:]=np.fliplr(a[:,:w//2]);return a
 if op=='CR':a[:,:w//2]=np.fliplr(a[:,w//2:]);return a
 if op=='CT':a[h//2:,:]=np.flipud(a[:h//2,:]);return a
 if op=='CB':a[:h//2,:]=np.flipud(a[h//2:,:]);return a
 if op=='DL':a[:,w//2:]=a[:,:w//2];return a
 if op=='DR':a[:,:w//2]=a[:,w//2:];return a
 if op=='DT':a[h//2:,:]=a[:h//2,:];return a
 if op=='DB':a[:h//2,:]=a[h//2:,:];return a
 if op in ('QCW','QCCW'):
  b=a.copy()
  for r in (0,h//2):
   for c in (0,w//2):b[r:r+h//2,c:c+w//2]=turn(a[r:r+h//2,c:c+w//2],op=='QCW')
  return b
 if op in ('PCW','PCCW'):
  q=[a[:h//2,:w//2],a[:h//2,w//2:],a[h//2:,w//2:],a[h//2:,:w//2]]
  t=[q[(i-1)%4] if op=='PCW' else q[(i+1)%4] for i in range(4)]
  return np.vstack((np.hstack((t[0],t[1])),np.hstack((t[3],t[2]))))
 if op in ('KCW','KCCW'):
  b=a.copy();u=h//4
  for r,c in ((0,0),(0,w-u),(h-u,0),(h-u,w-u)):b[r:r+u,c:c+u]=turn(a[r:r+u,c:c+u],op=='KCW')
  return b
 if op=='DM':return a.T.copy()
 if op=='DA':return np.rot90(a.T,2).copy()
 raise ValueError(op)

def safe_samples(a):
 u=a.shape[0]//4
 # Four safely interior sites per triangle, 256 sites in the 4x4 figure.
 offsets=[(4,1),(6,1),(4,2),(6,2),(9,4),(9,6),(8,4),(8,6),
          (6,9),(4,9),(6,8),(4,8),(1,6),(1,4),(2,6),(2,4)]
 return [bool(a[r*u+round(dy*u/10),c*u+round(dx*u/10)]) for r in range(4) for c in range(4) for dx,dy in offsets]

def run(source_box,option_boxes):
 m=json.loads(MANIFEST.read_text(encoding='utf-8'))
 first=json.loads((ROOT/'first_answers_01_21.json').read_text(encoding='utf-8'))
 first_answers=first['answers']
 items=[];answers={}
 for group in m['groups']:
  if group['group']>7:continue
  for item in group['items']:
   path=Path(item['image']);im=Image.open(path).convert('L')
   def binary(box):return np.asarray(im.crop(box))<128
   a=binary(source_box);steps=[]
   for op in item['seq']:
    a=replay(a,op);steps.append({'operation':op,'safe_black_bits':''.join('1' if b else '0' for b in safe_samples(a))})
   expected=safe_samples(a)
   comparisons=[]
   for letter,box in zip('ABCD',option_boxes):
    actual=safe_samples(binary(box));diff=sum(x!=y for x,y in zip(expected,actual))
    comparisons.append({'option':letter,'differing_triangle_interior_samples':diff,'matches':diff==0})
   selected=[x['option'] for x in comparisons if x['matches']]
   answer=selected[0] if len(selected)==1 else '?'
   answers[str(item['n'])]=answer
   items.append({'n':item['n'],'group':group['group'],'first_answer':first_answers[str(item['n'])],
     'selected':answer,'unique':len(selected)==1,'first_answer_confirmed':answer==first_answers[str(item['n'])],
     'input_image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'steps':steps,
     'candidate_comparisons':comparisons,'first_reasoning':first['notes'][str(item['n'])],
     'public_sequence':item['seq'],'visible_layout_issues':[]})
 report={'reviewer':'operations_audit独立代理','answers':answers,'items':items,
  'scope':'实际打开题1—21的原图，先写目视答案；仅依公开规则和题图，独立像素数组变换后比较每候选256个三角形内点；未读取作者model.py/questions.json/verification.json/build.py或Word答案。',
  'all_unique':all(x['unique'] for x in items),'all_first_answers_confirmed':all(x['first_answer_confirmed'] for x in items),
  'actual_view_all_assigned_images':True,'source_box':source_box,'option_boxes':option_boxes,
  'first_visual_errors':[x['n'] for x in items if not x['first_answer_confirmed']],
  'error_reinspection':'首次目视题3、7、8、12误判，保留原始答案；之后对这4题输入、初选与复算选项放大实际查看。第3题仅凭下半排除不充分、忽略上半；7和8把若干候选的纯色/半格位置看错；12已标初判不确定且把原图半格读成纯色。复算与再次核对后采用独立像素唯一解，不将首次成绩改写为全对。',
  'limits':['本报告不是教师盲审或学员试测。','已查看21张题图，未检查最终Word规则表和整页排版。','256点覆盖全部64个半格扇区；没有自动判断自然语言释义或实测区分度。']}
 (ROOT/'blind_review_01_21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'answers':answers,'all_unique':report['all_unique'],'all_first_answers_confirmed':report['all_first_answers_confirmed']},ensure_ascii=False))

if __name__=='__main__':
 run((25,30,265,270),[(713+j*265,30,953+j*265,270) for j in range(4)])
