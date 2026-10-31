from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
P1 = [(-1,-1),(0,-1),(1,0),(0,0),(0,1),(-1,1)]
P2 = [(0,-1),(1,-1),(0,0),(1,0),(1,1),(0,1),(-1,0)]
C = [(0,-1),(.5,-.5),(0,0),(0,1),(-1,0)]
parts = [ [(-1,0),(0,-1),(0,0)], [(0,-1),(.5,-.5),(0,0)], [(-1,0),(0,0),(0,1)] ]

def area(poly):
    return abs(sum(x*y2-x2*y for (x,y),(x2,y2) in zip(poly,poly[1:]+poly[:1])))/2

# Exact partition: P1 = left rectangle plus upper-right triangle;
# P2 = upper diagonal parallelogram plus lower trapezoid.
# Their intersection is exactly the three triangles listed above.
assert sum(area(p) for p in parts) == area(C) == 1.25
report = {
 'coordinate_convention':'x to right, y down, shared square [-1,1] x [-1,1]',
 'first_polygon':P1, 'second_polygon':P2, 'intersection_C':C,
 'intersection_triangle_partition':parts, 'intersection_area':area(C),
 'display_instruction':'same size, centered alignment, translation only; no rotation or reflection',
 'source_black_pixel_bbox_threshold_128':{'first':[319,16,372,68],'second':[401,16,451,69],'C':[300,129,339,180]},
 'registration_note':'Source black-shape bbox centers are about 80.5px apart; grid centers are about85px apart. Do not align source shapes using grid offset alone. Normalized polygons idealize slight raster/printing distortions.',
 'comparison':'Computed intersection has same five directed edges and notch as C; source scan differs by approximately 1-2px in edge proportions after shape-centered normalization.'
}
(HERE/'second_group_geometry.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

im=Image.new('RGB',(1200,420),'#101B2D')
d=ImageDraw.Draw(im)
f=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',28)
for i,(poly,color,title) in enumerate([(P1,'#42BBD8','图1'),(P2,'#F7B45E','图2'),(C,'#7DE3C0','共同区域 = C')]):
    cx=200+400*i; cy=220; scale=100
    d.rectangle((cx-130,cy-130,cx+130,cy+130),fill='white')
    d.polygon([(cx+x*scale,cy+y*scale) for x,y in poly],fill=color)
    d.text((cx-90,26),title,font=f,fill='white')
d.text((70,370),'归一化轮廓示意：同尺寸、中心对齐，只平移，不旋转。',font=f,fill='#AAB9CC')
im.save(HERE/'second_group_geometry.png')
print(json.dumps(report,ensure_ascii=False))
