from pathlib import Path
import json,pprint,hashlib
from datetime import datetime
from puzzles import QUESTIONS
from solver import *
ROOT=Path(__file__).resolve().parent

ANALYSES={
1:[
'答案为C。甲中的连续三格长臂必须沿长方体的3格方向放置；把甲转入目标后，空缺形状在整体旋转意义下只有一种，不能只凭六块体积相等判断。',
'可先在缺块中找出2×2方片，再看方片外的两格：两格分别接在相邻角，其中一格沿方片平面向外延伸，另一格垂直方片伸出；平面内延长方向平行于这两个相邻角的连线。C满足其位置与左右顺序。',
'A与所需缺块互为镜像，只旋转不能重合；B的两根短枝接在方片的对角位置；D虽然也接在相邻角，但平面内延长方向与两角连线垂直。三项均不能填满缺口。解析分层图给出甲与C的完整无重叠拼法。'],
2:[
'答案为A。甲含一条连续四格直臂，只能沿目标4格长边放置。其余凸格也必须随甲一起旋转，不能分别移动。由此确定的八格空缺可由A补齐，分层图给出一组完整拼法。',
'B与所需缺块互为镜像，端部偏出的短枝左右顺序不对。A中分别与四格、三格面相邻的两个分岔格直接相邻；C中这两个分岔格之间隔了一格，其连接关系不能靠旋转改变。D的任一直线上最多只有三格，缺少空缺要求的连续四格长臂。'],
3:[
'答案为D。甲是带一处分岔的六格部件，乙是没有分岔的六格折链。先辨认甲的三格长臂及两端凸格，再看放入候选立体后留下的六格是否能连成乙。',
'A、B中，甲无论怎样完整放入，剩余六格都会分裂成不相连的部分，不能由不可拆开的乙填入。C中甲只有一种可放位置，余部虽连通，却有一格同时连接另外三格；乙没有这一分岔。D中可以使甲、乙分别占据分层图所标的区域，两部件均保持原形并恰好拼满。'],
4:[
'答案为B。两个部件形状相同，都是三段依次沿三个互相垂直方向转折的四格折链。不能把其中一件变成平面的L形，也不能改成一格带三个分支的形状。',
'B可按解析分层图分成两个与原部件旋转同形的四格折链。A、D中放入第一件后，若剩余四格连通，余部只能形成一格连接三格的分岔形；C中连通余部只能形成平面L形。它们均不等于第二个空间折链，所以不能拼成。'],
5:[
'答案为A。两个已给部件都是四格L形，三格长臂必须沿目标的3格方向摆放，再比较两条短臂占据的宽、高位置。虽然每件本身可平放，本题需要将它们立起并与第三件拼成两层立体。',
'当两个L形不重叠地放入3×2×2长方体，且剩下四格仍连通时，余部在整体旋转意义下只可能是2×2方片，或平面的S形错位折片。四个选项中只有A是上述一种；B、C是空间折链，D是L形，均不是可用余部。分层图所示拼法中，两L形各占一个竖向截面，A填入剩余方片。'],
6:[
'答案为C。甲、乙是一对转折方向相反的四格空间折链；丙则是一格分别沿三个互相垂直方向连接另外三格的分岔部件。三件须同时保持原形，不能只检查某两件局部吻合。',
'C能按分层图分成甲、乙、丙三件，既无重叠也无缺格。A、B、D中，甲、乙不重叠放入后，若剩余四格连通，余部均只能是折链或2×2方片，没有丙所需的一格连三格分岔结构；其余摆法的余部不连通。因此这三项都不能由全部部件拼成。'],
7:[
'答案为B。已给九格部件在3×3×2目标内放好后，连通空缺只有一种旋转同形的形状。该缺块是一棵无环的分岔折链，从唯一的三岔格走向三个端格，分别经过1、1、6次面相接。',
'B既符合上述三条分支长度，也符合长分支转折的左右顺序。A是B的镜像，体块数与连接图虽相同，仍不能经旋转重合；C的三条分支长度为2、3、3，D为1、3、4，均改变了固定的连接结构。分层图给出B填满目标的具体位置。'],
8:[
'答案为D，本题选不能拼成的一项。甲、乙各有六格；四个候选都是十二格，单纯数体块无法排除。应先用甲的三格直臂和侧面凸格定位，再核对余部能否保持乙的完整形状。',
'A、B、C均存在甲、乙不重叠且覆盖全部体块的拼法，解析辅助图展示A的一种构造。D中甲虽然能单独放入，但每一种完整放法都会把剩余六格分成不相连的部分；乙是连通且不可拆的部件，故不可能补齐。不能把“某部件单独能放进去”误当成“两个部件能同时拼成”。'],
9:[
'答案为C。甲、乙各六格，需再选六格部件拼满3×3×2目标。先同时安排两件的长臂与侧面凸格，不能只在目标中为其中一件找到位置。',
'甲、乙不重叠放入后，连通余部在旋转意义下只有两类：一类有两个三岔格，另一类由2×2方片接一条两格短尾构成。四个选项都属于后一连接类型，所以还要比较短尾如何从方片伸出。',
'C的短尾先沿方片平面伸出，再垂直方片转折，且左右顺序与空缺相符。A是C的镜像；B的两格尾部排成直线；D先垂直方片伸出、再向平面方向转折。三个近似项都不能填入实际空缺。分层图显示甲、乙和C恰好覆盖全部十八格。'],
10:[
'答案为A，本题选不能拼成的一项。甲是2×3方片去掉一角的五格部件；乙含一条三格长臂及空间凸格；丙含2×2方片及一格凸起。三个五格部件必须同时进入候选形状。',
'A中甲、乙各自都可以单独放入，但沿所有允许方向摆放时，两件总会争占至少一个单位格，无法同时安放；即使暂不考虑丙，已经不能成立。这一干扰专门利用“各自能放入”与“能同时无重叠放入”的区别。',
'B、C、D均能完整放入三个部件，解析辅助图展示B的一种分层构造。拼合时先辨认甲的缺角方片和乙的三格臂，再让丙补齐余下五格；不能为了贴合外轮廓而拆开部件或移动单个凸格。']}

reports=[]
for q in QUESTIONS:
 q['analysis']=ANALYSES[q['n']]
 assert all(connected(p) for p in q['pieces']+q['options'])
 assert len(set(map(len,q['options'])))==1
 assert len({canonical(p) for p in q['options']})==4
 fits=[];optsols=[];certs=[]
 for letter,opt in zip('ABCD',q['options']):
  parts=q['pieces']+[opt] if q['mode']=='fill' else q['pieces']
  target=q['target'] if q['mode']=='fill' else opt
  sols=solve(parts,target,limit=1)
  fit=bool(sols);fits.append(fit);optsols.append(sols[0] if sols else None)
  if fit:
   assert len(set().union(*map(set,sols[0])))==len(target)
   assert set().union(*map(set,sols[0]))==set(target)
   assert all(canonical(a)==canonical(b) for a,b in zip(parts,sols[0]))
   assert sum(map(len,sols[0]))==len(target)
  certs.append({'option':letter,'fits':fit,'piece_placement_counts':[len(placements(p,target)) for p in parts], 'witness':sols[0] if sols else None})
 answer_index='ABCD'.index(q['answer'])
 if q['except']:
  assert fits.count(False)==1 and not fits[answer_index]
  assert q['solution_for']!='ABCD'[answer_index]
 else:assert fits.count(True)==1 and fits[answer_index]
 q['option_solutions']=optsols
 if not q['except']:q['solution_for']=q['answer']
 reports.append({'n':q['n'],'mode':q['mode'],'except':q['except'],'answer':q['answer'],'fits':fits,'options':certs,'true_3d_targets': all(min(dims(o))>1 for o in q['options']) if q['mode']=='assemble' else min(dims(q['target']))>1,'same_option_volume':True,'same_option_box_dimensions':len({tuple(sorted(dims(o))) for o in q['options']})==1})

out=ROOT/'puzzles.py'
out.write_text('"""Original spatial assembly models; integer cells, proper rotations only."""\nQUESTIONS = '+pprint.pformat(QUESTIONS,width=120,sort_dicts=False)+'\n',encoding='utf-8')
report={'status':'passed','time':datetime.now().astimezone().isoformat(),'rotation_count':len(ROTATIONS),'question_count':len(QUESTIONS),'option_count':40,'answer_distribution':dict((l,sum(q['answer']==l for q in QUESTIONS)) for l in 'ABCD'),'model_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scope':'24 proper rotations and all integer translations in each target; exact cover, no overlap, all pieces used, no reflections; not learner difficulty validation','questions':reports}
(ROOT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('All 10 models verified, unique choices and constructive witnesses saved.')
