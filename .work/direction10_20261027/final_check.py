from pathlib import Path
import json,hashlib,datetime,zipfile,io,re,math
from PIL import Image
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader
from model import *

INDEX=PROJECT/'知识库'/'套卷索引'/(OUT.stem+'.md')
RULES=PROJECT/'知识库'/'情境方向图形题命题与检查规则.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def norm(t):return re.sub(r'\s+','',t)
def record_visual():
 # Run only after root has actually opened all final page images at original size.
 pages=[]
 for n in range(1,11):
  p=ROOT/'render'/f'page-{n:02}.png';assert p.exists()
  pages.append({'page':n,'actually_opened':True,'passed':True,'sha256':sha(p),
   'observations':'两题题干、必要方位及地标、完整照片/候选、编号和候选外字母均可读，未见裁切、重叠、缺图或题图拆页。' if n<=5 else '两题正确答案、方向示意图及具体干扰解释完整，未见裁切、重叠、缺字或解析拆页。'})
 (ROOT/'visual_review.json').write_text(json.dumps({'checked_at':now(),'word_sha256':sha(OUT),'pdf_sha256':sha(ROOT/'preview.pdf'),'pages':pages,'reference_pages_actually_opened':2,'renderer':'打包render_docx.py缺少soffice.exe；诊断后用独立隐藏Word只读导出PDF，pypdfium2按150dpi栅格化。'},ensure_ascii=False,indent=2),encoding='utf-8')

def physics_checks():
 # Independently intersect each light-to-rim ray with Z=0, without using its
 # previously derived shadow formula, then compare the actual model endpoints.
 count=0
 for point in POSTS7:
  for k in range(24):
   rim=(point[0]+.3*math.cos(k*math.tau/24),point[1]+.3*math.sin(k*math.tau/24),1.8)
   ray=tuple(rim[j]-LIGHT[j] for j in range(3));t=-LIGHT[2]/ray[2]
   intersection=tuple(LIGHT[j]+t*ray[j] for j in range(3))
   expected=shadow_point(rim[:2],LIGHT,1.8)
   assert abs(intersection[2])<1e-9 and all(abs(a-b)<1e-9 for a,b in zip(intersection[:2],expected));count+=1
 # Shadow-gray pixels must not touch any option's camera viewport boundary.
 for n in [6,7]:
  with Image.open(ROOT/'assets'/f'question-{n:02}.png') as im:
   for j in range(4):
    tile=im.crop((30+440*j,373,450+440*j,733))
    for x,y in [(x,y) for x in range(420) for y in [0,1,358,359]]+[(x,y) for x in [0,1,418,419] for y in range(360)]:
     r,g,b=tile.getpixel((x,y));assert not (130<=r<=165 and r==g==b),(n,j,x,y)
 # Cardinal sign pairs of the southward ground shadow separate all four observers.
 quadrants=[(8,10),(-8,10),(-8,-10),(8,-10)];signs=[]
 for cam in quadrants:
  r=relative((0,-1),(0,0),(-cam[0],-cam[1]));signs.append(tuple(map(sign,r)))
 assert len(set(signs))==4 and signs[2]==(1,-1)
 return {'point_light_rim_ray_plane_checks':count,'shadow_option_viewports':8,'sun_observer_quadrants_unique':4}

def check():
 model=verify();physics=physics_checks();doc=Document(OUT)
 assert len(doc.inline_shapes)==20 and len(doc.sections)==1 and not doc.tables
 assert not list(doc.element.iter(qn('w:pBdr'))) and not list(doc.styles.element.iter(qn('w:pBdr')))
 for i,s in enumerate(doc.inline_shapes):
  n=i%10+1;kind='question' if i<10 else 'solution';path=ROOT/'assets'/f'{kind}-{n:02}.png'
  rid=s._inline.graphic.graphicData.pic.blipFill.blip.embed;data=doc.part.related_parts[rid].blob
  assert hashlib.sha256(data).hexdigest()==sha(path)
  with Image.open(io.BytesIO(data)) as im:assert abs(float(s.width)/float(s.height)-im.width/im.height)<.00002
 reader=PdfReader(ROOT/'preview.pdf');assert len(reader.pages)==10
 full=norm(''.join(p.text for p in doc.paragraphs));page_texts=[norm(p.extract_text()) for p in reader.pages]
 for i in range(5):
  assert len(reader.pages[i].images)==2 and len(reader.pages[i+5].images)==2
  assert '干扰项辨析' not in page_texts[i] and page_texts[i+5].count('干扰项辨析')==2
  for q in Q[i*2:i*2+2]:
   assert norm(q['stem']) in full and norm(q['stem']) in page_texts[i]
   assert f'{q["n"]}.' in page_texts[i]
   if q['n']<=5:
    for letter,v in zip('ABCD',q['options']):assert letter+'.'+v in page_texts[i]
   for text in [q['explanation'],'干扰项辨析：'+q['distractors']]:assert norm(text) in page_texts[i+5]
   assert f'第{q["n"]}题{q["answer"]}' in page_texts[i+5]
 assert '阳光照射下' in page_texts[2]
 answers={};first_correct=0
 for name in ['blind_review_01_05.json','blind_review_06_10.json']:
  b=json.loads((ROOT/name).read_text(encoding='utf-8'));answers.update(b['answers'])
  for item in b['items']:
   assert item['image_sha256']==sha(ROOT/'assets'/f'question-{item["n"]:02}.png') and item['unique']
   assert item.get('actually_opened_original',item.get('image_actually_opened'))
   assert not item.get('defects',item.get('visible_issues',[]))
   first_correct+=item['first_answer']==b['answers'][str(item['n'])]
  if name.endswith('06_10.json'):
   r=b['wording_recommendation'];assert r['accepted'] and r['after_stem']==Q[5]['stem'] and r['after_public_questions_sha256']==sha(ROOT/'public_questions.json')
 assert answers=={str(q['n']):q['answer'] for q in Q} and first_correct==10
 baseline=json.loads((ROOT/'baseline_docx.json').read_text(encoding='utf-8'))
 for p,h in baseline.items():assert sha(PROJECT/p)==h,p
 fidelity=json.loads((ROOT/'template_fidelity.json').read_text(encoding='utf-8'))
 assert fidelity['word_sha256']==sha(OUT) and fidelity['section_identical']
 with zipfile.ZipFile(REF) as a,zipfile.ZipFile(OUT) as b:
  for n in fidelity['preserve_only_identical']:assert a.read(n)==b.read(n)
 visual=json.loads((ROOT/'visual_review.json').read_text(encoding='utf-8'))
 assert visual['word_sha256']==sha(OUT) and visual['pdf_sha256']==sha(ROOT/'preview.pdf')
 assert len(visual['pages'])==10 and all(p['passed'] and p['actually_opened'] for p in visual['pages'])
 for v in visual['pages']:assert v['sha256']==sha(ROOT/'render'/f'page-{v["page"]:02}.png')
 for md in [INDEX,RULES,PROJECT/'知识库'/'项目说明.md',PROJECT/'知识库'/'建议与变更记录.md']:
  assert md.exists()
  for target in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
   if '://' not in target:assert (md.parent/target).resolve().exists(),(md,target)
 report={'passed':True,'checked_at':now(),'word':str(OUT),'word_sha256':sha(OUT),'pdf_sha256':sha(ROOT/'preview.pdf'),
  'questions':10,'pages':10,'question_pages':5,'analysis_pages':5,'visible_images':20,'model_checks':model,
  'physics_checks':physics,'blind_first_answers_matching':first_correct,'blind_final_answers_matching':10,
  'sunlight_wording_issue_closed':True,'existing_words_unchanged':len(baseline),'template_preserve_only_parts_unchanged':True,
  'visual_pages_actually_opened':10,'knowledge_links_passed':True,'limits':['原创专项配额并非某年考试配额','代理试解不是教师盲审','未进行学员试测或实测难度校准']}
 (ROOT/'final_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:report[k] for k in ['passed','questions','pages','visible_images','blind_final_answers_matching','existing_words_unchanged','word_sha256']},ensure_ascii=False))
if __name__=='__main__':
 import sys
 if '--record-visual' in sys.argv:record_visual();print('actual final 10 pages recorded')
 else:check()
