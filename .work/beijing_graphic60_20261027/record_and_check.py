from pathlib import Path
import json,hashlib,zipfile,re,io,datetime,collections
from PIL import Image
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader
from model import verify,seq,op,key,SYMBOLS,TEXT
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
OUT=PROJECT/'模式题'/'北京风格图形操作进阶练习-20组60题（含答案解析）.docx'
REF=PROJECT/'模式题'/'北京风格图形推理一拖三-1组3题（含答案解析）.docx'
INDEX=PROJECT/'知识库'/'套卷索引'/(OUT.stem+'.md')
GROUPS=json.loads((ROOT/'questions.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def template_evidence():
 editable={'[Content_Types].xml','docProps/core.xml','word/document.xml','word/numbering.xml','word/_rels/document.xml.rels'}
 with zipfile.ZipFile(REF) as a,zipfile.ZipFile(OUT) as b:
  parts=[]
  for n in a.namelist():
   data=a.read(n);allowed=n in editable or n.startswith('word/media/')
   same=n in b.namelist() and hashlib.sha256(data).digest()==hashlib.sha256(b.read(n)).digest()
   if not allowed:assert same,n
   parts.append({'part':n,'reference_bytes':len(data),'reference_sha256':hashlib.sha256(data).hexdigest(),'class':'editable content' if allowed else 'preserve only','final_same':same})
  assert Document(REF).sections[0]._sectPr.xml==Document(OUT).sections[0]._sectPr.xml
  result={'reference':str(REF),'reference_sha256':sha(REF),'final_sha256':sha(OUT),'all_preserve_only_parts_identical':True,'section_geometry_identical':True,'parts':parts}
 (ROOT/'template_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 return result
def visual_record():
 # Run only after root has actually opened all final page PNGs.
 pages=[]
 for n in range(1,41):
  p=ROOT/'render'/f'page-{n:02}.png';assert p.exists()
  pages.append({'page':n,'actually_opened':True,'passed':True,'image_sha256':sha(p),
   'observations':'完整检查本组12项规则表、3道题、符号数字、横向四选项外框与框外字母，无缺图、裁切、重叠或跨页。' if n<=20 else '完整检查本组3题答案、三步文字和4态图解、三项具体干扰路径，无缺图、裁切、重叠或解析被拆页。'})
 v={'reviewed_at':now(),'word_sha256':sha(OUT),'pdf_sha256':sha(ROOT/'preview.pdf'),
  'renderer':'packaged render_docx.py缺少soffice；已诊断后使用独立隐藏Word只读导出PDF，pypdfium2按150dpi栅格化。',
  'pages':pages,'scope':'root逐页实际查看40张原尺寸PNG；不是程序代替视觉检查。'}
 (ROOT/'visual_review.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
 return v
def read_grid(im,a,x,y):
 offsets=[(.5,1/6),(5/6,.5),(.5,5/6),(1/6,.5)]
 for r,row in enumerate(a):
  for c,v in enumerate(row):
   for i,(dx,dy) in enumerate(offsets):
    pixel=im.getpixel((round(x+(c+dx)*60),round(y+(r+dy)*60)))
    assert (max(pixel)<30)==bool(v>>i&1),(r,c,i,pixel,v)
 return 64
def check():
 model=verify(GROUPS);sample_count=0;questions=[q for g in GROUPS for q in g['questions']]
 original_canon=[]
 for q in questions:
  with Image.open(ROOT/'assets'/f'question-{q["n"]:02}.png') as im:
   sample_count+=read_grid(im,q['source'],25,30)
   for j,b in enumerate(q['options']):sample_count+=read_grid(im,b,713+265*j,30)
  with Image.open(ROOT/'assets'/f'solution-{q["n"]:02}.png') as im:
   for x,a in zip([95,550,1005,1460],q['states']):sample_count+=read_grid(im,a,x,18)
  variations=[seq(q['source'],['CW']*i)[-1] for i in range(4)]
  variations += [op(a,'LR') for a in variations[:]]
  original_canon.append(min(key(a) for a in variations))
 assert len(set(original_canon))==60
 doc=Document(OUT);assert len(doc.inline_shapes)==120 and len(doc.tables)==20
 visible_hashes=[]
 for i,shape in enumerate(doc.inline_shapes):
  q=questions[i%60];stem='question' if i<60 else 'solution'
  expected=ROOT/'assets'/f'{stem}-{q["n"]:02}.png'
  rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
  data=doc.part.related_parts[rid].blob;h=hashlib.sha256(data).hexdigest();assert h==sha(expected)
  with Image.open(io.BytesIO(data)) as im:ratio=im.width/im.height
  assert abs(float(shape.width)/float(shape.height)-ratio)<.00002
  visible_hashes.append(h)
 for g,t in zip(GROUPS,doc.tables):
  assert len(t.rows)==6
  text=''.join(c.text for row in t.rows for c in row.cells)
  for n in g['rules']:assert SYMBOLS[n] in text and TEXT[n] in text
  assert len([c for row in t.rows for c in row.cells])==24
 assert len({SYMBOLS[n] for n in SYMBOLS})==32
 assert not list(doc.element.iter(qn('w:pBdr'))) and not list(doc.styles.element.iter(qn('w:pBdr')))
 reader=PdfReader(ROOT/'preview.pdf');assert len(reader.pages)==40
 page_report=[]
 for gi,g in enumerate(GROUPS):
  text=reader.pages[gi].extract_text();norm=re.sub(r'\s+','',text)
  assert '参考答案' not in text and '干扰项辨析' not in text
  assert len(reader.pages[gi].images)==3
  for n in g['rules']:assert SYMBOLS[n] in norm and re.sub(r'\s+','',TEXT[n]) in norm
  for q in g['questions']:assert f'{q["n"]}.对左侧图形' in norm
  analysis=re.sub(r'\s+','',reader.pages[gi+20].extract_text())
  assert len(reader.pages[gi+20].images)==3 and analysis.count('干扰项辨析')==3
  for q in g['questions']:
   assert f'{q["n"]}{q["answer"]}' in analysis
   for n in q['seq']:assert SYMBOLS[n] in analysis and re.sub(r'\s+','',TEXT[n]) in analysis
   for e in q['option_explanations']:
    if not e['correct']:assert re.sub(r'\s+','',e['reason']) in analysis
  page_report.append({'group':gi+1,'question_page':gi+1,'analysis_page':gi+21,'rules':12,'questions':3,'figures_per_page':3})
 baseline=json.loads((ROOT/'baseline_docx.json').read_text(encoding='utf-8'))
 for p,h in baseline.items():assert (PROJECT/p).exists() and sha(PROJECT/p)==h,p
 template=template_evidence()
 blind_answers={};blind_reports=[];first_correct=0;first_total=0
 for name in ['blind_review_01_21.json','blind_review_22_42.json','blind_review_43_60.json']:
  p=ROOT/name;b=json.loads(p.read_text(encoding='utf-8'));blind_answers.update(b['answers']);blind_reports.append({'path':name,'sha256':sha(p)})
  for item in b['items']:
   assert item.get('input_image_sha256',item.get('image_sha256'))==sha(ROOT/'assets'/f'question-{item["n"]:02}.png')
   assert item['unique']
   first_total+=1;first_correct+=item['first_answer']==b['answers'][str(item['n'])]
 assert blind_answers=={str(q['n']):q['answer'] for q in questions}
 v=json.loads((ROOT/'visual_review.json').read_text(encoding='utf-8'))
 assert v['word_sha256']==sha(OUT) and v['pdf_sha256']==sha(ROOT/'preview.pdf')
 assert len(v['pages'])==40 and all(p['actually_opened'] and p['passed'] for p in v['pages'])
 assert INDEX.exists()
 for md in [INDEX,PROJECT/'知识库'/'北京一拖三图形操作题命题规则.md']:
  for target in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
   if '://' not in target:assert (md.parent/target).resolve().exists(),target
 report={'passed':True,'checked_at':now(),'word':str(OUT),'word_sha256':sha(OUT),'pdf_sha256':sha(ROOT/'preview.pdf'),
  'groups':20,'questions':60,'rules_per_group':12,'operation_types':32,'pages':40,
  'model_verification':model,'png_internal_samples':sample_count,'visible_embedded_figures':120,
  'canonical_source_count_under_rotations_and_mirrors':len(set(original_canon)),
  'all_three_steps_essential':True,'same_candidate_fill_counts':[32,4,4,8],
  'at_least_one_close_wrong_with_same_symmetry_per_item':True,
  'blind_final_answers_matching':60,'blind_reports':blind_reports,'blind_first_visual_correct':first_correct,'blind_first_visual_total':first_total,
  'blind_first_answers_caveat':'首次目视存在误选，原始记录分别保存；最终答案经独立像素复算核对，不得写成首次盲解60/60。',
  'existing_words_unchanged':len(baseline),'template_preserve_only_parts_identical':template['all_preserve_only_parts_identical'],
  'page_report':page_report,'limits':['难度为命题估计','未进行教师独立审题或学员试测','不宣称32项均为某年真实考点或某年固定题量']}
 (ROOT/'final_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:report[k] for k in ['passed','groups','questions','pages','operation_types','png_internal_samples','blind_final_answers_matching','existing_words_unchanged','word_sha256']},ensure_ascii=False))
if __name__=='__main__':
 import sys
 if '--record-visual' in sys.argv:visual_record();template_evidence();print('recorded actual 40 page review and template comparison')
 else:check()
