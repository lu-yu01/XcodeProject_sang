"""Verify knowledge-base links and published corpus indexes."""
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "知识库"
AUDIT = ROOT / ".work/corpus_audit"
failures = []


def markdown_targets(text):
    """Yield link targets, allowing balanced parentheses in file names."""
    i = 0
    while True:
        start = text.find("](", i)
        if start < 0:
            return
        depth = 1
        j = start + 2
        while j < len(text) and depth:
            if text[j] == "(" and (j == 0 or text[j - 1] != "\\"):
                depth += 1
            elif text[j] == ")" and (j == 0 or text[j - 1] != "\\"):
                depth -= 1
            j += 1
        if depth == 0:
            target = text[start + 2:j - 1].strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            yield target
        i = j


all_md = list(ROOT.rglob("*.md"))
for file in all_md:
    if not file.is_relative_to(KB):
        failures.append(f"Markdown outside knowledge base: {file}")
    for target in markdown_targets(file.read_text(encoding="utf-8")):
        if target.startswith(("http:", "https:", "mailto:", "#")):
            continue
        clean = target.split("#", 1)[0]
        if not (file.parent / clean).exists():
            failures.append(f"Broken link: {file.relative_to(ROOT)} -> {target}")

manifest = [json.loads(line) for line in (AUDIT / "manifest.jsonl").open(encoding="utf-8")]
metadata = [json.loads(line) for line in (AUDIT / "xls_question_metadata.jsonl").open(encoding="utf-8")]
with (KB / "资料索引/真题文件清单.csv").open(encoding="utf-8-sig", newline="") as f:
    source_rows = list(csv.DictReader(f))
with (KB / "资料索引/判断推理题型结构索引.csv").open(encoding="utf-8-sig", newline="") as f:
    taxonomy_rows = list(csv.DictReader(f))
source_paths = [row["源文件路径（工程根目录相对）"] for row in source_rows]
metadata_paths = [row["表格路径（工程根目录相对）"] for row in taxonomy_rows]
if source_paths != [item["path"] for item in manifest]:
    failures.append("Source catalog order/paths differ from audit manifest")
if metadata_paths != [item["path"] for item in metadata]:
    failures.append("Taxonomy catalog order/paths differ from XLS metadata")
for path in source_paths:
    if not (ROOT / path).is_file():
        failures.append(f"Missing source file: {path}")
for path in metadata_paths:
    if not (ROOT / path).is_file():
        failures.append(f"Missing taxonomy source: {path}")

print(f"Markdown files: {len(all_md)}; source rows: {len(source_rows)}; taxonomy rows: {len(taxonomy_rows)}; failures: {len(failures)}")
for message in failures[:30]:
    print(message)
if failures:
    raise SystemExit(1)
