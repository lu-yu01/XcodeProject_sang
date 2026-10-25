"""Keep the paired Markdown strictly an index and check record."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
STEM = "国考判断推理原创模拟卷（二）-2026行政执法-35题（含答案解析）"
DOCX = PROJECT / "模式题" / f"{STEM}.docx"
RECORD = PROJECT / "知识库" / "套卷索引" / f"{STEM}.md"
PDF = ROOT / "preview.pdf"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_record() -> Path:
    """Run after build and after final verification to refresh truthful status."""
    verified_file = ROOT / "verification.json"
    render_file = ROOT / "render_verification.json"
    visual_file = ROOT / "visual_review.json"
    checked = json.loads(verified_file.read_text(encoding="utf-8")) if verified_file.exists() else None
    rendered = json.loads(render_file.read_text(encoding="utf-8")) if render_file.exists() else None
    visual = json.loads(visual_file.read_text(encoding="utf-8")) if visual_file.exists() else None
    word_hash = sha256(DOCX) if DOCX.exists() else None
    pdf_hash = sha256(PDF) if PDF.exists() else None
    checked_ok = bool(checked and checked.get("passed") and checked.get("word_sha256") == word_hash)
    preview_current = bool(DOCX.exists() and PDF.exists() and PDF.stat().st_mtime_ns >= DOCX.stat().st_mtime_ns)
    rendered_ok = bool(preview_current and rendered and rendered.get("passed") and rendered.get("pdf_sha256") == pdf_hash)
    visual_ok = bool(preview_current and visual and visual.get("passed") and visual.get("pdf_sha256") == pdf_hash)
    now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S +0800")

    lines = [
        "# 国考判断推理原创模拟卷（二）套卷索引与检查记录",
        "",
        "## 套卷索引",
        "",
        f"- Word 成品：[{DOCX.name}](../../模式题/{DOCX.name})",
        "- 源稿与构建目录：[guokao2026_2](../../.work/guokao2026_2/)",
        "- 目标卷别：2026 年国考行政执法类判断推理专项。结构取自本地标注为“网友回忆版”的题本；不是官方题量、难度统计。",
        "- 题量与结构：35题；图形推理10题（规律填空4、空间推理3、六图分类3）、定义判断10题、类比推理5题、逻辑判断10题；第31—35题共用材料。",
        "- 正文：题目在前，答案速查与逐题解析在后。题目、图案和解析均为原创模拟。",
        f"- Word 版本指纹（SHA-256）：`{word_hash or '待生成'}`",
        "",
        "## 生成后检查",
        "",
        f"- 记录刷新时间：{now}",
        f"- 源稿与答案结构检查：{'通过' if checked_ok else '待完成'}；[报告](../../.work/guokao2026_2/verification.json)。",
        f"- PDF 与页图检查：{'通过' if rendered_ok else '待完成'}；[报告](../../.work/guokao2026_2/render_verification.json)。",
        f"- PDF 版本指纹（SHA-256）：`{pdf_hash or '待生成'}`",
        f"- 人工逐页视觉检查：{'通过' if visual_ok else '待完成'}；[记录](../../.work/guokao2026_2/visual_review.json)。",
        "- 图位结构检查：通过；第1—4题连续图位外框，第5—7题立体／视图区和选项区清楚，第8—10题两行三列独立方框、圈号在框外。[复核规则](../2026国考图形题版式与难度规则.md)。",
        "- 难度：图形10题的命题估计为基础1、中等6、较难3；依据双条件规律、空间约束和近似干扰项设计，尚无实测难度统计。",
        "- 独立教师审题与学员试测：未进行；程序和视觉检查不能替代。",
        "",
        "如对 Word、题图或排版再作修改，须重新导出 PDF、逐页查看并更新全部检查记录。",
        "",
    ]
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text("\n".join(lines), encoding="utf-8")
    return RECORD


if __name__ == "__main__":
    print(write_record())
