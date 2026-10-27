from model import *
from docx import Document
import io
doc=Document(OUT);assert len(doc.inline_shapes)==120
before_word=sha(OUT)
items=[]
for i,shape in enumerate(list(doc.inline_shapes)[:60]):
 n=i+1
 rid=shape._inline.graphic.graphicData.pic.blipFill.blip.embed
 blob=doc.part.related_parts[rid].blob
 old=Image.open(io.BytesIO(blob)).convert('RGB')
 newpath=ROOT/'assets'/f'question-{n:02}.png'
 new=Image.open(newpath).convert('RGB')
 boxes=[(30,32,310,312)]+[(660+300*j,32,940+300*j,312) for j in range(4)]
 assert all(pix_key(old.crop(b))==pix_key(new.crop(b)) for b in boxes),n
 delta=ImageChops.difference(old,new).getbbox()
 assert delta is None or (delta[0]>=330 and delta[2]<=640 and delta[1]>=100 and delta[3]<=200),(n,delta)
 items.append({'n':n,'before_sha256':hashlib.sha256(blob).hexdigest(),'after_sha256':sha(newpath),'source_and_four_options_pixel_identical':True,'change_bbox':delta})
dump(ROOT/'legibility_revision.json',{'before_word_sha256':before_word,'changes':'步骤间空白缩短；11组R/L、14组P/Q、16组C、19组T替代可能与分隔箭头混淆的长代码；三角构架底边文字、17/18组三角尖端方向补明。图形与正确链语义和选项顺序未改。','items':items})
print('60 source and candidate panels unchanged; changes restricted to operation-code strip')
