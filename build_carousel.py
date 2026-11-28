#!/usr/bin/env python3
"""Usage: python3 build_carousel.py <id|all>
Reads carousels/source.json, renders 1080x1350 JPEG slides to carousels/<id>/<id>-N.jpg,
adds an entry to carousels/queue.json. Slide types: cover, flow, list, compare, final."""
import json, subprocess, sys, os, html, tempfile
from PIL import Image
FONT="file:///usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
FONTI="file:///usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
RAW="https://raw.githubusercontent.com/highyielddaily-rgb/Reels/main/carousels"
FOOT="\n\nEducational content only, not medical advice.\n\nWhat systems, topics, pearls & tidbits would help you? Comment below."
# (accent, dark, light tint)
P=[("#534ab7","#3b3480","#eceafb"),("#0f766e","#0b4f4a","#e1f3f0"),("#b4442b","#7d2d1b","#fbe9e3"),
   ("#1d5fa8","#134074","#e3eefa"),("#8a5a00","#5c3c00","#faf0d6"),("#9b2c64","#6b1c44","#f8e4ee")]
E=html.escape
def body(s,a,d,t):
    ty=s["type"]; h=""
    if ty=="cover":
        return f'<div class="cv"><div class="tg">{E(s["tag"])}</div><div class="big">{E(s["title"])}</div><div class="sb">{E(s["sub"])}</div></div>'
    h+=f'<div class="tg">{E(s["tag"])}</div><div class="ttl">{E(s["title"])}</div>'
    if s.get("sub"): h+=f'<div class="sb">{E(s["sub"])}</div>'
    h+='<div id="c">'
    if ty=="flow":
        n=len(s["steps"])
        for i,x in enumerate(s["steps"]):
            cls="bx last" if i==n-1 and s.get("end",True) else "bx"
            h+=f'<div class="{cls}"><b>{E(x[0])}</b><span>{E(x[1])}</span></div>'
            if i<n-1: h+='<div class="ar">&#8595;</div>'
    elif ty=="list":
        for x in s["items"]: h+=f'<div class="bx"><b>{E(x[0])}</b><span>{E(x[1])}</span></div>'
    elif ty=="compare":
        h+='<div class="cp">'
        for col in s["cols"]:
            h+=f'<div class="col"><div class="ch">{E(col[0])}</div>'+"".join(f'<div class="ci">{E(i)}</div>' for i in col[1])+'</div>'
        h+='</div>'
    elif ty=="svg":
        import bodydraw
        h+=getattr(bodydraw,s["fn"])()
    elif ty=="ecg":
        import ecgdraw
        n=len(s["panels"]); hh={1:560,2:380,3:236}[n]
        h+="".join(ecgdraw.P(k,hh,d) for k in s["panels"])
    elif ty=="final":
        cta=s.get("cta","Save this for later. Comment the topic you want next.")
        h+=f'<div class="fin{" big" if s.get("big") else ""}">{E(s["text"])}</div>'+(f'<div class="cta">{E(cta)}</div>' if cta else '')
    return h+'</div>'
def page(s,i,N,pal):
    a,d,t=P[pal%len(P)]
    foot="Swipe for more" if i<N else "Follow for daily high yield"
    cover=s["type"]=="cover"
    bg="#f5efe3" if not cover else a
    return f"""<html><head><meta charset="utf-8"><style>
@font-face{{font-family:'LoraL';src:url('{FONT}');font-weight:400 700}}
@font-face{{font-family:'LoraL';src:url('{FONTI}');font-style:italic;font-weight:400 700}}
html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;font-family:'LoraL',serif;background:{bg};color:#2b2a33}}
.badge{{position:absolute;left:70px;top:60px;background:#ffe14d;color:#1d1d1d;font-weight:700;font-size:32px;padding:6px 16px;border-radius:8px}}
.cnt{{position:absolute;right:70px;top:70px;font-size:28px;color:{'#fff' if cover else '#777'};opacity:.8}}
.area{{position:absolute;left:70px;right:70px;top:140px;bottom:130px}}
.tg{{font-size:27px;letter-spacing:6px;font-weight:700;color:{'#ffe14d' if cover else a};text-transform:uppercase;margin-bottom:14px}}
.ttl{{font-size:62px;font-weight:700;line-height:1.1}}
.sb{{font-size:32px;color:#555;margin-top:14px;line-height:1.3}}
.cv{{position:absolute;left:0;right:0;top:230px;color:#fff}}
.cv .big{{font-size:96px;font-weight:700;line-height:1.08;margin:20px 0 30px}}
.cv .sb{{color:#fff;opacity:.9;font-size:40px}}
#c{{margin-top:26px;font-size:30px}}
.bx{{border:3px solid {a};background:{t};color:{d};border-radius:22px;padding:.5em .9em;margin:0}}
.bx b{{display:block;font-size:1.2em;line-height:1.2}} .bx span{{display:block;font-size:.95em;margin-top:.15em;line-height:1.25}}
.bx.last{{background:{a};color:#fff}}
.bx + .bx{{margin-top:.7em}}
.ar{{text-align:center;color:{a};font-size:1.1em;line-height:1;height:1.1em;margin:.1em 0}}
.cp{{display:flex;gap:22px}} .col{{flex:1;background:{t};border:3px solid {a};border-radius:22px;padding:.6em .8em}}
.ch{{font-weight:700;font-size:1.3em;color:{a};margin-bottom:.4em;line-height:1.15}}
.ci{{color:{d};margin:.45em 0;line-height:1.25;font-size:1em}}
.fin{{font-size:1.45em;line-height:1.4;background:{t};border:3px solid {a};border-radius:22px;padding:.8em .9em;color:{d}}}
.fin.big{{font-size:2.3em;line-height:1.25;padding:1.1em 1em;margin-top:1.2em;font-weight:700}}
.cta{{margin-top:1.1em;font-style:italic;color:#555;font-size:1em}}
.foot{{position:absolute;left:70px;bottom:60px;font-size:28px;color:{'#fff' if cover else '#777'}}}
.dis{{position:absolute;right:70px;bottom:60px;font-size:28px;color:{'#fff' if cover else '#777'}}}
</style></head><body>
<div class="badge">High Yield Daily</div><div class="cnt">{i} / {N}</div>
<div class="area" id="a">{body(s,a,d,t)}</div>
<div class="foot">{foot}</div><div class="dis">Educational only, not medical advice</div>
<script>
function fit(){{var c=document.getElementById('c'),a=document.getElementById('a');if(!c){{document.body.setAttribute('data-fit','ok');return;}}
var s=40;c.style.fontSize=s+'px';while(a.scrollHeight>a.clientHeight&&s>16){{s--;c.style.fontSize=s+'px';}}
document.body.setAttribute('data-fit',(a.scrollHeight<=a.clientHeight)?'ok':'over');}}
fit();document.fonts.ready.then(fit);setTimeout(fit,400);setTimeout(fit,1200);
</script></body></html>"""
def build(q):
    d=tempfile.mkdtemp(); od=f"carousels/{q['id']}"; os.makedirs(od,exist_ok=True)
    S=q["slides"]; N=len(S); urls=[]
    for n,s in enumerate(S,1):
        open(f"{d}/s{n}.html","w").write(page(s,n,N,q["palette"]))
        png=f"{d}/s{n}.png"
        subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars","--window-size=1080,1350","--virtual-time-budget=3000",f"--screenshot={png}",f"file://{d}/s{n}.html"],check=True,capture_output=True)
        dom=subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--virtual-time-budget=3000","--window-size=1080,1350","--dump-dom",f"file://{d}/s{n}.html"],capture_output=True,text=True).stdout
        if 'data-fit="ok"' not in dom: print("OVERFLOW",q['id'],n); sys.exit(1)
        Image.open(png).convert("RGB").save(f"{od}/{q['id']}-{n}.jpg",quality=90)
        urls.append(f"{RAW}/{q['id']}/{q['id']}-{n}.jpg")
    qp="carousels/queue.json"; queue=json.load(open(qp))
    if not any(e["id"]==q["id"] for e in queue):
        queue.append(dict(id=q["id"],caption=q["caption"]+FOOT,image_urls=urls,posted=False,media_id=None,posted_at=None))
    json.dump(queue,open(qp,"w"),indent=1)
    print(q["id"],N,"slides")
src=json.load(open("carousels/source.json")); which=sys.argv[1]
for q in src:
    if which in("all",q["id"]): build(q)
