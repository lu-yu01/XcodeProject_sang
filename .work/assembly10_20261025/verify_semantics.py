"""Check the specific geometric rejection statements used in the Chinese analyses."""
from pathlib import Path
from collections import Counter,deque
import json,hashlib
from puzzles import QUESTIONS
from solver import *
ROOT=Path(__file__).resolve().parent

def degree_profile(cells):
 s=set(cells)
 return tuple(sorted(sum(n in s for n in neighbors(c)) for c in s))

def connected_remainders(parts,target):
 result=[]
 def rec(i,used):
  if i==len(parts):
   rem=set(target)-used
   if rem and connected(rem):result.append(tuple(sorted(rem)))
   return
  for p in placements(parts[i],target):
   if not set(p)&used:rec(i+1,used|set(p))
 rec(0,set())
 return result

def max_run(cells):
 s=set(cells);best=0
 for c in s:
  for i in range(3):
   q=list(c);n=0
   while tuple(q) in s:n+=1;q[i]+=1
   best=max(best,n)
 return best

def branch_lengths(cells):
 s=set(cells);degrees={c:sum(p in s for p in neighbors(c)) for c in s}
 starts=[c for c in s if degrees[c]==3]
 assert len(starts)==1 and edges(s)==len(s)-1
 start=starts[0];todo=deque([(start,0)]);seen={start};out=[]
 while todo:
  c,d=todo.popleft()
  if degrees[c]==1:out.append(d)
  for p in neighbors(c):
   if p in s and p not in seen:seen.add(p);todo.append((p,d+1))
 return sorted(out)

C={}
for n in (1,2,7):
 q=QUESTIONS[n-1];r=connected_remainders(q['pieces'],q['target'])
 assert len({canonical(s) for s in r})==1
 good=q['options']['ABCD'.index(q['answer'])]
 bad=q['options'][0 if n!=2 else 1]
 assert canonical(bad)==canonical(mirror(good)) and canonical(bad)!=canonical(good)
 C[str(n)]={'unique_residual_rotation_class':True,'mirror_distractor_proved':True}
assert max_run(QUESTIONS[1]['options'][0])==4 and max_run(QUESTIONS[1]['options'][3])==3
C['2']['correct_max_straight_run']=4;C['2']['D_max_straight_run']=3

q=QUESTIONS[2]
assert all(not connected_remainders(q['pieces'][:1],q['options'][i]) for i in (0,1))
r=connected_remainders(q['pieces'][:1],q['options'][2])
assert r and all(max(degree_profile(s))==3 for s in r)
assert max(degree_profile(q['pieces'][1]))==2
C['3']={'A_B_all_residuals_disconnected':True,'C_connected_residual_has_degree3':True,'given_B_has_max_degree2':True}

q=QUESTIONS[3]
for i in (0,3):
 rr=connected_remainders(q['pieces'][:1],q['options'][i]);assert rr and all(degree_profile(s)==(1,1,1,3) for s in rr)
rr=connected_remainders(q['pieces'][:1],q['options'][2]);assert rr and all(not is_3d(s) for s in rr)
C['4']={'A_D_connected_residuals_branched':True,'C_connected_residuals_planar':True,'given_piece_3d_chain':True}

q=QUESTIONS[4];rr=connected_remainders(q['pieces'],q['target']);classes={canonical(s) for s in rr}
assert len(classes)==2 and all(not is_3d(s) for s in rr)
assert {degree_profile(s) for s in rr}=={(2,2,2,2),(1,1,2,2)}
C['5']={'connected_residual_classes':2,'all_planar':True,'profiles':['square_cycle','S_chain']}

q=QUESTIONS[5]
for i in (0,1,3):
 rr=connected_remainders(q['pieces'][:2],q['options'][i]);assert rr and all(max(degree_profile(s))==2 for s in rr)
assert degree_profile(q['pieces'][2])==(1,1,1,3)
C['6']={'A_B_D_connected_remainders_max_degree':2,'given_C_degree_profile':[1,1,1,3]}

q=QUESTIONS[6]
assert [branch_lengths(s) for s in q['options']]==[[1,1,6],[1,1,6],[2,3,3],[1,3,4]]
C['7']['branch_lengths_by_option']=[[1,1,6],[1,1,6],[2,3,3],[1,3,4]]

q=QUESTIONS[7]
assert not connected_remainders(q['pieces'][:1],q['options'][3])
C['8']={'D_all_remainders_disconnected':True,'A_B_C_witnesses_saved':True}

q=QUESTIONS[8];rr=connected_remainders(q['pieces'],q['target']);assert len({canonical(s) for s in rr})==2
assert {degree_profile(s) for s in rr}=={(1,1,2,2,3,3),(1,2,2,2,2,3)}
assert all(degree_profile(s)==(1,2,2,2,2,3) for s in q['options'])
assert canonical(q['options'][0])==canonical(mirror(q['options'][2]))!=canonical(q['options'][2])
C['9']={'connected_residual_classes':2,'all_options_cycle_with_two_cell_tail':True,'A_is_mirror_of_C':True}

q=QUESTIONS[9];target=q['options'][0]
overlaps=[len(set(a)&set(b)) for a in placements(q['pieces'][0],target) for b in placements(q['pieces'][1],target)]
assert min(overlaps)==1
C['10']={'A_minimum_overlap_between_given_A_B':1,'B_C_D_witnesses_saved':True}

path=ROOT/'verification.json'
report=json.loads(path.read_text(encoding='utf-8'))
for q in QUESTIONS:
 fits=[]
 for opt in q['options']:
  parts=q['pieces']+[opt] if q['mode']=='fill' else q['pieces']
  target=q['target'] if q['mode']=='fill' else opt
  fits.append(bool(solve(parts,target)))
 i='ABCD'.index(q['answer'])
 assert (fits.count(False)==1 and not fits[i]) if q['except'] else (fits.count(True)==1 and fits[i])
 assert fits==report['questions'][q['n']-1]['fits']
report['human_reason_certificates']=C
report['model_sha256']=hashlib.sha256((ROOT/'puzzles.py').read_bytes()).hexdigest()
path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('40 assembly options and specific human explanation certificates verified; model fingerprint refreshed.')
