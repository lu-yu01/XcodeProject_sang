from pathlib import Path
import json,shutil,importlib
ROOT=Path(__file__).resolve().parent
p=ROOT/'model.py';t=p.read_text(encoding='utf8')
old='随后连续向自己的右侧转身，每次转过相同角度，再拍一幅，共拍四幅。'
new='随后继续向自己的右侧转身，依次又拍了三幅画面。'
assert t.count(old)==1
p.write_text(t.replace(old,new),encoding='utf8')
import model
(ROOT/'questions.json').write_text(json.dumps(model.Q,ensure_ascii=False,indent=2),encoding='utf8')
model.export_public()
revision=json.loads((ROOT/'q1_revision.json').read_text(encoding='utf8'))
shutil.copy2(revision['generated_path'],ROOT/'assets'/'question-01.png')
print('Q1 stable facade selected; Q4 equal-angle claim removed; no answer changed')
