"""Refresh media-file counts in a manifest made by an older scanner revision."""
import json
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
manifest = ROOT / ".work/corpus_audit/manifest.jsonl"
temporary = manifest.with_suffix(".corrected.jsonl")
fixed = 0
with manifest.open(encoding="utf-8") as source, temporary.open("w", encoding="utf-8") as target:
    for line in source:
        item = json.loads(line)
        if "embedded_media" in item and item["extension"] in {".docx", ".pptx"}:
            prefix = "word/media/" if item["extension"] == ".docx" else "ppt/media/"
            with ZipFile(ROOT / item["path"]) as archive:
                count = sum(name.startswith(prefix) and not name.endswith("/") for name in archive.namelist())
            fixed += count != item["embedded_media"]
            item["embedded_media"] = count
        target.write(json.dumps(item, ensure_ascii=False) + "\n")
temporary.replace(manifest)
print("corrected media counts:", fixed)
