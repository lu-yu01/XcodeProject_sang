"""Confirm square grid geometry and actual reviews, archive records, clean page PNGs."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from datetime import datetime
from PIL import Image
from verify_render import ROOT,read,write,digest

PROJECT=ROOT.parent.parent
SPECS={'doc1':[(2,'word/media/image2.png',(435,5,1065,635),210)],
       'doc2':[(4,'word/media/image4.png',(450,20,1350,920),300)],
       'doc55':[(q,f'word/media/image{q}.png',(480,40,1320,880),280) for q in range(9,13)]}

def actual_geometry(word,render,key):
    result=[]
    with ZipFile(word) as z:
        for q,media,box,side in SPECS[key]:
            im=Image.open(BytesIO(z.read(media))).convert('RGB');px=im.load()
            x0,y0,x1,y1=box
            assert x1-x0==y1-y0==side*3
            # Independently inspect all eight continuous raster grid lines.
            for x in [x0+i*side for i in range(4)]:
                assert max(sum(max(px[xx,y])<100 for y in range(y0,y1+1)) for xx in range(x-3,x+4))/(y1-y0+1)>.99
            for y in [y0+i*side for i in range(4)]:
                assert max(sum(max(px[x,yy])<100 for x in range(x0,x1+1)) for yy in range(y-3,y+4))/(x1-x0+1)>.99
            binding=next(x for x in render['equal_scale_image_checks'] if x['part']==media)
            width_mm=(x1-x0)*binding['x_emu_per_pixel']/36000
            height_mm=(y1-y0)*binding['y_emu_per_pixel']/36000
            assert abs(width_mm-height_mm)<.001
            result.append({'question':q,'part':media,'outer_box':list(box),'outer_size_px':[side*3,side*3],
                           'cell_size_px':[side,side],'grid_lines_continuous':True,
                           'word_grid_dimensions_mm':[width_mm,height_mm],'square_in_word':True})
    return result

def main():
    baselines=read(ROOT/'baselines.json');checked=[]
    for b in baselines:
        key=b['key'];folder=ROOT/key;word=Path(b['output']);pdf=folder/'preview.pdf'
        r=read(folder/'render_verification.json');v=read(folder/'visual_review.json')
        assert r['passed'] and v['passed']
        assert r['word_sha256']==digest(word) and r['pdf_sha256']==v['pdf_sha256']==digest(pdf)
        assert digest(b['before'])==b['before_sha256'] and digest(b['original'])==b['original_sha256']
        assert sorted(v['pages_reviewed'])==list(range(1,r['pages']+1)) and len(set(v['pages_reviewed']))==r['pages']
        geometry=actual_geometry(word,r,key)
        page_dir=(folder/'render').resolve();assert page_dir.is_relative_to(ROOT.resolve())
        targets=[]
        assert len(list(page_dir.glob('page-*.png')))==r['pages']
        for row in r['page_images']:
            p=Path(row['path']);assert p.resolve().parent==page_dir and not p.is_symlink()
            assert p.name==f'page-{row["page"]:02}.png' and digest(p)==row['sha256']
            targets.append({'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size})
        protected=[word,pdf,Path(b['before']),Path(b['original'])]+[p for p in folder.rglob('*.png') if 'render' not in p.relative_to(folder).parts]
        protected=[{'path':str(p),'sha256':digest(p)} for p in protected]
        checked.append((b,folder,r,v,geometry,targets,protected))
    # All versions, raster geometry, bindings and actual reviews pass before any deletion.
    now=datetime.now().astimezone().isoformat();summary=[]
    for b,folder,r,v,geometry,targets,protected in checked:
        key=b['key'];write(folder/'square_geometry_verification.json',{'passed':True,'word_sha256':r['word_sha256'],'grids':geometry})
        cleanup={'status':'planned','time':now,'deleted_count':len(targets),'deleted_bytes':sum(t['bytes'] for t in targets),'files':targets,'protected_files':protected}
        write(folder/'preview_cleanup.json',cleanup)
        for row in targets:Path(row['path']).unlink()
        assert all(not Path(row['path']).exists() for row in targets)
        assert all(digest(row['path'])==row['sha256'] for row in protected)
        cleanup.update(status='completed',protected_hashes_unchanged=True);write(folder/'preview_cleanup.json',cleanup)
        r['preview_png_status']='cleaned_after_completed_visual_review';write(folder/'render_verification.json',r)
        word=Path(b['output']);original=Path(b['original']);title=word.stem
        index=PROJECT/'知识库'/'套卷索引'/(title+'.md')
        dims='；'.join(f'第{x["question"]}题外框{x["outer_size_px"][0]}×{x["outer_size_px"][1]}像素，每格{x["cell_size_px"][0]}×{x["cell_size_px"][1]}像素' for x in geometry)
        text=f'''# {title} 索引与检查记录

## 当前套卷

- Word成品：[图片规范版](../../模式题/{word.name})，本次在同一路径更新正方形九宫格。
- 题量：{b['questions']}题；题干、选项、答案、解析和自动编号保持上轮版本。
- 当前源图、可复现修改脚本与报告：[工作目录](../../.work/ninegrid_square_20261025/{key}/)。
- Word指纹：`{r['word_sha256']}`。
- 图片要求：四个图形候选共用横向四格外框，A—D在框外下方；两组对照图同横排；六图分类保持原题型；解题必需标记保留，无关说明移出题图。九宫格题干须为正方形，九个小格等宽等高。

## 本次正方形九宫格修订与检查

- 记录时间：{now}。
- 改动位置与尺寸：{dims}。
- 调整格线及图形中心位置，未拉伸题图；四选项完整区域保持原样，图形内容、黑白、方向与顺序保留。逐图像素平移或几何检查的准确范围见[修改报告](../../.work/ninegrid_square_20261025/{key}/change_report.json)。
- 独立框线核验：通过；从Word内嵌PNG读取全部4条横线和4条竖线，外框宽高相等、格距一致、线条连续；Word中横纵缩放相等，实际九宫格宽高一致。[几何与显示比例报告](../../.work/ninegrid_square_20261025/{key}/square_geometry_verification.json)。
- 包结构：通过；仅本次目标PNG发生变化，document.xml、numbering.xml以及全部其他包内容逐字节相同，原文与答案表未改。
- 实际渲染：通过；{r['pages']}页，{r['embedded_images']}张内嵌图，题干、解析与表格文本在PDF中完整显示。[显示与版本检查](../../.work/ninegrid_square_20261025/{key}/render_verification.json)。
- 最终逐页视觉复核：通过；第1—{r['pages']}页均实际查看，九宫格为正方形，图形及问号居中，框线与内容留白清楚；题干与候选完整同页，无未解决的遮挡、裁切、缺图或分页异常。[视觉记录](../../.work/ninegrid_square_20261025/{key}/visual_review.json)。
- PDF指纹：`{r['pdf_sha256']}`。
- 渲染器缺少LibreOffice，诊断日志保留；改用独立、只读、禁宏的Word实例串行导出，未关闭用户其他Word文档。
- 本次检查范围为九宫格版式、内容保留及显示完整性，没有重新命题或进行全卷独立解题；原卷审题范围及未进行教师盲审、学员试测的情况见原卷记录。

## 版本与检查历史

- 最初原Word保留：[原文件](../../模式题/{original.name})；[原卷索引](./{original.stem}.md)。
- 上轮图片规范版另行保留：[修改前Word](../../.work/ninegrid_square_20261025/{key}/before.docx)，指纹`{b['before_sha256']}`。上轮报告对应该备份，不能作为当前版本验收。
- 上轮图片修改、渲染、逐页检查及预览清理历史见[历史工作目录](../../.work/image_format_batch_20261025/{key}/)。原始文件与上轮备份的指纹均未变。
- 通用规则：[图形题版式与难度规则](../2026国考图形题版式与难度规则.md)；[工程验收规则](../工程协作与套卷验收规则.md)。

## 临时预览与再次复核

本次{len(targets)}张页面PNG在实际逐页查看后已删除，题图、Word、PDF、源代码和报告保留，保护文件指纹未变。[清理清单](../../.work/ninegrid_square_20261025/{key}/preview_cleanup.json)。当前没有页面PNG，视觉记录为已完成的检查历史。

再次修改时，以本轮脚本和修改前备份为依据生成成品；导出新PDF后运行本批次`verify_render.py {key}`，重新查看全部页图并更新`visual_review.json`，最后运行`finalize.py`归档。不能沿用旧版本指纹或旧视觉结论。
'''
        index.write_text(text,encoding='utf-8')
        summary.append({'key':key,'word':str(word),'index':str(index),'questions_changed':[x['question'] for x in geometry],
                        'pages':r['pages'],'word_sha256':r['word_sha256'],'pdf_sha256':r['pdf_sha256'],'temporary_png_cleaned':len(targets)})
    total={'status':'complete','time':now,'documents':summary,'ninegrid_count':sum(len(x['questions_changed']) for x in summary),
           'total_pages_reviewed':sum(x['pages'] for x in summary),'temporary_png_cleaned':sum(x['temporary_png_cleaned'] for x in summary)}
    write(ROOT/'final_summary.json',total)
    print({k:v for k,v in total.items() if k!='documents'})

if __name__=='__main__':main()
