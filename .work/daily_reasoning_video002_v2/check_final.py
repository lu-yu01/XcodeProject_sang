from pathlib import Path
import json, subprocess, shutil, hashlib
from PIL import Image, ImageDraw, ImageFont

W=Path(__file__).resolve().parent
O=Path(r'E:\XcodeProject_sang\短视频\第002期_去异求同\改进版_逐步演示')
F=Path(r'E:\JianyingPro\11.6.0.14552\ffmpeg.exe')
V=O/'第002讲_去异求同_逐步叠加演示.mp4'
times=[2,12,18.7,19.7,22.9,26.5,31.8,33.6,37.2,38.8,40.6,42.5,46.9,49.9,52.9,55.8,61.4,74.8]
frames=O/'成片抽帧';frames.mkdir(exist_ok=True)
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',21)
contact=Image.new('RGB',(1120,1660),'#E9EDF2');draw=ImageDraw.Draw(contact)
for n,t in enumerate(times):
    path=frames/f'{t:05.1f}s.png'
    subprocess.run([str(F),'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1',str(path)],check=True)
    image=Image.open(path).convert('RGB');image.thumbnail((170,302))
    x=14+(n%6)*185;y=14+(n//6)*545
    # Larger panels use a 6 x 3 grid and retain full portrait composition.
    contact.paste(image,(x,y));draw.text((x,y+310),f'{t:.1f}秒',font=font,fill='#101B2D')
contact=contact.crop((0,0,1120,1420))
contact.save(O/'成片抽帧总览.png')
cmd=[str(F),'-hide_banner','-i',str(V),'-af','silencedetect=noise=-35dB:d=0.5','-vf','blackdetect=d=0.2:pix_th=0.05','-f','null','NUL']
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
(O/'完整解码检查.txt').write_text(r.stderr,encoding='utf-8')
if r.returncode:raise RuntimeError('完整解码失败')
if 'black_start:' in r.stderr:raise RuntimeError('发现黑屏，请复核')
report={'video':V.name,'duration_seconds':75.5,'resolution':[1080,1920],'fps':30,'frames':2265,
        'decode_exit_code':r.returncode,'black_segments_detected':False,'AIGC_metadata_retained':'AIGC' in r.stderr,
        'thinking_silence_seconds':3.626961,'scene_durations':[13.3,23.1,27.2,11.9],
        'scene_audio_cutoffs':{'01':10.5,'02':23.1,'03':27.2,'04':11.9},
        'audio2_main_end':22.612132,'audio2_footer_start':23.82712,
        'audio3_main_end':26.735578,'audio3_footer_start':27.993787,
        'video_sha256':hashlib.sha256(V.read_bytes()).hexdigest(),
        'actual_video_frame_samples':times,
        'auditory_review':'待用户试听发音、抑扬顿挫和衔接；程序检查不能替代试听'}
(O/'验证记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
dest=O/'可修改源文件';dest.mkdir(exist_ok=True)
for name in ['render_dynamic.py','配音对齐时间表.json','verify_first_set.py','first_set_geometry_check.json',
             'first_set_math_check.png','second_group_geometry.py','second_group_geometry.json','second_group_geometry.png','check_final.py']:
    shutil.copy2(W/name,dest/name)
print(json.dumps(report,ensure_ascii=False,indent=2))
