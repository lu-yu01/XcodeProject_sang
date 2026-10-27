"""Thirty original definition-reasoning items, global numbers 21--50.

Definitions are supplied in the stems.  Model facts encode what the options
actually say; verify evaluates the definition predicates, not an answer table.
No Word or Markdown output is produced by this module.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import json

ROOT = Path(__file__).resolve().parent
QUESTIONS = []


def evaluate(expr, facts):
    if isinstance(expr, bool):
        return expr
    if isinstance(expr, str):
        return facts[expr]
    op, *args = expr
    if op == 'all': return all(evaluate(x, facts) for x in args)
    if op == 'any': return any(evaluate(x, facts) for x in args)
    if op == 'not': return not evaluate(args[0], facts)
    if op == 'eq': return value(args[0], facts) == value(args[1], facts)
    if op == 'ge': return value(args[0], facts) >= value(args[1], facts)
    if op == 'gt': return value(args[0], facts) > value(args[1], facts)
    raise ValueError(op)


def value(x, facts):
    if isinstance(x, dict) and 'fact' in x: return facts[x['fact']]
    if isinstance(x, list) and x and x[0] == 'div':
        return value(x[1], facts) / value(x[2], facts)
    return x


def add(n, stem, ask, options, requirements, records, reasons, refs,
        point, mechanism, difficulty='中高', expr=None, direction='positive',
        data=None):
    expr = expr or ['all', *requirements]
    matched = [bool(evaluate(expr, f)) for f in records]
    chosen = [i for i, v in enumerate(matched) if v == (direction == 'positive')]
    if len(chosen) != 1:
        raise ValueError((n, matched, direction))
    idx = chosen[0]
    QUESTIONS.append({
        'n': n, 'category': '定义判断', 'stem': stem, 'ask': ask,
        'options': options, 'answer': 'ABCD'[idx], 'point': point,
        'analysis': [f'判别要点：{point}。'] + [f'{"ABCD"[i]}项：{s}' for i, s in enumerate(reasons)]
                    + [f'本题为{"选非" if direction == "negative" else "选是"}题，故选{"ABCD"[idx]}。'],
        'difficulty': difficulty, 'mechanism': mechanism, 'source_refs': refs,
        'model': {'requirements': requirements, 'expression': expr,
                  'direction': direction, 'option_facts': records,
                  'option_evidence': reasons, 'data': data or {},
                  'definition_status': '题内给定；真实术语已列出处，进一步限定以本题明示边界为准'}
    })


add(21,
    '数据溯源是对数据的来源及其变化过程作有序记录，以便解释特定结果如何产生。本题所称完整的数据溯源，须能由指定结果定位其原始数据，沿转换先后次序还原加工链，并识别各次加工使用的规则或参数；只保存结果的历次版本不视为完整的数据溯源。',
    '根据上述定义，下列没有实现完整数据溯源的是：',
    ['监测站为每份水质月报保存原始读数编号、剔除异常值的阈值和合并日期，点击月报可依次查到对应记录',
     '档案馆给修复图像关联底片编号，记录去噪、补色的先后次序及各自参数，能够按记录解释图像中各处变化',
     '物流平台按天备份运量报表并标出修改人，能恢复每一版报表，但未保留各版本所用订单和计算规则',
     '气象团队将预测图关联观测批次，记录插补、校正、模型计算的依赖关系，并保存各环节的配置文件'],
    {'origin':'可由结果定位原始数据','ordered_chain':'可还原有序加工链','rules':'可识别加工规则或参数'},
    [dict(origin=True,ordered_chain=True,rules=True),dict(origin=True,ordered_chain=True,rules=True),
     dict(origin=False,ordered_chain=False,rules=False),dict(origin=True,ordered_chain=True,rules=True)],
    ['原始读数编号、阈值及合并日期共同提供来源、次序和规则，三项条件均成立。',
     '底片是原始来源，去噪补色有先后和参数，三项条件均成立；人工加工也能形成溯源链。',
     '修改人和历史版本只能说明谁改过及结果差异，不能从报表定位所用订单，也不能还原所用规则，不符合定义。',
     '观测批次提供来源，依赖关系提供加工次序，配置文件提供规则参数，三项条件均成立。'],
    ['D04','D14','T01'],'必须追溯结果的来源、加工链和规则，版本备份本身不足','过程追踪与结果留存边界',direction='negative')

add(22,
    '最小权限原则要求每个账号只获得完成其被分配任务所必需的权限。职责分离原则要求一项关键业务中相互制约的操作由不同主体实施，任何单一主体不能独自完成整项业务。本题将采购单的提出与批准视为必须相互制约的两项操作，不考虑账号被冒用。',
    '根据上述定义，下列安排同时符合最小权限原则和职责分离原则的是：',
    ['提出采购单的职员不能批准本人提交的单据，但每人均可查看并修改全公司的工资资料，便于临时协调',
     '采购员只可提出和修改本人未批准的单据，审核员只可批准他人提交的单据，两类账号都无工资资料权限',
     '采购员可提出并批准本人限额内的单据，超过限额才交审核员；两类账号均只开放办理采购所需功能',
     '采购员和审核员使用同一工作账号，密码由二人分别保管半段；登录后可完成提出、批准和财务系统设置'],
    {'minimum':'每个账号无超任务权限','different':'提出与批准由不同主体实施','no_single':'单个主体不能独立完成采购'},
    [dict(minimum=False,different=True,no_single=True),dict(minimum=True,different=True,no_single=True),
     dict(minimum=True,different=False,no_single=False),dict(minimum=False,different=False,no_single=False)],
    ['提出和批准相分离，但修改全公司工资与既定采购任务无关，不符合最小权限。',
     '采购员和审核员各限于所需操作，不能批准本人提出的采购，且无无关权限，两项原则均符合。',
     '权限虽然限于采购任务，但限额内可由同一人提出并批准，违反本题给定的职责分离要求。',
     '共用账号拥有提出、批准全权限，账号角色没有分离；同时开放系统设置超出给定采购任务。密码如何保管不能补足这些条件。'],
    ['D09','D17','T02','T03'],'分别核验权限范围和关键操作的主体分离','两个定义交叉合取')

add(23,
    '故障容错是指系统在一个或多个部件发生故障后，仍能维持所要求的正确服务。故障安全是指系统检测到故障后自动进入预先确定的安全状态，以限制危险后果；进入安全状态可以中断原有服务。本题只按所描述故障发生后的即时行为判定，不把事后维修算作维持服务。',
    '根据上述定义，下列体现了故障安全，但没有体现故障容错的是：',
    ['收费设备主电源断开后自动切换备用电源，交易不丢失，车辆仍按正常流程通过，维修员次日更换电源',
     '传送带控制器失灵后，安全回路立即切断驱动并制动，人员不再受卷入危险影响，但运送服务随即停止',
     '显示屏偶尔出现乱码，值班员收到旅客投诉后重启设备；重启期间，旅客改看旁边的纸质时刻表',
     '检测系统主传感器损坏后，由另一个传感器继续给出满足精度要求的读数，并将损坏信息发送给维护人员'],
    {'detected':'检测故障','automatic_safe':'自动进入预定安全状态','service':'原要求服务继续正确运行'},
    [dict(detected=True,automatic_safe=False,service=True),dict(detected=True,automatic_safe=True,service=False),
     dict(detected=False,automatic_safe=False,service=False),dict(detected=True,automatic_safe=False,service=True)],
    ['切换后原服务继续，体现容错；没有描述因危险而进入预定安全状态，不满足设问的组合。',
     '检测失灵后自动制动进入安全状态，符合故障安全；原运送服务中断，不属于本题所称故障容错。',
     '由人获知投诉并重启，不是系统检测故障后自动进入安全状态，且服务中断。',
     '备份传感器维持正确读数，体现容错，不能仅因发出通知就认定自动进入了预定安全状态。'],
    ['D20','D25','T04'],'区分故障后继续服务与允许停服的安全状态','结果相近而机制不同',expr=['all','detected','automatic_safe',['not','service']])

add(24,
    '去标识化，是指个人信息经过处理，使其在不借助额外信息的情况下无法识别特定自然人的过程。匿名化，是指个人信息经过处理，无法识别特定自然人且不能复原的过程。本题判断均以选项所述技术能力和保留信息为准，不推测未交代的外部信息。',
    '根据上述定义，下列处理属于去标识化，但不属于匿名化的是：',
    ['研究中心把姓名替换为随机编号，交付表不能单独识别人；另存可获授权使用的编号与姓名对应表',
     '展馆把调查记录按足够大的群组汇总，删除全部个体记录，经题设确认无法从汇总结果识别或复原任何个人',
     '社团只向负责人开放会员名册，其余人员没有访问权限；名册中的姓名、手机号和住址仍保持原样',
     '学校将成绩表中的手机号删除，但仍保留每行的姓名及完整身份证号，阅读该表即可直接识别对应学生'],
    {'no_identification_alone':'不借额外信息不能识别','restorable':'借保留信息可以复原'},
    [dict(no_identification_alone=True,restorable=True),dict(no_identification_alone=True,restorable=False),
     dict(no_identification_alone=False,restorable=True),dict(no_identification_alone=False,restorable=True)],
    ['研究表单独不能识别，但额外对应表允许复原，符合去标识化且不符合不能复原的匿名化。',
     '题设明确不可识别且不能复原，属于匿名化，不符合“但不属于匿名化”的限制。',
     '只是限制访问者，信息内容仍直接识别个人，没有实施所定义的信息处理。',
     '姓名及完整身份证号仍直接指向本人，删除手机号未使信息达到不能直接识别的状态。'],
    ['D23','D09','T05'],'能否单独识别与能否复原是两个不同条件','双定义包含与差异条件',difficulty='中')

add(25,
    '本题讨论两种控制方式：负反馈控制根据已测得的输出与目标值之差进行调整，使偏差减小；扰动型前馈控制根据已检测到、尚未作用于输出的外部扰动，利用预先建立的关系作补偿，不以已经出现的输出偏差为启动依据。同一系统可以兼用两者。',
    '根据上述定义，下列两项控制动作的归类均正确的是：',
    ['空调根据室温高于设定值而加大制冷——前馈；根据门外热风即将进入的测量结果提前加大制冷——负反馈',
     '水泵每天八点按固定日程启动——前馈；水泵因出口压力低于目标而提高转速——负反馈',
     '烘干机因成品含水率高于目标而延长烘干——负反馈；根据尚未进入的原料湿度提前调节热量——前馈',
     '温控器因水温低于目标而加热——负反馈；管理员测得室内照度已超目标后手动关闭部分照明——前馈'],
    {'first_label':'第一项动作归类正确','second_label':'第二项动作归类正确'},
    [dict(first_label=False,second_label=False),dict(first_label=False,second_label=True),
     dict(first_label=True,second_label=True),dict(first_label=True,second_label=False)],
    ['室温已有偏差是负反馈；外部热风尚未进入而提前补偿是前馈，两个标签均颠倒。',
     '固定日程不是检测外部扰动后按模型补偿，第一项不是定义中的前馈；第二项是负反馈。',
     '成品含水率偏差引发调整，属于负反馈；尚未进入的原料湿度作为扰动引发预补偿，属于前馈，两项均正确。',
     '第一项符合负反馈；第二项同样依据已出现的室内照度偏差进行调整，仍是负反馈，不能归为前馈。'],
    ['D06','D20','T06'],'控制依据是已出现的输出偏差还是尚未作用的扰动','多定义双情境逐项对应')

add(26,
    '词典序决策是将评价指标按重要性排定顺序，先仅保留第一指标最优的方案；若仍不止一个，则只在这些方案中按第二指标保留最优者，如此继续，直到选出一个方案或所有指标用尽。本题的指标依次为安全分、寿命、成本，前两项越大越优，成本越小越优。四个方案的数据为：甲（95分、8年、12万元），乙（95分、10年、15万元），丙（94分、12年、9万元），丁（95分、10年、14万元）。',
    '根据上述定义，下列决策过程正确的是：',
    ['先保留甲、乙、丁，再保留乙、丁，最后选择丁；不让丙凭较长寿命重新进入比较',
     '先删除成本最高的乙，再在余下方案中按安全分比较，因甲与丁并列而选成本更低的甲',
     '先保留甲、乙、丁，再将四个方案的寿命一同比较，因丙寿命最长而最终选择丙',
     '给安全、寿命、成本分别赋予五、三、二的权重，将各项折算为分值后选择综合得分最高者'],
    {'priority':'严格按安全、寿命、成本次序','nested':'后轮仅在前轮入选集合内','extreme':'每轮仅保留该指标最优者'},
    [dict(priority=True,nested=True,extreme=True),dict(priority=False,nested=True,extreme=False),
     dict(priority=True,nested=False,extreme=True),dict(priority=False,nested=False,extreme=False)],
    ['安全最优集合是甲乙丁，寿命最优集合缩为乙丁，成本较低的是丁；每轮只处理上一轮的入选者。',
     '先按成本淘汰违反重要性次序，且安全并列后应先比较寿命，不能跳到成本。',
     '丙已因安全分被淘汰，不能在寿命比较时重回候选集合。',
     '加权得分允许低优先级指标补偿高优先级劣势，不是词典序逐级保留法。'],
    ['D10','D13'],'重要性顺序、嵌套候选范围与逐项最优须同时满足','定义推演程序与数据复算',data={'kind':'lexicographic','rows':{'甲':[95,8,12],'乙':[95,10,15],'丙':[94,12,9],'丁':[95,10,14]},'maximize':[True,True,False],'stages':[['甲','乙','丁'],['乙','丁'],['丁']]})

add(27,
    '分层抽样是先按某种特征将总体划分为不同层，再从每一层中独立、随机抽取个体组成样本。整群抽样是先把总体划为若干群，随机抽取部分群，再调查入选群的全部个体。本题不将先抽群再抽群内个体的多阶段抽样直接等同于上述整群抽样。',
    '根据上述定义，下列两种调查与所标抽样方式均相符的是：',
    ['从每种班型中各随机抽三名学生——整群抽样；随机抽五个班并调查全班学生——分层抽样',
     '按工作年限分组后各找十名自愿者——分层抽样；随机抽三个车间再各随机抽十人——整群抽样',
     '随机抽四栋楼并调查楼内所有住户——整群抽样；按年龄分层后只调查人数最多的一层——分层抽样',
     '按经营规模分层，每层独立随机抽企业——分层抽样；随机抽六村并调查入选村全部农户——整群抽样'],
    {'first_label':'第一项满足所标方法','second_label':'第二项满足所标方法'},
    [dict(first_label=False,second_label=False),dict(first_label=False,second_label=False),
     dict(first_label=True,second_label=False),dict(first_label=True,second_label=True)],
    ['每类中抽个体是分层，抽班后全查是整群，两个标签对调。',
     '自愿报名不是层内随机抽取；车间内又抽部分人也不是本题所定义的入选群全查。',
     '楼内住户全查符合整群；只调查一个年龄层未从每层抽样，不符合分层。',
     '每一规模层都随机抽企业，符合分层；随机选村后对入选村农户全查，符合整群，两项均正确。'],
    ['D06','D28','T07','T08'],'检查抽取单位、每层是否均抽样及入选群是否全查','相近统计方法与双项匹配')

add(28,
    '随机分配是指由随机机制决定受试者进入哪一实验组，而非由受试者或研究者选择。双盲是指受试者和直接实施干预、评定结果的研究人员在实验期间均不知道受试者所处的具体组别；可由不参与这些工作的独立人员保管编码。本题仅据此判断“双盲随机实验”。',
    '根据上述定义，下列不属于双盲随机实验的是：',
    ['记忆训练采用外观相同的两套材料，由独立人员用随机数分组，学员、授课员和评分员在结题前均不知编码含义',
     '学员按方便时段选择甲班或乙班，训练材料只标编码，学员、授课员和评分员均不知班别对应方法',
     '两种注意力训练由程序抽签分配，执行员和受试者只见材料代码，独立编码员封存分组表，评分员也不知组别',
     '同一批志愿者经电脑随机分为两组，训练内容通过同样界面呈现，志愿者及实施、评分人员均不知代码对应方法'],
    {'random':'分组由随机机制决定','participant_blind':'受试者不知道具体方法组别','researcher_blind':'直接实施与评分人员均不知组别'},
    [dict(random=True,participant_blind=True,researcher_blind=True),dict(random=False,participant_blind=True,researcher_blind=True),
     dict(random=True,participant_blind=True,researcher_blind=True),dict(random=True,participant_blind=True,researcher_blind=True)],
    ['随机数决定组别，受试者及实施、评分者均不知编码含义；独立人员保管编码不破坏题设双盲。',
     '虽采取盲法，但由学员选择时段并由此决定班别，不是随机机制分组，不满足合取定义。',
     '程序抽签满足随机分配，独立编码员不参与实施和评分，其知情不破坏题设双盲。',
     '随机分组与受试者、实施评分者不知组别均已满足，界面一致只是辅助条件，不是唯一判据。'],
    ['D23','D28','T09'],'随机分配与双盲为两个独立必要条件','科研设计双条件与选非',direction='negative')

add(29,
    '操作性定义是用明确的观察、测量或操作程序界定某个概念，使其他研究者能够按同样程序得到可比较的指标。本题要求操作性定义同时交代实施条件、可记录的反应及计分或判定规则；说明概念的重要性或给出相关关系，不等于操作性定义。',
    '根据上述定义，下列对“持续注意”的处理属于操作性定义的是：',
    ['持续注意使人把精力长期集中于特定任务，它是完成复杂工作的基础，也可能受睡眠与环境影响',
     '邀请三名专家讨论持续注意的内涵，认为它既包括保持清醒，也包括抑制无关信息对任务的干扰',
     '安静房间内呈现二十分钟符号序列，遇目标符号按键，以后十分钟漏按次数占目标次数的比例计分',
     '对一百名职员测得的注意量表分数与工作差错率作比较，发现两者相关，因而认为量表具有研究价值'],
    {'conditions':'实施条件明确','response':'可记录反应明确','rule':'指标规则明确'},
    [dict(conditions=False,response=False,rule=False),dict(conditions=False,response=False,rule=False),
     dict(conditions=True,response=True,rule=True),dict(conditions=False,response=False,rule=False)],
    ['解释功能和可能影响因素，没有规定如何实施、观察和计分。',
     '是在讨论概念内涵，未给出可复现的具体测量程序。',
     '安静房间和呈现时长是条件，目标按键及漏按是反应，后十分钟漏按比例是计算规则，三项均明确。',
     '报告量表分数与差错的相关性，未给出量表如何施测和计分，不能据结果相关代替操作性定义。'],
    ['D26','D28','T10'],'概念须落实为条件、观察反应和可复现的计分规则','元层级定义与相关证据边界')

add(30,
    '再利用是将废物直接作为产品，或经修复、翻新、再制造后继续作为产品使用，或将其全部、部分作为其他产品的部件使用。资源化是将废物直接作为原料进行利用，或对废物进行再生利用。本题按选项明示的利用对象和方式判断，不将“减少丢弃”本身作为资源化的充分条件。',
    '根据上述定义，下列没有体现资源化的是：',
    ['回收站将废纸打浆，去除杂质后制成再生纸，作为包装纸的生产原料投入后续加工',
     '建材厂把废弃玻璃粉碎熔融，制成玻璃原料，供另一条生产线制作新的玻璃制品',
     '家具作坊拆下废弃旧柜的完好门板，按原尺寸装到新柜上继续启闭使用',
     '纺织厂把废旧聚酯织物处理成可再纺的聚酯原料，再用这些原料生产纤维'],
    {'waste':'对象为废物','raw_or_regenerate':'作为原料或经再生利用'},
    [dict(waste=True,raw_or_regenerate=True),dict(waste=True,raw_or_regenerate=True),
     dict(waste=True,raw_or_regenerate=False),dict(waste=True,raw_or_regenerate=True)],
    ['废纸再生为纸浆及再生纸原料，符合废物的再生利用。',
     '废玻璃转为生产原料，符合资源化，不能因最终仍制玻璃而否定。',
     '门板保持部件身份直接用于新柜，是再利用；所述过程没有转为原料，未体现资源化。',
     '废织物被处理为可再纺原料，符合资源化，不是完整旧织物继续作产品使用。'],
    ['D01','D20','T11'],'产品或部件继续使用与转作原料、再生利用有别','相同环保结果的机制边界',direction='negative')

add(31,
    '中介变量解释某因素如何影响结果，即该因素先改变中介变量，再由中介变量影响结果。调节变量描述某因素与结果之间关系的强弱或方向如何随该变量取值而改变，回答何种条件下作用不同。某训练先改善学员的检索策略，再由检索策略提高成绩；训练对成绩的提升在睡眠充足者中较强，在睡眠不足者中较弱，且训练不改变睡眠状况。以上作用关系均为题设已确认的关系，不推测未交代的作用。',
    '根据上述定义，对该情境的判断正确的是：',
    ['检索策略是调节变量，睡眠状况是中介变量，因为两者均与训练后的成绩有关',
     '检索策略与睡眠状况都是中介变量，因为两者都能解释学员之间的成绩差异',
     '检索策略与睡眠状况都是调节变量，因为训练效果会随学员情况而有所不同',
     '检索策略是中介变量，睡眠状况是调节变量，二者承担不同的作用'],
    {'chain_label':'检索策略被归为中介','strength_label':'睡眠状况被归为调节'},
    [dict(chain_label=False,strength_label=False),dict(chain_label=True,strength_label=False),
     dict(chain_label=False,strength_label=True),dict(chain_label=True,strength_label=True)],
    ['两种角色颠倒；与结果有关不是区分中介和调节的充分条件。',
     '检索策略位于训练到成绩的作用链，确属中介；睡眠未被训练改变且改变训练效果强弱，不能归为该作用链的中介。',
     '睡眠的归类正确，但检索策略承接训练对成绩的作用，不是题设所述关系强弱的分组条件。',
     '训练→检索策略→成绩构成中介路径，睡眠状况改变训练效果的强弱，分别符合两个定义。'],
    ['D06','D16','D20','T12'],'先辨作用链的中间环节，再辨改变关系强弱的条件','因果角色区分与双定义对应')

add(32,
    '本题所称诊断性评价，是在一项学习活动开始前识别学习者已有知识和具体困难，并据此安排该项活动的内容或支持；预测性评价，是依据当前测得的信息预测学习者在后续目标任务中的表现。两者可以使用相同工具，但应按评价的实际目的和用途区分。',
    '根据上述定义，下列只体现诊断性评价、没有体现预测性评价的是：',
    ['竞赛训练前，教练依据体能测试估计队员半年后进入决赛的可能性，并据此确定参赛名单',
     '统计课开课前，教师用小测定位学生不懂的概率概念，据此安排补习单元及课堂内容',
     '阅读课进行到一半，教师通过随堂问答发现学生刚学段落的误解，随即用另一例子再次讲解',
     '编程课开课前，教师查明学生的知识缺口以分组辅导，同时据测评分数预测其完成期末项目的水平'],
    {'before':'在该学习活动开始前','diagnose':'识别已有知识/困难','plan':'据此安排内容支持','predict':'预测后续目标表现'},
    [dict(before=True,diagnose=False,plan=False,predict=True),dict(before=True,diagnose=True,plan=True,predict=False),
     dict(before=False,diagnose=True,plan=True,predict=False),dict(before=True,diagnose=True,plan=True,predict=True)],
    ['直接预测半年后决赛表现，体现预测性评价，未体现根据知识困难安排学习内容。',
     '开课前识别具体概念困难并据此安排补习，满足诊断的时间、对象和用途；所述用途没有预测后续表现。',
     '反馈发生在该阅读活动进行中，不符合本题限定的开始前，不能按本题定义归为诊断性评价。',
     '既识别困难用于辅导，又预测期末项目表现，同时体现两种评价，不符合“只体现”的限制。'],
    ['D08','D23','D28'],'评价工具相同不决定类别，须看发生阶段与实际用途','双定义交叉及只属于限制',expr=['all','before','diagnose','plan',['not','predict']])

add(33,
    '重测信度关注同一工具对同一批对象间隔一段时间重复测量时结果的一致程度。效标关联效度关注工具结果与一个独立、适当的外部效标之间的联系，用以考察工具是否测到了拟测特征。本题均假定重复测量期间拟测特征没有实质变化，所述外部效标适当。',
    '根据上述定义，下列是在考察重测信度，而不是效标关联效度的是：',
    ['将职业兴趣量表得分与受测者后来实际选择的职业类型相比较，考察量表能否反映职业取向',
     '让两名评分员使用同一评分表，在同一天独立评定同一批人的演讲，比较二人的分数是否一致',
     '让同一批成年人间隔两周填写同一份空间能力量表，比较两次得分的稳定程度，不另取外部指标',
     '让受测者填写专注量表，并用一项独立实验任务的正确率作参照，比较量表分数与该参照的关系'],
    {'same_tool':'同一工具','same_people':'同一批对象','separated':'不同时间重复测量','consistency':'比较重复结果一致性','external':'比较独立外部效标'},
    [dict(same_tool=True,same_people=True,separated=False,consistency=False,external=True),
     dict(same_tool=True,same_people=True,separated=False,consistency=True,external=False),
     dict(same_tool=True,same_people=True,separated=True,consistency=True,external=False),
     dict(same_tool=True,same_people=True,separated=False,consistency=False,external=True)],
    ['职业选择是独立的外部效标，比较的是量表与效标的关系，不是同一工具的两次测量。',
     '两名评分员的同日评分考察评分者之间的一致性，缺少间隔一段时间的重测条件。',
     '同一批对象、同一工具、两周间隔和重复得分一致性均满足，没有外部效标比较，符合设问。',
     '独立任务正确率作为外部参照，属于效标关联效度的考察，不是量表的重复测量。'],
    ['D28','D19','T13'],'同一工具跨时间的一致性不能与对外部效标的联系互换','测量证据对象与时序边界',expr=['all','same_tool','same_people','separated','consistency',['not','external']])

add(34,
    '本题所称主动信息推送，是指系统依据预先设定的规则，向用户发送其当时未主动请求的具体信息；用户事先授权某类提醒，不等于当时请求某条具体信息。按需获取则由用户针对所需具体内容发起请求，系统作出响应。是否收费、是否使用个性化算法，不是两者的区分标准。',
    '根据上述定义，下列不属于主动信息推送的是：',
    ['读者事先订阅到期提醒，图书馆系统在借书到期前三天自动发来该书的归还日期和续借入口',
     '旅客允许航班提醒，航空系统发现其航班登机口变更后，未等旅客查询即发送新登机口信息',
     '居民在地图中输入“附近可借用的轮椅”，系统据此返回当前位置周边的具体借用点和开放时段',
     '用户允许安全告警，设备发现异常登录后按既定规则发送登录地点与核验提示，无须用户先提出查询'],
    {'rule':'按预设规则发送','not_specific_request':'当时未主动请求该具体内容'},
    [dict(rule=True,not_specific_request=True),dict(rule=True,not_specific_request=True),
     dict(rule=True,not_specific_request=False),dict(rule=True,not_specific_request=True)],
    ['事先订阅一类提醒不等于当时请求某条信息，到期规则触发具体通知，属于主动推送。',
     '系统依据变更事件主动通知，用户没有当时查询该信息，符合主动推送。',
     '居民针对轮椅借用点发起具体检索，结果是对该请求的响应，属于按需获取。',
     '安全告警由异常登录触发，用户的预先授权不改变当时未具体请求这一事实，符合主动推送。'],
    ['D08','D14'],'预先授权类别不等于当时主动请求具体信息','总定义优先与时间对象边界',direction='negative')

add(35,
    '本题所称公共服务共同生产，是指专业服务提供者与该项服务的使用者持续协作，使用者以时间、技能或劳动等资源直接参与服务的实施或交付。仅评价服务、表达需求，或由非使用者承接服务外包，都不属于本题所称共同生产。',
    '根据上述定义，下列属于公共服务共同生产的是：',
    ['社区助餐站和就餐老人共排值班表，老人轮流分餐、维护秩序，专业人员负责营养和食品安全',
     '社区助餐站每月向老人发问卷，收集菜品意见并据此调整菜单；分餐及其他服务一直由站内人员完成',
     '街道将助餐站运营交给一家餐饮企业，企业派出厨师与配送员，为社区老人提供连续的助餐服务',
     '几位居民自发轮流为彼此做饭，费用自行分摊；他们没有与任何专业服务提供者建立合作关系'],
    {'professional':'有专业提供者','users':'协作者是该服务使用者','sustained':'持续协作','delivery':'使用者直接投入资源参与实施交付'},
    [dict(professional=True,users=True,sustained=True,delivery=True),dict(professional=True,users=True,sustained=True,delivery=False),
     dict(professional=True,users=False,sustained=True,delivery=False),dict(professional=False,users=True,sustained=True,delivery=True)],
    ['老人既是服务使用者，又持续投入分餐等劳动，与专业人员共同交付服务，全部条件成立。',
     '参与的是需求表达和评价，没有直接参与服务实施，缺少交付要件。',
     '餐饮企业承接外包，其员工不是作为该项服务使用者参与，缺少专业提供者与使用者共同实施的关系。',
     '虽有持续劳动与互助，但没有专业服务提供者参与，不符合题设的合作主体结构。'],
    ['D04','D15','D24'],'必须是专业提供者与使用者持续合作，且使用者直接参与交付','主体、阶段与投入资源的合取')

add(36,
    '通用设计是尽可能使产品、环境或服务在无须另作适应性改造、专门设计的情况下即可供所有人使用的设计。合理便利是在特定个案中，为保障某人平等使用而作必要、适当且不造成不成比例负担的调整。通用设计并不排斥个别人仍需辅助措施；提供调整的时间早晚，也不是唯一判据。',
    '根据上述定义，下列两项措施的归类均正确的是：',
    ['因一名听障员工的需要为其会议配手语译员——通用设计；新系统一开始就让所有人可选文字或语音操作——合理便利',
     '新馆入口统一采用便于多类人群通行的无台阶方案——通用设计；为一名低视力学员单独提供适配材料且负担适当——合理便利',
     '按常见用户的习惯设计小字号界面，遇投诉再另作处理——通用设计；给一名行动不便者调整工位且负担适当——合理便利',
     '服务系统初始即支持键盘和触屏等多种输入方式供不同用户选择——通用设计；为一名用户改造设施，虽已确认造成不成比例负担仍实施——合理便利'],
    {'first_label':'第一项归类满足定义','second_label':'第二项归类满足定义'},
    [dict(first_label=False,second_label=False),dict(first_label=True,second_label=True),
     dict(first_label=False,second_label=True),dict(first_label=True,second_label=False)],
    ['为具体员工配译员是个案调整；初始为不同用户提供输入方式体现通用设计，标签颠倒。',
     '统一无台阶设计面向尽可能广泛使用者；针对一名学员的适配材料是必要且负担适当的个案调整，两项正确。',
     '只按常见用户设计并待投诉处理，未体现尽可能无需另行改造即可供所有人使用；第二项符合合理便利。',
     '第一项是通用设计；第二项已确认造成不成比例负担，缺少合理便利的负担边界条件，不能据个别请求就归类。'],
    ['D06','D23','T14'],'面向广泛使用者的初始可用性与有负担边界的个案调整不同','多定义对应与例外边界')

add(37,
    '本题区分两类产品创新：模块创新改变一个或若干基本模块，而模块之间的主要连接方式和整体布局不变；架构创新保留基本模块自身的工作原理与功能，通过重新安排模块之间的连接或布局产生新功能。不涉及新功能的外观调整不计入这两类创新。',
    '根据上述定义，下列属于架构创新的是：',
    ['检测仪更换灵敏度更高的传感模块，模块的安装位置、连接接口和整机布局不变，使原有检测更精确',
     '照明设备把原有光源模块换成另一种发光原理的模块，外壳和主要连接方式保持不变，从而降低能耗',
     '工具箱保留全部工具及托架的原有功能，仅给外表涂上不同颜色，并保持内部连接和布局不变',
     '巡检装置保留摄像、驱动、控制模块的工作原理与功能，将串联改为环形协同连接，从而实现接力巡检新功能'],
    {'modules_same':'基本模块原理与功能保留','architecture_change':'主要连接或布局改变','new_function':'产生新功能'},
    [dict(modules_same=False,architecture_change=False,new_function=True),dict(modules_same=False,architecture_change=False,new_function=True),
     dict(modules_same=True,architecture_change=False,new_function=False),dict(modules_same=True,architecture_change=True,new_function=True)],
    ['改变传感模块而维持架构，属于本题所称模块创新，不是架构创新。',
     '改变发光模块的工作原理，主要连接不变，缺少保留模块而重组架构的条件。',
     '涂色既未改连接布局，也未产生新功能，题设明确不计入两类创新。',
     '基本模块保留，模块间连接由串联改为环形协同，并产生接力巡检新功能，满足全部条件。'],
    ['D22','D25'],'保留模块本身，通过连接布局改变获得新功能','工程创新层级辨析')

add(38,
    '本题所称众包，是组织将原本可由内部人员或特定承包者承担的任务，以公开征集的方式交给事先不特定的参与者自愿贡献方案、劳动或知识，并将这些贡献用于完成任务。参与可以有报酬，也可以无报酬；仅把消息传给很多人不算贡献任务。',
    '根据上述定义，下列不属于众包的是：',
    ['博物馆公开征集老照片拍摄地点线索，任何知情者均可提交，馆员核验后将有效线索用于完善照片档案',
     '设计机构公开发布座椅改造任务，任何人均可投稿，评审后采用若干方案，并向被采用者支付报酬',
     '研究站面向社会公开招募志愿者按统一规则标注图片，参与者自行认领任务，合格标注汇入研究数据库',
     '研究站邀请三位已确定的顾问签订合同，规定每人完成部分图片标注，按验收结果支付报酬'],
    {'task':'存在可交付任务','open_unspecified':'公开面向事先不特定参与者','voluntary':'自愿贡献','used':'贡献用于任务'},
    [dict(task=True,open_unspecified=True,voluntary=True,used=True),dict(task=True,open_unspecified=True,voluntary=True,used=True),
     dict(task=True,open_unspecified=True,voluntary=True,used=True),dict(task=True,open_unspecified=False,voluntary=True,used=True)],
    ['不特定知情者公开提交线索，核验后用于档案任务，符合众包；成果仍经专业核验不影响归类。',
     '公开自愿投稿并采用成果，符合众包；支付报酬不是排除条件。',
     '公开招募、不特定参与者自愿认领，且贡献进入数据库，符合定义。',
     '任务交给事先确定的三位合同顾问，不是面向不特定参与者公开征集；有无报酬不是决定因素。'],
    ['D02','D15','D23'],'公开征集不特定参与者并实际使用贡献，不以报酬为标准','主体范围与非必要属性干扰',direction='negative')

add(39,
    '基础研究主要为获得现象基本原理的新知识，而不指向某一特定实际用途；应用研究为获取新知识而开展，但具有特定的实际目标；试验发展利用研究和实践知识开展系统工作，产生额外知识，以形成新产品、新工艺或实质改进。三者均不包括按成熟规程进行的例行检测。现有三个项目：甲不设具体应用目标，探究一种晶体在极端条件下的结构规律；乙针对海水检测的明确需求，研究尚未知晓的选择性识别机制；丙依据已知识别机制试制检测器，通过系统试验解决小型化中的未知问题并形成新设计。',
    '根据上述定义，甲、乙、丙的项目类别依次是：',
    ['基础研究、试验发展、应用研究',
     '应用研究、基础研究、试验发展',
     '基础研究、应用研究、试验发展',
     '应用研究、试验发展、例行检测'],
    {'jia':'甲归为基础研究','yi':'乙归为应用研究','bing':'丙归为试验发展'},
    [dict(jia=True,yi=False,bing=False),dict(jia=False,yi=False,bing=True),
     dict(jia=True,yi=True,bing=True),dict(jia=False,yi=False,bing=False)],
    ['甲的归类正确；乙是在明确用途下获得机制新知识，应属应用；丙是基于已有知识解决产品开发未知问题，应属试验发展。',
     '甲未指向特定应用，不能归应用；乙有明确检测目标，不能归基础；只有丙的归类正确。',
     '甲研究基本原理而无特定用途，乙为明确用途取得机制新知识，丙在产品开发中系统地产生额外知识，三项分别符合。',
     '甲无明确用途，乙重点是机制新知识，丙解决尚未知问题而非按成熟规程检测，三项均不相符。'],
    ['D18','D20','D22','T15'],'按知识目标、特定用途和开发中的知识增量区分，例行活动不能冒充研发','三定义连锁分类')

add(40,
    '系统测量误差是在重复测量中保持恒定或按可预测方式变化的误差分量；随机测量误差是在重复测量中以不可预测方式变化的误差分量。本题已确认：甲仪器因零点设置问题，每次读数均比参照值高0.4；乙仪器的误差随温度按已知线性规律变化；丙仪器受不可预测的电子噪声影响，在相同条件下的误差有正有负。',
    '根据上述定义，下列归类正确的是：',
    ['甲、乙属于系统误差，丙属于随机误差；是否恒定不变不是区分二者的唯一标准',
     '甲属于系统误差，乙、丙属于随机误差；只要误差大小发生变化便归为随机误差',
     '甲、丙属于系统误差，乙属于随机误差；误差正负交替即可认定存在确定的系统规律',
     '甲、乙、丙均属于随机误差；仪器读数与参照值不完全相等便足以说明误差随机'],
    {'constant':'甲恒定分量归系统','predictable':'乙可预测变化归系统','unpredictable':'丙不可预测变化归随机'},
    [dict(constant=True,predictable=True,unpredictable=True),dict(constant=True,predictable=False,unpredictable=True),
     dict(constant=True,predictable=False,unpredictable=False),dict(constant=False,predictable=False,unpredictable=True)],
    ['甲恒定、乙可预测变化，均符合系统误差；丙不可预测，符合随机误差，三项均正确。',
     '乙虽变化但按已知规律可预测，仍属系统误差；把“变化”等同“随机”不符合定义。',
     '正负均出现不能推翻题设已确认的不可预测性，丙仍是随机误差；乙归类也不正确。',
     '与参照值不相等只表明有误差，不能决定其是否随机；甲、乙均有明确系统性。'],
    ['D06','D25','T16'],'可预测性而非是否变化、是否有正负决定误差分量类别','专业概念边界与必要条件')

add(41,
    '抽样误差是由于样本抽取的随机性造成样本指标与总体指标之间的差异，并不是调查环节发生错误的结果。非抽样误差来自调查设计、实施或处理等环节的问题，包括抽样框遗漏、对象不回答和数据录入错误等；全面调查中也可能存在。本题已说明的其他环节均无问题。',
    '根据上述定义，下列差异不能归为非抽样误差的是：',
    ['居民调查采用的完整名册覆盖全部住户，但抽中的一批租户未回复，调查员将其全部按无相关需求处理',
     '企业调查沿用两年前名录，未纳入后来成立的企业，却将据此抽到的企业用于代表当前全部企业',
     '工作人员把三份记录中的“18”录成“81”，汇总时未发现错误，导致本次公布的平均值偏高',
     '依完整名录随机抽到的住户均据实回复，数据处理无误，估计值仍仅因本次样本构成而与总体值有差别'],
    {'problem_in_survey':'差异来自设计实施处理问题而非纯随机抽取'},
    [dict(problem_in_survey=True),dict(problem_in_survey=True),dict(problem_in_survey=True),dict(problem_in_survey=False)],
    ['无回答又被擅自按无需求处理，属于实施及处理环节的问题，是非抽样误差。',
     '目标总体包括新企业而名录遗漏，属于抽样框覆盖问题，是非抽样误差。',
     '错误来自录入环节，不是随机抽样的代表性差异，属于非抽样误差。',
     '名录、回答、处理均无误，题项将差异限定为随机抽取的样本构成，属于抽样误差，不能归为非抽样误差。'],
    ['D28','D07','T17'],'随机抽取带来的差异与调查过程中的错误来源不同','误差来源边界与选非',direction='negative')

add(42,
    '方法三角互证是针对同一研究现象，采用两种以上具有不同取证机制的方法，分别形成证据，再对照其一致和不一致之处以检验解释。本题不把同一种方法仅更换调查人员、增加样本或重复计算视为不同方法；互证也不要求所有结果完全一致。',
    '根据上述定义，下列没有体现方法三角互证的是：',
    ['研究候诊拥堵时，团队将现场计时观察与患者访谈分别形成的证据相对照，对两者分歧再查证原因',
     '研究展厅动线时，团队比较电子轨迹记录与跟随访谈的证据，既记录共同发现，也解释不同之处',
     '研究社区信任时，三人分别用同一问卷询问不同居民，合并答卷后重复计算均分，认为多人参与即完成互证',
     '研究维修响应时，团队把工单系统时间戳与随访访谈形成的证据相比较，用不一致记录检查“已完成”的含义'],
    {'same_phenomenon':'针对同一现象','different_methods':'不同取证机制至少两种','separate_evidence':'各自形成证据','crosscheck':'对照证据检验解释'},
    [dict(same_phenomenon=True,different_methods=True,separate_evidence=True,crosscheck=True),
     dict(same_phenomenon=True,different_methods=True,separate_evidence=True,crosscheck=True),
     dict(same_phenomenon=True,different_methods=False,separate_evidence=False,crosscheck=False),
     dict(same_phenomenon=True,different_methods=True,separate_evidence=True,crosscheck=True)],
    ['计时观察与访谈的取证机制不同，分别形成证据后比较分歧，符合定义；存在分歧不是排除条件。',
     '轨迹记录与访谈分别提供证据，比较共同及不同发现，满足方法互证。',
     '只更换调查员和受访者，仍为同一问卷方法，且只是合并计算，未有不同方法证据的对照检验。',
     '系统记录与访谈是不同取证机制，围绕同一响应问题比较并检验解释，符合定义。'],
    ['D14','D29','T23'],'不同方法分别取证并对照解释，人数或计算次数不能替代方法差异','科研证据层级与选非',direction='negative')

add(43,
    '语用预设是话语作为背景而默认的命题。在本题限定的普通正常语境中，如果一句话的肯定式和只否定其所述事件的否定式都保留同一背景承诺，该命题可判为该话语的预设。不考虑专门反驳用词或否认背景的特殊说法，也不能把肯定句直接断言的内容当然认作预设。',
    '根据上述定义，下列背景命题能同时通过所列肯定式和否定式检验的是：',
    ['“张工已经停止值夜班”与“张工没有停止值夜班”——张工过去值过夜班',
     '“小赵至少得了两票”与“小赵没有至少得两票”——小赵至少得了一票',
     '“所有代表均已到场”与“并非所有代表均已到场”——至少有一位代表已经到场',
     '“车间今天停工了”与“车间今天没有停工”——车间昨天处于开工状态'],
    {'positive_preserves':'肯定式保留该命题','negative_preserves':'否定式仍保留该命题'},
    [dict(positive_preserves=True,negative_preserves=True),dict(positive_preserves=True,negative_preserves=False),
     dict(positive_preserves=True,negative_preserves=False),dict(positive_preserves=False,negative_preserves=False)],
    ['在题设限定的普通事件否定中，停止或未停止均以过去值夜班为背景，该背景在两式中都保留。',
     '至少两票能推出至少一票，但否定至少两票允许零票，因此后者不能保留所列命题。',
     '所有人到场能推出有人到场，但并非所有人到场允许无人到场，不能保留所列命题。',
     '今天是否停工均未承诺昨天开工；从今天状态不能补出昨天状态。'],
    ['D03','D18','T18'],'预设须在普通的事件否定下保留，不能仅由肯定断言推出','语言定义与否定测试',data={'kind':'presupposition_worlds','options':[
        {'positive_worlds':[{'past_duty':True,'now_duty':False}],'negative_worlds':[{'past_duty':True,'now_duty':True}],'claim_key':'past_duty'},
        {'positive_worlds':[{'one_vote':True}],'negative_worlds':[{'one_vote':False},{'one_vote':True}],'claim_key':'one_vote'},
        {'positive_worlds':[{'someone_arrived':True}],'negative_worlds':[{'someone_arrived':False},{'someone_arrived':True}],'claim_key':'someone_arrived'},
        {'positive_worlds':[{'open_yesterday':False},{'open_yesterday':True}],'negative_worlds':[{'open_yesterday':False},{'open_yesterday':True}],'claim_key':'open_yesterday'}]})

add(44,
    '内聚焦叙述把信息限制在某一人物能够感知、知道或想到的范围内，可以直接呈现该人物的内心，但不能越出其知识范围直接揭示他人的内心或未知事实。外聚焦叙述只呈现外部可观察的言行，不直接进入人物内心。能同时直接揭示多人的内心，或告知聚焦人物不可能知道的事实，则超出了本题的内聚焦范围。',
    '根据上述定义，下列含有内心呈现且符合内聚焦限制的片段是：',
    ['林岚把信放进口袋。门外的人并未敲门，只抬手碰了碰帽檐，随后沿着走廊走到楼梯口',
     '林岚把信放进口袋，心里后悔没有早些打开；门外的陈伯却暗自庆幸她没有看见信里的秘密',
     '林岚把信放进口袋，想着母亲会不会生气。她听见门外轻响，猜是陈伯回来了，却不敢开门确认',
     '林岚把信放进口袋，想着明天再读。她还不知道，那封信里的地址早已被改掉，真正的收信人已经搬走'],
    {'one_mind':'直接内心信息限于一个人物','within_knowledge':'不直接揭示该人物未知事实','inner_present':'确有内心呈现而非纯外部观察'},
    [dict(one_mind=True,within_knowledge=True,inner_present=False),dict(one_mind=False,within_knowledge=False,inner_present=True),
     dict(one_mind=True,within_knowledge=True,inner_present=True),dict(one_mind=True,within_knowledge=False,inner_present=True)],
    ['只描述可观察动作和声音，没有直接内心呈现，属于本题的外聚焦。',
     '同时直接进入林岚和陈伯的内心，越出单一人物的知识范围。',
     '所见所闻与担忧、猜测都限于林岚，陈伯是否回来没有被叙述者直接证实，符合内聚焦。',
     '叙述者直接告诉读者林岚尚不知道的改址和搬家事实，超出了林岚的知识范围。'],
    ['D03','D08','T19'],'内心信息限于单个人物，并不越出其知识范围','人文专业概念与观察层级')

add(45,
    '溯因推理是从已接受的现象出发，比较候选解释，提出较能解释这些现象的假说；即使推理合理，假说也并非由前提必然保证。演绎推理则要求：当前提为真时，结论必然为真。只将重复观察的频率推广到未观察对象，而不提出解释假说的推断，不计入本题的溯因推理。',
    '根据上述定义，下列属于溯因推理的是：',
    ['工程师根据“凡更换控制板的设备都须重新校准”和该设备已更换控制板，认定该设备须重新校准',
     '两个传感器同时失信号，维修组比较不同原因，暂取共用电源中断而非各自损坏作为较佳的待检解释',
     '质检员在连续抽查的二十件样品中发现十八件合格，据此估计下一件产品合格的可能性也较大',
     '档案员先查到设备于某日入库，再依保管制度计算应归入哪个年度目录，将其放入相应文件夹'],
    {'phenomenon':'从已接受现象出发','explanation':'比较并选择解释性假说','not_guaranteed':'结论不是前提必然保证'},
    [dict(phenomenon=True,explanation=False,not_guaranteed=False),dict(phenomenon=True,explanation=True,not_guaranteed=True),
     dict(phenomenon=True,explanation=False,not_guaranteed=True),dict(phenomenon=True,explanation=False,not_guaranteed=False)],
    ['按全称规则和个体事实推出必然结论，属于演绎，未提出解释假说。',
     '由共同失信号现象比较解释并选出待检假说，解释仍可能被后续证据推翻，符合溯因。',
     '只由观察频率估计下一件合格概率，没有提出解释现象的假说，按题设不属于溯因。',
     '按日期和既定制度进行归类，不是比较解释并提出假说。'],
    ['D21','D27','T24'],'解释已有现象的可错假说不同于必然演绎及纯频率推广','推理定义的方向与认识强度')

add(46,
    '某学习平台规定：激活率为已激活人数除以注册人数，提交率为至少提交过一次作业的人数除以已激活人数，通过率为最终通过的人数除以至少提交过一次作业的人数；同一人的重复提交只计一次提交人数。某期有注册者120人，已激活90人，共收到100次作业提交，来自75人，其中60人最终通过。百分数需要时保留一位小数。',
    '根据上述定义，下列统计表述正确的是：',
    ['激活率为75%，提交率为111.1%；提交次数多于已激活人数，故提交率可以超过100%',
     '激活率为83.3%，通过率为60%；前者使用注册人数作分母，后者使用全部提交次数作分母',
     '提交率83.3%，通过率80%；提交人数只计75人，重复提交不把通过率分母增到100',
     '提交率为62.5%，通过率为50%；同一批注册者应作为各类人数比率的统一分母'],
    {'claims_correct':'选项中全部比率及口径符合定义'},
    [dict(claims_correct=False),dict(claims_correct=False),dict(claims_correct=True),dict(claims_correct=False)],
    ['激活率90/120=75%正确；提交率应为75/90而非100/90，次数和人数不能混用。',
     '激活率应为90/120=75%；通过率应为60/75=80%，不能将次数当分母。',
     '提交率75/90≈83.3%，通过率60/75=80%，均按题定人数口径计算，两项正确。',
     '两项均擅自改以注册人数为分母；定义中提交率分母为已激活人数，通过率分母为提交人数。'],
    ['D07','D12'],'分子分母须使用相应人数，同一人多次操作不增加人数','多定义比率及去重单位',difficulty='中高',data={'kind':'rates','registered':120,'activated':90,'submitting_people':75,'attempts':100,'passed':60,'claims':[
        {'activation':75,'submission':111.1},{'activation':83.3,'pass':60},{'submission':83.3,'pass':80},{'submission':62.5,'pass':50}]})

add(47,
    '帕累托改进是指从一种安排转到另一种安排后，至少一人的状况严格变好，并且没有任何人的状况变差。本题用各人对最终结果的评价值表示其状况，数值越高表示本人越满意，不作人与人之间评价值的直接比较；未实际兑现的补偿不计入最终结果。',
    '根据上述定义，下列变更构成帕累托改进的是：',
    ['三位使用者的评价值由（6、6、6）变为（10、5、7），虽然第二人减少一分，但三人总分提高四分',
     '三位使用者的评价值由（6、6、6）变为（8、6、7），第二人保持原状，第一人与第三人均比原来满意',
     '三位使用者的评价值由（6、6、6）变为（9、4、7），第一人表示以后会补偿第二人，但目前尚未兑现',
     '三位使用者的评价值由（6、6、6）变为（6、6、6），三人均未变差，管理者将方案命名为共享提升计划'],
    {'someone_better':'至少一人严格更好','nobody_worse':'没有任何人更差'},
    [dict(someone_better=True,nobody_worse=False),dict(someone_better=True,nobody_worse=True),
     dict(someone_better=True,nobody_worse=False),dict(someone_better=False,nobody_worse=True)],
    ['第二人6→5变差，整体总分上升不能替代无人变差条件。',
     '第一人6→8、第三人6→7严格更好，第二人维持6，无人变差，满足两个条件。',
     '第二人6→4已经变差，未兑现承诺不能计入结果，仍不符合。',
     '无人变差成立，但也无人严格变好，缺少改进条件；方案名称不能改变结果。'],
    ['D07','D19','T20'],'逐人核验无人变差且至少一人严格改善，不能以总和或承诺替代','合取定义与数量记录复算',data={'kind':'pareto','before':[6,6,6],'after':[[10,5,7],[8,6,7],[9,4,7],[6,6,6]]})

add(48,
    '适应性管理是在管理效果存在重要不确定性时，将管理行动与学习结合：明确目标和待检验的作用认识，实施行动并监测结果，据此评估、更新认识，再调整后续管理。监测本身或遇事灵活处理都不足以构成完整的适应性管理。本题要求上述环节形成可反馈的连续过程。',
    '根据上述定义，下列没有形成完整适应性管理过程的是：',
    ['湿地管理者以提高鸟类栖息利用率为目标，不确定补水时点的效果，按预期机制试行两种安排，连续监测鸟类使用情况并据比较结果修订下一季方案',
     '林场以增加幼树更新量为目标，尚不确定疏伐强度与更新效果的关系，提出待检解释，分区实施后监测幼树，据此更新模型并调整后续疏伐',
     '公园突遇暴雨便临时封闭步道，事后将积水点拍照归档，仍沿用原方案，未用记录检验或更新作用认识',
     '河道治理效果尚不确定，团队明确水质目标并提出可检验预期，实施后持续测量、评估，据所得认识改订后续措施'],
    {'uncertainty':'存在管理效果重要不确定性','explicit':'明确目标及待检作用认识','act_monitor':'行动并监测','learn_adjust':'评估更新认识并调整后续'},
    [dict(uncertainty=True,explicit=True,act_monitor=True,learn_adjust=True),dict(uncertainty=True,explicit=True,act_monitor=True,learn_adjust=True),
     dict(uncertainty=False,explicit=False,act_monitor=True,learn_adjust=False),dict(uncertainty=True,explicit=True,act_monitor=True,learn_adjust=True)],
    ['不确定性、作用预期、行动监测和反馈修订均已形成连续过程，符合定义。',
     '分区行动用于检验解释，并根据监测更新模型及后续措施，满足完整过程。',
     '有临时应对和记录，但未用记录检验作用认识，更未据学习更新后续管理，反馈学习链条缺失。',
     '目标、预期、实施监测、偏差评估及改订措施构成反馈学习闭环，符合定义。'],
    ['D10','D13','D15','T21'],'管理行动必须带来可用于后续决策的反馈学习，不止监测和应急','程序条件合取与选非',direction='negative')

add(49,
    '同源结构是不同谱系从共同祖先继承而来的对应结构，其现在的功能可以不同；趋同特征是在不同谱系中独立形成、因相似功能需要而相似的特征。判断必须保持所比较的结构层级一致。题设已知：物种甲、乙的前肢骨架均继承自共同祖先；该祖先没有滑翔膜，甲、乙分别在各自谱系中独立形成相似滑翔膜，用于相近环境中的滑翔。',
    '根据上述定义，下列判断正确的是：',
    ['前肢骨架属于同源结构；相似滑翔膜属于趋同特征，二者的比较层级不同，并不矛盾',
     '前肢骨架和滑翔膜均属于同源结构；只要物种存在共同祖先，其后来相似结构都必定同源',
     '前肢骨架和滑翔膜均属于趋同特征；只要现在承担相近功能，就不能再判断结构同源',
     '前肢骨架属于趋同特征，滑翔膜属于同源结构；前者出现在较早阶段，后者出现在较晚阶段'],
    {'skeleton':'继承的前肢骨架归同源','membrane':'独立形成的相似滑翔膜归趋同'},
    [dict(skeleton=True,membrane=True),dict(skeleton=True,membrane=False),dict(skeleton=False,membrane=True),dict(skeleton=False,membrane=False)],
    ['前肢骨架具有明确共同祖先来源；滑翔膜在祖先不存在而在两谱系独立出现，分别符合两个定义。',
     '共同祖先的存在不意味着后来每种相似特征都由祖先继承，滑翔膜已明确为独立形成。',
     '功能相近不能推翻题设确认的骨架继承关系，同源判据是结构来源，不是功能是否相近。',
     '归类完全颠倒；出现早晚不是定义中的区分标准，应看共同继承还是独立形成。'],
    ['D08','D18','D20','T22'],'来源及结构层级决定同源或趋同，功能相似不能直接替代来源证据','生物概念双层对象辨析')

add(50,
    '本题区分两种围绕同一有限资源的竞争：干扰性竞争是通过驱赶、阻挡或抑制对方等直接方式，降低对方获得资源的机会；利用性竞争是先利用共同资源，使剩余可用量减少，间接降低对方的资源获取。仅有共同生活或相同需求，而没有资源限制及不利影响，不足以认定上述竞争。',
    '根据上述定义，下列情境与所作归类不相符的是：',
    ['在有限的附着空间内，一类生物释放物质直接抑制另一类在附近定殖，使后者难以占据空间——干扰性竞争',
     '两种微生物利用同一批有限营养，一种先大量吸收，另一种因剩余营养不足而生长受限——利用性竞争',
     '水源有限时，一群鸟持续驱赶另一群靠近饮水点，使后者即使在水尚有剩余时也难以进入——干扰性竞争',
     '两类植物依赖同层土壤水分，一类先吸收导致可用水量下降，另一类因剩余水不足而受限——干扰性竞争'],
    {'shared_limited':'同一有限资源','mechanism_label':'所标类别符合直接干扰或先利用的机制'},
    [dict(shared_limited=True,mechanism_label=True),dict(shared_limited=True,mechanism_label=True),
     dict(shared_limited=True,mechanism_label=True),dict(shared_limited=True,mechanism_label=False)],
    ['有限空间是共同资源，释放物质直接抑制对方定殖，符合干扰性竞争。',
     '通过先吸收使营养剩余量减少，并非直接攻击对方，符合利用性竞争。',
     '直接驱赶使对方无法接近水源，归为干扰性竞争正确；尚有水不改变直接阻止获取的机制。',
     '题项只描述先吸水造成剩余量减少，属于利用性竞争；没有直接驱赶、阻挡或抑制对方，标签错误。'],
    ['D02','D20','D29','T25'],'共同有限资源是前提，再按直接阻碍与先消耗资源区分机制','上位条件与机制辨类选非',direction='negative')


def attach_classification_model(n, definitions, cases, claims):
    q = next(q for q in QUESTIONS if q['n']==n)
    q['model']['data'] = {'kind':'classification', 'definitions':definitions,
                          'cases':cases, 'option_claims':claims}


def claim(case, definition, key):
    return {'case':case,'definition':definition,'matrix_key':key}


# For paired/multi-definition items, derive each label from underlying
# mechanism facts rather than treating "label correct" as a primitive fact.
control = {
    'feedback':['all','output_error','reduce_error'],
    'feedforward':['all','external_detected','before_output','prior_relation']}
fb = dict(output_error=True,reduce_error=True,external_detected=False,before_output=False,prior_relation=False)
ff = dict(output_error=False,reduce_error=False,external_detected=True,before_output=True,prior_relation=True)
fixed = dict(output_error=False,reduce_error=False,external_detected=False,before_output=False,prior_relation=False)
attach_classification_model(25, control,
    {'a1':fb,'a2':ff,'b1':fixed,'b2':fb,'c1':fb,'c2':ff,'d1':fb,'d2':fb},
    [[claim('a1','feedforward','first_label'),claim('a2','feedback','second_label')],
     [claim('b1','feedforward','first_label'),claim('b2','feedback','second_label')],
     [claim('c1','feedback','first_label'),claim('c2','feedforward','second_label')],
     [claim('d1','feedback','first_label'),claim('d2','feedforward','second_label')]])

sample_defs = {'stratified':['all','each_layer','individual_random'],
               'cluster':['all','group_random','all_in_group']}
stratified = dict(each_layer=True,individual_random=True,group_random=False,all_in_group=False)
cluster = dict(each_layer=False,individual_random=False,group_random=True,all_in_group=True)
volunteer = dict(each_layer=True,individual_random=False,group_random=False,all_in_group=False)
multistage = dict(each_layer=False,individual_random=True,group_random=True,all_in_group=False)
one_layer = dict(each_layer=False,individual_random=True,group_random=False,all_in_group=False)
attach_classification_model(27,sample_defs,
    {'a1':stratified,'a2':cluster,'b1':volunteer,'b2':multistage,
     'c1':cluster,'c2':one_layer,'d1':stratified,'d2':cluster},
    [[claim('a1','cluster','first_label'),claim('a2','stratified','second_label')],
     [claim('b1','stratified','first_label'),claim('b2','cluster','second_label')],
     [claim('c1','cluster','first_label'),claim('c2','stratified','second_label')],
     [claim('d1','stratified','first_label'),claim('d2','cluster','second_label')]])

attach_classification_model(31,
    {'mediator':'effect_chain','moderator':'changes_strength'},
    {'strategy':dict(effect_chain=True,changes_strength=False),
     'sleep':dict(effect_chain=False,changes_strength=True)},
    [[claim('strategy','moderator','chain_label'),claim('sleep','mediator','strength_label')],
     [claim('strategy','mediator','chain_label'),claim('sleep','mediator','strength_label')],
     [claim('strategy','moderator','chain_label'),claim('sleep','moderator','strength_label')],
     [claim('strategy','mediator','chain_label'),claim('sleep','moderator','strength_label')]])

u = dict(wide_use=True,no_special_adaptation=True,individual_case=False,necessary=False,appropriate=False,no_undue=True)
r = dict(wide_use=False,no_special_adaptation=False,individual_case=True,necessary=True,appropriate=True,no_undue=True)
not_u = dict(wide_use=False,no_special_adaptation=False,individual_case=False,necessary=False,appropriate=False,no_undue=True)
burdensome = dict(wide_use=False,no_special_adaptation=False,individual_case=True,necessary=True,appropriate=True,no_undue=False)
attach_classification_model(36,
    {'universal':['all','wide_use','no_special_adaptation'],
     'accommodation':['all','individual_case','necessary','appropriate','no_undue']},
    {'a1':r,'a2':u,'b1':u,'b2':r,'c1':not_u,'c2':r,'d1':u,'d2':burdensome},
    [[claim('a1','universal','first_label'),claim('a2','accommodation','second_label')],
     [claim('b1','universal','first_label'),claim('b2','accommodation','second_label')],
     [claim('c1','universal','first_label'),claim('c2','accommodation','second_label')],
     [claim('d1','universal','first_label'),claim('d2','accommodation','second_label')]])

attach_classification_model(39,
    {'basic':['all','new_knowledge',['not','specific_use'],['not','development'],['not','routine']],
     'applied':['all','new_knowledge','specific_use',['not','development'],['not','routine']],
     'development':['all','new_knowledge','development',['not','routine']],
     'routine':'routine'},
    {'jia':dict(new_knowledge=True,specific_use=False,development=False,routine=False),
     'yi':dict(new_knowledge=True,specific_use=True,development=False,routine=False),
     'bing':dict(new_knowledge=True,specific_use=True,development=True,routine=False)},
    [[claim('jia','basic','jia'),claim('yi','development','yi'),claim('bing','applied','bing')],
     [claim('jia','applied','jia'),claim('yi','basic','yi'),claim('bing','development','bing')],
     [claim('jia','basic','jia'),claim('yi','applied','yi'),claim('bing','development','bing')],
     [claim('jia','applied','jia'),claim('yi','development','yi'),claim('bing','routine','bing')]])

attach_classification_model(40,
    {'systematic':'predictable','random':['not','predictable']},
    {'jia':dict(predictable=True),'yi':dict(predictable=True),'bing':dict(predictable=False)},
    [[claim('jia','systematic','constant'),claim('yi','systematic','predictable'),claim('bing','random','unpredictable')],
     [claim('jia','systematic','constant'),claim('yi','random','predictable'),claim('bing','random','unpredictable')],
     [claim('jia','systematic','constant'),claim('yi','random','predictable'),claim('bing','systematic','unpredictable')],
     [claim('jia','random','constant'),claim('yi','random','predictable'),claim('bing','random','unpredictable')]])

attach_classification_model(50,
    {'interference':['all','limited','adverse','direct'],
     'exploitation':['all','limited','adverse','depletion',['not','direct']]},
    {'a':dict(limited=True,adverse=True,direct=True,depletion=False),
     'b':dict(limited=True,adverse=True,direct=False,depletion=True),
     'c':dict(limited=True,adverse=True,direct=True,depletion=False),
     'd':dict(limited=True,adverse=True,direct=False,depletion=True)},
    [[claim('a','interference','mechanism_label')],[claim('b','exploitation','mechanism_label')],
     [claim('c','interference','mechanism_label')],[claim('d','interference','mechanism_label')]])

for q in QUESTIONS:
    if q['n'] in {26,31,36,39,43,46,49}: q['difficulty']='高'
    elif q['n'] in {24,34,40,47}: q['difficulty']='中'


def extra_checks(question):
    """Recompute numerical/procedural semantics directly from raw records."""
    d = question['model']['data']
    kind = d.get('kind')
    checks = {}
    if kind == 'classification':
        traces = []
        all_match = True
        for i,claims in enumerate(d['option_claims']):
            row = []
            for c in claims:
                actual = bool(evaluate(d['definitions'][c['definition']],d['cases'][c['case']]))
                expected = question['model']['option_facts'][i][c['matrix_key']]
                all_match &= actual == expected
                row.append({'case':c['case'],'claimed_definition':c['definition'],
                            'underlying_facts':d['cases'][c['case']],
                            'satisfies_claimed_definition':actual,
                            'matrix_key':c['matrix_key']})
            traces.append(row)
        checks = {'classification_trace':traces,'classification_matches_facts':all_match}
    elif kind == 'lexicographic':
        candidates = list(d['rows'])
        stages = []
        for col, maximize in enumerate(d['maximize']):
            best = (max if maximize else min)(d['rows'][k][col] for k in candidates)
            candidates = [k for k in candidates if d['rows'][k][col] == best]
            stages.append(list(candidates))
        checks = {'computed_stages':stages, 'declared_stages_match':stages == d['stages']}
    elif kind == 'presupposition_worlds':
        preserved = []
        for opt in d['options']:
            k = opt['claim_key']
            preserved.append([all(w[k] for w in opt['positive_worlds']),
                              all(w[k] for w in opt['negative_worlds'])])
        expected = [[f['positive_preserves'],f['negative_preserves']] for f in question['model']['option_facts']]
        checks = {'truth_world_preservation':preserved,'worlds_match_facts':preserved == expected}
    elif kind == 'rates':
        rates = {'activation':round(100*d['activated']/d['registered'],1),
                 'submission':round(100*d['submitting_people']/d['activated'],1),
                 'pass':round(100*d['passed']/d['submitting_people'],1)}
        claims = [all(rates[k] == v for k,v in c.items()) for c in d['claims']]
        checks = {'computed_rates_percent':rates,'claim_truth':claims,
                  'raw_rates_match_facts':claims == [f['claims_correct'] for f in question['model']['option_facts']]}
    elif kind == 'pareto':
        tuples = [[any(a>b for a,b in zip(row,d['before'])),
                   all(a>=b for a,b in zip(row,d['before']))] for row in d['after']]
        checks = {'computed_individual_conditions':tuples,
                  'raw_utilities_match_facts':tuples == [[f['someone_better'],f['nobody_worse']] for f in question['model']['option_facts']]}
    return checks


def verify():
    source = json.loads((ROOT/'sources_definitions.json').read_text(encoding='utf8'))
    allowed_refs = {x['id'] for x in source['cases']} | {x['id'] for x in source['technical_definition_sources']}
    report = []
    for q in QUESTIONS:
        m = q['model']
        matched = [bool(evaluate(m['expression'], f)) for f in m['option_facts']]
        selected = ['ABCD'[i] for i,v in enumerate(matched) if v == (m['direction']=='positive')]
        extra = extra_checks(q)
        extra_ok = all(v for k,v in extra.items() if k.endswith('_match') or k.endswith('_facts'))
        source_ok = all(r in allowed_refs for r in q['source_refs'])
        shape_ok = len(q['options']) == len(m['option_facts']) == len(m['option_evidence']) == 4
        matrix = [{
            'option':'ABCD'[i],
            'necessary_conditions':{key:f[key] for key in m['requirements']},
            'definition_expression_satisfied':matched[i],
            'selected_by_question_direction':'ABCD'[i] in selected,
            'specific_evidence':m['option_evidence'][i]
        } for i,f in enumerate(m['option_facts'])]
        ok = shape_ok and source_ok and extra_ok and len(selected)==1 and selected[0]==q['answer']
        report.append({'n':q['n'],'passed':ok,'direction':m['direction'],
                       'expression':m['expression'],'necessary_condition_matrix':matrix,
                       'computed_selected_options':selected,'unique':len(selected)==1,
                       'matches_published_answer':len(selected)==1 and selected[0]==q['answer'],
                       'source_refs_valid':source_ok,'independent_recomputation':extra,
                       'option_lengths':[len(x) for x in q['options']]})
    return {'passed':len(QUESTIONS)==30 and [q['n'] for q in QUESTIONS]==list(range(21,51)) and all(x['passed'] for x in report),
            'question_count':len(QUESTIONS),'global_numbers':[q['n'] for q in QUESTIONS],
            'negative_questions':[q['n'] for q in QUESTIONS if q['model']['direction']=='negative'],
            'difficulty_counts':dict(Counter(q['difficulty'] for q in QUESTIONS)),
            'answer_distribution':dict(Counter(q['answer'] for q in QUESTIONS)),
            'verification_scope':'可执行要件合取/否定方向/唯一性及4题原始数据复算；自然语言到要件的映射另需无答案独立试解复核，不将此程序检查冒称独立盲审。',
            'items':report}


if __name__ == '__main__':
    (ROOT/'questions_definitions.json').write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    result=verify()
    (ROOT/'verification_definitions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k!='items'},ensure_ascii=False))
    if not result['passed']: raise SystemExit(1)

