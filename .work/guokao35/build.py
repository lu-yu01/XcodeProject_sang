"""Create the teacher's requested DOCX, preserving a test-first / answers-last workflow."""
from pathlib import Path
import json
import re
import sys
from collections import Counter
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image
from content import TITLE, SUBTITLE, INTRO, NOTICE, QUESTIONS, COMMON
import figures

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parents[1] / '模式题' / '国考判断推理原创模拟卷（一）-35题（含答案解析）.docx'

# Base: compact_reference_guide. Named overrides for Chinese printed exams:
# A4; margins 20 mm; SimSun 11pt / 1.25 lines; grayscale heading palette;
# short centered title; options 2pt after; 22pt gap between question blocks.
TOKENS = dict(page_mm=(210,297), margin_mm=20, content_width_dxa=9638,
              header_mm=9, footer_mm=10, body_font='宋体', latin_font='Calibri',
              body_size=11, body_line=1.25, body_after=6,
              h1=(16,18,10), h2=(13,14,7), h3=(12,10,5),
              question_before=9, question_after=4, option_after=2,
              title_size=21, title_before=0, title_after=5,
              table_margins=dict(top=80,bottom=80,start=100,end=100))


def set_style(style, size=11, bold=False, before=0, after=6, line=1.25, east='宋体'):
    style.font.name='Calibri'
    style.font.size=Pt(size)
    style.font.bold=bold
    style.font.italic=False
    style.font.color.rgb=RGBColor(0,0,0)
    rf=style.element.get_or_add_rPr().get_or_add_rFonts()
    for key,value in [('ascii','Calibri'),('hAnsi','Calibri'),('eastAsia',east)]:rf.set(qn('w:'+key),value)
    p=style.paragraph_format
    p.space_before=Pt(before);p.space_after=Pt(after);p.line_spacing=line
    p.widow_control=True
    pPr=style.element.get_or_add_pPr()
    sg=OxmlElement('w:snapToGrid');sg.set(qn('w:val'),'0');pPr.append(sg)


class Numbers:
    def __init__(self,doc):
        self.root=doc.part.numbering_part.element
        self.abs=max([int(e.get(qn('w:abstractNumId'))) for e in self.root if e.tag==qn('w:abstractNum')]+[0])+1
        self.num=max([int(e.get(qn('w:numId'))) for e in self.root if e.tag==qn('w:num')]+[0])+1
    def make(self, fmt='decimal', label='%1.', left=0, hang=0, start=1):
        aid=self.abs;self.abs+=1;nid=self.num;self.num+=1
        a=OxmlElement('w:abstractNum');a.set(qn('w:abstractNumId'),str(aid))
        nsid=OxmlElement('w:nsid');nsid.set(qn('w:val'),f'{0xA5000000+aid:08X}');a.append(nsid)
        multi=OxmlElement('w:multiLevelType');multi.set(qn('w:val'),'singleLevel');a.append(multi)
        lvl=OxmlElement('w:lvl');lvl.set(qn('w:ilvl'),'0')
        for tag,val in [('start',str(start)),('numFmt',fmt),('suff','space'),('lvlText',label),('lvlJc','left')]:
            e=OxmlElement('w:'+tag);e.set(qn('w:val'),val);lvl.append(e)
        pr=OxmlElement('w:pPr');ind=OxmlElement('w:ind')
        ind.set(qn('w:left'),str(left));ind.set(qn('w:hanging'),str(hang));pr.append(ind)
        lvl.append(pr);a.append(lvl)
        # OOXML requires all abstractNum elements BEFORE all num instances.
        first_num=next((e for e in self.root if e.tag==qn('w:num')),None)
        if first_num is None:self.root.append(a)
        else:first_num.addprevious(a)
        n=OxmlElement('w:num');n.set(qn('w:numId'),str(nid));x=OxmlElement('w:abstractNumId');x.set(qn('w:val'),str(aid));n.append(x);self.root.append(n)
        return nid
    def apply(self,p,nid):
        np=OxmlElement('w:numPr')
        for tag,val in [('ilvl','0'),('numId',str(nid))]:
            e=OxmlElement('w:'+tag);e.set(qn('w:val'),val);np.append(e)
        p._p.get_or_add_pPr().append(np)


def keep_block(paras):
    for p in paras[:-1]:
        p.paragraph_format.keep_with_next=True
        p.paragraph_format.keep_together=True
    if paras:
        paras[-1].paragraph_format.keep_with_next=False
        paras[-1].paragraph_format.keep_together=True


def field(p,code):
    run=p.add_run()
    for typ,txt in [('begin',None),(None,code),('end',None)]:
        if typ:
            el=OxmlElement('w:fldChar');el.set(qn('w:fldCharType'),typ)
        else:
            el=OxmlElement('w:instrText');el.set(qn('xml:space'),'preserve');el.text=txt
        run._r.append(el)


def picture(doc,path,question=True,max_width=6.6):
    p=doc.add_paragraph(style='Figure')
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    with Image.open(path) as im:w,h=im.size
    # Compact diagrams remain legible at 250+ pixels/inch. q02 is taller.
    max_height=3.5 if path.name=='q02.png' else (2.95 if question else 2.05)
    width=min(max_width, max_height*w/h)
    run=p.add_run();inline=run.add_picture(str(path),width=Inches(width))
    inline._inline.docPr.set('descr', f'{path.stem}：'+('题目图及选项' if question else '解析辅助图'))
    return p


def answer_table(doc):
    # Repeated records genuinely tabular: one record per question.
    t=doc.add_table(rows=8,cols=10)
    t.autofit=False
    t.style='Table Grid'
    width=9640;col=964
    pr=t._tbl.tblPr
    tw=pr.find(qn('w:tblW'));tw.set(qn('w:type'),'dxa');tw.set(qn('w:w'),str(width))
    ind=OxmlElement('w:tblInd');ind.set(qn('w:w'),'100');ind.set(qn('w:type'),'dxa');pr.append(ind)
    mar=OxmlElement('w:tblCellMar')
    for side,v in TOKENS['table_margins'].items():
        e=OxmlElement('w:'+side);e.set(qn('w:w'),str(v));e.set(qn('w:type'),'dxa');mar.append(e)
    pr.append(mar)
    for child in list(t._tbl.tblGrid):t._tbl.tblGrid.remove(child)
    for _ in range(10):
        e=OxmlElement('w:gridCol');e.set(qn('w:w'),str(col));t._tbl.tblGrid.append(e)
    for r,row in enumerate(t.rows):
        for c,cell in enumerate(row.cells):
            cell.width=Inches(col/1440)
            tcW=cell._tc.get_or_add_tcPr().find(qn('w:tcW'));tcW.set(qn('w:w'),str(col));tcW.set(qn('w:type'),'dxa')
            if r==0:value='题号' if c%2==0 else '答案'
            else:
                n=(c//2)*7+r
                value=str(n) if c%2==0 else QUESTIONS[n-1]['answer']
            p=cell.paragraphs[0];p.style=doc.styles['AnswerTable'];p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.add_run(value).bold=r==0 or c%2==1
            if r==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EEEEEE');cell._tc.get_or_add_tcPr().append(sh)
            va=OxmlElement('w:vAlign');va.set(qn('w:val'),'center');cell._tc.get_or_add_tcPr().append(va)
    hdr=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(hdr)
    for row in t.rows:
        cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    assert len(QUESTIONS)==35
    assert [q['n'] for q in QUESTIONS]==list(range(1,36))
    figures.main()
    doc=Document()
    for border in list(doc.styles.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
    from docx.shared import Mm
    sec=doc.sections[0]
    sec.page_width=Mm(210);sec.page_height=Mm(297)
    sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Mm(20)
    sec.header_distance=Mm(9);sec.footer_distance=Mm(10)
    doc.core_properties.title=TITLE
    doc.core_properties.subject='原创国考风格判断推理练习；35题；附答案与解析'
    doc.core_properties.author='教研资料'
    doc.core_properties.keywords='图形推理,定义判断,类比推理,逻辑判断,原创模拟卷'
    set_style(doc.styles['Normal'])
    for name,size,before,after in [('Heading 1',16,18,10),('Heading 2',13,14,7),('Heading 3',12,10,5)]:
        set_style(doc.styles[name],size,True,before,after,east='黑体')
        doc.styles[name].paragraph_format.keep_with_next=True
    set_style(doc.styles['Title'],21,True,0,5,1.1,'黑体')
    set_style(doc.styles['Subtitle'],10.5,False,0,5,1.15)
    for name,params in {
        'Question':dict(size=11,before=9,after=4),
        'Ask':dict(size=11,before=0,after=3),
        'Option':dict(size=11,before=0,after=2),
        'Figure':dict(size=1,before=2,after=4,line=1),
        'AnswerTitle':dict(size=11.5,bold=True,before=10,after=4,east='黑体'),
        'Analysis':dict(size=10.5,before=0,after=4,line=1.25),
        'AnalysisCompact':dict(size=10.5,before=0,after=3,line=1.1),
        'Point':dict(size=10,bold=True,before=0,after=3),
        'Small':dict(size=9,before=0,after=5,line=1.2),
        'AnswerTable':dict(size=10,before=0,after=1,line=1.1),
        'Common':dict(size=10.5,before=0,after=3,line=1.2),
    }.items():
        st=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH);st.base_style=doc.styles['Normal'];set_style(st,**params)
    doc.styles['AnswerTitle'].paragraph_format.keep_with_next=True
    doc.styles['Point'].paragraph_format.keep_with_next=True
    for s in ('Header','Footer'):
        set_style(doc.styles[s],8.5,False,0,0,1.0)
        doc.styles[s].font.color.rgb=RGBColor.from_string('666666')
    head=sec.header.paragraphs[0]
    head.text=TITLE+'　｜　判断推理专项'
    foot=sec.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
    foot.add_run('第 ');field(foot,' PAGE ');foot.add_run(' 页')
    nums=Numbers(doc)
    qid=nums.make(left=300,hang=300)
    aid=nums.make(left=300,hang=300)
    p=doc.add_paragraph(TITLE,'Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p=doc.add_paragraph('题目册 · 35题','Subtitle');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p=doc.add_paragraph(INTRO,'Small')
    p=doc.add_paragraph('图形推理10题　定义判断10题　类比推理5题　逻辑判断10题','Small')
    p=doc.add_paragraph('姓名：________________　日期：________________　得分：________','Small')
    doc.add_paragraph(NOTICE,'Small')
    headings={1:'一、图形推理（第1—10题）',11:'二、定义判断（第11—20题）',21:'三、类比推理（第21—25题）',26:'四、逻辑判断（第26—35题）'}
    for q in QUESTIONS:
        n=q['n']
        if n in headings:
            if n!=1:doc.add_page_break()
            h=doc.add_paragraph(headings[n],'Heading 1')
        if n==31:
            doc.add_page_break()
            group=[]
            cnum=nums.make(label='（%1）',left=360,hang=360)
            for i,s in enumerate(COMMON):
                p=doc.add_paragraph(re.sub(r'^（\d）','',s) if 2<=i<=5 else s,'Common')
                if i==0:p.runs[0].bold=True
                if 2<=i<=5:nums.apply(p,cnum)
                group.append(p)
            for p in group:p.paragraph_format.keep_with_next=True
        block=[]
        p=doc.add_paragraph(q['stem'],'Question');nums.apply(p,qid);block.append(p)
        if q['ask']:block.append(doc.add_paragraph(q['ask'],'Ask'))
        if q['image']:block.append(picture(doc,figures.ASSETS/q['image']))
        if q['options']:
            opt=nums.make('upperLetter',left=500,hang=300)
            for s in q['options']:
                p=doc.add_paragraph(s,'Option');nums.apply(p,opt);block.append(p)
        keep_block(block)
    doc.add_page_break()
    p=doc.add_paragraph('参考答案与解析','Title');p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('答案速查','Heading 2')
    answer_table(doc)
    for q in QUESTIONS:
        block=[]
        p=doc.add_paragraph('答案：'+q['answer'],'AnswerTitle');nums.apply(p,aid);block.append(p)
        if q['n']>=30:p.paragraph_format.space_before=Pt(6)
        p=doc.add_paragraph('考点：'+q['point'],'Point');block.append(p)
        for i,s in enumerate(q['analysis']):
            p=doc.add_paragraph(('解析：' if i==0 else '')+s,'AnalysisCompact' if q['n']>=30 else 'Analysis');block.append(p)
        if q['explanation_image']:
            block.append(picture(doc,figures.ASSETS/q['explanation_image'],False,max_width=6.2))
        keep_block(block)
    OUTPUT.parent.mkdir(exist_ok=True)
    doc.save(OUTPUT)
    meta={'file':str(OUTPUT),'questions':len(QUESTIONS),'categories':dict(Counter(q['category'] for q in QUESTIONS)),
          'answers':dict(Counter(q['answer'] for q in QUESTIONS)),'inline_images':len(doc.inline_shapes),'style_tokens':TOKENS}
    (ROOT/'build_info.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(meta,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
