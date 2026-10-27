"""Remove only explicitly identified, regenerable QA PNGs inside this task."""
from pathlib import Path
from model import ROOT,OUT,sha,dump

root=ROOT.resolve()
assets=sorted((root/'assets').glob('*.png'))
assert len(assets)==120
retained={str(p):sha(p) for p in assets+[OUT,root/'preview.pdf']}
temporary=[]
for name in ['render','template_render','blind_temp']:
    folder=root/name
    temporary.extend(p for p in folder.glob('*.png') if p.is_file())
for name in ['curves_contact.png','tokens_contact.png','tokens_group20_preview.png']:
    p=root/name
    if p.exists():temporary.append(p)
resolved=[p.resolve() for p in temporary]
assert len(set(resolved))==len(resolved)==46
deleted=[]
for p in resolved:
    assert root in p.parents and p.suffix=='.png'
    assert (root/'assets') not in p.parents
    assert p.parent.name in ['render','template_render','blind_temp'] or p.name in ['curves_contact.png','tokens_contact.png','tokens_group20_preview.png']
    deleted.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'Regenerable QA page, crop or contact preview; inspection complete.'})
# Verify the complete target list before starting any deletion.
assert (root/'final_check.json').exists()
for p in resolved:p.unlink()
for p,h in retained.items():assert sha(Path(p))==h
assert len(list((root/'assets').glob('*.png')))==120
dump(root/'cleanup.json',{'scope':str(root),'deleted_count':len(deleted),'deleted_bytes':sum(x['bytes'] for x in deleted),
    'deleted':deleted,'retained_source_assets':120,'retained_word_sha256':sha(OUT),
    'retained_pdf_sha256':sha(root/'preview.pdf'),'retained_fingerprints':retained,
    'word_pdf_and_all_formal_source_assets_unchanged':True})
print(f'Removed {len(deleted)} temporary PNGs; retained 120 formal assets, Word, PDF and audit history.')
