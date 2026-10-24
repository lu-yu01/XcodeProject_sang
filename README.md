# 公考判断推理命题与质检工程

本工程保存判断推理真题样本、原创模拟卷、命题规范及第一套模拟卷的生成和校验记录。当前成品为35道单选题：图形推理10题、定义判断10题、类比推理5题、逻辑判断10题；第31—35题共用材料。试卷先列题目，后列答案与逐题解析。

## 目录

| 路径 | 内容 |
| --- | --- |
| [`真题/`](./真题/) | 国考、北京和山东真题样本；保留原始编辑问题，不能直接当作无误题库 |
| [`模式题/`](./模式题/) | 已完成的原创模拟卷 Word 成品 |
| [`规范/`](./规范/) | 基础命题规范、35题固定模板和制作质检经验 |
| [`.work/guokao35/`](./.work/guokao35/) | 模拟卷（一）的源稿、题图、构建脚本、校验结果和预览 |

新卷先阅读[固定模板](./规范/国考判断推理35题出卷固定模板.md)和[质检规范](./规范/国考判断推理模拟卷制作经验与质检规范.md)，并以[基础命题规范](./规范/公考判断推理真题命题与解析规范.md)为风格依据。每套新卷应使用独立工作目录；现有脚本和断言针对模拟卷（一），直接运行 `build.py` 会覆盖其 Word 成品。

## 模拟卷（一）的生成与检查

脚本需要 Python 3.12 及 `python-docx`、`Pillow`、`lxml`、`pypdf`；PDF 预览脚本需要本机 Microsoft Word。生成和校验程序位于 [`.work/guokao35/`](./.work/guokao35/)。在工程根目录依次执行：

```powershell
python .work/guokao35/build.py
python .work/guokao35/verify.py
pwsh -NoProfile -File .work/guokao35/render_word.ps1
```

将最新的 `preview.pdf` 逐页转为 `render/page-01.png` 等页图后，再运行：

```powershell
python .work/guokao35/verify_render.py
```

最后一步同时核对 PDF 页数与 `render/` 中的页图集合，出现缺页或旧页会报错。数学和有限状态检查覆盖第1—10题、第30—35题；其余题目的语义审查、独立教师审题和学员试测不能由这些脚本代替。现有[校验报告](./.work/guokao35/verification.json)和[渲染校验报告](./.work/guokao35/render_verification.json)对应模拟卷（一）的19页成品。
