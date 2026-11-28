"""Schematic torso diagrams (SVG). Not real photographs."""
W=940
def torso(ox,label,extra,back=False):
    skin="#f1d5c0"
    p=(f'<path transform="translate({ox},60)" d="M60,50 C60,28 110,18 180,18 C250,18 300,28 300,50 L292,150 C282,200 262,240 262,282 L288,410 L72,410 L98,282 C98,240 78,200 68,150 Z" fill="{skin}" stroke="#7a4b35" stroke-width="3"/>')
    return p+f'<g transform="translate({ox},60)">{extra}</g>'+f'<text x="{ox+180}" y="40" font-size="30" font-weight="700" fill="#5a1a2b" text-anchor="middle">{label}</text>'
def blot(cx,cy,rx,ry,rot=0,idn="b"):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx+14}" ry="{ry+14}" transform="rotate({rot} {cx} {cy})" fill="#c9b458" opacity=".45"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({rot} {cx} {cy})" fill="#6a3d8f" opacity=".75"/>'
            f'<ellipse cx="{cx+4}" cy="{cy-3}" rx="{rx*0.55:.0f}" ry="{ry*0.55:.0f}" transform="rotate({rot} {cx} {cy})" fill="#2f3f8f" opacity=".6"/>')
def cullen():
    front=('<ellipse cx="180" cy="270" rx="9" ry="12" fill="#c49a80" stroke="#7a4b35" stroke-width="2"/>'
           +blot(180,270,64,52)+
           '')
    back=('<line x1="180" y1="30" x2="180" y2="400" stroke="#b08968" stroke-width="2" stroke-dasharray="6 6"/>'
          '<line x1="80" y1="195" x2="280" y2="195" stroke="#9c6b52" stroke-width="2" stroke-dasharray="3 5"/>'
          '<line x1="80" y1="330" x2="280" y2="330" stroke="#9c6b52" stroke-width="2" stroke-dasharray="3 5"/>'
          +blot(118,262,30,66,6)+blot(242,262,30,66,-6)+
          '<text x="180" y="188" font-size="19" fill="#7a4b35" text-anchor="middle">last rib</text>'
          '<text x="180" y="352" font-size="19" fill="#7a4b35" text-anchor="middle">top of hip</text>'
          '')
    svg=(f'<svg viewBox="0 0 {W} 600" width="{W}" height="600" style="display:block">'
         +torso(20,"Front",front)+torso(500,"Back",back)
         +'<text x="200" y="548" font-size="30" font-weight="700" fill="#5a1a2b" text-anchor="middle">Cullen sign</text><text x="200" y="582" font-size="25" fill="#5a1a2b" text-anchor="middle">around the belly button</text>'
         +'<text x="680" y="548" font-size="30" font-weight="700" fill="#5a1a2b" text-anchor="middle">Grey Turner sign</text><text x="680" y="582" font-size="25" fill="#5a1a2b" text-anchor="middle">the flanks</text>'
         +'</svg>')
    return svg
