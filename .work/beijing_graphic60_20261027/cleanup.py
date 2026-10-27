from pathlib import Path
import json,hashlib,datetime,re

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
WORD=PROJECT/'模式题'/'北京风格图形操作进阶练习-20组60题（含答案解析）.docx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((ROOT/'final_check.json').read_text(encoding='utf-8'))
assert report['passed'] and report['word_sha256']==sha(WORD)
assert report['blind_first_visual_total']==60 and report['blind_first_visual_correct']==48
folder=(ROOT/'render').resolve()
assert folder.is_relative_to(PROJECT.resolve()) and folder.parent==ROOT
targets=sorted(folder.glob('page-*.png'))
assert len(targets)==40
review=json.loads((ROOT/'visual_review.json').read_text(encoding='utf-8'))
for n,p in enumerate(targets,1):
 assert p.resolve().parent==folder and p.name==f'page-{n:02}.png'
 assert sha(p)==review['pages'][n-1]['image_sha256']
assets=list((ROOT/'assets').glob('*.png'));assert len(assets)==120
retained=assets+[WORD,ROOT/'preview.pdf',ROOT/'final_check.json']
fingerprints={str(p):sha(p) for p in retained}
deleted=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in targets]
for p in targets:p.unlink()
assert not list(folder.glob('page-*.png'))
assert all(sha(Path(p))==h for p,h in fingerprints.items())
for name in ['项目说明.md','建议与变更记录.md','北京一拖三图形操作题命题规则.md','套卷索引/'+WORD.stem+'.md']:
 md=PROJECT/'知识库'/name
 for link in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
  if '://' not in link:assert (md.parent/link).resolve().exists(),(name,link)
outside=[str(p) for p in PROJECT.rglob('*.md') if not p.is_relative_to(PROJECT/'知识库') and '.git' not in p.parts]
assert not outside,outside
result={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deleted':deleted,
 'deleted_count':len(deleted),'freed_bytes':sum(p['bytes'] for p in deleted),
 'retained_files_hash_unchanged':len(retained),'retained_source_pngs':len(assets),
 'retained_file_sha256':fingerprints,'knowledge_links_passed':True,'all_project_markdown_in_knowledge_base':True,
 'scope':'仅本轮render/page-*.png共40张临时页图；保留120张正式图源、Word、PDF、源稿和全部报告。'}
(ROOT/'cleanup.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['deleted_count','freed_bytes','retained_source_pngs','retained_files_hash_unchanged','knowledge_links_passed']},ensure_ascii=False))
