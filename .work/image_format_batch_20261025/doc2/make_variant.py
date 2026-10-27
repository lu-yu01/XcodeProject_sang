"""Apply image layout changes while retaining the original DOCX package contents."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from hashlib import sha256
from PIL import Image,ImageChops
from lxml import etree
import importlib.util,json,shutil,sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
SOURCE=PROJECT/'.work/guokao2026_2'
OLD_DOC=PROJECT/'模式题/国考判断推理原创模拟卷（二）-2026行政执法-35题（含答案解析）.docx'
NEW_DOC=PROJECT/'模式题/国考判断推理原创模拟卷（二）-2026行政执法-35题（图片规范版，含答案解析）.docx'

TEXT_REPLACEMENTS={
    '下图分为上下两组。':'下图分为左右两组。',
    '先看上组：':'先看第一组：',
    '用于下组：':'用于第二组：',
    '下组第二格':'第二组第二格',
    '下组第一格':'第二组第一格',
    '正视图从左到右、右视图从前到后如图；':'左侧正视图从左到右、右侧右视图从前到后；',
}

def digest(p):return sha256(p.read_bytes()).hexdigest()
def strict_replace(s,old,new):
    assert s.count(old)==1,(old,s.count(old))
    return s.replace(old,new)

def region(im,box):return im.crop(box).convert('RGB')

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    for name in ['figures.py','q7_design.py','content.py','verbal_draft.py','logic_draft.py']:
        shutil.copy2(SOURCE/name,ROOT/name)
    p=ROOT/'figures.py';s=p.read_text(encoding='utf-8')
    old='''    grid = outer_matrix(d, (75,45,1725,625), 2,3)
    for center,state in zip(grid[0],[Q2_TOP,Q2_TOP_B,Q2_TOP_C]):
        motif(d,*center,state)
    for center,state in zip(grid[1][:2],[Q2_BOTTOM,Q2_BOTTOM_B]):
        motif(d,*center,state)
    label(d,*grid[1][2],"?",105)'''
    new='''    left=outer_row(d,(75,145,855,525),3)
    right=outer_row(d,(945,145,1725,525),3)
    for center,state in zip(left,[Q2_TOP,Q2_TOP_B,Q2_TOP_C]):
        motif(d,*center,state)
    for center,state in zip(right[:2],[Q2_BOTTOM,Q2_BOTTOM_B]):
        motif(d,*center,state)
    label(d,*right[2],"?",105)'''
    s=strict_replace(s,old,new)
    old='''    grid=outer_matrix(d,(75,45,1725,625),2,3)
    for center,edges in zip(grid[0]+grid[1][:2],Q3_NETWORKS):
        network_picture(d,*center,edges,51)
    label(d,*grid[1][2],"?",105)'''
    new='''    left=outer_row(d,(75,145,855,525),3)
    right=outer_row(d,(945,145,1725,525),3)
    for center,edges in zip(left+right[:2],Q3_NETWORKS):
        network_picture(d,*center,edges,51)
    label(d,*right[2],"?",105)'''
    s=strict_replace(s,old,new)
    s=strict_replace(s,'    label(d,1260,250,"P、Q、R确定一个截平面",36)\n','')
    s=strict_replace(s,'    label(d,centers[0][0],378,"正视图",38)\n','')
    s=strict_replace(s,'    label(d,centers[1][0],378,"右视图",38)\n','')
    p.write_text(s,encoding='utf-8')
    p=ROOT/'content.py';s=p.read_text(encoding='utf-8')
    for old,new in TEXT_REPLACEMENTS.items():s=s.replace(old,new)
    p.write_text(s,encoding='utf-8')
    sys.path.insert(0,str(ROOT));import figures
    figures.draw_all()
    report={'source_word':str(OLD_DOC),'output_word':str(NEW_DOC),'source_word_sha256':digest(OLD_DOC),
            'changed_questions':[2,3,5,7],'retained_questions':[1,4,6,8,9,10],
            'text_replacements':TEXT_REPLACEMENTS,'inserted_captions':[],
            'details':{
                '2':'上下两组三图改为左右同一横排两组三格；原五图及问号、四候选内容顺序和尺寸不变。',
                '3':'上下两组线网改为同一横排两组三格；原五图及问号、四候选内容顺序和尺寸不变。',
                '5':'删除图内冗余“P、Q、R确定一个截平面”；P/Q/R几何点标签和图形保留。',
                '7':'删除图内正视图/右视图说明；原生题干改为左侧正视图/右侧右视图，信息移到图外。',
                'other':'其余四候选本已共用横向四格大框、A-D在框外下方，保留原样；六图分类8-10保持六图和Word分组选项。'},
            'pixel_checks':[],'source_image_hashes':{},'new_image_hashes':{}}
    for n in range(1,11):
        name=f'q{n:02}.png';old=SOURCE/'assets'/name;new=ROOT/'assets'/name
        report['source_image_hashes'][name]=digest(old);report['new_image_hashes'][name]=digest(new)
        a=Image.open(old).convert('RGB');b=Image.open(new).convert('RGB');assert a.size==b.size
        if n not in report['changed_questions']:
            assert digest(old)==digest(new),(n,'unchanged image differs')
            report['pixel_checks'].append({'n':n,'scope':'whole image','pixel_identical':True})
        if n in (2,3):
            old_centers=[(350,190),(900,190),(1450,190),(350,480),(900,480)]
            new_centers=[(205,335),(465,335),(725,335),(1075,335),(1335,335)]
            radius=100 if n==2 else 120
            for i,((ox,oy),(nx,ny)) in enumerate(zip(old_centers,new_centers)):
                aa=region(a,(ox-radius,oy-radius,ox+radius,oy+radius));bb=region(b,(nx-radius,ny-radius,nx+radius,ny+radius))
                assert ImageChops.difference(aa,bb).getbbox() is None,(n,i,'translated graphic differs')
            assert ImageChops.difference(region(a,(0,700,1800,1100)),region(b,(0,700,1800,1100))).getbbox() is None
            report['pixel_checks'].append({'n':n,'scope':'5 stem figures under integer translation + entire options area','pixel_identical':True})
        if n==5:
            for box in [(500,45,1045,480),(0,535,1800,960)]:
                assert ImageChops.difference(region(a,box),region(b,box)).getbbox() is None
            report['pixel_checks'].append({'n':n,'scope':'solid, PQR labels and entire option row','pixel_identical':True})
        if n==7:
            for box in [(390,95,640,345),(1160,95,1410,345),(0,480,1800,950)]:
                assert ImageChops.difference(region(a,box),region(b,box)).getbbox() is None
            report['pixel_checks'].append({'n':n,'scope':'2 elevations and entire option row','pixel_identical':True})
    with ZipFile(OLD_DOC) as z:parts={name:z.read(name) for name in z.namelist()}
    image_by_sha={sha256(value).hexdigest():name for name,value in parts.items() if name.startswith('word/media/')}
    bindings=[]
    for n in report['changed_questions']:
        name=f'q{n:02}.png';part=image_by_sha[report['source_image_hashes'][name]]
        parts[part]=(ROOT/'assets'/name).read_bytes();bindings.append({'n':n,'part':part,'source_asset':str(SOURCE/'assets'/name),'new_asset':str(ROOT/'assets'/name)})
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    original=etree.fromstring(parts['word/document.xml']);xml=etree.fromstring(parts['word/document.xml'])
    seen={k:0 for k in TEXT_REPLACEMENTS}
    for text in xml.findall('.//w:t',ns):
        value=text.text or ''
        for old,new in TEXT_REPLACEMENTS.items():
            seen[old]+=value.count(old);value=value.replace(old,new)
        text.text=value
    assert all(count>0 for count in seen.values()),seen
    parts['word/document.xml']=etree.tostring(xml,encoding='UTF-8',xml_declaration=True,standalone=True)
    new_texts=[t.text or '' for t in xml.findall('.//w:t',ns)]
    expected=[]
    for t in original.findall('.//w:t',ns):
        value=t.text or ''
        for old,new in TEXT_REPLACEMENTS.items():value=value.replace(old,new)
        expected.append(value)
    assert new_texts==expected
    with ZipFile(NEW_DOC,'w',ZIP_DEFLATED) as z:
        for name,value in parts.items():z.writestr(name,value)
    with ZipFile(OLD_DOC) as old,ZipFile(NEW_DOC) as new:
        changed=[name for name in old.namelist() if old.read(name)!=new.read(name)]
        assert set(changed)=={'word/document.xml',*[b['part'] for b in bindings]},changed
        assert old.read('word/numbering.xml')==new.read('word/numbering.xml')
    report.update({'passed':True,'image_bindings':bindings,'text_replacement_occurrences':seen,
                   'native_paragraph_count_unchanged':True,'word_text_only_whitelisted_replacements':True,
                   'automatic_numbering_xml_unchanged':True,'all_other_package_parts_unchanged':True,
                   'changed_package_parts':changed,'output_word_sha256':digest(NEW_DOC),
                   'new_image_format':{'choices':'one outer frame + 3 dividers + A-D below','two_group_stems':'3 + 3 in same horizontal row'},
                   'limitations':'Q2/Q3 figures changed absolute position only; compared in local coordinates to prove exact pixels unchanged. Geometry, color, option order and mathematical models unchanged.'})
    (ROOT/'change_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':True,'output_word':str(NEW_DOC),'changed_questions':report['changed_questions'],'text_replacement_occurrences':seen},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
