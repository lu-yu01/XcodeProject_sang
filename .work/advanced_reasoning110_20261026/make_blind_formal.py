from pathlib import Path
import json,hashlib
import formal
ROOT=Path(__file__).resolve().parent
cards=[]
for q in formal.QUESTIONS:
 card={k:q[k] for k in ['n','category','stem','ask','options']}
 group=next((k for k in formal.GROUPS if k<=q['n']<k+5),None)
 if group:card.update(group=group,material=formal.GROUPS[group])
 cards.append(card)
report={'instruction':'仅依据本卡的原生材料、题干和选项独立解题。不要读取 formal.py、formal_parallel.py、explore_formal.py、questions_formal.json、验证报告或作者答案。新增条件只作用本题。记录答案、自然推理和歧义。','cards':cards}
(ROOT/'blind_cards_formal.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cards':len(cards),'sha256':hashlib.sha256((ROOT/'blind_cards_formal.json').read_bytes()).hexdigest()}))
