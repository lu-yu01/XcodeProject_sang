"""Replace figure media and add native Word view/frame captions without changing old text."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from hashlib import sha256
from copy import deepcopy
import json
from lxml import etree

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
SOURCE=PROJECT/'模式题'/'国考判断推理原创模拟卷（一）-35题（含答案解析）.docx'
OUTPUT=PROJECT/'模式题'/'国考判断推理原创模拟卷（一）-35题（图片规范版，含答案解析）.docx'
ORIGINAL=PROJECT/'.work'/'guokao35'/'assets'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def tag(n):return '{'+NS['w']+'}'+n
def sha(b):return sha256(b).hexdigest()
def native_caption(text):
    paragraph=etree.Element(tag('p'));properties=etree.SubElement(paragraph,tag('pPr'))
    etree.SubElement(properties,tag('pStyle')).set(tag('val'),'Small')
    etree.SubElement(properties,tag('keepNext'));etree.SubElement(properties,tag('keepLines'))
    run=etree.SubElement(paragraph,tag('r'));etree.SubElement(run,tag('t')).text=text
    return paragraph

def main():
    mapping={sha(p.read_bytes()):p.name for p in ORIGINAL.glob('*.png')}
    with ZipFile(SOURCE) as z:
        original={n:z.read(n) for n in z.namelist()}
    changed=dict(original)
    media=[]
    for n,data in original.items():
        if not n.startswith('word/media/'):continue
        name=mapping[sha(data)]
        replacement=(ROOT/'assets'/name).read_bytes()
        changed[n]=replacement
        media.append({'package_path':n,'source_asset':name,'old_sha256':sha(data),'new_sha256':sha(replacement),'changed':data!=replacement})
    assert len(media)==13 and sum(m['changed'] for m in media)==10
    doc=etree.fromstring(original['word/document.xml'])
    inline=next(i for i in doc.findall('.//wp:inline',NS) if i.find('wp:docPr',NS).get('descr','').startswith('q02：'))
    ext=inline.find('wp:extent',NS);old_cy=ext.get('cy');new_cy=str(round(int(old_cy)*900/840));ext.set('cy',new_cy)
    shape_ext=inline.find('.//a:xfrm/a:ext',NS);old_shape_cy=shape_ext.get('cy');shape_ext.set('cy',new_cy)
    p7=next(p for p in doc.findall('.//w:body/w:p',NS) if '若干个等大的小正方体逐层堆放' in ''.join(p.itertext()))
    view_note='上排左图为正视图，右图为右视图。'
    frame_note='为各图统一增设的最外层细框仅作排版，不参与规律判断。'
    p7.addnext(native_caption(view_note))
    section=next(p for p in doc.findall('.//w:body/w:p',NS) if ''.join(p.itertext())=='一、图形推理（第1—10题）')
    section.addnext(native_caption(frame_note))
    changed['word/document.xml']=etree.tostring(doc,encoding='UTF-8',xml_declaration=True,standalone=True)
    # Undo only the declared changes, then compare the complete XML canonically.
    check=deepcopy(doc)
    for note in (view_note,frame_note):
        cp=next(p for p in check.findall('.//w:body/w:p',NS) if ''.join(p.itertext())==note)
        cp.getparent().remove(cp)
    ci=next(i for i in check.findall('.//wp:inline',NS) if i.find('wp:docPr',NS).get('descr','').startswith('q02：'))
    ci.find('wp:extent',NS).set('cy',old_cy);ci.find('.//a:xfrm/a:ext',NS).set('cy',old_shape_cy)
    assert etree.tostring(check,method='c14n')==etree.tostring(etree.fromstring(original['word/document.xml']),method='c14n')
    assert changed['word/numbering.xml']==original['word/numbering.xml']
    OUTPUT.parent.mkdir(exist_ok=True)
    with ZipFile(OUTPUT,'w',ZIP_DEFLATED) as z:
        for n,data in changed.items():z.writestr(n,data)
    touched=[n for n in original if changed[n]!=original[n]]
    assert sorted(touched)==sorted(['word/document.xml']+[m['package_path'] for m in media if m['changed']])
    report={'status':'ready_for_render','source_word':str(SOURCE),'output_word':str(OUTPUT),'source_word_sha256':sha(SOURCE.read_bytes()),'output_word_sha256':sha(OUTPUT.read_bytes()),
            'changed_question_images':list(range(1,11)),'image_choice_questions':[1,2,3,4,5,6,7],'six_image_classification_questions':[8,9,10],
            'media':media,'embedded_images':13,'package_parts_changed':touched,
            'original_text_and_numbering_preserved':True,'numbering_xml_byte_identical':True,'all_other_document_xml_canonically_identical_after_undoing_declared_changes':True,
            'native_caption_added':{'question':7,'text':'上排左图为正视图，右图为右视图。','reason':'图内正视图/右视图说明移到图片外；前后方向已由原题干定义'},
            'frame_convention_added':{'location':'图形推理节标题之后','text':frame_note,'reason':'明确新增装饰框不计入面数、一笔画、对称等图形规律；Q10内层原方框仍为题目内容'},
            'text_replacements':{},
            'native_text_additions':[{'location':'图形推理节标题之后','text':frame_note},{'location':'第7题题干之后','text':view_note}],
            'removed_question_image_labels':['正视图','右视图','前','后'],
            'required_symbols_preserved':['问号','正方体面数字1—6','截面点P/Q/R','分类圈号①—⑥','选项A—D'],
            'per_question_changes':{
                '1':'题干六格连续外框；四候选统一大框，A—D在下方',
                '2':'九宫格连续外框；四候选整体下移60源像素并统一大框，A—D在下方；画布840→900，Word图片高度等比增加以保留实体物理比例',
                '3':'题干五格连续外框；四候选统一大框，A—D在下方',
                '4':'题干五格连续外框；四候选统一大框，A—D在下方',
                '5':'展开图与面内数字不变；四个立方体候选统一大框，A—D在下方',
                '6':'截面题立方体、点标PQR不变；四个截面候选统一大框，A—D在下方',
                '7':'图内视图和前后文字删除，必要视图顺序移至Word正文；四候选统一大框，A—D在下方',
                '8':'六幅分类题干各补等大独立方框，圈号移至框外；Word文字分组选项不变',
                '9':'六幅分类题干各补等大独立方框，圈号移至框外；Word文字分组选项不变',
                '10':'六幅分类题干各补等大独立方框，圈号移至框外；内层原正方框及分割线完整保留；新增图外总说明明确最外层装饰框不参与规律判断；Word文字分组选项不变'},
            'graphic_preservation_evidence':str(ROOT/'geometry_comparison.json'),'graphic_regions_pixel_identical':75,'explanation_images_byte_identical':3,
            'image_extent_change':{'question':2,'old_height_emu':old_cy,'new_height_emu':new_cy,'width_unchanged':True,'aspect_ratio_preserved':True},
            'question_answer_content_changed':False}
    (ROOT/'change_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(OUTPUT),'modified_images':10,'unchanged_explanations':3,'graphics_pixel_identical':75,'native_text_additions':2},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
