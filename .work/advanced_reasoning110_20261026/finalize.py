import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent.parent
NAME='国考判断推理进阶专项练习-110题（含答案解析）'
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def local_links(path):
    text=path.read_text(encoding='utf-8');out=[]
    for m in re.finditer(r'\]\(',text):
        j=m.end();start=j;depth=1
        while j<len(text) and depth:
            if text[j]=='(':depth+=1
            elif text[j]==')':depth-=1
            j+=1
        if depth:raise AssertionError((str(path),'unclosed Markdown target'))
        target=text[start:j-1].strip().strip('<>')
        if target.startswith(('http:','https:','#','mailto:','codex:')):continue
        target=target.split('#')[0]
        if target:out.append((target,(path.parent/target).resolve()))
    return out
def main():
    info=read('build_info.json');d=read('document_verification.json');cross=read('cross_review_verification.json');manifest=read('page_manifest.json')
    assert d['passed'] and cross['passed']
    word=Path(info['word']);pdf=ROOT/'preview.pdf'
    assert sha(word)==info['word_sha256']==d['word_sha256']==manifest['word_sha256']
    assert sha(pdf)==d['pdf_sha256']==manifest['pdf_sha256']
    reports=[];coverage={}
    for filename in ['visual_review_a.json','visual_review_b.json','visual_review_c.json']:
        v=read(filename)
        assert v['word_sha256']==sha(word) and v['pdf_sha256']==sha(pdf)
        rows=v['pages'];reports.append(dict(path=filename,sha256=sha(ROOT/filename),pages=len(rows)))
        for row in rows:
            p=int(row['page']);assert p not in coverage,(p,'duplicate coverage')
            viewed=any(row.get(k) is True for k in ['actually_viewed','actual_viewed','actual_image_viewed','viewed'])
            assert viewed and row['passed'],(filename,row)
            target=manifest['pages'][p-1]
            assert row.get('sha256',row.get('png_sha256'))==target['sha256']==sha(target['path'])
            coverage[p]=filename
    assert set(coverage)==set(range(1,d['pages']+1))
    visual=dict(passed=True,word_sha256=sha(word),pdf_sha256=sha(pdf),pages=d['pages'],all_pages_actually_viewed=True,
      reports=reports,coverage=coverage,scope='58张最终PDF150dpi页图由3名代理逐张实际打开；根代理补看关系图、共材、答案表等关键页。不是教师审题。')
    write('visual_verification.json',visual)
    protected=read('existing_word_baselines.json')
    for x in protected:assert sha(x['path'])==x['sha256'],x['path']
    # Native source pictures and the reference are preserved before removing only current rendered pages.
    retained=[word,pdf,*sorted((ROOT/'assets').glob('*')),*sorted((ROOT/'reference').glob('*'))]
    keep_hash={str(p):sha(p) for p in retained if p.is_file()}
    target_dir=(ROOT/'render').resolve()
    assert target_dir.parent==ROOT.resolve() and target_dir.name=='render'
    files=sorted(target_dir.glob('page-*.png'))
    assert len(files)==d['pages']
    deleted=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
    for p in files:
        assert p.resolve().parent==target_dir and re.fullmatch(r'page-\d+\.png',p.name)
        p.unlink()
    assert not list(target_dir.glob('page-*.png'))
    assert all(sha(p)==h for p,h in keep_hash.items())
    cleanup=dict(date='2026-10-26',deleted_count=len(deleted),bytes_freed=sum(x['bytes'] for x in deleted),
      scope='仅本轮render/page-*.png，逐页检查后删除；PDF、源图、参考图、源稿与检查报告保留',deleted=deleted,retained_sha256=keep_hash,retained_unchanged=True)
    write('png_cleanup.json',cleanup)
    title=BASE/'知识库'/'套卷索引'/(NAME+'.md')
    title.write_text(f'''# {NAME}

- Word：[110题成品](../../模式题/{NAME}.docx)
- 源稿与模型：[本轮独立工作目录](../../.work/{ROOT.name}/)
- 版本：2026-10-26最终稿，共{d['pages']}页；题目在前，答案表与逐题解析在后。
- 状态：生成、内容检查、代理独立试解及修订复核、最终逐页视觉检查已完成。
- 本文件仅作索引与检查记录，不复制完整题目、题图和解析。

## 题量与参考

| 范围 | 内容 |
| --- | --- |
| 1—20 | 类比推理20题，含两道概念集合关系图 |
| 21—50 | 定义判断30题，正问/选非、多定义、程序与比率等 |
| 51—65 | 三组一拖五共15题：配置、多对多分配、共享资源排程 |
| 66—80 | 独立15题：翻译4、真假4、分析4、平行结构3 |
| 81—110 | 逻辑论证30题：加强10、削弱10、前提4、解释3、评价2、归纳1 |

以2022—2026国考为主，近期2026和2025题面优先，地方考试辅助；分模块共107条具体题例研究记录，不代表频率统计或107份卷。配额由用户指定，属于专项练习。[研究与蓝图](../近五年文字判断推理研究与110题蓝图.md)、[固定命题规则](../文字判断推理进阶命题规则.md)已归档；具体资料真实性和年份边界见四份sources报告。

## 内容与答案检查

- 110连续题号、440文字选项、110答案及解析、四模块答案表逐项一致；Word原生题号/选项编号使用完整。
- 三组共材基准10、56、17解，逐选项验证成立见证或反例，新增条件每题重置。独立推理保留真值、量词反例空间或结构同构检查。
- 类比语义标签、定义要件矩阵及论证数值检查不冒充自然语言自动证明。各模块程序范围如实记录在[模型报告](../../.work/{ROOT.name}/model_verification.json)。
- 110题均有非作者代理或根代理未见答案的首次试解，首选与作者答案一致；首轮仍发现定义要件不自足、必要前提过强及类比偏弱等问题，已保留记录并修订。修订复核者知晓首轮选择，不称为全新盲审。[交叉检查汇总](../../.work/{ROOT.name}/cross_review_verification.json)。
- 第28题补明参与者未知分组；27、37、48补明独立抽样、原理功能与明确目标。第95题澄清成本基数及加成比例；101前提限本批对象；102按净变化判断，不用毛新增代替。类比6、7、17收紧关系，其余若干干扰项提高贴近度。

## 最终版式检查

- 打包render_docx.py已实际尝试，因本机PATH缺少soffice.exe失败；保留诊断后改用独立、隐藏、只读、禁用宏的Microsoft Word实例导出PDF，再以150dpi生成页图。
- [成品文字/编号/图文绑定报告](../../.work/{ROOT.name}/document_verification.json)：所有题干、四项及完整解析均在对应页中，无题目块或解析块拆页；共用材料与首题同页，三组各五题也均同页。
- 最终58页由三个代理逐张实际打开查看，覆盖1—20、21—40、41—58页，根代理补看关键页。未见裁切、重叠、缺字、图形拉伸或页码问题。[逐页汇总](../../.work/{ROOT.name}/visual_verification.json)。
- 临时页图已于2026-10-26清理：删除{len(deleted)}张，释放{cleanup['bytes_freed']:,}字节；保留2张原创关系图、1张参考图、PDF、源稿与报告。保留文件指纹均未变化。[清理清单](../../.work/{ROOT.name}/png_cleanup.json)。再次查看须从保留PDF重建；修改Word须重新导出并复核。
- 原有{len(protected)}份Word指纹与开工基线相同，未覆盖旧成品。

## 文件指纹与适用边界

- Word SHA-256：`{sha(word)}`
- PDF SHA-256：`{sha(pdf)}`
- 单一题目源SHA-256：`{sha(ROOT/'questions.json')}`
- 难度为命题估计，保留中等至较难梯度；代理试解不能替代独立教师盲审、学员试测及实测难度统计。以上三项外部检验未开展。
''',encoding='utf-8')
    project=BASE/'知识库'/'项目说明.md';s=project.read_text(encoding='utf-8')
    insertion=f'''\n新增[文字判断推理进阶110题](./套卷索引/{NAME}.md)：类比20、定义30、逻辑推理30、逻辑论证30；推理含3组一拖五和15道独立题，题目与解析集中分开。共58页，程序核对、110题非作者首次试解及必要修订、全部页面实际复核完成；原有8份Word保留。研究依据与可复用结论见[近五年文字研究与蓝图](./近五年文字判断推理研究与110题蓝图.md)、[文字进阶命题规则](./文字判断推理进阶命题规则.md)。工作目录为[本轮源稿与检查](../.work/{ROOT.name}/)，临时58张页图已清理，原始题图、PDF、模型及报告保留。\n'''
    if insertion not in s:s=s.replace('\n## 目录\n',insertion+'\n## 目录\n')
    project.write_text(s,encoding='utf-8')
    log=BASE/'知识库'/'建议与变更记录.md';s=log.read_text(encoding='utf-8')
    s=s.replace('## 2026-10-26 文字判断推理进阶110题（制作中）','## 2026-10-26 文字判断推理进阶110题')
    s=s.replace('- 当前状态：四模块源稿已形成；作者自审、模型验证、代理无答案交叉试解和最终Word逐页验收正在进行。最终结论及实际检查范围将在成品索引回填。',
      f'- 完成：[110题成品及检查索引](./套卷索引/{NAME}.md)，58页，题目在前、答案解析在后。107条分模块题例研究记录已归档，110题首次非作者试解与作者首选一致，仍发现并修正类比层级、定义双盲和必要要件、论证成本口径及必要前提过强等问题；首轮异议和后续复核分别保留。\n- 最终验证：110题/440选项/答案表/全部解析文字与Word/PDF一致，三组共材10/56/17基准解且逐项有见证反例，最终58页均逐张实际查看通过。既有8份Word指纹不变。检查后清理58张临时页图，保留题图、参考图、PDF和报告。难度为命题估计，未进行教师盲审、学员试测。')
    log.write_text(s,encoding='utf-8')
    files=[title,project,log,BASE/'知识库'/'文字判断推理进阶命题规则.md',BASE/'知识库'/'近五年文字判断推理研究与110题蓝图.md']
    links=[]
    for p in files:
        for target,resolved in local_links(p):
            assert resolved.exists(),(p,target,resolved)
            links.append(dict(file=str(p),target=target,exists=True))
    audit=dict(passed=True,date='2026-10-26',word=str(word),word_sha256=sha(word),pdf_sha256=sha(pdf),pages=d['pages'],questions=110,
      visual_pages=58,independent_questions=110,protected_existing_words=len(protected),protected_words_unchanged=True,
      source_modules={n:sha(ROOT/(n+'.py')) for n in ['analogy','definitions','formal','arguments']},
      source_json_sha256=sha(ROOT/'questions.json'),markdown_links_checked=len(links),links=links,preview_pngs_removed=True,
      limitations=['未进行教师盲审、学员试测或难度统计','代理首次答案一致不等同没有题面缺陷，首轮问题及修复均另记录'])
    write('final_audit.json',audit)
    print({k:audit[k] for k in ['passed','pages','questions','visual_pages','independent_questions','protected_existing_words','preview_pngs_removed']})
if __name__=='__main__':main()
