from pathlib import Path
import argparse, json, shutil
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BG = '#101B2D'
PANEL = '#1A2A40'
WHITE = '#F3F6FA'
MUTED = '#AAB9CC'
MINT = '#7DE3C0'
GOLD = '#F7CC79'
REGULAR = Path(r'C:\Windows\Fonts\msyh.ttc')
BOLD = Path(r'C:\Windows\Fonts\msyhbd.ttc')
METRICS = []

def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else REGULAR), size)

def text(im, content, x, y, size, color=WHITE, bold=False, width=836):
    f = font(size, bold)
    box = ImageDraw.Draw(im).textbbox((x,y), content, font=f)
    if box[2] > x + width or box[0] < 0 or box[2] > 930:
        raise ValueError(f'文字越界: {content}: {box}')
    if box[3] > 1575:
        raise ValueError(f'文字过低: {content}: {box}')
    ImageDraw.Draw(im).text((x,y), content, font=f, fill=color)
    METRICS.append({'text':content, 'box':list(box), 'font_size':size})

def wrapped(im, content, x, y, size, width=836, color=WHITE, line_height=None):
    f=font(size)
    d=ImageDraw.Draw(im)
    rows=[]
    line=''
    for char in content:
        if d.textlength(line+char,font=f)>width:
            rows.append(line)
            line=char
        else:
            line+=char
    if line: rows.append(line)
    for n,row in enumerate(rows):
        text(im,row,x,y+n*(line_height or int(size*1.45)),size,color,width=width)
    return len(rows)*(line_height or int(size*1.45))

def panel(im, box, color=PANEL):
    ImageDraw.Draw(im).rectangle(box, fill=color)

def base(data, step, progress):
    im=Image.new('RGB',(1080,1920),BG)
    d=ImageDraw.Draw(im)
    d.rectangle((84,118,126,125), fill=MINT)
    text(im,data['series'],84,163,34,MUTED)
    text(im,f"第{data['episode']}期",745,165,30,MINT,width=180)
    d.rectangle((84,235,920,238), fill='#304157')
    if progress: d.rectangle((84,235,84+progress*209,238),fill=MINT)
    text(im,step,84,270,28,GOLD)
    text(im,data['source_label'],84,1480,28,MUTED)
    text(im,'每天一道题，讲透一个方法。',84,1530,28,MUTED)
    return im

def place_crop(im, source, crop, x, y, width):
    pic=source.crop(tuple(crop)).convert('RGB')
    height=round(pic.height*width/pic.width)
    im.paste(pic.resize((width,height),Image.Resampling.LANCZOS),(x,y))
    return (x,y,x+width,y+height)

def main():
    ap=argparse.ArgumentParser(description='第002期四卡生成器；须明确输出目录以免覆盖历史文件。')
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--lesson',default=str(HERE/'lesson.json'))
    args=ap.parse_args()
    lp=Path(args.lesson).resolve()
    data=json.loads(lp.read_text(encoding='utf-8-sig'))
    out=Path(args.output_dir).resolve()
    out.mkdir(parents=True,exist_ok=True)
    source_path=(lp.parent/data['image_path']).resolve()
    source=Image.open(source_path).convert('RGB')
    shutil.copy2(source_path,out/'原题.png') if source_path != out/'原题.png' else None
    generated=[]

    im=base(data,'本期主题',0)
    text(im,data['cover_title'][0],84,355,95,bold=True)
    text(im,data['cover_title'][1],84,500,85,MINT,True)
    panel(im,(84,750,920,1230))
    place_crop(im,source,(0,0,source.width,source.height),110,812,784)
    text(im,'第002讲 · 去异求同',84,1300,51,GOLD,True)
    im.save(out/'00_视频封面.png')

    im=base(data,'01 / 04    先做一道题',1)
    text(im,data['cards'][0]['title'][0],84,353,83,bold=True)
    text(im,data['cards'][0]['title'][1],84,468,83,MINT,True)
    wrapped(im,data['question'],84,605,31,line_height=46)
    panel(im,(84,775,920,1170))
    place_crop(im,source,(0,0,source.width,source.height),102,801,800)
    text(im,'先做题，停 3 秒',84,1250,54,WHITE,True)
    text(im,'观察：前两图怎样得到第三图？',84,1365,39,GOLD)
    im.save(out/data['cards'][0]['file'])
    generated.append(im.copy())

    im=base(data,'02 / 04    第一组找规律',2)
    text(im,data['cards'][1]['title'][0],84,353,83,bold=True)
    text(im,data['cards'][1]['title'][1],84,468,71,MINT,True)
    panel(im,(84,640,920,1080))
    text(im,'前两图 → 第三图',110,668,36,MUTED,width=780)
    box=place_crop(im,source,data['crops']['first_set'],110,752,784)
    # Highlight the original result; never invent unverified line intersections.
    d=ImageDraw.Draw(im)
    result_x=110+round(169/254*784)
    d.rectangle((result_x,box[1],box[2]-2,box[3]-1),outline=MINT,width=6)
    text(im,'原位置叠加，不旋转',84,1165,48,WHITE,True)
    text(im,'共有的留下，独有的去掉',84,1260,47,WHITE,True)
    text(im,'第一组，比较共有“线条”。',84,1370,36,GOLD)
    im.save(out/data['cards'][1]['file'])
    generated.append(im.copy())

    im=base(data,'03 / 04    第二组用规律',3)
    text(im,data['cards'][2]['title'][0],84,353,83,bold=True)
    text(im,data['cards'][2]['title'][1],84,468,63,MINT,True)
    panel(im,(84,640,920,1050))
    text(im,'同样原位叠加',110,665,36,MUTED,width=780)
    place_crop(im,source,data['crops']['second_set'],110,748,784)
    panel(im,(84,1110,920,1375))
    place_crop(im,source,data['crops']['option_c'],120,1140,210)
    text(im,'答案 C',384,1145,64,MINT,True,width=500)
    text(im,'两图都覆盖的部分',384,1245,38,WHITE,width=500)
    text(im,'第二组，比较共同“黑色区域”。',84,1410,34,GOLD)
    im.save(out/data['cards'][2]['file'])
    generated.append(im.copy())

    im=base(data,'04 / 04    记住三步方法',4)
    text(im,data['cards'][3]['title'][0],84,353,90,MINT,True)
    text(im,data['cards'][3]['title'][1],84,485,55,WHITE,True)
    for n,(title,desc) in enumerate(data['summary_steps'],1):
        top=655+(n-1)*218
        panel(im,(84,top,920,top+188))
        text(im,f'{n:02}',112,top+29,61,MINT,True,width=110)
        text(im,title,240,top+26,48,WHITE,True,width=650)
        text(im,desc,240,top+106,31,MUTED,width=650)
    text(im,'位置和方向不变，别擅自旋转。',84,1405,37,GOLD)
    im.save(out/data['cards'][3]['file'])
    generated.append(im.copy())

    contact=Image.new('RGB',(1080,560),'#E9EDF2')
    cd=ImageDraw.Draw(contact)
    cd.text((24,17),'第002期 · 四张内容题卡预览',font=font(29,True),fill=BG)
    for n,img in enumerate(generated):
        img.thumbnail((250,1000),Image.Resampling.LANCZOS)
        contact.paste(img,(24+n*262,70))
    contact.save(out/'题卡总览.png')
    (out/'文字边界检查.json').write_text(json.dumps(METRICS,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=[f"第{data['episode']}期｜{data['topic']}｜逐页口播稿",'',
           '四段分别生成，sangsang 优先使用保留口音版。第一段结束后在时间轴实际留3秒，不朗读停顿说明。','']
    for n,card in enumerate(data['cards'],1):
        lines.extend([f"【{n:02}｜{card['label']}】",card['voice'],''])
    (out/'配音稿.txt').write_text('\n'.join(lines),encoding='utf-8-sig')
    src=out/'可修改源文件'
    src.mkdir(exist_ok=True)
    for original,name in [(Path(__file__).resolve(),'build.py'),(lp,'lesson.json'),(source_path,'原题.png')]:
        if original != src/name: shutil.copy2(original,src/name)
    (out/'题卡制作说明.txt').write_text(
        '第002期 去异求同｜题卡素材\n'
        '题目与解析由用户提供，未核实考试出处，不标注为真题。\n'
        '00封面；01完整原题和A—D；02第一组原图放大并高亮第三图；03第二组原图放大和原C选项；04方法总结。\n'
        '原题裁剪后等比例放大，不修改图形位置、方向和轮廓。未绘制未经核实的精确叠加图；原图第三图与C选项配合口播解释。\n'
        '首图原始分辨率554×236，放大后清晰度受原始图像限制。\n'
        '所有正片与封面为1080×1920，颜色沿用第001期。配音与视频由主任务继续完成。\n'
        '修改源位于可修改源文件，修改lesson.json后用python build.py --output-dir 新目录生成，注意原题裁剪坐标需随源图调整。\n',encoding='utf-8-sig')
    print(json.dumps({'output_dir':str(out),'card_count':len(generated),'png_size':[1080,1920],'metrics_count':len(METRICS)},ensure_ascii=False))

if __name__=='__main__': main()
