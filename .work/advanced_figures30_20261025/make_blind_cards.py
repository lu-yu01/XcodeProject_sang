"""Create answer-free cards bound to the current images and normalized stems."""
from build import ROOT,data
from hashlib import sha256
import json
def main():
    qs,_=data(draw=False)
    for group,lo,hi in [('a',1,10),('b',11,20),('c',21,30)]:
        cards=[]
        for q in qs:
            if not lo<=q['n']<=hi:continue
            p=ROOT/'assets'/q['image']
            cards.append({'n':q['n'],'stem':q['stem'],'ask':q.get('ask',''),'options':q.get('options',[]),
                          'image':str(p),'image_sha256':sha256(p.read_bytes()).hexdigest()})
        out=ROOT/f'blind_cards_{group}.json'
        old=json.loads(out.read_text(encoding='utf-8'))['cards'] if out.exists() else []
        previous={x['n']:x['image_sha256'] for x in old}
        changed=[x['n'] for x in cards if x['image_sha256']!=previous.get(x['n'])]
        out.write_text(json.dumps({'instruction':'仅看题干、原图和选项独立求解，不读作者代码、答案、解析和模型；记录自然规则、选择、置信度及歧义。','cards':cards},ensure_ascii=False,indent=2),encoding='utf-8')
        print(group,'updated_image_questions',changed)
if __name__=='__main__':main()
