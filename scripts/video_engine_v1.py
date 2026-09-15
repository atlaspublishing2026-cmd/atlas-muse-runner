#!/usr/bin/env python3
import os, subprocess, json, urllib.parse, urllib.request, textwrap, shutil
from pathlib import Path

OUT=Path('video_engine_output'); WORK=Path('/tmp/atlas_video_v1')
OUT.mkdir(exist_ok=True); WORK.mkdir(exist_ok=True)
W,H,FPS=1080,1920,30
scenes=[
 ('small kitchen cabinets interior','YOU ALREADY OWN THIS SPACE','There is usable storage hiding under most kitchen cabinets.'),
 ('kitchen cabinet drawer','THE TOE-KICK IS USUALLY EMPTY','That strip beneath the cabinet is normally treated like dead space.'),
 ('kitchen drawer storage','TURN IT INTO A DRAWER','A shallow pull-out can hold trays, linens, baking sheets, or other flat items.'),
 ('small kitchen storage','ZERO EXTRA FLOOR SPACE','The room does not get bigger. The storage does.'),
]

def commons_image(query, dest):
    params=urllib.parse.urlencode({'action':'query','generator':'search','gsrsearch':query+' filetype:bitmap','gsrnamespace':6,'gsrlimit':10,'prop':'imageinfo','iiprop':'url','iiurlwidth':1400,'format':'json','origin':'*'})
    url='https://commons.wikimedia.org/w/api.php?'+params
    req=urllib.request.Request(url,headers={'User-Agent':'AtlasVideoEngine/1.0'})
    data=json.load(urllib.request.urlopen(req,timeout=30))
    pages=list(data.get('query',{}).get('pages',{}).values())
    for p in pages:
        info=(p.get('imageinfo') or [{}])[0]
        img=info.get('thumburl') or info.get('url')
        if img and any(img.lower().split('?')[0].endswith(x) for x in ['.jpg','.jpeg','.png','.webp']):
            try:
                r=urllib.request.Request(img,headers={'User-Agent':'AtlasVideoEngine/1.0'})
                with urllib.request.urlopen(r,timeout=30) as src, open(dest,'wb') as f: shutil.copyfileobj(src,f)
                return p.get('title',''), info.get('descriptionurl','')
            except Exception: pass
    raise RuntimeError('No usable Commons image for '+query)

def run(cmd): subprocess.run(cmd,check=True)

credits=[]; clips=[]
for i,(query,hook,narr) in enumerate(scenes):
    img=WORK/f'scene{i}.jpg'
    title,source=commons_image(query,img); credits.append({'scene':i+1,'title':title,'source':source})
    clip=WORK/f'scene{i}.mp4'; clips.append(clip)
    # 3.4 sec vertical Ken Burns, darkened for readable kinetic type
    vf=(f"scale=1400:-2,crop=1080:1920:(iw-1080)/2:(ih-1920)/2," if False else
        f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,")
    vf += f"zoompan=z='min(zoom+0.0015,1.12)':d=102:s=1080x1920:fps=30,eq=brightness=-0.12:saturation=1.08,"
    safe=hook.replace("'","\\'").replace(':','\\:')
    vf += "drawbox=x=55:y=118:w=970:h=270:color=black@0.48:t=fill," + \
          f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{safe}':fontcolor=white:fontsize=58:x=(w-text_w)/2:y=185:box=0,"
    vf += f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='BUILD IT SMALLER':fontcolor=white@0.9:fontsize=32:x=65:y=1740"
    run(['ffmpeg','-y','-loop','1','-i',str(img),'-vf',vf,'-t','3.4','-r','30','-c:v','libx264','-pix_fmt','yuv420p','-an',str(clip)])

# concatenate scenes
concat=WORK/'concat.txt'; concat.write_text(''.join(f"file '{c.resolve()}'\n" for c in clips))
visual=WORK/'visual.mp4'; run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c:v','libx264','-r','30','-pix_fmt','yuv420p',str(visual)])

script=' '.join(s[2] for s in scenes)+" Would you put hidden drawers under your cabinets?"
voice=WORK/'voice.mp3'
# Edge TTS is free; fall back to espeak if service is unavailable
try:
    run(['edge-tts','--voice','en-US-GuyNeural','--rate','+8%','--text',script,'--write-media',str(voice)])
except Exception:
    wav=WORK/'voice.wav'; run(['espeak','-s','165','-w',str(wav),script]); run(['ffmpeg','-y','-i',str(wav),str(voice)])

final=OUT/'atlas-video-engine-v1-toe-kick.mp4'
# mix narration, add subtle generated music bed, force TikTok-safe output
run(['ffmpeg','-y','-i',str(visual),'-i',str(voice),'-f','lavfi','-i','sine=frequency=110:sample_rate=44100:duration=13.6',
     '-filter_complex','[1:a]volume=1.25[vo];[2:a]volume=0.025[bed];[vo][bed]amix=inputs=2:duration=first[a]',
     '-map','0:v','-map','[a]','-t','13.6','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','128k','-movflags','+faststart',str(final)])

# hard preflight
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,avg_frame_rate,width,height','-of','json',str(final)]))['streams'][0]
assert probe['codec_name']=='h264' and probe['pix_fmt']=='yuv420p' and probe['avg_frame_rate']=='30/1' and probe['width']==1080 and probe['height']==1920, probe
(OUT/'atlas-video-engine-v1-credits.json').write_text(json.dumps(credits,indent=2))
print('ATLAS_VIDEO_ENGINE_ACCEPTANCE_PASS',final,probe)
