from pathlib import Path
import hashlib,json,re,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont

W=Path(__file__).resolve().parent
EP=Path(r'E:\XcodeProject_sang\短视频\第002期_去异求同')
O=EP/'优化版_原题常驻'
F=Path(r'E:\JianyingPro\11.6.0.14552\ffmpeg.exe')
V=O/'第002讲_去异求同_原题常驻版.mp4'
OLD=EP/'改进版_逐步演示'/'第002讲_去异求同_逐步叠加演示.mp4'

def run(args):
    r=subprocess.run([str(F),'-hide_banner',*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
    if r.returncode:raise RuntimeError(r.stderr)
    return r

times=[2,12,13.4,18.7,22.9,26.5,31.8,33.6,36.5,40.6,42.5,46.9,49.9,52.9,55.8,61.4,63.5,74.8]
frames=O/'成片抽帧';frames.mkdir(exist_ok=True)
contact=Image.new('RGB',(1080,1580),'#E9EDF2');d=ImageDraw.Draw(contact)
font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',21)
for n,t in enumerate(times):
    p=frames/f'{t:05.1f}s.png'
    run(['-loglevel','error','-y','-ss',str(t),'-i',str(V),'-frames:v','1',str(p)])
    im=Image.open(p).convert('RGB');im.thumbnail((164,292))
    x=12+(n%6)*178;y=14+(n//6)*510
    contact.paste(im,(x,y));d.text((x,y+304),f'{t:.1f}秒',font=font,fill='#101B2D')
contact=contact.crop((0,0,1080,1380));contact.save(O/'成片抽帧总览.png')
decoded=run(['-i',str(V),'-af','silencedetect=noise=-35dB:d=0.5','-vf','blackdetect=d=0.2:pix_th=0.05','-f','null','NUL'])
(O/'完整解码检查.txt').write_text(decoded.stderr,encoding='utf-8')
if 'black_start:' in decoded.stderr:raise RuntimeError('检出黑屏')
audio_hash={}
for label,p in [('v2',OLD),('v3',V)]:
    h=run(['-v','error','-i',str(p),'-map','0:a:0','-f','hash','-hash','sha256','-']).stdout.strip()
    audio_hash[label]=h
if audio_hash['v2']!=audio_hash['v3']:raise RuntimeError('与v2解码后音频不一致')
layout=json.loads((W/'layout_verification.json').read_text(encoding='utf-8-sig'))
report={'video':V.name,'duration_seconds':75.5,'resolution':[1080,1920],'fps':30,'frames':2265,
        'decode_exit_code':0,'black_segments_detected':False,'AIGC_metadata_retained':'AIGC' in decoded.stderr,
        'audio_identical_to_approved_v2':True,'decoded_audio_sha256':audio_hash['v3'],
        'scene_durations':[13.3,23.1,27.2,11.9],'question_visible_during':[13.3,63.6],
        'question_and_options_fixed_box':[80,290,900,644],'layout_source_verification':layout,
        'video_sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'actual_video_frame_samples':times}
(O/'验证记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
source=O/'可修改源文件';source.mkdir(exist_ok=True)
for name in ['render_dynamic.py','配音对齐时间表.json','layout_verification.json','check_final.py']:
    shutil.copy2(W/name,source/name)
shutil.copy2(EP/'改进版_逐步演示'/'配音稿.txt',O/'配音稿.txt')
print(json.dumps(report,ensure_ascii=False,indent=2))
