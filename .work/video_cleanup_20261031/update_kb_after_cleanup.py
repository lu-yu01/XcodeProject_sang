from pathlib import Path
import json,re

ROOT=Path(r'E:\XcodeProject_sang')
KB=ROOT/'知识库'
AUDIT=ROOT/'.work'/'video_cleanup_20261031'
manifest=json.loads((AUDIT/'cleanup_manifest.json').read_text(encoding='utf-8-sig'))
deleted={str(Path(x['Path']).resolve()).casefold():x for x in manifest['Candidates']}
changed=[]
removed_links=[]
pattern=re.compile(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)')
for p in KB.rglob('*.md'):
    original=p.read_text(encoding='utf-8-sig')
    def replace(m):
        label,target=m.groups()
        if target.startswith(('http://','https://','#','plugin://','app://')):return m.group(0)
        target_path=target.split('#',1)[0].strip('<>')
        resolved=(p.parent/target_path).resolve()
        item=deleted.get(str(resolved).casefold())
        if item is None:return m.group(0)
        removed_links.append({'document':str(p.relative_to(ROOT)),'label':label,'deleted_target':item['Path']})
        suffix='已于2026-10-31清理，可重建预览' if item['Category']=='可重建预览PNG' else '已于2026-10-31清理的历史测试素材'
        return f'{label}（{suffix}）'
    revised=pattern.sub(replace,original)
    if revised!=original:
        p.write_text(revised,encoding='utf-8')
        changed.append(str(p.relative_to(ROOT)))

index=KB/'短视频索引'/'第002讲_去异求同.md'
text=index.read_text(encoding='utf-8-sig')
start=text.index('- 发布后素材依赖：')
end=text.index('\n',start)
text=text[:start]+'- 发布后素材依赖：最新渲染源读取本期原题及第4张方法题卡；实际4条默认音源和最新版本原始配音备份保留，逐步演示版与原题常驻版的8份重复配音备份已清理。各版独立关键帧与成片抽帧已清理，最新无角标关键帧总览保留作模板参考；详见[素材清理记录](./素材清理记录_20261031.md)。'+text[end:]
index.write_text(text,encoding='utf-8')

master=KB/'每日一讲判断推理短视频制作模板.md'
text=master.read_text(encoding='utf-8-sig')
anchor='可清理对象是确认能够重建且不被当前草稿或脚本依赖的抽帧、关键帧预览、总览图、废弃试音、旧无声预览和重复导出。'
replacement=anchor+'已作为当前模板视觉参考的总览可保留一张，避免每次查模板都重新渲染。'
if '已作为当前模板视觉参考的总览可保留一张' not in text:text=text.replace(anchor,replacement)
master.write_text(text,encoding='utf-8')

report={'changed_documents':changed,'converted_deleted_links':removed_links,'deleted_link_count':len(removed_links)}
(AUDIT/'knowledge_link_updates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'changed_documents':changed,'deleted_link_count':len(removed_links)},ensure_ascii=False))
