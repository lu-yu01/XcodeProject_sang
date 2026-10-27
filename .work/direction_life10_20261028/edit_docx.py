from pathlib import Path
from io import BytesIO
import zipfile,json,hashlib,posixpath
from lxml import etree as E
from PIL import Image
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source.docx';OUT=ROOT/'revised.docx'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','pic':'http://schemas.openxmlformats.org/drawingml/2006/picture','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(SOURCE) as z:
    parts={n:z.read(n) for n in z.namelist()};infos=z.infolist()
doc=E.fromstring(parts['word/document.xml'])
rels=E.fromstring(parts['word/_rels/document.xml.rels'])
targets={r.get('Id'):posixpath.normpath('word/'+r.get('Target')) for r in rels}
drawings=doc.findall('.//w:drawing',NS);assert len(drawings)==20
bindings=[]
for i,d in enumerate(drawings):
    kind='question' if i<10 else 'solution';n=i%10+1
    path=ROOT/'assets'/f'{kind}-{n:02}.png'
    with Image.open(path) as im:pw,ph=im.size
    blip=d.find('.//a:blip',NS);rid=blip.get('{'+NS['r']+'}embed');target=targets[rid]
    parts[target]=path.read_bytes()
    ex=d.find('.//wp:extent',NS);cx=int(ex.get('cx'));cy=round(cx*ph/pw)
    ex.set('cy',str(cy))
    transform=d.find('.//pic:spPr/a:xfrm/a:ext',NS)
    assert transform is not None;transform.set('cx',str(cx));transform.set('cy',str(cy))
    bindings.append({'n':n,'kind':kind,'source':str(path),'pixels':[pw,ph],'word_part':target,'sha256':sha(path),'cx':cx,'cy':cy})
q=json.loads((ROOT/'questions.json').read_text(encoding='utf8'))
changed=0
for p in doc.findall('.//w:body/w:p',NS):
    ts=p.findall('.//w:t',NS);text=''.join(t.text or '' for t in ts)
    if text.startswith('小顾站在同一地点，先正对钟楼'):
        assert '每次转过相同角度' in text
        ts[0].text=q[3]['stem']
        for t in ts[1:]:t.text=''
        changed+=1
    if text.startswith('上方俯视图给出一个点光源、'):
        ts[0].text=q[6]['stem']
        for t in ts[1:]:t.text=''
        changed+=1
assert changed==2
parts['word/document.xml']=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
    for info in infos:z.writestr(info,parts[info.filename])
editable={'word/document.xml'}|{x['word_part'] for x in bindings}
with zipfile.ZipFile(SOURCE) as a,zipfile.ZipFile(OUT) as b:
    preserved=[n for n in a.namelist() if n not in editable]
    for n in preserved:assert a.read(n)==b.read(n),n
(ROOT/'word_bindings.json').write_text(json.dumps({'source_sha256':sha(SOURCE),'revised_sha256':sha(OUT),'bindings':bindings,'preserve_only_identical':preserved,'text_changes':['第4题取消等角条件，保留连续向右转、同地同焦距及顺序判断。','第7题明确黑点为点光源在地面的竖直投影。']},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'staged_word':str(OUT),'sha256':sha(OUT),'figures':20,'preserved_package_parts':len(preserved)},ensure_ascii=False))
