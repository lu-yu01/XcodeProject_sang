"""Minimal picture-format revision: six explanatory-label edits, two native captions."""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
from copy import deepcopy
from datetime import datetime
import json,sys
from PIL import Image,ImageChops,ImageDraw
from lxml import etree
import graphics_b
import drawkit as k

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
OLD=PROJECT/'.work'/'zhuanxiang55_20261025'
SOURCE=PROJECT/'模式题'/'国考图形与逻辑专项练习-55题（含答案解析）.docx'
OUTPUT=PROJECT/'模式题'/'国考图形与逻辑专项练习-55题（图片规范版，含答案解析）.docx'
CHANGED=[14,17,18,19,20,21]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
qn=lambda local:'{'+NS['w']+'}'+local
sha=lambda data:sha256(data).hexdigest()
CAPTIONS={18:'题干三图从左到右依次为正视图、右视图、俯视占位图。',
          19:'题干三图从左到右依次为第1、第2、第3层，各小图上方均为前方。'}
REMOVALS={14:['相对（四处）'],17:['原纸','左半向右折','下半向上折后剪去灰格'],
18:['正视图','右视图','俯视占位图'],19:['第1层','第2层','第3层','前（三处）'],
20:['部件（两处前缀；甲、乙保留）'],21:['原纸','右半向左折','上半向下折','沿斜线再对折']}
MASKS={14:[(200,705,1600,755)],17:[(200,350,1730,420)],18:[(300,350,1550,420)],
19:[(200,50,1600,110),(200,340,1600,415)],20:[(500,345,1300,420)],21:[(150,350,1730,420)]}

def caption(text):
    p=etree.Element(qn('p'));pr=etree.SubElement(p,qn('pPr'))
    etree.SubElement(pr,qn('pStyle')).set(qn('val'),'Small')
    etree.SubElement(pr,qn('keepNext'));etree.SubElement(pr,qn('keepLines'))
    run=etree.SubElement(p,qn('r'));etree.SubElement(run,qn('t')).text=text
    return p

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    source_bytes=SOURCE.read_bytes()
    for n in CHANGED:getattr(graphics_b,f'draw{n}')()
    comparisons=[]
    for n in range(1,31):
        old=Image.open(OLD/'assets'/f'q{n:02}.png').convert('RGB')
        new=Image.open(ROOT/'assets'/f'q{n:02}.png').convert('RGB')
        assert old.size==new.size
        diff=ImageChops.difference(old,new)
        box=diff.getbbox()
        if n not in CHANGED:assert box is None,(n,'unexpected image change')
        else:
            assert box is not None
            allowed=Image.new('1',old.size,0);d=ImageDraw.Draw(allowed)
            for rect in MASKS[n]:d.rectangle(rect,fill=1)
            outside=diff.copy();outside.paste((0,0,0),(0,0),allowed)
            assert outside.getbbox() is None,(n,'geometry changed outside text bands',outside.getbbox())
        comparisons.append({'n':n,'changed':box is not None,'difference_bbox':box,
                            'only_text_regions_changed':True,'source_png_sha256':sha((OLD/'assets'/f'q{n:02}.png').read_bytes()),
                            'new_png_sha256':sha((ROOT/'assets'/f'q{n:02}.png').read_bytes()),
                            'removed_text':REMOVALS.get(n,[]),'native_caption_added':CAPTIONS.get(n)})
    source_hashes={sha((OLD/'assets'/f'q{n:02}.png').read_bytes()):n for n in range(1,31)}
    replacements={};media_by_question={}
    with ZipFile(SOURCE) as z:
        for name in z.namelist():
            if not name.startswith('word/media/'):continue
            n=source_hashes.get(sha(z.read(name)))
            assert n is not None,('unrecognized embedded media',name)
            media_by_question[n]=name
            if n in CHANGED:replacements[name]=(ROOT/'assets'/f'q{n:02}.png').read_bytes()
        assert len(media_by_question)==30
        original_xml=z.read('word/document.xml');doc=etree.fromstring(original_xml)
        original_c14n=etree.tostring(doc,method='c14n')
        rel=etree.fromstring(z.read('word/_rels/document.xml.rels'))
        relationships={r.get('Id'):'word/'+r.get('Target') for r in rel if r.get('Type','').endswith('/image')}
        added=[]
        for n,text in CAPTIONS.items():
            rid=next(key for key,value in relationships.items() if value==media_by_question[n])
            found=doc.xpath('.//a:blip[@r:embed=$rid]',namespaces=NS,rid=rid)
            assert len(found)==1
            node=found[0]
            while node.tag!=qn('p'):node=node.getparent()
            new_para=caption(text);node.addprevious(new_para);added.append(new_para)
        verify_doc=deepcopy(doc)
        for p in verify_doc.xpath('.//w:p',namespaces=NS):
            if ''.join(p.itertext()) in CAPTIONS.values():p.getparent().remove(p)
        assert etree.tostring(verify_doc,method='c14n')==original_c14n,'original Word text/formatting changed'
        replacements['word/document.xml']=etree.tostring(doc,encoding='UTF-8',xml_declaration=True,standalone=True)
        with ZipFile(OUTPUT,'w') as out:
            for info in z.infolist():out.writestr(info,replacements.get(info.filename,z.read(info.filename)))
    assert SOURCE.read_bytes()==source_bytes
    with ZipFile(SOURCE) as a,ZipFile(OUTPUT) as b:
        differences=[name for name in a.namelist() if a.read(name)!=b.read(name)]
        assert set(differences)==set(replacements)
        assert a.read('word/numbering.xml')==b.read('word/numbering.xml')
        assert len([name for name in b.namelist() if name.startswith('word/media/')])==30
    layouts=json.loads((OLD/'figure_layout.json').read_text(encoding='utf-8'))
    layouts.update({str(n):v for n,v in k.LAYOUTS.items()})
    (ROOT/'figure_layout.json').write_text(json.dumps(layouts,ensure_ascii=False,indent=2),encoding='utf-8')
    report={'status':'content_and_image_checks_passed_waiting_render','time':datetime.now().astimezone().isoformat(),
            'source_word':str(SOURCE),'output_word':str(OUTPUT),'source_sha256':sha(source_bytes),'output_sha256':sha(OUTPUT.read_bytes()),
            'question_count':55,'image_count':30,'changed_question_images':CHANGED,
            'unchanged_question_images':[n for n in range(1,31) if n not in CHANGED],
            'native_captions_added':CAPTIONS,'original_word_xml_preserved_except_two_caption_paragraphs':True,
            'numbering_xml_identical':True,'all_other_zip_members_identical':True,'changed_zip_members':differences,
            'no_shape_pixels_changed_outside_exact_text_bands':True,
            'four_option_form':'Questions 1-21 already use a single four-cell horizontal outer frame with A-D underneath; preserved.',
            'classification_form':'Questions 22-30 keep six separate source figures and original native text choices; preserved.',
            'two_group_form':'Questions 5-8 remain on one horizontal baseline; source figure pixels unchanged.',
            'preserved_essential_data':['question marks','cube face digits','section point labels','circles 1-6','Q18 numeric answer values','Q20 part identifiers 甲/乙'],
            'per_question':comparisons,'media_by_question':media_by_question}
    (ROOT/'change_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','output_word','changed_question_images','native_captions_added','output_sha256']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
