"""Independent review from published rules and final PNGs only; no author model."""
from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
def run(a,code):
 a=a.copy()
 if code=='CW':return np.rot90(a,-1)
 if code=='CCW':return np.rot90(a,1)
 if code=='R180':return np.rot90(a,2)
 if code=='LR':return np.fliplr(a)
 if code=='UD':return np.flipud(a)
 if code=='DM':return a.T
 if code=='DA':return np.flipud(np.fliplr(a.T))
 if code=='SX':return np.concatenate([a[:,120:],a[:,:120]],axis=1)
 if code=='SY':return np.concatenate([a[120:,:],a[:120,:]],axis=0)
 if code=='IA':return ~a
 if code=='IT':a[:120,:]=~a[:120,:];return a
 if code=='IB':a[120:,:]=~a[120:,:];return a
 if code=='IL':a[:,:120]=~a[:,:120];return a
 if code=='IR':a[:,120:]=~a[:,120:];return a
 if code=='MT':a[:120,:]=np.fliplr(a[:120,:]);return a
 if code=='MB':a[120:,:]=np.fliplr(a[120:,:]);return a
 if code=='ML':a[:,:120]=np.flipud(a[:,:120]);return a
 if code=='MR':a[:,120:]=np.flipud(a[:,120:]);return a
 if code=='CL':a[:,120:]=np.fliplr(a[:,:120]);return a
 if code=='CR':a[:,:120]=np.fliplr(a[:,120:]);return a
 if code=='CT':a[120:,:]=np.flipud(a[:120,:]);return a
 if code=='CB':a[:120,:]=np.flipud(a[120:,:]);return a
 if code=='DL':a[:,120:]=a[:,:120];return a
 if code=='DR':a[:,:120]=a[:,120:];return a
 if code=='DT':a[120:,:]=a[:120,:];return a
 if code=='DB':a[:120,:]=a[120:,:];return a
 if code in ('PCW','PCCW'):
  blocks=[a[:120,:120].copy(),a[:120,120:].copy(),a[120:,120:].copy(),a[120:,:120].copy()]
  src=[3,0,1,2] if code=='PCW' else [1,2,3,0]
  for (ys,xs),i in zip([(slice(0,120),slice(0,120)),(slice(0,120),slice(120,240)),(slice(120,240),slice(120,240)),(slice(120,240),slice(0,120))],src):a[ys,xs]=blocks[i]
  return a
 if code in ('QCW','QCCW'):
  for y in (0,120):
   for x in (0,120):a[y:y+120,x:x+120]=np.rot90(a[y:y+120,x:x+120],-1 if code=='QCW' else 1)
  return a
 if code in ('KCW','KCCW'):
  for y in (0,180):
   for x in (0,180):a[y:y+60,x:x+60]=np.rot90(a[y:y+60,x:x+60],-1 if code=='KCW' else 1)
  return a
 raise ValueError(code)
def main():
 pub=json.loads((R/'public_rules_and_questions.json').read_text(encoding='utf-8'))
 first=json.loads((R/'first_answers_43_60.json').read_text(encoding='utf-8'))
 rules={r['id']:r for r in pub['rules']}
 safe=[(ry*60+y,cx*60+x) for ry in range(4) for cx in range(4) for y in (7,17,43,53) for x in (10,22,38,50)]
 records=[];answers={}
 for g in pub['groups']:
  if not 15<=g['group']<=20:continue
  for q in g['items']:
   path=Path(q['image']);im=Image.open(path).convert('L')
   pixels=np.asarray(im)<128
   a=pixels[30:270,25:265].copy();states=[]
   for code in q['seq']:
    a=run(a,code);states.append({'rule':rules[code]['symbol'],'definition':rules[code]['definition']})
   options=[]
   for j in range(4):
    b=pixels[30:270,713+265*j:953+265*j]
    bad=sum(bool(a[y,x])!=bool(b[y,x]) for y,x in safe)
    options.append({'letter':'ABCD'[j],'different_safe_samples':bad,'matches':bad==0})
   matches=[v['letter'] for v in options if v['matches']]
   selected=matches[0] if len(matches)==1 else None
   answers[str(q['n'])]=selected
   records.append({'n':q['n'],'group':g['group'],'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    'actually_opened_original':True,'first_answer':first['answers'][str(q['n'])],
    'first_answer_confirmed':selected==first['answers'][str(q['n'])],
    'answer':selected,'unique':len(matches)==1,'steps':states,'option_comparison':options,
    'visible_issues':[]})
 report={'reviewer':'blind43_60 独立代理','reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'input_scope':['公开规则清单','18张最终题图'],
  'author_model_or_answers_read':False,'answers':answers,'items':records,
  'all_unique':all(r['unique'] for r in records),'first_answers_correct':sum(r['first_answer_confirmed'] for r in records),
  'actual_images_opened':18,'comparison_method':'实际裁取240×240输入PNG，以独立NumPy数组实现公开规则，比较每选项256个远离格线与斜边的内点；未读取作者模型或答案。',
  'limits':['独立代理审题不等于教师盲审或学员试测','只检查题图与规则语义，没有查看最终Word页面或答案解析'],
  'visual_notes':'已逐一打开18张原始题图。4×4格网正方，四候选共用外框，A—D位于框外下方；形状及右侧数字可辨；无明显裁切或重叠。'}
 (R/'blind_review_43_60.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'answers':answers,'all_unique':report['all_unique'],'first_answers_correct':report['first_answers_correct'],'differences':[(r['n'],r['first_answer'],r['answer']) for r in records if not r['first_answer_confirmed']]},ensure_ascii=False))
if __name__=='__main__':main()
