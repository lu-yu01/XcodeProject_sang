"""Single binding source for the requested 30 + 15 + 10 workbook."""
from graphics_a import QUESTIONS as A
from graphics_b import QUESTIONS as B
from logic_groups import QUESTIONS as GROUP_QUESTIONS, GROUPS
from argument import QUESTIONS as ARGUMENTS

TITLE='国考图形与逻辑专项练习'
SUBTITLE='55题 图形推理30题 一拖五15题 加强削弱10题'
INTRO='本练习共55道单项选择题，每题只有一个最合适的答案。第31至45题分为三组，每组五题共用材料，各子题新增条件彼此独立。参考答案与逐题解析集中附在题目之后。'
QUESTIONS=sorted(A+B+GROUP_QUESTIONS+ARGUMENTS,key=lambda q:q['n'])
assert [q['n'] for q in QUESTIONS]==list(range(1,56))
assert set(GROUPS)=={31,36,41}

def draw_all():
    import graphics_a,graphics_b
    graphics_a.draw_all();graphics_b.draw_all()
