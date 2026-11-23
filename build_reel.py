#!/usr/bin/env python3
"""Usage: python3 build_reel.py <topic_id>  -> writes videos/<topic_id>.mp4 (1080x1920, 8s, Lora font)."""
import json, subprocess, sys, os, html, tempfile
FONT="file:///usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
FONTI="file:///usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
HANDLE="@highyielddaily"
P=[
 ("radial-gradient(circle at 20% 15%, #3b6ea8 0%, transparent 55%), radial-gradient(circle at 85% 85%, #0b2545 0%, transparent 60%), linear-gradient(160deg,#13315c,#0b2545)","#f4f1ea","#f2c14e"),
 ("radial-gradient(circle at 80% 10%, #f6c7a0 0%, transparent 55%), radial-gradient(circle at 10% 90%, #e07a5f 0%, transparent 60%), linear-gradient(200deg,#f4e1d2,#e9b8a0)","#3a1f1a","#8c2f1b"),
 ("radial-gradient(circle at 15% 20%, #7fb685 0%, transparent 55%), radial-gradient(circle at 90% 90%, #1b4332 0%, transparent 60%), linear-gradient(150deg,#2d6a4f,#1b4332)","#f1f7ee","#ffd6a5"),
 ("radial-gradient(circle at 80% 15%, #8e6bbf 0%, transparent 55%), radial-gradient(circle at 15% 90%, #2b1a4d 0%, transparent 60%), linear-gradient(170deg,#4a2c7a,#24143f)","#f5f0fb","#ffd166"),
 ("radial-gradient(circle at 20% 80%, #5fb3b3 0%, transparent 55%), radial-gradient(circle at 90% 10%, #0b3c49 0%, transparent 60%), linear-gradient(190deg,#1d6f7a,#0b3c49)","#eefafa","#ffe29a"),
 ("radial-gradient(circle at 85% 20%, #d4707a 0%, transparent 55%), radial-gradient(circle at 10% 90%, #5a1a2b 0%, transparent 60%), linear-gradient(165deg,#8c2f45,#4a1423)","#fdf1f2","#f6d38a"),
]
def main(tid):
    q=json.load(open("topics.json")); r=next(x for x in q if x["id"]==tid)
    bg,fg,acc=P[r["palette"]%len(P)]
    d=tempfile.mkdtemp(); os.makedirs("videos",exist_ok=True)
    css_font=f"@font-face{{font-family:'LoraL';src:url('{FONT}');font-weight:400 700}}@font-face{{font-family:'LoraL';src:url('{FONTI}');font-style:italic;font-weight:400 700}}"
    open(f"{d}/bg.html","w").write(f"""<html><head><style>{css_font}
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden}}
.bg{{position:absolute;inset:-120px;background:{bg}}}
.grain{{position:absolute;inset:-120px;opacity:.10;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='300' height='300' filter='url(%23n)'/></svg>")}}
</style></head><body><div class="bg"></div><div class="grain"></div></body></html>""")
    ln=len(r["line"]); size=84 if ln<75 else 72
    open(f"{d}/text.html","w").write(f"""<html><head><style>{css_font}
html,body{{margin:0;width:1080px;height:1920px;background:transparent;font-family:'LoraL',serif;color:{fg}}}
.wrap{{position:absolute;left:100px;right:100px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center}}
.tag{{font-size:34px;letter-spacing:10px;color:{acc};font-weight:600;margin-bottom:50px}}
.rule{{width:120px;height:5px;background:{acc};margin-bottom:60px}}
.line{{font-size:{size}px;line-height:1.2;font-weight:600}}
.sub{{font-size:46px;font-style:italic;margin-top:60px;opacity:.85;line-height:1.3}}
.handle{{position:absolute;bottom:150px;left:0;right:0;text-align:center;font-size:32px;letter-spacing:4px;opacity:.6}}
</style></head><body><div class="wrap"><div class="tag">{html.escape(r['tag'])}</div><div class="rule"></div><div class="line">{html.escape(r['line'])}</div><div class="sub">{html.escape(r['sub'])}</div></div><div class="handle">{HANDLE}</div></body></html>""")
    base=["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars","--window-size=1080,1920","--virtual-time-budget=3000"]
    subprocess.run(base+[f"--screenshot={d}/bg.png",f"file://{d}/bg.html"],check=True,capture_output=True)
    subprocess.run(base+["--default-background-color=00000000",f"--screenshot={d}/text.png",f"file://{d}/text.html"],check=True,capture_output=True)
    fc=("[0:v]scale=2160:3840,zoompan=z='1+0.0006*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:s=1080x1920:fps=30[b];"
        "[1:v]format=rgba,fade=t=in:st=0.6:d=1:alpha=1[t];[b][t]overlay=0:0,format=yuv420p[v]")
    subprocess.run(["ffmpeg","-y","-loop","1","-i",f"{d}/bg.png","-loop","1","-i",f"{d}/text.png","-filter_complex",fc,"-map","[v]","-t","8","-c:v","libx264","-preset","veryfast","-crf","20",f"videos/{tid}.mp4"],check=True,capture_output=True)
    subprocess.run(["ffmpeg","-y","-ss","4","-i",f"videos/{tid}.mp4","-frames:v","1","-vf","scale=360:-1",f"{d}/check.png","-loglevel","error"],check=True)
    print(f"videos/{tid}.mp4 built; preview frame: {d}/check.png")
main(sys.argv[1])
