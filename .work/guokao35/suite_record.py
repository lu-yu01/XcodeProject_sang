"""Write this suite's Markdown index and check record in the knowledge base."""

from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path

from content import TITLE, QUESTIONS


WORK = Path(__file__).resolve().parent
PROJECT = WORK.parents[1]
DOCX = PROJECT / '模式题' / f'{TITLE}-35题（含答案解析）.docx'
RECORD = PROJECT / '知识库' / '套卷索引' / f'{DOCX.stem}.md'


def link(path):
    """Make a link from the record, never an environment-specific absolute path."""
    return Path(os.path.relpath(path, RECORD.parent)).as_posix()


def digest(path):
    h = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_record(verification=None, render=None, visual=None):
    assert DOCX.is_file(), DOCX
    counts = Counter(q['category'] for q in QUESTIONS)
    pdf = WORK / 'preview.pdf'
    checked = verification is not None and render is not None
    if checked:
        assert verification['status'] == render['status'] == 'passed'
        assert render['answer_count'] == len(QUESTIONS)
    if visual is not None:
        assert checked
        assert visual['pdf_sha256'] == digest(pdf)
        assert visual['pages'] == list(range(1, render['pages'] + 1))
    lines = [
        f'# {TITLE} 套卷索引与检查记录',
        '',
        '## 套卷索引',
        '',
        f'- Word 成品：[{DOCX.name}]({link(DOCX)})',
        f'- 源稿与构建目录：[{WORK.name}]({link(WORK)}/)',
        f'- 题量与结构：{len(QUESTIONS)}题；' + '、'.join(f'{name}{counts[name]}题' for name in ('图形推理', '定义判断', '类比推理', '逻辑判断')) + '；第31—35题共用材料。',
        '- 正文：题目在前，答案速查与逐题解析在后。',
        f'- Word 版本指纹（SHA-256）：`{digest(DOCX)}`',
        '',
        '## 生成后检查',
        '',
    ]
    if checked:
        lines.extend([
            f'- 本次程序复核时间：{datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")}',
            f'- 源稿与 Word 结构检查：通过；{verification["questions"]}题；数学与有限状态检查覆盖第1—10、30—35题。[报告]({link(WORK / "verification.json")})',
            f'- PDF 与页图检查：通过；{render["pages"]}页、{render["answer_count"]}个答案；题干、文字选项及解析均在渲染文本中。[报告]({link(WORK / "render_verification.json")})',
            f'- PDF 版本指纹（SHA-256）：`{digest(pdf)}`',
        ])
    else:
        lines.extend([
            '- 程序复核：待运行最终检查；不能沿用上一版的报告。',
            '- PDF 与页图复核：待运行最终检查；不能沿用上一版的预览。',
        ])
    lines.extend([
        f'- 人工逐页视觉检查：{visual["date"]} 已查看第1—{render["pages"]}页；{visual["result"]}。[记录]({link(WORK / "visual_review.json")})' if visual else '- 人工逐页视觉检查：待记录；检查题图、字体、裁切、分页和页眉页脚。',
        '- 独立教师审题与学员试测：未进行；程序检查不能替代。',
        '- 仍需确认：未经过程序求解的题目内容仍需独立审题。' if visual else '- 仍需确认：人工逐页视觉检查及未经过程序求解的题目内容。',
        '',
        '如对 Word、题图或排版再作修改，必须重新导出 PDF、更新全部页图，并重跑最终检查；人工检查状态也须重新核对。',
        '',
    ])
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text('\n'.join(lines), encoding='utf-8')
    return RECORD


if __name__ == '__main__':
    print(json.dumps({'record': str(write_record()), 'status': 'pending'}, ensure_ascii=False))
