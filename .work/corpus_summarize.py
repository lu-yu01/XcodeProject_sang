"""Summarize the read-only exam corpus scan for human review."""

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import statistics


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / '.work' / 'corpus_audit'
ITEMS = [json.loads(line) for line in (AUDIT / 'manifest.jsonl').read_text(encoding='utf-8').splitlines()]


def collection(item):
    parts = Path(item['path']).parts
    if len(parts) >= 4 and parts[1] == '试卷':
        return '/'.join(parts[1:3])
    if len(parts) >= 3:
        return '/'.join(parts[1:3])
    return '/'.join(parts[1:])


def base_name(item):
    stem = Path(item['path']).stem
    stem = re.sub(r'_20\d{6}_?\d{2}_?\d{2}$', '', stem)
    stem = re.sub(r'\(\d+\)$', '', stem)
    return stem


def main():
    groups = defaultdict(list)
    hashes = defaultdict(list)
    subjects = Counter()
    provenance = Counter()
    for item in ITEMS:
        groups[collection(item)].append(item)
        hashes[item['sha256']].append(item)
        subjects[item['subject']] += 1
        provenance[item['provenance']] += 1
    word_bases = {base_name(item) for item in ITEMS if item['extension'] == '.docx' and 'error' not in item}
    xls = [item for item in ITEMS if item['extension'] == '.xls']
    exact_duplicates = [values for values in hashes.values() if len(values) > 1]
    summary = {
        'files': len(ITEMS),
        'extensions': dict(Counter(item['extension'] for item in ITEMS)),
        'subjects_by_path': dict(subjects),
        'provenance_by_path': dict(provenance),
        'collections': [
            {'name': name, 'files': len(values), 'extensions': dict(Counter(item['extension'] for item in values)),
             'text_read': sum(item.get('text_chars', 0) > 0 for item in values),
             'text_chars': sum(item.get('text_chars', 0) for item in values),
             'errors': sum('error' in item for item in values)}
            for name, values in sorted(groups.items(), key=lambda group: (-len(group[1]), group[0]))
        ],
        'xls_with_matching_word_name': sum(base_name(item) in word_bases for item in xls),
        'xls_total': len(xls),
        'exact_duplicate_sets': len(exact_duplicates),
        'extra_exact_duplicate_copies': sum(len(values) - 1 for values in exact_duplicates),
        'errors': [{'path': item['path'], 'error': item['error']} for item in ITEMS if 'error' in item],
    }
    (AUDIT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in summary.items() if key != 'collections'}, ensure_ascii=False, indent=2))
    print('TOP COLLECTIONS')
    for row in summary['collections'][:25]:
        print(row['name'], row['files'], row['extensions'], 'text_read', row['text_read'])


if __name__ == '__main__':
    main()
