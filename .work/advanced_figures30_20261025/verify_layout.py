"""Inspect continuous frames, square matrices and single-row option geometry."""
from pathlib import Path
from collections import Counter
from PIL import Image
import json
from build import ROOT,data
def main():
    qs,_=data(False);layout=json.loads((ROOT/'figure_layout.json').read_text(encoding='utf-8'))
    assert set(map(int,layout))==set(range(1,31))
    count=Counter(x['kind'] for x in layout.values())
    assert count['spatial']==count['classification_3x2']==9
    assert sum(count[k] for k in ['sequence','matrix','two_groups_horizontal'])==12
    checks=[]
    def lines(px,box,cols=4,rows=1):
        x0,y0,x1,y1=map(round,box)
        for i in range(cols+1):
            x=round(x0+(x1-x0)*i/cols)
            assert max(sum(max(px[xx,y])<100 for y in range(y0,y1+1)) for xx in range(x-3,x+4))/(y1-y0+1)>.985
        for i in range(rows+1):
            y=round(y0+(y1-y0)*i/rows)
            assert max(sum(max(px[x,yy])<100 for x in range(x0,x1+1)) for yy in range(y-3,y+4))/(x1-x0+1)>.985
    for q in qs:
        n=q['n'];spec=layout[str(n)];im=Image.open(ROOT/'assets'/q['image']).convert('RGB');px=im.load();kind=spec['kind']
        row={'question':n,'kind':kind}
        if kind=='classification_3x2':
            assert len(q['options'])==4 and len(spec['stem_centers'])==6
            for x,y in spec['stem_centers']:lines(px,(x-137,y-137,x+137,y+137),1,1)
            row['six_equal_square_frames']=True
        else:
            centers=spec['option_centers'];assert len(centers)==4 and len({y for x,y in centers})==1
            if kind=='spatial':box=spec['option_frame'];assert spec['letters_below']
            elif kind=='matrix':box=(170,930,1630,1080)
            else:box=(170,470,1630,740)
            lines(px,box)
            # Each letter has black pixels below, outside the common candidate frame.
            for x,y in centers:
                x=round(x);bottom=round(box[3]);strip=im.crop((x-35,bottom+9,x+36,min(bottom+78,im.height)))
                assert min(v[0] for v in strip.getextrema())<100,(n,'missing letter below frame')
            row['four_options_single_row_common_frame']=True;row['letters_outside_below']=True
        if kind=='two_groups_horizontal':
            assert len({y for x,y in spec['stem_centers']})==1
            row['two_groups_same_horizontal_baseline']=True
        if kind=='matrix':
            xs=sorted(set(x for x,y in spec['stem_centers']));ys=sorted(set(y for x,y in spec['stem_centers']))
            assert len(xs)==len(ys)==3 and xs[1]-xs[0]==ys[1]-ys[0]==280
            lines(px,(480,40,1320,880),3,3)
            row['square_grid']={'outer':[840,840],'cells':[280,280]}
        checks.append(row)
    result={'passed':True,'counts':dict(count),'questions':checks}
    (ROOT/'layout_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print({'passed':True,'counts':dict(count),'questions':len(checks)})
if __name__=='__main__':main()
