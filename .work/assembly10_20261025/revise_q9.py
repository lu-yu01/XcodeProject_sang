from pathlib import Path
import pprint
from puzzles import QUESTIONS
ns={'__file__':str(Path(__file__).with_name('generate.py'))}
exec(Path(__file__).with_name('generate.py').read_text(encoding='utf-8').split('Q=[]')[0],ns)
oldkeys={ns['canonical'](p) for p in QUESTIONS[0]['options']}
for attempt in range(100):
    known=ns['partition'](ns['T18'] if 'T18' in ns else ns['box']((3,3,2)),[6,6,6])[:-1]
    q=ns['fill'](9,ns['box']((3,3,2)),known,'C',hard=True)
    keys={ns['canonical'](p) for p in q['options']}
    if ns['canonical'](q['options'][2]) not in oldkeys and len(keys&oldkeys)<=1:
        q['stem']='从A—D中选出一个部件，与已给部件拼成右侧完整长方体。目标尺寸为3×3×2个单位格。'
        q['analysis']=[]
        q['option_profiles']=[ns['profile'](p) for p in q['options']]
        q['piece_profiles']=[ns['profile'](p) for p in q['pieces']]
        QUESTIONS[8]=q
        out=Path(__file__).with_name('puzzles.py')
        out.write_text('"""Original spatial assembly models; integer cells, proper rotations only."""\nQUESTIONS = '+pprint.pformat(QUESTIONS,width=120,sort_dicts=False)+'\n',encoding='utf-8')
        print('q9 changed',attempt,'shared option shapes',len(keys&oldkeys),'parts',q['pieces'],'options',q['options'])
        break
else:raise RuntimeError('unable to diversify q9')
