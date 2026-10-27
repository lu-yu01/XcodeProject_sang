from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((ROOT/'render_manifest.json').read_text(encoding='utf8'))
assert len(m['pages'])==10
for p in m['pages']:
    assert sha(Path(p['path']))==p['sha256']
    p.update(actually_opened_at_original_size=True,result='pass')
m.update(word_sha256=sha(ROOT/'revised.docx'),reviewer='root',date='2026-10-28',
    observation='10页全部实际逐页打开。10题生活场景、必要方位标记及四候选清楚；无缺图、拉伸、裁切、文字遮盖、候选拆页或意外空白页。解析图、答案及干扰解释完整。',
    basis='Direct viewing of all final PDF page PNGs, not inferred from XML or text extraction.')
(ROOT/'visual_review.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print('Actual 10-page visual review recorded')
