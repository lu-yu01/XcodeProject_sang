"""Bind final checks, record historical visual review and clean temporary page PNGs."""
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile
import hashlib,json
from build import ROOT,PROJECT,DOCX,MD,sha

def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def write(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    model=read('verification.json');ind=read('independent_review.json');render=read('render_verification.json')
    assert model['status']=='passed' and ind['passed_math'] and ind['passed_semantics']
    assert model['model_sha256']==ind['puzzles_sha256']==sha(ROOT/'puzzles.py')
    assert render['passed'] and render['pages']==15
    assert render['word_sha256']==sha(DOCX)
    assert render['pdf_sha256']==sha(ROOT/'preview.pdf')
    assert read('build_info.json')['word_sha256']==sha(DOCX)
    reviews=[read('visual_01_10.json'),read('visual_11_15.json')]
    assert all(v['passed'] and v['pdf_sha256']==render['pdf_sha256'] for v in reviews)
    pages=[p for v in reviews for p in v['pages_reviewed']]
    assert sorted(pages)==list(range(1,16)) and len(set(pages))==15
    image_paths=[ROOT/'assets'/f'q{n:02}{suffix}.png' for n in range(1,11) for suffix in ('','_solution')]
    assert len(list((ROOT/'assets').glob('*.png')))==20
    with ZipFile(DOCX) as z:
        embedded=[hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')]
    assert sorted(embedded)==sorted(sha(p) for p in image_paths)
    now=datetime.now().astimezone().isoformat()
    review={'passed':True,'time':now,'pdf_sha256':render['pdf_sha256'],'word_sha256':render['word_sha256'],
            'pages_reviewed':sorted(pages),'review_records':['visual_01_10.json','visual_11_15.json'],
            'status':'completed_before_cleanup','note':'历史逐页检查绑定未修改的最终PDF；检查完成后按用户偏好清理页面PNG。'}
    write('visual_review.json',review)
    targets=[]
    render_dir=(ROOT/'render').resolve()
    assert render_dir.is_relative_to(PROJECT.resolve())
    assert len(list(render_dir.glob('*.png')))==15
    for row in render['page_images']:
        p=Path(row['path'])
        assert p.resolve().parent==render_dir and not p.is_symlink()
        assert p.name==f'page-{row["page"]:02}.png' and sha(p)==row['sha256']
        targets.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
    protected=image_paths+list((ROOT/'reference').glob('*.png'))+[DOCX,ROOT/'preview.pdf']
    protected=[{'path':str(p),'sha256':sha(p)} for p in protected]
    cleanup={'status':'planned','time':now,'files':targets,'deleted_count':len(targets),'deleted_bytes':sum(p['bytes'] for p in targets),
             'protected_files':protected}
    write('preview_cleanup.json',cleanup)
    for row in targets:Path(row['path']).unlink()
    assert all(not Path(row['path']).exists() for row in targets)
    assert all(sha(Path(row['path']))==row['sha256'] for row in protected)
    cleanup['status']='completed';cleanup['protected_hashes_unchanged']=True
    write('preview_cleanup.json',cleanup)
    render['preview_png_status']='cleaned_after_completed_visual_review'
    write('render_verification.json',render)
    text=f'''# 立体拼合专项练习10题 索引与检查记录

## 套卷索引

- Word成品：[立体拼合专项练习10题](../../模式题/立体拼合专项练习-10题（含答案解析）.docx)。
- 源稿及构建目录：[assembly10_20261025](../../.work/assembly10_20261025/)。
- 题量：10道原创单选题；补块5题、给部件选拼合结果5题，其中第8、10题为选非。题目在前，答案与逐题分层拼合解析在后。
- 参考：2016—2025年范围内9个已核对案例，涵盖省考、事业单位及联考；见[跨考试依据与命题规则](../立体拼合题命题与检查规则.md)。本专项不采用某单一考试的题量配额。
- 难度为命题估计：中等6题、较难4题；未进行独立教师盲审或学员试测。
- Word版本指纹：`{render['word_sha256']}`。

## 生成后检查

- 记录时间：{now}。
- 数学与语义检查：通过；24种正旋转与全部目标内平移，逐项验证40个选项的可拼性；另复算余部连通、分岔、镜像、直臂、支链长度和最小重叠等解析依据。[报告](../../.work/assembly10_20261025/verification.json)。
- 独立复核：通过；另一实现用四分之一转闭包与锚点平移搜索复核40项、构造、面连通、同体积及选项不旋转等价；解析修正后逐题审读通过。[报告](../../.work/assembly10_20261025/independent_review.json)。
- 文件绑定与实际渲染：通过；10个题号、10个答案题号、20张内嵌图，全部题干与解析在PDF中完整对应；最终15页，前10页每页一题。[报告](../../.work/assembly10_20261025/render_verification.json)。
- 逐页视觉检查：通过；最终第1—15页均已实际查看，未见缺图、裁切、重叠或题干与选项拆页。[记录](../../.work/assembly10_20261025/visual_review.json)。
- 本次落实修正：第3题甲为带分岔部件，乙为折链；第8、10题仅展示一个可拼项构造，注明对应字母；各图框统一标总块数补足遮挡识别；加大分层图说明与网格间距，并放大题图视角标注。全部重新导出与检查。
- PDF版本指纹：`{render['pdf_sha256']}`。
- 渲染方式：常规渲染器在本机缺少LibreOffice，诊断后使用独立、只读、禁宏的Word实例导出PDF，再用页面渲染逐页检查。

## 预览清理与再次检查

按用户清理偏好，逐页检查完成后已删除15张临时页面PNG；保留10张题图、10张分层解析图、6张必要参考图、Word、PDF及检查历史，保留文件指纹未变化。[清理清单](../../.work/assembly10_20261025/preview_cleanup.json)。当前没有页面PNG，上述逐页结论为清理前的历史检查。

再次运行完整验收前，先运行本目录`render_check.py`从PDF重建页图；若修改题目、题图或排版，须先重新构建Word、导出PDF，并重新逐页查看及更新全部报告，不能沿用旧指纹和视觉结论。`build.py`仅生成待验收索引，`finalize.py`要求同版本报告和全部页图齐全后归档、清理。
'''
    MD.write_text(text,encoding='utf-8')
    print(json.dumps({'status':'complete','pages':15,'deleted_preview_png':len(targets),'docx':str(DOCX),'markdown':str(MD)},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
