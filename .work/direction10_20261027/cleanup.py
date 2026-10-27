from pathlib import Path
import json,hashlib,datetime
from model import ROOT,PROJECT,OUT
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
final=json.loads((ROOT/'final_check.json').read_text(encoding='utf-8'))
visual=json.loads((ROOT/'visual_review.json').read_text(encoding='utf-8'))
assert final['passed'] and final['word_sha256']==sha(OUT) and final['pdf_sha256']==sha(ROOT/'preview.pdf')
targets=[]
for dirname,expected in [('render',10),('template_render',2)]:
 folder=(ROOT/dirname).resolve();assert folder.is_relative_to(PROJECT.resolve()) and folder.parent==ROOT
 files=sorted(folder.glob('page-*.png'));assert len(files)==expected
 for i,p in enumerate(files,1):
  assert p.resolve().parent==folder and p.name==f'page-{i:02}.png'
  if dirname=='render':assert sha(p)==visual['pages'][i-1]['sha256']
 targets+=files
assets=list((ROOT/'assets').glob('*.png'));assert len(assets)==20
refs=[p for p in (ROOT/'research').iterdir() if p.suffix.lower() in ['.png','.tiff']]
retained=assets+refs+[OUT,ROOT/'preview.pdf',ROOT/'final_check.json']
fingerprints={str(p):sha(p) for p in retained}
deleted=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in targets]
for p in targets:p.unlink()
assert all(not p.exists() for p in targets)
assert all(sha(Path(p))==h for p,h in fingerprints.items())
outside=[str(p) for p in PROJECT.rglob('*.md') if not p.is_relative_to(PROJECT/'知识库') and '.git' not in p.parts]
assert not outside,outside
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deleted':deleted,
 'deleted_count':len(deleted),'freed_bytes':sum(p['bytes'] for p in deleted),'retained_source_pngs':20,
 'retained_reference_images':len(refs),'retained_files_hash_unchanged':len(retained),'retained_sha256':fingerprints,
 'all_project_markdown_in_knowledge_base':True,'scope':'仅本轮render下10张最终成品页图与template_render下2张参考页图；保留正式题图、必要参考图、Word、PDF、源稿和报告。'}
(ROOT/'cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['deleted_count','freed_bytes','retained_source_pngs','retained_reference_images','retained_files_hash_unchanged']},ensure_ascii=False))
