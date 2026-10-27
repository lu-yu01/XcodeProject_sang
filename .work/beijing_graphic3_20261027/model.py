"""Exact four triangular sectors per grid cell. No bitmap heuristics in answers."""
from pathlib import Path
from fractions import Fraction as F
import random,json,hashlib,itertools
ROOT=Path(__file__).resolve().parent
SYMBOLS={'CW':'●','CCW':'○','LR':'◆','UD':'◇','IT':'▲','IR':'△','CL':'■','MT':'□'}
RULES=[('CW','整体顺时针旋转90°'),('CCW','整体逆时针旋转90°'),
 ('LR','整体左右镜像'),('UD','整体上下镜像'),
 ('IT','上半部分黑白反色，下半不变'),('IR','右半部分黑白反色，左半不变'),
 ('CL','保留左半，将右半替换为左半的左右镜像'),('MT','仅将上半部分左右镜像，下半不变')]
def cell_rot(v,k=1):
 return sum(((v>>i)&1)<<((i+k)%4) for i in range(4))
def cell_lr(v):return sum(((v>>i)&1)<<[0,3,2,1][i] for i in range(4))
def cell_ud(v):return sum(((v>>i)&1)<<[2,1,0,3][i] for i in range(4))
def op(a,name):
 n=4
 if name=='CW':return [[cell_rot(a[n-1-c][r]) for c in range(n)] for r in range(n)]
 if name=='CCW':return [[cell_rot(a[c][n-1-r],-1) for c in range(n)] for r in range(n)]
 if name=='LR':return [[cell_lr(a[r][n-1-c]) for c in range(n)] for r in range(n)]
 if name=='UD':return [[cell_ud(a[n-1-r][c]) for c in range(n)] for r in range(n)]
 if name=='IT':return [[v^15 if r<2 else v for c,v in enumerate(row)] for r,row in enumerate(a)]
 if name=='IR':return [[v^15 if c>=2 else v for c,v in enumerate(row)] for r,row in enumerate(a)]
 if name=='IL':return [[v^15 if c<2 else v for c,v in enumerate(row)] for r,row in enumerate(a)]
 if name=='IALL':return [[v^15 for v in row] for row in a]
 if name=='CL':return [[a[r][c] if c<2 else cell_lr(a[r][n-1-c]) for c in range(n)] for r in range(n)]
 if name=='CR':return [[a[r][c] if c>=2 else cell_lr(a[r][n-1-c]) for c in range(n)] for r in range(n)]
 if name=='MT':return [[cell_lr(a[r][n-1-c]) if r<2 else a[r][c] for c in range(n)] for r in range(n)]
 if name=='MTUD':return [[cell_ud(a[1-r][c]) if r<2 else a[r][c] for c in range(n)] for r in range(n)]
 raise ValueError(name)
def sequence(a,seq):
 states=[a]
 for name in seq:states.append(op(states[-1],name))
 return states
def key(a):return tuple(v for row in a for v in row)
def distance(a,b):return sum((x^y).bit_count() for x,y in zip(key(a),key(b)))
def signature(a):
 return {'black_sectors':sum(v.bit_count() for v in key(a)),
  'white_cells':key(a).count(0),'black_cells':key(a).count(15),
  'half_cells':sum(v in (3,6,9,12) for v in key(a)),
  'left_right_symmetric':op(a,'LR')==a,'up_down_symmetric':op(a,'UD')==a}

# An independently coded geometry representation: exact triangle centroids.
OFFSETS=[(F(1,2),F(1,6)),(F(5,6),F(1,2)),(F(1,2),F(5,6)),(F(1,6),F(1,2))]
ALL={(F(c)+x,F(r)+y) for r in range(4) for c in range(4) for x,y in OFFSETS}
def points(a):return {(F(c)+x,F(r)+y) for r in range(4) for c in range(4) for i,(x,y) in enumerate(OFFSETS) if a[r][c]>>i&1}
def geometric(p,name):
 if name=='CW':return {(4-y,x) for x,y in p}
 if name=='CCW':return {(y,4-x) for x,y in p}
 if name=='LR':return {(4-x,y) for x,y in p}
 if name=='UD':return {(x,4-y) for x,y in p}
 if name in ('IT','IR','IL','IALL'):
  region={z for z in ALL if (z[1]<2 if name=='IT' else z[0]>=2 if name=='IR' else z[0]<2 if name=='IL' else True)}
  return p^region
 if name=='CL':
  left={z for z in p if z[0]<2};return left|{(4-x,y) for x,y in left}
 if name=='CR':
  right={z for z in p if z[0]>=2};return right|{(4-x,y) for x,y in right}
 if name=='MT':return {(4-x,y) if y<2 else (x,y) for x,y in p}
 if name=='MTUD':return {(x,2-y) if y<2 else (x,y) for x,y in p}
 raise ValueError(name)

SPECS=[
 {'n':1,'seq':['LR','CW','IT'],'answer':'B','wrong':[
  (['CW','LR','IT'],'将前两步的先后顺序颠倒'),
  (['LR','CW','IALL'],'把上半部分反色扩大为全图反色'),
  (['LR','IT','CW'],'在旋转前就进行上半部分反色')],
  'point':'整体镜像与旋转的先后，以及旋转后半区的位置'},
 {'n':2,'seq':['CL','CCW','IR'],'answer':'D','wrong':[
  (['CR','CCW','IR'],'把保留左半误读为保留右半'),
  (['CL','CW','IR'],'把逆时针旋转90°误做顺时针旋转90°'),
  (['CL','CCW','IL'],'最后对左半反色，误认当前图的右半')],
  'point':'半区镜像重建、旋转方向与当前图反色范围'},
 {'n':3,'seq':['MT','UD','CW'],'answer':'A','wrong':[
  (['MTUD','UD','CW'],'把上半内部的左右镜像误做上下镜像'),
  (['LR','UD','CW'],'将仅上半镜像扩大为全图左右镜像'),
  (['UD','MT','CW'],'把前两步颠倒，使局部镜像作用在另一半')],
  'point':'半区内部镜像与全图镜像的区别，局部操作的时序'}]

def generate():
 rng=random.Random(20261027);qs=[]
 for spec in SPECS:
  for attempt in range(20000):
   a=[[0]*4 for _ in range(4)]
   for br,bc in itertools.product([0,2],repeat=2):
    vals=[0,15,rng.choice([3,6,9,12]),rng.choice([3,6,9,12])];rng.shuffle(vals)
    for (dr,dc),v in zip(itertools.product(range(2),repeat=2),vals):a[br+dr][bc+dc]=v
   good=sequence(a,spec['seq'])[-1]
   candidates=[good]+[sequence(a,s)[-1] for s,_ in spec['wrong']]
   if len({key(x) for x in candidates})!=4:continue
   if len({key(sequence(a,['CW']*k)[-1]) for k in range(4)})<4:continue
   if any(not 8<=distance(good,b)<=64 for b in candidates[1:]):continue
   sigs=[signature(x) for x in candidates]
   if len({(x['black_sectors'],x['white_cells'],x['black_cells'],x['half_cells'],x['left_right_symmetric'],x['up_down_symmetric']) for x in sigs})!=1:continue
   if any(key(q['source'])==key(a) for q in qs):continue
   break
  else:raise AssertionError(f'no suitable item for {spec["n"]}')
  pos='ABCD'.index(spec['answer']);options=candidates[1:pos+1]+[good]+candidates[pos+1:]
  wrong_lookup={key(sequence(a,s)[-1]):dict(seq=s,reason=reason) for s,reason in spec['wrong']}
  explanations=[]
  for letter,b in zip('ABCD',options):
   explanations.append(dict(letter=letter,correct=b==good,**({'seq':spec['seq'],'reason':'依次执行题面三步操作'} if b==good else wrong_lookup[key(b)])))
  qs.append(dict(n=spec['n'],source=a,seq=spec['seq'],answer=spec['answer'],point=spec['point'],
    options=options,option_explanations=explanations,states=sequence(a,spec['seq']),
    difficulty='中等至中高（命题估计）',candidate_signatures=sigs))
 return qs
QUESTIONS=generate()
def verify():
 tests=[]
 for q in QUESTIONS:
  states=sequence(q['source'],q['seq']);p=points(q['source']);steps=[]
  for name,a in zip(q['seq'],states[1:]):
   p=geometric(p,name);assert p==points(a);steps.append({'operation':name,'geometric_representation_agrees':True})
  expected=states[-1];valid=[x==expected for x in q['options']]
  assert sum(valid)==1 and 'ABCD'[valid.index(True)]==q['answer']
  for e,b in zip(q['option_explanations'],q['options']):
   p=points(q['source'])
   for name in e['seq']:p=geometric(p,name)
   assert p==points(b)
  assert all(signature(b)['black_sectors']==32 for b in q['options'])
  tests.append({'n':q['n'],'steps':steps,'option_validity':valid,'answer':q['answer'],
    'sector_distance_to_answer':[distance(expected,b) for b in q['options']],
    'candidate_signatures':[signature(b) for b in q['options']]})
 # Test every primitive against independent geometry on every individual sector.
 for name in SYMBOLS:
  for r,c,i in itertools.product(range(4),range(4),range(4)):
   a=[[0]*4 for _ in range(4)];a[r][c]=1<<i
   assert points(op(a,name))==geometric(points(a),name)
 return dict(passed=True,questions=3,shared_rule_count=8,primitive_single_sector_checks=8*64,
   scope='四扇区离散模型与独立分数坐标几何模型逐步一致；候选唯一；干扰路径可复算。语义与图像另做无答案试解。',items=tests)
if __name__=='__main__':
 (ROOT/'questions.json').write_text(json.dumps(QUESTIONS,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'verification.json').write_text(json.dumps(verify(),ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'passed':True,'answers':{q['n']:q['answer'] for q in QUESTIONS},'sources':[q['source'] for q in QUESTIONS]},ensure_ascii=False))
