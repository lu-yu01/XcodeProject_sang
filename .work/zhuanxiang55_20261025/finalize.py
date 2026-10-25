"""Bind completed visual inspections to the final files and refresh the index."""
import json,sys
from suite_record import ROOT,DOCX,PDF,sha,read,write_record

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    v,r=read('verification.json'),read('render_verification.json')
    wh,ph=sha(DOCX),sha(PDF)
    assert v.get('passed') and r.get('passed')
    assert wh==v['word_sha256']==r['word_sha256']
    assert ph==r['pdf_sha256']
    assert PDF.stat().st_mtime_ns>=DOCX.stat().st_mtime_ns
    files=['visual_01_16.json','visual_17_24.json','visual_25_32.json']
    pages=[]
    for filename in files:
        item=read(filename);assert item.get('passed') and item['pdf_sha256']==ph
        if 'pages_reviewed' in item:pages.extend(item['pages_reviewed'])
        else:
            assert all(x['passed'] for x in item['pages'])
            pages.extend(x['page'] for x in item['pages'])
    assert sorted(pages)==list(range(1,r['pages']+1)),pages
    assert len(list((ROOT/'render').glob('page-*.png')))==r['pages']
    visual={'passed':True,'review_date':'2026-10-25','pdf_sha256':ph,'word_sha256':wh,
            'pages_reviewed':sorted(pages),'detail_reports':files,
            'horizontal_groups_verified':[5,6,7,8],
            'findings':'32页全部已实际查看；题干、图形、选项、答案表和解析可读，无裁切、重叠或缺页。',
            'scope':'代理交叉审稿与逐页视觉复核；教师盲审和学员试测未进行。'}
    (ROOT/'visual_review.json').write_text(json.dumps(visual,ensure_ascii=False,indent=2),encoding='utf-8')
    print(write_record())
    print(f'完成：{len(pages)}页，Word和PDF指纹及全部检查记录一致。')

if __name__=='__main__':main()
