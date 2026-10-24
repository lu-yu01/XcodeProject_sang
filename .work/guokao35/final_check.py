"""Re-check the final DOCX, PDF and page images, then update the suite record."""

import json
from pathlib import Path
import subprocess
import sys

from suite_record import DOCX, RECORD, WORK, digest, write_record


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    pdf = WORK / 'preview.pdf'
    assert DOCX.is_file(), DOCX
    assert pdf.is_file(), pdf
    assert pdf.stat().st_mtime_ns >= DOCX.stat().st_mtime_ns, 'PDF 早于 Word，请重新导出预览'
    for script in ('verify.py', 'verify_render.py'):
        result = subprocess.run([sys.executable, '-B', str(WORK / script)], text=True, capture_output=True, encoding='utf-8')
        print(result.stdout.strip())
        if result.returncode:
            print(result.stderr, file=sys.stderr)
            raise RuntimeError(f'{script} 检查失败')
    verification = json.loads((WORK / 'verification.json').read_text(encoding='utf-8'))
    render = json.loads((WORK / 'render_verification.json').read_text(encoding='utf-8'))
    for n in range(1, render['pages'] + 1):
        page = WORK / 'render' / f'page-{n:02d}.png'
        assert page.stat().st_mtime_ns >= pdf.stat().st_mtime_ns, f'页图早于 PDF：{page.name}'
    visual_file = WORK / 'visual_review.json'
    visual = json.loads(visual_file.read_text(encoding='utf-8')) if visual_file.is_file() else None
    if visual is not None and visual['pdf_sha256'] != digest(pdf):
        visual = None
    record = write_record(verification, render, visual)
    assert record == RECORD and record.is_file()
    print(json.dumps({'status': 'passed', 'record': str(record), 'pages': render['pages'], 'visual_review': 'passed' if visual else 'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
