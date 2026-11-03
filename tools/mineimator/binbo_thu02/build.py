"""Mine-imator 2.0.2 .miproject, test scene 02: faceless skins + a code-built face rig (textured surfaces on the head:
eyes / pupils / brows / mouth on separate channels), loudness-graded lip-sync, blinks, idle breathing, 6 camera shots.
Techniques from reports/research/mineimator_study (groups B, C, D)."""
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
# ---- resources: one faceless skin per character + face-part textures (type 'texture')
res=[]; RID={}
for n in ('bin','bo','zu'):
    i=nid(); RID[n+'_skin']=i
    res.append({'id':i,'type':'skin','filename':f'skins/{n}_faceless.png','player_skin':True,'material_format':0})
for f in sorted(os.listdir('proj/face')):
    k=f[:-4]; i=nid(); RID[k]=i
    res.append({'id':i,'type':'texture','filename':'face/'+f,'material_format':0})
# ---- templates (human, wide), model_tex = faceless skin; one surface template for the face layers
steve_t=[t for t in d['templates'] if t['model']['name']=='human'][0]
temps=[]; TID={}
for n in ('bin','bo','zu'):
    t=copy.deepcopy(steve_t); t['id']=nid(); t['model_tex']=RID[n+'_skin']; t['name']=n.capitalize(); temps.append(t); TID[n]=t['id']
SURF_T={'id':nid(),'type':'surface','name':'face layer','shape':{'tex':RID['bin_eyes_open'],'tex_mapped':False,'tex_hoffset':0,'tex_voffset':0,'tex_hrepeat':1,'tex_vrepeat':1,'tex_hmirror':False,'tex_vmirror':False,'closed':True,'invert':False,'detail':32,'face_camera':False}}
temps.append(SURF_T)
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
    # face rig: 4 textured surfaces parented to the head, in front of the face plane (head-local +Y = forward, origin at head centre: measured)
    base=copy.deepcopy(steve); [base.pop(k,None) for k in ('parts',)]
    for li,(layer,dy) in enumerate((('eyes',4.02),('pupils',4.035),('brows',4.045),('mouth',4.025))):
        s_=copy.deepcopy(base); s_.update(id=nid(),type='surface',name=f'{n}_{layer}',temp=SURF_T['id'],keyframes={},parent=P[n]['head']['id'],parent_tree_index=li+1,shadows=False,ssao=False)
        s_['inherit']=dict(s_['inherit'],texture=False,alpha=True,visibility=True,scale=True,position=True,rotation=True)
        new.append(s_); P[n][layer]=s_; P[n][layer+'_y']=dy
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
# Conventions (measured on renders): facing(ROT_Z=t)=(sin t, cos t); +ROT_X tips a part's top forward,
# so a hanging arm/leg swings BACK with +ROT_X (raise arm forward = negative), head +ROT_X looks down.
# Zu sits at origin facing camera (-Y), scale 0.6, big head
K(Z['char'],0,'linear',POS_X=0,POS_Y=0,POS_Z=-6,ROT_Z=180,SCA_X=.6,SCA_Y=.6,SCA_Z=.6)
K(Z['head'],0,'linear',SCA_X=1.25,SCA_Y=1.25,SCA_Z=1.25,ROT_X=18)
for leg in ('right_leg','left_leg'): K(Z[leg],0,'linear',ROT_X=-90)
for arm,s in (('right_arm',1),('left_arm',-1)): K(Z[arm],0,'linear',ROT_X=-35,ROT_Z=8*s)
# sobbing shoulders 0..240
for f in range(12,296,12): K(Z['char'],f,'easeinoutsine',POS_Z=-5.4 if (f//12)%2 else -6)
# Bin & Bo walk in from +X (screen-left) to stops, facing -X (ROT_Z 90)
for ch,x0,x1,y,off in ((B,120,30,-8,0),(O,150,58,6,3)):
    # [B: NU0fAvOgEv0 13:09, BmWf6dR4kks 3:22] legs linear, travel linear, swing sized to the stride (no foot slide)
    K(ch['char'],0,'linear',POS_X=x0,POS_Y=y,ROT_Z=-90)
    K(ch['char'],72,'easeoutquad',POS_X=x1+5,POS_Y=y,ROT_Z=-90)
    K(ch['char'],82,'easeoutquad',POS_X=x1,POS_Y=y,ROT_Z=-90)
    for i,f in enumerate(range(0+off,78,6)):
        a=16 if i%2 else -16
        K(ch['right_leg'],f,'linear',ROT_X=a); K(ch['left_leg'],f,'linear',ROT_X=-a)
        K(ch['right_arm'],f,'easeinoutsine',ROT_X=-a*1.2); K(ch['left_arm'],f,'easeinoutsine',ROT_X=a*1.2)
        K(ch['body'],f,'easeinoutsine',ROT_Z=3 if i%2 else -3)
    for part in ('right_leg','left_leg','right_arm','left_arm'): K(ch[part],84,'easeoutquad',ROT_X=0)
# Bin: "Huh? Bo, look!" turn toward camera side then point at Zu
K(B['char'],84,'easeinoutquad',ROT_Z=-90); K(B['char'],96,'easeoutback',ROT_Z=-120)
K(B['head'],84,'easeoutquad',ROT_Y=0); K(B['head'],92,'easeoutback',ROT_X=-5)
K(B['right_arm'],96,'easeoutback',ROT_X=0); K(B['right_arm'],106,'easeoutquad',ROT_X=-95,ROT_Z=-10)
K(B['char'],132,'easeinoutquad',ROT_Z=-120); K(B['char'],142,'easeinoutquad',ROT_Z=-90)
K(B['right_arm'],128,'easeinoutquad',ROT_X=-95,ROT_Z=-10); K(B['right_arm'],140,'easeinoutquad',ROT_X=0,ROT_Z=0)
K(B['head'],130,'easeinoutquad',ROT_X=-5); K(B['head'],140,'easeinoutquad',ROT_X=8)
# Bo: kneel-ish lean + reach hand "Are you okay?"
K(O['char'],140,'easeinoutquad',POS_X=58,POS_Z=0); K(O['char'],152,'easeoutquad',POS_X=44,POS_Z=-3)
K(O['head'],140,'easeinoutquad',ROT_X=0); K(O['head'],150,'easeoutquad',ROT_X=14)
K(O['left_arm'],140,'easeinoutquad',ROT_X=0); K(O['left_arm'],154,'easeoutback',ROT_X=-60)
K(O['left_arm'],196,'easeinoutquad',ROT_X=-60); K(O['left_arm'],208,'easeinoutquad',ROT_X=0)
# Zu looks up at Bo when spoken to, then down while answering
K(Z['head'],150,'easeinoutquad',ROT_X=18); K(Z['head'],162,'easeoutquad',ROT_X=-8,ROT_Z=-15)
K(Z['head'],204,'easeinoutquad',ROT_X=-8,ROT_Z=-15); K(Z['head'],214,'easeinoutquad',ROT_X=12,ROT_Z=0)
# Bin: "Don't cry! We'll help you!" fist pump
K(B['right_arm'],258,'easeinoutquad',ROT_X=0); K(B['right_arm'],266,'easeoutback',ROT_X=-150)
K(B['right_arm'],286,'easeoutback',ROT_X=-150); K(B['right_arm'],298,'easeinoutquad',ROT_X=0)
K(B['head'],262,'easeoutquad',ROT_X=0)
# Zu stands up and hops (Really? Yaaay!)
K(Z['char'],300,'easeoutback',POS_Z=-6); K(Z['char'],312,'easeoutquad',POS_Z=0)
for leg in ('right_leg','left_leg'): K(Z[leg],300,'easeoutback',ROT_X=-90); K(Z[leg],312,'easeoutquad',ROT_X=0)
K(Z['head'],300,'easeoutquad',ROT_X=12); K(Z['head'],312,'easeoutquad',ROT_X=-6)
for arm,s in (('right_arm',1),('left_arm',-1)):
    K(Z[arm],300,'easeinoutquad',ROT_X=-35,ROT_Z=8*s); K(Z[arm],314,'easeoutback',ROT_X=-165,ROT_Z=25*s)
hop=[(324,0),(331,9),(338,0),(345,9),(352,0),(359,9),(366,0)]
for f,z in hop: K(Z['char'],f,'easeoutquad' if z else 'easeinquad',POS_Z=z)
# Bo + Bin cheer, then "Group hug!" step in
for ch in (B,O):
    for arm,s in (('right_arm',1),('left_arm',-1)):
        K(ch[arm],330,'easeinoutquad',ROT_X=0); K(ch[arm],340,'easeoutback',ROT_X=-150,ROT_Z=20*s)
        K(ch[arm],372,'easeinoutquad',ROT_X=-150,ROT_Z=20*s); K(ch[arm],384,'easeoutquad',ROT_X=-80,ROT_Z=0)
K(O['char'],340,'easeinoutquad',POS_X=44,POS_Z=-3); K(O['char'],350,'easeoutquad',POS_X=48,POS_Z=0)
K(B['char'],370,'easeinoutquad',POS_X=30,POS_Y=-8,ROT_Z=-90); K(B['char'],386,'easeoutquad',POS_X=16,POS_Y=-6,ROT_Z=-90)
K(O['char'],370,'easeinoutquad',POS_X=48,POS_Y=6); K(O['char'],386,'easeoutquad',POS_X=20,POS_Y=9)
# ================= FACE RIG (instant keys; eye darts and texture swaps are discrete) =================
# expression = (eyes texture, brows texture, silent mouth, pupil size, gaze (dx,dz) in head px)
EXPR={'neutral':('open','neutral','rest','normal',(0,0)),'notice':('wide','raised','oh','small',(0,0)),
      'curious':('open','curious','rest','normal',(0,0)),'worried':('open','worried','rest','big',(0,0)),
      'cry':('cry','sad','frown','big',(0,-.3)),'sad':('sad','sad','frown','big',(0,-.4)),'sad_up':('sad','worried','frown','big',(.2,.45)),
      'surprised':('wide','raised','oh','small',(0,0)),'happy':('happy','raised','smile','normal',(0,0)),
      'cheer':('open','raised','smile','normal',(0,0)),'determined':('open','angry','smile','normal',(0,0))}
TALK={'rest':'open','oh':'open','smile':'grin','frown':'wail'}
FX={n:{} for n in ('bin','bo','zu')}          # frame -> dict(eyes,brows,mouth,psize,gaze)
CUR={}
def expr(n,f,e):
    E=EXPR[e]; FX[n].setdefault(f,{}).update(eyes=E[0],brows=E[1],mouth=E[2],psize=E[3],gaze=E[4],expr=e)
expr('zu',0,'cry'); expr('bin',0,'neutral'); expr('bo',0,'neutral')
expr('bin',64,'notice'); expr('bo',68,'notice'); expr('bin',84,'curious'); expr('bo',100,'curious')
expr('bo',140,'worried'); expr('zu',150,'sad_up'); expr('zu',214,'sad'); expr('bo',196,'neutral')
expr('bin',250,'neutral'); expr('bin',262,'determined'); expr('zu',290,'surprised'); expr('zu',304,'happy')
expr('bin',296,'cheer'); expr('bo',300,'happy'); expr('bin',330,'happy')
def state_at(n,f):
    st={}
    for k in sorted(FX[n]):
        if k<=f: st.update(FX[n][k])
    return st
def set_fx(n,f,**v): FX[n].setdefault(f,{}).update(v)
# lip-sync [C: jGvOjgVfN_A 3:19, 10:37, 12:04, 12:15]: key the loudness peaks, openness graded by volume, no close between open sounds
def talk(n,lid):
    s=START[lid]; env=ENV[lid]; mx=max(env) or 1; last=None
    for k in range(0,len(env),3):
        v=max(env[k:k+3])/mx
        lvl=0 if v<.12 else 1 if v<.38 else 2 if v<.7 else 3
        base=state_at(n,s+k).get('mouth','rest'); fam=TALK.get(base,'open')
        m=base if lvl==0 else f'{fam}{lvl}'
        if m!=last: set_fx(n,s+k,mouth=m); last=m
    set_fx(n,s+len(env)+2,mouth=state_at(n,s).get('mouth','rest'))
SPEAK={'zu1':'zu','bin1':'bin','bo1':'bo','zu2':'zu','bin2':'bin','zu3':'zu','bo2':'bo'}
for lid,n in SPEAK.items(): talk(n,lid)
# blinks: one just before each line [C: QRwM5E7NVaA 7:21] + every ~3 s, 4-frame half/closed/half
def blink(n,f0):
    st=state_at(n,f0)
    if st.get('eyes') not in ('open','sad','wide'): return
    e=st['eyes']; set_fx(n,f0,eyes='half'); set_fx(n,f0+1,eyes='closed'); set_fx(n,f0+3,eyes='half'); set_fx(n,f0+4,eyes=e)
for lid,n in SPEAK.items(): blink(n,START[lid]-6)
for n,off in (('bin',30),('bo',52),('zu',75)):
    f=off
    while f<END-8:
        if all(abs(f-k)>8 for k in FX[n] if k!=0): blink(n,f)
        f+=64+random.randint(-10,14)
# write face keys
for n in FX:
    ch=P[n]; st={}
    for f in sorted(FX[n]):
        st.update(FX[n][f])
        closed=st['eyes'] in ('closed','happy')
        gx,gz=st.get('gaze',(0,0))
        K(ch['eyes'],f,'instant',TEXTURE_OBJ=RID[f"{n}_eyes_{st['eyes']}"],POS_Y=ch['eyes_y'],POS_Z=0,SCA_X=.5,SCA_Y=.5,SCA_Z=.5)
        K(ch['pupils'],f,'instant',TEXTURE_OBJ=RID[f"{n}_pupils_{st['psize']}"],POS_X=gx,POS_Y=(3.0 if closed else ch['pupils_y']),POS_Z=gz+(-0.3 if st['eyes']=='half' else 0),SCA_X=.5,SCA_Y=.5,SCA_Z=.5)
        K(ch['brows'],f,'instant',TEXTURE_OBJ=RID[f"{n}_brows_{st['brows']}"],POS_Y=ch['brows_y'],POS_Z=0,SCA_X=.5,SCA_Y=.5,SCA_Z=.5)
        K(ch['mouth'],f,'instant',TEXTURE_OBJ=RID[f"{n}_mouth_{st['mouth']}"],POS_Y=ch['mouth_y'],POS_Z=0,SCA_X=.5,SCA_Y=.5,SCA_Z=.5)
# idle breathing on the body part for everyone, every frame alive [B: aMTNQBzSGA8 1:36, C: QRwM5E7NVaA 5:37]
for n,ph in (('bin',0),('bo',11),('zu',5)):
    body=P[n]['body']
    for f in range(84+ph if n!='zu' else ph,END,24):
        K(body,f,'easeinoutsine',ROT_X=1.5 if (f//24)%2 else -0.5, ROT_Z=0)
# ================= CAMERA (hard cuts) =================
def look(px,py,pz,tx,ty,tz):
    dx,dy,dz=tx-px,ty-py,tz-pz
    rz=math.degrees(math.atan2(dx,dy))   # camera: +ROT_Z turns the view toward +X (characters use the opposite)
    rx=-math.degrees(math.atan2(dz,math.hypot(dx,dy)))  # camera: +ROT_X tilts the view down
    return dict(POS_X=round(px,2),POS_Y=round(py,2),POS_Z=round(pz,2),ROT_X=round(rx,2),ROT_Z=round(rz,2))
SH=[ # start,end,(cam start),(cam end),fov
 (0,83,(60,-175,34,40,0,14),(52,-150,30,36,0,14),44),        # S1 wide establishing
 (84,139,(8,-46,30,30,-8,27),(10,-42,30,30,-8,27),34),          # S2 Bin medium
 (140,205,(18,26,24,44,4,21),(21,23,23,44,4,20),34),         # S3 Bo talks to Zu (camera on +Y side so Bin is out of line)
 (206,261,(-5,-36,13,-5,0,12),(-5,-31,13,-5,0,12),28),             # S4 Zu close-up
 (262,305,(6,-44,29,30,-8,27),(9,-40,29,30,-8,27),34),         # S5 Bin cheer
 (306,END,(24,-120,26,20,0,14),(20,-96,24,18,0,14),44)]        # S6 wide celebration
for s,e,a,b,fov in SH:
    K(cam,s,'easeinoutsine',CAM_FOV=fov,**look(*a)); K(cam,e,'instant',CAM_FOV=fov,**look(*b))
flush()
cam['keyframes'].pop(str(END),None); K(cam,END,'linear',CAM_FOV=44,**look(20,-96,24,18,0,14)); flush()
# ---- assemble
cam['parent_tree_index']=0
for i,n in enumerate(('bin','bo','zu')): P[n]['char']['parent_tree_index']=i+1
d['templates']=temps; d['resources']=res; d['timelines']=[cam]+new
pr=d['project']; pr['name']='BinBo MI thu 02'; pr['video_width']=1920; pr['video_height']=1080; pr['tempo']=FPS
pr['timeline']['marker']=0; pr['timeline']['zoom']=3.5; pr['timeline']['hor_scroll']=0; pr['timeline']['region_start']=0; pr['timeline']['region_end']=END
json.dump(d,open('proj/BinBo MI thu 02.miproject','w'),indent=1)
n=sum(len(t['keyframes']) for t in d['timelines'])
print('MIPROJECT_OK::timelines=%d::keyframes=%d::frames=%d::resources=%d'%(len(d['timelines']),n,END,len(res)))
json.dump({'start':START,'end':END,'fps':FPS},open('proj/timing.json','w'))
