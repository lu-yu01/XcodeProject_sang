from pathlib import Path
from fractions import Fraction as F
import json,random,itertools,collections
ROOT=Path(__file__).resolve().parent
NAMES=[
 ('CW','●1','全图顺时针旋转90°'),('CCW','●2','全图逆时针旋转90°'),('R180','●3','全图旋转180°'),('IA','●4','全图黑白反色'),
 ('LR','○1','全图左右镜像'),('UD','○2','全图上下镜像'),('SX','○3','左右半区直接换位，内部朝向不变'),('SY','○4','上下半区直接换位，内部朝向不变'),
 ('MT','◆1','仅上半内部左右镜像，下半不变'),('MB','◆2','仅下半内部左右镜像，上半不变'),('ML','◆3','仅左半内部上下镜像，右半不变'),('MR','◆4','仅右半内部上下镜像，左半不变'),
 ('IT','◇1','仅上半黑白反色，下半不变'),('IB','◇2','仅下半黑白反色，上半不变'),('IL','◇3','仅左半黑白反色，右半不变'),('IR','◇4','仅右半黑白反色，左半不变'),
 ('CL','▲1','保留左半，将其左右镜像覆盖右半'),('CR','▲2','保留右半，将其左右镜像覆盖左半'),('CT','▲3','保留上半，将其上下镜像覆盖下半'),('CB','▲4','保留下半，将其上下镜像覆盖上半'),
 ('DL','△1','保留左半，向右平移复制以覆盖右半'),('DR','△2','保留右半，向左平移复制以覆盖左半'),('DT','△3','保留上半，向下平移复制以覆盖下半'),('DB','△4','保留下半，向上平移复制以覆盖上半'),
 ('PCW','■1','象限位置顺时针轮换一格，内部朝向不变'),('PCCW','■2','象限位置逆时针轮换一格，内部朝向不变'),('QCW','■3','每个象限各自顺时针转90°，象限位置不变'),('QCCW','■4','每个象限各自逆时针转90°，象限位置不变'),
 ('KCW','□1','四角小格各自顺时针转90°，格子位置不变'),('KCCW','□2','四角小格各自逆时针转90°，格子位置不变'),('DM','□3','全图关于左上至右下对角线镜像'),('DA','□4','全图关于右上至左下对角线镜像')]
SYMBOLS={n:s for n,s,t in NAMES};TEXT={n:t for n,s,t in NAMES}
RELATED=[['CW','CCW','R180','PCW','PCCW','QCW','QCCW','KCW','KCCW'],['LR','UD','SX','SY','DM','DA','MT','MB','ML','MR'],['IT','IB','IL','IR','IA'],['CL','CR','DL','DR','CT','CB','DT','DB']]
# 12 public rules per group, with neighbouring semantics present as lookup distractors.
BLUEPRINTS=[
 ('左右换位与整体镜像',['SX','LR','MT'],['SX','LR','UD','SY','CW','CCW','MT','MB','IT','IB','IL','IR']),
 ('上下换位与整体镜像',['SY','UD','ML'],['SY','UD','LR','SX','CW','CCW','ML','MR','IT','IB','IL','IR']),
 ('整体与象限内部旋转',['QCW','QCCW','R180'],['CW','CCW','R180','QCW','QCCW','PCW','PCCW','LR','UD','MT','IT','IR']),
 ('象限位置轮换',['PCW','PCCW','SX'],['PCW','PCCW','QCW','QCCW','SX','SY','CW','CCW','LR','UD','IT','IL']),
 ('位置轮换与内部旋转',['PCW','QCW','QCCW'],['PCW','PCCW','QCW','QCCW','CW','CCW','MT','MB','ML','MR','IT','IR']),
 ('角格与象限旋转',['KCW','KCCW','QCW'],['KCW','KCCW','QCW','QCCW','CW','CCW','MT','MB','LR','UD','IT','IB']),
 ('左半普通复制与镜像复制',['DL','CL','MT'],['DL','CL','DR','CR','CW','CCW','LR','UD','MT','MB','IT','IR']),
 ('右半普通复制与镜像复制',['DR','CR','MB'],['DR','CR','DL','CL','CW','CCW','LR','UD','MT','MB','IB','IL']),
 ('上半普通复制与镜像复制',['DT','CT','ML'],['DT','CT','DB','CB','CW','CCW','LR','UD','ML','MR','IT','IR']),
 ('下半普通复制与镜像复制',['DB','CB','MR'],['DB','CB','DT','CT','CW','CCW','LR','UD','ML','MR','IB','IL']),
 ('复制来源与覆盖方向',['CL','DR','CT'],['CL','CR','DL','DR','CT','CB','DT','DB','CW','CCW','IT','IR']),
 ('上半与下半局部镜像',['MT','MB','UD'],['MT','MB','LR','UD','SX','SY','CW','CCW','IT','IB','QCW','QCCW']),
 ('左半与右半局部镜像',['ML','MR','LR'],['ML','MR','LR','UD','SX','SY','CW','CCW','IL','IR','PCW','PCCW']),
 ('上下反色与操作时序',['IT','IB','IA'],['IT','IB','IL','IR','IA','CW','CCW','MT','MB','PCW','PCCW','KCW']),
 ('左右反色与作用范围',['IL','IR','IA'],['IL','IR','IT','IB','IA','CW','CCW','ML','MR','QCW','QCCW','KCCW']),
 ('对角线与水平竖直镜像',['DM','DA','LR'],['DM','DA','LR','UD','SX','SY','CW','CCW','MT','ML','IT','IR']),
 ('旋转后复制与反色',['CL','CT','CW'],['CL','CT','DL','DT','CW','CCW','R180','IT','IB','IL','IR','LR']),
 ('连续局部操作',['MT','ML','MR'],['MT','MB','ML','MR','IT','IB','IL','IR','CW','CCW','DM','DA']),
 ('角格转向与半区重建',['KCW','KCCW','CR'],['KCW','KCCW','CR','DR','CB','DB','QCW','QCCW','CW','CCW','IT','IR']),
 ('综合空间范围辨析',['DA','PCW','DL'],['DA','DM','PCW','PCCW','QCW','QCCW','DL','CL','DB','CB','IT','IR'])]
def rot(v,k=1):return sum(((v>>i)&1)<<((i+k)%4) for i in range(4))
def reflect(v,axis):
 p={'LR':[0,3,2,1],'UD':[2,1,0,3],'DM':[3,2,1,0],'DA':[1,0,3,2]}[axis]
 return sum(((v>>i)&1)<<p[i] for i in range(4))
def op(a,n):
 if n=='CW':return [[rot(a[3-c][r]) for c in range(4)] for r in range(4)]
 if n=='CCW':return [[rot(a[c][3-r],-1) for c in range(4)] for r in range(4)]
 if n=='R180':return op(op(a,'CW'),'CW')
 if n=='LR':return [[reflect(a[r][3-c],'LR') for c in range(4)] for r in range(4)]
 if n=='UD':return [[reflect(a[3-r][c],'UD') for c in range(4)] for r in range(4)]
 if n=='SX':return [[a[r][(c+2)%4] for c in range(4)] for r in range(4)]
 if n=='SY':return [[a[(r+2)%4][c] for c in range(4)] for r in range(4)]
 if n in ('IA','IT','IB','IL','IR'):
  return [[v^15 if (n=='IA' or n=='IT' and r<2 or n=='IB' and r>=2 or n=='IL' and c<2 or n=='IR' and c>=2) else v for c,v in enumerate(row)] for r,row in enumerate(a)]
 if n in ('MT','MB'):
  return [[reflect(a[r][3-c],'LR') if (r<2)==(n=='MT') else a[r][c] for c in range(4)] for r in range(4)]
 if n in ('ML','MR'):
  return [[reflect(a[3-r][c],'UD') if (c<2)==(n=='ML') else a[r][c] for c in range(4)] for r in range(4)]
 if n in ('CL','CR','DL','DR'):
  left=n in ('CL','DL');mirror=n.startswith('C')
  return [[a[r][c] if (c<2)==left else reflect(a[r][3-c],'LR') if mirror else a[r][(c+2)%4] for c in range(4)] for r in range(4)]
 if n in ('CT','CB','DT','DB'):
  top=n in ('CT','DT');mirror=n.startswith('C')
  return [[a[r][c] if (r<2)==top else reflect(a[3-r][c],'UD') if mirror else a[(r+2)%4][c] for c in range(4)] for r in range(4)]
 if n in ('PCW','PCCW','QCW','QCCW'):
  out=[[0]*4 for _ in range(4)]
  for r,c in itertools.product(range(4),repeat=2):
   br,bc=r//2,c//2;dr,dc=r%2,c%2
   if n=='PCW':nr,nc=bc*2+dr,(1-br)*2+dc;v=a[r][c]
   elif n=='PCCW':nr,nc=(1-bc)*2+dr,br*2+dc;v=a[r][c]
   elif n=='QCW':nr,nc=br*2+dc,bc*2+1-dr;v=rot(a[r][c])
   else:nr,nc=br*2+1-dc,bc*2+dr;v=rot(a[r][c],-1)
   out[nr][nc]=v
  return out
 if n in ('KCW','KCCW'):return [[rot(v,1 if n=='KCW' else -1) if r in (0,3) and c in (0,3) else v for c,v in enumerate(row)] for r,row in enumerate(a)]
 if n=='DM':return [[reflect(a[c][r],'DM') for c in range(4)] for r in range(4)]
 if n=='DA':return [[reflect(a[3-c][3-r],'DA') for c in range(4)] for r in range(4)]
 raise ValueError(n)
def key(a):return tuple(x for row in a for x in row)
def seq(a,names):
 states=[a]
 for n in names:states.append(op(states[-1],n))
 return states
def dist(a,b):return sum((x^y).bit_count() for x,y in zip(key(a),key(b)))
def counts(a):return [sum(v.bit_count() for v in key(a)),key(a).count(0),key(a).count(15),sum(v in (3,6,9,12) for v in key(a))]
def symmetry(a):return [op(a,n)==a for n in ('LR','UD','DM','DA','R180')]

# Independent fractional centroid geometry, no reuse of cell permutations.
OFF=[(F(1,2),F(1,6)),(F(5,6),F(1,2)),(F(1,2),F(5,6)),(F(1,6),F(1,2))]
UNIVERSE={(F(c)+x,F(r)+y) for r,c in itertools.product(range(4),repeat=2) for x,y in OFF}
def pts(a):return {(F(c)+x,F(r)+y) for r,c in itertools.product(range(4),repeat=2) for i,(x,y) in enumerate(OFF) if a[r][c]>>i&1}
def geom(p,n):
 if n in ('IA','IT','IB','IL','IR'):
  reg={z for z in UNIVERSE if n=='IA' or n=='IT' and z[1]<2 or n=='IB' and z[1]>=2 or n=='IL' and z[0]<2 or n=='IR' and z[0]>=2};return p^reg
 if n in ('CL','CR','DL','DR','CT','CB','DT','DB'):
  horiz=n[-1] in 'LR';low=n[-1] in 'LT'
  keep={z for z in p if (z[0 if horiz else 1]<2)==low}
  if n.startswith('C'):other={(4-x,y) if horiz else (x,4-y) for x,y in keep}
  else:other={(x+(2 if low else -2),y) if horiz else (x,y+(2 if low else -2)) for x,y in keep}
  return keep|other
 out=set()
 for x,y in p:
  if n=='CW':z=(4-y,x)
  elif n=='CCW':z=(y,4-x)
  elif n=='R180':z=(4-x,4-y)
  elif n=='LR':z=(4-x,y)
  elif n=='UD':z=(x,4-y)
  elif n=='SX':z=(x+2 if x<2 else x-2,y)
  elif n=='SY':z=(x,y+2 if y<2 else y-2)
  elif n=='MT':z=(4-x,y) if y<2 else (x,y)
  elif n=='MB':z=(4-x,y) if y>=2 else (x,y)
  elif n=='ML':z=(x,4-y) if x<2 else (x,y)
  elif n=='MR':z=(x,4-y) if x>=2 else (x,y)
  elif n in ('PCW','PCCW','QCW','QCCW'):
   bx,by=int(x//2),int(y//2);lx,ly=x-2*bx,y-2*by
   if n=='PCW':z=(2*(1-by)+lx,2*bx+ly)
   elif n=='PCCW':z=(2*by+lx,2*(1-bx)+ly)
   elif n=='QCW':z=(2*bx+2-ly,2*by+lx)
   else:z=(2*bx+ly,2*by+2-lx)
  elif n in ('KCW','KCCW'):
   cx,cy=int(x),int(y);lx,ly=x-cx,y-cy
   z=(cx+1-ly,cy+lx) if n=='KCW' else (cx+ly,cy+1-lx)
   if cx not in (0,3) or cy not in (0,3):z=(x,y)
  elif n=='DM':z=(y,x)
  elif n=='DA':z=(4-y,4-x)
  else:raise ValueError(n)
  out.add(z)
 return out

def source(rng):
 a=[[0]*4 for _ in range(4)]
 for br,bc in itertools.product((0,2),repeat=2):
  vals=[0,15,rng.choice((3,6,9,12)),rng.choice((3,6,9,12))];rng.shuffle(vals)
  for (r,c),v in zip(itertools.product(range(2),repeat=2),vals):a[br+r][bc+c]=v
 return a
def error_paths(chain,bank):
 out=[]
 for i,n in enumerate(chain):
  rel=next(x for x in RELATED if n in x)
  for other in bank:
   if other==n or other not in rel:continue
   ns=chain[:];ns[i]=other
   out.append((ns,f'第{i+1}步应为“{TEXT[n]}”，却误作“{TEXT[other]}”','替换'+str(i)))
 for i in (0,1):
  ns=chain[:];ns[i],ns[i+1]=ns[i+1],ns[i]
  out.append((ns,f'将第{i+1}步与第{i+2}步的先后顺序颠倒','错序'+str(i)))
 return out
def generate():
 rng=random.Random(2026102760);answers=list('ABCD')*15;rng.shuffle(answers)
 groups=[];seen_sources=set();seen_chains=set();used=collections.Counter()
 # Nonconstant test grids disallow chains that collapse globally to a single operation.
 probes=[source(random.Random(800+i)) for i in range(3)]
 singles={tuple(key(op(a,n)) for a in probes) for n in SYMBOLS}|{tuple(key(a) for a in probes)}
 for gi,(theme,focus,bank) in enumerate(BLUEPRINTS,1):
  questions=[]
  for local in range(3):
   for attempt in range(15000):
    required=focus[local]
    others=rng.sample([n for n in bank if n!=required],2)
    chain=others+[required];rng.shuffle(chain)
    if tuple(chain) in seen_chains:continue
    if tuple(key(seq(a,chain)[-1]) for a in probes) in singles:continue
    a=source(rng)
    if key(a) in seen_sources:continue
    states=seq(a,chain);good=states[-1]
    if any(states[i]==states[i+1] for i in range(3)):continue
    if any(seq(a,chain[:i]+chain[i+1:])[-1]==good for i in range(3)):continue
    candidates={}
    for ns,reason,kind in error_paths(chain,bank):
     bad=seq(a,ns)[-1];delta=dist(good,bad)
     if 4<=delta<=48 and counts(bad)==counts(good):
      k=key(bad)
      rank=(delta,0 if kind.startswith('错序') else 1)
      if k not in candidates or rank<candidates[k]['rank']:candidates[k]={'image':bad,'seq':ns,'reason':reason,'kind':kind,'rank':rank,'distance':delta,'same_symmetry':symmetry(bad)==symmetry(good)}
    errors=sorted(candidates.values(),key=lambda e:e['rank'])
    if len(errors)<3:continue
    close=[e for e in errors if e['distance']<=24 and e['same_symmetry']]
    order=[e for e in errors if e['kind'].startswith('错序')]
    if not close or not order:continue
    chosen=[close[0]]
    if key(order[0]['image'])!=key(chosen[0]['image']):chosen.append(order[0])
    for e in errors:
     if len(chosen)==3:break
     if key(e['image']) in {key(v['image']) for v in chosen}:continue
     if e['kind'] in {v['kind'] for v in chosen} and any(x['kind'] not in {v['kind'] for v in chosen} for x in errors):continue
     chosen.append(e)
    if len(chosen)<3:continue
    break
   else:raise AssertionError(f'cannot generate group{gi} item{local+1}')
   n=(gi-1)*3+local+1;ans=answers[n-1];rng.shuffle(chosen);pos='ABCD'.index(ans)
   candidates=[dict(image=good,seq=chain,reason='严格按规则从左至右执行三步',kind='正确',distance=0) if i==pos else chosen.pop(0) for i in range(4)]
   q={'n':n,'group':gi,'local':local+1,'source':a,'seq':chain,'answer':ans,'states':states,
    'options':[e['image'] for e in candidates],
    'option_explanations':[dict(letter=l,correct=l==ans,seq=e['seq'],reason=e['reason'],kind=e['kind'],distance=e['distance']) for l,e in zip('ABCD',candidates)]}
   questions.append(q);seen_chains.add(tuple(chain));seen_sources.add(key(a));used.update(chain)
  groups.append({'group':gi,'theme':theme,'rules':bank,'questions':questions})
 assert len(used)==32,(len(used),set(SYMBOLS)-set(used))
 return groups
def verify(groups):
 # 32 operators on each of 64 individual sectors, also empty and full images.
 primitive=0
 for n in SYMBOLS:
  for r,c,i in itertools.product(range(4),range(4),range(4)):
   a=[[0]*4 for _ in range(4)];a[r][c]=1<<i
   assert pts(op(a,n))==geom(pts(a),n),(n,r,c,i);primitive+=1
  for v in (0,15):
   a=[[v]*4 for _ in range(4)];assert pts(op(a,n))==geom(pts(a),n)
 reports=[];use=collections.Counter();answers=collections.Counter()
 for g in groups:
  assert len(g['rules'])==12 and len(set(g['rules']))==12
  for q in g['questions']:
   p=pts(q['source'])
   for n,a in zip(q['seq'],q['states'][1:]):p=geom(p,n);assert p==pts(a)
   good=q['states'][-1]
   validity=[b==good for b in q['options']]
   assert sum(validity)==1 and 'ABCD'[validity.index(True)]==q['answer']
   assert all(n in g['rules'] for n in q['seq'])
   assert len({key(b) for b in q['options']})==4
   for i in range(3):assert seq(q['source'],q['seq'][:i]+q['seq'][i+1:])[-1]!=good
   for e,b in zip(q['option_explanations'],q['options']):
    p=pts(q['source'])
    for n in e['seq']:p=geom(p,n)
    assert p==pts(b)
   assert all(counts(b)==[32,4,4,8] for b in q['options'])
   wrong=[b for b in q['options'] if b!=good]
   assert any(dist(good,b)<=24 and symmetry(b)==symmetry(good) for b in wrong)
   reports.append({'n':q['n'],'group':g['group'],'answer':q['answer'],'unique':True,'all_steps_essential':True,
    'distances':[dist(good,b) for b in q['options']],'all_candidate_counts':[32,4,4,8],
    'same_symmetry_wrong_count':sum(symmetry(b)==symmetry(good) for b in wrong)})
   use.update(q['seq']);answers[q['answer']]+=1
 assert dict(answers)==dict.fromkeys('ABCD',15),answers
 return {'passed':True,'groups':20,'questions':60,'rules_per_group':12,'operation_types':32,'primitive_sector_checks':primitive,'operation_usage':dict(use),'answer_distribution':dict(answers),'items':reports,
  'scope':'离散扇区与独立分数坐标几何交叉计算；输入与操作链不重复；每步必要；候选唯一；真实PNG及独立盲解另验。'}
def main():
 groups=generate();(ROOT/'questions.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'verification.json').write_text(json.dumps(verify(groups),ensure_ascii=False,indent=2),encoding='utf-8')
 public={'instructions':'每组独立，三问共用该组12项规则。按从左至右顺序，每步作用于上一步结果，上下左右以当前图为准。符号右侧数字是标识的一部分，含义全卷一致。象限为4×4图中四个2×2区域；四角小格为整图的四个最外角单元。镜像改变格内朝向；平移复制保持朝向。',
  'rules':[{'id':n,'symbol':s,'definition':t} for n,s,t in NAMES],
  'groups':[{'group':g['group'],'rules':g['rules'],'items':[{'n':q['n'],'seq':q['seq'],'image':str(ROOT/'assets'/f'question-{q["n"]:02}.png')} for q in g['questions']]} for g in groups]}
 (ROOT/'public_rules_and_questions.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'passed':True,'groups':20,'questions':60,'operation_usage':verify(groups)['operation_usage']},ensure_ascii=False))
if __name__=='__main__':main()
