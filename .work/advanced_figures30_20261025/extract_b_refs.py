from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from PIL import Image,ImageDraw,ImageFont
import io,json,re
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
OUT=ROOT/'reference_b';OUT.mkdir(exist_ok=True)
paths=[
 '真题/最新试卷/2025江苏判断题本.docx',
 '真题/最新试卷/2025浙江判断题本.docx',
 '真题/最新试卷/2024江苏C类真题.docx',
 '真题/最新试卷/2023江苏省考行测AB判断部分(2).docx',
 '真题/最新试卷/北京OK/2022年北京公务员考试《行测》真题_2023122615_50.docx',
 '真题/真题录制（事业单位、独立省份、国省考）/特殊省份/23-24.2025-2024广东.docx',
]
paths += [str(p.relative_to(PROJECT)) for p in (PROJECT/'真题/最新试卷/前图相关真题/23-25联考职测ABC类试题').glob('*2024年3月30日*C类*试题.docx')]
paths += ['真题/真题录制（事业单位、独立省份、国省考）/国考/2026年国家公务员录用考试【行政执法卷】.docx']
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','v':'urn:schemas-microsoft-com:vml'}
records=[];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
for di,path in enumerate(paths):
 p=PROJECT/path
 if not p.exists():continue
 with ZipFile(p) as z:
  rel={e.get('Id'):e.get('Target') for e in etree.fromstring(z.read('word/_rels/document.xml.rels'))}
  body=etree.fromstring(z.read('word/document.xml')).find('w:body',ns)
  last=[];thumbs=[]
  for pi,par in enumerate(body.findall('.//w:p',ns)):
   txt=''.join(par.itertext()) if False else ''.join(par.xpath('.//w:t/text()',namespaces=ns))
   if txt.strip():last=(last+[txt])[-4:]
   ids=par.xpath('.//a:blip/@r:embed|.//v:imagedata/@r:id',namespaces=ns)
   for ii,rid in enumerate(ids):
    target=rel.get(rid,'');name='word/'+target.lstrip('/')
    if name not in z.namelist():continue
    data=z.read(name)
    try:im=Image.open(io.BytesIO(data)).convert('RGB')
    except:continue
    if im.width<120 or im.height<60:continue
    fn=f'd{di}_p{pi}_i{ii}.png';im.save(OUT/fn)
    record={'id':fn[:-4],'path':str(p),'paragraph':pi,'image':str(OUT/fn),'context':last,'size':im.size}
    records.append(record)
    # Early diagram section only; keep contact sheets tractable.
    if len(thumbs)<35:
     tile=Image.new('RGB',(580,330),'white');im.thumbnail((560,275));tile.paste(im,((580-im.width)//2,43));ImageDraw.Draw(tile).text((8,5),fn,font=font,fill='black');thumbs.append(tile)
  for page in range((len(thumbs)+7)//8):
   sheet=Image.new('RGB',(1160,1320),'#dddddd')
   for j,tile in enumerate(thumbs[page*8:(page+1)*8]):sheet.paste(tile,((j%2)*580,(j//2)*330))
   sheet.save(OUT/f'contact_d{di}_{page}.png')
(OUT/'extracted_index.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'doc':i,'path':p} for i,p in enumerate(paths)],ensure_ascii=False,indent=2))
print('records',len(records))
