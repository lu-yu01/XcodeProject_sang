"""Publish traceable corpus catalogs in the knowledge base from read-only audit data."""
import csv
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
AUDIT = PROJECT / ".work/corpus_audit"
DEST = PROJECT / "知识库/资料索引"
DEST.mkdir(parents=True, exist_ok=True)
manifest = [json.loads(line) for line in (AUDIT / "manifest.jsonl").open(encoding="utf-8")]
metadata = [json.loads(line) for line in (AUDIT / "xls_question_metadata.jsonl").open(encoding="utf-8")]
by_path = {item["path"]: item for item in metadata}

CATEGORIES = {
    "图形": {"数量类", "样式类", "重构类", "位置类", "创新类（图形）", "复合类（图形）"},
    "定义": {"单定义", "多定义"},
    "类比": {"映射类", "集合类", "语义类", "语法类", "复合类（类比）"},
    "逻辑": {"论证类", "其他论证", "分析推理", "翻译推理", "归纳推理", "原因解释", "真假推理", "平行结构"},
}

with (DEST / "真题文件清单.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["源文件路径（工程根目录相对）", "格式", "字节", "SHA256", "初步范围（仅按路径）", "初步来源（仅按路径）", "文本字数", "图片数", "页数或幻灯片数", "读取状态"])
    for item in manifest:
        if item["path"].split("/")[-1].startswith("~$"):
            status = "Office临时锁文件，不是试题源件"
        elif "error" in item:
            status = item["error"]
        elif item["extension"] == ".xls" and item["path"] in by_path:
            status = "题序/知识点/答案已读取；同名Word另见清单"
        elif item["extension"] == ".xls":
            status = "仅建索引；非本次判断推理题型统计范围"
        elif item["extension"] in {".docx", ".pdf", ".pptx"}:
            status = "文字结构已扫描；图像内容需按命题任务复看"
        else:
            status = "文件已建索引；非可直接提取试题格式"
        writer.writerow([
            item["path"], item["extension"], item["bytes"], item["sha256"],
            item["subject"], item["provenance"], item.get("text_chars", ""),
            item.get("embedded_media", ""), item.get("pages", item.get("slides", "")), status,
        ])

with (DEST / "判断推理题型结构索引.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.writer(stream)
    head = ["表格路径（工程根目录相对）", "表格题目行数", "知识点空白行数", "答案空白行数", "非单选答案行数", "题号不连续"]
    for category in CATEGORIES:
        head.extend([f"{category}标签题数", f"{category}起始题号", f"{category}末题题号"])
    writer.writerow(head)
    for item in metadata:
        questions = item["questions"]
        row = [
            item["path"], len(questions), sum(not q["point"].strip() for q in questions),
            sum(not q["answer"].strip() for q in questions),
            sum(bool(q["answer"].strip()) and q["answer"].strip() not in {"A", "B", "C", "D"} for q in questions),
            int(any(int(b["no"]) != int(a["no"]) + 1 for a, b in zip(questions, questions[1:])
                    if isinstance(a["no"], (int, float)) and isinstance(b["no"], (int, float)))),
        ]
        for labels in CATEGORIES.values():
            numbers = [int(q["no"]) for q in questions if q["point"] in labels and isinstance(q["no"], (int, float))]
            row.extend([len(numbers), min(numbers) if numbers else "", max(numbers) if numbers else ""])
        writer.writerow(row)

print("published", len(manifest), "source rows and", len(metadata), "question-table rows")
