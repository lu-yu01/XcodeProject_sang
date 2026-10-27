"""Three original strict parallel-structure questions and formal validation."""
from itertools import product,permutations
QUESTIONS=[];REG={};LETTERS='ABCD'
def js(v):
 if isinstance(v,dict):return {str(k):js(x) for k,x in v.items()}
 if isinstance(v,(tuple,list)):return [js(x) for x in v]
 return v
def Not(a):return ('not',a)
def And(a,b):return ('and',a,b)
def Or(a,b):return ('or',a,b)
def Imp(a,b):return ('imp',a,b)
def All(a):return ('all',a)
def Some(a):return ('some',a)
def ast_atoms(a):
 if isinstance(a,str):return {a}
 return set().union(*(ast_atoms(x) for x in a[1:]))
def ast_norm(a,mapping=None):
 if isinstance(a,str):return (mapping or {}).get(a,a)
 op=a[0];args=[ast_norm(x,mapping) for x in a[1:]]
 if op in ('and','or'):args=sorted(args,key=repr)
 return (op,*args)
def structure_key(premises,conclusion,mapping=None):
 return tuple(sorted((ast_norm(p,mapping) for p in premises),key=repr)),ast_norm(conclusion,mapping)
def structure_isomorphic(source,target):
 sa=sorted(set().union(*(ast_atoms(x) for x in source[0]),ast_atoms(source[1])))
 ta=sorted(set().union(*(ast_atoms(x) for x in target[0]),ast_atoms(target[1])))
 if len(sa)!=len(ta):return False
 target_key=structure_key(*target)
 return any(structure_key(*source,dict(zip(sa,perm)))==target_key for perm in permutations(ta))
def ast_eval(a,assignment,domain=None):
 if isinstance(a,str):return assignment[a]
 op=a[0]
 if op=='not':return not ast_eval(a[1],assignment,domain)
 if op=='and':return ast_eval(a[1],assignment,domain) and ast_eval(a[2],assignment,domain)
 if op=='or':return ast_eval(a[1],assignment,domain) or ast_eval(a[2],assignment,domain)
 if op=='imp':return not ast_eval(a[1],assignment,domain) or ast_eval(a[2],assignment,domain)
 if op=='all':return all(ast_eval(a[1],individual,domain) for individual in domain)
 if op=='some':return any(ast_eval(a[1],individual,domain) for individual in domain)
 raise ValueError(op)
def inference_truth_check(inference,quantified):
 premises,conclusion=inference
 names=sorted(set().union(*(ast_atoms(x) for x in premises),ast_atoms(conclusion)))
 assignments=[dict(zip(names,bits)) for bits in product([False,True],repeat=len(names))]
 universes=product(assignments,repeat=2) if quantified else assignments
 total=0;true=0;counterexample=None;witness=None
 for world in universes:
  ass={} if quantified else world;domain=world if quantified else None
  if all(ast_eval(x,ass,domain) for x in premises):
   total+=1
   if witness is None:witness=world
   if ast_eval(conclusion,ass,domain):true+=1
   elif counterexample is None:counterexample=world
 assert total>0
 return dict(premise_model_count=total,conclusion_true_count=true,conclusion_false_count=total-true,
  valid_in_small_model_family=true==total,first_premise_witness=js(witness),counterexample=js(counterexample))
def parallel(n,stem,options,source,inferences,point,reason,refs,quantified=True):
 valid=[structure_isomorphic(source,x) for x in inferences];assert sum(valid)==1
 ans=LETTERS[valid.index(True)]
 source_check=inference_truth_check(source,quantified)
 checks=[dict(structure_match=v,**inference_truth_check(x,quantified)) for x,v in zip(inferences,valid)]
 QUESTIONS.append(dict(n=n,category='逻辑推理',stem=stem,ask='以下哪项在量词、否定位置以及前提到结论的连接关系上，与上述推理结构一致？',options=options,answer=ans,
  point=point,analysis=list(reason)+[f'故选{ans}。判断的是量词、否定作用域与条件连接结构，不能仅以结论是否成立或情境是否相似代替。'],
  difficulty='难',mechanism=point,source_refs=refs,model=dict(evaluation_mode='structure_isomorphism',
  source_ast=js(source),options_ast=js(inferences),option_validity=valid,source_truth_check=source_check,option_checks=checks,
  normalized_by='只允许谓词/命题整体重命名、合取析取交换顺序和前提交换顺序；不允许把原子任意替换为其否定，不反转条件方向，不增删存在量词。',
  quantified_small_model_bound=2 if quantified else None)))
 REG[n]=dict(kind='parallel',source=source,inferences=inferences,quantified=quantified)

S78=([All(Imp('A','B')),All(Imp('B',Not('C'))),Some(And('D','A'))],Some(And('D',Not('C'))))
O78=[
 ([All(Imp('A','B')),All(Imp('B',Not('C'))),Some(And('D','B'))],Some(And('D',Not('C')))),
 S78,
 ([All(Imp('B','A')),All(Imp('B',Not('C'))),Some(And('D','A'))],Some(And('D',Not('C')))),
 ([All(Imp('A','B')),All(Imp('B',Not('C'))),All(Imp('D','A'))],All(Imp('D',Not('C'))))]
parallel(78,'所有馆藏修复件都完成了登记；所有完成登记的物件均未外借；有些特展物件是馆藏修复件。因此，有些特展物件未外借。',
 ['所有志愿教师都完成了培训；所有完成培训者均未在岗；有些社区服务者完成了培训。因此，有些社区服务者未在岗。',
  '所有冷链样品都经过了封签；所有封签样品均未拆封；有些复检样品是冷链样品。因此，有些复检样品未拆封。',
  '所有可拆卸展架都是木制展架；所有可拆卸展架均未固定在地面；有些新展架是木制展架。因此，有些新展架未固定在地面。',
  '所有低碳巡检车都完成了充电备案；所有完成充电备案的车辆均不使用燃油；所有夜巡车都是低碳巡检车。因此，所有夜巡车均不使用燃油。'],
 S78,O78,'平行结构：存在见证沿两段全称链传递',
 ['原推理为“所有A是B；所有B非C；有些D是A；所以有些D非C”。B项冷链—封签—未拆封的链条及复检样品的存在见证完全对应。',
  'A项把存在见证接在中间类B，而原题接在起点类A；A本身可有效推出结论，但结构少经过一段链。C项第一条包含方向相反。D项把“有些”改成了全称，结论也变成全称，均不相同。'],['BJ25-76','N26-103'])

S79=([Imp(And('P','Q'),'R'),'R'],And('P','Q'))
O79=[
 ([Imp(Or('P','Q'),'R'),'R'],Or('P','Q')),
 ([Imp(And('P','Q'),'R'),Not('R')],Or(Not('P'),Not('Q'))),
 ([Imp(And('P','Q'),'R'),And('P','Q')],'R'),S79]
parallel(79,'如果线路完成封测且备用电源就绪，那么试验可以启动。现在试验可以启动，所以线路完成了封测且备用电源已就绪。',
 ['如果完成预订或持有年票，就能进入展厅。现在能进入展厅，所以完成了预订或持有年票。',
  '如果样本已冷却且已密封，就能入库。现在样本不能入库，所以样本未冷却或未密封。',
  '如果雨量达标且土壤适宜，试种就会启动。现在雨量达标且土壤适宜，所以试种会启动。',
  '如果完成场地检测且器材齐备，演练就能开展。现在演练能开展，所以完成了场地检测且器材齐备。'],
 S79,O79,'平行结构：合取充分条件中的肯定后件',
 ['原题结构是“P且Q→R；R；所以P且Q”，属于肯定后件，不能保证结论正确。D项完整保留了合取前件、肯定后件及合取结论。',
  'A项虽也肯定后件，但前件和结论是析取，结构不同。B项为正确的否定后件，结论是否定合取后的析取。C项为肯定前件。'],['JS24B-91','BJ25-73'],quantified=False)

S80=([Some(And('A',Not('B'))),All(Imp(Not('B'),'C'))],Some(And('A','C')))
O80=[
 ([All(Imp('A',Not('B'))),All(Imp(Not('B'),'C'))],All(Imp('A','C'))),
 ([Some(And('A',Not('B'))),All(Imp('C',Not('B')))],Some(And('A','C'))),
 S80,
 ([Some(And('A','B')),All(Imp('B','C'))],Some(And('A','C')))]
parallel(80,'有些受检器件不耐高温；所有不耐高温的器件均须加装隔热层。因此，有些受检器件须加装隔热层。',
 ['所有山区线路均未铺设光缆；所有未铺设光缆的线路均使用无线回传。因此，所有山区线路均使用无线回传。',
  '有些馆藏书尚未数字化；所有需要修复的图书均未数字化。因此，有些馆藏书需要修复。',
  '有些新到标本未完成定名；所有未完成定名的标本均须单独存放。因此，有些新到标本须单独存放。',
  '有些培训课程属于实践课程；所有实践课程均在工坊开展。因此，有些培训课程在工坊开展。'],
 S80,O80,'平行结构：特称否定见证与否定前件的全称链',
 ['原推理为“有些A非B；所有非B是C；所以有些A是C”。C项以“新到标本—未定名—单独存放”逐项对应，存在量词与否定位置一致。',
  'A项把特称改为全称；B项把第二前提的包含方向倒置；D项没有两个前提中共同出现的否定谓词。D虽也是有效的特称传递，但不满足本题否定位置完全一致的要求。'],['BJ25-75','BJ25-76'])
