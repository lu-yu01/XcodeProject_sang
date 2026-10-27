from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent;PROJECT=ROOT.parents[1];KB=PROJECT/'知识库'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
names={
 'house':('房屋线描','https://openclipart.org/detail/213780/house-lineart','https://openclipart.org/download/213780'),
 'car':('汽车线描','https://openclipart.org/detail/215974/car-lineart','https://openclipart.org/download/215974'),
 'tree':('自然树线描','https://openclipart.org/detail/213774/tree-lineart','https://openclipart.org/download/213774'),
 'lamp':('无背景路灯','https://openclipart.org/detail/251873/street-lamp-without-background','https://openclipart.org/download/251873'),
 'library':('图书馆建筑','https://freesvg.org/library-building-icon','https://freesvg.org/download/205739'),
 'shop':('商店外观','https://freesvg.org/supermarket-building','https://freesvg.org/download/199559'),
 'clock':('钟楼外观','https://freesvg.org/art-deco-clock-tower','https://freesvg.org/download/59933'),
 'person':('摄影者','https://openclipart.org/detail/21887/comic-characters-photographer','https://openclipart.org/download/21887'),
 'cinema':('影院外观','https://freesvg.org/odeon-cinema-building-vector-image','https://freesvg.org/download/30020')}
manifest=[]
for name,(label,page,download) in names.items():
    p=ROOT/'sources'/f'{name}.svg'
    manifest.append({'name':name,'label':label,'source_page':page,'download_url':download,'original_svg_sha256':sha(p),
       'license':'CC0 / Public Domain as stated on source service page','license_evidence':'https://openclipart.org/share' if 'openclipart' in page else page,
       'use':'Native scene bases and explanatory diagrams; main question scenes unified with built-in image generation; original source vectors preserved.'})
dump(ROOT/'source_manifest.json',manifest)
gen=json.loads((ROOT/'imagegen_final.json').read_text(encoding='utf8'))
for n in [1,7]:
    rev=json.loads((ROOT/f'q{n}_revision.json').read_text(encoding='utf8'))
    rec=next(x for x in gen if x['n']==n);rec['superseded_generated_path']=rec['generated_path'];rec['generated_path']=rev['generated_path'];rec['revision_record']=f'q{n}_revision.json'
for rec in gen:
    rec['workspace_asset']=str(ROOT/'assets'/f'question-{rec["n"]:02}.png');rec['sha256']=sha(Path(rec['workspace_asset']))
dump(ROOT/'selected_assets.json',gen)

rule=KB/'情境方向图形题命题与检查规则.md';t=rule.read_text(encoding='utf8')
heading='## 2026-10-28 生活化素材与场景表现规则'
addition='''用户反馈原10题使用空方盒、点与小框过多，缺少生活辨识度。后续情境方向题按以下标准制作。

1. 先搜房屋、街景建筑、树木、路灯、车辆、影院和人物等生活素材，检查实际原图，不只读取搜索描述。记录来源页、下载链接、许可说明及源文件指纹；原始素材留存，正式图源和临时预览分开。
2. 主图采用一致的黑白生活场景线描，建筑有可辨的门窗、屋顶、檐口、钟面或门头，树有自然树冠及树干，路灯有灯具。不能只在空方盒旁加“影院”就称为生活化，也不能只添加无关背景装饰。
3. 跨帧保持地标身份，屋顶、门窗、钟面、路牌和近远层次可稳定追踪；相邻帧允许画笔细节差异，但不能把同一地标改成另一栋建筑。凡涉及遮挡，必须实际画出可见遮挡边界。
4. 地图用建筑占地或门口、人物脚点作锚点。装饰图标不等于坐标；点光源须明确画出并命名地面投影，不能把偏出灯杆的灯头或图标中心默认为光源坐标。必要的定位点和方向箭头可以保留，但不能只以圆点和文字替代生活场景。
5. 不考距离时，草图可以单调拉开间距以避免图标、标签相互遮挡，但必须保持所有被考查的前后左右、同轴及次序关系，且题干声明不按距离比例。四候选仍横排共同外框，字母在框外下方。
6. 图片生成仅用于艺术表现，生成提示中的“保持几何”不构成验收证据。若题干要求等角、等距、精确尺寸或光线并发等条件，必须由确定性投影保证，或重新验证最终图；不能核实的定量条件应重做或合理删去。最终润饰图按定性方向示意使用，不把其细部线条当作相机标定数据。
7. 搜图不能把互不相关的街景照片当成同一连拍。若素材自带太阳、影子、背景或视角，应先核对它们是否加入额外条件；影子题应保留可验的光源、地面方向及唯一正确候选。
8. 换图后重新让非作者只看最终题干和图片试解，冻结首次答案；修改地标身份、光源标记或关键条件后另存复核。答案一致不代表图面合格，仍须检查同景身份、遮挡、影向、缺物和文字遮盖。
9. 同一题的题图与解释图保持实体名称和逻辑一致，解释图可以用方向示意帮助说明。Word保留图片比例，并实际导出检查所有最终页；只清理临时预览PNG，保存正式素材、源稿、首次试解和修订历史。

本轮换图修正第1题地标屋顶不一致、生成过程中漏路牌、第3题隐藏展馆露在错误一侧、第8题相邻建筑遮盖；第4题删除无法从润饰图严格保证的等角条件，第7题补明光源地面投影。修订后重新复核；图源和提示词见[本轮工作目录](../.work/direction_life10_20261028/)，当前成品检查见[套卷索引](./套卷索引/北京风格情境方向图形推理-10题（含答案解析）.md)。
'''
if heading not in t:rule.write_text(t+'\n\n'+heading+'\n\n'+addition,encoding='utf8')

index=KB/'套卷索引'/'北京风格情境方向图形推理-10题（含答案解析）.md'
t=index.read_text(encoding='utf8')
current='当前版本：2026-10-28生活化换图版，Word同名更新；下方原始制作记录保留为历史，最新指纹及检查见本页末尾。'
if current not in t:
    first,rest=t.split('\n',1);t=first+'\n\n'+current+'\n'+rest
section='## 2026-10-28 生活化换图记录'
if section not in t:
    rows='\n'.join(f'| {label} | [来源页]({page}) |' for label,page,_ in names.values())
    t+=f'''\n\n{section}

- 处理：搜图选材后统一为黑白生活场景线描，重做10题主图和10张解释图。房屋、树木、汽车、路灯、影院、商店、图书馆、人物和钟楼素材用于原生图稿与解释，主图结合内置图片生成工具润饰；未把多张无关街景当作同一连拍。
- 逻辑修订：第1题统一左邻建筑三角山墙并恢复生成时遗漏的②路牌；第3题将隐藏展馆恢复到钟楼左侧；第4题取消等角条件，保留原地连续右转、不平移、不变焦；第7题用黑点及“光源投影”明确地面坐标，并同步修订题干。答案保持原顺序。
- 版式：保留原Word的节、样式、编号、关系、主题及其他包内部分，仅更新20张嵌图、相应图片高宽比和两处必要题干。第8—10题候选图腾出更多纵向空间，图标与文字分开；实际Word导出仍为10页，所有10页已实际逐页打开。
- 独立试解：两名非作者只读取公开题干及最终PNG，首次答案为1B、2D、3A、4C、5C、6A、7D、8B、9C、10A。发现的问题与修改后复看另存，首次文件不覆盖。第1、4、7题均经原复核者重新查看并关闭阻断问题；轻微画笔、窗格差异不用于精确量角或距离推断。
- 检查：20张Word嵌图与正式图源逐张指纹匹配，比例正确；题干、选项、答案及解析与最终PDF文字对应。最终图面试解、10页实际目视、包内保留项及其他12份Word指纹均复核。
- 当前成品SHA-256：`{sha(ROOT/'revised.docx')}`；内部PDF SHA-256：`{sha(ROOT/'preview.pdf')}`。
- 源稿：[生活化换图工作目录](../../.work/direction_life10_20261028/)。原Word备份为工作目录 `source.docx`，正式图源为 `assets/`，原始搜索素材为 `sources/`，原生图稿为 `svg/`。
- 溯源：`source_manifest.json` 保存来源及下载指纹；`imagegen_final.json`、`q1_revision.json`、`q7_revision.json` 和 `selected_assets.json` 保存内置生成工具、提示词、修订及最终图片指纹。脚本模型验证属于基础图几何验证，最终润饰PNG另外通过实际读图检查，不能把两者混称逐像素几何认证。
- 最终记录：`visual_review.json`、`final_check.json`，首次试解为 `life_first_*.json`，复核及关闭记录为 `life_blind_*.json`、`life_revision_closure_*.json`。检查后清理本轮临时页面和素材预览PNG，保留20张正式图源、9张原始SVG、Word备份、PDF、原生SVG、提示词及全部审稿历史，见 `cleanup.json`。
- 新规范：[生活化素材与场景表现规则](../情境方向图形题命题与检查规则.md)。这次是换图和条件澄清，仍为原创专项；难度未做学员实测，代理试解不替代教师审题。

素材来源如下，许可记录以本轮保存的官方来源为准。

| 素材 | 官方来源 |
|---|---|
{rows}

复现时直接用保留的最终 `assets/` 运行 `edit_docx.py` 即可重建换图Word。`scenes.py` 与 `raster.cjs` 生成的是原生基础图，会覆盖同名PNG；不得在已选择的润饰图上无备份全量重跑。提示词不能保证再次生成像素相同的图片。
'''
index.write_text(t,encoding='utf8')

log=KB/'建议与变更记录.md';t=log.read_text(encoding='utf8')
entry='''## 2026-10-28 情境方向10题生活化换图

- 来源：用户反馈街景、建筑和位置题图过于简陋，要求启动搜图，使用生活化图片，使真题风格的情境清楚易辨。
- 落实：搜集并保留房屋、自然树、汽车、路灯、影院、商店、图书馆、摄影者和钟楼SVG素材，统一黑白生活场景线描，重做原10题主图和解释图，同名更新Word。详见[本轮成品索引](./套卷索引/北京风格情境方向图形推理-10题（含答案解析）.md)。
- 修订：解决跨帧屋顶身份、生成漏路牌、展馆遮挡边、图标标签遮盖等问题；第4题取消等角条件，第7题补明点光源的地面投影并标注黑点，均重新读图确认。首次试解与修订历史完整保留。
- 规范：[情境方向规则](./情境方向图形题命题与检查规则.md)新增搜图溯源、生活场景表现、锚点、生成润饰的几何边界、换图后重新试解及印刷尺寸检查要求。
- 验证：20张嵌图与图源匹配，Word仍为10页，全部10页实际逐页打开；其他12份Word未改。只清理本轮临时页面与预览PNG，保留正式素材、备份、提示词和检查记录。

'''
if entry.split('\n')[0] not in t:t=t.replace('# 建议与变更记录\n','# 建议与变更记录\n\n'+entry,1)
log.write_text(t,encoding='utf8')

project=KB/'项目说明.md';t=project.read_text(encoding='utf8')
para='2026-10-28已对情境方向10题同名更新生活化换图版，搜集房屋、树木、路灯、影院和人物等素材并统一线描，20张主图及解释图更新，补清等角与光源投影条件；最终10页实际复核及换图后独立试解完成。最新内容见[成品索引](./套卷索引/北京风格情境方向图形推理-10题（含答案解析）.md)，新增要求纳入[情境方向规则](./情境方向图形题命题与检查规则.md)。\n'
if para not in t:t=t.replace('## 新增北京图形专项','## 新增北京图形专项\n\n'+para,1)
project.write_text(t,encoding='utf8')

contract=KB/'制作合同'/'北京方向10题生活化换图'/'artifact.md';contract.parent.mkdir(parents=True,exist_ok=True)
contract.write_text(f'''# 北京方向10题生活化换图执行记录

原Word保留在 `{ROOT/'source.docx'}`，SHA256 `{sha(ROOT/'source.docx')}`。本次为局部图片修改，原稿10页，最终仍为10页。沿用全部原节属性、A4页面、页边距、字体、段落样式、真实连续编号、题干与图同页及集中答案结构。

可编辑槽为 `word/document.xml` 中20个顺序内嵌绘图的尺寸、其20个既有PNG包内部分，以及第4、7题的两段题干。按图片自身比例更新纵向extent，宽度保持原值；图标或标签不得为保页数而压扁。其余16个包内部分逐字节保留，见 `word_bindings.json`。

本次不增加装饰标题或文本框，不重建原文档。先写工作目录 `revised.docx`，原生Word只读导出后逐页检查，再同名替换正式文档。其他12份Word及原稿备份指纹须不变。临时PNG仅在复核后按明确清单清理，正式20张图源、搜索SVG和提示词保留。
''',encoding='utf8')
print('Source manifest, final assets and four KB records archived')
