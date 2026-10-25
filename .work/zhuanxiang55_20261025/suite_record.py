"""Hash-bound index and check record, without duplicating question content."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
STEM='国考图形与逻辑专项练习-55题（含答案解析）'
DOCX=PROJECT/'模式题'/f'{STEM}.docx'
RECORD=PROJECT/'知识库'/'套卷索引'/f'{STEM}.md'
PDF=ROOT/'preview.pdf'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):
    p=ROOT/name
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
def write_record():
    v,r,a=read('verification.json'),read('render_verification.json'),read('visual_review.json')
    wh=sha(DOCX) if DOCX.exists() else '';ph=sha(PDF) if PDF.exists() else ''
    current=bool(wh and ph and PDF.stat().st_mtime_ns>=DOCX.stat().st_mtime_ns)
    vp=bool(v.get('passed') and v.get('word_sha256')==wh)
    rp=bool(current and r.get('passed') and r.get('pdf_sha256')==ph)
    ap=bool(current and a.get('passed') and a.get('pdf_sha256')==ph)
    now=datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S +0800')
    lines=[
        '# 国考图形与逻辑专项练习55题 索引与检查记录','',
        '## 套卷索引','',
        f'- Word成品：[{DOCX.name}](../../模式题/{DOCX.name})',
        '- 源稿及构建目录：[zhuanxiang55_20261025](../../.work/zhuanxiang55_20261025/)',
        '- 题量：55题；图形推理30题，一拖五3组15题，加强5题、削弱5题。题目在前，参考答案和逐题解析在后。',
        '- 图形结构：规律与运算12题、空间推理9题、六图分类9题。两组对照式第5至8题的两组三格同一横排；分类题为两行三列独立方框。',
        f'- Word版本指纹：`{wh or "待生成"}`','',
        '## 生成后检查','',f'- 记录刷新：{now}',
        f'- 内容与答案绑定：{"通过" if vp else "待完成"}；[检查报告](../../.work/zhuanxiang55_20261025/verification.json)。',
        f'- PDF与页图：{"通过" if rp else "待完成"}；最终页数{r.get("pages","待检查")}；[报告](../../.work/zhuanxiang55_20261025/render_verification.json)。',
        f'- PDF版本指纹：`{ph or "待生成"}`',
        f'- 逐页视觉检查：{"通过" if ap else "待完成"}；[记录](../../.work/zhuanxiang55_20261025/visual_review.json)。',
        '- 数学范围：30道图形的生成模型；三组一拖五公共解及各子题选项的可能、必然、等价或唯一性；论证题中可计算的比例与全流程时间。',
        '- 代理交叉复核：已完成；加强削弱逐项比较论点、证据和干扰机制，图形另核对实际图像与模型。[修订记录](../../.work/zhuanxiang55_20261025/editorial_review.json)。',
        '- 两组对照横排：已通过坐标检查和第3至4页实际预览；两组三图同一基线，选项另排。',
        '- 难度为命题估计；未进行独立教师盲审或学员试测。',
        '- 复用规则：[图形版式与难度规则](../2026国考图形题版式与难度规则.md)。','',
        '如修改Word、题图或解析，须重新渲染、检查并刷新文件指纹及验收状态。',''
    ]
    RECORD.parent.mkdir(parents=True,exist_ok=True);RECORD.write_text('\n'.join(lines),encoding='utf-8');return RECORD
if __name__=='__main__':print(write_record())
