"""Bind actual page reviews, archive three revision records, and remove QA page PNGs."""
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from batch_common import ROOT,PROJECT,CASES,digest,read,write

def relative(path):return Path(path).relative_to(PROJECT).as_posix()

def main():
    source_baselines={r['key']:r for r in read(ROOT/'source_baselines.json')}
    checked=[]
    for key,case in CASES.items():
        folder=ROOT/key;word=PROJECT/'模式题'/case['output'];pdf=folder/'preview.pdf'
        render=read(folder/'render_verification.json');visual=read(folder/'visual_review.json');change=read(folder/'change_report.json')
        assert render['passed'] and visual['passed'],key
        assert visual['pdf_sha256']==render['pdf_sha256']==digest(pdf),key
        assert render['word_sha256']==digest(word),key
        assert digest(PROJECT/'模式题'/case['source'])==source_baselines[key]['word_sha256'],key
        pages=visual['pages_reviewed']
        assert sorted(pages)==list(range(1,render['pages']+1)) and len(set(pages))==render['pages'],key
        assert render['original_paragraphs_preserved'] and render['numbering_xml_unchanged'] and render['all_paragraphs_and_table_cells_rendered'],key
        page_dir=(folder/'render').resolve()
        assert page_dir.is_relative_to(ROOT.resolve())
        assert len(list(page_dir.glob('page-*.png')))==render['pages'],key
        targets=[]
        for row in render['page_images']:
            p=Path(row['path'])
            assert p.resolve().parent==page_dir and not p.is_symlink() and digest(p)==row['sha256'],key
            assert p.name==f'page-{row["page"]:02}.png'
            targets.append({'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size})
        protected=[word,pdf]+[p for p in folder.rglob('*.png') if 'render' not in p.relative_to(folder).parts]
        protected=[{'path':str(p),'sha256':digest(p)} for p in protected]
        checked.append((key,case,folder,word,pdf,render,visual,change,targets,protected))
    # Mutation begins only after all three final versions and all page reviews pass.
    now=datetime.now().astimezone().isoformat();summary=[]
    for key,case,folder,word,pdf,render,visual,change,targets,protected in checked:
        cleanup={'status':'planned','time':now,'deleted_count':len(targets),'deleted_bytes':sum(t['bytes'] for t in targets),
                 'files':targets,'protected_files':protected}
        write(folder/'preview_cleanup.json',cleanup)
        for t in targets:Path(t['path']).unlink()
        assert all(not Path(t['path']).exists() for t in targets)
        assert all(digest(Path(t['path']))==t['sha256'] for t in protected)
        cleanup['status']='completed';cleanup['protected_hashes_unchanged']=True;write(folder/'preview_cleanup.json',cleanup)
        render['preview_png_status']='cleaned_after_completed_visual_review';write(folder/'render_verification.json',render)
        title=Path(case['output']).stem
        md=PROJECT/'知识库'/'套卷索引'/(title+'.md')
        old_index=Path(case['source']).stem+'.md'
        native_wording=render.get('documented_direction_wording_replacements',{})
        wording='；'.join(f'“{a}”改为“{b}”' for a,b in native_wording.items()) if native_wording else '原题干与解析文字保留，必要说明另列图片外的原生Word段落。'
        frame_note='卷（一）在图形推理节标题后增加原生说明，统一增设的最外层细框仅作排版、不参与规律判断，原图自身边线仍保留。' if key=='doc1' else '本卷没有为原图新增参与规律的封闭轮廓；原有框线与图形内容保持，相关核对已归档。'
        record=f'''# {title} 索引与检查记录

## 套卷索引

- Word成品：[图片规范版](../../模式题/{case['output']})。
- 原卷保留：[原Word](../../模式题/{case['source']})；[原卷检查记录](./{old_index})。
- 新工作目录：[{key}](../../.work/image_format_batch_20261025/{key}/)。
- 题量：{case['questions']}题，沿用原卷题目、选项顺序、答案和解析；本次只调整图片规范及与图位直接相关的说明。
- 图片规范：四个图形候选同一横排，共用连续大外框、三条竖线四等格；A—D位于各图下方、外框之外。删除无关图内说明，解题数据和必要标记保留。六图分类保持原类型，两组对照题保持同横排。
- Word版本指纹：`{render['word_sha256']}`。

## 本次修改与检查

- 记录时间：{now}。
- 逐题图片处理、像素或几何比对、保留标记及原生说明，见[修改报告](../../.work/image_format_batch_20261025/{key}/change_report.json)。
- 文字与方位配套处理：{wording}
- 外框与考点：{frame_note}[专项核对](../../.work/image_format_batch_20261025/frame_impact_review.json)。
- 原文件保护：通过；原Word指纹未变。
- 内容与编号：通过；原段落按已记录的方位措辞映射保留，Word自动编号XML未变；完整题干、解析及表格文本均在最终PDF中显示。
- 实际渲染：通过；最终{render['pages']}页，内嵌图片{render['embedded_images']}张。[显示与绑定检查](../../.work/image_format_batch_20261025/{key}/render_verification.json)。
- 逐页视觉复核：通过；第1—{render['pages']}页均已实际查看，核对图形内容、黑块、框线、字母、说明、分页与解析，无未解决的裁切、重叠或缺图问题。[记录](../../.work/image_format_batch_20261025/{key}/visual_review.json)。
- PDF版本指纹：`{render['pdf_sha256']}`。
- 渲染方式：常规渲染器缺少LibreOffice，诊断后使用独立、只读、禁宏的Word实例串行导出，再渲染页图检查；未关闭用户其他Word文档。
- 本次检查范围为图片版式、内容保留及文件显示；没有重新命题或重新进行全卷独立解题，原卷内容审查范围与未进行教师盲审、学员试测的情况见原记录。
- 通用规则：[图形题版式与难度规则](../2026国考图形题版式与难度规则.md)。

## 预览清理与再次复核

逐页检查后已删除{len(targets)}张临时页面PNG，保留题图、必要源素材、Word、PDF及检查历史，保留文件指纹未变化。[清理清单](../../.work/image_format_batch_20261025/{key}/preview_cleanup.json)。当前无页面PNG，视觉记录为清理前已完成的检查历史。

内容、图片、说明或版式修改后，重新生成Word、串行导出PDF、运行本批次`verify_render.py {key}`、逐页查看并更新视觉记录，最后才运行`finalize_batch.py`归档清理。不能复制旧指纹或旧视觉结论。
'''
        md.write_text(record,encoding='utf-8')
        summary.append({'key':key,'word':str(word),'index':str(md),'pages':render['pages'],'questions':case['questions'],
                        'word_sha256':render['word_sha256'],'pdf_sha256':render['pdf_sha256'],'temporary_png_cleaned':len(targets)})
    write(ROOT/'final_batch_summary.json',{'status':'complete','time':now,'documents':summary,'total_pages':sum(x['pages'] for x in summary)})
    print({'status':'complete','documents':3,'total_pages':sum(x['pages'] for x in summary),'temporary_png_cleaned':sum(x['temporary_png_cleaned'] for x in summary)})

if __name__=='__main__':main()
