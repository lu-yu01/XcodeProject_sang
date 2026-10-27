"""Bind each final item to independent image-based solving evidence."""
from build import ROOT,data
from hashlib import sha256
import json

def rows(name):
    x=json.loads((ROOT/name).read_text(encoding='utf-8'))
    if isinstance(x,list):return x
    if 'n' in x:return [x]
    return x.get('reviews',x.get('questions',[]))

def main():
    qs,_=data(False);by_n={q['n']:q for q in qs}
    routes=[('blind_review_a_by_b.json',range(1,11)),
            ('blind_review_b_11_12_15_by_a.json',[11,12]),
            ('blind_review_b_by_c.json',[13,14,16,17,18,19,20]),
            ('blind_review_c_by_a.json',range(21,30)),
            ('blind_review_c30_by_b.json',[30]),
            ('blind_review_b15_revised_by_a.json',[15])]
    selected=[]
    for name,numbers in routes:
        data_rows={x['n']:x for x in rows(name)}
        for n in numbers:
            row=data_rows[n];q=by_n[n];p=ROOT/'assets'/q['image']
            h=sha256(p.read_bytes()).hexdigest()
            assert row['answer']==q['answer'],(n,name,'independent answer mismatch')
            assert row['image_sha256']==h,(n,name,'stale reviewed image')
            assert row.get('actual_image_viewed',row.get('image_actually_viewed',False)),(n,'image not viewed')
            assert row.get('natural_rule'),(n,'no independent reasoning')
            assert row.get('answer') in 'ABCD'
            selected.append({'n':n,'answer':row['answer'],'review_file':name,'image_sha256':h,
                             'natural_rule':row['natural_rule'],'confidence':row.get('confidence'),
                             'notes':row.get('ambiguities',[])})
    assert sorted(x['n'] for x in selected)==list(range(1,31))
    result={'passed':True,'scope':'代理交叉独立求解，非教师盲审或学员试测；每题至少一份最终图像绑定且答案一致的独立推理记录。',
            'questions':sorted(selected,key=lambda x:x['n']),
            'history':['B11首位试解者未恢复空心标记意义；另一个独立试解者从图面恢复黑区部分数与框边接触数双对应。',
                       'B12由补充独立试解恢复直线方向种数和封闭面数对应；记录保留首轮较低置信度。',
                       '原B15两位试解者均借图片数据的有限运算枚举才恢复，因发现成本偏高已改题；旧题和旧试解放revision_history/b15_initial，不能作为新15验收。',
                       '原C30有直接提示，已删除；A曾看到提示的第30题结果不计入无提示独立证据，采用B对无提示最终图的补充独立解题。'],
            'unresolved_answer_disagreements':[]}
    (ROOT/'cross_review_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print({'passed':True,'final_items_independently_solved':len(selected)})
if __name__=='__main__':main()
