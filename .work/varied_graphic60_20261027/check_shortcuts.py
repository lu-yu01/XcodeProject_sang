from model import *
g,qs,mods=make();collapsed=[]
for q in qs:
 m=mods[q['module']];group=g[q['group']-1];k=m.scene_key(q['states'][-1])
 singles=[r['id'] for r in group['rules'] if m.scene_key(m.apply(q['source'],r['id']))==k]
 if singles or m.scene_key(q['source'])==k:collapsed.append({'n':q['n'],'group':q['group'],'chain':q['chain'],'single':singles,'identity':m.scene_key(q['source'])==k})
dump(ROOT/'shortcut_audit.json',collapsed);print(json.dumps(collapsed,ensure_ascii=False))
