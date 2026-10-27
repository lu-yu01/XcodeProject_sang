"""Independent finite models transcribed solely from blind_cards_formal.

Does not import or read any author module, question JSON, answers or checks.
First natural answers were saved before this enumeration was written/run.
"""
from itertools import combinations, permutations, product
from pathlib import Path
import json, hashlib

ROOT=Path(__file__).resolve().parent
FIRST=json.loads((ROOT/'review_formal_first_answers_a.json').read_text(encoding='utf8'))
RESULTS={}

def imp(a,b): return not a or b

def check(n,models,predicates,mode):
    counts=[sum(bool(p(m)) for m in models) for p in predicates]
    total=len(models)
    assert total
    pick={'possible':lambda c:c>0, 'necessary':lambda c:c==total,
          'impossible':lambda c:c==0,'notnecessary':lambda c:c<total,
          'unique':lambda c:c==1}[mode]
    chosen=['ABCD'[i] for i,c in enumerate(counts) if pick(c)]
    witnesses=[]
    for p in predicates:
        yes=next((m for m in models if p(m)),None)
        no=next((m for m in models if not p(m)),None)
        witnesses.append({'satisfying':yes,'counterexample':no})
    RESULTS[n]={'model_count':total,'option_satisfying_counts':counts,
                'mode':mode,'selected_options':chosen,'unique':len(chosen)==1,
                'witnesses':witnesses}

def scalar(n,values,options,kind):
    selected=['ABCD'[i] for i,x in enumerate(options) if x in values]
    RESULTS[n]={'mode':kind,'computed_values':values,'selected_options':selected,'unique':len(selected)==1}

# 51--55 binary station selection; each question starts from the same base.
stations=[]
for selected in combinations(range(8),4):
    a,b,c,d,e,f,g,h=(i in selected for i in range(8))
    if not (a or b):continue
    if not imp(a,c) or not imp(b,not d):continue
    if f != (a != e):continue
    if not imp(g,b):continue
    stations.append(tuple(i in selected for i in range(8)))
targets=[(0,1,2,3),(1,4,5,6),(0,2,4,5),(0,2,3,7)]
check(51,stations,[lambda m,t=t:tuple(i for i,v in enumerate(m) if v)==t for t in targets],'possible')
check(52,stations,[lambda m:m[0] or m[4],lambda m:m[2] or m[5],lambda m:m[3] or m[7],lambda m:m[4] or m[6]],'necessary')
check(53,[m for m in stations if not m[2]],
      [lambda m:m[0] and not m[5],lambda m:m[3] and m[7],lambda m:m[6] and m[7],lambda m:m[6] and not m[7]],'possible')
check(54,[m for m in stations if not m[5]],
      [lambda m:m[1] and m[7] and not m[4],lambda m:m[3] and not m[7],lambda m:m[0] and m[1],lambda m:m[6] and m[4]],'impossible')
check(55,stations,[lambda m:not m[0] and not m[4],lambda m:m[0] and not m[7],lambda m:m[1] and not m[6],lambda m:m[2] and m[5]],'unique')

# 56--60 four unordered pairs over five people (L,Z,X,C,R = 0..4).
L,Z,X,C,R=range(5)
pairs=[tuple(x) for x in combinations(range(5),2) if x!=(L,Z)]
allocations=[]
for files in product(pairs,repeat=4):
    count=[sum(k in f for f in files) for k in range(5)]
    if not all(1<=c<=2 for c in count):continue
    if ((L in files[0])+(X in files[0])) != 1 or R in files[0]:continue
    if (C in files[1]) != (Z in files[3]):continue
    if not any(f==(X,R) for f in files):continue
    allocations.append(files)

def same(f,*people):return f==tuple(sorted(people))
targets56=[((L,C),(L,X),(Z,C),(Z,R)),((Z,X),(L,C),(X,R),(L,C)),
           ((X,C),(L,R),(Z,C),(X,R)),((Z,X),(L,R),(L,Z),(X,C))]
check(56,allocations,[lambda m,t=t:all(same(f,*p) for f,p in zip(m,t)) for t in targets56],'possible')
def count(m,k):return sum(k in f for f in m)
check(57,[m for m in allocations if same(m[0],X,C)],
      [lambda m:count(m,R)==1,lambda m:count(m,L)==1,lambda m:count(m,Z)==2,lambda m:count(m,X)==1],'necessary')
check(58,[m for m in allocations if same(m[1],L,X)],
      [lambda m:same(m[2],Z,R),lambda m:same(m[3],L,R),lambda m:same(m[0],Z,X),lambda m:count(m,C)==count(m,R)==1],'possible')
check(59,[m for m in allocations if C in m[0] and count(m,C)==1],
      [lambda m:count(m,Z)==2,lambda m:count(m,L)==1,lambda m:sum(same(f,X,R) for f in m)==2,lambda m:X in m[1] and X in m[3]],'impossible')
check(60,allocations,[lambda m:same(m[0],L,C) and same(m[1],L,X),
                     lambda m:same(m[0],X,C) and same(m[3],X,R),
                     lambda m:same(m[0],Z,X) and same(m[2],X,R),
                     lambda m:same(m[0],L,C) and same(m[1],X,C)],'unique')

# 61--65 starts (clean,calibrate,scan,review,pack). End before next start.
schedules=[]
for w,k,s,r,p in product(range(1,7),repeat=5):
    if w+1>6 or s+1>6:continue
    occupied=[set(range(w,w+2)),set(range(s,s+2)),{p}]
    if any(occupied[i]&occupied[j] for i,j in combinations(range(3),2)):continue
    if k==r:continue
    if not (w+1<k<p and s+1<r):continue
    schedules.append((w,k,s,r,p))
targets61=[(1,3,2,5,5),(1,4,3,5,6),(3,4,1,3,6),(1,3,3,3,5)]
check(61,schedules,[lambda m,t=t:m==t for t in targets61],'possible')
finish=min(max(w+1,k,s+1,r,p) for w,k,s,r,p in schedules)
scalar(62,[finish],[4,6,5,None],'earliest_finish')
check(63,[m for m in schedules if m[2]==1],
      [lambda m:m[4]==6,lambda m:m[1]==4,lambda m:m[3]==5,lambda m:m[0]==1],'necessary')
check(64,[m for m in schedules if m[1]==4],
      [lambda m:m[4]==5,lambda m:m[3]==4,lambda m:m[0]==2,lambda m:m[2]==4],'impossible')
check(65,[m for m in schedules if m[3]==5],
      [lambda m:m[0]==1,lambda m:m[2]==3,lambda m:m[4]>=5,lambda m:m[1]==3],'notnecessary')

models66=[]
for s,b,c,d,y in product([False,True],repeat=5):
    if s and d and imp(s,b or c) and imp(d,not b) and imp(not y,not c):models66.append((s,b,c,d,y))
check(66,models66,[lambda m:m[1],lambda m:not m[3],lambda m:not m[2],lambda m:m[4]],'necessary')

# A finite first-order type population suffices; duplicate individuals irrelevant.
types67=[t for t in product([False,True],repeat=4) if imp(t[0],t[1]) and imp(t[1] and t[2],not t[3])]
pops67=[]
for flags in product([False,True],repeat=len(types67)):
    pop=tuple(t for t,f in zip(types67,flags) if f)
    if any(t[2] and t[0] for t in pop) and any(t[1] and not t[2] for t in pop):pops67.append(pop)
check(67,pops67,[lambda pop:any(not t[2] and t[0] for t in pop),
                lambda pop:all(imp(t[1],not t[3]) for t in pop),
                lambda pop:any(t[0] and not t[3] for t in pop),
                lambda pop:any(t[3] and not t[1] for t in pop)],'necessary')

types68=list(product([False,True],repeat=4))
equiv68=[True]*4;counter68=[None]*4
for bits in range(1,1<<len(types68)):
    pop=[t for i,t in enumerate(types68) if bits>>i&1]
    original=not all(imp(t[0],t[1]) and imp(t[2],t[3]) for t in pop)
    forms=[any(t[0] and not t[1] and t[2] and not t[3] for t in pop),
           all(not (imp(t[0],t[1]) and imp(t[2],t[3])) for t in pop),
           any(t[0] and not t[1] for t in pop) and any(t[2] and not t[3] for t in pop),
           any((t[0] and not t[1]) or (t[2] and not t[3]) for t in pop)]
    for i,f in enumerate(forms):
        if f!=original:equiv68[i]=False;counter68[i]=counter68[i] or pop
RESULTS[68]={'mode':'quantified_equivalence_all_nonempty_type_populations','population_count':65535,
             'equivalent':equiv68,'counterexamples':counter68,
             'selected_options':['ABCD'[i] for i,v in enumerate(equiv68) if v],'unique':sum(equiv68)==1}

models69=[m for m in product([False,True],repeat=5) if imp(m[0],m[1]) and imp(m[2],m[3]) and (m[1]!=m[3]) and (m[2]!=m[4])]
check(69,models69,[lambda m:imp(m[4],m[0]),lambda m:imp(not m[0],m[2]),lambda m:imp(m[0],m[4]),lambda m:imp(m[3],m[2])],'necessary')
models70=[]
for chosen in range(3):
    a,b,c=(chosen==i for i in range(3))
    truths=[imp(a,b),b or c,not b]
    if sum(truths)==2:models70.append((a,b,c))
check(70,models70,[lambda m:m[0],lambda m:m[2],lambda m:m[1],lambda m:m[0] or m[2]],'necessary')

models71=[]
for selected in combinations(range(5),2):
    a,b,c,d,e=(i in selected for i in range(5))
    truths=[a and b,c or d,a==e,not b and not c]
    if sum(truths)==2 and truths[2]==truths[3]:models71.append(selected)
check(71,models71,[lambda m:m==(0,1),lambda m:m==(2,3),lambda m:m==(1,4),lambda m:m==(0,4)],'possible')
ks=[k for k in range(2,7) if sum([k==6,k<6,k==3,6-k>=2])==2]
scalar(72,ks,[3,5,4,6],'possible_pass_counts')

models73=[]
for selected in combinations(range(4),2):
    a,b,c,d=(i in selected for i in range(4))
    truths=[a==b,imp(not c,d),a!=c,b and not d]
    if truths[0]!=truths[1] and truths[2]==truths[3]:models73.append((a,b,c,d))
check(73,models73,[lambda m:m[0] or m[3],lambda m:m[1] or m[2],lambda m:m[1]==m[3],lambda m:m[0]==m[2]],'necessary')
models74=[p for p in permutations(range(1,6)) if p[0]+p[1]==p[2]+p[3] and p[0]<p[2] and p[4] not in (1,5)]
check(74,models74,[lambda m:m[4]==2,lambda m:m[4]==3,lambda m:m[0]==1,lambda m:m[1]<m[3]],'necessary')

# Person positions (Lin,Zhou,Xu,Chen,Zhao,Wu); fix rotational symmetry only.
models75=[]
for pos in permutations(range(1,6)):
    m=(0,)+pos
    if m[1]!=3:continue
    if m[4]!=(m[2]+1)%6:continue
    if (m[2]-m[3])%6 in (1,5):continue
    if (m[5]-m[3])%6==3:continue
    models75.append(m)
adj=lambda a,b:(a-b)%6 in (1,5)
check(75,models75,[lambda m:(m[2]-m[3])%6==3,lambda m:(m[4]-m[5])%6==3,
                  lambda m:adj(m[3],m[5]),lambda m:adj(m[0],m[4])],'necessary')

# People Tang,Yue,Meng. Stations E,S,W; methods sound,light,magnetic.
models76=[]
for station in permutations('ESW'):
 for method in permutations('slm'):
    if station[0]=='E' or method[1]=='m':continue
    if any(station[i]=='E' and method[i]!='l' for i in range(3)):continue
    if any(method[i]=='m' and station[i]=='S' for i in range(3)):continue
    if (station[2]=='W') != (method[0]=='s'):continue
    models76.append((station,method))
check(76,models76,[lambda m:imp(m[0][0]=='W',m[1][2]!='m'),
                  lambda m:imp(m[0][1]=='E',m[0][2]=='W'),
                  lambda m:imp(m[0][2]=='S',m[1][1]=='s'),
                  lambda m:imp(m[1][0]=='s',m[0][2]=='S')],'necessary')
models77=[m for m in product(range(1,7),repeat=4) if len(set(m))==4 and sum(m)==14 and m[0]+m[1]==7 and m[1]>m[2] and m[3]%2==0]
possible_max=sorted(set(m.index(max(m)) for m in models77))
scalar(77,[len(possible_max)],[1,3,4,2],'count_of_possible_largest_centers')
RESULTS[77].update(possible_center_indices=possible_max,assignments=models77)

# Independently normalized connective/quantifier structures, not author models.
signatures={
78:[
    'All(A,B);All(B,notC);Some(D,A)=>Some(D,notC)',
    ['All(A,B);All(B,notC);Some(D,B)=>Some(D,notC)',
     'All(A,B);All(B,notC);Some(D,A)=>Some(D,notC)',
     'All(A,B);All(A,notC);Some(D,B)=>Some(D,notC)',
     'All(A,B);All(B,notC);All(D,A)=>All(D,notC)']],
79:[
    'Implies(And(P,Q),R);R=>And(P,Q)',
    ['Implies(Or(P,Q),R);R=>Or(P,Q)',
     'Implies(And(P,Q),R);notR=>Or(notP,notQ)',
     'Implies(And(P,Q),R);And(P,Q)=>R',
     'Implies(And(P,Q),R);R=>And(P,Q)']],
80:[
    'Some(A,notB);All(notB,C)=>Some(A,C)',
    ['All(A,notB);All(notB,C)=>All(A,C)',
     'Some(A,notB);All(C,notB)=>Some(A,C)',
     'Some(A,notB);All(notB,C)=>Some(A,C)',
     'Some(A,B);All(B,C)=>Some(A,C)']]}
for n,(original,options) in signatures.items():
    selected=['ABCD'[i] for i,s in enumerate(options) if s==original]
    RESULTS[n]={'mode':'normalized_structure','original_structure':original,
                'option_structures':options,'selected_options':selected,'unique':len(selected)==1}

first={x['n']:x for x in FIRST['items']}
items=[]
for n in range(51,81):
    proof=RESULTS[n]; old=first[n]
    answer=proof['selected_options'][0] if proof['unique'] else None
    items.append({'n':n,'first_answer':old['first_answer'],'answer':answer,
                  'first_natural_derivation':old['natural_derivation'],
                  'independent_method':'先自然演绎记录首次答案；随后自行从题卡转录约束并枚举/规范化，不读取作者模型。',
                  'confidence':0.99 if proof['unique'] and answer==old['first_answer'] else old['confidence'],
                  'ambiguities':[] if proof['unique'] else ['独立枚举未得唯一答案，需作者检查。'],
                  'first_answer_confirmed':answer==old['first_answer'],
                  'independent_validation':proof})
report={'passed':all(x['first_answer_confirmed'] and not x['ambiguities'] for x in items),
        'reviewer':'代理A独立求解，非教师盲审',
        'source_card':'blind_cards_formal.json',
        'card_sha256':hashlib.sha256((ROOT/'blind_cards_formal.json').read_bytes()).hexdigest(),
        'forbidden_author_materials_read':False,
        'additional_conditions_not_inherited_between_questions':True,
        'question_count':len(items),'items':items}
(ROOT/'review_formal_blind.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'passed':report['passed'],'answer_string':''.join(x['answer'] or '?' for x in items),
                  'first_answer_mismatches':[x['n'] for x in items if not x['first_answer_confirmed']],
                  'ambiguities':[x['n'] for x in items if x['ambiguities']]},ensure_ascii=False))
