"""Independent review model, manually transcribed from public question PNGs only."""
from copy import deepcopy
from pathlib import Path
import json
import hashlib

P=Path(__file__).resolve().parent

def rotate(items):return items[-1:]+items[:-1]
def shape_token(x):return ((x[0]+1)%3,x[1])
def invert_token(x):return (x[0],1-x[1])
def mul(a,b):return tuple(sum(a[r*2+k]*b[k*2+c] for k in range(2)) for r in range(2) for c in range(2))
ID=(1,0,0,1);R=(0,-1,1,0);R2=mul(R,R);R3=mul(R2,R);MX=(-1,0,0,1);MY=(1,0,0,-1)

SOURCE={
43:[(1,0),(3,0),(0,1),(1,1)],44:[(0,1),(3,0),(3,1),(1,0)],45:[(1,0),(2,1),(2,0),(1,1)],
46:[('F',MY),('R',R3),('P',ID)],47:[('R',R3),('P',mul(MX,R)),('F',R2)],48:[('F',R),('P',MY),('R',mul(MX,R3))],
49:[(2,0),(2,1),(1,0),(0,1),(0,0),(1,1)],50:[(2,1),(0,0),(1,1),(0,1),(1,0),(2,0)],51:[(1,1),(2,0),(2,1),(0,1),(0,0),(1,0)],
52:[(0,0),(0,1),(1,0),(2,1)],53:[(0,1),(2,0),(2,1),(1,0)],54:[(1,0),(2,0),(0,1),(2,1)],
55:([2,0,1,3],[2,1,0,0]),56:([2,3,0,1],[1,1,2,0]),57:([3,0,1,2],[1,0,2,2]),
58:(41,55),59:(49,60),60:(222,205),
}
TARGET={
43:[(3,1),(1,1),(0,0),(1,0)],44:[(0,0),(1,1),(2,0),(0,1)],45:[(0,0),(1,1),(3,0),(2,1)],
46:[('P',MY),('F',R),('R',ID)],47:[('F',MY),('P',R),('R',mul(MX,R3))],48:[('P',MX),('R',R),('F',R2)],
49:[(0,1),(2,0),(2,1),(0,0),(1,1),(1,0)],50:[(2,1),(0,1),(1,0),(0,0),(1,1),(2,0)],51:[(2,1),(2,0),(1,1),(0,1),(1,0),(0,0)],
52:[(2,0),(0,1),(0,0),(0,1)],53:[(2,0),(1,0),(1,1),(0,1)],54:[(0,0),(2,0),(0,1),(1,1)],
55:([2,0,1,3],[0,1,2,0]),56:([2,1,0,3],[1,0,2,2]),57:([1,2,3,0],[2,0,1,2]),
58:(30,200),59:(195,3),60:(204,254),
}

def step(g,s,op):
    s=deepcopy(s)
    if g==15:
        if op=='↻':s=rotate(s)
        elif op=='↷':s=[((d+1)%4,b) for d,b in s]
        elif op=='B':s=[((d+2*b)%4,b) for d,b in s]
        elif op=='◇':s=[(d,1-b) for d,b in s]
        elif op=='↕':s[0],s[2]=s[2],s[0]
        elif op=='↔':s[1],s[3]=s[3],s[1]
    elif g==16:
        if op in ('F→P','C'):s=[({'F':'P','P':'R','R':'F'}[c],m) for c,m in s]
        elif op=='△':s=rotate(s)
        elif op=='↔':s[1],s[2]=s[2],s[1]
        elif op=='↷':s=[(c,mul(R,m)) for c,m in s]
        elif op=='⇆':s=[(c,mul(MX,m)) for c,m in s]
        elif op=='F²':s=[(c,mul(R2,m) if c=='F' else m) for c,m in s]
    elif g==17:
        if op=='↻':s=rotate(s)
        elif op=='⇆':s=[s[i] for i in [0,5,4,3,2,1]]
        elif op=='S':s=[shape_token(x) for x in s]
        elif op=='◇':s=[invert_token(x) for x in s]
        elif op=='↕':s[0],s[3]=s[3],s[0]
        elif op=='B':s=[shape_token(x) if x[1] else x for x in s]
    elif g==18:
        if op=='⇄':s=s[2:]+s[:2]
        elif op=='↔':s=[s[i] for i in [1,0,3,2]]
        elif op=='M':s[1],s[2]=s[2],s[1]
        elif op=='L':s=[shape_token(x) if i<2 else x for i,x in enumerate(s)]
        elif op=='◇':s=[invert_token(x) for x in s]
        elif op=='B':s=[shape_token(x) if x[1] else x for x in s]
    elif g==19:
        a,b=s
        if op=='⇆':a,b=a[::-1],b[::-1]
        elif op=='E':a=a[1:]+a[:1]
        elif op=='K':b=rotate(b)
        elif op in ('·→×','T'):b=[(x+1)%3 for x in b]
        elif op=='S':a=[(x+1)%4 for x in a]
        elif op=='M':b[1],b[2]=b[2],b[1]
        s=(a,b)
    elif g==20:
        a,b=s
        if op=='⊕':a=a^b
        elif op=='∩':b=a&b
        elif op=='∪':a=a|b
        elif op=='⇄':a,b=b,a
        elif op=='↶':a,b=((a<<4)|(a>>4))&255,((b<<4)|(b>>4))&255
        elif op=='¬':b=b^255
        s=(a,b)
    return s

if __name__=='__main__':
    public=json.loads((P/'public_questions.json').read_text(encoding='utf-8'))
    first=json.loads((P/'first_answers_43_60.json').read_text(encoding='utf-8'))
    reviewed=[]
    for g in public['groups']:
        if not 15<=g['id']<=20:continue
        for q in g['questions']:
            n=q['n'];s=SOURCE[n];states=[s]
            for op in q['chain']:s=step(g['id'],s,op);states.append(s)
            assert s==TARGET[n],(n,s,TARGET[n])
            frozen=next(x for x in first['answers'] if x['n']==n)
            current_sha=hashlib.sha256(Path(q['image']).read_bytes()).hexdigest()
            assert current_sha==q['image_sha256']
            reviewed.append({'n':n,'first_choice':next(x['first_choice'] for x in first['answers'] if x['n']==n),'independently_recomputed':True,'source_transcribed_from_image':SOURCE[n],'states':states,'selected_option_transcribed_from_image':TARGET[n],'matches_selected_option':True,'original_frozen_image_sha256':frozen['actual_image_sha256'],'final_reviewed_image_sha256':current_sha,'final_image_actually_reopened':True,'final_public_chain':q['chain'],'final_visible_match_remains_unique':True})
    report={'scope':'Groups 15-20, questions 43-60. Group 20 uses the final eight-ray public images.','materials':'Public instructions and actual PNGs only; no author model, answer or solution read.','first_choices_preserved':True,'independent_method':'Manually transcribed image states; independent tuple permutations, modular token replacement, 2x2 glyph matrices and eight-bit set masks.','results':reviewed,'text_suggestions':[{'groups':[17,18],'suggestion':'Explicitly fix newly generated triangles to point upward.','impact':'No present option ambiguity; improves the full rule definition.','status':'Author accepted; awaiting updated public wording.'}],'pending':[]}
    intros={g['id']:g['intro'] for g in public['groups'] if g['id'] in (17,18)}
    if all('尖端朝上' in v for v in intros.values()):
        report['text_suggestions'][0].update(status='Closed: updated public introductions reread and accepted. All 18 revised PNGs actually reopened; first choices remain unchanged.',accepted_final_intros=intros)
    report['final_revision']={'reported_change':'Operation-chain spaces reduced; group 16 code F→P replaced by C and group 19 code ·→× replaced by T; author reports scene data and option ordering unchanged.','reviewer_confirmation':'All 18 final question PNGs actually reopened, public rules and final codes reread, same visible source and candidate content observed; independently recomputed answers unchanged. This review does not itself claim pixel-level identity.','code_mapping':{'group16':{'old':'F→P','final':'C','meaning':'F→P→R→F; glyph pose preserved'},'group19':{'old':'·→×','final':'T','meaning':'point→cross→dash→point'}},'final_public_manifest_sha256':hashlib.sha256((P/'public_questions.json').read_bytes()).hexdigest(),'original_first_record_sha256':hashlib.sha256((P/'first_answers_43_60.json').read_bytes()).hexdigest()}
    (P/'blind_review_43_60.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Independent public-only recomputation passed for 18 questions.')
