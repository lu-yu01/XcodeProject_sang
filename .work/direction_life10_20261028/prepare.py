from pathlib import Path
import json,shutil,hashlib,urllib.request,concurrent.futures
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
OLD=PROJECT/'.work/direction10_20261027'
OUT=PROJECT/'模式题/北京风格情境方向图形推理-10题（含答案解析）.docx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['sources','svg','assets','render']: (ROOT/name).mkdir(exist_ok=True)
if not (ROOT/'source.docx').exists():shutil.copy2(OUT,ROOT/'source.docx')
for name in ['model.py','questions.json']:
    if not (ROOT/name).exists():shutil.copy2(OLD/name,ROOT/name)
if not (ROOT/'baseline.json').exists():
    (ROOT/'baseline.json').write_text(json.dumps({str(p.relative_to(PROJECT)):sha(p) for p in (PROJECT/'模式题').glob('*.docx')},ensure_ascii=False,indent=2),encoding='utf8')
urls={'house':'https://openclipart.org/download/213780','car':'https://openclipart.org/download/215974',
      'tree':'https://openclipart.org/download/213774','lamp':'https://openclipart.org/download/251873',
      'library':'https://freesvg.org/download/205739','shop':'https://freesvg.org/download/199559',
      'clock':'https://freesvg.org/download/59933','person':'https://openclipart.org/download/21887',
      'cinema':'https://freesvg.org/download/30020'}
def fetch(item):
    n,u=item;p=ROOT/'sources'/f'{n}.svg'
    if p.exists():return n,len(p.read_bytes()),'already saved'
    try:
        response=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0','Referer':'https://freesvg.org/'}),timeout=25)
        data=response.read()
        if b'<svg' not in data:
            if data[:2]==b'\x1f\x8b':
                import gzip
                data=gzip.decompress(data)
            else:return n,'non-SVG response',response.headers.get('Content-Type'),repr(data[:120])
        assert b'<svg' in data and len(data)>100
        p.write_bytes(data);return n,len(data),sha(p)
    except Exception as e:return n,type(e).__name__,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for r in pool.map(fetch,urls.items()):print(r)
