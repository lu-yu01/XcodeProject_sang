"""First-set mathematical redraw and visual audit; never mutates the original."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

HERE=Path(__file__).resolve().parent
SOURCE=Path(r'E:\XcodeProject_sang\短视频\第002期_去异求同\原题.png')
SCALE=10
W=88*SCALE
STROKE=18
REGULAR=Path(r'C:\Windows\Fonts\msyh.ttc')
BOLD=Path(r'C:\Windows\Fonts\msyhbd.ttc')

FIRST=[(72,16),(16,16),(16,44),(44,44),(44,72),(72,72)]
SECOND=[(16,44),(44,44),(44,16),(72,16),(72,72),(16,72)]
COMMON_LINES=[[(44,16),(72,16)],[(44,72),(72,72)],[(16,44),(44,44)]]

def pts(items):return [(round(x*SCALE),round(y*SCALE)) for x,y in items]
def bb(cx,cy,r):return tuple(round(v*SCALE) for v in (cx-r,cy-r,cx+r,cy+r))
def shape_mask(which):
    im=Image.new('L',(W,W),0)
    d=ImageDraw.Draw(im)
    if which==1:
        d.ellipse(bb(44,44,28),outline=255,width=STROKE)
        d.line(pts(FIRST),fill=255,width=STROKE,joint='curve')
    elif which==2:
        d.line(pts(SECOND),fill=255,width=STROKE,joint='curve')
        d.arc(bb(44,44,28),270,450,fill=255,width=STROKE)
        d.arc(bb(72,16,28),90,180,fill=255,width=STROKE)
        d.arc(bb(72,72,28),180,270,fill=255,width=STROKE)
    elif which==3:
        d.arc(bb(44,44,28),270,450,fill=255,width=STROKE)
        for line in COMMON_LINES:d.line(pts(line),fill=255,width=STROKE)
    return im

def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else REGULAR),size)
def labeled_text(canvas,s,xy,size=32,color='#101B2D',bold=False):
    ImageDraw.Draw(canvas).text(xy,s,font=font(size,bold),fill=color)

def white_shape(mask,color='black'):
    result=Image.new('RGB',mask.size,'white')
    result.paste(color,mask=mask)
    return result

def main():
    source=Image.open(SOURCE).convert('RGB')
    masks=[shape_mask(n) for n in (1,2,3)]
    assets=HERE/'first_set_assets'
    assets.mkdir(exist_ok=True)
    for n,mask in enumerate(masks,1):
        rgba=Image.new('RGBA',(W,W),(0,0,0,255))
        rgba.putalpha(mask)
        rgba.save(assets/f'first_{n}.png')

    canvas=Image.new('RGB',(1320,1300),'#E9EDF2')
    labeled_text(canvas,'第一组数学重绘核对', (38,24),42,bold=True)
    labeled_text(canvas,'上：原图裁剪　　下：88 × 88 坐标重绘', (38,83),27)
    crops=[(0,0,85,86),(85,0,170,86),(170,0,254,86)]
    lefts=[42,482,922]
    for idx,(crop,mask,x) in enumerate(zip(crops,masks,lefts),1):
        labeled_text(canvas,f'图{idx}',(x,136),30,bold=True)
        pic=source.crop(crop)
        factor=min(355/pic.width,355/pic.height)
        pic=pic.resize((round(pic.width*factor),round(pic.height*factor)),Image.Resampling.LANCZOS)
        canvas.paste(pic,(x+(355-pic.width)//2,185+(355-pic.height)//2))
        redraw=white_shape(mask).resize((355,355),Image.Resampling.LANCZOS)
        canvas.paste(redraw,(x,625))
        ImageDraw.Draw(canvas).rectangle((x,625,x+354,979),outline='#63768B',width=2)
    labeled_text(canvas,'原图', (42,550),27,color='#63768B')
    labeled_text(canvas,'重绘', (42,590),27,color='#63768B')
    labeled_text(canvas,'共同部分：右半圆弧 + 右上短横 + 右下短横 + 左中短横', (38,1030),33,bold=True)
    labeled_text(canvas,'第一图：完整圆 + 折线；第二图：右半圆弧 + 两条内弧 + 折线。',(38,1090),29)
    labeled_text(canvas,'保持位置与方向；原图为低分辨率位图，线宽和间距有像素级差异。',(38,1140),29)
    labeled_text(canvas,'本核对图不替换既有题卡或视频。',(38,1200),25,color='#63768B')
    canvas.save(HERE/'first_set_math_check.png')

    intersection=ImageChops.darker(masks[0],masks[1])
    expected=masks[2]
    # Stroke joins and tangencies can create one-pixel fringes. Audit at 1 logical pixel tolerance.
    extra=ImageChops.subtract(intersection,expected.filter(ImageFilter.MaxFilter(21)))
    missing=ImageChops.subtract(expected,intersection.filter(ImageFilter.MaxFilter(21)))
    extra_pixels=sum(v>0 for v in extra.getdata())
    missing_pixels=sum(v>0 for v in missing.getdata())
    report={
        'coordinate_canvas':[88,88],
        'source_crops':crops,
        'first':{'circle':{'center':[44,44],'radius':28},'polyline':FIRST},
        'second':{'polyline':SECOND,'arcs':[{'center':[44,44],'radius':28,'angles':[270,450]},{'center':[72,16],'radius':28,'angles':[90,180]},{'center':[72,72],'radius':28,'angles':[180,270]}]},
        'common':{'arc':{'center':[44,44],'radius':28,'angles':[270,450]},'lines':COMMON_LINES},
        'raster_check':{'scale':SCALE,'stroke_in_logical_pixels':STROKE/SCALE,'tolerance_in_logical_pixels':1,'extra_pixels_outside_tolerance':extra_pixels,'missing_pixels_outside_tolerance':missing_pixels},
        'visual_review':'生成代理已对照原图检查：圆、折线、两条内弧及共有结果的构成和方向一致；原图像素间距与理想88坐标不完全相同。'
    }
    (HERE/'first_set_geometry_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report['raster_check']))

if __name__=='__main__':main()
