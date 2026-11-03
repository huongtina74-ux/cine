"""Generate a Mine-imator 2.0.2 .miproject: Bin, Bo, Zu scene with face swaps, walk, gestures, 6 camera shots."""
import json, math, random, copy, sys, os
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(sys.argv[1] if len(sys.argv)>1 else HERE)
random.seed(7)
SRC=os.path.join(HERE,'template.miproject')
d=json.load(open(SRC)); L=json.load(open('vo/lines.json' if os.path.exists('vo/lines.json') else os.path.join(HERE,'lines.json')))
FPS=24
def nid(): return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16))
# ---- timing (frames), audio-first
START={'zu1':12,'bin1':84,'bo1':140,'zu2':206,'bin2':262,'zu3':306,'bo2':356}
LEN={l['id']:int(math.ceil(l['dur']*FPS)) for l in L}
ENV={l['id']:l['env'] for l in L}
END=408
# ---- resources: one skin resource per face png
res=[]; RID={}
import os
for f in sorted(os.listdir('proj/skins')):
    k=f[:-4]; i=nid(); RID[k]=i
    res.append({'id':i,'type':'skin','filename':'skins/'+f,'player_skin':True,'material_format':0})
# ---- templates (human, wide), model_tex = neutral skin
steve_t=[t for t in d['templates'] if t['model']['name']=='human'][0]
temps=[]; TID={}
for n in ('bin','bo','zu'):
    t=copy.deepcopy(steve_t); t['id']=nid(); t['model_tex']=RID[n+'_neutral']; t['name']=n.capitalize(); temps.append(t); TID[n]=t['id']
# ---- timelines: clone Steve char + parts
tls=d['timelines']; steve=[t for t in tls if t.get('name')=='Steve'][0]
parts={t['id']:t for t in tls if t.get('part_of')==steve['id']}
cam=copy.deepcopy([t for t in tls if t['type']=='camera'][0])
new=[]; P={}
for n in ('bin','bo','zu'):
    c=copy.deepcopy(steve); c['id']=nid(); c['name']=n.capitalize(); c['temp']=TID[n]; c['keyframes']={}
    m={}
    for pid in steve['parts']: m[pid]=nid()
    c['parts']=[m[p] for p in steve['parts']]
    new.append(c); P[n]={'char':c}
    for pid in steve['parts']:
        b=copy.deepcopy(parts[pid]); b['id']=m[pid]; b['temp']=TID[n]; b['part_of']=c['id']; b['keyframes']={}
        b['parent']=m.get(b['parent'],c['id']) if b['parent']!=steve['id'] else c['id']
        new.append(b); P[n][b['model_part_name']]=b
# ---- keyframe helper: events per timeline, carried forward (Mine-imator stores only non-default values per keyframe)
EV={}
def K(tl,f,tr='easeinoutquad',**v):
    EV.setdefault(tl['id'],(tl,{}))[1].setdefault(int(f),[{},tr])
    e=EV[tl['id']][1][int(f)]; e[0].update(v); e[1]=tr
def flush():
    for tid,(tl,ev) in EV.items():
        state={}; out={}
        for f in sorted(ev):
            vals,tr=ev[f]; state.update(vals)
            kf={k:v for k,v in state.items() if v not in (0,None)}
            kf['TRANSITION']=tr; out[str(f)]=kf
        tl['keyframes']=out
# ================= BLOCKING =================
B,O,Z=P['bin'],P['bo'],P['zu']
# Zu sits at origin facing camera (-Y), scale 0.6, big head
K(Z['char'],0,'linear',POS_X=0,POS_Y=0,POS_Z=-6,ROT_Z=180,SCA_X=.6,SCA_Y=.6,SCA_Z=.6)
K(Z['head'],0,'linear',SCA_X=1.25,SCA_Y=1.25,SCA_Z=1.25,ROT_X=18)
for leg in ('right_leg','left_leg'): K(Z[leg],0,'linear',ROT_X=90)
for arm,s in (('right_arm',1),('left_arm',-1)): K(Z[arm],0,'linear',ROT_X=40,BEND_ANGLE_X=70,ROT_Z=8*s)
# sobbing shoulders 0..240
for f in range(12,296,12): K(Z['char'],f,'easeinoutsine',POS_Z=-5.4 if (f//12)%2 else -6)
# Bin & Bo walk in from +X (screen-left) to stops, facing -X (ROT_Z 90)
for ch,x0,x1,y,off in ((B,120,30,-8,0),(O,150,58,6,3)):
    K(ch['char'],0,'linear',POS_X=x0,POS_Y=y,ROT_Z=90)
    K(ch['char'],80,'easeoutquad',POS_X=x1,POS_Y=y,ROT_Z=90)
    for i,f in enumerate(range(0+off,80,6)):
        a=30 if i%2 else -30
        K(ch['right_leg'],f,'easeinoutsine',ROT_X=a); K(ch['left_leg'],f,'easeinoutsine',ROT_X=-a)
        K(ch['right_arm'],f,'easeinoutsine',ROT_X=-a); K(ch['left_arm'],f,'easeinoutsine',ROT_X=a)
    for part in ('right_leg','left_leg','right_arm','left_arm'): K(ch[part],84,'easeoutquad',ROT_X=0)
# Bin: "Huh? Bo, look!" turn toward camera side then point at Zu
K(B['char'],84,'easeinoutquad',ROT_Z=90); K(B['char'],96,'easeoutback',ROT_Z=120)
K(B['head'],84,'easeoutquad',ROT_Y=0); K(B['head'],92,'easeoutback',ROT_X=-10)
K(B['right_arm'],96,'easeoutback',ROT_X=0); K(B['right_arm'],106,'easeoutquad',ROT_X=95,ROT_Z=-10)
K(B['char'],132,'easeinoutquad',ROT_Z=120); K(B['char'],142,'easeinoutquad',ROT_Z=90)
K(B['right_arm'],128,'easeinoutquad',ROT_X=95,ROT_Z=-10); K(B['right_arm'],140,'easeinoutquad',ROT_X=0,ROT_Z=0)
K(B['head'],130,'easeinoutquad',ROT_X=-10); K(B['head'],140,'easeinoutquad',ROT_X=8)
# Bo: kneel-ish lean + reach hand "Are you okay?"
K(O['char'],140,'easeinoutquad',POS_X=58,POS_Z=0); K(O['char'],152,'easeoutquad',POS_X=44,POS_Z=-3)
K(O['head'],140,'easeinoutquad',ROT_X=0); K(O['head'],150,'easeoutquad',ROT_X=14)
K(O['left_arm'],140,'easeinoutquad',ROT_X=0); K(O['left_arm'],154,'easeoutback',ROT_X=60,BEND_ANGLE_X=20)
K(O['left_arm'],196,'easeinoutquad',ROT_X=60,BEND_ANGLE_X=20); K(O['left_arm'],208,'easeinoutquad',ROT_X=0,BEND_ANGLE_X=0)
# Zu looks up at Bo when spoken to, then down while answering
K(Z['head'],150,'easeinoutquad',ROT_X=18); K(Z['head'],162,'easeoutquad',ROT_X=-8,ROT_Z=-15)
K(Z['head'],204,'easeinoutquad',ROT_X=-8,ROT_Z=-15); K(Z['head'],214,'easeinoutquad',ROT_X=12,ROT_Z=0)
# Bin: "Don't cry! We'll help you!" fist pump
K(B['right_arm'],258,'easeinoutquad',ROT_X=0); K(B['right_arm'],266,'easeoutback',ROT_X=150,BEND_ANGLE_X=40)
K(B['right_arm'],286,'easeoutback',ROT_X=150,BEND_ANGLE_X=40); K(B['right_arm'],298,'easeinoutquad',ROT_X=0,BEND_ANGLE_X=0)
K(B['head'],262,'easeoutquad',ROT_X=0)
# Zu stands up and hops (Really? Yaaay!)
K(Z['char'],300,'easeoutback',POS_Z=-6); K(Z['char'],312,'easeoutquad',POS_Z=0)
for leg in ('right_leg','left_leg'): K(Z[leg],300,'easeoutback',ROT_X=90); K(Z[leg],312,'easeoutquad',ROT_X=0)
K(Z['head'],300,'easeoutquad',ROT_X=12); K(Z['head'],312,'easeoutquad',ROT_X=-6)
for arm,s in (('right_arm',1),('left_arm',-1)):
    K(Z[arm],300,'easeinoutquad',ROT_X=40,BEND_ANGLE_X=70,ROT_Z=8*s); K(Z[arm],314,'easeoutback',ROT_X=165,BEND_ANGLE_X=0,ROT_Z=25*s)
hop=[(324,0),(331,9),(338,0),(345,9),(352,0),(359,9),(366,0)]
for f,z in hop: K(Z['char'],f,'easeoutquad' if z else 'easeinquad',POS_Z=z)
# Bo + Bin cheer, then "Group hug!" step in
for ch in (B,O):
    for arm,s in (('right_arm',1),('left_arm',-1)):
        K(ch[arm],330,'easeinoutquad',ROT_X=0); K(ch[arm],340,'easeoutback',ROT_X=150,ROT_Z=20*s)
        K(ch[arm],372,'easeinoutquad',ROT_X=150,ROT_Z=20*s); K(ch[arm],384,'easeoutquad',ROT_X=80,ROT_Z=0)
K(O['char'],340,'easeinoutquad',POS_X=44,POS_Z=-3); K(O['char'],350,'easeoutquad',POS_X=48,POS_Z=0)
K(B['char'],370,'easeinoutquad',POS_X=30,POS_Y=-8,ROT_Z=90); K(B['char'],386,'easeoutquad',POS_X=16,POS_Y=-6,ROT_Z=90)
K(O['char'],370,'easeinoutquad',POS_X=48,POS_Y=6); K(O['char'],386,'easeoutquad',POS_X=20,POS_Y=9)
# ================= FACES (TEXTURE_OBJ on body; head/hat inherit) =================
FACE={n:{} for n in ('bin','bo','zu')}
def face(n,f,name): FACE[n][f]=name
face('zu',0,'cry'); face('bin',0,'neutral'); face('bo',0,'neutral')
face('bin',66,'wow'); face('bo',70,'wow')
face('zu',150,'sad'); face('zu',246,'sad'); face('zu',290,'wow'); face('zu',304,'happy')
face('bo',196,'neutral'); face('bin',250,'neutral'); face('bin',296,'happy'); face('bo',300,'happy')
def talk(n,lid,open_,closed):
    s=START[lid]; env=ENV[lid]; thr=max(env)*0.25; last=None
    for k in range(0,len(env),2):
        st=open_ if env[k]>thr else closed
        if st!=last: face(n,s+k,st); last=st
    face(n,s+len(env)+1,closed)
talk('zu','zu1','crytalk','cry'); talk('bin','bin1','talk','wow' if False else 'neutral'); talk('bo','bo1','talk','neutral')
talk('zu','zu2','sadtalk','sad'); talk('bin','bin2','happytalk','happy'); talk('zu','zu3','happytalk','happy'); talk('bo','bo2','happytalk','happy')
# blinks (only when face is a plain open-eye state)
for n,base_ok in (('bin',('neutral',)),('bo',('neutral',)),('zu',('sad',))):
    for f0 in range(40,END,70+random.randint(-12,12)):
        cur=max([f for f in FACE[n] if f<=f0],default=0); st=FACE[n][cur]
        nxt=min([f for f in FACE[n] if f>f0],default=10**6)
        if st in base_ok and nxt>f0+4: face(n,f0,'blink'); face(n,f0+3,st)
for n in FACE:
    for f,name in sorted(FACE[n].items()): K(P[n]['body'],f,'instant',TEXTURE_OBJ=RID[f'{n}_{name}'])
# Zu body sob ROT_X also lives on body -> merge happens in K() (same timeline, carried state)
# ================= CAMERA (hard cuts) =================
def look(px,py,pz,tx,ty,tz):
    dx,dy,dz=tx-px,ty-py,tz-pz
    rz=math.degrees(math.atan2(dx,dy))   # camera: +ROT_Z turns the view toward +X (characters use the opposite)
    rx=-math.degrees(math.atan2(dz,math.hypot(dx,dy)))  # camera: +ROT_X tilts the view down
    return dict(POS_X=round(px,2),POS_Y=round(py,2),POS_Z=round(pz,2),ROT_X=round(rx,2),ROT_Z=round(rz,2))
SH=[ # start,end,(cam start),(cam end),fov
 (0,83,(60,-175,34,40,0,14),(52,-150,30,36,0,14),50),        # S1 wide establishing
 (84,139,(8,-46,30,30,-8,27),(10,-42,30,30,-8,27),42),          # S2 Bin medium
 (140,205,(16,-36,26,48,6,22),(19,-32,25,46,6,21),44),         # S3 Bo talks to Zu
 (206,261,(0,-36,13,0,0,12),(0,-31,13,0,0,12),38),             # S4 Zu close-up
 (262,305,(6,-44,29,30,-8,27),(9,-40,29,30,-8,27),42),         # S5 Bin cheer
 (306,END,(24,-120,26,20,0,14),(20,-96,24,18,0,14),48)]        # S6 wide celebration
for s,e,a,b,fov in SH:
    K(cam,s,'easeinoutsine',CAM_FOV=fov,**look(*a)); K(cam,e,'instant',CAM_FOV=fov,**look(*b))
flush()
cam['keyframes'].pop(str(END),None); K(cam,END,'linear',CAM_FOV=48,**look(20,-96,24,18,0,14)); flush()
# ---- assemble
cam['parent_tree_index']=0
for i,n in enumerate(('bin','bo','zu')): P[n]['char']['parent_tree_index']=i+1
d['templates']=temps; d['resources']=res; d['timelines']=[cam]+new
pr=d['project']; pr['name']='BinBo MI thu 01'; pr['video_width']=1920; pr['video_height']=1080; pr['tempo']=FPS
pr['timeline']['marker']=0; pr['timeline']['zoom']=3.5; pr['timeline']['hor_scroll']=0; pr['timeline']['region_start']=0; pr['timeline']['region_end']=END
json.dump(d,open('proj/BinBo MI thu 01.miproject','w'),indent=1)
n=sum(len(t['keyframes']) for t in d['timelines'])
print('MIPROJECT_OK::timelines=%d::keyframes=%d::frames=%d::resources=%d'%(len(d['timelines']),n,END,len(res)))
json.dump({'start':START,'end':END,'fps':FPS},open('proj/timing.json','w'))
