"""Read-only inventory and structural scan of the supplied exam corpus.

This script never changes source files. Its JSONL output is audit evidence, not
an automatically approved question bank or an answer-key validator.
"""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from zipfile import BadZipFile, ZipFile

from lxml import etree
from pypdf import PdfReader


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / '真题'
OUT = PROJECT / '.work' / 'corpus_audit'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
MARKERS = ('判断推理', '图形推理', '定义判断', '类比推理', '逻辑判断',
           '常识判断', '言语理解', '数量关系', '资料分析', '申论', '综合应用能力',
           '职业能力倾向测验', '参考答案', '答案及解析')
Q_RE = re.compile(r'^\s*(?:第\s*)?(\d{1,3})\s*(?:题|[.．、])')


def file_hash(path):
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def text_profile(lines):
    headings = []
    numbers = []
    counts = Counter()
    samples = []
    chars = 0
    for i, line in enumerate(lines):
        line = re.sub(r'\s+', ' ', line).strip()
        if not line:
            continue
        chars += len(line)
        if len(samples) < 6:
            samples.append(line[:100])
        for marker in MARKERS:
            if marker in line:
                counts[marker] += 1
                if len(headings) < 32 and len(line) <= 100:
                    headings.append({'line': i, 'text': line[:100]})
                break
        match = Q_RE.match(line)
        if match:
            numbers.append(int(match.group(1)))
    return {
        'text_chars': chars,
        'paragraphs_or_lines': len(lines),
        'marker_counts': dict(counts),
        'headings': headings,
        'question_number_min': min(numbers) if numbers else None,
        'question_number_max': max(numbers) if numbers else None,
        'question_number_candidates': len(numbers),
        'first_lines': samples,
    }


def read_docx(path):
    with ZipFile(path) as z:
        xml = z.open('word/document.xml')
        lines = []
        for _, para in etree.iterparse(xml, events=('end',), tag=W + 'p', recover=True, huge_tree=True):
            lines.append(''.join(node.text or '' for node in para.iter(W + 't')))
            para.clear()
            while para.getprevious() is not None:
                del para.getparent()[0]
        result = text_profile(lines)
        result['embedded_media'] = sum(name.startswith('word/media/') and not name.endswith('/') for name in z.namelist())
        return result


def read_pptx(path):
    with ZipFile(path) as z:
        slides = sorted((name for name in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)),
                        key=lambda name: int(re.search(r'slide(\d+)', name).group(1)))
        lines = []
        for name in slides:
            root = etree.fromstring(z.read(name))
            text = ' '.join(node.text or '' for node in root.iter(A + 't'))
            lines.append(text)
        result = text_profile(lines)
        result['slides'] = len(slides)
        result['embedded_media'] = sum(name.startswith('ppt/media/') and not name.endswith('/') for name in z.namelist())
        return result


def read_pdf(path):
    reader = PdfReader(str(path), strict=False)
    lines = []
    for page in reader.pages:
        lines.extend((page.extract_text() or '').splitlines())
    result = text_profile(lines)
    result['pages'] = len(reader.pages)
    return result


def classify(path):
    parts = path.relative_to(SOURCE).parts
    joined = '/'.join(parts)
    if '自建试卷' in joined or re.search(r'模考|模拟|押题|冲刺|预测|密卷', path.stem):
        provenance = '模拟或自建'
    elif '真题' in joined or '公务员录用考试' in joined:
        provenance = '真题标称（未核实来源）'
    else:
        provenance = '来源待核'
    if '申论' in joined:
        subject = '申论'
    elif '综应' in joined or '公基' in joined or 'D类' in joined:
        subject = '综应/公基等'
    elif '行测' in joined or '国考' in joined or '省考' in joined or '公务员笔试' in joined:
        subject = '行测候选'
    elif '职测' in joined or '职业能力' in joined:
        subject = '职测候选'
    else:
        subject = '待分类'
    return provenance, subject


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted((p for p in SOURCE.rglob('*') if p.is_file()), key=lambda p: str(p).casefold())
    extensions = Counter()
    errors = Counter()
    with (OUT / 'manifest.jsonl').open('w', encoding='utf-8') as stream:
        for index, path in enumerate(files, 1):
            relative = path.relative_to(PROJECT).as_posix()
            provenance, subject = classify(path)
            item = {'path': relative, 'extension': path.suffix.lower(), 'bytes': path.stat().st_size,
                    'sha256': file_hash(path), 'provenance': provenance, 'subject': subject}
            try:
                if path.suffix.lower() == '.docx':
                    item.update(read_docx(path))
                elif path.suffix.lower() == '.pptx':
                    item.update(read_pptx(path))
                elif path.suffix.lower() == '.pdf':
                    item.update(read_pdf(path))
                elif path.suffix.lower() == '.xls':
                    item['read_scope'] = 'indexed_only; paired Word version checked separately where present'
            except (BadZipFile, KeyError, etree.XMLSyntaxError, ValueError, OSError) as exc:
                item['error'] = f'{type(exc).__name__}: {str(exc)[:180]}'
                errors[type(exc).__name__] += 1
            stream.write(json.dumps(item, ensure_ascii=False) + '\n')
            extensions[path.suffix.lower()] += 1
            if index % 200 == 0:
                print(json.dumps({'scanned': index, 'total': len(files)}, ensure_ascii=False), flush=True)
    summary = {'files': len(files), 'extensions': dict(extensions), 'errors': dict(errors)}
    (OUT / 'scan_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
