from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from PIL import Image,ImageDraw,ImageFont
import json,re,posixpath

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
OUT=ROOT/'reference_a';OUT.mkdir(exist_ok=True)
BASE=PROJECT/'真题/试卷/公务员笔试-行测真题试卷/word版公务员笔试行测665套'
SB=PROJECT/'真题/试卷/事业单位笔试-职测真题试卷/word版事业单位笔试职测563套'
def find(base,glob):return next(base.glob(glob))
CASES=[
 ('A01',2022,'国考行政执法',find(BASE,'2022年国家*行政执法*.docx'),71,'对称轴方向逆时针45度，外形不同但属性方向可迁移'),
 ('A02',2022,'国考行政执法',find(BASE,'2022年国家*行政执法*.docx'),72,'分割图中两个面相似但大小不同，不能把全等混为相似入口'),
 ('A03',2022,'国考行政执法',find(BASE,'2022年国家*行政执法*.docx'),73,'仅数白球连通部分，不数整图/黑球'),
 ('A04',2023,'国考行政执法',find(BASE,'2023年国家*行政执法*.docx'),72,'外轮廓轴对称与内部中心对称需同时满足'),
 ('A05',2024,'国考行政执法',find(BASE,'2024年国家*行政执法*.docx'),73,'黑块外轮廓边数与白块外轮廓边数差值交替，需分主体'),
 ('A06',2022,'天津省考',find(BASE,'2022年天津*.docx'),46,'最大面边数与整图外轮廓边数相等'),
 ('A07',2022,'浙江事业单位5月29日',find(SB,'2022年5月29日浙江*.docx'),42,'总面数无序，改取唯一最大面，最大面为四边形'),
 ('A08',2023,'湖北事业联考D类4月2日',find(SB,'2023年4月2日湖北*D类*.docx'),63,'选取黑圆整体判断对称，避免被相同圆形外框替代'),
 ('A09',2025,'国考行政执法',PROJECT/'真题/最新试卷/前图相关真题/国家/2025年国考真题/2025国考执法-题本+解析.docx',76,'唯一最大面为轴对称，整体形状和面总数均非核心'),
 ('A10',2025,'山东省考',PROJECT/'真题/17-18.2025-2023山东.docx',64,'两组迁移：第一组轴+中心，第二组仅轴对称'),
 ('A11',2025,'江苏A类',PROJECT/'真题/真题录制（事业单位、独立省份、国省考）/26-27.2025-2024江苏A.docx',85,'九宫格对称方向横/竖/双轴与面数3/4/5复合验证'),
 ('A12',2025,'上海省考整理稿',PROJECT/'真题/真题录制（事业单位、独立省份、国省考）/38-39.2025-2024上海.docx',9,'米字分组观察对称类型，不能机械只看横行'),
]
LATEST=PROJECT/'真题/真题录制（事业单位、独立省份、国省考）/国考/2026年国家公务员录用考试【行政执法卷】.docx'
for q in range(76,86):CASES.append((f'A{q-63:02}',2026,'国考行政执法',LATEST,q,'待实际题图与配套解析核对'))
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','v':'urn:schemas-microsoft-com:vml'}
def load(p):
 z=ZipFile(p);r=etree.fromstring(z.read('word/document.xml'));ps=[]
 for i,x in enumerate(r.findall('.//w:p',NS)):
  ps.append({'i':i,'text':''.join(x.xpath('.//w:t/text()',namespaces=NS)),'ids':x.xpath('.//a:blip/@r:embed | .//v:imagedata/@r:id',namespaces=NS)})
 rel={x.get('Id'):posixpath.normpath('word/'+x.get('Target')) for x in etree.fromstring(z.read('word/_rels/document.xml.rels'))}
 return z,ps,rel
def main():
 records=[]
 for sid,year,exam,p,q,mechanism in CASES:
  z,ps,rels=load(p)
  starts=[i for i,x in enumerate(ps) if re.match(rf'^{q}[.．、]',x['text']) and '答案' not in x['text']]
  assert starts,(sid,q)
  i=starts[0];end=next((j for j in range(i+1,len(ps)) if re.match(r'^\d+[.．、]',ps[j]['text']) and '答案' not in ps[j]['text']),min(i+30,len(ps)))
  ids=[]
  for x in ps[i:end]:
   ids+=x['ids']
  paths=[]
  for k,rid in enumerate(dict.fromkeys(ids)):
   name=rels[rid];dest=OUT/f'{sid}_{k+1}{Path(name).suffix}';dest.write_bytes(z.read(name));paths.append(str(dest))
  # A contact sheet is a reading aid; originals remain separately archived.
  images=[Image.open(path).convert('RGB') for path in paths]
  if images:
   maxw=1500;scaled=[]
   for im in images:
    ratio=min(1,maxw/im.width);scaled.append(im.resize((round(im.width*ratio),round(im.height*ratio))))
   sheet=Image.new('RGB',(max(max(im.width for im in scaled),900),sum(im.height for im in scaled)+25*(len(scaled)+1)+65),'white');d=ImageDraw.Draw(sheet)
   d.text((15,10),f'{sid} {year} {exam} Q{q}',font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25),fill='black')
   y=65
   for im in scaled:sheet.paste(im,((sheet.width-im.width)//2,y));y+=im.height+25
   sheetpath=OUT/f'{sid}_review.png';sheet.save(sheetpath)
  else:sheetpath=None
  records.append({'id':sid,'year':year,'exam':exam,'path':str(p),'question':q,'stem_paragraph':ps[i]['i'],'original_mechanism':mechanism,'original_images':paths,'review_image':str(sheetpath) if sheetpath else None,'visual_checked':False,'source_status':'本地题本/教辅整理资料；未核对官方发布原件'})
 (ROOT/'sources_a.json').write_text(json.dumps({'scope':'具体题例抽样研究，不宣称全量官方核实','cases':records},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps([{'id':r['id'],'q':r['question'],'images':len(r['original_images']),'review':r['review_image']} for r in records],ensure_ascii=False,indent=2))
if __name__=='__main__':main()
