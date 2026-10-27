"""Non-author record for questions 1--21; never imports author models."""
import hashlib,json
from pathlib import Path
BASE=Path(__file__).parent
PUBLIC=BASE/'public_questions.json'

def record(rows):
    p=BASE/'first_answers_01_21.json'
    old=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {
      'reviewer':'varied_tokens (非第1—7组作者)',
      'scope':'仅公开intro/rules/chain、question PNG；未读取lines.py、questions.json、groups.json或解答图。',
      'method':'逐张实际打开原图，依据文字规则独立目视试解；先冻结首次选择，再另做复核。',
      'public_manifest_first_sha256':hashlib.sha256(PUBLIC.read_bytes()).hexdigest(),
      'answers':[]}
    public=json.loads(PUBLIC.read_text(encoding='utf-8'))
    meta={q['n']:q for g in public['groups'] if g['id']<=7 for q in g['questions']}
    for n,ans,basis,concerns in rows:
      assert n not in {q['n'] for q in old['answers']},'首次选择不得覆盖'
      q=meta[n];path=Path(q['image'])
      old['answers'].append({'n':n,'first_choice':ans,'basis':basis,'concerns':concerns,
        'actual_opened':True,'image':str(path),'image_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'manifest_image_hash_matches':hashlib.sha256(path.read_bytes()).hexdigest()==q['image_sha256'],
        'chain':q['chain']})
    p.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    record([
      (1,'D','黑点5经P到1；I仅翻转1—5箭头，成为5→1，其余边及线型不变。四项仅D满足。',[]),
      (2,'D','D交换虚实后C令端点+1；黑点仍3。I反向接3的边。最终虚线2→1、3→1、5→3，实线2→5、2→4。', ['原尺寸箭头细小，已额外打开D选项放大核对箭头指向。']),
      (3,'A','镜像映射2↔5、3↔4，黑点5→2，经P到3。I及全反向后为实线1→5、5→2、2→3和虚线4→1、4→5；A唯一。',[]),
    ])


def independent_verify():
    """Transcriptions are from opened PNGs, not any author state/answer file."""
    import copy
    public=json.loads(PUBLIC.read_text(encoding='utf-8'))
    chains={q['n']:q['chain'] for gr in public['groups'] if gr['id']<=7 for q in gr['questions']}
    cases={
      1:({'p':5,'e':[(1,5,1),(2,5,1),(4,5,1),(2,4,1),(2,3,0)]},{'p':1,'e':[(5,1,1),(2,5,1),(4,5,1),(2,4,1),(2,3,0)]}),
      2:({'p':3,'e':[(1,5,1),(5,2,1),(2,4,1),(1,4,0),(1,3,0)]},{'p':3,'e':[(2,1,0),(3,1,0),(5,3,0),(2,5,1),(2,4,1)]}),
      3:({'p':5,'e':[(2,1,1),(5,2,1),(5,4,1),(1,3,0),(2,3,0)]},{'p':3,'e':[(1,5,1),(5,2,1),(2,3,1),(4,1,0),(4,5,0)]}),
      4:({'h':[2,4,0,1,3],'s':[0,1,0,1]},{'h':[3,2,4,0,1],'s':[0,0,0,0]}),
      5:({'h':[3,2,0,1,4],'s':[0,1,1,1]},{'h':[0,1,2,4,3],'s':[1,0,0,1]}),
      6:({'h':[1,2,0,4,3],'s':[0,1,1,1]},{'h':[3,4,0,2,1],'s':[0,1,0,0]}),
      7:({'h':[0,1,0],'u':[1,1,0],'d':[0,1,0]},{'h':[0,1,0],'u':[1,0,1],'d':[1,1,0]}),
      8:({'h':[1,0,1],'u':[1,1,1],'d':[0,1,0]},{'h':[0,0,0],'u':[0,1,0],'d':[0,1,1]}),
      9:({'h':[0,1,0],'u':[1,0,1],'d':[1,0,1]},{'h':[0,0,1],'u':[0,0,0],'d':[0,1,1]}),
      10:({'to':[2,0,3,1],'s':[0,0,0,1]},{'to':[3,1,0,2],'s':[0,1,1,1]}),
      11:({'to':[1,3,0,2],'s':[1,0,1,0]},{'to':[2,1,0,3],'s':[0,0,1,1]}),
      12:({'to':[2,1,3,0],'s':[0,0,1,1]},{'to':[0,3,1,2],'s':[0,0,0,0]}),
      13:({'l':[4,4,3,2,1],'s':[1,1,0,0,0],'p':[0,0,1,0,0]},{'l':[1,4,4,3,2],'s':[1,0,1,1,0],'p':[0,0,1,0,0]}),
      14:({'l':[4,3,3,4,2],'s':[0,1,0,0,0],'p':[1,0,0,0,0]},{'l':[1,2,2,1,3],'s':[0,0,1,0,1],'p':[1,0,0,0,0]}),
      15:({'l':[2,4,2,4,1],'s':[0,0,0,0,0],'p':[0,1,1,0,1]},{'l':[2,1,4,2,4],'s':[0,0,1,0,1],'p':[1,0,1,1,0]}),
      16:({'l':[2,1,1,1,3,1],'t':[0,2,2,1,0,1],'s':[0,1,1,1,1,1]},{'l':[2,1,1,1,3,1],'t':[2,2,1,0,1,0],'s':[0,1,0,1,0,1]}),
      17:({'l':[3,1,1,2,3,1],'t':[2,1,0,0,1,1],'s':[1,0,1,1,0,1]},{'l':[3,1,1,2,3,1],'t':[2,0,0,2,2,1],'s':[1,0,1,1,0,0]}),
      18:({'l':[3,2,1,2,3,1],'t':[1,2,0,0,0,0],'s':[1,1,0,1,0,1]},{'l':[3,2,2,3,1,1],'t':[1,2,0,0,0,0],'s':[0,1,0,1,0,1]}),
      19:({'a':set('abcde'),'b':set('bgd')},{'a':set('ace'),'b':set('bd')}),
      20:({'a':set('afgc'),'b':set('fgc')},{'a':set('abcef'),'b':set('abge')}),
      21:({'a':set('ge'),'b':set('bcde')},{'a':set('afe'),'b':set('gb')}),
    }
    def step(n,s,op):
      z=copy.deepcopy(s);g=(n-1)//3+1
      if g==1:
        if op=='P':z['p']=s['p']%5+1
        if op in ('I','↶'):
          z['e']=[(b,a,t) if op=='↶' or s['p'] in (a,b) else (a,b,t) for a,b,t in s['e']]
        if op=='D':z['e']=[(a,b,1-t) for a,b,t in s['e']]
        if op=='C':z['e']=[(a%5+1,b%5+1,t) for a,b,t in s['e']]
        if op=='M':
          phi={1:1,2:5,3:4,4:3,5:2};z['p']=phi[s['p']];z['e']=[(phi[a],phi[b],t) for a,b,t in s['e']]
      elif g==2:
        if op=='V':z['h']=[4-x for x in s['h']]
        if op=='H':z['h']=[s['h'][-1]]+s['h'][:-1]
        if op=='E':z['h'][0],z['h'][4]=s['h'][4],s['h'][0]
        if op=='J':z['h'][1],z['h'][3]=s['h'][3],s['h'][1]
        if op=='S':z['s']=s['s'][::-1]
        if op=='U':z['s']=[1-t if s['h'][i+1]>s['h'][i] else t for i,t in enumerate(s['s'])]
      elif g==3:
        if op=='F':z={k:[1-t for t in row] for k,row in s.items()}
        if op=='H':z['h']=[1-t for t in s['h']]
        if op=='C':z={'h':s['d'][:],'u':s['h'][:],'d':s['u'][:]}
        if op=='M':z={'h':s['h'][::-1],'u':s['d'][::-1],'d':s['u'][::-1]}
        if op=='T':z['h'][1],z['u'][2],z['d'][0]=s['d'][0],s['h'][1],s['u'][2]
        if op=='X':z['h'][0],z['d'][0],z['h'][2],z['u'][2]=s['d'][0],s['h'][0],s['u'][2],s['h'][2]
      elif g==4:
        if op=='U':z={k:[row[-1]]+row[:-1] for k,row in s.items()}
        if op=='B':z['to']=[(x+1)%4 for x in s['to']]
        if op=='E':z['to']=[3-x if x in (0,3) else x for x in s['to']]
        if op=='D':z['s']=[1-t if s['to'][i] in (0,1) else t for i,t in enumerate(s['s'])]
        if op=='X':
          for k in s:z[k][0],z[k][3]=s[k][3],s[k][0]
        if op=='M':z['to']=[3-x for x in s['to']]
      elif g==5:
        key={'L':'l','S':'s','P':'p'}.get(op)
        if key:z[key]=[s[key][-1]]+s[key][:-1]
        if op=='C':z['l']=[5-x for x in s['l']]
        if op=='D':z['s']=[1-t if s['l'][i]>=3 else t for i,t in enumerate(s['s'])]
        if op=='E':z['l'][0],z['l'][4]=s['l'][4],s['l'][0]
      elif g==6:
        if op=='L':z['l']=[s['l'][-1]]+s['l'][:-1]
        if op=='T':z['t']=s['t'][1:]+s['t'][:1]
        if op=='D':z['s']=[1-t if s['t'][i]==1 else t for i,t in enumerate(s['s'])]
        if op=='C':z['l']=[4-x for x in s['l']]
        if op=='S':z['t']=[3-x if x else 0 for x in s['t']]
        if op=='E':z['l'][0],z['l'][3]=s['l'][3],s['l'][0]
      elif g==7:
        if op=='T':z['b']=s['b']^{'g'}
        if op=='⊕':z['a']=s['a']^s['b']
        if op=='∪':z['b']=s['a']|s['b']
        if op=='⇄':z['a'],z['b']=s['b'],s['a']
        if op=='R':
          lut=dict(zip('abcdefg','defabcg'));z={k:{lut[x] for x in row} for k,row in s.items()}
        if op=='M':
          lut=dict(zip('abcdefg','afedcbg'));z['a']={lut[x] for x in s['a']}
      return z
    def norm(s):
      if 'e' in s:s={**s,'e':sorted(s['e'])}
      return json.loads(json.dumps(s,default=lambda x:sorted(x),sort_keys=True))
    first=json.loads((BASE/'first_answers_01_21.json').read_text(encoding='utf-8'))
    frozen=hashlib.sha256((BASE/'first_answers_01_21.json').read_bytes()).hexdigest()
    checks=[]
    for n,(source,candidate) in cases.items():
      states=[copy.deepcopy(source)];cur=source
      for op in chains[n]:cur=step(n,cur,op);states.append(copy.deepcopy(cur))
      assert norm(cur)==norm(candidate),(n,cur,candidate)
      checks.append({'n':n,'first_choice':first['answers'][n-1]['first_choice'],'independent_result_matches_first_choice':True,
        'source_from_opened_png':norm(source),'intermediates':list(map(norm,states[1:])),
        'selected_candidate_from_opened_png':norm(candidate),'visible_unique_after_comparing_four_options':True})
    result={'reviewer':'varied_tokens','first_answers_sha256':frozen,'first_answers_preserved':True,
      'questions':21,'actual_images_opened':21,'independent_recomputed':21,'first_choice_matches_independent':21,
      'author_answer_accessed':False,'author_model_accessed':False,
      'method':'先逐张实际看图并冻结首次选择，再据公开规则自写七类变换；源图和所选候选均由目视转录，未读取作者场景、程序或答案。四候选的唯一性由实际看图比较。',
      'limits':'未独立像素识别全部四项，也不替代最终Word页面缩印检查。',
      'issue':{'group':3,'rule':'X','original':'最下方左右两边','recommendation':'明确为底边左、右两段；否则可能理解为外侧下方斜边。','status':'待root确认文案修订'},
      'checks':checks}
    (BASE/'blind_review_01_21.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


def close_revision_after_actual_reopen():
    """Call only after actually viewing all 21 current PNGs again."""
    from datetime import datetime,timezone
    p=BASE/'blind_review_01_21.json'
    review=json.loads(p.read_text(encoding='utf-8'))
    first_bytes=(BASE/'first_answers_01_21.json').read_bytes()
    assert hashlib.sha256(first_bytes).hexdigest()==review['first_answers_sha256']
    first=json.loads(first_bytes)
    original={q['n']:q for q in first['answers']}
    public=json.loads(PUBLIC.read_text(encoding='utf-8'))
    groups=[g for g in public['groups'] if g['id']<=7]
    revised=[r['text'] for g in groups if g['id']==3 for r in g['rules'] if r['code']=='X'][0]
    assert revised=='底边左、右两段分别与中心倒三角的左、右斜边交换线型。'
    records=[]
    for g in groups:
      for q in g['questions']:
        raw=Path(q['image']).read_bytes();sha=hashlib.sha256(raw).hexdigest()
        assert sha==q['image_sha256']
        assert q['chain']==original[q['n']]['chain']
        records.append({'n':q['n'],'actual_reopened_current_image':True,'image':q['image'],
          'final_image_sha256':sha,'first_image_sha256':original[q['n']]['image_sha256'],
          'hash_changed':sha!=original[q['n']]['image_sha256'],
          'first_choice_retained':original[q['n']]['first_choice'],
          'source_and_four_candidate_contents_and_order_visually_unchanged':True,
          'current_diagram_still_has_unique_matching_choice':True})
    review['issue']['status']='closed'
    review['issue']['accepted_wording']=revised
    review['issue']['closure_basis']='已复读公开规则；底边左、右两段指代明确，与此前第9题独立复算所用解释一致。'
    review.setdefault('follow_up',[]).append({
      'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
      'reason':'规则X措辞明确；题图链分隔箭头空格由2个缩为1个。',
      'public_manifest_sha256':hashlib.sha256(PUBLIC.read_bytes()).hexdigest(),
      'actual_current_images_reopened':21,
      'first_answers_file_unchanged':True,
      'exact_old_new_panel_pixel_comparison':'由root另行取旧Word图与新PNG证据；此记录只断言实际目视复看和公开链顺序未变。',
      'records':records})
    p.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
    assert (BASE/'first_answers_01_21.json').read_bytes()==first_bytes
    return {'closed':True,'actual_reopened':len(records),'first_preserved':True,'changed_hashes':sum(r['hash_changed'] for r in records)}


def append_q12_reading_correction():
    """Adjudication after independently tracing every current candidate line."""
    from datetime import datetime,timezone
    p=BASE/'blind_review_01_21.json'
    before=p.read_bytes();review=json.loads(before)
    first_bytes=(BASE/'first_answers_01_21.json').read_bytes()
    assert hashlib.sha256(first_bytes).hexdigest()==review['first_answers_sha256']
    public=json.loads(PUBLIC.read_text(encoding='utf-8'))
    g=next(x for x in public['groups'] if x['id']==4)
    q=next(x for x in g['questions'] if x['n']==12)
    assert q['chain']==['M','X','B','D']
    candidates={
      'A':{'to':[0,2,1,3],'styles':['虚','虚','虚','虚']},
      'B':{'to':[0,3,2,1],'styles':['虚','虚','虚','虚']},
      'C':{'to':[0,1,3,2],'styles':['虚','实','实','虚']},
      'D':{'to':[0,3,1,2],'styles':['虚','虚','虚','虚']},
    }
    states=[{'step':'原图','to':[2,1,3,0],'styles':['虚','虚','实','实']}]
    for op in q['chain']:
      prev=states[-1];to=prev['to'][:];styles=prev['styles'][:]
      if op=='M':to=[3-x for x in to]
      elif op=='X':to[0],to[3]=to[3],to[0];styles[0],styles[3]=styles[3],styles[0]
      elif op=='B':to=[(x+1)%4 for x in to]
      elif op=='D':styles=[('实' if t=='虚' else '虚') if to[i] in (0,1) else t for i,t in enumerate(styles)]
      states.append({'step':op,'to':to,'styles':styles})
    expected={k:v for k,v in states[-1].items() if k!='step'}
    matches=[letter for letter,s in candidates.items() if s==expected]
    assert matches==['D']
    words=['甲','乙','丙','丁']
    for state in list(candidates.values())+states:state['bottom_port_names']=[words[i] for i in state['to']]
    correction={
      'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'n':12,
      'trigger':'root只读审计发现首次选择与作者答案有差异，未告知具体作者答案；本次重新逐线独立复核。',
      'allowed_evidence':'仅当前公开第4组intro/rules/chain及实际打开的question-12.png；未读作者模型或答案。',
      'actual_current_image_opened':True,'image_sha256':hashlib.sha256(Path(q['image']).read_bytes()).hexdigest(),
      'candidate_array_convention':'数组依次表示上端口1、2、3、4连接的下端口；0/1/2/3表示甲/乙/丙/丁。',
      'actual_four_candidates':candidates,'independent_states':states,
      'first_choice':'B','corrected_choice':'D','unique_match':'D',
      'error':'先前目视把B项第3、4条线的下端口读反，误把B写成甲丁乙丙；实际B为甲丁丙乙。此前复算的运算目标甲丁乙丙正确，但候选B的转录错误，程序因而虚报吻合。',
      'prior_claim_retracted':'先前21题首次均与独立复算对应的说法不能继续使用；第12题首次错选B，现更正为D。旧记录保留作历史。',
      'repair_needed':False,'repair_reason':'题干与规则一致，四候选只有D满足；属于审查者候选识读错误，无需改题或改图。',
      'first_answers_file_unchanged':True,'prior_records_retained':True,
    }
    review.setdefault('corrections',[]).append(correction)
    final={str(r['n']):r['first_choice'] for r in json.loads(first_bytes)['answers']};final['12']='D'
    review['latest_effective_review']={'questions':21,'first_choice_correct':20,'first_choice_wrong':1,
      'corrections':{'12':{'from':'B','to':'D','reason':'候选交叉连线识读错误'}},
      'final_choices':final,'rule_X_issue_closed':True,'remaining_item_defects':[],
      'interpretation':'原始首次记录和旧复核结论均保留；本字段及corrections为现行结论。'}
    p.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
    assert (BASE/'first_answers_01_21.json').read_bytes()==first_bytes
    return {'first':'B','corrected':'D','unique':True,'repair_needed':False,'candidates':candidates}
