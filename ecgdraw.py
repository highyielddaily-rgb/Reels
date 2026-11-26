"""Schematic ECG waveform drawings (SVG). Not real tracings: teaching diagrams.
Units: time in ms, amplitude in 'mm' (1 mm = h/25 px)."""
import numpy as np
from scipy.interpolate import PchipInterpolator
W=940; SPAN=2400.0; PX=W/SPAN
def base_beat(**k):
    b=dict(p=1.0,pr=160,prdep=0.0,
           qrs=[(0,0),(12,-1),(30,10),(48,-1.5),(60,0)],
           stt=[(0,0),(60,0),(110,1.2),(170,3),(230,1.2),(280,0)])
    b.update(k); return b
def add_beat(y,t,t0,s):
    if s.get("p"):
        c=t0-s["pr"]+45
        y+=s["p"]*np.exp(-((t-c)/18.0)**2/2)*(np.abs(t-c)<80)
    if s["prdep"]:
        a=t0-s["pr"]+10; b=t0
        w=np.clip((t-a)/25.0,0,1)*np.clip((b-t)/1.0+1,0,1)*((t>=a)&(t<=b))
        y+=s["prdep"]*w
    q=list(s["qrs"]); q[0]=(0,s["prdep"]); stt=list(s["stt"]); q[-1]=(q[-1][0],stt[0][1])
    xs,ys=zip(*q); dur=xs[-1]
    m=(t>=t0)&(t<=t0+dur); y[m]=np.interp(t[m]-t0,xs,ys)
    sx,sy=zip(*stt); f=PchipInterpolator(sx,sy)
    J=t0+dur; m=(t>J)&(t<=J+sx[-1]); y[m]=f(t[m]-J)
def build(beats,span=SPAN,noise=0.0,mirror=False):
    t=np.arange(0,span,2.0); y=np.zeros_like(t)
    for t0,s in beats: add_beat(y,t,t0,s)
    if noise:
        r=np.random.RandomState(3); k=np.convolve(r.randn(len(t)),np.ones(9)/9,'same')
        y+=noise*k*3
    return t,(-y if mirror else y)
def panel(name,t,y,anns=(),h=250,col="#7d2d1b",base=0.6,extra=""):
    vp=h/25.0; b=h*base
    g=[f'<rect width="{W}" height="{h}" rx="14" fill="#fff8f6" stroke="#d9a3a3" stroke-width="2"/>']
    step=40*PX
    i=0
    while i*step<=W:
        c="#e8a9a9" if i%5==0 else "#f4d3d3"; g.append(f'<line x1="{i*step:.1f}" y1="0" x2="{i*step:.1f}" y2="{h}" stroke="{c}" stroke-width="{1.6 if i%5==0 else 1}"/>'); i+=1
    j=0
    while b-j*step>=0 or b+j*step<=h:
        for yy in (b-j*step,b+j*step):
            if 0<=yy<=h:
                c="#e8a9a9" if j%5==0 else "#f4d3d3"; g.append(f'<line x1="0" y1="{yy:.1f}" x2="{W}" y2="{yy:.1f}" stroke="{c}" stroke-width="{1.6 if j%5==0 else 1}"/>')
        j+=1
        if j>60: break
    pts=" ".join(f"{ti*PX:.1f},{b-yi*vp:.1f}" for ti,yi in zip(t,y))
    g.append(f'<polyline points="{pts}" fill="none" stroke="#161616" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>')
    g.append(f'<text x="18" y="34" font-size="27" font-weight="700" fill="{col}">{name}</text>')
    for a in anns:
        if a[0]=="br":   # bracket: ("br", t1, t2, y, text)
            _,t1,t2,yy,tx=a; x1,x2,py=t1*PX,t2*PX,b-yy*vp
            g.append(f'<path d="M{x1:.1f},{py-8:.1f} L{x1:.1f},{py+8:.1f} M{x1:.1f},{py:.1f} L{x2:.1f},{py:.1f} M{x2:.1f},{py-8:.1f} L{x2:.1f},{py+8:.1f}" stroke="{col}" stroke-width="3" fill="none"/>')
            g.append(f'<text x="{max(x1,12):.1f}" y="{py+30:.1f}" font-size="23" font-weight="700" fill="{col}" text-anchor="start">{tx}</text>')
        elif a[0]=="mk":  # marker triangle: ("mk", t, y, text)
            _,tt,yy,tx=a; x,py=tt*PX,b-yy*vp
            g.append(f'<path d="M{x:.1f},{py:.1f} l-8,14 h16 z" fill="{col}"/>')
            if tx: g.append(f'<text x="{x:.1f}" y="{py+36:.1f}" font-size="21" font-weight="700" fill="{col}" text-anchor="middle">{tx}</text>')
        else:             # ("an", text, tt, yy, tx_t, tx_y)
            _,tx,tt,yy,xt,yt=a; x,py=tt*PX,b-yy*vp; X,Y=xt*PX,b-yt*vp
            w=len(tx)*11.6+16; Y=min(max(Y,64),h-24); X=min(max(X,w/2+8),W-w/2-8)
            g.append(f'<line x1="{X:.1f}" y1="{Y:.1f}" x2="{x:.1f}" y2="{py:.1f}" stroke="{col}" stroke-width="3"/><circle cx="{x:.1f}" cy="{py:.1f}" r="6" fill="{col}"/>')
            g.append(f'<rect x="{X-w/2:.1f}" y="{Y-18:.1f}" width="{w:.1f}" height="32" rx="8" fill="#fff" stroke="{col}" stroke-width="2"/><text x="{X:.1f}" y="{Y+6:.1f}" font-size="22" font-weight="700" fill="{col}" text-anchor="middle">{tx}</text>')
    g.append(extra)
    return f'<svg viewBox="0 0 {W} {h}" width="{W}" height="{h}" style="display:block;margin-bottom:14px">{"".join(g)}</svg>'
RR=800
def seq(spec,n=3,start=420,rr=RR): return [(start+i*rr,spec) for i in range(n)]
QR_V2=[(0,0),(10,2),(24,-7),(42,0.3)]
def P(key,h,col):
    N=base_beat
    if key=="brug1":
        s=N(p=0.5,qrs=[(0,0),(12,2),(24,-1),(38,5.5),(55,4)],stt=[(0,4),(40,3.4),(100,1.6),(150,-1),(205,-3),(260,-3.2),(320,-1),(360,0)])
        t,y=build(seq(s)); return panel("V1 · Type 1: diagnostic",t,y,[("an","Coved ST ≥ 2 mm",455+RR*0+110,3.6,720,10),("an","Inverted T",420+RR+300,-3,1500,-8.5)],h,col)
    if key=="brug2":
        s=N(p=0.5,qrs=[(0,0),(12,2),(24,-1),(38,5),(55,3.5)],stt=[(0,3.5),(50,2.4),(100,1.2),(160,2.8),(220,1.6),(270,0)])
        t,y=build(seq(s)); return panel("V1 · Type 2: saddleback, suggestive only",t,y,[("an","Saddleback",420+55+100,1.3,820,9.5),("an","T upright",420+RR+55+160,2.8,1650,9.5)],h,col)
    if key=="peri2":
        s=N(p=1.0,prdep=-1.3,qrs=[(0,0),(12,-1),(30,10),(48,-1.5),(60,1.5)],stt=[(0,1.5),(30,1.3),(70,1.6),(120,2.8),(170,4),(230,2.5),(280,0.6),(320,0)])
        t,y=build(seq(s)); return panel("Lead II",t,y,[("an","PR depression",420-60,-1.3,200,-9),("an","Concave ST elevation",420+60+80,1.7,900,11.5)],h,col)
    if key=="peri_avr":
        s=N(p=1.0,prdep=-1.3,qrs=[(0,0),(12,-1),(30,10),(48,-1.5),(60,1.5)],stt=[(0,1.5),(30,1.3),(70,1.6),(120,2.8),(170,4),(230,2.5),(280,0.6),(320,0)])
        t,y=build(seq(s),mirror=True); return panel("Lead aVR (mirror image)",t,y,[("an","PR elevation",420-60,1.3,200,9),("an","ST depression",420+60+80,-1.7,900,-11.5)],h,col)
    if key=="tors":
        s=N(p=1.0,qrs=[(0,0),(12,-1),(30,9),(48,-1.5),(60,0)],stt=[(0,0),(80,0),(180,1.0),(290,3.2),(380,3.2),(450,0.5),(500,0)])
        bs=seq(s,2,200)
        t,y=build(bs)
        m=(t>=1450)&(t<2400); tt=t[m]-1450
        y[m]=9*np.sin(2*np.pi*tt/270.0)*np.sin(np.pi*tt/470.0)
        return panel("Torsades de pointes",t,y,[("br",200,760,-8,"Long QT"),("an","Twists around the baseline",1950,6,1180,11.5)],h,col)
    if key=="wct":
        s=dict(p=0,pr=0,prdep=0,qrs=[(0,0),(25,4),(55,9),(85,3),(115,-5),(140,-5.5)],stt=[(0,-5.5),(40,-4),(90,-1),(130,0.8),(160,0)])
        bs=[(120+i*345,s) for i in range(7)]
        t,y=build(bs)
        an=[("mk",240+i*760,-9,"P" if True else "") for i in range(3)]
        an=[("mk",150+i*760,-9.5,"P") for i in range(3)]
        return panel("Regular wide complex tachycardia",t,y,an+[("an","QRS > 120 ms, monomorphic",120+345*2+70,9,1000,11.5),("an","P waves march at their own slower rate",150+760,-9.5,1500,-12)],h,col)
    if key=="rv_ii":
        s=N(p=1.0,qrs=[(0,0),(10,-1),(28,5),(46,-1),(60,1.5)],stt=[(0,1.5),(70,1.8),(130,2.2),(190,1.5),(240,0.4),(280,0)])
        t,y=build(seq(s)); return panel("Lead II · ST elevation",t,y,[("an","1.5 mm",420+130,2.2,1100,7)],h,col)
    if key=="rv_iii":
        s=N(p=1.0,qrs=[(0,0),(10,-1),(28,5),(46,-1),(60,3)],stt=[(0,3),(60,3.4),(120,4),(180,3.2),(240,1.2),(290,0)])
        t,y=build(seq(s)); return panel("Lead III · ST elevation greater than lead II",t,y,[("an","III > II",420+120,4,1100,8.5)],h,col)
    if key=="rv_v4r":
        s=N(p=1.0,qrs=[(0,0),(12,-0.5),(26,3),(40,-1),(55,1.5)],stt=[(0,1.5),(70,1.9),(130,2.2),(190,1.2),(240,0.4),(280,0)])
        t,y=build(seq(s)); return panel("V4R · right sided lead",t,y,[("an","ST elevation ≥ 1 mm",420+125,2.2,1150,8)],h,col)
    if key=="dig_eff":
        s=N(p=1.0,qrs=[(0,0),(12,-0.5),(30,12),(48,-1),(62,-1.5)],stt=[(0,-1.5),(40,-3.0),(90,-3.5),(130,-2.5),(170,-0.8),(200,0.0),(240,0.5),(270,0)])
        t,y=build(seq(s),); return panel("V5 · digitalis effect (not toxicity)",t,y,[("an","Scooped ST, 'reverse tick'",420+62+90,-3.5,1050,-9)],h,col)
    if key=="dig_at":
        s=N(p=0,qrs=[(0,0),(12,-1),(30,9),(48,-1.5),(60,0)],stt=[(0,0),(60,0),(110,1),(160,0.8),(200,0)])
        pw=N(p=1.3,qrs=[(0,0),(1,0),(2,0)],stt=[(0,0),(1,0)])
        y=np.zeros(int(SPAN/2)); t=np.arange(0,SPAN,2.0)
        for k in range(6): y+=1.3*np.exp(-((t-(150+k*390))/18.0)**2/2)
        for k in range(3): add_beat(y,t,260+k*780,dict(s,p=0,pr=160))
        pm=[("mk",150+k*390,-3.2,"") for k in range(6)]
        return panel("Atrial tachycardia with 2:1 block",t,y,pm+[("an","P waves: 2 for every QRS",150+390,-3.2,1200,-9.5)],h,col)
    if key=="dig_bivt":
        pos=dict(p=0,pr=0,prdep=0,qrs=[(0,0),(30,9),(70,5),(100,-1),(120,0)],stt=[(0,0),(1,0)])
        neg=dict(pos,qrs=[(0,0),(30,-9),(70,-5),(100,1),(120,0)])
        bs=[(120+i*400,(pos if i%2==0 else neg)) for i in range(6)]
        t,y=build(bs); return panel("Bidirectional VT (suggests digoxin toxicity)",t,y,[("an","QRS axis alternates beat to beat",120+400*2,-8.5,1200,-11.5)],h,col)
    if key in("ca_norm","ca_low","ca_high"):
        if key=="ca_norm": st=[(0,0),(80,0),(130,1.2),(190,3),(250,1.2),(300,0)]; nm="Normal calcium"; qt="QT normal"
        if key=="ca_low": st=[(0,0),(220,0),(270,1.2),(330,3),(390,1.2),(440,0)]; nm="Low calcium"; qt="QT long: ST segment stretched"
        if key=="ca_high": st=[(0,0),(4,0),(35,1.4),(80,3),(125,1.2),(155,0)]; nm="High calcium"; qt="QT short: ST segment almost gone"
        s=N(p=1.0,stt=st); t,y=build(seq(s,2,300))
        end=300+60+st[-1][0]
        return panel(f"{nm}",t,y,[("br",300,end,-3.5 if True else 0,qt)],h,col)
    if key=="pe_v2":
        s=N(p=1.0,qrs=QR_V2,stt=[(0,0.3),(60,0.2),(120,-1.5),(180,-3),(240,-1.5),(290,0)])
        t,y=build(seq(s,4,300,rr=550)); return panel("V2 · T wave inversion",t,y,[("an","Inverted T",300+42+180,-3,1100,9)],h,col)
    if key=="pe_i":
        s=N(p=1.0,qrs=[(0,0),(10,-0.5),(24,6),(42,-4),(56,0)],stt=[(0,0),(60,0),(110,1),(160,2),(210,1),(250,0)])
        t,y=build(seq(s,4,300,rr=550)); return panel("Lead I · S wave",t,y,[("an","Deep S wave",300+42,-4,900,-10)],h,col)
    if key=="pe_iii":
        s=N(p=1.0,qrs=[(0,0),(8,-3.5),(20,-3.5),(34,4),(48,-0.5),(58,0)],stt=[(0,0),(60,0),(110,-1.2),(165,-2.5),(215,-1.2),(260,0)])
        t,y=build(seq(s,4,300,rr=550)); return panel("Lead III · Q wave and inverted T",t,y,[("an","Q wave",300+14,-3.5,820,-10),("an","Inverted T",300+58+165,-2.5,1500,-10)],h,col)
    if key=="wel_a":
        s=N(p=1.0,qrs=QR_V2,stt=[(0,0.3),(60,0.8),(110,1.8),(150,0.2),(200,-2.5),(250,-2.0),(300,0)])
        t,y=build(seq(s,3,300,rr=800)); return panel("V2 · Wellens type A: biphasic T",t,y,[("an","Up then down",300+42+200,-2.5,1300,8),("an","No ST elevation",300+60,0.3,700,8)],h,col)
    if key=="wel_b":
        s=N(p=1.0,qrs=QR_V2,stt=[(0,0.5),(60,0.6),(120,-1.5),(180,-5),(230,-5.2),(280,-2.5),(330,0)])
        t,y=build(seq(s,3,300,rr=800)); return panel("V2 · Wellens type B: deep symmetric T inversion",t,y,[("an","Deep, symmetric",300+42+210,-5.2,1400,8)],h,col)
    if key=="dw_norm":
        s=N(p=1.0,qrs=[(0,0),(10,1),(22,-3),(36,8),(52,0)],stt=[(0,0),(80,0.2),(140,2),(200,3.5),(260,1.5),(310,0)])
        t,y=build(seq(s)); return panel("V3 · normal for comparison",t,y,[],h,col)
    if key=="dw_dw":
        s=N(p=1.0,qrs=[(0,0),(10,1),(22,-3),(36,8),(52,-1),(58,-2.2)],stt=[(0,-2.2),(40,-1.4),(90,0.5),(140,5),(180,8),(220,5),(270,0.5),(310,0)])
        t,y=build(seq(s)); return panel("V3 · de Winter pattern",t,y,[("an","Upsloping ST depression",420+58+20,-1.8,780,-8),("an","Tall, symmetric T",420+58+180,8,1500,11.5)],h,col)
    if key=="post_v2":
        s=N(p=1.0,qrs=[(0,0),(12,0.5),(26,10),(44,-0.5),(58,-2.5)],stt=[(0,-2.5),(80,-2.5),(130,-0.5),(180,2.5),(230,1.5),(280,0)])
        t,y=build(seq(s)); return panel("V2 · anterior leads",t,y,[("an","Tall R wave",420+26,10,820,9),("an","Horizontal ST depression",420+58+60,-2.5,1050,-9)],h,col)
    if key=="post_v7":
        s=N(p=1.0,qrs=[(0,0),(10,-1),(26,6),(42,-1),(56,1.8)],stt=[(0,1.8),(90,2.3),(150,2.5),(210,1.5),(260,0)])
        t,y=build(seq(s)); return panel("V7 · posterior lead",t,y,[("an","ST elevation: confirms it",420+56+120,2.5,1150,8)],h,col)
    if key=="avr_avr":
        s=N(p=-1.0,qrs=[(0,0),(10,0.5),(28,-9),(46,0.5),(58,1.8)],stt=[(0,1.8),(100,2.0),(150,1.5),(210,-1),(260,0)])
        t,y=build(seq(s)); return panel("aVR",t,y,[("an","ST elevation ≥ 1 mm",420+58+100,2.0,1100,8.5)],h,col)
    if key=="avr_v5":
        s=N(p=1.0,qrs=[(0,0),(12,-1),(30,10),(48,-1),(60,-2)],stt=[(0,-2),(90,-2.4),(150,-1.5),(200,0.5),(240,0)])
        t,y=build(seq(s)); return panel("V5 · diffuse ST depression",t,y,[("an","ST depression",420+60+90,-2.4,1100,-8.5)],h,col)
    if key=="sg_lbbb":
        s=dict(p=1.0,pr=170,prdep=0,qrs=[(0,0),(30,-8),(70,-14),(110,-9),(140,-2)],stt=[(0,2.5),(80,3),(160,4),(240,2),(300,0)])
        t,y=build(seq(s,3,300,rr=800)); return panel("V1 · LBBB with expected, proportional ST elevation",t,y,[("an","ST elevation < 25% of S depth",300+140+80,3,1180,8)],h,col)
    if key=="sg_exc":
        s=dict(p=1.0,pr=170,prdep=0,qrs=[(0,0),(30,-8),(70,-14),(110,-9),(140,-2)],stt=[(0,6),(80,6.6),(160,6),(240,3),(300,0)])
        t,y=build(seq(s,3,300,rr=800)); return panel("V1 · excessively discordant ST elevation: STEMI",t,y,[("an","≥ 25% of S depth",300+140+80,6.6,1250,11.5)],h,col)
    if key=="sg_conc":
        s=dict(p=1.0,pr=170,prdep=0,qrs=[(0,0),(25,6),(50,9),(75,7),(95,-1),(115,0)],stt=[(0,3),(70,3.4),(140,3),(220,1),(280,0)])
        t,y=build(seq(s,3,300,rr=800)); return panel("V5 · concordant ST elevation: STEMI",t,y,[("an","ST elevation in the same direction as the QRS",300+115+90,3.4,1200,11)],h,col)
    if key=="tam":
        a=N(p=1.0,qrs=[(0,0),(10,-0.5),(24,7),(38,-1),(48,0)],stt=[(0,0),(50,0),(100,0.5),(140,0.8),(180,0.3),(220,0)],pr=130)
        b=N(p=1.0,qrs=[(0,0),(10,-0.3),(24,3.5),(38,-0.5),(48,0)],stt=[(0,0),(50,0),(100,0.3),(140,0.5),(180,0.2),(220,0)],pr=130)
        bs=[(240+i*470,(a if i%2==0 else b)) for i in range(5)]
        t,y=build(bs); return panel("Electrical alternans with low voltage",t,y,[("an","Tall",240+24,7,700,11),("an","Short",240+470+24,3.5,1200,11)],h,col)
    if key=="wpw_sin":
        s=dict(p=1.0,pr=100,prdep=0,qrs=[(0,0),(25,1.0),(50,3),(65,8),(80,6),(110,-0.5)],stt=[(0,-0.5),(70,0.5),(130,2),(190,0.5),(240,0)])
        t,y=build(seq(s,3,360)); return panel("WPW in sinus rhythm",t,y,[("an","Delta wave",360+35,2,520,9),("an","Short PR",360-50,0,150,6),("an","Wide QRS",360+85,7,1000,10)],h,col)
    if key=="wpw_af":
        a=dict(p=0,pr=0,prdep=0,qrs=[(0,0),(25,2),(50,6),(75,8),(100,2),(125,-1),(140,0)],stt=[(0,0),(1,0)])
        c=dict(a,qrs=[(0,0),(15,3),(30,9),(50,-1),(65,0)])
        d=dict(a,qrs=[(0,0),(25,-1),(50,-5),(85,-7),(110,-2),(135,0)])
        ts=[60,300,430,700,830,1050,1160,1440,1550,1830,1950,2200]
        sp=[a,c,a,d,a,c,a,c,d,a,c,a]
        t,y=build(list(zip(ts,sp)),noise=0.08)
        return panel("AF with WPW",t,y,[("an","Irregular, fast",ts[3]+40,-7,780,-11),("an","QRS width and shape vary",ts[8]+50,-5,1700,-11.5)],h,col)
    raise KeyError(key)
