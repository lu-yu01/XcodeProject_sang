from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / '短视频' / '第002期_去异求同'
FFMPEG = r'E:\JianyingPro\11.6.0.14552\ffmpeg.exe'
OUTPUT = ASSETS / '第002讲_去异求同_sangsang口音版.mp4'
cards = ['01_先做一道题.png', '02_第一组找规律.png', '03_第二组用规律.png', '04_记住三步方法.png']
durations = [13.3, 12.0, 12.6, 11.9]
audio_trims = [10.5, 12.0, 12.6, 11.9]
args = [FFMPEG, '-hide_banner', '-y']
for card, duration in zip(cards, durations):
    args += ['-loop', '1', '-framerate', '30', '-t', str(duration), '-i', str(ASSETS / card)]
for n in range(1, 5):
    args += ['-i', str(ASSETS / f'002_{n:02d}_原始配音.mp3')]
filters = [f'[{i}:v]format=yuv420p,setpts=PTS-STARTPTS[v{i}]' for i in range(4)]
filters += ['[v0][v1][v2][v3]concat=n=4:v=1:a=0[v]']
for i, trim in enumerate(audio_trims):
    pad = ',apad=pad_dur=2.8' if i == 0 else ''
    filters += [f'[{i+4}:a]atrim=duration={trim},asetpts=PTS-STARTPTS{pad}[a{i}]']
filters += ['[a0][a1][a2][a3]concat=n=4:v=0:a=1[a]']
args += ['-filter_complex', ';'.join(filters), '-map', '[v]', '-map', '[a]', '-map_metadata', '4', '-c:v', 'h264_mf', '-b:v', '5M', '-r', '30', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+use_metadata_tags+faststart', str(OUTPUT)]
subprocess.run(args, check=True)
(ASSETS / '剪辑时间表.json').write_text(json.dumps({'cards': cards, 'card_seconds': durations, 'source_audio_trim_seconds': audio_trims, 'first_card_added_silence_seconds': 2.8, 'total_seconds': sum(durations), 'output': OUTPUT.name, 'metadata': 'Copy AIGC from first input; original metadata for all four audio sources retained in source exports.'}, ensure_ascii=False, indent=2), encoding='utf-8')
