from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
assert (ROOT/'final_check.json').exists()
assert json.loads((ROOT/'final_check.json').read_text(encoding='utf-8'))['passed']
target=(ROOT/'render').resolve()
assert target.is_relative_to(PROJECT.resolve()) and target.name=='render'
files=sorted(target.glob('page-*.png'))
assert len(files)==2
keep=[p for p in (ROOT/'assets').glob('*.png')]+[ROOT/'preview.pdf',PROJECT/'模式题'/'北京风格图形推理一拖三-1组3题（含答案解析）.docx']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in keep}
deleted=[]
for p in files:
 assert p.resolve().parent==target and p.is_file()
 deleted.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 p.unlink()
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items())
report={'deleted':deleted,'deleted_count':len(deleted),'freed_bytes':sum(x['bytes'] for x in deleted),'retained_files_hash_unchanged':len(before),'scope':'仅本轮render/page-*.png临时页图；全部题图、解析图、参考图、Word、PDF和报告保留。'}
(ROOT/'cleanup.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['deleted_count','freed_bytes','retained_files_hash_unchanged']},ensure_ascii=False))
