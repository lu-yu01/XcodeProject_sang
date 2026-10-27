from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1]
FINAL=PROJECT/'模式题/北京风格情境方向图形推理-10题（含答案解析）.docx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((ROOT/'final_check.json').read_text(encoding='utf8'))
assert report['passed'] and report['remaining_delivery_blockers']==[]
assert sha(ROOT/'revised.docx')==report['staged_word_sha256']
assert sha(FINAL)==sha(ROOT/'source.docx'),'Original target changed since backup'
assert FINAL.resolve().parent==(PROJECT/'模式题').resolve()
shutil.copy2(ROOT/'revised.docx',FINAL)
assert sha(FINAL)==report['staged_word_sha256']
retained=list((ROOT/'assets').glob('*.png'))+list((ROOT/'sources').glob('*.svg'))+[FINAL,ROOT/'source.docx',ROOT/'preview.pdf']
before={str(p):sha(p) for p in retained}
temporary=sorted((ROOT/'render').glob('page-*.png'))+sorted((ROOT/'sources').glob('*-preview.png'))
assert len(temporary)==18
deleted=[]
for p in temporary:
    p=p.resolve()
    assert ROOT.resolve() in p.parents and p.suffix=='.png'
    assert p.parent in [(ROOT/'render').resolve(),(ROOT/'sources').resolve()]
    deleted.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'Temporary inspected final-page render or source-art preview; regenerable.'})
# Complete absolute-path validation above precedes every unlink below.
for record in deleted:Path(record['path']).unlink()
for p,h in before.items():assert sha(Path(p))==h
cleanup={'scope':str(ROOT),'deleted_count':len(deleted),'deleted':deleted,
         'formal_pngs_retained':20,'used_original_svg_assets_retained':9,
         'all_retained_fingerprints_unchanged':True,'retained':before,
         'final_word_sha256':sha(FINAL),'source_backup_sha256':sha(ROOT/'source.docx')}
(ROOT/'cleanup.json').write_text(json.dumps(cleanup,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'same_name_word_updated':str(FINAL),'sha256':sha(FINAL),'temporary_pngs_removed':18},ensure_ascii=False))
