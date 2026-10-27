from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parent
p=ROOT/'model.py';t=p.read_text(encoding='utf8')
old='上方俯视图给出一个点光源、三根相同竖直圆柱以及观察者的位置。'
new='上方俯视图中，黑点表示点光源在地面的竖直投影，并给出三根相同竖直圆柱及观察者的位置。'
assert t.count(old)==1;p.write_text(t.replace(old,new),encoding='utf8')
import model
(ROOT/'questions.json').write_text(json.dumps(model.Q,ensure_ascii=False,indent=2),encoding='utf8');model.export_public()
r=json.loads((ROOT/'q7_revision.json').read_text(encoding='utf8'));shutil.copy2(r['generated_path'],ROOT/'assets'/'question-07.png')
print('Q7 black dot now explicitly represents source ground projection')
