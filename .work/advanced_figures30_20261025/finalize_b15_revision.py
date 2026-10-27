"""Finalize only the revised question 15 and preserve the other nine questions."""
from pathlib import Path
import hashlib
import json
import advanced_b as b

root = Path(__file__).resolve().parent
prior = json.loads((root / 'questions_b.json').read_text(encoding='utf-8'))
report_path = root / 'b15_revision_report.json'
report = json.loads(report_path.read_text(encoding='utf-8'))
assert [q for q in prior if q['n'] != 15] == [q for q in b.QUESTIONS if q['n'] != 15]
for name, expected in report['before_other_assets'].items():
    assert hashlib.sha256((root / 'assets' / name).read_bytes()).hexdigest() == expected, name
checks = b.verify()
assert checks['passed']
q = next(q for q in b.QUESTIONS if q['n'] == 15)
assert q['stem'] == report['before_q15']['stem']
report['after_q15'] = q
report['passed'] = True
report['other_nine_question_models_text_preserved'] = True
report['other_eighteen_images_preserved'] = True
report['visual_review'] = {
    'images_reviewed': ['assets/q15.png', 'assets/e15.png'],
    'passed': True,
    'observations': [
        '九宫格为正方形，九个等方格；图形及问号留有清楚间距。',
        '四个候选同一四等格横框，A—D位于框外下方，均为四个黑格。',
        '解释图四个阶段横排，文字、网格与黑格均清晰，无相互遮挡。'
    ]
}
for prefix, field in [('q', 'new_q15_image_sha256'), ('e', 'new_e15_image_sha256')]:
    report[field] = hashlib.sha256((root / 'assets' / f'{prefix}15.png').read_bytes()).hexdigest()
(root / 'questions_b.json').write_text(json.dumps(b.QUESTIONS, ensure_ascii=False, indent=2), encoding='utf-8')
(root / 'verify_b.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
card = {key: q[key] for key in ['n', 'stem', 'ask', 'options']}
card['image'] = str(root / 'assets' / q['image'])
card['image_sha256'] = report['new_q15_image_sha256']
(root / 'blind_card_b15_revised.json').write_text(json.dumps({
    'instruction': '只看题干、题图、选项独立求解，不读作者代码、答案、解析、模型、解释图或修订记录；记录自然规律、选择、置信度及歧义。',
    'cards': [card]
}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'passed': checks['passed'], 'answer': q['answer'],
                  'q15_sha256': report['new_q15_image_sha256'],
                  'e15_sha256': report['new_e15_image_sha256'],
                  'others_preserved': True,
                  'checks': checks['checks']['15']}, ensure_ascii=False))
