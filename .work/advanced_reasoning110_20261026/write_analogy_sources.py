import json, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
leads=json.loads((ROOT/'analogy_source_leads.json').read_text(encoding='utf-8'))
older=json.loads((ROOT/'older_analogy_leads.json').read_text(encoding='utf-8'))
records=[]
def add(id,year,path,n,digest,lesson,**extra):
    records.append(dict(id=id,year=year,path=path,question=n,digest=digest,
        application=lesson,read_method='实际读取题干、四项与本地解析；不把解析结论等同官方定论',**extra))
latest=[
 (96,'经年/积岁','近义关系，还需排除种属、交叉、组成'),
 (97,'口腔/唾液/淀粉酶','三词的分泌与成分关系须同时满足'),
 (98,'护士人数/护患比/患者人数','公式位置、口径、分母单位都需一致'),
 (99,'颅内疾病与岩石断裂填空','两侧因果方向一致'),
 (100,'两集合交叉、第三集合位于交集的图示','按全套集合区域选项，而非只识别一对关系')]
for n,d,l in latest:add(f'AX26-{n}',2026,leads[0]['path'],n,d,l,figure_actually_viewed=n==100)
city=[(96,'殚精竭虑/费尽心机','近义之外检查感情色彩方向'),
 (97,'逐客令/挡箭牌','名物与其命名依据，而非只看功能相似'),
 (98,'直观性/即时性/网络直播','多属性与对象的同时对应'),
 (99,'群众来访/窗口接访/调查督办','连续环节与偏序，不混目的或工具'),
 (100,'稀树草原/国际公约填空','两侧种属关系和词序对齐')]
for n,d,l in city:add(f'AX25-{n}',2025,leads[3]['path'],n,d,l)
for n,d,l in [(96,'嘤其鸣矣/求其友声','方式到目的'),(99,'收集罪证/提取指纹/透明胶','目的、方法、工具分层'),(100,'行政文书/汇编语言填空','上下位概念方向')]:
    add(f'AX25E-{n}',2025,leads[4]['path'],n,d,l)
add('AX25D-104',2025,leads[2]['path'],104,'光伏电站/电池板/发电','整体组成与功能同时校验；同主题不能替代关系')
old={2022:[(91,'贸易摩擦/出口下滑','因果方向'),(92,'载歌/载舞','语法结构之外再判同时或先后'),(93,'微型无人机/旋翼无人机','分类维度不同形成交叉'),(94,'呼吸系统/生殖系统','并列关系仍区分反对与矛盾')],
 2023:[(91,'铜镜/化妆镜','交叉之外区分材料命名、用途命名'),(92,'小计/总计','数量汇总、平均或乘积不能混淆'),(93,'原棉/脱脂棉','原料加工与同层产品'),(94,'海棠红/南瓜橙','颜色名称及借用对象类别')],
 2024:[(91,'法庭/质证','场所与活动；不照搬解析中未经证明的必然性'),(92,'植物及其部分','天然组成与加工物不同'),(93,'古句分句对应','因果、并列及词序'),(94,'花香四溢/分子运动','现象与机理对应')]}
for source in older:
 y=source['year_in_file_name']
 for n,d,l in old[y]:add(f'AX{str(y)[2:]}-{n}',y,source['path'],n,d,l)
facts=[
 dict(id='FACT-TEARS',claim='泪腺分泌泪液；水是泪液成分',urls=['https://www.nei.nih.gov/eye-health-information/healthy-vision/how-eyes-work/how-tears-work','https://www.nei.nih.gov/sites/default/files/health-pdfs/factsaboutdryeye.pdf']),
 dict(id='FACT-SWEAT',claim='汗腺分泌汗液，汗液含盐分',urls=['https://my.clevelandclinic.org/health/body/sweat']),
 dict(id='FACT-WHALES',claim='鲸类属于哺乳动物，鲸类完全水生；哺乳动物不等于鲸类或陆生动物之并',urls=['https://www.fisheries.noaa.gov/whales','https://oceanservice.noaa.gov/facts/dolphin.html','https://cdn.oceanservice.noaa.gov/oceanserviceprod/about/environmental-compliance/final-peis/Section%203.5%20Marine%20Mammals.pdf']),
 dict(id='FACT-BORROW',claim='鸿雁借指书信、桑梓借指故乡',urls=['https://www.ccdi.gov.cn/lswh/wenhua/wyzd/201704/t20170405_156326.html','https://www.moe.gov.cn/jyb_xwfb/moe_2082/2025/2025_zl02/202509/t20250901_1411314.html']),
 dict(id='FACT-IDIOM',claim='一丝不苟释义；风平浪静字面构词',urls=['https://dict.revised.moe.edu.tw/dictView.jsp?ID=149832&la=0&powerMode=0','https://dict.idioms.moe.edu.tw/idiomView.jsp?ID=1447']),
 dict(id='FACT-SETS',claim='有限/无限在集合范围内构成互补划分',urls=['https://math.ecnu.edu.cn/~wsun/teaching/Analysis_short_course_2014/Analysis.pdf'])]
report=dict(scope='2022—2026国考为主；26个不同题例，不对跨卷重复题多计权',sources=records,
 source_count=len(records),fact_sources=facts,limitations=['本地回忆整理题本不是官方完整题库','2025副省101—105才是类比，96—100为定义；没有用编号机械分类','2025跨卷重复逐客令、古句、属性、流程、稀树草原等只计原题一次','题量配额是用户专项要求，不代表国考整卷比例或历年频率统计'])
known={x['id'] for x in records+facts}
qs=json.loads((ROOT/'questions_analogy.json').read_text(encoding='utf-8'))
assert all(set(q['source_refs'])<=known for q in qs)
for x in records:
 assert Path(x['path']).is_file()
 x['file_sha256']=hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()
(ROOT/'sources_analogy.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print({'source_count':len(records),'fact_records':len(facts)})
