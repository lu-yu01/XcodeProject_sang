"""Three requested local document revisions; final files live beside the originals."""
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent.parent
CASES={
 'doc1':{'source':'国考判断推理原创模拟卷（一）-35题（含答案解析）.docx',
         'output':'国考判断推理原创模拟卷（一）-35题（图片规范版，含答案解析）.docx','questions':35,'original_workdir':'guokao35'},
 'doc2':{'source':'国考判断推理原创模拟卷（二）-2026行政执法-35题（含答案解析）.docx',
         'output':'国考判断推理原创模拟卷（二）-2026行政执法-35题（图片规范版，含答案解析）.docx','questions':35,'original_workdir':'guokao2026_2'},
 'doc55':{'source':'国考图形与逻辑专项练习-55题（含答案解析）.docx',
          'output':'国考图形与逻辑专项练习-55题（图片规范版，含答案解析）.docx','questions':55,'original_workdir':'zhuanxiang55_20261025'},
}
def digest(path):return sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,data):Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
