"""Summarize question taxonomy from read-only legacy XLS metadata."""
import collections
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RECORDS = [json.loads(line) for line in (ROOT / "corpus_audit/xls_question_metadata.jsonl").open(encoding="utf-8")]
CATEGORIES = {
    "图形": {"数量类", "样式类", "重构类", "位置类", "创新类（图形）", "复合类（图形）"},
    "定义": {"单定义", "多定义"},
    "类比": {"映射类", "集合类", "语义类", "语法类", "复合类（类比）"},
    "逻辑": {"论证类", "其他论证", "分析推理", "翻译推理", "归纳推理", "原因解释", "真假推理", "平行结构"},
}


def describe(record):
    result = {}
    for name, labels in CATEGORIES.items():
        hits = [q for q in record["questions"] if q["point"] in labels]
        nums = [int(q["no"]) for q in hits if isinstance(q["no"], (int, float))]
        result[name] = {"count": len(hits), "start": min(nums) if nums else None, "end": max(nums) if nums else None}
    return result


national = [r for r in RECORDS if "国家公务员考试" in r["path"]]
print("NATIONAL")
for record in national:
    print(record["path"].split("/")[-1], len(record["questions"]), describe(record))

print("OVERALL")
for group, subset in [
    ("行测", [r for r in RECORDS if "公务员笔试-行测真题试卷" in r["path"]]),
    ("职测", [r for r in RECORDS if "事业单位笔试-职测真题试卷" in r["path"]]),
    ("自建", [r for r in RECORDS if "自建试卷" in r["path"]]),
]:
    counters = {name: collections.Counter() for name in CATEGORIES}
    hit_files = collections.Counter()
    for r in subset:
        d = describe(r)
        for name in CATEGORIES:
            counters[name].update(q["point"] for q in r["questions"] if q["point"] in CATEGORIES[name])
            if d[name]["count"]:
                hit_files[name] += 1
    print(group, "files", len(subset), "hits", dict(hit_files))
    for name, counter in counters.items():
        print(name, counter.total(), counter.most_common())

print("METADATA_QUALITY")
all_questions = [q for r in RECORDS for q in r["questions"]]
print("questions", len(all_questions))
print("point_blank", sum(not q["point"].strip() for q in all_questions))
print("answer_blank", sum(not q["answer"].strip() for q in all_questions))
print("answer_values", collections.Counter(q["answer"] for q in all_questions).most_common(25))
print("bad_number_files", [r["path"] for r in RECORDS if any(not isinstance(q["no"], (int, float)) for q in r["questions"])][:15])
print("nonsequential_number_files", sum(
    any(int(b["no"]) != int(a["no"]) + 1 for a, b in zip(r["questions"], r["questions"][1:]))
    for r in RECORDS if all(isinstance(q["no"], (int, float)) for q in r["questions"])
))
