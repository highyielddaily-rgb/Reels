#!/usr/bin/env python3
"""Usage: python3 build_question.py <id|all>
Reads questions/source.json, renders 1080x1350 JPEG slides to questions/<id>/<id>-N.jpg
and adds an entry to questions/queue.json (id, caption, image_urls, posted...)."""
import json, subprocess, sys, os, html, tempfile
FONT="file:///usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
FONTI="file:///usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
RAW="https://raw.githubusercontent.com/highyielddaily-rgb/Reels/main/questions"
FOOT="\n\nEducational content only, not medical advice.\n\nWhat systems, topics, pearls & tidbits would help you? Comment below."
HANDLE="@highyielddaily"
# (background, text color, accent, panel)
P=[
 ("radial-gradient(circle at 20% 15%, #3b6ea8 0%, transparent 55%), linear-gradient(160deg,#13315c,#0b2545)","#f4f1ea","#f2c14e","rgba(0,0,0,.20)"),
 ("radial-gradient(circle at 80% 10%, #f6c7a0 0%, transparent 55%), linear-gradient(200deg,#f4e1d2,#e9b8a0)","#3a1f1a","#8c2f1b","rgba(255,255,255,.40)"),
 ("radial-gradient(circle at 15% 20%, #7fb685 0%, transparent 55%), linear-gradient(150deg,#2d6a4f,#1b4332)","#f1f7ee","#ffd6a5","rgba(0,0,0,.20)"),
 ("radial-gradient(circle at 80% 15%, #8e6bbf 0%, transparent 55%), linear-gradient(170deg,#4a2c7a,#24143f)","#f5f0fb","#ffd166","rgba(0,0,0,.22)"),
 ("radial-gradient(circle at 20% 80%, #5fb3b3 0%, transparent 55%), linear-gradient(190deg,#1d6f7a,#0b3c49)","#eefafa","#ffe29a","rgba(0,0,0,.20)"),
 ("radial-gradient(circle at 85% 20%, #d4707a 0%, transparent 55%), linear-gradient(165deg,#8c2f45,#4a1423)","#fdf1f2","#f6d38a","rgba(0,0,0,.22)"),
]
def page(q,heading,body_html,footer):
    bg,fg,acc,panel=P[q["palette"]%len(P)]
    return f"""<html><head><meta charset="utf-8"><style>
@font-face{{font-family:'LoraL';src:url('{FONT}');font-weight:400 700}}
@font-face{{font-family:'LoraL';src:url('{FONTI}');font-style:italic;font-weight:400 700}}
html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;font-family:'LoraL',serif;color:{fg}}}
.bg{{position:absolute;inset:0;background:{bg}}}
.tag{{position:absolute;left:80px;top:64px;font-size:28px;letter-spacing:7px;color:{acc};font-weight:600}}
.rule{{position:absolute;left:80px;top:118px;width:110px;height:5px;background:{acc}}}
.head{{position:absolute;left:80px;right:80px;top:146px;font-size:52px;font-weight:700;color:{acc}}}
.panel{{position:absolute;left:60px;right:60px;top:236px;bottom:150px;background:{panel};border-radius:22px;padding:36px 44px;box-sizing:border-box;overflow:hidden}}
#c{{font-size:40px;line-height:1.38;}}
#c p{{margin:0 0 .6em 0}}
.opt{{margin:0 0 .45em 0;padding-left:2.1em;text-indent:-2.1em}}
.opt b{{color:{acc};display:inline-block;width:1.6em;text-indent:0}}
.foot{{position:absolute;left:80px;right:80px;bottom:62px;font-size:30px;font-style:italic;opacity:.85}}
.handle{{position:absolute;right:80px;bottom:62px;font-size:26px;letter-spacing:3px;opacity:.6}}
</style></head><body><div class="bg"></div>
<div class="tag">{html.escape(q['tag'])}</div><div class="rule"></div><div class="head">{html.escape(heading)}</div>
<div class="panel"><div id="c">{body_html}</div></div>
<div class="foot">{footer}</div><div class="handle">{HANDLE}</div>
<script>
var c=document.getElementById('c'),p=c.parentElement;
function fit(){{var s=56;c.style.fontSize=s+'px';while(c.scrollHeight>p.clientHeight-80&&s>20){{s-=1;c.style.fontSize=s+'px';}}
document.body.setAttribute('data-fit',(c.scrollHeight<=p.clientHeight-72)?'ok':'over');}}
fit();document.fonts.ready.then(fit);setTimeout(fit,400);setTimeout(fit,1200);
</script></body></html>"""
def slides(q):
    E=html.escape; c=q["correct"]; opts=q["options"]
    wrong=[k for k in opts if k!=c]
    ol="".join(f'<div class="opt"><b>{k}.</b>{E(v)}</div>' for k,v in opts.items())
    out=[("Question",f'<p>{E(q["stem"])}</p>{ol}',"Swipe for the answer →")]
    out.append(("Answer",f'<p style="font-size:70px;font-weight:700;margin-bottom:.2em">{c}.</p><p>{E(opts[c])}</p><p style="font-style:italic;opacity:.85">Swipe for the explanations →</p>',"Did you get it?"))
    out.append((f"Why {c} is correct",f'<p>{E(q["why"][c])}</p>',"Next: why the others are wrong →"))
    for i in range(0,len(wrong),2):
        grp=wrong[i:i+2]
        body="".join(f'<p><b style="color:var(--a)">{k}. {E(opts[k])}</b><br>{E(q["why"][k])}</p>' for k in grp)
        out.append(("Why the others are wrong",body,"→"))
    out.append(("Key takeaway",f'<p>{E(q["takeaway"])}</p><p style="font-style:italic;opacity:.85;margin-top:1.2em">Save this for later, and comment the topic you want next.</p>',"Follow for daily high yield"))
    return out
def build(q):
    d=tempfile.mkdtemp(); od=f"questions/{q['id']}"; os.makedirs(od,exist_ok=True)
    urls=[]
    for n,(h,body,foot) in enumerate(slides(q),1):
        acc=P[q["palette"]%len(P)][2]
        html_s=page(q,h,body.replace("var(--a)",acc),foot)
        open(f"{d}/s{n}.html","w").write(html_s)
        png=f"{d}/s{n}.png"
        subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars","--window-size=1080,1350","--virtual-time-budget=3000",f"--screenshot={png}",f"file://{d}/s{n}.html"],check=True,capture_output=True)
        from PIL import Image
        dom=subprocess.run(["google-chrome","--headless=new","--no-sandbox","--disable-gpu","--virtual-time-budget=3000","--window-size=1080,1350","--dump-dom",f"file://{d}/s{n}.html"],capture_output=True,text=True).stdout
        if 'data-fit="ok"' not in dom: print("OVERFLOW",q['id'],n); sys.exit(1)
        Image.open(png).convert("RGB").save(f"{od}/{q['id']}-{n}.jpg",quality=90)
        urls.append(f"{RAW}/{q['id']}/{q['id']}-{n}.jpg")
    cap=f"Practice question ({q['kind']}). Try it before you swipe. Slide 2 has the answer, then we go through every option."+FOOT
    qp="questions/queue.json"; queue=json.load(open(qp)) if os.path.exists(qp) else []
    queue=[e for e in queue if e["id"]!=q["id"] or e.get("posted")]
    if not any(e["id"]==q["id"] for e in queue):
        queue.append(dict(id=q["id"],caption=cap,image_urls=urls,posted=False,media_id=None,posted_at=None))
    json.dump(queue,open(qp,"w"),indent=1)
    print(q["id"],len(urls),"slides")
src=json.load(open("questions/source.json")); which=sys.argv[1]
for q in src:
    if which in("all",q["id"]): build(q)
