import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    qs=read('questions.json');answers={q['n']:q['answer'] for q in qs}
    inputs=[('review_analogy_blind.json','items','first_answer'),
      ('review_definitions_blind.json','reviews','first_pass_answer'),
      ('review_formal_blind.json','items','first_answer'),
      ('review_arguments_root_first.json','items','answer'),
      ('review_arguments_b_blind.json','items','first_answer')]
    items={};reports=[]
    for filename,key,akey in inputs:
        d=read(filename);rows=d[key]
        if isinstance(rows,dict):rows=[dict(n=int(n),**v) for n,v in rows.items()]
        reports.append(dict(path=filename,sha256=sha(ROOT/filename),count=len(rows)))
        for x in rows:
            n=int(x['n']);assert n not in items,(n,'repeated reviewer assignment')
            a=x.get(akey,x.get('answer'));assert a in 'ABCD',(n,akey,x)
            items[n]=dict(first_answer=a,author_answer=answers[n],agrees=a==answers[n],report=filename)
    assert set(items)==set(range(1,111)),set(range(1,111))-set(items)
    assert all(x['agrees'] for x in items.values())
    rev_names=['review_analogy_revision.json','review_analogy_q7_final.json','review_definitions_revised_c.json','review_arguments_revised_b.json']
    for name in rev_names:assert (ROOT/name).exists(),name
    report=dict(passed=True,initial_independent_choices=110,first_choices_matching_author=110,
      independent_semantic_agreement_does_not_prove_uniqueness=True,
      reviewer_type='AI代理非作者试解；不是教师盲审或学员试测',reports=reports,items=items,
      issues_retained=['类比6命名层级及17方法/目的表述','类比7编辑多义与基础干扰项偏弱','定义28未明示参与者盲','定义27/37/48必要条件明示','论证95成本基数','论证101对象范围','论证102净变化与毛新增区别'],
      revision_reports=[dict(path=n,sha256=sha(ROOT/n)) for n in rev_names],
      limitations=['首次选项一致并不等于原题面没有歧义；首轮异议单列并修订','修订复核者知晓自己首轮选择，不能冒充全新盲审','类比部分条目保留中等难度梯度，未用外部试测标定难度'])
    (ROOT/'cross_review_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print({'passed':True,'independent_first_choices':110,'matching':110})
if __name__=='__main__':main()
