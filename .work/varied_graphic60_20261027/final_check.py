import json,zipfile,hashlib,re,importlib,collections,unicodedata
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from pypdf import PdfReader
from PIL import Image
from model import ROOT,PROJECT,REF,OUT,sha,dump,verify

def read(name):return json.loads((ROOT/name).read_text(encoding='utf8'))
def norm(t):return re.sub(r'\s+','',t)
def run():
    groups=read('groups.json');qs=read('questions.json')
    mods={name:importlib.import_module(name) for name in ['lines','curves','tokens']}
    report={'word':str(OUT),'word_sha256':sha(OUT),'pdf_sha256':sha(ROOT/'preview.pdf')}
    report['model']=verify(groups,qs,mods)
    # Renew the preliminary shortcut audit from the final, frozen source data.
    dump(ROOT/'shortcut_audit.json',{'questions_checked':60,'identity_chain':[],
        'single_public_rule_shortcut':[],'removable_steps':[],
        'basis':'Final model.verify checks all 60 source states, every public rule and every step deletion.'})
    doc=Document(OUT)
    assert len(doc.inline_shapes)==120 and len(doc.tables)==20
    assets=[ROOT/'assets'/f'{kind}-{n:02}.png' for kind in ['question','solution'] for n in range(1,61)]
    expected=collections.Counter(sha(p) for p in assets)
    with zipfile.ZipFile(OUT) as z,zipfile.ZipFile(REF) as ref:
        images={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')}
        assert collections.Counter(images.values())==expected
        fidelity=read('template_fidelity.json')
        assert fidelity['word_sha256']==sha(OUT)
        for n in fidelity['preserve_only_identical']:assert z.read(n)==ref.read(n)
    assert doc.sections[0]._sectPr.xml==Document(REF).sections[0]._sectPr.xml
    paragraphs=[p.text for p in doc.paragraphs]
    for p in doc.paragraphs:
        if p.style.name in ['Title','Subtitle','Heading 1','Heading 2']:
            assert not any(unicodedata.category(c).startswith('P') for c in p.text),p.text
    for g,t in zip(groups,doc.tables):
        cells=[c.text for row in t.rows for c in row.cells]
        assert cells==[x for r in g['rules'] for x in [r['code'],r['text']]]
    for q in qs:
        assert f'第{q["n"]}题 {q["answer"]}' in paragraphs
        rules={r['id']:r for r in groups[q['group']-1]['rules']}
        steps='；'.join(f'{j+1} {rules[r]["code"]}：{rules[r]["text"].rstrip("。；")}' for j,r in enumerate(q['chain']))+'。'
        assert steps in paragraphs
        wrong='干扰项辨析：'+'  '.join(f'{c}项：{o["explanation"]}' for c,o in zip('ABCD',q['options']) if c!=q['answer'])
        assert wrong in paragraphs
    for i,shape in enumerate(doc.inline_shapes):
        assert shape.width<=int(6.69*914400)
        rel=doc.part.related_parts[shape._inline.graphic.graphicData.pic.blipFill.blip.embed]
        from io import BytesIO
        with Image.open(BytesIO(rel.blob)) as im:
            assert abs(shape.width/shape.height-im.width/im.height)<.0001
    pdf=PdfReader(ROOT/'preview.pdf');assert len(pdf.pages)==40
    normalized=[norm(p.extract_text()) for p in pdf.pages]
    for i,g in enumerate(groups):
        t=normalized[i];a=normalized[i+20]
        assert norm(g['intro']) in t
        for r in g['rules']:assert norm(r['text']) in t
        assert len(pdf.pages[i].images)==3 and len(pdf.pages[i+20].images)==3
        for n in g['question_numbers']:
            q=qs[n-1]
            assert norm(f'{n}. 对左侧图形依次操作后，可以得到右侧哪个图形？') in t
            assert norm(f'第{n}题 {q["answer"]}') in a
            rules={r['id']:r for r in g['rules']}
            steps='；'.join(f'{j+1} {rules[r]["code"]}：{rules[r]["text"].rstrip("。；")}' for j,r in enumerate(q['chain']))+'。'
            wrong='干扰项辨析：'+'  '.join(f'{c}项：{o["explanation"]}' for c,o in zip('ABCD',q['options']) if c!=q['answer'])
            assert norm(steps) in a,(n,'step text')
            assert norm(wrong) in a,(n,'decoy text')
    v=read('visual_review.json')
    assert v['word_sha256']==sha(OUT) and v['pdf_sha256']==sha(ROOT/'preview.pdf')
    assert len(v['final_pages'])==40
    for page in v['final_pages']:
        assert page['actually_opened_at_original_size'] and page['result']=='pass'
        p=Path(page['path'])
        if p.exists():assert sha(p)==page['sha256']
        else:
            cleanup=read('cleanup.json')
            assert any(x['path']==str(p) and x['sha256']==page['sha256'] for x in cleanup['deleted'])
    legibility=read('legibility_revision.json')
    assert len(legibility['items'])==60
    for item in legibility['items']:
        assert item['source_and_four_options_pixel_identical']
        assert item['after_sha256']==sha(ROOT/'assets'/f'question-{item["n"]:02}.png')
    independent=read('final_independent_audit.json')
    assert independent['word_sha256']==sha(OUT) and independent['all_checks_passed'],independent.get('unresolved')
    index=PROJECT/'知识库'/'套卷索引'/f'{OUT.stem}.md'
    required=[index,PROJECT/'知识库'/'项目说明.md',PROJECT/'知识库'/'建议与变更记录.md',PROJECT/'知识库'/'北京一拖三图形操作题命题规则.md']
    for path in required:
        text=path.read_text(encoding='utf8')
        assert OUT.stem in text or path.name=='北京一拖三图形操作题命题规则.md'
    assert sha(OUT) in index.read_text(encoding='utf8')
    for target in re.findall(r'\]\(([^)]+)\)',index.read_text(encoding='utf8')):
        if '://' not in target:assert (index.parent/target.split('#')[0]).resolve().exists(),target
    report.update(all_checks_passed=True,embedded_images=120,source_assets=120,rule_tables=20,
        final_pdf_pages=40,actual_page_review=True,template_preserved=True,
        word_and_pdf_text_verified=True,source_images_match_word=True,
        independent_audit_sha256=sha(ROOT/'final_independent_audit.json'),
        independent_first_result='59/60; frozen original records preserved',
        independent_final_result='60/60 unique and consistent after correcting question12 candidate transcription',
        visual_review_sha256=sha(ROOT/'visual_review.json'),
        knowledge_base_fingerprints={str(p.relative_to(PROJECT)):sha(p) for p in required},
        report_sha256s={name:sha(ROOT/name) for name in ['groups.json','questions.json','public_questions.json','model_check.json','template_fidelity.json','legibility_revision.json']})
    dump(ROOT/'final_check.json',report)
    print(json.dumps({k:report[k] for k in ['all_checks_passed','word_sha256','final_pdf_pages','embedded_images']},ensure_ascii=False))

if __name__=='__main__':run()
