"""第002讲逐步叠加演示。以流方式送帧给FFmpeg，避免将全部帧存入内存。"""
from pathlib import Path
from functools import lru_cache
import argparse, json, math, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
EP=Path(r'E:\XcodeProject_sang\短视频\第002期_去异求同')
FFMPEG=Path(r'E:\JianyingPro\11.6.0.14552\ffmpeg.exe')
BG='#101B2D'; PANEL='#1A2A40'; WHITE='#F3F6FA'; MUTED='#AAB9CC'
GREEN='#53BD8E'; MINT='#7DE3C0'; GOLD='#F7CC79'
BLUE='#179EC4'; ORANGE='#F28B30'
FONT=Path(r'C:\Windows\Fonts\msyh.ttc')
BOLD=Path(r'C:\Windows\Fonts\msyhbd.ttc')
SIZE=(1080,1920)

@lru_cache(maxsize=64)
def font(size,bold=False):return ImageFont.truetype(str(BOLD if bold else FONT),size)

def tx(im,s,xy,size=36,color=WHITE,bold=False):
    d=ImageDraw.Draw(im)
    box=d.textbbox(xy,s,font=font(size,bold))
    if box[2]>925 or box[3]>1560:raise ValueError(f'文字超出安全区: {s}, {box}')
    d.text(xy,s,font=font(size,bold),fill=color)

def rgba(hexcolor,alpha=255):
    return tuple(int(hexcolor[i:i+2],16) for i in (1,3,5))+(round(alpha),)

def clamp(x):return min(1,max(0,x))
def ease(x):
    x=clamp(x)
    return x*x*(3-2*x)

def header(step,title,subtitle):
    im=Image.new('RGB',SIZE,BG)
    d=ImageDraw.Draw(im)
    d.rectangle((80,106,126,114),fill=MINT)
    tx(im,'每日一讲 · 判断推理',(80,145),32,MUTED)
    tx(im,'第002期',(748,147),29,MINT)
    d.line((80,215,900,215),fill='#304157',width=3)
    d.line((80,215,80+205*step,215),fill=MINT,width=3)
    tx(im,f'{step:02} / 04　逐步看懂去异求同',(80,250),28,GOLD)
    tx(im,title,(80,312),63,WHITE,True)
    tx(im,subtitle,(80,400),36,MINT)
    tx(im,'题目与解析：用户提供',(80,1486),26,MUTED)
    tx(im,'每天一道题，讲透一个方法。',(80,1524),26,MUTED)
    return im

def paste_fit(im,pic,box):
    x,y,w,h=box
    factor=min(w/pic.width,h/pic.height)
    dest=pic.resize((round(pic.width*factor),round(pic.height*factor)),Image.Resampling.LANCZOS)
    im.paste(dest,(x+(w-dest.width)//2,y+(h-dest.height)//2))

@lru_cache(maxsize=80)
def first_layer(kind,size,color):
    # All linework uses one 88×88 coordinate system and the same stroke width.
    scale=size*3/88
    s=size*3
    im=Image.new('RGBA',(s,s),(0,0,0,0)); d=ImageDraw.Draw(im)
    col=rgba(color); width=max(2,round(1.65*scale))
    pp=lambda pts:[(round(x*scale),round(y*scale)) for x,y in pts]
    bb=lambda cx,cy,r:tuple(round(v*scale) for v in (cx-r,cy-r,cx+r,cy+r))
    if kind=='first':
        d.ellipse(bb(44,44,28),outline=col,width=width)
        d.line(pp([(72,16),(16,16),(16,44),(44,44),(44,72),(72,72)]),fill=col,width=width,joint='curve')
    elif kind=='second':
        d.line(pp([(16,44),(44,44),(44,16),(72,16),(72,72),(16,72)]),fill=col,width=width,joint='curve')
        d.arc(bb(44,44,28),270,450,fill=col,width=width)
        d.arc(bb(72,16,28),90,180,fill=col,width=width)
        d.arc(bb(72,72,28),180,270,fill=col,width=width)
    elif kind=='arc':d.arc(bb(44,44,28),270,450,fill=col,width=width+3)
    elif kind=='top':d.line(pp([(44,16),(72,16)]),fill=col,width=width+3)
    elif kind=='bottom':d.line(pp([(44,72),(72,72)]),fill=col,width=width+3)
    elif kind=='middle':d.line(pp([(16,44),(44,44)]),fill=col,width=width+3)
    elif kind=='common':
        d.arc(bb(44,44,28),270,450,fill=col,width=width)
        for line in [[(44,16),(72,16)],[(44,72),(72,72)],[(16,44),(44,44)]]:
            d.line(pp(line),fill=col,width=width)
    return im.resize((size,size),Image.Resampling.LANCZOS)

POLYS={
    'first':[(-1,-1),(0,-1),(1,0),(0,0),(0,1),(-1,1)],
    'second':[(0,-1),(1,-1),(0,0),(1,0),(1,1),(0,1),(-1,0)],
    'common':[(0,-1),(.5,-.5),(0,0),(0,1),(-1,0)],
}

@lru_cache(maxsize=20)
def second_layer(kind,size,color):
    s=size*3; im=Image.new('RGBA',(s,s),(0,0,0,0));d=ImageDraw.Draw(im)
    points=[(round(s*(.5+x*.34)),round(s*(.5+y*.34))) for x,y in POLYS[kind]]
    d.polygon(points,fill=rgba(color))
    return im.resize((size,size),Image.Resampling.LANCZOS)

def layer(im,asset,xy,opacity=1):
    if opacity<=0:return
    if opacity<1:
        asset=asset.copy()
        asset.putalpha(asset.getchannel('A').point(lambda a:round(a*opacity)))
    im.paste(asset,(round(xy[0]),round(xy[1])),asset)

def board(im):ImageDraw.Draw(im).rounded_rectangle((80,490,900,1260),radius=15,fill='#FFFFFF')

def caption(im,s,s2=None):
    tx(im,s,(80,1320),38,GOLD,True)
    if s2:tx(im,s2,(80,1383),32,WHITE)

def source_assets():
    pic=Image.open(EP/'原题.png').convert('RGB')
    return {'question':pic,'third':pic.crop((170,0,254,88)),
            'choices':pic.crop((108,112,446,pic.height)),
            'c':pic.crop((278,112,362,198))}

def default_timings(d2,d3):
    return {
        'first':{'move_start':d2*.19,'move_end':d2*.19+2,
                 'green':d2*.29,'arc':d2*.34,'top_bottom':d2*.42,'middle':d2*.52,
                 'fade_start':d2*.73,'fade_end':d2*.81,'compare':d2*.85},
        'second':{'color':.7,'move_start':d3*.18,'move_end':d3*.18+2,
                  'green':d3*.30,'fade_start':d3*.38,'fade_end':d3*.46,
                  'left_tip':d3*.51,'upper_corner':d3*.56,'right_edge':d3*.61,
                  'choices':d3*.70,'answer':d3*.79,'recap':d3*.88}}

def render_scene1(t,duration,assets):
    im=header(1,'这道题，你选哪一个？','先观察：每组前两图，怎样得到第三图？')
    tx(im,'从四个选项中，选择最合适的一项',(80,520),34,WHITE)
    tx(im,'填入问号处。',(80,570),34,WHITE)
    paste_fit(im,assets['question'],(80,690,820,400))
    if t>=duration-3:
        number=max(1,math.ceil(duration-t))
        ImageDraw.Draw(im).ellipse((390,1130,550,1290),fill=MINT)
        # Countdown is visual only; the audio is silent for the thinking interval.
        tx(im,str(number),(445,1150),74,BG,True)
        caption(im,'给你 3 秒，先自己判断。')
    else:caption(im,'先别看答案，找出两组共同的规律。')
    return im

def render_scene2(t,duration,assets,T):
    im=header(2,'第一组：看共同的线条','蓝色是图一，橙色是图二。')
    board(im)
    if t>=T['compare']:
        tx(im,'叠加结果',(134,535),34,'#405469',True)
        tx(im,'原来的图三',(570,535),34,'#405469',True)
        layer(im,first_layer('common',360,GREEN),(80,650))
        paste_fit(im,assets['third'],(540,650,360,360))
        tx(im,'＝',(450,774),66,'#405469',True)
        tx(im,'轮廓、方向和位置相同',(230,1125),35,'#405469',True)
        caption(im,'去异求同：共同的留下，独有的去掉。')
        return im
    move=ease((t-T['move_start'])/(T['move_end']-T['move_start']))
    pos1=(80+210*move,625); pos2=(500-210*move,625)
    fade=1-ease((t-T['fade_start'])/(T['fade_end']-T['fade_start']))
    opacity=1 if move<1 else .68*fade
    layer(im,first_layer('first',400,BLUE),pos1,opacity)
    layer(im,first_layer('second',400,ORANGE),pos2,opacity)
    if move<1:
        tx(im,'图一',(200,545),35,BLUE,True)
        tx(im,'图二',(620,545),35,ORANGE,True)
        tx(im,'对齐叠加，保持方向不变',(220,1130),36,'#405469',True)
        caption(im,'把两幅图移到同一个位置。')
    else:
        tx(im,'重合部分标成绿色',(290,540),37,GREEN,True)
        layer(im,first_layer('common',400,GREEN),(290,625),
              .4*ease((t-T.get('green',T['arc']))/.45))
        states=[('arc',T['arc']),('top',T['top_bottom']),('bottom',T['top_bottom']),('middle',T['middle'])]
        for kind,start in states:
            a=ease((t-start)/.45)
            layer(im,first_layer(kind,400,GREEN),(290,625),a)
        if t<T['top_bottom']:label='先看右边的半圆弧'
        elif t<T['middle']:label='再看上下两条短横线'
        elif t<T['fade_start']:label='还有左边中间的横线'
        else:label='其余线条，全部去掉'
        tx(im,label,(215,1125),39,'#405469',True)
        caption(im,'两幅图里都有，才保留。')
    return im

def draw_pointer(im,anchor,end,label,label_xy):
    d=ImageDraw.Draw(im)
    d.line((*anchor,*end),fill=GREEN,width=5)
    r=10;d.ellipse((anchor[0]-r,anchor[1]-r,anchor[0]+r,anchor[1]+r),fill=GREEN)
    tx(im,label,label_xy,30,'#176A4B',True)

def render_scene3(t,duration,assets,T):
    im=header(3,'第二组：看共同的区域','位置和方向不变，只留下共同区域。')
    board(im)
    move=ease((t-T['move_start'])/(T['move_end']-T['move_start']))
    if t>=T['choices']:
        layer(im,second_layer('common',365,GREEN),(310,510))
        tx(im,'留下的轮廓',(348,875),36,'#405469',True)
        paste_fit(im,assets['choices'],(115,970,750,280))
        if t>=T['answer']:
            # Exact C cell bounds in the source choices crop: x170..254 of338.
            k=min(750/assets['choices'].width,280/assets['choices'].height)
            rendered_w=round(assets['choices'].width*k)
            rendered_h=round(assets['choices'].height*k)
            xx=115+(750-rendered_w)//2; yy=970+(280-rendered_h)//2
            c1=xx+round((278-108)*k);c2=xx+round((362-108)*k)
            ImageDraw.Draw(im).rectangle((c1,yy,c2,yy+rendered_h),outline=GREEN,width=7)
        if t>=T['recap']:
            caption(im,'答案 C：左边求共同线条，','右边求共同区域，规则都是去异求同。')
        else:caption(im,'逐一对照选项，轮廓与朝向都要相同。')
        return im
    pos1=(80+210*move,625);pos2=(500-210*move,625)
    fade=1-ease((t-T['fade_start'])/(T['fade_end']-T['fade_start']))
    col1=BLUE if t>=T.get('color',.7) else '#111111';col2=ORANGE if t>=T.get('color',.7) else '#111111'
    layer(im,second_layer('first',400,col1),pos1,1 if move<1 else .6*fade)
    layer(im,second_layer('second',400,col2),pos2,1 if move<1 else .6*fade)
    if move<1:
        tx(im,'图一',(200,545),35,BLUE,True)
        tx(im,'图二',(620,545),35,ORANGE,True)
        tx(im,'同尺寸、同中心，只平移',(220,1130),35,'#405469',True)
        caption(im,'这次比较的是黑色区域。')
    else:
        g=ease((t-T['green'])/.7)
        layer(im,second_layer('common',400,GREEN),(290,625),g)
        tx(im,'绿色 = 两图共同覆盖',(255,540),37,GREEN,True)
        if t>=T['left_tip']:
            draw_pointer(im,(354,825),(200,825),'左侧尖角',(130,765))
        if t>=T['upper_corner']:
            draw_pointer(im,(558,757),(750,700),'右上拐角',(690,635))
        if t>=T['right_edge']:
            draw_pointer(im,(490,916),(730,1050),'右下竖边',(680,1075))
        if t<T['fade_start']:caption(im,'共同覆盖的区域，标成绿色。')
        else:caption(im,'只留下绿色，去掉各自多出来的部分。')
    return im

def render_scene4(t,duration):
    im=Image.open(EP/'04_记住三步方法.png').convert('RGB')
    n=min(2,int(t/(duration/3)))
    top=655+n*218
    ImageDraw.Draw(im).rectangle((84,top,920,top+188),outline=MINT,width=7)
    return im

def find_audio(name,explicit=None):
    if explicit:
        p=Path(explicit)
        if p.exists():return p
        raise FileNotFoundError(p)
    places=[HERE/name,EP/'v2'/name,EP/'改进版_逐步演示'/name,EP/name]
    for p in places:
        if p.exists():return p
    raise FileNotFoundError('未找到配音：'+name+'；可用--audio2/--audio3指定。')

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument('--durations',required=True,help='四段画面与拼接音频时长，如13.3,24,26,11.9')
    p.add_argument('--output-dir',required=True)
    p.add_argument('--fps',type=int,default=15)
    p.add_argument('--ffmpeg',default=str(FFMPEG))
    p.add_argument('--timings-json')
    p.add_argument('--audio2');p.add_argument('--audio3')
    p.add_argument('--keyframes-only',action='store_true')
    return p.parse_args()

def main():
    args=parse_args(); durations=[float(x.strip()) for x in args.durations.split(',')]
    if len(durations)!=4 or any(x<=3 for x in durations):raise ValueError('需要四个大于3秒的时长')
    if args.fps<=0:raise ValueError('fps须为正数')
    out=Path(args.output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    if out==EP.resolve():raise ValueError('请使用改进版子目录，避免混入旧成品')
    assets=source_assets()
    T=default_timings(durations[1],durations[2])
    if args.timings_json:
        override=json.loads(Path(args.timings_json).read_text(encoding='utf-8-sig'))
        for key in ('first','second'):T[key].update(override.get(key,{}))
    (out/'动画时间表.json').write_text(json.dumps({'durations':durations,'local_scene_timings':T,'fps':args.fps,'output_fps':30},ensure_ascii=False,indent=2),encoding='utf-8')
    def frame(scene,t):
        if scene==0:return render_scene1(t,durations[0],assets)
        if scene==1:return render_scene2(t,durations[1],assets,T['first'])
        if scene==2:return render_scene3(t,durations[2],assets,T['second'])
        return render_scene4(t,durations[3])
    stages=[(0,2),(0,durations[0]-1.5),(1,max(0,T['first']['move_start']-.5)),(1,T['first']['move_start']+1),
            (1,T['first']['middle']+.8),(1,T['first']['compare']+.2),
            (2,max(0,T['second']['move_start']-.5)),(2,T['second']['move_start']+1),
            (2,T['second']['right_edge']+.8),(2,T['second']['answer']+.4),(3,2),(3,durations[3]-.5)]
    contact=Image.new('RGB',(1080,1580),'#E9EDF2')
    d=ImageDraw.Draw(contact);d.text((18,10),'第002讲 · 动态版关键画面',font=font(28,True),fill=BG)
    for n,(scene,t) in enumerate(stages):
        fr=frame(scene,min(durations[scene]-.05,t))
        fr.resize((250,444),Image.Resampling.LANCZOS).save(out/f'关键帧_{n+1:02}.png')
        x=18+(n%4)*266;y=58+(n//4)*502
        contact.paste(fr.resize((250,444),Image.Resampling.LANCZOS),(x,y))
        d.text((x,y+448),f'{scene+1}段 · {t:.1f}秒',font=font(21),fill=BG)
    contact.save(out/'动态关键帧总览.png')
    if args.keyframes_only:
        print('关键帧完成：'+str(out/'动态关键帧总览.png'));return
    audios=[find_audio('002_01_原始配音.mp3'),find_audio('002_v2_02_原始配音.mp3',args.audio2),
            find_audio('002_v2_03_原始配音.mp3',args.audio3),find_audio('002_04_原始配音.mp3')]
    # Each original export remains intact and keeps its own provenance metadata.
    original_dir=out/'原始配音';original_dir.mkdir(exist_ok=True)
    for p in audios:
        if p.resolve()!=(original_dir/p.name).resolve():shutil.copy2(p,original_dir/p.name)
    total=sum(durations)
    filters=[f'[0:v]fps=30[v]',
             f'[1:a]atrim=duration=10.5,asetpts=PTS-STARTPTS,apad=whole_dur={durations[0]:.6f},atrim=duration={durations[0]:.6f}[a0]',
             f'[2:a]atrim=duration={durations[1]:.6f},asetpts=PTS-STARTPTS[a1]',
             f'[3:a]atrim=duration={durations[2]:.6f},asetpts=PTS-STARTPTS[a2]',
             f'[4:a]atrim=duration={durations[3]:.6f},asetpts=PTS-STARTPTS[a3]',
             '[a0][a1][a2][a3]concat=n=4:v=0:a=1[a]']
    dest=out/'第002讲_去异求同_逐步叠加演示.mp4'
    command=[args.ffmpeg,'-hide_banner','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1080x1920','-framerate',str(args.fps),'-i','pipe:0']
    for p in audios:command+=['-i',str(p)]
    command+=['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-map_metadata','1',
              '-t',f'{total:.6f}','-c:v','h264_mf','-b:v','6M','-pix_fmt','yuv420p','-r','30',
              '-c:a','aac','-b:a','192k','-movflags','+use_metadata_tags+faststart',str(dest)]
    log=out/'渲染日志.txt'
    boundaries=[0]
    for duration in durations:boundaries.append(boundaries[-1]+duration)
    with log.open('w',encoding='utf-8') as lf:
        proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=lf)
        try:
            total_frames=math.ceil(total*args.fps)
            scene=0
            for n in range(total_frames):
                t=n/args.fps
                while scene<3 and t>=boundaries[scene+1]:scene+=1
                proc.stdin.write(frame(scene,t-boundaries[scene]).tobytes())
                if n and n%(args.fps*10)==0:print(f'已送入 {t:.0f}/{total:.1f} 秒画面',flush=True)
            proc.stdin.close()
            code=proc.wait()
        except Exception:
            proc.kill();proc.wait();raise
    if code:raise RuntimeError(f'FFmpeg退出码{code}，见{log}')
    print('成片完成：'+str(dest),flush=True)

if __name__=='__main__':main()
