"""Original formal reasoning Q51-Q80; all finite cases are exhaustively checked."""
from pathlib import Path
from itertools import product, permutations, combinations
from collections import Counter
import json, hashlib
from explore_formal import g1,g2,g3,DUR

ROOT=Path(__file__).resolve().parent
LETTERS='ABCD'
QUESTIONS=[]
REG={}
GROUPS={
51:[
'某水文监测网有甲、乙、丙、丁、戊、己、庚、辛八个监测站。本轮试运行恰好启用其中四站，其余站不启用。配置须同时满足：',
'（1）甲、乙至少启用一站。',
'（2）如果启用甲，则启用丙；如果启用乙，则不启用丁。',
'（3）己启用，当且仅当甲、戊中恰好有一站启用。换言之，甲、戊同为启用或同为不启用时，己不启用；两者恰好一站启用时，己启用。',
'（4）只有启用乙，才可以启用庚。',
'第51—55题各自增加的条件仅对本题有效，不带入其他题。'],
56:[
'某档案中心由林、周、许、陈、赵五人复核甲、乙、丙、丁四份文件。每份文件恰由两名不同人员共同复核，同一人可以复核多份文件；每人至少复核一份、至多复核两份。分工须同时满足：',
'（1）林、周不共同复核任何一份文件。',
'（2）甲文件的两名复核者中，林、许恰好有一人；赵不复核甲文件。',
'（3）陈复核乙文件，当且仅当周复核丁文件。',
'（4）许、赵至少共同复核一份文件。',
'每份文件内两名复核者不区分先后。第56—60题各自增加的条件仅对本题有效，不带入其他题。'],
61:[
'某检测台要在第1—6时段内完成清洗、标定、扫描、复核、封装五项任务。每个时段长度相同，各任务均从某一时段开始并连续进行，中途不得暂停。清洗和扫描各占连续两个时段，标定、复核、封装各占一个时段。须同时满足：',
'（1）清洗、扫描、封装共用同一台设备，任意两项不能占用同一时段。',
'（2）标定和复核由同一名操作员完成，两项不能占用同一时段；它们可以与不受其他条件限制的设备任务并行。',
'（3）清洗完成后才能开始标定，标定完成后才能开始封装；扫描完成后才能开始复核。',
'一项任务在某时段结束后，后续任务最早可在紧接的下一时段开始。例如清洗从第1时段开始，则占用第1、2时段，标定最早从第3时段开始。第61—65题各自增加的条件仅对本题有效，不带入其他题。']}
GROUP_MODELS={51:g1(),56:g2(),61:g3()}
PEOPLE='林周许陈赵'
STATIONS='甲乙丙丁戊己庚辛'
def fmt1(m):return '启用'+ '、'.join(STATIONS[i] for i,x in enumerate(m) if x)+'，其余不启用'
def fmt2(m):return '；'.join('甲乙丙丁'[i]+'由'+ '、'.join(PEOPLE[j] for j in row)+'复核' for i,row in enumerate(m))
def fmt3(m):return '清洗、标定、扫描、复核、封装分别从第'+ '、'.join(map(str,m))+'时段开始'
def js(v):
 if isinstance(v,dict):return {str(k):js(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [js(x) for x in v]
 if isinstance(v,(set,frozenset)):return sorted(js(x) for x in v)
 return v
def eval_record(models,preds,mode,formatter):
 assert models,'附加条件不得导致无解'
 records=[];valid=[]
 for pred in preds:
  yes=[m for m in models if pred(m)];no=[m for m in models if not pred(m)]
  good={'must':len(yes)==len(models),'may':len(yes)>0,'cannot':len(yes)==0,
        'not_must':len(yes)<len(models),'unique':len(yes)==1}[mode]
  valid.append(good)
  records.append(dict(true_count=len(yes),false_count=len(no),satisfying_witness=js(yes[0]) if yes else None,
   counterexample=js(no[0]) if no else None,satisfying_witness_text=formatter(yes[0]) if yes else None,
   counterexample_text=formatter(no[0]) if no else None,
   second_satisfying_witness=js(yes[1]) if len(yes)>1 else None,
   second_satisfying_witness_text=formatter(yes[1]) if len(yes)>1 else None))
 assert sum(valid)==1,(mode,valid,[(x['true_count'],x['false_count']) for x in records])
 return records,valid
def add(n,stem,options,models,preds,mode,point,reason,refs,formatter=str,group=None,condition='无新增条件',difficulty='中难',ask=''):
 records,valid=eval_record(models,preds,mode,formatter)
 ans=LETTERS[valid.index(True)]
 evidence=[]
 for i,r in enumerate(records):
  letter=LETTERS[i]
  if mode in ('must','not_must'):
   s=f'{letter}项在全部可行情况中均成立。' if r['false_count']==0 else f'{letter}项不是必然的。例如，{r["counterexample_text"]}，该项不成立。'
  elif mode in ('may','cannot'):
   s=f'{letter}项可以成立，例如：{r["satisfying_witness_text"]}。' if r['true_count'] else f'{letter}项与全部条件不能同时成立。'
  else:
   s=f'{letter}项新增信息后有{r["true_count"]}种完整安排。'
   if r['true_count']:s+='例如：'+r['satisfying_witness_text']+'。'
   if r['true_count']>1:s+='另有：'+r['second_satisfying_witness_text']+'。'
  evidence.append(s)
 analysis=list(reason)+evidence+[f'本题应选{ans}项。']
 model=dict(evaluation_mode=mode,conditions=condition,model_count=len(models),option_checks=records,option_validity=valid)
 if group:model['group']=group;model['base_model_count']=len(GROUP_MODELS[group])
 else:model['all_models']=js(models)
 q=dict(n=n,category='逻辑推理',stem=stem,ask=ask,options=options,answer=ans,point=point,analysis=analysis,
        difficulty=difficulty,mechanism=point,source_refs=refs,model=model)
 QUESTIONS.append(q);REG[n]=dict(kind='ordinary',models=models,preds=preds,mode=mode,formatter=formatter)
 return q
def aggregate(n,stem,options,models,values,result_fn,point,reason,refs,formatter=str,group=None,condition='无新增条件',difficulty='中难'):
 result=result_fn(models);valid=[v==result for v in values];assert sum(valid)==1
 ans=LETTERS[valid.index(True)]
 model=dict(evaluation_mode='aggregate',model_count=len(models),option_values=values,computed_value=result,option_validity=valid)
 if group:model.update(group=group,base_model_count=len(GROUP_MODELS[group]),conditions=condition)
 else:model['all_models']=js(models)
 QUESTIONS.append(dict(n=n,category='逻辑推理',stem=stem,ask='',options=options,answer=ans,point=point,
  analysis=list(reason)+[f'四项中只有{ans}项与计算结果一致。'],difficulty=difficulty,mechanism=point,source_refs=refs,model=model))
 REG[n]=dict(kind='aggregate',models=models,values=values,result_fn=result_fn)

# Group 1: Boolean dependency, exclusive status and exact cardinality, not a timetable.
M=GROUP_MODELS[51]
add(51,'下列哪四站可以构成本轮启用站点的完整名单？',
 ['甲、乙、丙、丁','乙、戊、己、庚','甲、丙、戊、己','甲、丙、丁、辛'],M,
 [lambda m:m==(1,1,1,1,0,0,0,0),lambda m:m==(0,1,0,0,1,1,1,0),lambda m:m==(1,0,1,0,1,1,0,0),lambda m:m==(1,0,1,1,0,0,0,1)],
 'may','配置可行性：同时核对双向条件与启用总数',
 ['A项同时启用乙、丁；C项中甲、戊均启用，却仍启用己；D项中甲启用、戊不启用，却未启用己。B项满足全部条件。'],['N26-106','JS24B-96'],fmt1,51)
add(52,'关于本轮配置，以下哪项一定成立？',
 ['甲、戊至少启用一站','丙、己至少启用一站','丁、辛至少启用一站','戊、庚至少启用一站'],M,
 [lambda m:m[0] or m[4],lambda m:m[2] or m[5],lambda m:m[3] or m[7],lambda m:m[4] or m[6]],
 'must','由总量约束补足必要析取',
 ['假设丙、己都不启用，则甲不启用。由甲、戊与己的等价条件，戊也不启用。甲不启用要求乙启用，继而丁不启用，只剩乙、庚、辛可启用，最多三站，与恰好四站矛盾。'],['JS24B-96','N26-103'],fmt1,51)
Ms=[m for m in M if not m[2]]
add(53,'如果丙不启用，以下哪项是可能的？',
 ['甲启用，己不启用','丁、辛均启用','庚、辛均启用','庚启用，辛不启用'],Ms,
 [lambda m:m[0] and not m[5],lambda m:m[3] and m[7],lambda m:m[6] and m[7],lambda m:m[6] and not m[7]],
 'may','新增否定条件后的补位分支',
 ['丙不启用使甲不能启用，因此乙必须启用、丁不能启用。若戊不启用，则己也不启用，剩余站数不足四；故戊、己均启用，最后一席由庚、辛二选一。'],['N26-110'],fmt1,51,'丙不启用')
Ms=[m for m in M if not m[5]]
add(54,'如果己不启用，以下哪项不可能成立？',
 ['乙、辛启用，戊不启用','丁启用，辛不启用','甲、乙均启用','庚、戊均启用'],Ms,
 [lambda m:m[1] and m[7] and not m[4],lambda m:m[3] and not m[7],lambda m:m[0] and m[1],lambda m:m[6] and m[4]],
 'cannot','等价条件取反后的容量排除',
 ['己不启用意味着甲、戊同状态。若庚、戊均启用，则乙、甲也均启用，甲又要求丙启用，至少五站启用，超出四站名额。其余三项各有完整构造。'],['N23-108','JS24B-96'],fmt1,51,'己不启用')
add(55,'在公共条件之外，增加以下哪组信息，可以唯一确定全部八站的启用状态？',
 ['甲、戊均不启用','甲启用，辛不启用','乙启用，庚不启用','丙、己均启用'],M,
 [lambda m:not m[0] and not m[4],lambda m:m[0] and not m[7],lambda m:m[1] and not m[6],lambda m:m[2] and m[5]],
 'unique','区分唯一确定与仅缩小范围',
 ['甲、戊均不启用时，己也不启用；乙必须启用，从而丁不启用。余下能启用的恰为乙、丙、庚、辛，四站全部确定。其余信息均留下多个配置。'],['N25-108','N26-110'],fmt1,51)

# Group 2: labelled-edge incidence, repeated people and row capacities.
M=GROUP_MODELS[56]
choices56=[((0,3),(0,2),(1,3),(1,4)),((1,2),(0,3),(2,4),(0,3)),
           ((2,3),(0,4),(1,3),(2,4)),((1,2),(0,4),(0,1),(2,3))]
add(56,'下列哪项可以是四份文件的完整复核分工？',
 ['甲：林、陈；乙：林、许；丙：周、陈；丁：周、赵',
  '甲：周、许；乙：林、陈；丙：许、赵；丁：林、陈',
  '甲：许、陈；乙：林、赵；丙：周、陈；丁：许、赵',
  '甲：周、许；乙：林、赵；丙：林、周；丁：许、陈'],M,
 [lambda m,x=x:m==x for x in choices56],'may','多对多分工的完整可行性',
 ['A项没有任何文件由许、赵共同复核；B项陈复核乙却没有周复核丁，不满足双向条件；D项林、周共同复核丙。C项各人参与次数与所有关系均符合。'],['N26-106'],fmt2,56)
Ms=[m for m in M if m[0]==(2,3)]
add(57,'如果甲由许、陈共同复核，以下哪项一定成立？',
 ['赵只复核一份文件','林只复核一份文件','周复核两份文件','许只复核一份文件'],Ms,
 [lambda m:sum(4 in r for r in m)==1,lambda m:sum(0 in r for r in m)==1,
  lambda m:sum(1 in r for r in m)==2,lambda m:sum(2 in r for r in m)==1],
 'must','参与次数与双向条件的联合分支',
 ['甲已由许、陈占满。若林复核两份，则乙丙丁中两份含林；周至少复核一份且不能与林同组，只能占第三份。这样其余三份都含林或周，连同甲文件，没有任何一份能由许赵共同复核，矛盾。因此林只复核一份。同理周也只复核一份。共八个名额，余下许、陈、赵各复核两份。'],['N26-108','N24-109'],fmt2,56,'甲由许、陈复核')
Ms=[m for m in M if m[1]==(0,2)]
add(58,'如果乙由林、许共同复核，以下哪项是可能的？',
 ['丙由周、赵共同复核','丁由林、赵共同复核','甲由周、许共同复核','陈、赵各只复核一份文件'],Ms,
 [lambda m:m[2]==(1,4),lambda m:m[3]==(0,4),lambda m:m[0]==(1,2),
  lambda m:sum(3 in r for r in m)==1 and sum(4 in r for r in m)==1],
 'may','固定一条复核关系后的两种余解',
 ['乙没有陈，故丁没有周。林在乙已有一次，甲若不含林则甲必须含许；再安排许赵同组会令许超过两份，故甲只能为林陈。林已满两份，丁不能再含林；剩余许赵共同复核丁，丙为周陈或周赵。'],['N26-110'],fmt2,56,'乙由林、许复核')
Ms=[m for m in M if m[0]==(0,3) and sum(3 in r for r in m)==1]
add(59,'如果陈只复核甲文件，以下哪项不可能成立？',
 ['周复核两份文件','林只复核一份文件','许、赵共同复核两份文件','乙、丁两份文件都有许参与复核'],Ms,
 [lambda m:sum(1 in r for r in m)==2,lambda m:sum(0 in r for r in m)==1,
  lambda m:sum(2 in r and 4 in r for r in m)==2,lambda m:2 in m[1] and 2 in m[3]],
 'cannot','重复同组导致剩余名额冲突',
 ['陈只复核甲，甲的另一人只能是林。若许、赵又共同复核两份，二人各已满两份；剩余一份只能由林、周共同复核，违反二人不得同组。故共同复核至多一份。'],['N26-109','N23-108'],fmt2,56,'陈只复核甲文件')
add(60,'在公共条件之外，增加以下哪组信息，可以唯一确定四份文件的完整分工？',
 ['甲由林、陈复核，乙由林、许复核','甲由许、陈复核，丁由许、赵复核',
  '甲由周、许复核，丙由许、赵复核','甲由林、陈复核，乙由许、陈复核'],M,
 [lambda m:m[0]==(0,3) and m[1]==(0,2),lambda m:m[0]==(2,3) and m[3]==(2,4),
  lambda m:m[0]==(1,2) and m[2]==(2,4),lambda m:m[0]==(0,3) and m[1]==(2,3)],
 'unique','双向约束与参与上限共同锁定余项',
 ['D项下陈已复核甲乙两份，不能再复核丙丁；因陈复核乙，周必须复核丁。许已复核乙，尚须与赵共同复核，故许赵只能共同复核丙，丁即由周赵复核。其余信息分别留有余解。'],['N26-107','N24-109'],fmt2,56)

# Group 3: five integer interval starts, two exclusive resources, explicit duration.
M=GROUP_MODELS[61]
choices61=[(1,3,2,5,5),(1,4,3,5,6),(3,4,1,3,6),(1,3,3,3,5)]
add(61,'下列五项任务的开始时段，哪项可能成立？各项依次为清洗、标定、扫描、复核、封装。',
 ['第1、3、2、5、5时段','第1、4、3、5、6时段','第3、4、1、3、6时段','第1、3、3、3、5时段'],M,
 [lambda m,x=x:m==x for x in choices61],'may','区间占用而非单点排序',
 ['A项清洗占第1、2时段，与从第2时段开始的扫描重叠。C项清洗到第4时段才结束，标定不能从第4时段开始。D项扫描尚未完成即开始复核，且标定与复核同时占用操作员。B项没有资源或先后冲突。'],['N25-106','BJ25-79'],fmt3,61)
aggregate(62,'如果尽可能早地完成全部五项任务，最早可以在第几时段结束时全部完成？',
 ['第4时段','第6时段','第5时段','第6时段结束前无法全部完成'],M,[4,6,5,7],
 lambda ms:min(max(m[i]+DUR[i]-1 for i in range(5)) for m in ms),
 '最早完成：资源下界与达到下界的构造',
 ['共用设备的清洗、扫描、封装合计占2＋2＋1＝5个时段，互不重叠，故不可能早于第5时段完成。',
  '清洗占1—2，扫描占3—4，封装占5；标定在3、复核在5，满足两条先后链和操作员限制，恰能在第5时段结束。'],['N22-108','N25-108'],fmt3,61)
Ms=[m for m in M if m[2]==1]
add(63,'如果扫描从第1时段开始，以下哪项一定成立？',
 ['封装从第6时段开始','标定从第4时段开始','复核从第5时段开始','清洗从第1时段开始'],Ms,
 [lambda m:m[4]==6,lambda m:m[1]==4,lambda m:m[3]==5,lambda m:m[0]==1],
 'must','反转设备任务先后后的连锁压缩',
 ['扫描占1—2，清洗最早占3—4；其后标定最早5、封装最早6。所有任务须在6内完成，故清洗只能3—4、标定只能5、封装只能6。复核可在3、4或6，不与标定冲突即可。'],['N25-108'],fmt3,61,'扫描从第1时段开始')
Ms=[m for m in M if m[1]==4]
add(64,'如果标定从第4时段开始，以下哪项不可能成立？',
 ['封装从第5时段开始','复核从第4时段开始','清洗从第2时段开始','扫描从第4时段开始'],Ms,
 [lambda m:m[4]==5,lambda m:m[3]==4,lambda m:m[0]==2,lambda m:m[2]==4],
 'cannot','共享资源排除与可并行任务区分',
 ['标定和复核共用操作员，不能同在第4时段。扫描由设备承担，可以与标定并行；清洗从2开始占2—3，结束后也可在4标定。'],['N25-110'],fmt3,61,'标定从第4时段开始',difficulty='中')
Ms=[m for m in M if m[3]==5]
add(65,'如果复核从第5时段开始，以下哪项不能确定为真？',
 ['清洗从第1时段开始','扫描从第3时段开始','封装不早于第5时段开始','标定从第3时段开始'],Ms,
 [lambda m:m[0]==1,lambda m:m[2]==3,lambda m:m[4]>=5,lambda m:m[1]==3],
 'not_must','区分已锁定的设备顺序与仍可浮动的单时段任务',
 ['复核在5要求扫描最晚在4结束。若扫描先于清洗，则扫描1—2、清洗3—4、标定5，会与复核同占操作员，故不可行。因此清洗1—2、扫描3—4，封装只能5或6。标定可在3或4，不能锁定为3。'],['N23-107','BJ25-79'],fmt3,61,'复核从第5时段开始')

# Four translation questions: disjunctive necessity, witnesses, scope, exclusive alternatives.
def implies(p,q):return not p or bool(q)
def bits_models(k,condition):return [m for m in product([False,True],repeat=k) if condition(m)]
M=bits_models(5,lambda m:implies(m[2],m[0] or m[1]) and implies(m[3],not m[0]) and implies(not m[4],not m[1]) and m[2] and m[3])
def f66(m):return '备用链路'+('可用' if m[0] else '不可用')+'，本地缓存'+('可用' if m[1] else '不可用')+'，'+('已' if m[4] else '未')+'完成预同步'
add(66,'某远程巡检系统规定：只有备用链路可用或本地缓存可用，巡检才可能成功；如果主站断联，则备用链路不可用；如果未完成预同步，则本地缓存不可用。现知某次巡检成功，而且主站断联。由此可以推出：',
 ['备用链路可用','主站未断联','本地缓存不可用','已完成预同步'],M,
 [lambda m:m[0],lambda m:not m[3],lambda m:not m[1],lambda m:m[4]],'must',
 '必要条件中的析取与连续否定后件',
 ['巡检成功要求“备用链路可用或本地缓存可用”。主站断联排除备用链路，只能使用本地缓存。由“未完成预同步→缓存不可用”的逆否，缓存可用要求已完成预同步。'],['N26-103','JS24B-91','BJ25-73'],f66,difficulty='中')

def unary_models(k,size,premise):
 return [m for m in product(range(1<<k),repeat=size) if premise(m)]
def bit(t,i):return bool(t&(1<<i))
def describe_unary(m,names,object_name='对象'):
 return '；'.join(f'{object_name}{i+1}：'+ '、'.join(name[0] if bit(t,j) else name[1] for j,name in enumerate(names)) for i,t in enumerate(m))
def p67(m):
 return (all(implies(bit(t,0),bit(t,1)) and implies(bit(t,2) and bit(t,1),not bit(t,3)) for t in m)
  and any(bit(t,2) and bit(t,0) for t in m) and any(bit(t,1) and not bit(t,2) for t in m))
M=unary_models(4,3,p67)
add(67,'某批档案中，所有经过特别复核的档案均已登记；所有已登记的加密档案均未公开；有些加密档案经过了特别复核；有些已登记档案未加密。如果上述陈述为真，以下哪项一定为真？',
 ['有些未加密档案经过了特别复核','所有已登记档案均未公开','有些经过特别复核的档案未公开','有些已公开档案未登记'],M,
 [lambda m:any(not bit(t,2) and bit(t,0) for t in m),lambda m:all(implies(bit(t,1),not bit(t,3)) for t in m),
  lambda m:any(bit(t,0) and not bit(t,3) for t in m),lambda m:any(bit(t,3) and not bit(t,1) for t in m)],
 'must','存在见证与交集前件：不能合并不同的“有些”',
 ['取一份“加密且经过特别复核”的档案作见证：特别复核使其已登记，“已登记且加密”又使其未公开，因此必有经过特别复核而未公开的档案。另一条“有些已登记但未加密”不能保证这些档案也经过特别复核，不能把两个不同见证合并。'],
 ['BJ25-76','N26-103'],lambda m:describe_unary(m,[('经特别复核','未经特别复核'),('已登记','未登记'),('已加密','未加密'),('已公开','未公开')],'档案'))
QUESTIONS[-1]['model']['small_model_bound']='前提有两个存在见证；否定任一选项至多再需一个见证，故三个对象已覆盖反例所需类型，不把有限抽样当作无限全称证明。'

def bad68(t):return (bit(t,0) and not bit(t,1)) or (bit(t,2) and not bit(t,3))
M=unary_models(4,2,lambda m:any(bad68(t) for t in m))
add(68,'某审核员说：“并非每份申请都同时满足以下两条：若申请加急，则已经复核；若申请涉密，则已经授权。”下列哪项与这句话的逻辑含义完全一致？',
 ['有一份申请既加急且未经复核，又涉密且未经授权',
  '每份申请至少违反上述两条中的一条',
  '存在加急但未经复核的申请，而且存在涉密但未经授权的申请',
  '至少有一份申请，或者加急但未经复核，或者涉密但未经授权'],M,
 [lambda m:any(bit(t,0) and not bit(t,1) and bit(t,2) and not bit(t,3) for t in m),
  lambda m:all(bad68(t) for t in m),
  lambda m:any(bit(t,0) and not bit(t,1) for t in m) and any(bit(t,2) and not bit(t,3) for t in m),
  lambda m:any(bad68(t) for t in m)],'must','全称合取的整体否定与条件句反例',
 ['“并非每份都同时满足两条”等价于“有一份至少违反一条”。“若加急则已复核”为假的条件是加急且未复核；另一条为假的条件是涉密且未授权。至少违反一条用“或”连接，不要求两条都违反，也不要求每份都违反。'],
 ['BJ25-75','JS24B-91'],lambda m:describe_unary(m,[('加急','不加急'),('已复核','未复核'),('涉密','不涉密'),('已授权','未授权')],'申请'),difficulty='难')
QUESTIONS[-1]['model']['small_model_bound']='所有候选只涉及同一对象的布尔类型和一至两个存在见证；两个对象足以构造各错误强化项的反例。D项的全域等价另由量词否定和德摩根律证明。'

M=bits_models(5,lambda m:implies(m[0],m[1]) and implies(m[2],m[3]) and m[1]!=m[3] and m[2]!=m[4])
def f69(m):return '精密模式'+('开启' if m[0] else '关闭')+'，刻写采用'+('激光' if m[2] else '机械')+'；温控'+('开启' if m[1] else '关闭')+'，光学防护'+('开启' if m[3] else '关闭')
add(69,'某加工单元规定：开启精密模式就必须开启温控；采用激光刻写就必须开启光学防护。温控与光学防护恰好开启一项，激光刻写与机械刻写恰好采用一种。下列哪项一定成立？',
 ['采用机械刻写，就一定开启精密模式','不开启精密模式，就一定采用激光刻写','开启精密模式，就一定采用机械刻写','开启光学防护，就一定采用激光刻写'],M,
 [lambda m:implies(m[4],m[0]),lambda m:implies(not m[0],m[2]),lambda m:implies(m[0],m[4]),lambda m:implies(m[3],m[2])],
 'must','两个排他选择之间的条件传递',
 ['若开启精密模式，则开启温控，排除光学防护；由“激光刻写→光学防护”的逆否，不能采用激光刻写。激光、机械刻写恰好选一种，因此必须采用机械刻写。其余三项分别倒推条件或把未开精密模式误作必用激光。'],['JS24B-91','N26-103'],f69)

# Four truth questions; distinct roles of equivalence, truth counts and cardinality.
M=[]
for cabinet in range(3):
 a,b,c=(cabinet==i for i in range(3))
 reports=(implies(a,b),b or c,not b)
 if sum(reports)==2:M.append((cabinet,reports))
add(70,'甲、乙、丙三个密封柜中，恰有一个柜存放样本。三条记录分别是：①如果甲柜有样本，那么乙柜有样本；②乙柜或丙柜有样本；③乙柜没有样本。已知三条记录恰有两条为真。以下哪项一定为真？',
 ['甲柜有样本','丙柜有样本','乙柜有样本','甲柜、丙柜至少有一个存放样本'],M,
 [lambda m:m[0]==0,lambda m:m[0]==2,lambda m:m[0]==1,lambda m:m[0] in [0,2]],
 'must','条件句与析取的等价关系结合真假数量',
 ['因恰有一个柜存放样本，记录①为“甲柜没有样本”，与记录②等价，二者同真同假。若两者同假，三条最多一真，不符；故①②均真，③为假，样本在乙柜。'],['JS24B-92','BJ25-73'],lambda m:'样本在'+ '甲乙丙'[m[0]]+'柜，三条记录依次为'+ '、'.join('真' if x else '假' for x in m[1]),difficulty='中')

M=[]
for m in product([False,True],repeat=5):
 if sum(m)!=2:continue
 a,b,c,d,e=m
 reports=(a and b,c or d,a==e,not b and not c)
 if sum(reports)==2 and reports[2]==reports[3]:M.append((m,reports))
pairs71=[(0,1),(2,3),(1,4),(0,4)]
add(71,'甲、乙、丙、丁、戊五个方案中恰好批准两个。四位评审分别判断：第一位：“甲、乙都获批”；第二位：“丙、丁至少一个获批”；第三位：“甲、戊的获批状态相同”；第四位：“乙、丙都未获批”。已知四个判断恰有两个为真，且第三、第四个判断真假相同。获批的两个方案是：',
 ['甲、乙','丙、丁','乙、戊','甲、戊'],M,[lambda m,p=p:all(m[0][i] for i in p) for p in pairs71],
 'must','同真同假与总真假数的反证分支',
 ['若第三、第四同假，则第一、第二都真。第一真要求甲乙获批，两个名额已满，与第二要求丙丁至少一个获批矛盾。因此第三、第四均真，第一、第二均假。第二假排除丙丁，第四真排除乙，只能批准甲戊，且第三判断也真。'],['JS24B-92'],lambda m:'批准'+ '、'.join('甲乙丙丁戊'[i] for i,x in enumerate(m[0]) if x)+'，四个判断依次为'+ '、'.join('真' if x else '假' for x in m[1]),difficulty='难')

M=[]
for k in range(2,7):
 reports=(k==6,k<6,k==3,6-k>=2)
 if sum(reports)==2:M.append((k,reports))
add(72,'一批六份记录接受复核，至少两份通过。四条统计分别称：①六份全部通过；②至少一份未通过；③恰好三份通过；④至少两份未通过。已知四条统计恰有两条为真。通过复核的记录可能恰有多少份？',
 ['3份','5份','4份','6份'],M,[lambda m,v=v:m[0]==v for v in [3,5,4,6]],'may',
 '真假数量与整数区间联合筛选',
 ['通过3份时②③④均真，是三真；通过5份时仅②真；通过6份时仅①真，均不符。通过4份时②④真、①③假，恰好两真，可以成立。通过2份同样可行，但未列入候选；不能误判题干已唯一确定通过数。'],['BJ25-75','JS24B-92'],lambda m:'通过'+str(m[0])+'份，四条统计依次为'+ '、'.join('真' if x else '假' for x in m[1]),difficulty='中')

M=[]
for m in product([False,True],repeat=4):
 if sum(m)!=2:continue
 a,b,c,d=m
 reports=(a==b,implies(not c,d),a!=c,b and not d)
 if reports[0]!=reports[1] and reports[2]==reports[3]:M.append((m,reports))
add(73,'甲、乙、丙、丁四盏灯恰有两盏亮。四人分别判断：①甲、乙亮灭状态相同；②如果丙不亮，那么丁亮；③甲、丙恰好一盏亮；④乙亮且丁不亮。已知①②真假相反，③④真假相同。以下哪项一定成立？',
 ['甲、丁至少一盏亮','乙、丙至少一盏亮','乙、丁的亮灭状态相同','甲、丙的亮灭状态相同'],M,
 [lambda m:m[0][0] or m[0][3],lambda m:m[0][1] or m[0][2],lambda m:m[0][1]==m[0][3],lambda m:m[0][0]==m[0][2]],
 'must','不同真假关系下保留多解再求共同事实',
 ['按两盏亮的六种组合核对两个真假关系，可保留乙丁、乙丙、甲丙、甲乙四种组合，分别满足全部条件。四种都至少有乙或丙亮，故B项必真；其他三个判断都可由其中某一组反驳。这里并不能确定唯一亮灯组合。'],['JS24B-92'],lambda m:'亮灯为'+ '、'.join('甲乙丙丁'[i] for i,x in enumerate(m[0]) if x)+'，四个判断依次为'+ '、'.join('真' if x else '假' for x in m[1]),difficulty='难')

# Four independent analyses: rank arithmetic, circle, three-way matching and possible extrema.
M=[m for m in permutations(range(1,6)) if m[0]+m[1]==m[2]+m[3] and m[0]<m[2] and m[4] not in [1,5]]
add(74,'甲、乙、丙、丁、戊五台设备的检测用时各不相同，分别为1、2、3、4、5分钟。甲、乙用时之和等于丙、丁用时之和；甲比丙用时少；戊既非用时最少，也非用时最多。以下哪项一定成立？',
 ['戊用时2分钟','戊用时3分钟','甲用时1分钟','乙比丁用时少'],M,
 [lambda m:m[4]==2,lambda m:m[4]==3,lambda m:m[0]==1,lambda m:m[1]<m[3]],'must',
 '整数奇偶与等和配对',
 ['总用时为15分钟，甲乙与丙丁两组和相等，所以除去戊后总和必须为偶数，戊的用时是奇数。排除最少的1和最多的5，只能是3。又由甲＜丙且甲＋乙＝丙＋丁，得乙＞丁，D项方向相反。'],['JS24B-101'],lambda m:'甲、乙、丙、丁、戊分别用时'+ '、'.join(map(str,m))+'分钟')

M=[]
for tail in permutations(range(1,6)):
 row=(0,)+tail;p={x:row.index(x) for x in row}
 if p[1]!=3 or (p[2]-p[3])%6 in [1,5] or (p[4]-p[2])%6!=1 or (p[5]-p[3])%6==3:continue
 M.append(row)
def adjacent(m,a,b):return (m.index(a)-m.index(b))%6 in [1,5]
def opposite(m,a,b):return (m.index(a)-m.index(b))%6==3
add(75,'林、周、许、陈、赵、吴六人围坐在圆桌的六个等距座位。周与林相对；沿顺时针方向，赵紧接着坐在许后一个座位；许、陈不相邻；吴、陈不相对。以下哪项一定成立？',
 ['许与陈相对','赵与吴相对','陈与吴相邻','林与赵相邻'],M,
 [lambda m:opposite(m,2,3),lambda m:opposite(m,4,5),lambda m:adjacent(m,3,5),lambda m:adjacent(m,0,4)],
 'must','环形相邻与相对：合并有向连座后求共同关系',
 ['固定林作为圆桌参照起点，只消除整体旋转，不增加题干条件。周在相对位置，许赵按顺时针相邻。再排除许陈相邻和吴陈相对，可行顺时针序列为林许赵周陈吴、林许赵周吴陈、林陈吴周许赵、林吴陈周许赵。四种均有陈吴相邻。'],['N22-109','N23-107'],lambda m:'从林起按顺时针为'+ '、'.join('林周许陈赵吴'[i] for i in m))

M=[]
for cities in permutations(range(3)):
 for methods in permutations(range(3)):
  if cities[0]==0 or methods[1]==2 or methods[cities.index(0)]!=1 or cities[methods.index(2)]==1:continue
  if (cities[2]==2)!=(methods[0]==0):continue
  M.append((cities,methods))
def f76(m):return '；'.join('唐岳孟'[i]+'去'+['东站','南站','西站'][m[0][i]]+'用'+['声检','光检','磁检'][m[1][i]] for i in range(3))
add(76,'唐、岳、孟三人分别前往东、南、西三个检测站，每站一人，分别使用声检、光检、磁检三种不同方法，每人一种。已知唐不去东站，岳不用磁检；去东站者使用光检；磁检不在南站进行；孟去西站，当且仅当唐使用声检。以下哪项一定成立？',
 ['如果唐去西站，那么孟不用磁检','如果岳去东站，那么孟去西站','如果孟去南站，那么岳用声检','如果唐用声检，那么孟去南站'],M,
 [lambda m:implies(m[0][0]==2,m[1][2]!=2),lambda m:implies(m[0][1]==0,m[0][2]==2),
  lambda m:implies(m[0][2]==1,m[1][1]==0),lambda m:implies(m[1][0]==0,m[0][2]==1)],
 'must','三属性匹配中的条件式共同结论',
 ['若唐去西站，则唐不可能用光检，因为光检由去东站者使用。若唐用声检，双向条件又要求孟也去西站，与每站一人矛盾。因此唐只能用磁检，孟当然不能再用磁检，A项成立。其余条件式均有完整分配反例。'],['N24-109','JS24B-97','JS24B-98'],f76,difficulty='难')

M=[m for m in permutations(range(1,7),4) if sum(m)==14 and m[0]+m[1]==7 and m[1]>m[2] and m[3]%2==0]
def possible_maxima(ms):return len({m.index(max(m)) for m in ms})
aggregate(77,'甲、乙、丙、丁四个服务中心共有14名专员，每个中心1—6人，四中心人数各不相同。甲、乙共有7人，乙比丙人多，丁的人数是偶数。四个中心中，可能成为人数最多中心的，共有几个？',
 ['1个','3个','4个','2个'],M,[1,3,4,2],possible_maxima,
 '跨模型可能对象的并集：不能与单一安排的最多者混淆',
 ['丙少于乙，丙不可能最多。若甲多于乙，则由甲乙合计7，且丙更少，结合丙丁合计7、丁为偶数、人数均不同，可得丙1、丁6，丁又超过甲，所以甲也不能最多。',
  '甲乙丙丁为1、6、3、4时，乙最多；为2、5、1、6时，丁最多。故可能最多的只有乙、丁，共2个。'],['N24-110','JS24B-101'],lambda m:'甲乙丙丁人数依次为'+ '、'.join(map(str,m)))

from formal_parallel import QUESTIONS as PARALLEL_QUESTIONS,REG as PARALLEL_REG,structure_isomorphic,inference_truth_check
QUESTIONS.extend(PARALLEL_QUESTIONS);REG.update(PARALLEL_REG)

def verify():
 assert len(QUESTIONS)==30 and [q['n'] for q in QUESTIONS]==list(range(51,81))
 assert [len(GROUP_MODELS[k]) for k in (51,56,61)]==[10,56,17]
 checks={}
 for q in QUESTIONS:
  n=q['n'];r=REG[n]
  assert len(q['options'])==4 and len(set(q['options']))==4
  assert not any(x.startswith(('A.','B.','C.','D.','A、','B、','C、','D、')) for x in q['options'])
  if r['kind']=='ordinary':
   records,valid=eval_record(r['models'],r['preds'],r['mode'],r['formatter'])
   assert records==q['model']['option_checks'] and valid==q['model']['option_validity']
   item=dict(model_count=len(r['models']),evaluation_mode=r['mode'],unique_answer=True,option_validity=valid,options=records)
  elif r['kind']=='aggregate':
   result=r['result_fn'](r['models']);valid=[v==result for v in r['values']]
   assert sum(valid)==1 and result==q['model']['computed_value']
   item=dict(model_count=len(r['models']),evaluation_mode='aggregate',computed_value=result,unique_answer=True,
             option_values=r['values'],option_validity=valid)
   if n==62:
    finish=lambda m:max(m[i]+DUR[i]-1 for i in range(5))
    item['finish_distribution']=dict(Counter(finish(m) for m in r['models']))
    item['optimal_witness']=js(next(m for m in r['models'] if finish(m)==result))
    item['resource_lower_bound']=sum(DUR[i] for i in [0,2,4])
   if n==77:
    people=sorted({m.index(max(m)) for m in r['models']})
    item['possible_maximum_centers']=['甲乙丙丁'[i] for i in people]
    item['witnesses']={'甲乙丙丁'[i]:js(next(m for m in r['models'] if m.index(max(m))==i)) for i in people}
  else:
   valid=[structure_isomorphic(r['source'],x) for x in r['inferences']]
   assert sum(valid)==1 and valid==q['model']['option_validity']
   source_check=inference_truth_check(r['source'],r['quantified'])
   option_checks=[dict(structure_match=v,**inference_truth_check(x,r['quantified'])) for x,v in zip(r['inferences'],valid)]
   assert source_check==q['model']['source_truth_check'] and option_checks==q['model']['option_checks']
   item=dict(evaluation_mode='structure_isomorphism',unique_answer=True,option_validity=valid,
       source_truth_check=source_check,option_checks=option_checks)
  assert valid['ABCD'.index(q['answer'])]
  item['answer']=q['answer'];checks[str(n)]=item
 assert GROUP_MODELS=={51:g1(),56:g2(),61:g3()}
 # Check the direct scope translation of Q68 in both directions, including
 # worlds excluded by its premise; do not merely retest under the premise.
 q68_equivalence=all(
  (not all(implies(bit(t,0),bit(t,1)) and implies(bit(t,2),bit(t,3)) for t in m))
  == REG[68]['preds'][3](m) for m in product(range(16),repeat=2))
 assert q68_equivalence
 checks['68']['whole_statement_equivalence_all_256_worlds']=True
 sources=json.loads((ROOT/'sources_formal.json').read_text(encoding='utf-8'))
 known={x['id'] for x in sources['sources']}
 missing={ref for q in QUESTIONS for ref in q['source_refs'] if ref not in known}
 assert not missing,missing
 return dict(passed=True,questions=list(range(51,81)),
  structure={'shared_material':15,'translation':4,'truth':4,'independent_analysis':4,'parallel_structure':3},
  group_checks={str(k):dict(model_count=len(v),all_models=js(v),additional_conditions_reset_per_question=True) for k,v in GROUP_MODELS.items()},
  checks=checks,answer_counts=dict(Counter(q['answer'] for q in QUESTIONS)),
  scope='结构同构检查以明确的算子、量词和否定作用域为准；不以主题或有效性代替结构。量词题的有限反例空间配有小模型界及演绎说明。')

if __name__=='__main__':
 report=verify()
 (ROOT/'questions_formal.json').write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'groups_formal.json').write_text(json.dumps(GROUPS,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'verification_formal.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'passed':report['passed'],'group_models':{k:v['model_count'] for k,v in report['group_checks'].items()},
  'answers':[(q['n'],q['answer']) for q in QUESTIONS]},ensure_ascii=False))


