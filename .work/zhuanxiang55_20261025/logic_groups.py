"""原创逻辑判断一拖五三组。公共条件与全部子题均保留有限状态验证。"""
from __future__ import annotations

from itertools import combinations, permutations


NAMES = dict(zip("ABCDEFGH", "甲乙丙丁戊己庚辛"))
TOPICS = dict(T="天文", G="地质", O="海洋", P="植物", I="昆虫")


def names(values):
    return "、".join(NAMES[x] for x in values)


def order_option(values):
    return names(values)


def slot_option(am, pm):
    return f"上午：{names(am)}；下午：{names(pm)}"


def question(n, stem, options, answer, point, analysis, level="较难"):
    return dict(n=n, category="逻辑判断一拖五", stem=stem, ask="", options=options,
                answer=answer, point=point, analysis=analysis,
                image=None, explanation_image=None, level=level)


GROUPS = {
    31: [
        "根据以下材料，回答第31—35题。各题新增条件彼此独立。",
        "某文化馆依次安排甲、乙、丙、丁、戊、己、庚七场专题活动，时段编号为1—7，每个时段安排一场，每场只安排一次。安排须满足：",
        "（1）甲紧接着安排在丁之前，即甲、丁占相邻的两个时段。",
        "（2）乙安排在戊之前。",
        "（3）丙与己之间恰好隔一场活动。",
        "（4）庚既不安排在第1时段，也不安排在第7时段。",
        "（5）若戊安排在丙之前，则庚安排在乙之前。",
    ],
    36: [
        "根据以下材料，回答第36—40题。各题新增条件彼此独立。",
        "某交流会从甲、乙、丙、丁、戊、己、庚、辛八个项目中恰好选出四项，安排上午、下午各展示两项；每个入选项目只安排一场，未入选项目不作安排。同一场内不区分先后。安排须满足：",
        "（1）甲、乙恰好有一项入选。",
        "（2）若丙入选，则丁也入选，且丙、丁分属上午和下午。",
        "（3）戊、己至少有一项入选。",
        "（4）若甲入选，则庚也入选，且甲、庚安排在同一场。",
        "（5）丁、辛不能同时入选。",
        "（6）己、乙不能同时入选。",
        "（7）若戊入选，安排在上午；若辛入选，安排在下午。",
    ],
    41: [
        "根据以下材料，回答第41—45题。各题新增条件彼此独立。",
        "某科普展设有从左至右编号1—5的五个展台，甲、乙、丙、丁、戊五名讲解员各负责一个展台；天文、地质、海洋、植物、昆虫五个主题也各占一个展台，每人只负责一个主题。已知：",
        "（1）甲所在展台在乙所在展台左侧，不要求相邻。",
        "（2）丙负责海洋主题，乙负责昆虫主题。",
        "（3）天文主题位于第1台或第5台。",
        "（4）地质主题台紧挨丁所在展台的右侧。",
        "（5）戊所在展台与植物主题台相邻。",
    ],
}


QUESTIONS = [
    question(31,
        "下列哪一项可能是第1—7时段的完整安排？",
        [order_option(x) for x in ("CBFGDAE", "CEFGADB", "CBFGADE", "CBGFADE")],
        "C", "排序：连块、间隔与条件句逐项核对", [
            "C项中甲、丁占第5、6时段；乙在第2时段，早于第7时段的戊；丙、己占第1、3时段，中间恰隔一场；庚在第4时段。戊并未早于丙，条件（5）不再增加限制，全部条件满足。",
            "A项把丁放在甲之前，违反条件（1）；B项乙在第7时段、戊在第2时段，违反条件（2）；D项丙、己相距三个时段，中间隔了两场，违反条件（3）。故正确答案为C。",
        ], level="中等"),
    question(32,
        "若戊安排在第4时段，则以下哪项一定成立？",
        ["甲安排在第6时段", "乙安排在第1时段", "庚安排在第5时段", "丙安排在第3时段"],
        "A", "排序：固定位置与连块、间隔联合推理", [
            "把甲丁视为连续两格的连块，再核对丙己相隔一场、乙早于戊及条件（5），符合戊在第4时段的完整安排只有三种：乙庚丙戊己甲丁；丙乙己戊庚甲丁；己乙丙戊庚甲丁。三种中甲都在第6时段，A项必真。",
            "第二种安排中乙在第2时段，否定B项；第一种安排中庚在第2时段，否定C项；第二种安排中丙在第1时段，否定D项。不能把某一种可行安排中的事实当成所有安排的共同事实。故正确答案为A。",
        ]),
    question(33,
        "若丙安排在第5时段，则以下哪项不可能成立？",
        ["甲安排在第3时段", "乙安排在第6时段", "庚安排在第3时段", "戊安排在第4时段"],
        "D", "排序选非：间隔两侧分支与反例构造", [
            "丙在第5时段时，己只能在第3或第7时段。将这两个分支分别与甲丁连排、乙早于戊、庚非首尾及条件（5）核对：己在第3时段时，戊只能在第7时段；己在第7时段时，戊只能在第6时段。因此戊不可能在第4时段。",
            "乙庚甲丁丙戊己使A项成立；甲丁己庚丙乙戊使B项成立；甲丁庚乙丙戊己使C项成立。三项都有满足全部条件的见证，只有D项不可能。本题选不可能项，故正确答案为D。",
        ]),
    question(34,
        "在公共条件之外，增加以下哪组信息，可以唯一确定七场活动的安排？",
        ["甲在第1时段，戊在第6时段", "甲在第2时段，戊在第6时段", "甲在第2时段，戊在第7时段", "甲在第6时段，戊在第4时段"],
        "B", "排序：新增条件下的唯一解", [
            "B项确定甲在第2、丁在第3、戊在第6时段。丙己相隔一场，只能占第5、7时段；剩余第1、4时段由乙、庚占据，而庚不能在第1时段，所以乙在第1、庚在第4时段。若丙在第7时段，戊就早于丙，条件（5）要求庚早于乙，与第4晚于第1矛盾。因此丙第5、己第7，唯一安排为乙甲丁庚丙戊己。",
            "A项仍有甲丁乙庚丙戊己、甲丁庚乙丙戊己等三种；C项仍有乙甲丁丙庚己戊、乙甲丁己庚丙戊两种；D项仍有乙庚丙戊己甲丁、丙乙己戊庚甲丁等三种，均不足以唯一确定。故正确答案为B。",
        ]),
    question(35,
        "其他公共条件不变，下列哪条可以替换条件（5），且不改变合法安排的范围？",
        ["若庚安排在乙之前，则戊安排在丙之前", "若乙安排在庚之前，则戊安排在丙之前", "若乙安排在庚之前，则丙安排在戊之前", "戊安排在丙之前，当且仅当庚安排在乙之前"],
        "C", "条件句：逆否等价与排列中的严格先后", [
            "条件（5）是“戊早于丙→庚早于乙”。它的逆否命题是“庚不早于乙→戊不早于丙”。七场活动各占不同的时段，不存在同时发生，因此可改写为“乙早于庚→丙早于戊”，正是C项。",
            "A项把原命题的箭头倒转；B项在否定结论后仍保留原前提，方向错误；D项除原条件外又加上其逆命题，限制更强。例如甲丁乙丙庚己戊满足全部原条件，乙早于庚、丙早于戊；它会被B项错误排除。甲丁庚丙乙己戊满足原条件，却不满足A、D项。故正确答案为C。",
        ], level="中等"),
    question(36,
        "下列哪一项可能是完整的展示安排？",
        [slot_option("CE", "BG"), slot_option("EG", "BD"), slot_option("BD", "CE"), slot_option("BE", "FG")],
        "B", "选择与分场：入选约束和场次约束同时检验", [
            "B项入选乙、丁、戊、庚：甲乙只选乙，戊己至少选戊；没有选丙、甲、辛、己，所以相应的条件句或互斥条件都不产生冲突；戊排在上午，每场恰好两项，完全可行。",
            "A项选了丙却没选丁，违反条件（2）；C项把已入选的戊安排在下午，违反条件（7）；D项同时选了己、乙，违反条件（6）。故正确答案为B。",
        ], level="中等"),
    question(37,
        "若丙入选，则以下哪项一定成立？",
        ["丁安排在上午", "戊安排在下午", "庚也入选", "乙安排在下午"],
        "D", "选择与分场：配额约束触发条件链", [
            "丙入选必带丁。若再选甲，就必须选庚，四个名额被甲庚丙丁占满，无法满足戊己至少选一项。因此不选甲而选乙；己不能与乙同选，于是必须选戊。入选名单只能是乙丙丁戊。",
            "戊在上午，丙丁分属两场，所以另一上午名额给丙或丁，乙只能在下午。两种安排为上午丙戊、下午乙丁，或上午丁戊、下午乙丙。前一种否定A项；戊都在上午，B项错误；名单中没有庚，C项错误。故正确答案为D。",
        ]),
    question(38,
        "若己安排在上午，则以下哪项一定成立？",
        ["丁入选", "戊入选", "庚安排在下午", "辛入选"],
        "C", "选择与分场：互斥、捆绑与容量联动", [
            "己入选排除乙，因甲乙恰选一项，甲必须入选并带庚。甲庚需同场，上午已有己，不能再放两项，因此甲庚只能一起排下午，C项一定成立。",
            "剩余上午名额可以给丁，也可以给戊，分别得到上午丁己、下午甲庚，或上午戊己、下午甲庚。前一安排否定B项，后一安排否定A项。下午两名额已经占满，辛若入选必须排下午而无处可放，D项错误。故正确答案为C。",
        ]),
    question(39,
        "若丁未入选而戊已入选，则以下哪项可能成立？",
        ["甲安排在下午，戊安排在上午", "己安排在下午，辛未入选", "乙安排在下午，戊未入选", "庚未入选，辛安排在下午"],
        "A", "选择与分场：分类讨论后检验可能性", [
            "丁未入选使丙也不能入选。已选戊且戊在上午：若选甲，就必须选庚，两者同场只能占下午，第四项为己；若选乙，则不能选己，另两项只能是庚、辛，辛在下午。全部安排为上午戊己／下午甲庚，上午乙戊／下午庚辛，上午戊庚／下午乙辛。",
            "第一种安排使A项成立。三种中己要么在上午要么未入选，B项不可能；C项违背本题戊已入选的前提；三种都选庚，D项也不可能。故正确答案为A。",
        ]),
    question(40,
        "增加以下哪组信息，可以唯一确定入选项目以及上午、下午的安排？",
        ["甲未入选，戊与庚安排在同一场", "庚安排在下午，丁未入选", "乙安排在下午，辛未入选", "丁安排在上午，戊未入选"],
        "D", "选择与分场：唯一安排与余解排除", [
            "D项不选戊，条件（3）要求选己；己排除乙，故选甲并带庚。四项只能是甲丁己庚，甲庚同场，而丁已在上午，所以甲庚在下午、丁己在上午，唯一确定。",
            "A项至少有上午戊庚／下午乙丁和上午戊庚／下午乙辛两种；B项有上午戊己／下午甲庚和上午乙戊／下午庚辛两种；C项有上午丙戊／下午乙丁、上午丁戊／下午乙丙等四种。三项均还有余解。故正确答案为D。",
        ]),
    question(41,
        "根据公共条件，以下哪项一定成立？",
        ["天文主题位于第1台", "地质主题位于第3台", "昆虫主题位于第4台", "植物主题位于第2台"],
        "A", "双属性匹配：端点假设与身份排除", [
            "假设天文在第5台：甲需在乙左侧，甲不能占第5台；乙和丙各负责昆虫、海洋，也不能占天文台；丁的右侧还要有地质台，丁同样不能占第5台。故第5台只能由戊负责。戊与植物台相邻，于是植物在第4台。",
            "丁不能负责海洋或昆虫，也不能负责紧挨自己右侧的地质，故丁只能负责天文或植物。天文第5台已由戊占据，丁只能在第4台负责植物，但这样地质又须在第5台，与天文冲突。假设不成立，所以天文一定在第1台。",
            "甲乙丙丁戊／天文昆虫海洋植物地质是一种合法安排，地质在第5台、昆虫在第2台，分别否定B、C项；甲丙丁戊乙／天文海洋植物地质昆虫也合法，植物在第3台，否定D项。故正确答案为A。",
        ]),
    question(42,
        "若丙在第2台，则以下哪项一定成立？",
        ["乙在第3台", "戊负责地质主题", "丁在第4台", "植物主题位于第3台"],
        "B", "双属性匹配：位置固定后的两种分支", [
            "丙在第2台负责海洋，天文仍须在第1台。结合甲在乙左侧、地质紧挨丁右侧和戊与植物相邻，只剩两种完整安排：讲解员甲丙乙丁戊、主题天文海洋昆虫植物地质；或讲解员甲丙丁戊乙、主题天文海洋植物地质昆虫。两种都由戊负责地质。",
            "第二种安排中乙在第5、丁在第3台，否定A、C项；第一种安排中植物在第4台，否定D项。因此只有B项在所有安排中成立。故正确答案为B。",
        ]),
    question(43,
        "若甲负责地质主题，则以下哪项一定成立？",
        ["丙在第4台", "乙在第5台", "丁在第2台", "植物主题位于第3台"],
        "C", "双属性匹配：身份与相邻关系交叉", [
            "甲负责地质，丁必须紧挨甲左侧。乙、丙分别占昆虫、海洋，戊与植物相邻；又因天文在第1台，可行安排只有：讲解员戊丁甲乙丙、主题天文植物地质昆虫海洋；或讲解员戊丁甲丙乙、主题天文植物地质海洋昆虫。两种都把丁放在第2台。",
            "第一种安排中丙在第5、乙在第4台，分别否定A、B项；两种植物都在第2台，D项错误。故正确答案为C。",
        ]),
    question(44,
        "若昆虫主题台紧挨植物主题台的右侧，则海洋主题台左侧紧邻的讲解员是谁？",
        ["甲", "丁", "戊", "乙"],
        "D", "双属性匹配：相邻主题连块与排除分支", [
            "天文在第1台，因此“植物—昆虫”连块只能占第2、3台，第3、4台，或第4、5台。昆虫由乙负责，戊又必须与植物台相邻；将三种位置分别与丁的右邻为地质、甲在乙左侧核对，只有植物第3、昆虫第4可行。",
            "具体安排唯一为：讲解员丁戊甲乙丙；主题天文地质植物昆虫海洋。海洋在第5台，左邻是第4台的乙，其余三人分别在第3、1、2台。故正确答案为D。",
        ]),
    question(45,
        "增加以下哪组信息，可以唯一确定五台的讲解员与主题？",
        ["甲负责地质，乙在第4台", "海洋在第4台，戊负责地质", "乙在第5台，植物在第2台", "丁负责植物，甲负责天文"],
        "A", "双属性匹配：新增信息的充分性与唯一解", [
            "甲负责地质时，丁紧挨甲左侧；再结合天文的端点位置、戊与植物相邻，只有讲解员戊丁甲乙丙与戊丁甲丙乙两种安排。新增乙在第4台排除后一种，唯一结果为讲解员戊丁甲乙丙，主题天文植物地质昆虫海洋，A项足够。这里从公共条件重新推导，不沿用其他子题的附加条件。",
            "B项仍有讲解员甲丁戊丙乙／主题天文植物地质海洋昆虫，以及丁戊甲丙乙／天文地质植物海洋昆虫两种；C项仍有甲丁戊丙乙／天文植物地质海洋昆虫，以及戊丁甲丙乙／天文植物地质海洋昆虫两种；D项仍有六种，例如甲乙丙丁戊／天文昆虫海洋植物地质与甲丙乙丁戊／天文海洋昆虫植物地质。故正确答案为A。",
        ]),
]


def valid_order(seq, include_fifth=True):
    if len(seq) != 7 or set(seq) != set("ABCDEFG"):
        return False
    p = {x: seq.index(x) + 1 for x in seq}
    base = (p["D"] == p["A"] + 1 and p["B"] < p["E"]
            and abs(p["C"] - p["F"]) == 2 and p["G"] not in (1, 7))
    return base and (not include_fifth or p["E"] > p["C"] or p["G"] < p["B"])


ORDER_BASE = [{x: s.index(x) + 1 for x in s} for s in permutations("ABCDEFG") if valid_order(s, False)]
ORDER_CASES = [p for p in ORDER_BASE if p["E"] > p["C"] or p["G"] < p["B"]]


def valid_slots(am, pm):
    am, pm = frozenset(am), frozenset(pm)
    if len(am) != 2 or len(pm) != 2 or am & pm or not am | pm <= set("ABCDEFGH"):
        return False
    selected = am | pm
    return (int("A" in selected) + int("B" in selected) == 1
            and ("C" not in selected or ("D" in selected and (("C" in am) != ("D" in am))))
            and bool(selected & set("EF"))
            and ("A" not in selected or ("G" in selected and (("A" in am) == ("G" in am))))
            and not set("DH") <= selected and not set("FB") <= selected
            and ("E" not in selected or "E" in am)
            and ("H" not in selected or "H" in pm))


SLOT_CASES = []
for selected in combinations("ABCDEFGH", 4):
    for am in combinations(selected, 2):
        pm = set(selected) - set(am)
        if valid_slots(am, pm):
            SLOT_CASES.append((frozenset(am), frozenset(pm)))


def valid_match(people, topics):
    p = {x: people.index(x) + 1 for x in people}
    t = {x: topics.index(x) + 1 for x in topics}
    return (p["A"] < p["B"] and p["C"] == t["O"] and p["B"] == t["I"]
            and t["T"] in (1, 5) and t["G"] == p["D"] + 1
            and abs(p["E"] - t["P"]) == 1)


MATCH_CASES = []
for people in permutations("ABCDE"):
    for topics in permutations("TGOPI"):
        if valid_match(people, topics):
            MATCH_CASES.append({
                "p": {x: people.index(x) + 1 for x in people},
                "t": {x: topics.index(x) + 1 for x in topics},
                "people": people, "topics": topics,
            })


def _check(result, expected, qn):
    assert result == expected, (qn, result, expected)


def _truth_counts(cases, predicates):
    assert cases, "子题条件解集不得为空"
    return [sum(bool(fn(case)) for case in cases) for fn in predicates]


def verify():
    """每题从公共模型重新选子集，不把其他子题条件累加。"""
    assert len(ORDER_CASES) == 35
    assert len(SLOT_CASES) == 12
    assert len(MATCH_CASES) == 10
    report = {"passed": True, "public_case_counts": {"31—35": 35, "36—40": 12, "41—45": 10}, "questions": {}}

    # 31：四个完整候选依公共条件检验。
    values = [valid_order(s) for s in ("CBFGDAE", "CEFGADB", "CBFGADE", "CBGFADE")]
    _check(values, [False, False, True, False], 31)
    report["questions"][31] = {"type": "possible", "option_results": values}

    sub = [p for p in ORDER_CASES if p["E"] == 4]
    counts = _truth_counts(sub, [lambda p: p["A"] == 6, lambda p: p["B"] == 1, lambda p: p["G"] == 5, lambda p: p["C"] == 3])
    _check([x == len(sub) for x in counts], [True, False, False, False], 32)
    report["questions"][32] = {"cases": len(sub), "option_true_counts": counts, "type": "must"}

    sub = [p for p in ORDER_CASES if p["C"] == 5]
    counts = _truth_counts(sub, [lambda p: p["A"] == 3, lambda p: p["B"] == 6, lambda p: p["G"] == 3, lambda p: p["E"] == 4])
    _check([x == 0 for x in counts], [False, False, False, True], 33)
    report["questions"][33] = {"cases": len(sub), "option_true_counts": counts, "type": "impossible"}

    constraints34 = [(1, 6), (2, 6), (2, 7), (6, 4)]
    counts = [sum(p["A"] == a and p["E"] == e for p in ORDER_CASES) for a, e in constraints34]
    _check(counts, [3, 1, 2, 3], 34)
    report["questions"][34] = {"option_solution_counts": counts, "type": "unique"}

    original = {tuple(sorted(p.items())) for p in ORDER_CASES}
    predicates35 = [
        lambda p: p["G"] > p["B"] or p["E"] < p["C"],
        lambda p: p["B"] > p["G"] or p["E"] < p["C"],
        lambda p: p["B"] > p["G"] or p["C"] < p["E"],
        lambda p: (p["E"] < p["C"]) == (p["G"] < p["B"]),
    ]
    replacements = [{tuple(sorted(p.items())) for p in ORDER_BASE if fn(p)} for fn in predicates35]
    _check([x == original for x in replacements], [False, False, True, False], 35)
    assert valid_order("ADBCGFE") and valid_order("ADGCBFE")
    report["questions"][35] = {"replacement_case_counts": [len(x) for x in replacements], "equivalent": [x == original for x in replacements], "type": "equivalence"}

    candidates36 = [("CE", "BG"), ("EG", "BD"), ("BD", "CE"), ("BE", "FG")]
    values = [valid_slots(a, p) for a, p in candidates36]
    _check(values, [False, True, False, False], 36)
    report["questions"][36] = {"type": "possible", "option_results": values}

    sub = [c for c in SLOT_CASES if "C" in c[0] | c[1]]
    counts = _truth_counts(sub, [lambda c: "D" in c[0], lambda c: "E" in c[1], lambda c: "G" in c[0] | c[1], lambda c: "B" in c[1]])
    _check([x == len(sub) for x in counts], [False, False, False, True], 37)
    report["questions"][37] = {"cases": len(sub), "option_true_counts": counts, "type": "must"}

    sub = [c for c in SLOT_CASES if "F" in c[0]]
    counts = _truth_counts(sub, [lambda c: "D" in c[0] | c[1], lambda c: "E" in c[0] | c[1], lambda c: "G" in c[1], lambda c: "H" in c[0] | c[1]])
    _check([x == len(sub) for x in counts], [False, False, True, False], 38)
    report["questions"][38] = {"cases": len(sub), "option_true_counts": counts, "type": "must"}

    sub = [c for c in SLOT_CASES if "D" not in c[0] | c[1] and "E" in c[0] | c[1]]
    counts = _truth_counts(sub, [lambda c: "A" in c[1] and "E" in c[0], lambda c: "F" in c[1] and "H" not in c[0] | c[1], lambda c: "B" in c[1] and "E" not in c[0] | c[1], lambda c: "G" not in c[0] | c[1] and "H" in c[1]])
    _check([x > 0 for x in counts], [True, False, False, False], 39)
    report["questions"][39] = {"cases": len(sub), "option_true_counts": counts, "type": "possible"}

    constraints40 = [lambda c: "A" not in c[0] | c[1] and "E" in c[0] and "G" in c[0], lambda c: "G" in c[1] and "D" not in c[0] | c[1], lambda c: "B" in c[1] and "H" not in c[0] | c[1], lambda c: "D" in c[0] and "E" not in c[0] | c[1]]
    counts = [sum(fn(c) for c in SLOT_CASES) for fn in constraints40]
    _check(counts, [2, 2, 4, 1], 40)
    report["questions"][40] = {"option_solution_counts": counts, "type": "unique"}

    counts = _truth_counts(MATCH_CASES, [lambda c: c["t"]["T"] == 1, lambda c: c["t"]["G"] == 3, lambda c: c["t"]["I"] == 4, lambda c: c["t"]["P"] == 2])
    _check([x == len(MATCH_CASES) for x in counts], [True, False, False, False], 41)
    report["questions"][41] = {"cases": len(MATCH_CASES), "option_true_counts": counts, "type": "must"}

    sub = [c for c in MATCH_CASES if c["p"]["C"] == 2]
    counts = _truth_counts(sub, [lambda c: c["p"]["B"] == 3, lambda c: c["p"]["E"] == c["t"]["G"], lambda c: c["p"]["D"] == 4, lambda c: c["t"]["P"] == 3])
    _check([x == len(sub) for x in counts], [False, True, False, False], 42)
    report["questions"][42] = {"cases": len(sub), "option_true_counts": counts, "type": "must"}

    sub = [c for c in MATCH_CASES if c["p"]["A"] == c["t"]["G"]]
    counts = _truth_counts(sub, [lambda c: c["p"]["C"] == 4, lambda c: c["p"]["B"] == 5, lambda c: c["p"]["D"] == 2, lambda c: c["t"]["P"] == 3])
    _check([x == len(sub) for x in counts], [False, False, True, False], 43)
    report["questions"][43] = {"cases": len(sub), "option_true_counts": counts, "type": "must"}

    sub = [c for c in MATCH_CASES if c["t"]["I"] == c["t"]["P"] + 1]
    counts = _truth_counts(sub, [lambda c: c["p"]["A"] == c["t"]["O"] - 1, lambda c: c["p"]["D"] == c["t"]["O"] - 1, lambda c: c["p"]["E"] == c["t"]["O"] - 1, lambda c: c["p"]["B"] == c["t"]["O"] - 1])
    _check([x == len(sub) for x in counts], [False, False, False, True], 44)
    report["questions"][44] = {"cases": len(sub), "option_true_counts": counts, "type": "must"}

    constraints45 = [lambda c: c["p"]["A"] == c["t"]["G"] and c["p"]["B"] == 4, lambda c: c["t"]["O"] == 4 and c["p"]["E"] == c["t"]["G"], lambda c: c["p"]["B"] == 5 and c["t"]["P"] == 2, lambda c: c["p"]["D"] == c["t"]["P"] and c["p"]["A"] == c["t"]["T"]]
    counts = [sum(fn(c) for c in MATCH_CASES) for fn in constraints45]
    _check(counts, [1, 2, 2, 6], 45)
    report["questions"][45] = {"option_solution_counts": counts, "type": "unique"}

    answers = "CADBCBDCADABCDA"
    assert [q["n"] for q in QUESTIONS] == list(range(31, 46))
    assert "".join(q["answer"] for q in QUESTIONS) == answers
    assert all(len(q["options"]) == 4 and q["analysis"][-1].endswith(f"故正确答案为{q['answer']}。") for q in QUESTIONS)
    return report


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
