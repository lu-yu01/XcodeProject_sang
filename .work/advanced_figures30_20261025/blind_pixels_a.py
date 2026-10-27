"""Read only rendered pixels to measure polygon right angles for independent review."""
from PIL import Image
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parent
def hull(points):
    points=sorted(set(points))
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[]
    for p in points:
        while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
        lo.append(p)
    hi=[]
    for p in points[::-1]:
        while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
        hi.append(p)
    return lo[:-1]+hi[:-1]
def rdp(points,epsilon=5):
    a,b=points[0],points[-1];dist=[]
    for p in points[1:-1]:dist.append(abs((b[0]-a[0])*(a[1]-p[1])-(a[0]-p[0])*(b[1]-a[1]))/max(math.dist(a,b),1e-9))
    if not dist or max(dist)<epsilon:return [a,b]
    i=dist.index(max(dist))+1
    return rdp(points[:i+1],epsilon)[:-1]+rdp(points[i:],epsilon)
def comps(im):
    pix=im.load();pts={(x,y) for y in range(im.height) for x in range(im.width) if sum(pix[x,y][:3])<250}
    out=[]
    while pts:
        group={pts.pop()};queue=list(group)
        for x,y in queue:
            for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if p in pts:pts.remove(p);group.add(p);queue.append(p)
        xs=[p[0] for p in group];ys=[p[1] for p in group]
        w,h=max(xs)-min(xs),max(ys)-min(ys)
        if 30<w<150 and 30<h<150:out.append(group)
    return out
for n in (4,9):
    im=Image.open(ROOT/f'assets/q{n:02}.png').convert('RGB');results=[]
    for component in comps(im):
        hh=hull(component);j=max(range(len(hh)),key=lambda i:math.dist(hh[0],hh[i]));pp=rdp(hh[:j+1])[:-1]+rdp(hh[j:]+[hh[0]])[:-1]
        if len(pp)<4:continue
        cosines=[]
        for i,p in enumerate(pp):
            a,b=pp[i-1],pp[(i+1)%len(pp)];u=(a[0]-p[0],a[1]-p[1]);v=(b[0]-p[0],b[1]-p[1])
            cosines.append((u[0]*v[0]+u[1]*v[1])/math.hypot(*u)/math.hypot(*v))
        right=[i for i,c in enumerate(cosines) if abs(c)<.07]
        cx=sum(p[0] for p in pp)/len(pp);cy=sum(p[1] for p in pp)/len(pp)
        results.append((round(cx),round(cy),len(right),right,[round(c,3) for c in cosines],pp))
    print('QUESTION',n)
    for result in sorted(results,key=lambda r:(r[1]//300,r[0])):print(result)
