from PIL import Image, ImageDraw, ImageFont
import math, os, subprocess

W,H=1080,1920
FPS=30
DUR=9
OUT='tomorrow_media'
os.makedirs(OUT, exist_ok=True)

BG=(8,18,26)
PANEL=(15,31,43)
TEAL=(78,226,203)
WHITE=(240,246,248)
MUTED=(156,177,187)
ACCENT=(255,183,77)
RED=(255,98,98)

try:
    FONT_B=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',72)
    FONT_M=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',48)
    FONT_S=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',34)
except:
    FONT_B=FONT_M=FONT_S=None

def ease(t):
    t=max(0,min(1,t)); return 1-(1-t)**3

def centered(draw,text,y,font,fill,maxw=980):
    box=draw.multiline_textbbox((0,0),text,font=font,spacing=10,align='center')
    x=(W-(box[2]-box[0]))/2
    draw.multiline_text((x,y),text,font=font,fill=fill,spacing=10,align='center')

def brand(draw,idx):
    draw.text((70,70),'BUILD IT SMALLER',font=FONT_M,fill=TEAL)
    draw.text((70,130),f'FIELD TEST {idx:02d}  /  09.15.26',font=FONT_S,fill=MUTED)
    draw.text((70,1790),'REAL SPACE  •  SMARTER USE  •  NO WASTED INCHES',font=FONT_S,fill=MUTED)

def kitchen(draw,t):
    # upper title timing
    if t<2.6:
        centered(draw,'THIS SPACE IS\nALREADY YOURS',250,FONT_B,WHITE)
        centered(draw,'You just can’t use it yet.',440,FONT_S,MUTED)
    else:
        centered(draw,'TOE-KICK DRAWERS',220,FONT_B,WHITE)
        centered(draw,'Storage hiding under the cabinets.',395,FONT_S,MUTED)
    # cabinets
    base_y=1050
    draw.rounded_rectangle((110,650,970,1320),30,fill=PANEL,outline=(40,84,102),width=4)
    for x in [135,410,685]:
        draw.rounded_rectangle((x,700,x+230,1075),18,fill=(28,49,61),outline=(65,94,107),width=3)
        draw.line((x+115,720,x+115,1050),fill=(52,75,88),width=2)
        draw.rounded_rectangle((x+95,860,x+135,872),6,fill=TEAL)
    # toe kick
    draw.rectangle((120,1110,960,1280),fill=(10,22,30))
    if t<2.7:
        centered(draw,'DEAD ZONE',1185,FONT_M,RED)
    else:
        p=ease((t-2.7)/1.7)
        # slide three drawers toward camera
        for i,x in enumerate([140,410,680]):
            yy=1135
            ext=int(180*p*(0.8+0.1*i))
            draw.rounded_rectangle((x,yy,x+220,yy+120+ext),16,fill=(34,62,73),outline=TEAL,width=4)
            draw.rounded_rectangle((x+78,yy+35,x+142,yy+48),6,fill=TEAL)
            # contents
            if p>.55:
                for j in range(3):
                    draw.rectangle((x+25+j*55,yy+70,x+60+j*55,yy+100),fill=(83,116,127))
        if t>5.8:
            centered(draw,'WOULD YOU ADD THESE?',1460,FONT_M,ACCENT)
            centered(draw,'Hidden storage or clean toe-kick?',1540,FONT_S,WHITE)

def desk(draw,t):
    if t<2.4:
        centered(draw,'A DESK DOESN’T NEED\nITS OWN ROOM',235,FONT_B,WHITE)
        centered(draw,'It can disappear when the workday does.',430,FONT_S,MUTED)
    else:
        centered(draw,'WALL → WORKSPACE',220,FONT_B,WHITE)
        centered(draw,'One shallow panel. One full setup.',390,FONT_S,MUTED)
    # room wall
    draw.rounded_rectangle((110,610,970,1370),28,fill=(19,35,46),outline=(55,85,98),width=4)
    draw.rectangle((165,690,915,1270),fill=(25,44,55))
    # panel/desk motion
    p=ease((t-2.1)/2.2)
    p=max(0,p)
    cx=540
    # closed panel behind
    draw.rounded_rectangle((355,730,725,1190),20,fill=(39,61,70),outline=TEAL,width=4)
    # desktop rotates down visually by changing height/position
    if p>0:
        y1=970
        y2=970+int(280*p)
        left=360-int(170*p)
        right=720+int(170*p)
        draw.polygon([(360,970),(720,970),(right,y2),(left,y2)],fill=(58,87,96),outline=TEAL)
        # legs appear
        if p>.55:
            a=(p-.55)/.45
            legy=1245+int(170*a)
            draw.line((left+90,y2,left+90,legy),fill=TEAL,width=8)
            draw.line((right-90,y2,right-90,legy),fill=TEAL,width=8)
        # laptop
        if p>.72:
            draw.rounded_rectangle((455,820,625,945),12,fill=(11,22,28),outline=(120,155,165),width=3)
            draw.rectangle((475,845,605,920),fill=(28,78,86))
            draw.line((440,950,640,950),fill=(155,180,185),width=8)
    if t>5.6:
        centered(draw,'WORK HERE. HIDE IT LATER.',1490,FONT_M,ACCENT)
        centered(draw,'Would this beat a permanent desk?',1570,FONT_S,WHITE)

def pantry(draw,t):
    if t<2.4:
        centered(draw,'THIS 9-INCH GAP\nCAN HOLD A LOT',235,FONT_B,WHITE)
        centered(draw,'Dead corners become expensive when space is small.',445,FONT_S,MUTED)
    else:
        centered(draw,'PULL-OUT VERTICAL STORAGE',210,FONT_B,WHITE)
        centered(draw,'Use the depth, not just the wall.',380,FONT_S,MUTED)
    # cabinets + narrow gap
    draw.rounded_rectangle((120,650,960,1380),28,fill=PANEL,outline=(49,78,92),width=4)
    draw.rectangle((160,710,435,1320),fill=(30,52,63))
    draw.rectangle((645,710,920,1320),fill=(30,52,63))
    gap=(465,710,615,1320)
    draw.rectangle(gap,fill=(8,18,26))
    if t<2.6:
        centered(draw,'WASTED',1110,FONT_M,RED)
    else:
        p=ease((t-2.6)/1.8)
        xoff=int(250*p)
        # tall rack slides outward
        x1=475+xoff; x2=605+xoff
        draw.rounded_rectangle((x1,735,x2,1295),14,fill=(39,69,78),outline=TEAL,width=4)
        for yy in [815,930,1045,1160]:
            draw.line((x1+12,yy,x2-12,yy),fill=TEAL,width=4)
        # jars/boxes
        if p>.35:
            for yy in [760,875,990,1105,1210]:
                draw.rounded_rectangle((x1+25,yy,x1+70,yy+38),8,fill=(89,123,130))
                draw.rounded_rectangle((x1+78,yy,x2-20,yy+38),8,fill=(110,93,72))
    if t>5.7:
        centered(draw,'NINE INCHES. FOUR SHELVES.',1490,FONT_M,ACCENT)
        centered(draw,'Would you trade trim for storage?',1570,FONT_S,WHITE)

def make(name,renderer,idx):
    frames=f'/tmp/{name}_frames'
    os.makedirs(frames,exist_ok=True)
    for n in range(FPS*DUR):
        t=n/FPS
        im=Image.new('RGB',(W,H),BG)
        d=ImageDraw.Draw(im)
        brand(d,idx)
        renderer(d,t)
        # progress rail
        d.rounded_rectangle((70,1715,1010,1730),8,fill=(34,56,66))
        d.rounded_rectangle((70,1715,70+int(940*(n/(FPS*DUR-1))),1730),8,fill=TEAL)
        im.save(f'{frames}/{n:04d}.png',compress_level=1)
    out=f'{OUT}/{name}.mp4'
    subprocess.run(['ffmpeg','-y','-framerate',str(FPS),'-i',f'{frames}/%04d.png','-f','lavfi','-i','anullsrc=channel_layout=stereo:sample_rate=44100','-shortest','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',str(FPS),'-movflags','+faststart','-c:a','aac','-b:a','96k',out],check=True)
    return out

files=[make('toe-kick-drawers-30fps',kitchen,1),make('fold-down-desk-30fps',desk,2),make('pull-out-pantry-30fps',pantry,3)]
for f in files:
    print('\nVERIFY',f)
    subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,avg_frame_rate,r_frame_rate,width,height','-of','default=nw=1',f],check=True)
