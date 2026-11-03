"""Original 64x64 skins for Bin, Bo, Zu + face variants (front face only changes)."""
from PIL import Image
import sys, os
OUT=sys.argv[1]
def rect(px,x,y,w,h,c):
    for i in range(x,x+w):
        for j in range(y,y+h): px[i,j]=c
def shade(c,f): return tuple(max(0,min(255,int(v*f))) for v in c[:3])+(255,)
def base(skin,hair,shirt,pants,shoes,shirt2=None):
    im=Image.new('RGBA',(64,64),(0,0,0,0)); p=im.load()
    # head faces (x,y of 8x8 squares)
    for (x,y,f) in [(8,0,1.1),(16,0,.9),(0,8,.92),(8,8,1),(16,8,.92),(24,8,.85)]:
        rect(p,x,y,8,8,shade(skin,f))
    # hair: top full, top 2 rows on sides/front, back mostly hair
    rect(p,8,0,8,8,hair); rect(p,24,8,8,7,hair)
    for x in (0,16): rect(p,x,8,8,3,hair); rect(p,x+ (0 if x==0 else 6),11,2,2,hair)
    rect(p,8,8,8,2,hair); p[8,10]=hair; p[15,10]=hair
    # body
    for (x,y,w,h,f) in [(20,16,8,4,1.1),(28,16,8,4,.8),(16,20,4,12,.9),(20,20,8,12,1),(28,20,4,12,.9),(32,20,8,12,.85)]:
        rect(p,x,y,w,h,shade(shirt,f))
    if shirt2: rect(p,22,24,4,4,shirt2)   # chest badge (original emblem)
    rect(p,20,30,8,2,shade(pants,.8))       # belt line
    # arms: sleeve top 4 rows shirt, rest skin
    for ox,oy in ((40,16),(32,48)):
        rect(p,ox+4,oy,4,4,shade(shirt,1.1)); rect(p,ox+8,oy,4,4,shade(skin,.9))
        rect(p,ox,oy+4,16,12,shade(skin,.95)); rect(p,ox,oy+4,16,4,shade(shirt,1))
    # legs
    for ox,oy in ((0,16),(16,48)):
        rect(p,ox+4,oy,4,4,shade(pants,1.1)); rect(p,ox+8,oy,4,4,shade(shoes,1))
        rect(p,ox,oy+4,16,12,shade(pants,.95)); rect(p,ox,oy+13,16,3,shoes)
    return im
W=(255,255,255,255); K=(30,24,24,255); M=(120,30,40,255); T=(90,170,255,255)
def face(im,skin,eye,kind):
    p=im.load(); X,Y=8,8; s=lambda f:shade(skin,f)
    rect(p,X,Y+2,8,6,skin+(255,) if len(skin)==3 else skin)
    def eyes_open():
        rect(p,X+1,Y+4,2,1,W); rect(p,X+5,Y+4,2,1,W)
        p[X+2,Y+4]=eye; p[X+5,Y+4]=eye
        rect(p,X+1,Y+3,2,1,s(.7)); rect(p,X+5,Y+3,2,1,s(.7))
    def eyes_closed(): rect(p,X+1,Y+4,2,1,s(.55)); rect(p,X+5,Y+4,2,1,s(.55))
    def eyes_happy():
        rect(p,X+1,Y+3,2,1,K); rect(p,X+5,Y+3,2,1,K); p[X+1,Y+5]=(240,120,120,255); p[X+6,Y+5]=(240,120,120,255)
    def eyes_sad():
        eyes_open(); p[X+1,Y+3]=s(.5); p[X+6,Y+3]=s(.5); p[X+2,Y+2]=s(.6); p[X+5,Y+2]=s(.6)
    def eyes_wide(): rect(p,X+1,Y+3,2,2,W); rect(p,X+5,Y+3,2,2,W); p[X+2,Y+4]=eye; p[X+5,Y+4]=eye
    mouths={
     'small':lambda:rect(p,X+3,Y+6,2,1,s(.55)),
     'open':lambda:(rect(p,X+3,Y+5,2,2,M),rect(p,X+2,Y+6,4,1,M)),
     'smile':lambda:(rect(p,X+3,Y+6,2,1,K),p.__setitem__((X+2,Y+5),K),p.__setitem__((X+5,Y+5),K)),
     'grin':lambda:(rect(p,X+2,Y+5,4,2,M),rect(p,X+2,Y+5,4,1,W)),
     'frown':lambda:(rect(p,X+3,Y+6,2,1,K),p.__setitem__((X+2,Y+7),K),p.__setitem__((X+5,Y+7),K)),
     'wail':lambda:(rect(p,X+2,Y+6,4,2,M),rect(p,X+3,Y+5,2,1,M)),
     'oh':lambda:rect(p,X+3,Y+5,2,2,M)}
    e,m,tears=kind
    {'open':eyes_open,'closed':eyes_closed,'happy':eyes_happy,'sad':eyes_sad,'wide':eyes_wide}[e]()
    mouths[m]()
    if tears: p[X+1,Y+5]=T; p[X+1,Y+6]=T; p[X+6,Y+5]=T; p[X+6,Y+6]=T; p[X+6,Y+7]=T
    return im
CH={
 'bin':dict(skin=(244,196,160),hair=(214,110,40,255),shirt=(250,196,40,255),pants=(92,64,44,255),shoes=(60,60,64,255),shirt2=(230,80,40,255),eye=(40,110,60,255)),
 'bo':dict(skin=(196,140,100),hair=(36,30,34,255),shirt=(70,170,90,255),pants=(40,56,110,255),shoes=(240,240,240,255),shirt2=(250,250,250,255),eye=(70,45,30,255)),
 'zu':dict(skin=(140,206,120),hair=(96,150,84,255),shirt=(240,140,60,255),pants=(120,80,50,255),shoes=(84,120,70,255),shirt2=(120,90,200,255),eye=(30,30,30,255)),
}
FACES={'neutral':('open','small',0),'talk':('open','open',0),'blink':('closed','small',0),
       'happy':('happy','smile',0),'happytalk':('happy','grin',0),'wow':('wide','oh',0),
       'sad':('sad','frown',0),'sadtalk':('sad','wail',0),'cry':('closed','wail',1),'crytalk':('sad','wail',1)}
os.makedirs(OUT,exist_ok=True)
for n,c in CH.items():
    for fname,k in FACES.items():
        im=base(c['skin']+(255,),c['hair'],c['shirt'],c['pants'],c['shoes'],c['shirt2'])
        face(im,c['skin'],c['eye'],k).save(f'{OUT}/{n}_{fname}.png')
print('SKINS_OK', len(os.listdir(OUT)))
