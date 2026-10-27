from pathlib import Path
import xml.etree.ElementTree as ET
import re,html,math,json
ROOT=Path(__file__).resolve().parent
W=1800
def f(x):return f'{x:.3f}'
def attrs(d):return ' '.join(f'{k.replace("_","-")}="{html.escape(str(v),quote=True)}"' for k,v in d.items())
def el(tag,**kw):return '<'+tag+' '+attrs(kw)+'/>'
def line(a,b,width=2,color='#202020',dash=None):
    kw=dict(x1=f(a[0]),y1=f(a[1]),x2=f(b[0]),y2=f(b[1]),stroke=color,stroke_width=width,stroke_linecap='round')
    if dash:kw['stroke_dasharray']=dash
    return el('line',**kw)
def poly(points,fill='white',width=2,stroke='#222'):
    return el('polygon',points=' '.join(f'{f(x)},{f(y)}' for x,y in points),fill=fill,stroke=stroke,stroke_width=width,stroke_linejoin='round')
def circle(x,y,r,fill='white',width=2):return el('circle',cx=f(x),cy=f(y),r=f(r),fill=fill,stroke='#222',stroke_width=width)
def rect(x,y,w,h,fill='white',width=2,rx=0,stroke='#222'):
    return el('rect',x=f(x),y=f(y),width=f(w),height=f(h),fill=fill,stroke=stroke,stroke_width=width,rx=rx)
def text(x,y,t,size=29,bold=False):
    return f'<text x="{f(x)}" y="{f(y)}" text-anchor="middle" dominant-baseline="central" font-family="Microsoft YaHei,SimSun" font-size="{size}" font-weight="{700 if bold else 400}" fill="#181818">{html.escape(t)}</text>'
def arrow(a,b,width=3,head=12):
    dx,dy=b[0]-a[0],b[1]-a[1];z=math.hypot(dx,dy);u,v=dx/z,dy/z
    return line(a,b,width)+poly([b,(b[0]-head*u-head*.45*v,b[1]-head*v+head*.45*u),(b[0]-head*u+head*.45*v,b[1]-head*v-head*.45*u)],'#222',0)
def north(x,y,size=48,angle=0):
    v=math.sin(angle),-math.cos(angle);b=x+v[0]*size,y+v[1]*size
    return arrow((x,y),b,3,12)+text(b[0]+v[0]*23,b[1]+v[1]*23,'北',27)
def group(body,x=0,y=0):return f'<g transform="translate({f(x)} {f(y)})">{body}</g>'
def nested(body,x,y,w,h,viewbox):return f'<svg x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" viewBox="{viewbox}">{body}</svg>'
_cache={};USED=set()
def icon(name,x,y,w=90,h=85):
    path=ROOT/'sources'/f'{name}.svg'
    if not path.exists():raise FileNotFoundError(path)
    USED.add(name)
    if name not in _cache:
        root=ET.parse(path).getroot()
        # Raw SVG assets are embedded as vectors, preserving alpha and line work.
        for child in list(root):
            if child.tag.split('}')[-1] in ['metadata','namedview','title','desc']:root.remove(child)
        for item in root.iter():
            for k in list(item.attrib):
                if k.split('}')[-1].lower().startswith('on'):del item.attrib[k]
        vb=root.get('viewBox')
        if not vb:
            def num(v):return re.match(r'[0-9.]+',v).group()
            vb='0 0 '+num(root.get('width','100'))+' '+num(root.get('height','100'))
        _cache[name]=(vb,''.join(ET.tostring(c,encoding='unicode') for c in root))
    vb,body=_cache[name]
    return '<g filter="url(#mono)">'+nested(body,x-w/2,y-h,w,h,vb)+'</g>'
def save(body,n,height,kind='question'):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1800" height="{height}" viewBox="0 0 1800 {height}"><defs><filter id="mono" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/></filter></defs><rect width="1800" height="{height}" fill="white"/>{body}</svg>'
    (ROOT/'svg'/f'{kind}-{n:02}.svg').write_text(svg,encoding='utf8')
def frame(tiles,y,height,labels='ABCD'):
    b=rect(20,y,1760,height,'white',3)
    for i,t in enumerate(tiles):
        b+=nested(t,30+440*i,y+8,420,height-16,f'0 0 420 {height-16}')
        if i:b+=line((20+440*i,y),(20+440*i,y+height),2)
        b+=text(240+440*i,y+height+36,labels[i],37,True)
    return b
def write_usage():
    (ROOT/'vector_usage.json').write_text(json.dumps({'actual_embedded_source_names':sorted(USED),'source_format':'downloaded SVG vectors embedded in native scene SVG, rasterized once for Word'},ensure_ascii=False,indent=2),encoding='utf8')
