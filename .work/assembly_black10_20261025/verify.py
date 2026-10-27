"""Re-solve all forty coloured and shape-only choices; never edits puzzles.py."""
from pathlib import Path
from datetime import datetime
from collections import Counter
import json,hashlib
from puzzles import QUESTIONS
from solver import *
ROOT=Path(__file__).resolve().parent

def rooted_signature(part):
 s=set(part['cells']);b=part['black'][0];ds={b:0};todo=[b]
 for c in todo:
  for q in neighbors(c):
   if q in s and q not in ds:ds[q]=ds[c]+1;todo.append(q)
 return (sum(q in s for q in neighbors(b)),tuple(sorted(ds.values())))

def degree_profile(part):
 s=set(part['cells']);return tuple(sorted(sum(n in s for n in neighbors(c)) for c in s))

def residuals(known,target):
 ts=set(target['cells']);tb=set(target['black']);out=[];partial=0
 for a in placements(known[0],target):
  for b in placements(known[1],target):
   if set(a['cells'])&set(b['cells']):continue
   partial+=1;cs=ts-set(a['cells'])-set(b['cells']);bs=tb-set(a['black'])-set(b['black'])
   if connected(cs):out.append(normalize({'cells':tuple(cs),'black':tuple(bs)}))
 return partial,out

reports=[]
for q in QUESTIONS:
 t=q['target'];assert len(t['black'])==3 and len(q['pieces'])==2 and len(q['options'])==4
 assert min(dims(t['cells']))>1 and connected(t['cells'])
 assert 12<=len(t['cells'])<=24
 assert len({len(p['cells']) for p in q['options']})==1
 assert all(len(p['black'])==1 and set(p['black'])<=set(p['cells']) and connected(p['cells']) for p in q['pieces']+q['options'])
 assert all(any(nb not in set(p['cells']) for nb in neighbors(p['black'][0])) for p in q['pieces']+q['options'])
 assert all(any(nb not in set(t['cells']) for nb in neighbors(b)) for b in t['black'])
 assert len({canonical(p) for p in q['options']})==4
 fits=[];shape_fits=[];option_reports=[]
 ai='ABCD'.index(q['answer']);good=q['options'][ai]
 for letter,p in zip('ABCD',q['options']):
  parts=q['pieces']+[p]
  cs=solve(parts,t,True);ss=solve(parts,t,False)
  fits.append(bool(cs));shape_fits.append(bool(ss))
  if cs:
   sol=cs[0]
   assert all(canonical(src)==canonical(dst) for src,dst in zip(parts,sol))
   assert set().union(*(set(x['cells']) for x in sol))==set(t['cells'])
   assert set().union(*(set(x['black']) for x in sol))==set(t['black'])
   assert sum(len(x['cells']) for x in sol)==len(t['cells'])
   assert all(set(x['cells'])&set(t['black'])==set(x['black']) for x in sol)
  option_reports.append({'option':letter,'coloured_fits':bool(cs),'shape_only_fits':bool(ss),'same_shape_as_correct':canonical(p,False)==canonical(good,False),'black_rooted_signature':rooted_signature(p),'degree_profile':degree_profile(p),'colored_placement_count':len(placements(p,t)),'colored_witness':cs[0] if cs else None,'shape_only_witness':ss[0] if ss else None})
 assert fits.count(True)==1 and fits[ai]
 same_shape_wrong=[i for i,p in enumerate(q['options']) if i!=ai and canonical(p,False)==canonical(good,False) and not fits[i] and shape_fits[i]]
 assert same_shape_wrong
 assert sum(len(p['cells']) for p in q['pieces'])+len(good['cells'])==len(t['cells'])
 assert len(q['solution'])==3
 assert all(canonical(src)==canonical(dst) for src,dst in zip(q['pieces']+[good],q['solution']))
 assert set().union(*(set(p['black']) for p in q['solution']))==set(t['black'])
 assert set().union(*(set(p['cells']) for p in q['solution']))==set(t['cells'])
 pc,rr=residuals(q['pieces'],t)
 assert rr
 reports.append({'n':q['n'],'answer':q['answer'],'fits':fits,'shape_only_fits':shape_fits,'same_shape_color_wrong_options':['ABCD'[i] for i in same_shape_wrong],'same_shape_wrong_black_signatures':[rooted_signature(q['options'][i]) for i in same_shape_wrong],'correct_black_signature':rooted_signature(good),'given_color_placement_counts':[len(placements(p,t)) for p in q['pieces']],'nonoverlapping_given_pairs':pc,'connected_residual_colored_classes':len({canonical(p) for p in rr}),'connected_residual_geometric_classes':len({canonical(p,False) for p in rr}),'options':option_reports})

for n in (7,9,10):
 q=QUESTIONS[n-1];ai='ABCD'.index(q['answer']);wi='ABCD'.index(q['same_shape_distractor'])
 assert rooted_signature(q['options'][ai])==rooted_signature(q['options'][wi])
q=QUESTIONS[7];assert rooted_signature(q['options'][3])[0]==rooted_signature(q['options'][0])[0]==2
assert all(q['analysis'] for q in QUESTIONS)
report={'status':'passed','time':datetime.now().astimezone().isoformat(),'question_count':10,'rotation_count':24,'colored_option_checks':40,'shape_only_option_checks':40,'exactly_three_parts_every_question':True,'target_three_black_every_question':True,'one_black_per_given_and_option':True,'at_least_one_same_shape_color_wrong_each_question':True,'hard_7_9_10_same_black_degree_and_distance_distribution':True,'all_black_cubes_on_surface':True,'answer_distribution':dict(Counter(q['answer'] for q in QUESTIONS)),'model_sha256':hashlib.sha256((ROOT/'puzzles.py').read_bytes()).hexdigest(),'solver_sha256':hashlib.sha256((ROOT/'solver.py').read_bytes()).hexdigest(),'scope':'Proper rotations and integer translations only, exact whole-target coverage, no overlap, colored black-white agreement and shape-only contrast; visual visibility is checked separately; difficulty estimates are not trial results.','questions':reports}
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('PASS: 10 unique answers; all 40 colored and 40 shape-only choices checked; color-sensitive distractor in every item.')
