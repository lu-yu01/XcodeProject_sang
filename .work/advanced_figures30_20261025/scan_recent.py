"""Locate recent-source evidence; text matches are leads, not visual verification."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from collections import Counter,defaultdict
import re,json
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parent.parent
def write(name,obj):(ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
    books=[];tags=defaultdict(Counter)
    for line in (PROJECT/'.work/corpus_audit/xls_question_metadata.jsonl').read_text(encoding='utf-8').splitlines():
        x=json.loads(line);name=Path(x['path']).name;m=re.match(r'(202[1-6])年',name)
        if not m:continue
        year=m[1];kind='职测' if '职测真题试卷' in x['path'] else ('行测' if '行测真题试卷' in x['path'] else '自建卷')
        points=Counter(q.get('point','') for q in x['questions'] if re.search('图形|数量规律|样式规律|位置规律|重构|属性规律',q.get('point','')))
        books.append({'year':int(year),'kind':kind,'path':x['path'],'graphic_tag_matches':sum(points.values()),'tags':dict(points)})
        tags[year].update(points)
    write('recent_metadata_index.json',{'note':'标签仅用定位，不是官方频率；同题不同卷可能重复，不能据此推断难度或唯一解。','books':books,'year_tag_counts':{k:dict(v) for k,v in tags.items()}})
    pattern=re.compile('最大.{0,8}面|黑色.{0,12}对称|面.{0,15}线|去同|求异|叠加.{0,20}旋转|截面|三视图|俯视图')
    candidates=[];hits=[];ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for p in (PROJECT/'真题').rglob('*.docx'):
        name=p.name
        if not re.match(r'(202[1-6]|2[1-6]年)',name):continue
        if any(t in str(p) for t in ['自建试卷','申论','综合应用']):continue
        candidates.append(p)
    errors=[]
    for p in candidates:
        try:
            with ZipFile(p) as z:x=etree.fromstring(z.read('word/document.xml'))
            paras=[''.join(v.xpath('.//w:t/text()',namespaces=ns)) for v in x.xpath('//w:body/w:p',namespaces=ns)]
            found=[]
            for i,s in enumerate(paras):
                if pattern.search(s):found.append({'paragraph':i,'text':s,'previous':paras[max(0,i-2):i],'following':paras[i+1:i+3]})
            if found:hits.append({'path':p.relative_to(PROJECT).as_posix(),'text_matches':found,'visual_review':'not_done_by_scan'})
        except Exception as e:errors.append({'path':str(p),'error':str(e)})
    write('source_text_leads.json',{'candidate_documents_read':len(candidates),'matching_documents':len(hits),'entries':hits,'errors':errors})
    print({'metadata_books':len(books),'documents_text_read':len(candidates),'matching_documents':len(hits),'errors':len(errors)})
if __name__=='__main__':main()
