from pathlib import Path
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
OUT=PROJECT/'模式题'/'北京风格图形推理一拖三-1组3题（含答案解析）.docx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
visual={'reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'word_sha256':sha(OUT),'pdf_sha256':sha(ROOT/'preview.pdf'),
 'renderer':'packaged render_docx.py failed: bundled soffice unavailable; dedicated hidden Microsoft Word COM read-only export succeeded; pypdfium2 rasterized at150dpi',
 'pages':[
 {'page':1,'actually_opened':True,'passed':True,'observations':'完整查看规则表与三题。8种规则符号均显示完整；3条操作链从左到右；每题四候选位于同一个外框，A—D在下方；4×4网格保持正方形。无缺图、裁切、重叠、跨页或答案泄露。'},
 {'page':2,'actually_opened':True,'passed':True,'observations':'完整查看答案表与三组4态分步图。原图、三步状态与操作符号一一对应；解析与干扰项文字完整，未被拆页、遮挡或裁切。'}],
 'limits':'代理逐页视觉复核，不等同教师独立审题或学员试测。'}
(ROOT/'visual_review.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2),encoding='utf-8')
old=json.loads((ROOT/'bj2025_0.json').read_text(encoding='utf-8'))
report={'source':old['file'],'source_sha256':sha(Path(old['file'])),
 'analysis_source':json.loads((ROOT/'bj2025_1.json').read_text(encoding='utf-8'))['file'],
 'shared_material_paragraphs':[222,238],'questions':[56,57,58],
 'actual_views':['q240_contact.png','q243_contact.png','q246_contact.png'],
 'format':'公开操作规则表加三个独立前向操作设问，每问三步；输入图与A—D候选，黑白图含半格三角形。',
 'operations':[
 {'question':56,'chain':['左半反色','全图反色','下半内部左右镜像'],'local_answer':'A'},
 {'question':57,'chain':['左右换位','整体逆时针90°','四个角小格各自顺时针90°'],'local_answer':'A'},
 {'question':58,'chain':['全图左右镜像','上半内部左右镜像','右半反色'],'local_answer':'A'}],
 'copyright_scope':'原创只借鉴公开规则表与前向操作的题型结构，不复用原题输入图或选项图。',
 'year_boundary':'2025单年题本与本地合编首章一致；后一组所谓2026章的年份问题另见sources_2026_review.json。'}
(ROOT/'sources_2025_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'visual_pages':2,'word_sha256':sha(OUT)},ensure_ascii=False))
