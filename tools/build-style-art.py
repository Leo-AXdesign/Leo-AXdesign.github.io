#!/usr/bin/env python3
"""Original educational SVG studies; no third-party pictures or traced artworks.
Run after editing this file. Existing six hand-drawn studies are retained.
"""
from pathlib import Path
from html import escape
import math, random
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets' / 'styles'
OUT.mkdir(parents=True, exist_ok=True)

def text(x,y,s,size=32,fill='#171717',family='Arial,Helvetica,sans-serif',extra=''):
    return f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" fill="{fill}" {extra}>{escape(s)}</text>'
def rect(x,y,w,h,fill,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'
def circle(x,y,r,fill,extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" {extra}/>'
def path(d,fill='none',stroke='#171717',width=3,extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'
def group(s,transform):
    return f'<g transform="{transform}">{s}</g>'
def base(c): return rect(0,0,640,480,c)
def label(s,fill='#171717'): return text(35,448,s,15,fill,extra='letter-spacing="3"')
def noise(seed=7,fill='#222',n=800,opacity=.15):
    rng=random.Random(seed)
    return f'<g opacity="{opacity}">'+''.join(circle(round(rng.uniform(0,640),1),round(rng.uniform(0,480),1),rng.choice([.6,1,1.6]),fill) for _ in range(n))+'</g>'
def lines(x,y,width,count,color='#aaa',gap=16):
    return ''.join(rect(x,y+i*gap,width if i<count-1 else width*.68,3,color) for i in range(count))
def save(slug,title,body,folder=OUT):
    folder.mkdir(parents=True,exist_ok=True)
    (folder/f'{slug}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img"><title>{escape(title)} — Design Hub illustrative study</title><desc>Original illustration explaining visual characteristics. Not a historical artwork or a screenshot of a product.</desc>{body}</svg>')
chrome='<defs><linearGradient id="metal" x2="0" y2="1"><stop stop-color="#fff"/><stop offset=".3" stop-color="#bec5d2"/><stop offset=".48" stop-color="#3f4054"/><stop offset=".55" stop-color="#fff"/><stop offset="1" stop-color="#727c95"/></linearGradient></defs>'
soft='<defs><radialGradient id="ball" cx=".3" cy=".2"><stop stop-color="#fff1ea"/><stop offset=".55" stop-color="#ffa9a1"/><stop offset="1" stop-color="#b96b85"/></radialGradient><filter id="shadow"><feDropShadow dx="0" dy="14" stdDeviation="13" flood-color="#443359" flood-opacity=".2"/></filter></defs>'
art={}
# Organic foliage and flowing ornaments rather than a reproduction of an existing poster.
art['art-nouveau']=base('#e8e2c7')+rect(25,25,590,430,'none','rx="130" stroke="#606c43" stroke-width="4"')
for flip in ['', 'translate(640 0) scale(-1 1)']:
    stem=path('M70 440C120 340 25 250 100 150S210 30 200 130S90 250 155 290','#c6c69c','#606c43',5)
    for x,y,a in [(95,335,-20),(90,230,20),(125,137,-35),(164,85,40)]:
        stem+=group(path(f'M{x} {y}q-65-60-38-90q70 22 38 90','#7d8c60','#606c43',2),f'rotate({a} {x} {y})')
    art['art-nouveau']+=group(stem,flip) if flip else stem
art['art-nouveau']+=text(320,230,'FLORA',62,'#455135','Georgia,serif','text-anchor="middle"')+text(320,275,'BOTANICAL STUDY',15,'#455135',extra='text-anchor="middle" letter-spacing="3"')
art['dada']=base('#dcd5c5')+group(rect(80,45,450,100,'#232323')+text(96,125,'DA',94,'#eee9d9',extra='font-weight="900"'),'rotate(-12 320 240)')+group(rect(250,150,275,180,'#b73928')+text(263,285,'DA',130,'#eee9d9','Georgia,serif'),'rotate(12 320 240)')+group(lines(40,340,260,7,'#333',12),'rotate(-8 40 340)')+circle(115,265,55,'#222')+text(58,294,'?',85,'#ddd','Georgia,serif')+label('CHANCE / CUT / REASSEMBLE')+noise(n=400)
art['constructivism']=base('#eadfbe')+circle(430,210,150,'#202020')+path('M25 370L335 25L360 420Z','#d63827','none')+group(rect(70,330,520,65,'#d63827')+text(86,381,'FORWARD',57,'#f4e8ce',extra='font-weight="900"'),'rotate(-21 320 240)')+lines(40,50,115,6,'#333',12)
art['de-stijl']=base('#f5f0dd')+rect(0,0,245,200,'#d53725')+rect(410,290,230,190,'#e7bd24')+rect(245,200,165,280,'#23539d')+''.join(path(d,stroke='#151515',width=16) for d in ['M245 0V480','M410 0V480','M0 200H640','M410 290H640','M0 390H245'])
art['bauhaus']=base('#eee4c9')+circle(210,210,125,'#d74429')+rect(270,100,230,230,'#e9b72c')+path('M335 60L545 375H125Z','#17467b','none',extra='opacity=".88"')+text(38,435,'FORM + FUNCTION',30,extra='font-weight="700"')
art['art-deco']=base('#112829')
for i in range(11):
    a=math.pi*(i/10); x=320+280*math.cos(a); y=320-280*math.sin(a)
    art['art-deco']+=path(f'M320 330L{x:.1f} {y:.1f}',stroke='#cba866',width=3)
art['art-deco']+=rect(30,30,580,420,'none','stroke="#cba866" stroke-width="3"')+path('M150 350V280H200V240H250V195H390V240H440V280H490V350','#112829','#cba866',4)+text(320,355,'NOCTURNE',45,'#e8cf95','Georgia,serif','text-anchor="middle"')+text(320,399,'GEOMETRY & ORNAMENT',14,'#e8cf95',extra='text-anchor="middle" letter-spacing="3"')
art['mid-century-modern']=base('#e8dfc2')+path('M90 80Q260 15 240 190T95 390Q15 210 90 80','#cf6d3e','none')+path('M290 85Q535 20 545 210T325 355Q450 235 290 85','#66764b','none')+path('M150 80L460 410M300 140L165 330',stroke='#252b25',width=8)+circle(415,120,62,'#d4ad37')+label('EVERYDAY / MODERN')
art['swiss-style']=base('#eeeae1')+text(36,79,'form',67,extra='font-weight="700"')+text(36,140,'and rhythm',64,extra='font-weight="700"')+rect(37,166,562,3,'#111')+circle(325,300,116,'#e94a32')+circle(440,300,116,'#172f47','opacity=".88"')+text(37,221,'01—08',20)+lines(38,249,120,6,'#333',14)+label('TYPOGRAPHIC STUDY / 01')
art['pop-art']=base('#ffde32')+'<defs><pattern id="dots" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="7" cy="7" r="3" fill="#ec544b"/></pattern></defs>'+rect(0,0,640,480,'url(#dots)')+path('M55 180L180 155L152 65L270 125L340 45L370 134L540 89L495 185L603 248L477 289L523 405L376 344L290 433L242 336L85 376L136 281L30 240Z','#f7f6df','#172c66',9)+text(320,283,'WOW!',112,'#1957b9',extra='text-anchor="middle" font-weight="900" transform="rotate(-9 320 240)"')
art['psychedelic']=base('#773398')
for i in range(12):
    art['psychedelic']+=f'<ellipse cx="320" cy="240" rx="{330-i*23}" ry="{250-i*17}" fill="{["#f29a2d","#d53e93","#502982"][i%3]}" transform="rotate({i*9} 320 240)"/>'
art['psychedelic']+=text(320,240,'MIND',89,'#f4ed71','Georgia,serif','text-anchor="middle" font-weight="bold"')+text(320,315,'WAVES',68,'#f4ed71','Georgia,serif','text-anchor="middle" font-weight="bold"')
art['punk']=base('#dedbcf')+group(rect(45,45,550,110,'#111')+text(65,130,'MAKE NOISE',76,'#eee',extra='font-weight="900"'),'rotate(-6 320 240)')
for i,(letter,y) in enumerate(zip('DIY',[240,220,258])):
    art['punk']+=group(rect(70+i*160,y-75,130,145,['#d22f28','#f3f0df','#111'][i])+text(88+i*160,y+40,letter,116,['white','#111','white'][i],family='Georgia,serif'),f'rotate({[-8,12,-5][i]} {100+i*160} {y})')
art['punk']+=noise(5,n=1000,opacity=.3)+label('CUT IT. COPY IT. PASS IT ON.')
art['memphis']=base('#f4b9b8')+path('M55 375L165 95L275 375Z','#edd85b','#25223c',5)+circle(430,177,100,'#71c9cb','stroke="#27223f" stroke-width="5"')+group(rect(315,285,260,70,'#a58bd5','stroke="#27223f" stroke-width="5"'),'rotate(-17 420 320)')
for x,y in [(45,55),(280,70),(480,385)]: art['memphis']+=path(f'M{x} {y}q15-30 30 0t30 0t30 0',stroke='#27223f',width=8)
art['memphis']+=''.join(circle(x,y,4,'#27223f') for x in range(360,520,22) for y in range(130,220,22))+label('PATTERN / PLAY')
art['grunge']=base('#bcb7a5')+group(text(22,180,'FRAG',135,'#282b27',extra='font-weight="900"')+text(72,300,'MENT',125,'#282b27',extra='font-weight="900"'),'rotate(-7 320 240)')+text(65,348,'fragments fragments',40,'#8c3933',extra='letter-spacing="-3"')+noise(8,n=2300,opacity=.55)
for i in range(18): art['grunge']+=path(f'M{(i*53)%640} 0l{-80+i*11} 480',stroke='#ece7d5',width=1+i%3)
art['retrofuturism']=base('#182f45')+circle(455,125,85,'#e6c58d')+'<ellipse cx="455" cy="125" rx="140" ry="28" fill="none" stroke="#d88b65" stroke-width="13" transform="rotate(-20 455 125)"/>'+path('M0 390Q320 260 640 390V480H0Z','#d48b66','none')+path('M100 350Q300 275 510 350Q300 420 100 350','#d5e5dc','none')+path('M235 328Q300 218 365 328Z','#81b7b9','none')+text(36,80,'TOMORROW',36,'#ebdfba',extra='letter-spacing="4"')+label('THE FUTURE, REMEMBERED','#f5e2b5')
art['y2k']=base('#d8d8ed')+chrome+'<ellipse cx="320" cy="240" rx="270" ry="124" fill="none" stroke="url(#metal)" stroke-width="28" transform="rotate(-22 320 240)"/>'+text(320,295,'Y2K',150,'url(#metal)',extra='text-anchor="middle" font-weight="900" font-style="italic" stroke="#6f7792" stroke-width="1"')+path('M536 40L545 77L582 86L545 95L536 132L527 95L490 86L527 77Z','#fafaff','none')+label('TRANSLUCENT / CHROME / DIGITAL','#555671')
art['frutiger-aero']='<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#359bda"/><stop offset="1" stop-color="#d7f6ff"/></linearGradient><radialGradient id="bubble" cx=".3" cy=".2"><stop stop-color="#fff" stop-opacity=".8"/><stop offset=".4" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#ddfaff" stop-opacity=".65"/></radialGradient></defs>'+base('url(#sky)')+path('M0 330Q170 220 360 345T640 300V480H0Z','#81c735','none')+path('M0 400Q370 260 640 365V480H0Z','#52a92f','none')+''.join(circle(x,y,r,'url(#bubble)','stroke="#e9ffff" stroke-width="2"') for x,y,r in [(210,165,112),(437,225,80),(480,80,30)])+path('M160 180Q190 100 275 140Q240 240 160 180','#70bf4a','#e3ffd7',3)+label('FRESH / GLOSS / NATURE','#fff')
art['flat-design']=base('#f6dfba')+rect(108,72,425,290,'#32567a','rx="12"')+rect(130,95,381,240,'#a3d5d0')+rect(155,122,126,186,'#ee876b')+rect(305,122,176,60,'#fff2ce')+lines(305,211,170,5,'#548d91',18)+path('M65 362H575L550 396H90Z','#324653','none')+circle(544,111,39,'#e5ad32')+label('SIMPLE SHAPES / SOLID COLOR')
art['material-design']=base('#dce2eb')+ '<defs><filter id="elevation"><feDropShadow dx="0" dy="10" stdDeviation="7" flood-opacity=".22"/></filter></defs>'+rect(95,50,450,380,'#f6f6fc','rx="14"')+rect(95,50,450,92,'#5d54b0','rx="14"')+text(125,108,'Collections',33,'white')+rect(120,168,400,178,'white','rx="9" filter="url(#elevation)"')+circle(169,210,18,'#d5d0ee')+lines(205,205,270,2,'#9c98af',16)+lines(145,268,320,3,'#cbc7dc',18)+circle(490,370,40,'#6659b6','filter="url(#elevation)"')+path('M470 370H510M490 350V390',stroke='white',width=4)
art['brutalism-web']=base('#eee')+rect(24,22,592,436,'none','stroke="black" stroke-width="3"')+text(40,57,'INDEX.HTML',20,family='monospace')+path('M24 77H616',width=3)+text(38,165,'RAW',100,extra='font-weight="900"')+text(38,252,'INTERNET',74,extra='font-weight="900"')+text(40,310,'[01] ENTER THE ARCHIVE',24,'#00e',family='monospace',extra='text-decoration="underline"')+text(40,354,'[02] READ THE MANIFESTO',24,'#00e',family='monospace',extra='text-decoration="underline"')+path('M24 390H616',width=3)+text(40,432,'NO DECORATION. JUST CONTENT.',20,family='monospace')
art['vaporwave']='<defs><linearGradient id="vapor" x2="0" y2="1"><stop stop-color="#44266c"/><stop offset="1" stop-color="#f09fba"/></linearGradient></defs>'+base('url(#vapor)')+circle(320,174,110,'#f3b2c0')+rect(0,290,640,190,'#483573')
for i in range(12): art['vaporwave']+=path(f'M320 290L{(i-3)*130} 480',stroke='#6fe9ed',width=2)
for y in [300,317,340,375,423,478]: art['vaporwave']+=path(f'M0 {y}H640',stroke='#6fe9ed',width=2)
art['vaporwave']+=rect(93,220,70,160,'#e5c8dc')+rect(77,205,102,20,'#faf0f2')+''.join(rect(x,230,6,145,'#b6a2c8') for x in range(103,158,15))+text(335,250,'AFTER / 90',39,'#422964','Georgia,serif')
art['corporate-memphis']=base('#f5e7da')+circle(345,112,32,'#e9a481')+path('M310 148Q400 140 427 246L337 279L255 204Z','#6f63b5','none')+path('M320 183Q240 190 155 95L113 123Q208 298 321 238Z','#6f63b5','none')+path('M367 256L492 366L461 397L306 309Z','#eb805f','none')+path('M332 260L255 412L202 411L263 269Z','#eb805f','none')+path('M201 411L262 411L285 435H190Z','#323559','none')+path('M459 394L493 364L533 402L524 419Z','#323559','none')+circle(120,100,24,'#e9a481')+circle(514,158,45,'#d6c28a')+label('FLAT PEOPLE / OVERSIZED GESTURES')
art['neumorphism']='<defs><filter id="raised" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="-10" dy="-10" stdDeviation="8" flood-color="white" flood-opacity=".9"/><feDropShadow dx="10" dy="10" stdDeviation="8" flood-color="#a7b1c1" flood-opacity=".65"/></filter></defs>'+base('#e0e5ec')+rect(175,55,290,360,'#e0e5ec','rx="38" filter="url(#raised)"')+circle(320,212,85,'#e0e5ec','filter="url(#raised)"')+path('M307 176L350 212L307 248Z','#a1aebf','none')+rect(215,338,210,16,'#e0e5ec','rx="8" filter="url(#raised)"')+circle(280,346,13,'#a4b1c4')
art['risograph']=base('#f2e8d4')+circle(260,218,140,'#ff6d80','style="mix-blend-mode:multiply"')+path('M280 70L540 355H90Z','#237cc4','none',0,extra='style="mix-blend-mode:multiply"')+text(54,416,'TWO INKS',62,'#ed6078',extra='font-weight="900"')+text(58,419,'TWO INKS',62,'#237cc4',extra='font-weight="900" opacity=".6"')+noise(10,fill='#f2e8d4',n=2400,opacity=.65)
art['collage']=base('#c9bca4')+group(rect(45,66,310,330,'#eee5cc')+lines(65,90,265,18,'#80796b',15),'rotate(-7 200 200)')+group(rect(273,73,292,313,'#faf5e8')+rect(290,90,258,235,'#91b9b4')+circle(455,149,42,'#eed593')+path('M290 325L375 177L470 325Z','#537c76','none')+path('M390 325L486 213L548 325Z','#385957','none'),'rotate(9 400 200)')+group(rect(251,65,140,37,'#e2b96d','opacity=".8"'),'rotate(-13 320 80)')+text(80,413,'collected moments',32,'#32322c','cursive')+circle(556,371,47,'#d45240')+text(536,385,'★',35,'#fff')
art['maximalism']=base('#e37fb6')
for x in range(0,640,64):
 for y in range(0,480,64):
  if (x//64+y//64)%2==0: art['maximalism']+=rect(x,y,64,64,'#f2a954')
art['maximalism']+=group(rect(65,55,480,105,'#3369ab')+text(85,139,'MORE',97,'#f5eb75','Georgia,serif'),'rotate(-8 320 240)')+circle(455,291,130,'#b8d54b')+text(40,290,'is more',99,'#722b53','Georgia,serif')+group(text(70,405,'AND MORE!',65,'#213995',extra='font-weight="900"'),'rotate(6 320 240)')+''.join(circle(70+i*30,330,9,'#fff6ce') for i in range(6))
art['pixel-art']=base('#161e3f')
for i,(x,h,w) in enumerate([(30,130,80),(125,230,100),(242,165,70),(332,280,100),(450,200,80),(549,145,65)]):
 art['pixel-art']+=rect(x,440-h,w,h,['#354166','#4a547b'][i%2])
 for xx in range(x+12,x+w-10,22):
  for yy in range(452-h,430,25): art['pixel-art']+=rect(xx,yy,8,10,'#ffc778' if (xx+yy)%3 else '#72bfc5')
art['pixel-art']+=rect(455,55,48,48,'#f6dbac')+rect(443,67,72,24,'#f6dbac')+''.join(rect(x,y,4,4,'#f4d9a2') for x,y in [(50,60),(170,40),(265,100),(390,40),(580,135),(85,180)])+rect(0,440,640,40,'#927dad')
art['cyberpunk']=base('#14152b')+rect(36,40,135,400,'#232743')+rect(430,15,180,440,'#282441')+rect(225,110,145,330,'#1e3040')+''.join(path(f'M0 {y}H640',stroke='#c1489a',width=.5) for y in range(0,480,7))+rect(51,77,100,215,'#ed4aa8','rx="4"')+text(78,145,'N',66,'#202440',extra='font-weight="900"')+text(78,217,'E',66,'#202440',extra='font-weight="900"')+rect(456,131,125,46,'none','stroke="#5af1ed" stroke-width="5"')+text(466,161,'24 / 7',24,'#5af1ed')+path('M200 480L290 300L420 480',stroke='#5af1ed',width=4)+text(47,400,'SIGNAL LOST_',38,'#5af1ed',family='monospace')+rect(0,353,460,5,'#ed4aa8')
art['japanese-modern']=base('#f0ecdf')+circle(320,210,138,'#d64530')+path('M182 210H458L320 348Z','#252c31','none')+path('M182 210L320 72V348Z','#e9b850','none')+text(43,105,'形',52,extra='font-weight="700"')+text(43,170,'と',40)+text(43,235,'間',52,extra='font-weight="700"')+rect(555,57,2,300,'#333')+text(35,443,'FORM / SPACE',20,extra='letter-spacing="4"')
for slug,body in art.items(): save(slug,slug.replace('-',' ').title(),body)
print(f'{len(art)} style studies drawn; 6 existing original studies retained.')

# Trend illustrations: specific demonstrations rather than generic cover art.
T=ROOT/'assets'/'trends'
tr={}
tr['liquid-glass']='<defs><linearGradient id="lg" x2="1" y2="1"><stop stop-color="#5490bc"/><stop offset="1" stop-color="#efd9c4"/></linearGradient><linearGradient id="pane" x2="0" y2="1"><stop stop-color="white" stop-opacity=".65"/><stop offset=".5" stop-color="white" stop-opacity=".12"/><stop offset="1" stop-color="white" stop-opacity=".5"/></linearGradient><filter id="blur"><feGaussianBlur stdDeviation="5"/></filter></defs>'+base('url(#lg)')+path('M0 310Q200 80 640 215V480H0Z','#527c80','none')+circle(470,100,66,'#f4e5c9')+rect(73,174,494,130,'url(#pane)','rx="65" stroke="#ffffffbb" stroke-width="3"')+rect(88,188,464,101,'none','rx="50" stroke="#ffffff55" stroke-width="7" filter="url(#blur)"')+''.join(circle(x,239,30,'#ffffff66') for x in [142,261,380,499])+path('M129 241L142 228L155 241V256H129Z',stroke='#344950',width=4)+path('M249 239H273M261 227V251',stroke='#344950',width=4)+label('REFRACTION / FLOATING CONTROLS','#fff')
tr['cloud-dancer']=base('#dedbd3')+rect(145,55,350,365,'#f4f1e8','rx="2"')+rect(145,315,350,105,'#fff')+text(170,355,'CLOUD DANCER',24)+text(170,388,'2026 / SOFT WHITE',15)+text(36,451,'PALETTE STUDY · NOT A COLOR STANDARD',12,'#666')
tr['human-touch']=base('#f1e4d1')+path('M69 80Q180 35 262 80L250 375Q160 350 60 388Z','#ebc35e','#8e6a38',2)+path('M315 95Q400 50 545 83L578 370Q450 400 325 353Z','#d8a4a2','#8e6a38',2)+path('M105 175Q137 80 177 175T220 175M351 180q72-110 147 0M353 236l143 9M102 269l103-11',stroke='#4a5b52',width=6)+text(80,326,'made by hand',22,'#4a5b52','cursive')+noise(5,n=650,opacity=.1)+label('LEAVE A TRACE')
tr['expressive-type']=base('#171c30')+text(34,160,'STRETCH',90,'#e9ed69',extra='font-weight="900" textLength="570" lengthAdjust="spacingAndGlyphs"')+text(34,276,'TYPE',130,'#f39fa9',extra='font-weight="900" textLength="570" lengthAdjust="spacingAndGlyphs"')+text(34,393,'MOVE',85,'#a9cbe4',extra='font-weight="900" letter-spacing="31"')
tr['neo-brutalism']=base('#efe7cb')+rect(82,70,486,340,'#161616')+rect(65,53,486,340,'#faf4db','stroke="#161616" stroke-width="5"')+rect(65,53,486,63,'#ddf174','stroke="#161616" stroke-width="5"')+text(90,96,'PLAYGROUND',25,extra='font-weight="700"')+text(96,208,'BUILD IT.',60,extra='font-weight="900"')+rect(105,274,220,70,'#171717')+rect(95,264,220,70,'#c8b4eb','stroke="black" stroke-width="4"')+text(118,310,'START →',29)+circle(451,275,52,'#f1a063','stroke="black" stroke-width="4"')
tr['pixel-nostalgia']=base('#a9a2bd')+rect(50,48,540,380,'#d9d9d9','stroke="#fff" stroke-width="5"')+rect(60,58,520,42,'#3c4184')+text(74,87,'memory.exe',23,'white',family='monospace')+text(82,169,'WELCOME BACK_',31,family='monospace')+rect(85,215,300,24,'white','stroke="#777" stroke-width="3"')+''.join(rect(91+i*23,221,18,12,'#4c5684') for i in range(9))+text(82,284,'LOADING MEMORIES...',22,family='monospace')+rect(415,275,128,94,'#efc75f')+rect(415,260,60,25,'#efc75f')+label('LOW RES / HIGH NOSTALGIA')
tr['bento-grid']=base('#f1f0ed')+rect(38,38,350,252,'#d3dfcc','rx="22"')+rect(406,38,196,150,'#e9cebb','rx="22"')+rect(406,206,196,236,'#c6cce4','rx="22"')+rect(38,308,166,134,'#e5d7a5','rx="22"')+rect(222,308,166,134,'#d8c8d5','rx="22"')+text(65,103,'Overview',30)+text(65,210,'24',98,extra='font-weight="700"')+path('M432 382l34-60 32 20 48-83 30 20',stroke='#56618a',width=9)+circle(121,375,32,'#a99a65')+text(245,388,'Aa',45)+lines(430,85,125,4,'#b28d78',17)
tr['chrome']=base('#26213a')+chrome+text(320,290,'Aa',230,'url(#metal)',extra='text-anchor="middle" font-weight="900" font-style="italic"')+label('LIQUID METAL / SPECULAR LIGHT','#d7d8ef')
tr['dopamine-color']=base('#ee644c')+rect(30,30,280,420,'#f3c831','rx="140"')+circle(460,170,137,'#7152c4')+rect(330,325,280,125,'#b7da55','rx="62"')+text(92,269,'JOY',68,'#c84659',extra='font-weight="900"')+text(413,192,'!',95,'#f2b8cc',extra='font-weight="900"')
tr['scrapbook']=base('#e6dcca')+rect(80,40,480,400,'#f7f2e6')+''.join(path(f'M80 {y}H560',stroke='#abc1c7',width=1) for y in range(90,440,30))+group(rect(119,115,220,235,'#e2aa7f')+circle(230,207,61,'#f1d575'),'rotate(-8 220 220)')+group(rect(328,166,175,160,'#b2c7b5')+text(347,258,'hello!',36,'#354a3e','cursive'),'rotate(10 400 240)')+path('M127 82q70-32 135 0M144 380q105-28 300 4',stroke='#c45346',width=4)+rect(180,92,120,30,'#d2bb86','opacity=".85"')+text(350,118,'note to self',23,'#354a3e','cursive')
tr['editorial']=base('#f0ece1')+text(40,105,'A slower',64,'#38392f','Georgia,serif')+text(40,175,'kind of story.',64,'#38392f','Georgia,serif')+rect(40,206,560,1,'#555')+rect(40,236,236,174,'#b4bea7')+circle(157,315,64,'#d9d9bf')+lines(310,246,280,11,'#99998c',15)+text(40,451,'VOL. 01 / TAKE YOUR TIME',14)
tr['tactile-3d']=soft+base('#e8ddd8')+circle(241,226,124,'url(#ball)','filter="url(#shadow)"')+rect(349,142,170,200,'url(#ball)','rx="65" filter="url(#shadow)"')+label('SOFT / ROUNDED / TACTILE','#675263')
tr['print-texture']=base('#eee1c9')+rect(80,50,480,370,'#f2ca46')+group(circle(280,205,125,'#f05d72')+circle(350,205,125,'#297ab0','style="mix-blend-mode:multiply"'),'rotate(-12 320 240)')+text(112,374,'OVERPRINT',56,'#155e90',extra='font-weight="900"')+noise(11,fill='#eee1c9',n=2200,opacity=.65)
tr['aura-gradient']='<defs><filter id="aura"><feGaussianBlur stdDeviation="45"/></filter></defs>'+base('#e5d5e5')+'<g filter="url(#aura)">'+circle(230,200,135,'#f0925c')+circle(410,250,135,'#7776d5')+circle(320,150,70,'#f6db94')+'</g>'+text(320,263,'aura',75,'#fff',family='Georgia,serif',extra='text-anchor="middle"')
tr['motion-interface']=base('#edf0ec')
for x,y,w,h,c in [(40,80,155,260,'#d3d9d0'),(243,120,155,260,'#c7d5ca'),(446,80,155,260,'#a9c9bb')]:
 tr['motion-interface']+=rect(x,y,w,h,'white','rx="15" stroke="#929e98" stroke-width="2"')+rect(x+13,y+48,w-26,96,c,'rx="8"')+lines(x+15,y+165,w-30,3,'#a4afa8',14)
tr['motion-interface']+=path('M204 205h27m-9-9 9 9-9 9M409 205h27m-9-9 9 9-9 9',stroke='#597567',width=4)+label('STATE 01 → TRANSITION → STATE 02')
tr['surreal-play']=base('#b7d8d5')+rect(0,350,640,130,'#d5b792')+path('M125 350Q200 190 270 350Z','#709681','none')+circle(450,115,57,'#f1dca0')+group(rect(226,100,175,130,'#e68c89','rx="20"')+path('M401 118q90 0 0 86',stroke='#e68c89',width=28)+path('M254 230l-25 80M371 230l25 80',stroke='#424f5a',width=12)+circle(229,319,15,'#424f5a')+circle(396,319,15,'#424f5a'),'rotate(-12 320 220)')+label('ORDINARY OBJECT / IMPOSSIBLE SCENE')
tr['local-culture']=base('#e6d0a9')+rect(55,50,530,365,'#b64f39')+rect(90,87,460,245,'#f0deb1')+text(320,184,'동네',84,'#274c48',family='sans-serif',extra='text-anchor="middle" font-weight="700"')+text(320,253,'LOCAL MARKET',30,'#274c48',extra='text-anchor="middle"')+''.join(path(f'M{x} 350l18-18 18 18-18 18Z','#ebc974','none') for x in range(90,540,52))+label('A PLACE / A LANGUAGE / A COMMUNITY')
tr['cinematic']=base('#251d2b')+path('M320 35L90 405H550Z','#b39572','none',extra='opacity=".35"')+''.join(rect(x,0,30,480,'#4c2638','rx="12"') for x in list(range(0,120,27))+list(range(520,640,27)))+circle(320,274,30,'#11131a')+path('M281 400L291 315Q320 290 349 315L360 400Z','#11131a','none')+text(320,111,'ONE NIGHT',44,'#eddfc1','Georgia,serif','text-anchor="middle"')+text(320,155,'A STORY IN LIGHT',16,'#eddfc1',extra='text-anchor="middle" letter-spacing="3"')
tr['connection']=base('#f0ddc5')+circle(223,150,43,'#bd805b')+circle(431,150,43,'#78503d')+path('M163 365L169 230Q223 183 270 230L293 365Z','#758b70','none')+path('M365 365L384 230Q431 183 475 230L496 365Z','#ca795c','none')+rect(102,322,440,30,'#ad7d54','rx="9"')+rect(270,281,40,42,'#f7edcb','rx="5"')+rect(337,281,40,42,'#f7edcb','rx="5"')+path('M272 254q-12-15 0-30M350 254q12-15 0-30',stroke='#b09d83',width=3)+label('SHARED RITUALS / HUMAN CONNECTION')
tr['interface-play']=base('#d1c8e7')+rect(55,50,530,370,'#f2f0e8','stroke="#37334c" stroke-width="3"')+rect(55,50,530,50,'#c6e2bd','stroke="#37334c" stroke-width="3"')+text(75,83,'IDEA_LAB.EXE',22,family='monospace')+text(83,155,'> make something playful',22,family='monospace')+rect(85,187,265,178,'white','stroke="#777" stroke-width="1"')+''.join(path(f'M85 {y}H350',stroke='#c5c5c5',width=1) for y in range(217,365,30))+''.join(path(f'M{x} 187V365',stroke='#c5c5c5',width=1) for x in range(135,350,50))+circle(458,240,68,'#edb568')+text(422,261,':)',53,family='monospace')+path('M379 309L405 391L423 367L451 366Z','#62508c','white',3)
for slug,body in tr.items(): save(slug,slug.replace('-',' ').title(),body,T)
print(f'{len(tr)} trend illustrations drawn.')
