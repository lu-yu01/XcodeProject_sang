"""Print bounded text around a marker or question number in one DOCX."""

import argparse
from pathlib import Path
import re
import sys
from zipfile import ZipFile

from lxml import etree


W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def paragraphs(path):
    with ZipFile(path) as archive:
        with archive.open('word/document.xml') as xml:
            for _, para in etree.iterparse(xml, events=('end',), tag=W + 'p', recover=True, huge_tree=True):
                value = ' '.join(''.join(node.text or '' for node in para.iter(W + 't')).split())
                if value:
                    yield value
                para.clear()
                while para.getprevious() is not None:
                    del para.getparent()[0]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path)
    parser.add_argument('--match', default='判断推理')
    parser.add_argument('--after', type=int, default=12)
    parser.add_argument('--limit', type=int, default=3)
    args = parser.parse_args()
    lines = list(paragraphs(args.path))
    hits = [i for i, line in enumerate(lines) if re.search(args.match, line)]
    print(f'{args.path.name}: {len(lines)} nonempty paragraphs, {len(hits)} matches')
    for i in hits[:args.limit]:
        print(f'--- paragraph {i + 1} ---')
        for j in range(i, min(len(lines), i + args.after)):
            print(f'{j + 1}: {lines[j][:220]}')


if __name__ == '__main__':
    main()
