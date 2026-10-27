"""Read the final Word-exported PDF and render every page for actual visual QA."""
import argparse,re,sys
from zipfile import ZipFile
from lxml import etree
from pypdf import PdfReader
import pypdfium2 as pdfium
from batch_common import ROOT,PROJECT,CASES,digest,read,write

def compact(s):return re.sub(r'\s+','',s)

def main(key):
    case=CASES[key];folder=ROOT/key
    word=PROJECT/'模式题'/case['output'];original=PROJECT/'模式题'/case['source'];pdf=folder/'preview.pdf'
    assert word.exists() and pdf.exists() and pdf.stat().st_mtime>=word.stat().st_mtime
    baselines={r['key']:r for r in read(ROOT/'source_baselines.json')}
    changes=read(folder/'change_report.json')
    replacements=changes.get('text_replacements',{})
    assert isinstance(replacements,dict),'Expected an exact old-to-new wording map'
    assert digest(original)==baselines[key]['word_sha256'],'Original document changed during task'
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with ZipFile(original) as z:
        oldxml=etree.fromstring(z.read('word/document.xml'))
        oldparas=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in oldxml.xpath('//w:body/w:p',namespaces=ns)]
        old_numbering=z.read('word/numbering.xml')
    with ZipFile(word) as z:
        newdoc=z.read('word/document.xml');xml=etree.fromstring(newdoc)
        newparas=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in xml.xpath('//w:body/w:p',namespaces=ns)]
        assert old_numbering==z.read('word/numbering.xml'),'Word list numbering changed'
        newtext=compact(''.join(xml.xpath('//w:t/text()',namespaces=ns)))
        for p in oldparas:
            for old,new in replacements.items():p=p.replace(old,new)
            if compact(p):assert compact(p) in newtext,('Original paragraph lost',p[:80])
        media=[n for n in z.namelist() if n.startswith('word/media/')]
    textpages=[p.extract_text() or '' for p in PdfReader(pdf).pages]
    rendered_text=compact(''.join(textpages))
    for p in newparas:
        if compact(p):assert compact(p) in rendered_text,('Paragraph not rendered',p[:90])
    # Table cells (including the answer table) must also be present in the rendered text.
    for t in xml.xpath('//w:tbl//w:t/text()',namespaces=ns):
        if compact(t):assert compact(t) in rendered_text,('Table cell not rendered',t)
    out=folder/'render';out.mkdir(exist_ok=True)
    for p in out.glob('page-*.png'):
        assert p.resolve().parent==out.resolve() and not p.is_symlink();p.unlink()
    document=pdfium.PdfDocument(str(pdf));pages=[]
    for i in range(len(document)):
        p=out/f'page-{i+1:02}.png';document[i].render(scale=150/72).to_pil().convert('RGB').save(p)
        pages.append({'page':i+1,'path':str(p),'sha256':digest(p)})
    report={'passed':True,'key':key,'pages':len(pages),'question_count':case['questions'],'word':str(word),
            'word_sha256':digest(word),'pdf_sha256':digest(pdf),'embedded_images':len(media),
            'original_word_unchanged':True,'original_paragraphs_preserved':True,'numbering_xml_unchanged':True,
            'documented_direction_wording_replacements':replacements,
            'all_paragraphs_and_table_cells_rendered':True,'page_images':pages,'preview_png_status':'awaiting_visual_review'}
    write(folder/'render_verification.json',report)
    (folder/'render_text.txt').write_text('\n\n'.join(f'=== PAGE {i+1} ===\n{p}' for i,p in enumerate(textpages)),encoding='utf-8')
    print({k:v for k,v in report.items() if k!='page_images'})

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');p=argparse.ArgumentParser();p.add_argument('key',choices=CASES);main(p.parse_args().key)
