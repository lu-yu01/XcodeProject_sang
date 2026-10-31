from pathlib import Path
import hashlib,json,re

ROOT=Path(r'E:\XcodeProject_sang');KB=ROOT/'知识库';AUDIT=ROOT/'.work'/'video_cleanup_20261031'
first=json.loads((AUDIT/'cleanup_manifest.json').read_text(encoding='utf-8-sig'))
extra=json.loads((AUDIT/'episode001_videos_manifest.json').read_text(encoding='utf-8-sig'))
extra_deleted={str(Path(x['Path']).resolve()).casefold():x for x in extra['Files']}
updated=[]
pattern=re.compile(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)')
for p in KB.rglob('*.md'):
    original=p.read_text(encoding='utf-8-sig')
    def replace(m):
        label,target=m.groups()
        if target.startswith(('http://','https://','#','plugin://','app://')):return m.group(0)
        target_path=target.split('#',1)[0].strip('<>')
        if str((p.parent/target_path).resolve()).casefold() in extra_deleted:
            return f'{label}（第001期历史成片，已于2026-10-31按用户要求删除）'
        return m.group(0)
    revised=pattern.sub(replace,original)
    if revised!=original:
        p.write_text(revised,encoding='utf-8');updated.append(str(p.relative_to(ROOT)))

master=KB/'每日一讲判断推理短视频制作模板.md'
text=master.read_text(encoding='utf-8-sig')
anchor='发布完成后仍保留本地最终MP4、原题、封面、实际用到的题卡或解析图、配音稿、时间表、可修改源及依赖文件，以及最终采用配音的原始导出和AI生成信息。'
if '用户明确废弃某一期视频时' not in text:
    text=text.replace(anchor,anchor+'用户明确废弃某一期视频时，按指定范围删除并记录清单，不把该决定扩展到其他期次。')
master.write_text(text,encoding='utf-8')

cleanup_record=KB/'短视频索引'/'素材清理记录_20261031.md'
text=cleanup_record.read_text(encoding='utf-8-sig')
heading='## 用户追加删除第001期全部视频'
if heading not in text:
    text+='\n\n'+heading+'\n\n用户随后明确表示“第001期视频都删掉，没用了”。另删第001期剩余3个有声视频：保留口音版、去除结尾提示版和有声预览版，共27.08MiB。此前5个无声测试视频已删除，第001期目录内现无MP4；题卡、原始配音和制作源未在此次追加删除范围内。\n\n两轮合计删除107个文件，释放68.92MiB。[追加删除清单](../../.work/video_cleanup_20261031/episode001_videos_manifest.json)及[追加执行结果](../../.work/video_cleanup_20261031/episode001_videos_result.json)已保存。第002期正式视频和制作源继续保留。\n'
    text=text.replace('保留正式视频、原题、封面、题卡、正式配音原件、制作源和一张当前模板参考总览。','首轮保留正式视频、原题、封面、题卡、正式配音原件、制作源和一张当前模板参考总览；用户随后追加删除第001期全部视频，见末节。')
    cleanup_record.write_text(text,encoding='utf-8')

notes=ROOT/'短视频'/'第001期_只有才'/'制作说明.txt'
text=notes.read_text(encoding='utf-8-sig')
prefix='2026-10-31用户追加删除第001期视频\n用户明确要求本期视频全部删除。已删除剩余3个正式有声MP4，加上首轮已清理的5个无声测试视频，本期目录现无MP4；题卡、原始配音、声音参考和制作源仍保留。下文为此前制作与清理历史状态。清单及执行结果见 .work/video_cleanup_20261031/episode001_videos_manifest.json 和 episode001_videos_result.json。\n\n'
if not text.startswith('2026-10-31用户追加删除第001期视频'):notes.write_text(prefix+text,encoding='utf-8')

allowed_docs={str((ROOT/'短视频'/'第001期_只有才'/'制作说明.txt').resolve()).casefold()}
for version in ['改进版_逐步演示','优化版_原题常驻','优化版_去右上角期数']:
    allowed_docs.add(str((ROOT/'短视频'/'第002期_去异求同'/version/'制作说明.txt').resolve()).casefold())
checked=0;documentation_changes=[]
for entry in first['PreservedBaseline']:
    p=Path(entry['Path']);key=str(p.resolve()).casefold()
    if key in extra_deleted:
        assert not p.exists(),f'第001期目标未删除: {p}';continue
    assert p.is_file(),f'保留文件缺失: {p}'
    if hashlib.sha256(p.read_bytes()).hexdigest().upper()!=entry['SHA256'].upper():
        assert key in allowed_docs,f'非说明文件发生意外变化: {p}'
        documentation_changes.append(str(p.relative_to(ROOT)))
    checked+=1
assert not list((ROOT/'短视频'/'第001期_只有才').rglob('*.mp4'))
remaining=list((ROOT/'短视频').rglob('*'))
assert len([p for p in remaining if p.is_file()])==checked
record={'total_deleted_files':107,'total_released_bytes':first['DeleteBytes']+extra['Bytes'],
        'total_released_MiB':round((first['DeleteBytes']+extra['Bytes'])/1024**2,2),
        'remaining_files':checked,'media_and_source_hashes_unchanged':True,
        'intentional_documentation_updates':documentation_changes,'episode001_remaining_mp4':0,
        'deleted_episode001_links_updated_in':updated}
(AUDIT/'final_verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
