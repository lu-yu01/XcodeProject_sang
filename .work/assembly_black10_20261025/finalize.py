"""Finalize the corrected form, colour-aware verification, visual record and cleanup."""
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile
import hashlib,json
from build import ROOT,PROJECT,DOCX,MD,sha
from puzzles import QUESTIONS

def read(n):return json.loads((ROOT/n).read_text(encoding='utf-8'))
def write(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    model=read('verification.json');ind=read('independent_review.json');r=read('render_verification.json')
    assert model['status']=='passed' and ind['passed_math'] and ind['passed_display_geometry'] and ind['passed_semantics']
    assert model['model_sha256']==ind['puzzles_sha256']==sha(ROOT/'puzzles.py')
    text_edit=read('text_cleanup_verification.json')
    assert text_edit['passed'] and text_edit['puzzles_sha256']==sha(ROOT/'puzzles.py')
    assert text_edit['solid_regions_rgb_identical']==80 and text_edit['explanation_images_unchanged']==10
    assert model['colored_option_checks']==model['shape_only_option_checks']==40
    for q in QUESTIONS:
        assert len(q['pieces'])==2 and len(q['options'])==4 and len(q['target']['black'])==3
        assert all(len(p['black'])==1 for p in q['pieces']+q['options'])
        assert len(q['solution'])==3 and all(len(p['black'])==1 for p in q['solution'])
    assert r['passed'] and r['pages']==10
    assert r['word_sha256']==read('build_info.json')['word_sha256']==sha(DOCX)
    assert r['pdf_sha256']==sha(ROOT/'preview.pdf')
    reviews=[read('visual_questions.json'),read('visual_answers.json')]
    assert all(v['passed'] and v['pdf_sha256']==r['pdf_sha256'] for v in reviews)
    pages=[p for v in reviews for p in v['pages_reviewed']]
    assert sorted(pages)==list(range(1,11)) and len(set(pages))==10
    images=[ROOT/'assets'/f'q{n:02}{s}.png' for n in range(1,11) for s in ('','_solution')]
    assert len(list((ROOT/'assets').glob('*.png')))==20
    with ZipFile(DOCX) as z:
        embedded=[hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/')]
    assert sorted(embedded)==sorted(sha(p) for p in images)
    now=datetime.now().astimezone().isoformat()
    write('visual_review.json',{'passed':True,'time':now,'word_sha256':r['word_sha256'],'pdf_sha256':r['pdf_sha256'],
          'pages_reviewed':sorted(pages),'sources':['visual_questions.json','visual_answers.json'],
          'status':'completed_before_preview_cleanup','note':'10页均已实际查看；临时页图随后按用户偏好清理，成品未改变。'})
    directory=(ROOT/'render').resolve();assert directory.is_relative_to(PROJECT.resolve())
    assert len(list(directory.glob('*.png')))==10
    targets=[]
    for row in r['page_images']:
        p=Path(row['path']);assert not p.is_symlink() and p.resolve().parent==directory
        assert p.name==f'page-{row["page"]:02}.png' and sha(p)==row['sha256']
        targets.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
    protected=images+list((ROOT/'reference').glob('*.png'))+[DOCX,ROOT/'preview.pdf']
    protected=[{'path':str(p),'sha256':sha(p)} for p in protected]
    cleanup={'status':'planned','time':now,'files':targets,'deleted_count':10,'deleted_bytes':sum(x['bytes'] for x in targets),'protected_files':protected}
    write('preview_cleanup.json',cleanup)
    for x in targets:Path(x['path']).unlink()
    assert all(not Path(x['path']).exists() for x in targets)
    assert all(sha(Path(x['path']))==x['sha256'] for x in protected)
    cleanup['status']='completed';cleanup['protected_hashes_unchanged']=True;write('preview_cleanup.json',cleanup)
    r['preview_png_status']='cleaned_after_completed_visual_review';write('render_verification.json',r)
    record=f'''# 立体拼合三黑块版10题 索引与检查记录

## 套卷索引

- Word成品：[立体拼合三黑块版10题](../../模式题/立体拼合专项练习-三黑块版10题（含答案解析）.docx)。
- 工作目录：[assembly_black10_20261025](../../.work/assembly_black10_20261025/)。
- 题量与形制：10题全部给出一个完整目标和两个已知部分，四选一第三部分，三件共同拼目标；全部正选，不混两件选结果或选非题。
- 黑块要求：目标共3黑块，部件①②各1黑块，四个候选各1黑块；白块纯白，黑块是固定材料标记，形状与颜色位置同时匹配。
- 版式：目标正反视图及两个已给部分处于题干同一横排，A—D四项同一横排；题目在前，答案、解析及分层拼合图在后，最终10页。
- 图片去文字：按用户确认删除题图内的标题、块数和正背面说明，仅保留①②与A—D。必要块数改列图片外的Word正文；解析图的分层、部件归属及方向标记保留。80个实体区域逐像素未变，10张解析图文件未变。[修改核对](../../.work/assembly_black10_20261025/text_cleanup_verification.json)。
- 难度为命题估计：中等6题、较难4题；未进行独立教师盲审或学员试测。
- 原稿处理：[上一版](./立体拼合专项练习-10题（含答案解析）.md)仅作为题型未对齐的历史稿，本次以本三黑块版为准。
- Word版本指纹：`{r['word_sha256']}`。

## 参考依据与生成后复核

- 记录时间：{now}。
- 严格同式样例：2023湖北职测C65、2024年11月职测C65、2025年3月职测C65、2025国考副省85／地市82同题。原图与正文核对目标3灰、两已给各1灰、四候选各1灰；本次按用户要求以黑色表达。[形制研究](../../.work/assembly_black10_20261025/source_findings.json)。不从这些样例推导所有考试统一的年份分界。
- 需求形制检查：通过；逐题核对一个目标、两个已知部分、四选第三件，以及3／1／1／1黑块要求。
- 几何与逐格颜色检查：通过；24种正向旋转与目标内平移，40项保持黑白位置的精确拼合及40项忽略颜色的对照验证；每题都有外形可拼但颜色错的干扰项。[报告](../../.work/assembly_black10_20261025/verification.json)。
- 独立复核：通过；另一实现复核40项、三件构造、完整覆盖、无重叠、黑白严格对应、选项不等价及显示遮挡；并逐题复核解析。[报告](../../.work/assembly_black10_20261025/independent_review.json)。
- 源稿、Word与实际显示：通过；10个题号与10个答案题号连续，20张内嵌图片与源图逐张一致，题干和解析均在PDF文本中完整对应。[报告](../../.work/assembly_black10_20261025/render_verification.json)。
- 逐页视觉检查：通过；第1—10页全部实际查看，题型、横排、黑块、分层解析、字体及分页均已核对。[历史记录](../../.work/assembly_black10_20261025/visual_review.json)。
- PDF版本指纹：`{r['pdf_sha256']}`。
- 渲染方式：常规渲染器缺少LibreOffice，诊断后使用独立、只读、禁宏的Word实例导出PDF，再渲染页图检查。
- 可复用要求：[立体拼合命题与检查规则](../立体拼合题命题与检查规则.md)。

## 预览清理

逐页检查完成后已删除10张临时页面PNG，保留10张题图、10张分层解析图、3张必要参考图、Word、PDF及检查历史，保留文件指纹未变化。[清理清单](../../.work/assembly_black10_20261025/preview_cleanup.json)。当前没有页面PNG，上述视觉结论为清理前完成的历史检查。

内容、题图或版式修改后须重新构建、导出PDF、逐页查看并刷新全部报告；完整验收前先用`render_check.py`重建页图。`build.py`生成的索引为待验收状态，`finalize.py`只有在同版本报告及全部页图齐全时才归档并清理。
'''
    MD.write_text(record,encoding='utf-8')
    print(json.dumps({'status':'complete','pages':10,'questions':10,'deleted_preview_png':10,'docx':str(DOCX),'markdown':str(MD)},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
