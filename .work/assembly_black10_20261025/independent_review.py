"""Independent colour-preserving assembly audit using quarter-turn closure."""
from pathlib import Path
from itertools import product
import hashlib,json
from puzzles import QUESTIONS

ROOT=Path(__file__).resolve().parent
REVIEWED_PUZZLES_SHA256='b78a7a214ef98bf7386f12cdbf2a47b74353cf632e9b8dfb2e502fa30fbb71e0'

def normalize(part):
    cells=tuple(map(tuple,part['cells']));lo=tuple(min(p[i] for p in cells) for i in range(3))
    move=lambda p:tuple(p[i]-lo[i] for i in range(3))
    return (tuple(sorted(map(move,cells))),tuple(sorted(map(move,part['black']))))

def mx(p):x,y,z=p;return (x,-z,y)
def my(p):x,y,z=p;return (z,y,-x)

def rotations(part):
    start=normalize(part);seen={start};todo=[start]
    while todo:
        state=todo.pop()
        for turn in (mx,my):
            new=normalize({'cells':[turn(p) for p in state[0]],'black':[turn(p) for p in state[1]]})
            if new not in seen:seen.add(new);todo.append(new)
    return seen

def canonical(part):return min(rotations(part))

def connected(cells):
    s=set(map(tuple,cells));todo=[next(iter(s))];seen=set(todo)
    while todo:
        p=todo.pop()
        for i in range(3):
            for d in (-1,1):
                q=list(p);q[i]+=d;q=tuple(q)
                if q in s and q not in seen:seen.add(q);todo.append(q)
    return len(seen)==len(s)

def placements(part,target,colours=True):
    ts=set(map(tuple,target['cells']));tb=set(map(tuple,target['black']));out=set()
    for cells,black in rotations(part):
        anchor=cells[0]
        for tc in ts:
            offset=tuple(tc[i]-anchor[i] for i in range(3))
            move=lambda p:tuple(p[i]+offset[i] for i in range(3))
            moved=frozenset(map(move,cells));mb=frozenset(map(move,black))
            if moved<=ts and (not colours or moved&tb==mb):out.add((moved,mb))
    return out

def solve_independent(parts,target,colours=True):
    ts=frozenset(map(tuple,target['cells']))
    if sum(len(p['cells']) for p in parts)!=len(ts):return False
    poses=[list(placements(p,target,colours)) for p in parts]
    order=sorted(range(len(parts)),key=lambda i:len(poses[i]))
    def search(k,remaining):
        if k==len(parts):return not remaining
        for cells,_ in poses[order[k]]:
            if cells<=remaining and search(k+1,remaining-cells):return True
        return False
    return search(0,ts)

def ray_hits(pt,direction,cell):
    lo,hi=.00001,1e9
    for i in range(3):
        a=(cell[i]-pt[i])/direction[i];b=(cell[i]+1-pt[i])/direction[i]
        lo=max(lo,min(a,b));hi=min(hi,max(a,b))
    return hi>lo+1e-8

def visible_cells(cells,directions):
    cells=set(map(tuple,cells));visible=set()
    for p in cells:
        for direction in directions:
            for axis in range(3):
                sign=direction[axis]
                other=tuple(p[i]+(sign if i==axis else 0) for i in range(3))
                if other in cells:continue
                free=[i for i in range(3) if i!=axis]
                for u,v in product((.1,.3,.5,.7,.9),repeat=2):
                    pt=[p[i]+.5 for i in range(3)];pt[axis]=p[axis]+(1 if sign>0 else 0)
                    pt[free[0]]=p[free[0]]+u;pt[free[1]]=p[free[1]]+v
                    if not any(ray_hits(pt,direction,c) for c in cells if c!=p):visible.add(p);break
                if p in visible:break
            if p in visible:break
    return visible

def visual_audit(part,target=False):
    # Only use the renderer's chosen displayed pose, not its visibility calculation.
    from draw import choose_pose
    shown,_=choose_pose(part,target)
    cells=set(shown['cells']);black=set(shown['black'])
    directions=((1,1,1),(-1,-1,1)) if target else ((1,1,1),)
    visible=visible_cells(cells,directions)
    hidden=sorted(cells-visible)
    bounds=[max(p[i] for p in cells)+1 for i in range(3)]
    empty_hidden=[p for p in product(*(range(n) for n in bounds)) if p not in cells and p not in visible_cells(cells|{p},directions)]
    return {'black_all_visible':black<=visible,'hidden_occupied_cells':hidden,'hidden_empty_cells':empty_hidden,
            'rendered_pose_cells':sorted(cells),'rendered_pose_black':sorted(black),
            'count_labels_sufficient_for_occlusion':not hidden or not empty_hidden}

def main():
    assert len(rotations({'cells':[(0,0,0),(1,0,0),(0,2,0),(0,0,3)],'black':[(0,0,0)]}))==24
    results=[];risks=[]
    for q in QUESTIONS:
        target=q['target'];pieces=q['pieces'];options=q['options'];n=q['n']
        assert len(pieces)==2 and len(options)==4
        assert len(target['black'])==3
        assert all(len(p['black'])==1 and set(p['black'])<=set(p['cells']) for p in pieces+options)
        assert set(target['black'])<=set(target['cells'])
        assert all(connected(p['cells']) for p in [target]+pieces+options)
        assert len({len(p['cells']) for p in options})==1
        assert len({canonical(p) for p in options})==4
        coloured=[solve_independent(pieces+[p],target,True) for p in options]
        plain=[solve_independent(pieces+[p],target,False) for p in options]
        assert sum(coloured)==1 and 'ABCD'[coloured.index(True)]==q['answer'],(n,coloured,q['answer'])
        traps=['ABCD'[i] for i in range(4) if plain[i] and not coloured[i]]
        assert traps,(n,'no geometry-valid colour trap')
        chosen=pieces+[options['ABCD'.index(q['answer'])]]
        assert len(q['solution'])==3
        assert all(canonical(p)==canonical(s) for p,s in zip(chosen,q['solution'])),(n,'witness not colour-preserving rigid copy')
        ss=[set(map(tuple,s['cells'])) for s in q['solution']]
        bb=[set(map(tuple,s['black'])) for s in q['solution']]
        assert sum(map(len,ss))==len(set.union(*ss))==len(target['cells'])
        assert set.union(*ss)==set(target['cells'])
        assert set.union(*bb)==set(target['black'])
        assert all(s&set(target['black'])==b for s,b in zip(ss,bb)),(n,'white occupying black target')
        visuals=[]
        for label,part in [('target',target)]+[(f'given{i+1}',p) for i,p in enumerate(pieces)]+list(zip('ABCD',options)):
            v=visual_audit(part,label=='target');v['shape']=label;visuals.append(v)
            if not v['black_all_visible'] or not v['count_labels_sufficient_for_occlusion']:risks.append({'n':n,**v})
        results.append({'n':n,'colour_solvable':dict(zip('ABCD',coloured)),'geometry_solvable':dict(zip('ABCD',plain)),
                        'answer':q['answer'],'geometry_valid_colour_wrong_options':traps,'black_counts':{'target':3,'each_part_and_option':1},
                        'coloured_witness_verified':True,'options_equal_volume':True,'visuals':visuals})
    digest=hashlib.sha256((ROOT/'puzzles.py').read_bytes()).hexdigest()
    semantic_review=digest==REVIEWED_PUZZLES_SHA256 and all(len(q['analysis'])==2 for q in QUESTIONS)
    report={'passed_math':True,'method':'Independent quarter-turn closure, anchor translations and recursive exact coverage with strict white/black correspondence',
            'puzzles_sha256':digest,'questions':results,'unresolved_visual_risks':risks,
            'passed_display_geometry':not risks,'passed_semantics':semantic_review,'analysis_review_status':'passed' if semantic_review else 'requires renewed manual review',
            'semantic_review_observations':[
                '逐题读完最终10题各两段解析；外形可拼但颜色错的选项与独立求解表一致。',
                '独立核对第1至6题黑格邻格数、端格、分岔、方片闭环与镜像描述，未发现错误。',
                '第7、9、10题同形换黑干扰的黑格度数及连接距离分布与正确项相同，确需比较空间位置；第8题正确黑格距链端为1和4，A为2和3。',
                '第9题正确黑格在两方片共用棱端点，A在接短尾角；第10题正确黑端格沿两三岔格连线延长，B位于垂直支枝。',
                '第8B、第9B、第10C的几何确与正确外形互为不可旋转重合的镜像。',
                '目标展示仅绕竖轴选择观察角度；第6题三层说明明确按解析图方向观察。'
            ] if semantic_review else []}
    (ROOT/'independent_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed_math':True,'passed_display_geometry':not risks,'visual_risks':risks,
                      'answers':[q['answer'] for q in QUESTIONS],'traps':[r['geometry_valid_colour_wrong_options'] for r in results]},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
