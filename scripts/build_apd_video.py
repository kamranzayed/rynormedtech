"""Create a captioned, original 36-second educational animation, without clinical operating steps."""
import math,subprocess,sys,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
import imageio_ffmpeg
OUT=ROOT/'assets/media';OUT.mkdir(parents=True,exist_ok=True)
W,H,FPS,DURATION=1024,576,20,36
NAVY='#181646';TEAL='#0b819d';LIGHT='#e4eef5';INK='#21354b';MUTED='#52667c';BG='#f3f7fa';GOLD='#c49b4b'
def font(n,bold=False):return ImageFont.truetype('C:/Windows/Fonts/'+('arialbd.ttf' if bold else 'arial.ttf'),n)
F={n:font(n) for n in [17,18,20,22,24,28,32,38]};B={n:font(n,True) for n in [18,20,24,28,32,38]}
scenes=[
 ('What is peritoneal\ndialysis?', 'A home treatment option\nfor some people with kidney failure.', 'PD uses the lining inside your belly to help remove waste and extra fluid from your blood.'),
 ('APD adds\na cycler.', 'A machine moves prescribed\ndialysis fluid through a soft catheter.', 'The cycler moves dialysis fluid. Your blood stays inside your body.'),
 ('Fill. Dwell. Drain.', 'The exchange repeats, following\nyour clinical team’s prescription.', 'Fresh fluid goes in, stays for a prescribed time, then drains out with waste and extra water.'),
 ('Often while\nyou sleep.', 'Your kidney team sets the schedule\nand trains you or a helper.', 'APD often runs overnight at home. Treatment is usually daily; some people need a daytime exchange too.'),
 ('More room for\neveryday life.', 'Home treatment may reduce travel\nfor routine dialysis sessions.', 'Clinic reviews, supplies, storage, electricity and a daily care routine are still needed.'),
 ('Start with\na conversation.', 'Ask your kidney-care team about\nsuitability, risks and the full cost of care.', 'PD is not suitable for everyone. Infection and discomfort can occur. RYNOR’s system is still in development.')]

def rounded(d,box,r=18,fill='white',outline=None,width=2):d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)
def wrap(d,text,f,width):
    words=text.split();lines=[];line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if d.textlength(candidate,font=f)>width and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines
def machine(d,x=537,y=294,scale=1):
    def b(a):return tuple(round((v*scale)+(x if i%2==0 else y)) for i,v in enumerate(a))
    rounded(d,b((0,0,159,106)),13*scale,'#dde5ee','#8e9eae',2)
    rounded(d,b((8,9,151,47)),7*scale,NAVY)
    d.line([b((20,30)),b((47,24)),b((79,35)),b((115,28)),b((138,31))],fill='#49bfda',width=max(2,int(3*scale)))
    d.text(b((51,65)),'Cycler',font=F[18] if scale>=.8 else F[17],fill=NAVY)
def bag(d,x=548,y=113):
    rounded(d,(x,y,x+80,y+113),12,'#e0eff4','#7da4b6')
    rounded(d,(x+25,y+10,x+55,y+20),5,'white','#9cb9c8',1)
    rounded(d,(x+8,y+65,x+72,y+104),7,'#9bd6e2')
    d.text((x+12,y+38),'Fluid',font=F[18],fill=INK)
    d.line((x+40,y+113,x+40,294),fill='#81afbf',width=5)
def person(d,fluid=.65,waste=False):
    d.ellipse((779,121,841,183),fill='#ead4bf',outline='#b69a80',width=2)
    d.polygon([(768,198),(850,198),(874,249),(866,400),(750,400),(746,249)],fill='#dce9f3',outline='#8ea9bb')
    rounded(d,(774,266,850,356),24,'#fcfefe','#6d9aab',2)
    if fluid>.04:
        level=350-int(76*fluid);rounded(d,(780,level,844,348),12,'#92d4e0')
    d.line((696,324,772,324),fill='#65adc1',width=6)
    if waste:
        for x,y in [(791,306),(822,319),(812,340)]:d.ellipse((x-4,y-4,x+4,y+4),fill=GOLD)
    d.text((774,412),'Belly lining',font=F[18],fill=MUTED)
def dot(d,x,y,color=TEAL):d.ellipse((x-5,y-5,x+5,y+5),fill=color)
def diagram(d,t,scene):
    if scene in [0,1,2]:
        bag(d);machine(d)
        sub=int(t//2) if scene==2 else 0
        fluid=(t%2)/2 if sub==0 and scene==2 else .8 if sub==1 or scene!=2 else .8*(1-(t%2)/2)
        person(d,fluid,scene==2 and sub>0)
        d.line((616,400,616,447,712,447),fill='#b3a27c',width=5)
        rounded(d,(713,421,780,462),9,'#f2e6c9','#b49e70',2)
        d.text((695,464),'Used fluid',font=F[17],fill=MUTED)
        if scene in [1,2]:
            for j in range(4):dot(d,699+((t*.45+j*.25)%1)*70,324,GOLD if scene==2 and sub==2 else TEAL)
        if scene==2:
            label=['FILL','DWELL','DRAIN'][min(sub,2)]
            rounded(d,(754,66,874,102),18,TEAL if sub!=2 else '#956e26')
            d.text((814,84),label,font=B[18],anchor='mm',fill='white')
    elif scene==3:
        d.ellipse((805,90,862,147),fill='#e6bc62');d.ellipse((821,78,874,131),fill=BG)
        rounded(d,(553,296,918,397),16,'#d5e3ed','#8ea6b8',2)
        rounded(d,(556,277,664,321),14,'white','#b5c8d4',2)
        d.ellipse((586,265,638,313),fill='#e9d4bf')
        rounded(d,(647,282,908,351),20,'#8dc9d8')
        d.line((565,398,565,429,906,429,906,398),fill='#8ea6b8',width=5)
        machine(d,556,159,.65)
        d.line((662,192,698,192,698,288),fill=TEAL,width=4)
        for j in range(3):d.text((730+j*31,157-j*18),'z',font=F[22],fill='#88acbc')
    elif scene==4:
        # Home and routine: an abstract illustration, not a promised clinical outcome.
        d.polygon([(558,257),(686,150),(814,257)],fill='#a9d1df',outline='#508398')
        rounded(d,(582,252,790,402),6,'white','#8eb0c2',2)
        rounded(d,(659,317,715,402),4,'#d3e5ee')
        d.ellipse((780,100,924,244),fill='#fff',outline='#84a4b8',width=4)
        a=(t/6)*math.pi*.6
        d.line((852,172,852+45*math.sin(a),172-45*math.cos(a)),fill=TEAL,width=4)
        d.line((852,172,879,184),fill=NAVY,width=4)
        d.ellipse((845,165,859,179),fill=TEAL)
        d.line((803,340,914,340),fill='#9cbcc9',width=5)
        for j in range(4):dot(d,805+((t*.2+j*.25)%1)*100,340,'#74b3c4')
    else:
        for x,color in [(626,'#e6d2be'),(824,'#e4ccb5')]:
            d.ellipse((x-31,161,x+31,223),fill=color,outline='#b49c86',width=2)
            rounded(d,(x-54,235,x+54,399),22,'#d9e9f3' if x==626 else 'white','#8ba8bb',2)
        rounded(d,(662,92,819,151),15,'white','#8ca8bb',2)
        d.polygon([(684,149),(698,149),(682,169)],fill='white')
        d.text((740,121),'Let’s talk',font=B[20],anchor='mm',fill=TEAL)
        d.line((800,268,849,268),fill=TEAL,width=3);d.line((824,245,824,293),fill=TEAL,width=3)

def frame(index):
    time=index/FPS;scene=min(5,int(time//6));t=time-scene*6
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,54),fill=NAVY)
    d.text((40,27),'RYNOR  /  PD AT HOME',font=B[18],anchor='lm',fill='white')
    d.text((982,27),f'{scene+1} / 6',font=F[18],anchor='rm',fill='#c4dae5')
    title,body,caption=scenes[scene]
    d.multiline_text((45,119),title,font=B[38],fill=NAVY,spacing=8)
    d.multiline_text((47,264),body,font=F[22],fill=MUTED,spacing=10)
    d.rectangle((47,349,91,353),fill=TEAL)
    diagram(d,t,scene)
    d.rectangle((0,492,W,576),fill=NAVY)
    lines=wrap(d,caption,F[20],940)
    for k,line in enumerate(lines):d.text((42,505+k*25),line,font=F[20],fill='white')
    d.rectangle((0,572,int(W*time/DURATION),575),fill='#64c7d6')
    return im

poster=frame(22);poster.save(OUT/'apd-overview-poster.webp',quality=92)
exe=imageio_ffmpeg.get_ffmpeg_exe()
process=subprocess.Popen([exe,'-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'apd-overview.mp4')],stdin=subprocess.PIPE)
for index in range(FPS*DURATION):process.stdin.write(frame(index).tobytes())
process.stdin.close();assert process.wait()==0
vtt='WEBVTT\n\n'
for i,(_,_,caption) in enumerate(scenes):vtt+=f'{i+1}\n00:{i*6:02d}.000 --> 00:{(i+1)*6:02d}.000\n{caption}\n\n'
(OUT/'apd-overview-en.vtt').write_text(vtt,encoding='utf-8')
print(f'Created {DURATION}s H.264 video: {(OUT/"apd-overview.mp4").stat().st_size} bytes',flush=True)
