#!/usr/bin/env python3
"""shortkit.py - short vertical video + cover for a blog post.
  python3 shortkit.py video post.json     -> $SHORT_WORK/out/<slug>.mp4 and <slug>-caption.txt
  python3 shortkit.py cover post.json     -> $SHORT_WORK/out/<slug>-thumbnail.jpg
$SHORT_WORK (default: current folder) must hold kokoro-v1.0.onnx, voices-v1.0.bin and the six .woff2 fonts."""
import json, os, sys, subprocess, shutil
WORK = os.environ.get('SHORT_WORK', os.getcwd())
S='#f4f1ea';P='#1d3249';A='#8fb3d4';D='#15273b';M='#3a5270'
def R(x,y,w,h,rx=20,f=P,s=S,sw=10):
    st=f' stroke="{s}" stroke-width="{sw}" stroke-linejoin="round"' if s else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{st}/>'
def L(x1,y1,x2,y2,c=S,w=12):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
def C(cx,cy,r,f=P,s=S,sw=10):
    st=f' stroke="{s}" stroke-width="{sw}"' if s else ''
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{f}"{st}/>'
def PA(d,f='none',s=S,sw=10):
    st=f' stroke="{s}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if s else ''
    return f'<path d="{d}" fill="{f}"{st}/>'
def arrowarc(extra=''):
    return (f'<g {extra}>'+PA('M104.7 145 A110 110 0 0 1 308.3 181',s=S,sw=22)+
            f'<polygon points="314,215 336,176 281,186" fill="{A}" stroke="{A}" stroke-width="6" stroke-linejoin="round"/></g>')
def chip():
    o=R(110,110,180,180,26,P)+R(150,150,100,100,14,A,None)
    for x in (150,200,250):
        o+=L(x,70,x,110,S,12)+L(x,290,x,330,S,12)
    for y in (150,200,250):
        o+=L(70,y,110,y,S,12)+L(290,y,330,y,S,12)
    return o
NEW_ICONS={
"router":L(120,220,120,120)+L(280,220,280,120)+R(60,220,280,90,22,P)+C(120,110,12,A,None)+C(280,110,12,A,None)+PA('M160 180 Q200 145 240 180',s=A,sw=12)+PA('M135 150 Q200 95 265 150',s=A,sw=12)+C(110,265,10,A,None)+C(150,265,10,S,None)+L(220,265,300,265,S,10),
"cards":R(100,80,240,150,22,D)+R(60,170,240,150,22,P)+'<rect x="65" y="205" width="230" height="34" fill="'+A+'"/>'+L(90,275,170,275,S,12),
"coin":C(200,200,140,P)+C(200,200,102,'none',M,8)+f'<text x="200" y="245" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="130" fill="{A}">$</text>',
"toggle":R(50,110,300,100,50,D)+C(300,160,34,A,S,8)+R(50,240,300,100,50,P)+C(100,290,34,S,S,8),
"chart":PA('M60 60 V340 H350',s=S,sw=12)+R(100,230,50,100,8,M,S,8)+R(180,170,50,160,8,P,S,8)+R(260,100,50,230,8,A,S,8),
"checklist":R(80,50,240,300,26,D)+PA('M115 130 l16 16 l30 -34',s=A,sw=14)+L(195,130,285,130,S,12)+PA('M115 205 l16 16 l30 -34',s=A,sw=14)+L(195,205,285,205,S,12)+C(138,275,17,'none',M,8)+L(195,275,260,275,M,12),
"chip":chip(),
"doc":PA('M100 50 H250 L310 110 V350 H100 Z',D)+PA('M250 50 V110 H310',s=S)+L(140,170,270,170,A,12)+L(140,220,270,220,M,12)+L(140,270,230,270,M,12),
"clock":C(200,200,140,D)+L(200,200,200,110,S,14)+L(200,200,265,235,A,14)+C(200,200,12,S,None),
"layers":PA('M200 70 L340 140 L200 210 L60 140 Z',A)+PA('M60 190 L200 260 L340 190',s=S)+PA('M60 240 L200 310 L340 240',s=S),
"idcard":R(50,100,300,200,26,D)+C(130,170,28,A,None)+PA('M88 262 q42 -62 84 0 Z',A,A,4)+L(210,160,310,160,S,12)+L(210,200,310,200,M,12)+L(210,240,280,240,M,12),
"person":C(200,140,60,P)+PA('M80 330 q0 -110 120 -110 q120 0 120 110 Z',P)+C(200,140,22,A,None),
"chat":PA('M70 90 H330 a20 20 0 0 1 20 20 V250 a20 20 0 0 1 -20 20 H190 L120 330 V270 H70 a20 20 0 0 1 -20 -20 V110 a20 20 0 0 1 20 -20 Z',P)+C(130,180,13,A,None)+C(200,180,13,S,None)+C(270,180,13,A,None),
"shield":PA('M200 50 L330 100 V200 C330 280 270 330 200 355 C130 330 70 280 70 200 V100 Z',P)+PA('M140 200 l45 45 l80 -90',s=A,sw=18),
"folder":PA('M50 110 a20 20 0 0 1 20 -20 H150 l35 40 H330 a20 20 0 0 1 20 20 V300 a20 20 0 0 1 -20 20 H70 a20 20 0 0 1 -20 -20 Z',D)+L(100,210,300,210,A,12)+L(100,255,240,255,M,12),
"copy":R(60,60,200,240,22,D)+R(140,110,200,240,22,P)+L(180,170,300,170,A,12)+L(180,220,300,220,M,12)+L(180,270,260,270,M,12),
"palette":C(200,200,140,P)+C(140,150,24,A,None)+C(210,115,24,S,None)+C(275,165,24,M,None)+C(115,225,24,S,None)+C(250,265,34,D,S,8),
"puzzle":C(185,110,34,P)+C(300,225,34,P)+R(70,110,230,230,22,P)+C(185,110,27,P,None)+C(300,225,27,P,None)+R(110,240,70,70,12,A,None),
"magnifier":C(170,170,100,D)+L(245,245,330,330,S,26)+PA('M130 175 l28 28 l48 -55',s=A,sw=16),
"pencil":PA('M80 320 L100 250 L270 80 L320 130 L150 300 Z',P)+PA('M270 80 L320 130',s=A,sw=24)+L(100,250,150,300,S,10)+PA('M80 320 L100 250 L150 300 Z',A,S,6),
"check":C(200,200,140,P)+PA('M130 205 l50 50 l95 -105',s=A,sw=24),
"pin":PA('M200 350 C120 260 90 215 90 160 a110 110 0 0 1 220 0 C310 215 280 260 200 350 Z',P)+C(200,160,40,A,None),
"grid":R(60,70,280,260,18,D)+'<rect x="64" y="74" width="82" height="72" fill="'+A+'"/>'+L(60,150,340,150,S,8)+L(60,235,340,235,S,8)+L(150,70,150,330,S,8)+L(250,70,250,330,S,8)+R(60,70,280,260,18,'none',S,10),
"pulse":R(30,90,340,220,30,D)+PA('M50 210 H120 L150 135 L210 280 L250 175 L280 210 H350',s=A,sw=16),
"mail":R(50,100,300,200,24,D)+PA('M62 122 L200 225 L338 122',s=S,sw=10)+C(330,105,22,A,S,6),
"cloud":PA('M110 290 a70 70 0 0 1 10 -139 a90 90 0 0 1 170 20 a62 62 0 0 1 -6 119 Z',P)+PA('M165 230 l28 28 l55 -62',s=A,sw=16),
"globe":C(200,200,140,D)+'<ellipse cx="200" cy="200" rx="62" ry="140" fill="none" stroke="'+A+'" stroke-width="8"/>'+L(60,200,340,200,S,8)+PA('M82 130 Q200 160 318 130',s=M,sw=8)+PA('M82 270 Q200 240 318 270',s=M,sw=8),
"lock":PA('M130 175 V125 a70 70 0 0 1 140 0 V175',s=S,sw=18)+R(80,170,240,180,28,P)+C(200,248,22,A,None)+L(200,258,200,300,A,14),
"cert":R(60,60,280,220,22,D)+L(100,120,300,120,S,12)+L(100,165,220,165,M,12)+PA('M245 285 l-15 60 l40 -22 l40 22 l-15 -60',P,S,8)+C(270,245,44,A,S,8)+PA('M252 245 l12 12 l24 -26',s=D,sw=10),
"refresh":arrowarc()+arrowarc('transform="rotate(180 200 200)"'),
"key":L(190,200,340,200,S,22)+L(290,200,290,250,S,18)+L(330,200,330,240,S,18)+C(120,200,70,P)+C(120,200,24,D,S,8),
"bell":PA('M120 270 V190 a80 80 0 0 1 160 0 V270 L310 300 H90 Z',P)+C(200,95,12,S,None)+C(200,335,24,A,None),
"db":PA('M70 100 V300 a130 45 0 0 0 260 0 V100',P)+PA('M70 170 a130 45 0 0 0 260 0',s=M,sw=8)+PA('M70 235 a130 45 0 0 0 260 0',s=M,sw=8)+'<ellipse cx="200" cy="100" rx="130" ry="45" fill="'+D+'" stroke="'+S+'" stroke-width="10"/>'+C(300,270,9,A,None)+C(300,205,9,A,None),
"archive":R(60,100,280,70,14,D)+R(80,170,240,170,14,P)+R(160,215,80,28,14,A,None),
"restore":arrowarc()+arrowarc('transform="rotate(180 200 200)"')+L(200,200,200,150,S,12)+L(200,200,238,222,A,12),
"calendar":R(60,90,280,250,26,D)+'<rect x="64" y="94" width="272" height="64" rx="22" fill="'+A+'"/>'+L(130,60,130,120,S,16)+L(270,60,270,120,S,16)+''.join(C(x,y,11,S if (x,y)!=(180,260) else A,None) for x in (110,180,250,310) for y in (205,260,305) if x<=310)+R(60,90,280,250,26,'none',S,10),
"tag":PA('M60 210 L210 60 H340 V190 L190 340 Z',P)+C(285,115,18,A,None)+f'<text x="210" y="240" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="80" fill="{A}" transform="rotate(-45 210 240)">%</text>',
"devices":R(40,110,220,150,16,D)+L(110,300,190,300,S,12)+L(150,260,150,300,S,12)+R(260,160,90,170,18,P)+C(305,305,6,A,None),
"bolt":PA('M230 50 L110 220 H190 L160 350 L300 160 H215 Z',A),
"image":R(50,80,300,240,24,D)+C(125,150,24,A,None)+PA('M62 300 L150 205 L215 270 L270 220 L338 295 Q338 302 330 302 H70 Q62 302 62 300 Z',M,None,0)+PA('M215 270 L270 220 L338 295',s=A,sw=8),
}
NEW_ICONS["frame"]=NEW_ICONS["image"]

BASE_ICONS = {
"alert": '<path d="M200 60 L350 320 H50 Z" fill="#1d3249" stroke="#f4f1ea" stroke-width="10" stroke-linejoin="round"/><line x1="200" y1="150" x2="200" y2="240" stroke="#f4f1ea" stroke-width="14" stroke-linecap="round"/><circle cx="200" cy="278" r="9" fill="#8fb3d4"/>',
"browser": '<rect x="40" y="80" width="320" height="240" rx="22" fill="#15273b" stroke="#f4f1ea" stroke-width="10"/><line x1="40" y1="140" x2="360" y2="140" stroke="#f4f1ea" stroke-width="10"/><circle cx="82" cy="110" r="9" fill="#8fb3d4"/><circle cx="116" cy="110" r="9" fill="#f4f1ea"/><circle cx="150" cy="110" r="9" fill="#f4f1ea"/><circle cx="200" cy="230" r="52" fill="#1d3249" stroke="#f4f1ea" stroke-width="10"/><path d="M176 232 l18 18 l32 -38" fill="none" stroke="#8fb3d4" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>',
"backup": '<path d="M110 270 a70 70 0 0 1 10 -139 a90 90 0 0 1 170 20 a62 62 0 0 1 -6 119 Z" fill="#1d3249" stroke="#f4f1ea" stroke-width="10" stroke-linejoin="round"/><line x1="200" y1="300" x2="200" y2="190" stroke="#8fb3d4" stroke-width="16" stroke-linecap="round"/><path d="M160 225 l40 -42 l40 42" fill="none" stroke="#8fb3d4" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>',
"gauge": '<path d="M50 280 A150 150 0 0 1 350 280 Z" fill="#15273b" stroke="#f4f1ea" stroke-width="10" stroke-linejoin="round"/><path d="M296.4 165.1 A150 150 0 0 1 350 280" fill="none" stroke="#8fb3d4" stroke-width="22" stroke-linecap="round"/><line x1="200" y1="280" x2="288" y2="178" stroke="#f4f1ea" stroke-width="12" stroke-linecap="round"/><circle cx="200" cy="280" r="20" fill="#f4f1ea"/>',
"plug": '<rect x="110" y="150" width="180" height="120" rx="30" fill="#1d3249" stroke="#f4f1ea" stroke-width="10"/><line x1="160" y1="150" x2="160" y2="80" stroke="#f4f1ea" stroke-width="14" stroke-linecap="round"/><line x1="240" y1="150" x2="240" y2="80" stroke="#f4f1ea" stroke-width="14" stroke-linecap="round"/><path d="M200 270 v50 q0 30 -40 30" fill="none" stroke="#f4f1ea" stroke-width="12" stroke-linecap="round"/><circle cx="200" cy="210" r="14" fill="#8fb3d4"/>',
"code": '<rect x="40" y="90" width="320" height="220" rx="26" fill="#f4f1ea"/><text x="200" y="228" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="92" fill="#1d3249">PHP</text><circle cx="78" cy="122" r="9" fill="#8fb3d4"/><circle cx="108" cy="122" r="9" fill="#1d3249"/><circle cx="138" cy="122" r="9" fill="#1d3249"/><rect x="260" y="262" width="70" height="14" rx="7" fill="#8fb3d4"/>',
"logs": '<rect x="70" y="50" width="260" height="300" rx="24" fill="#15273b" stroke="#f4f1ea" stroke-width="10"/><line x1="110" y1="110" x2="290" y2="110" stroke="#3a5270" stroke-width="12" stroke-linecap="round"/><rect x="100" y="146" width="200" height="40" rx="12" fill="#8fb3d4"/><line x1="120" y1="166" x2="270" y2="166" stroke="#15273b" stroke-width="12" stroke-linecap="round"/><line x1="110" y1="226" x2="290" y2="226" stroke="#3a5270" stroke-width="12" stroke-linecap="round"/><line x1="110" y1="276" x2="240" y2="276" stroke="#3a5270" stroke-width="12" stroke-linecap="round"/>',
"server": '<rect x="60" y="70" width="280" height="90" rx="20" fill="#15273b" stroke="#f4f1ea" stroke-width="10"/><rect x="60" y="190" width="280" height="90" rx="20" fill="#1d3249" stroke="#f4f1ea" stroke-width="10"/><circle cx="110" cy="115" r="12" fill="#8fb3d4"/><circle cx="110" cy="235" r="12" fill="#f4f1ea"/><line x1="160" y1="115" x2="300" y2="115" stroke="#f4f1ea" stroke-width="10" stroke-linecap="round"/><line x1="160" y1="235" x2="300" y2="235" stroke="#f4f1ea" stroke-width="10" stroke-linecap="round"/><path d="M250 300 h90 a20 20 0 0 1 20 20 v20 a20 20 0 0 1 -20 20 h-40 l-26 22 v-22 h-24 a20 20 0 0 1 -20 -20 v-20 a20 20 0 0 1 20 -20z" fill="#8fb3d4" stroke="#f4f1ea" stroke-width="8" stroke-linejoin="round" transform="translate(-60 -10) scale(0.9)"/>',
"book": '<path d="M200 110 q-70 -40 -150 -20 v220 q80 -20 150 20 q70 -40 150 -20 v-220 q-80 -20 -150 20 z" fill="#15273b" stroke="#f4f1ea" stroke-width="10" stroke-linejoin="round"/><line x1="200" y1="110" x2="200" y2="330" stroke="#f4f1ea" stroke-width="10"/><line x1="90" y1="150" x2="170" y2="160" stroke="#8fb3d4" stroke-width="12" stroke-linecap="round"/><line x1="90" y1="200" x2="170" y2="210" stroke="#3a5270" stroke-width="12" stroke-linecap="round"/><line x1="230" y1="160" x2="310" y2="150" stroke="#3a5270" stroke-width="12" stroke-linecap="round"/><line x1="230" y1="210" x2="310" y2="200" stroke="#3a5270" stroke-width="12" stroke-linecap="round"/>',
}
TEMPLATE = r'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"PF";font-weight:800;font-style:normal;src:url(__F__playfair-display-latin-800-normal.woff2)}
@font-face{font-family:"PF";font-weight:700;font-style:normal;src:url(__F__playfair-display-latin-700-normal.woff2)}
@font-face{font-family:"PF";font-weight:800;font-style:italic;src:url(__F__playfair-display-latin-800-italic.woff2)}
@font-face{font-family:"Poppins";font-weight:500;src:url(__F__poppins-latin-500-normal.woff2)}
@font-face{font-family:"Poppins";font-weight:600;src:url(__F__poppins-latin-600-normal.woff2)}
@font-face{font-family:"Poppins";font-weight:700;src:url(__F__poppins-latin-700-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0e1925}
#stage{position:relative;width:1080px;height:1920px;background:linear-gradient(165deg,#0e1925 0%,#15273b 55%,#0e1925 100%);overflow:hidden;font-family:Poppins,sans-serif;color:#f4f1ea}
.blob{position:absolute;border-radius:50%;filter:blur(110px)}
#b1{width:760px;height:760px;left:-260px;top:-180px;background:#2f5a85;opacity:.55}
#b2{width:820px;height:820px;right:-330px;bottom:-250px;background:#8fb3d4;opacity:.22}
#dots{position:absolute;inset:0;background-image:radial-gradient(#f4f1ea 1.6px,transparent 1.7px);background-size:44px 44px;opacity:.07}
#prog{position:absolute;left:0;right:0;top:222px;display:flex;gap:10px;align-items:center;justify-content:center}
.seg{width:62px;height:10px;border-radius:6px;background:#2a3d52;position:relative;overflow:hidden}
.seg i{position:absolute;left:0;top:0;bottom:0;background:#ece6d8;border-radius:6px;width:0}
#count{margin-left:14px;font-family:Poppins;font-weight:600;font-size:30px;letter-spacing:3px;color:#d3cec3}
#head{position:absolute;left:60px;right:60px;top:330px;text-align:center;font-family:PF,serif;font-weight:800;font-size:124px;line-height:1.05}
#head em{font-style:italic;background:linear-gradient(90deg,#ece6d8,#8fb3d4);-webkit-background-clip:text;background-clip:text;color:transparent;padding-right:.08em}
#icon{position:absolute;left:290px;top:640px;width:500px;height:500px}
#icon svg{width:500px;height:500px;overflow:visible}
#cap{position:absolute;left:100px;right:100px;top:1190px;text-align:center;font-weight:700;font-size:66px;line-height:1.38}
.w{display:inline-block;padding:0 12px;margin:2px 0;border-radius:16px;opacity:0;transition:none}
.logo{position:absolute;right:64px;bottom:200px;width:84px;height:84px;opacity:.9}
.badge{display:none;position:absolute;right:70px;top:190px;width:84px;height:84px;border-radius:20px;background:#141414;color:#f7f5f0;font-family:PF;font-weight:800;font-size:60px;display:flex;align-items:center;justify-content:center;padding-bottom:6px}
#cta{position:absolute;left:0;right:0;top:1470px;text-align:center;font-weight:600;font-size:40px;color:#b9b3a6;opacity:0}
</style></head><body><div id="stage"><div class="blob" id="b1"></div><div class="blob" id="b2"></div><div id="dots"></div>
<div id="prog"></div><div class="logo"><svg viewBox="0 0 100 100" width="84" height="84"><rect width="100" height="100" rx="24" fill="#ece6d8"/><text x="50" y="72" text-anchor="middle" font-family="PF" font-weight="700" font-size="72" fill="#15273b">__BRAND__</text></svg></div>
<div id="head"></div><div id="icon"></div><div id="cap"></div><div id="cta">Link in the description</div></div>
<script>
const TL=__TL__; const ICONS=__ICONS__; const TOTAL=__TOTAL__;
const steps=TL.scenes.filter(s=>s.label); 
const prog=document.getElementById('prog');
steps.forEach(()=>{const d=document.createElement('div');d.className='seg';d.innerHTML='<i></i>';prog.appendChild(d)});
const cnt=document.createElement('div');cnt.id='count';prog.appendChild(cnt);
const head=document.getElementById('head'),icon=document.getElementById('icon'),cap=document.getElementById('cap'),cta=document.getElementById('cta');
let cur=null;
const ease=x=>1-Math.pow(1-Math.min(1,Math.max(0,x)),3);
function words(txt){return txt.split(/\s+/).filter(Boolean)}
function setScene(sc){
  cur=sc; head.innerHTML=sc.headline;
  icon.innerHTML='<svg viewBox="0 0 400 400">'+ICONS[sc.icon]+'</svg>';
  cap.innerHTML='';
  sc.chunk_info.forEach((ch,ci)=>{
    const wrap=document.createElement('div'); wrap.dataset.ci=ci; wrap.style.display='none';
    const ws=words(ch.text); const wt=ws.map(w=>w.length+(/[.,?!]$/.test(w)?3:0)); const sum=wt.reduce((a,b)=>a+b,0);
    let acc=0; ch.words=ws.map((w,i)=>{const s=acc/sum*ch.dur; acc+=wt[i]; const e=acc/sum*ch.dur; const sp=document.createElement('span'); sp.className='w'; sp.textContent=w; wrap.appendChild(sp); return {s,e,el:sp}});
    cap.appendChild(wrap);
  });
}
function render(t){
  let sc=TL.scenes[TL.scenes.length-1]; for(const s of TL.scenes){ if(t>=s.start && t<s.start+s.dur){sc=s;break}}
  if(sc!==cur) setScene(sc);
  const lt=t-sc.start;
  // head/icon entrance
  const he=ease(lt/0.45); head.style.opacity=he; head.style.transform='translateY('+((1-he)*40)+'px)';
  const ie=ease((lt-0.12)/0.55); icon.style.opacity=ie; icon.style.transform='scale('+(0.7+0.3*ie)+') rotate('+((1-ie)*-6)+'deg)';
  // progress
  const idx=steps.indexOf(sc);
  document.querySelectorAll('.seg').forEach((sg,i)=>{ const f= idx<0 ? (t>=TL.scenes[TL.scenes.length-1].start?1:0) : (i<idx?1:(i===idx?Math.min(1,lt/sc.dur):0)); sg.firstChild.style.width=(f*100)+'%'});
  cnt.textContent = idx>=0 ? sc.label+' / '+String(steps.length).padStart(2,'0') : '';
  prog.style.opacity = (sc.id==='hook'||sc.id==='end')?0:1;
  // captions
  sc.chunk_info.forEach((ch,ci)=>{
    const wrap=cap.children[ci]; const active = lt>=ch.off-0.02 && lt<ch.off+ch.dur+0.18;
    // show only the latest started chunk
    let show=false; const nxt=sc.chunk_info[ci+1]; if(lt>=ch.off-0.02 && (!nxt || lt<nxt.off-0.02)) show=true;
    wrap.style.display=show?'block':'none';
    if(show){ const ct=lt-ch.off; ch.words.forEach(w=>{ const started=ct>=w.s-0.02; const on=started && ct<w.e;
      w.el.style.opacity=started?1:0; w.el.style.background=on?'#ece6d8':'transparent'; w.el.style.color=on?'#15273b':'#f4f1ea'; w.el.style.transform=on?'scale(1.06)':'scale(1)'; }); }
  });
  cta.style.opacity = sc.id==='end'? ease(lt/0.5):0;
}
window.render=render;
</script></body></html>'''

COVER = r'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:"PF";font-weight:800;font-style:normal;src:url(__F__playfair-display-latin-800-normal.woff2)}
@font-face{font-family:"PF";font-weight:800;font-style:italic;src:url(__F__playfair-display-latin-800-italic.woff2)}
@font-face{font-family:"PF";font-weight:700;font-style:normal;src:url(__F__playfair-display-latin-700-normal.woff2)}
@font-face{font-family:"Poppins";font-weight:600;src:url(__F__poppins-latin-600-normal.woff2)}
@font-face{font-family:"Poppins";font-weight:700;src:url(__F__poppins-latin-700-normal.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0e1925}
#s{position:relative;width:1080px;height:1920px;background:linear-gradient(165deg,#0e1925 0%,#15273b 55%,#0e1925 100%);overflow:hidden;font-family:Poppins,sans-serif;color:#f4f1ea}
.blob{position:absolute;border-radius:50%;filter:blur(110px)}
#b1{width:760px;height:760px;left:-260px;top:-180px;background:#2f5a85;opacity:.55}
#b2{width:820px;height:820px;right:-330px;bottom:-250px;background:#8fb3d4;opacity:.22}
#dots{position:absolute;inset:0;background-image:radial-gradient(#f4f1ea 1.6px,transparent 1.7px);background-size:44px 44px;opacity:.07}
#tag{position:absolute;left:0;right:0;top:250px;text-align:center;font-weight:600;font-size:34px;letter-spacing:8px;color:#8fb3d4}
#head{position:absolute;left:50px;right:50px;top:330px;height:470px;display:flex;align-items:center;justify-content:center;text-align:center;font-family:PF,serif;font-weight:800;font-size:150px;line-height:1.04}
#head em{font-style:italic;background:linear-gradient(90deg,#ece6d8,#8fb3d4);-webkit-background-clip:text;background-clip:text;color:transparent;padding-right:.08em}
#icon{position:absolute;left:260px;top:840px;width:560px;height:560px}
#icon svg{width:560px;height:560px;overflow:visible}
#pill{position:absolute;left:0;right:0;top:1470px;display:flex;justify-content:center}
#pill span{background:#ece6d8;color:#15273b;font-weight:700;font-size:46px;padding:20px 52px;border-radius:60px}
#sub{position:absolute;left:0;right:0;top:1600px;text-align:center;font-weight:600;font-size:36px;color:#b9b3a6}
.logo{position:absolute;right:64px;bottom:200px;width:84px;height:84px;opacity:.9}
</style></head><body><div id="s"><div class="blob" id="b1"></div><div class="blob" id="b2"></div><div id="dots"></div>
<div id="tag">QUICK GUIDE</div><div id="head"><div>__H__</div></div><div id="icon"><svg viewBox="0 0 400 400">__I__</svg></div>
<div id="pill"><span>__N__</span></div><div id="sub">Full guide on __SITE__</div>
<div class="logo"><svg viewBox="0 0 100 100" width="84" height="84"><rect width="100" height="100" rx="24" fill="#ece6d8"/><text x="50" y="72" text-anchor="middle" font-family="PF" font-weight="700" font-size="72" fill="#15273b">__BRAND__</text></svg></div></div></body></html>'''

ICONS = dict(BASE_ICONS); ICONS.update(NEW_ICONS)
FONTS = 'file://' + WORK + '/'
OUT = WORK + '/out'
ORD = ["One","Two","Three","Four","Five","Six","Seven","Eight"]
# Branding, from the environment so the same script serves any site:
#   BLOG_BASE    blog URL prefix, used in the caption file
#   SITE_DOMAIN  domain printed on the thumbnail
#   BRAND_LETTER single letter drawn in the corner watermark
BLOG = os.environ.get("BLOG_BASE", "https://example.com/blog/")
SITE = os.environ.get("SITE_DOMAIN", "example.com")
BRAND = os.environ.get("BRAND_LETTER", "B")

def split(s):                      # "shown text|spoken text"
    return tuple(s.split('|')) if '|' in s else (s, s)

def scenes_for(p):
    h = p['hook']
    sc = [dict(id='hook', label='', headline=h[0], icon=h[1], chunks=[split(h[2]), split(h[3])])]
    for i, (hd, ic, l1, l2) in enumerate(p['steps']):
        a, b = split(l1)
        sc.append(dict(id=f's{i+1}', label=f'{i+1:02d}', headline=hd, icon=ic,
                       chunks=[(f'{ORD[i]}. {a}', f'{ORD[i]}. {b}'), split(l2)]))
    sc.append(dict(id='end', label='', headline='Get the full <em>guide</em>', icon='book',
                   chunks=[('Read the full guide on my blog.',) * 2]))
    return sc

def make_video(p):
    import numpy as np, soundfile as sf
    from kokoro_onnx import Kokoro
    slug = p['slug']; W = f'{WORK}/posts/{slug}'; os.makedirs(W, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    K = Kokoro(f'{WORK}/kokoro-v1.0.onnx', f'{WORK}/voices-v1.0.bin')
    sr = 24000; parts = []; tl = {'scenes': []}
    for sc in scenes_for(p):
        pcs = []; ci = []
        for text, say in sc['chunks']:
            s, r = K.create(say, voice='af_heart', speed=1.0, lang='en-us'); s = np.asarray(s, dtype=np.float32)
            pcs += [s, np.zeros(int(r * 0.18), dtype=np.float32)]; ci.append({'text': text, 'dur': len(s) / r})
        pcs.append(np.zeros(int(sr * 0.35), dtype=np.float32)); a = np.concatenate(pcs); parts.append(a)
        sc['dur'] = len(a) / sr; sc['chunk_info'] = ci; del sc['chunks']; tl['scenes'].append(sc)
    t = 0
    for sc in tl['scenes']:
        sc['start'] = t; off = 0
        for ch in sc['chunk_info']: ch['off'] = off; off += ch['dur'] + 0.18
        t += sc['dur']
    total = t; sf.write(f'{W}/full.wav', np.concatenate(parts), sr)
    html = (TEMPLATE.replace('__F__', FONTS).replace('__TL__', json.dumps(tl))
            .replace('__ICONS__', json.dumps(ICONS)).replace('__TOTAL__', str(total))
            .replace('__BRAND__', BRAND).replace('__SITE__', SITE))
    open(f'{W}/index.html', 'w').write(html)
    fr = f'{W}/frames'; shutil.rmtree(fr, ignore_errors=True)
    ps = [subprocess.Popen(['python3', '-I', os.path.abspath(__file__), 'render', f'{W}/index.html', fr, str(total), str(k), '2']) for k in range(2)]
    for q in ps: q.wait()
    mp4 = f'{OUT}/{slug}.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-i', f'{fr}/f%05d.jpg', '-i', f'{W}/full.wav',
                    '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', mp4], check=True)
    shutil.rmtree(fr, ignore_errors=True)
    steps = '\n'.join(f'{i+1}. ' + split(s[2])[0].rstrip('.') for i, s in enumerate(p['steps']))
    cap = (f"{p['title']}\n\n{split(p['hook'][2])[0]} {split(p['hook'][3])[0]}\n\n{steps}\n\n"
           f"Read the full guide: {BLOG}{slug}\n\n{p['tags']}\n")
    open(f'{OUT}/{slug}-caption.txt', 'w').write(cap)
    print('video', mp4, round(total, 1), 's')

def make_cover(p):
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True); h = p['hook']; n = len(p['steps'])
    html = (COVER.replace('__F__', FONTS).replace('__H__', h[0]).replace('__I__', ICONS[h[1]])
            .replace('__N__', p.get('pill', f'{n} STEPS'))
            .replace('__BRAND__', BRAND).replace('__SITE__', SITE))
    open(f'{WORK}/cover.html', 'w').write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1080, 'height': 1920}); pg.goto('file://' + WORK + '/cover.html')
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(400)
        pg.screenshot(path=f"{OUT}/{p['slug']}-thumbnail.jpg", type='jpeg', quality=94); b.close()
    print('cover', p['slug'])

def render(html, out, total, part, parts, fps=30):
    from playwright.sync_api import sync_playwright
    os.makedirs(out, exist_ok=True); n = int(total * fps) + 1
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1080, 'height': 1920}); pg.goto('file://' + html)
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(500)
        for i in range(part, n, parts):
            pg.evaluate(f'render({i / fps})'); pg.screenshot(path=f'{out}/f{i:05d}.jpg', type='jpeg', quality=93)
        b.close()

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'render': render(sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
    else:
        post = json.load(open(sys.argv[2]))
        (make_video if cmd == 'video' else make_cover)(post)
