"""第26—35题原创逻辑判断源稿；共材题附穷举验证。"""

from collections import Counter
from itertools import product


COMMON = [
    '根据以下材料，回答第31—35题。',
    '某材料检测中心收到P、Q、R、S、T、U六份样本，需分别交由甲、乙、丙三条检测流程处理。每份样本只使用一条流程，每条流程恰好处理两份样本。安排还须满足以下条件：',
    '（1）P与S使用同一流程。',
    '（2）Q与T使用不同流程。',
    '（3）若R使用甲流程，则U使用丙流程。',
]


LOGIC = [
    dict(
        n=26, category='逻辑判断',
        stem='某编辑部试用一项只会标红易混字、不会自动替换文字的审校功能。试用后，刊印稿每万字易混字错误数由8处降至5处。负责人认为，下降的错误中至少有一部分是编辑按照标红提示修改文字带来的。',
        ask='上述判断成立必须以下列哪项为前提？',
        options=[
            '该功能能够标出稿件中所有的易混字错误，且从不误报',
            '至少有一处被标红的真实易混字错误，在刊印前被编辑依据该提示改正',
            '编辑收到标红提示后，没有增加通篇人工校对的时间',
            '试用前后原稿中的易混字错误密度完全相同',
        ],
        answer='B', point='论证前提：提示到改错的作用链',
        analysis=[
            '结论限定了具体作用路径：编辑按照标红提示改字，且这一路径至少促成了部分下降。标红本身不会替换文字；若没有一处被标出的真实错误因此在刊印前改正，这条路径就无法成立。B项是必要前提。',
            'A项要求全部标出且绝不误报，强于结论所需；C项即使为假，编辑也可能既增加校对又利用标红；D项即使为假，标红仍可能改正部分错误，原稿差异只影响前后统计如何解释。故正确答案为B。',
        ],
        image=None, explanation_image=None, level='中等',
    ),
    dict(
        n=27, category='逻辑判断',
        stem='某展馆把展品检索目录由按年代排列改为“主题—年代—展品”三级目录。改版后，访客自行找到指定展品的比例由60%升至74%。馆方认为，新目录帮助访客更准确地定位展品。',
        ask='以下哪项如果为真，不能支持馆方的判断？',
        options=[
            '起始检索能力相近的访客随机使用两版目录，新版使用者找对展品的比例更高',
            '改版后，访客把名称相似的两件展品弄混的比例明显下降',
            '访客在新版目录中可先按主题缩小候选展品范围，因而减少了误选',
            '新版目录使访客找到指定展品所在展厅的用时缩短，但没有记录进入展厅后是否选对那件展品',
        ],
        answer='D', point='论证评价：识别与结论无关的信息',
        analysis=[
            '结论只涉及目录结构能否提高定位展品的准确率。A项提供能力相近访客的随机对照，B项给出误选下降的直接现象，C项说明三级目录减少误选的机制，均能支持结论。',
            'D项只说明更快找到展厅；同一展厅仍可能有多件展品，未记录是否选对指定展品，因而不能支持“更准确地定位展品”。本题选不能支持项，故正确答案为D。',
        ],
        image=None, explanation_image=None, level='中等',
    ),
    dict(
        n=28, category='逻辑判断',
        stem='某机构规定：只有完成数据脱敏且通过双人复核，数据包才能进入共享区；如果某数据包已经完成脱敏但仍标记为“待核验”，它就不能通过双人复核。现有一份数据包X已经进入共享区。',
        ask='根据上述规定，可以推出以下哪项？',
        options=[
            'X已完成脱敏，且没有标记为“待核验”',
            'X已经被至少一个外部部门下载使用',
            '凡没有标记为“待核验”的数据包均可进入共享区',
            '只要完成脱敏并通过双人复核，数据包就一定进入共享区',
        ],
        answer='A', point='翻译推理：必要条件与逆否推理',
        analysis=[
            '“只有脱敏且通过复核，才能进入共享区”表示进入共享区→已脱敏且已复核。X已进入共享区，故两项必要条件均满足。又因“已脱敏且待核验→未通过复核”，X在已脱敏、已复核的前提下不能仍标记“待核验”。A项可推出。',
            'B项的下载情况没有给出；C项把未待核验误当作进入共享区的充分条件；D项把两个必要条件误当作充分条件。故正确答案为A。',
        ],
        image=None, explanation_image=None, level='较难',
    ),
    dict(
        n=29, category='逻辑判断',
        stem='一家工厂把操作培训中的一次性演示改为分步演示，并在每一步后要求学员先预测下一步操作。改版后，学员首次上机的操作错误率下降。负责人认为，预测下一步操作这一环节是错误率下降的主要原因。',
        ask='以下哪项如果为真，最能支持负责人的观点？',
        options=[
            '改版后，参加预测环节的学员更愿意主动提问，但未单独记录这些学员的首次上机错误',
            '设备和讲师均未改变，改版后整体错误率下降，但分步演示和预测环节仍是同时引入的',
            '起始水平相近的学员随机分组，均接受同一讲师的分步演示并使用同种设备；只有一组在每步后预测操作，该组首次上机错误率更低',
            '预测环节参与次数较多的学员错误率较低，但他们在改版前的操作基础也明显更好',
        ],
        answer='C', point='加强论证：控制其他变量的对照试验',
        analysis=[
            '改版同时包含分步演示和逐步预测，须把两者分开比较。C项让两组在起点、讲师、设备与分步演示上相同，只改变是否预测；预测组首次上机错误率更低，直接支持预测环节的独立作用。',
            'A项观察到提问积极性，但未提供目标结果；B项排除了设备和讲师变化，却仍无法区分分步演示与预测的作用；D项的相关性可能来自学员原有基础较好。三项的证据均弱于C项。故正确答案为C。',
        ],
        image=None, explanation_image=None, level='中等',
    ),
    dict(
        n=30, category='逻辑判断',
        stem='某服务平台把一份冗长的操作说明拆成三个依次显示的步骤。改版后，使用者完成任务的正确率提高。研究者认为，分步呈现使使用者更准确地理解了任务要求。',
        ask='以下除哪项外，均能削弱研究者的结论？',
        options=[
            '新版同时把需要判断的任务条件从五项减少为三项',
            '旧版统计了所有开始任务的使用者，新版只统计完成全部步骤的使用者',
            '新版除分步说明外，还新增了一道与任务几乎相同的示例题',
            '两版使用者的改版前任务理解水平相近，且两版均按完成全部步骤者及同一评分标准计算正确率',
        ],
        answer='D', point='削弱论证选非：任务变化、选择偏差与测量控制',
        analysis=[
            'A项使新版任务本身更简单，B项改变统计人群并可能排除失败者，C项让示例题成为另一个提高正确率的原因。这三项均使“分步呈现”难以单独解释正确率提高。',
            'D项让两版使用者的起点、统计分母和评分标准可比，减少了另一个解释空间，并不削弱分步呈现的作用。本题选不能削弱项，故正确答案为D。',
        ],
        image=None, explanation_image=None, level='较难',
    ),
    dict(
        n=31, category='逻辑判断',
        stem='下列哪一种完整安排可能成立？', ask='',
        options=[
            '甲：R、T；乙：P、S；丙：Q、U',
            '甲：Q、R；乙：T、U；丙：P、S',
            '甲：P、S；乙：Q、T；丙：R、U',
            '甲：P、R；乙：S、T；丙：Q、U',
        ],
        answer='A', point='组合推理：逐项检验配额与条件',
        analysis=[
            '每种流程均需恰好处理两份，先看P与S是否同流程、Q与T是否不同，再检查“R用甲→U用丙”。A项三个流程各两份，P、S均用乙，Q用丙而T用甲；R用甲时U用丙，全部满足。',
            'B项R用甲而U用乙，违反条件（3）；C项Q与T均用乙，违反条件（2）；D项P用甲而S用乙，违反条件（1）。故正确答案为A。',
        ],
        image=None, explanation_image=None, level='中等',
    ),
    dict(
        n=32, category='逻辑判断',
        stem='若U使用甲流程，且Q不使用甲流程，则以下哪项一定成立？', ask='',
        options=[
            'P与S使用乙流程',
            'R使用乙流程',
            'T使用甲流程',
            'Q使用丙流程',
        ],
        answer='C', point='组合推理：两项附加条件与条件链交叉',
        analysis=[
            'U已经占甲的一个名额。若R也用甲，条件（3）会要求U用丙，矛盾，因此R不能用甲。P、S必须同流程，甲仅剩一个名额，二者也不能用甲。题设又排除Q用甲，于是甲的第二份只能是T，C项必真。',
            '余下存在两种不同安排：P、S用乙、Q和R用丙；或P、S用丙、Q和R用乙。两种安排中T、U均用甲，且Q与T不同。前一种否定B项，后一种否定A、D项。故正确答案为C。',
        ],
        image=None, explanation_image=None, level='较难',
    ),
    dict(
        n=33, category='逻辑判断',
        stem='若R使用甲流程，则以下哪项一定成立？', ask='',
        options=[
            'Q使用甲流程',
            'P使用乙流程',
            'T使用丙流程',
            'U使用乙流程',
        ],
        answer='B', point='组合推理：条件链与同组配额',
        analysis=[
            'R使用甲时，条件（3）迫使U使用丙。P与S必须同流程；若二者使用甲，甲将与R合计三份；若二者使用丙，丙将与U合计三份，均违反配额。因此P、S只能共同使用乙流程，B项一定成立。',
            'Q可以使用甲而T使用丙，也可以Q使用丙而T使用甲；A、C项均只在部分安排中成立。U已使用丙，不可能使用乙，D项错误。故正确答案为B。',
        ],
        image=None, explanation_image=None, level='较难',
    ),
    dict(
        n=34, category='逻辑判断',
        stem='若Q使用甲流程，以下哪项不可能成立？', ask='',
        options=[
            'R使用甲流程',
            'P使用丙流程',
            'U使用乙流程',
            'T使用丙流程',
        ],
        answer='C', point='组合推理选非：条件分支与反例构造',
        analysis=[
            '穷举满足公共条件且Q用甲的安排，仅有三类：（一）P、S用乙，R用甲，T、U用丙；（二）P、S用乙，R、T用丙，U用甲；（三）P、S用丙，R、T用乙，U用甲。三类中U只可能用甲或丙，均不会用乙。',
            '第一类证明A项和D项可以成立，第三类证明B项可以成立；C项在三类中均不成立。本题选不可能项，故正确答案为C。',
        ],
        image=None, explanation_image=None, level='较难',
    ),
    dict(
        n=35, category='逻辑判断',
        stem='在公共条件之外，再给出以下哪组信息，可以唯一确定六份样本使用的流程？', ask='',
        options=[
            'P使用甲，Q使用乙',
            'P使用乙，Q使用甲',
            'P使用丙，Q使用乙',
            'P使用甲，Q使用丙',
        ],
        answer='C', point='组合推理：附加条件的唯一解',
        analysis=[
            '逐项加入P与Q的去向并穷举符合公共条件的安排，A、B、D三项各留下两种；C项只留下一种：甲流程处理T、U，乙流程处理Q、R，丙流程处理P、S。因此只有C项能唯一确定全部安排。',
            '例如A项仍可令R用乙、T和U用丙，或令R和T用丙、U用乙；B项可令R用甲或丙；D项可令R用乙或丙。上述余解说明三项都不足以唯一确定安排。故正确答案为C。',
        ],
        image=None, explanation_image=None, level='较难',
    ),
]


def _valid_common(case):
    counts = Counter(case.values())
    return (
        all(counts[flow] == 2 for flow in '甲乙丙')
        and case['P'] == case['S']
        and case['Q'] != case['T']
        and (case['R'] != '甲' or case['U'] == '丙')
    )


COMMON_CASES = [dict(zip('PQRSTU', values)) for values in product('甲乙丙', repeat=6)
                if _valid_common(dict(zip('PQRSTU', values)))]


def verify_common():
    assert len(COMMON_CASES) == 10, len(COMMON_CASES)
    option31 = [
        dict(P='乙', Q='丙', R='甲', S='乙', T='甲', U='丙'),
        dict(P='丙', Q='甲', R='甲', S='丙', T='乙', U='乙'),
        dict(P='甲', Q='乙', R='丙', S='甲', T='乙', U='丙'),
        dict(P='甲', Q='丙', R='甲', S='乙', T='乙', U='丙'),
    ]
    assert [_valid_common(case) for case in option31] == [True, False, False, False]
    u_a_q_not_a = [case for case in COMMON_CASES if case['U'] == '甲' and case['Q'] != '甲']
    assert len(u_a_q_not_a) == 2
    assert [all(pred(case) for case in u_a_q_not_a) for pred in [
        lambda case: case['P'] == case['S'] == '乙',
        lambda case: case['R'] == '乙',
        lambda case: case['T'] == '甲',
        lambda case: case['Q'] == '丙',
    ]] == [False, False, True, False]
    assert {case['P'] for case in u_a_q_not_a} == {'乙', '丙'}
    assert {case['R'] for case in u_a_q_not_a} == {'乙', '丙'}
    r_a = [case for case in COMMON_CASES if case['R'] == '甲']
    assert len(r_a) == 2 and all(case['P'] == '乙' for case in r_a)
    assert {case['Q'] for case in r_a} == {'甲', '丙'}
    assert {case['T'] for case in r_a} == {'甲', '丙'}
    assert all(case['U'] != '乙' for case in r_a)
    q_a = [case for case in COMMON_CASES if case['Q'] == '甲']
    assert len(q_a) == 3 and not any(case['U'] == '乙' for case in q_a)
    assert any(case['R'] == '甲' for case in q_a)
    assert any(case['P'] == '丙' for case in q_a)
    assert any(case['T'] == '丙' for case in q_a)
    conditions35 = [('甲', '乙'), ('乙', '甲'), ('丙', '乙'), ('甲', '丙')]
    assert [sum(case['P'] == p and case['Q'] == q for case in COMMON_CASES)
            for p, q in conditions35] == [2, 2, 1, 2]
    assert [(q['n'], q['answer']) for q in LOGIC] == [
        (26, 'B'), (27, 'D'), (28, 'A'), (29, 'C'), (30, 'D'),
        (31, 'A'), (32, 'C'), (33, 'B'), (34, 'C'), (35, 'C'),
    ]
    return True


verify_common()
