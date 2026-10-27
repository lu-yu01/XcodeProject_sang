from pathlib import Path
from zipfile import ZipFile
from lxml import etree
import json

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]
W={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def paragraphs(path):
    with ZipFile(path) as z:
        xml=etree.fromstring(z.read('word/document.xml'))
    return [''.join(p.itertext()) if False else ''.join(p.xpath('.//w:t/text()',namespaces=W)) for p in xml.xpath('//w:body//w:p',namespaces=W)]
sources={
 'N26':BASE/'真题/真题录制（事业单位、独立省份、国省考）/国考/2026年国家公务员录用考试【行政执法卷】.docx',
 'N26A':BASE/'真题/真题录制（事业单位、独立省份、国省考）/国考/2026年国家公务员录用考试【行政执法卷解析】.docx',
 'N25':BASE/'真题/最新试卷/前图相关真题/国家/2025年国考真题/2025国考执法-题本+解析.docx',
}
for year in [2022,2023,2024]:
    candidates=sorted((BASE/'真题/试卷/公务员笔试-行测真题试卷/word版公务员笔试行测665套').glob(f'{year}*国家*行政执法*.docx'))
    sources[f'N{year%100}']=candidates[0]
for name,path in sources.items():
    ps=paragraphs(path)
    (ROOT/f'research_{name}.txt').write_text('\n'.join(f'{i:04d} {p}' for i,p in enumerate(ps)),encoding='utf-8')
manifest={key:{'path':str(path),'paragraphs':len(paragraphs(path))} for key,path in sources.items()}
(ROOT/'research_formal_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
for p in (BASE/'模式题').glob('*.docx'):
    if any(s in p.name for s in ['模拟卷（一）-35','模拟卷（二）-2026','专项练习-55题']) and '图片规范' not in p.name:
        (ROOT/('old_'+p.stem+'.txt')).write_text('\n'.join(paragraphs(p)),encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))
