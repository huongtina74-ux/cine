/* ===== blockfilm factory — generic "Who can …?" contest engine, driven by SPEC (see factory/README.md) =====
   Challenges: 'launch' (spring pads, height of the bounce) and 'pillar' (build a tower under your feet).
   Story template (proven on S01): A tries, B beats A, C flops, laugh, TWIST, result, loop.
   Twists: 'glow' (the flopper's secret power sends them off the scale) and 'backfire' (the leader gets greedy, the tower collapses, the steady one wins).
   Everything the audio needs is exported as CUES; every shot change as SEG. */
const CUES=[];const cue=(t,type,g=1)=>CUES.push({t:+t.toFixed(3),type,g});
const NAME={bin:'BIN',bo:'BO',zu:'ZU'};
const IDLE_EYES={};

/* ---------- lights, sky ---------- */
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
const hemi=new THREE.HemisphereLight(0xCFE8FF,0x5A6B3A,.78);scene.add(hemi);
const sun=new THREE.DirectionalLight(0xFFF2DA,.82);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
sun.shadow.bias=-.0006;sun.shadow.normalBias=.03;scene.add(sun);scene.add(sun.target);
function sunFollow(y){const yy=Math.max(0,y-8);sun.position.set(10,26+yy,18);sun.target.position.set(0,yy,-1);Object.assign(sun.shadow.camera,{left:-14,right:14,top:22,bottom:-6,near:1,far:90});sun.shadow.camera.updateProjectionMatrix()}
sunFollow(0);
(function(){const c=document.createElement('canvas');c.width=4;c.height=256;const g=c.getContext('2d');const gr=g.createLinearGradient(0,0,0,256);
  [[0,'#2F86E0'],[.55,'#7CC2F5'],[1,'#D7F0FF']].forEach(([o,col])=>gr.addColorStop(o,col));g.fillStyle=gr;g.fillRect(0,0,4,256);const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;scene.background=t})();
scene.fog=new THREE.Fog(0xCDEBFF,38,110);
ODD.root.visible=false;Object.keys(CH).forEach(n=>{if(!LANES.includes(n))CH[n].root.visible=false});

/* ---------- props ---------- */
const PAD={};if(CHALL=='launch')for(const n of LANES){const m=new THREE.Mesh(box1,MAT.pad);m.castShadow=true;m.receiveShadow=true;scene.add(m);PAD[n]=m}
// soft bales next to every lane (pillar): safety first, and the backfire lands in them
const BALE={};if(CHALL=='pillar')for(const n of LANES){const b=new THREE.Mesh(box1,MAT.bale);b.position.set(LX[n]+1.05,1,0);b.castShadow=true;b.receiveShadow=true;scene.add(b);BALE[n]=b}
// ruler numbers on the tower
for(let y=4;y<=RULER;y+=4){const c=document.createElement('canvas');c.width=c.height=128;const g=c.getContext('2d');
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;const pl=new THREE.Mesh(new THREE.PlaneGeometry(.9,.9),new THREE.MeshBasicMaterial({map:t,transparent:true}));pl.position.set(5,BASE+y,-1.48);scene.add(pl);
  pl.userData.draw=()=>{g.clearRect(0,0,128,128);g.font='800 92px Kid';g.textAlign='center';g.textBaseline='middle';g.lineWidth=14;g.strokeStyle='#000';g.strokeText(String(y),64,70);g.fillStyle='#FFE14D';g.fillText(String(y),64,70);t.needsUpdate=true};(window.NUMS=window.NUMS||[]).push(pl)}
const cloudM=new THREE.MeshLambertMaterial({color:0xFFFFFF,emissive:0xBFD9F0,emissiveIntensity:.35});
const CLOUD=pool(90,cloudM,1,false);{const r=rng(301);let i=0;for(let c=0;c<14;c++){const cx=r()*44-22,cz=-r()*22+4,cy=Math.max(23,RULER-3)+r()*6;const n=4+(r()*4|0);
  for(let k=0;k<n&&i<90;k++){e.set(0,0,0);q.setFromEuler(e);sc3.set(2+r()*3,1+r()*.6,2+r()*2.5);m4.compose(V3(cx+r()*4-2,cy+r()*.8,cz+r()*3-1.5),q,sc3);CLOUD.setMatrixAt(i++,m4)}}CLOUD.count=i;CLOUD.instanceMatrix.needsUpdate=true}
{const r=rng(302);for(let i=0;i<46;i++){const x=(r()*22-11)|0,z=(r()*14-9)|0;if(Math.abs(z)<2&&Math.abs(x)<5)continue;const m=r()<.5?MAT.flowerW:MAT.flowerP;
  for(const a of[0,Math.PI/2]){const pl=new THREE.Mesh(new THREE.PlaneGeometry(.45,.45),m);pl.position.set(x+.5*(r()-.5),.72,z+.5*(r()-.5));pl.rotation.y=a+.6;scene.add(pl)}}}
const crown=new THREE.Group();{[[0,0,0,.42,.1,.42],[-.16,.12,0,.08,.16,.08],[.16,.12,0,.08,.16,.08],[0,.15,.16,.08,.2,.08],[0,.12,-.16,.08,.16,.08]].forEach(([x,y,z,w,h,d])=>{const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),MAT.gold);b.position.set(x,y,z);b.castShadow=true;crown.add(b)})}
crown.visible=false;
const DUST=pool(64,new THREE.MeshLambertMaterial({color:0xE8E2D0}),.14,false);
const SPARK=pool(40,new THREE.MeshBasicMaterial({color:0xFFF59D}),.12,false);
const GLOW=pool(36,new THREE.MeshBasicMaterial({color:0x39FF14}),.12,false);
// tower blocks (pillar): one instanced pool per lane, each lane its own block
const TOWER_MAT={bin:MAT.plank,bo:MAT.cobble,zu:MAT.dirt};const TOWER={};
if(CHALL=='pillar')for(const n of LANES){const im=new THREE.InstancedMesh(box1,TOWER_MAT[n]||MAT.plank,80);im.castShadow=true;im.receiveShadow=true;im.count=0;scene.add(im);TOWER[n]=im}

/* ---------- timeline from SPEC ---------- */
const SEG=[];let T0=0;
function seg(type,dur,o={}){const s={type,t0:T0,t1:T0+dur,...o};SEG.push(s);T0+=dur;return s}
const MOVES={};LANES.forEach(n=>MOVES[n]=[]);   // what each character does over time
const SCORE={};LANES.forEach(n=>SCORE[n]=[]);   // [t, value] steps for the scoreboard
const att=SPEC.attempts;const twist=SPEC.twist||{type:'glow'};
const flightDur=s=>clamp(.5+.42*Math.sqrt(s),.5,2.3);
const buildPer=(a)=>a.style=='fast'?.1:(a.style=='slow'||a.style=='flop')?.36:.16;
function addAttempt(a,o={}){const n=a.who;
  if(CHALL=='launch'){
    const prep=.3;const st=seg('act',0,{who:n});const t0=st.t0+prep;let t=t0;
    if(a.style=='double'){MOVES[n].push({k:'jump',t0:t,d:.8,pk:3});cue(t,'boing',.7);t+=.8;}
    const d=flightDur(a.score);MOVES[n].push({k:'jump',t0:t,d,pk:a.score});cue(t,'boing',a.score<3?.6:.9);if(a.score>=3)cue(t+.05,'whoosh',.45);
    SCORE[n].push([t,a.score,'live',t,d]);t+=d;cue(t,'thud',.9);st.land=t;st.t1=t+(o.react??.6);T0=st.t1}
  else{
    const prep=.25;const st=seg('act',0,{who:n});const per=buildPer(a);const t0=st.t0+prep;
    MOVES[n].push({k:'build',t0,per,from:towerAt(n,t0),to:a.score});for(let i=0;i<a.score-towerAt(n,t0-1e-3);i++)cue(t0+i*per,'place',a.style=='slow'?.9:.55);
    const t=t0+per*(a.score-towerAt(n,t0-1e-3));SCORE[n].push([t0,a.score,'build',t0,per]);cue(t,'top',.6);st.land=t;st.t1=t+(o.react??.6);T0=st.t1}}
function towerAt(n,t){let h=0;for(const m of MOVES[n]){if(m.k=='build'){if(t>=m.t0)h=Math.min(m.to,m.from+Math.floor((t-m.t0)/m.per)+1);}if(m.k=='collapse'&&t>=m.t0)h=0}return h}
// --- the story ---
seg('hook',.35);
const [AT1,AT2,AT3]=att;
addAttempt(AT1);
seg('sly',.8,{who:AT2.who});cue(SEG.at(-1).t0+.1,'ding',.45);
addAttempt(AT2);
seg('shock',.8,{who:AT1.who});cue(SEG.at(-1).t0+.05,'slide_down',.55);
addAttempt(AT3,{react:.5});
seg('laugh',1.0,{who:[AT1.who,AT2.who],butt:AT3.who});for(let i=0;i<6;i++)cue(SEG.at(-1).t0+.05+i*.15,'pop',.35);
let WIN=SPEC.winner;
if(twist.type=='glow'){
  const n=AT3.who;const ch=seg('charge',1.4,{who:n});cue(ch.t0,'scratch',.8);cue(ch.t0+.15,'heartbeat',.7);cue(ch.t0+.55,'riser',.7);cue(ch.t0,'music_off');
  const r=seg('rocket',1.6,{who:n});MOVES[n].push({k:'rocket',t0:r.t0});cue(r.t0,'boing_big',1);cue(r.t0,'blast',.45);cue(r.t0+.1,'whoosh_long',.6);cue(r.t0+1.05,'sparkle',.35);cue(r.t0,'music_on');cue(r.t0,'octave');
  SCORE[n].push([r.t0,Infinity,'rocket',r.t0]);
  const w=seg('wait',1.2,{who:[AT1.who,AT2.who],up:n});cue(w.t0,'music_off');for(let i=0;i<3;i++)cue(w.t0+.1+i*.35,'blink',.4);
  const b=seg('return',.45,{who:n});MOVES[n].push({k:'fall',t0:b.t0,d:.45,from:46});cue(b.t0,'slide_down',.6);
  const v=seg('win',1.25,{who:n,land:b.t1});cue(v.t0,'bonk',.7);cue(v.t0,'boing',.6);cue(v.t0+.07,'chaching',.5);cue(v.t0,'music_on');
  WIN=WIN||n}
else{ // backfire: the leader gets greedy
  const n=AT2.who;const extra=twist.to||30;
  const bo=seg('boast',.9,{who:n});cue(bo.t0+.1,'ding',.45);
  const per=.09;const b=seg('greed',0,{who:n});const t0=b.t0+.15;MOVES[n].push({k:'build',t0,per,from:AT2.score,to:extra,wobble:true});
  for(let i=0;i<extra-AT2.score;i++)cue(t0+i*per,'place',.45);cue(t0+(extra-AT2.score)*per-.6,'creak',.6);
  const tc=t0+(extra-AT2.score)*per+.35;b.t1=tc;T0=tc;SCORE[n].push([t0,extra,'build',t0,per]);
  const c=seg('collapse',1.6,{who:n});MOVES[n].push({k:'collapse',t0:c.t0,from:extra});cue(c.t0,'crumble',.9);cue(c.t0+.05,'slide_down',.6);cue(c.t0+Math.sqrt((extra-1)/15),'bonk',.7);cue(c.t0+Math.sqrt((extra-1)/15),'boing',.5);cue(c.t0,'music_off');cue(c.t0+.2,'whoosh_long',.55);
  SCORE[n].push([c.t0,'X','x']);
  const w=seg('wait',.9,{who:LANES.filter(x=>x!=n),up:n,frame:LANES});cue(w.t0+.05,'heartbeat',.6);
  WIN=WIN||AT1.who;const v=seg('win',1.35,{who:WIN});cue(v.t0,'chaching',.6);cue(v.t0,'sparkle',.4);cue(v.t0,'music_on')}
const loop=seg('loop',1.1);
// round up to whole bars (120 bpm, 2 s) so the music loops with the picture
const TOTAL=Math.ceil(T0/2)*2;loop.t1=TOTAL;
const segAt=t=>{for(const s of SEG)if(t>=s.t0&&t<s.t1)return s;return SEG.at(-1)};

/* ---------- motion ---------- */
function airH(n,t){let h=0;
  for(const m of MOVES[n]){
    if(m.k=='jump'&&t>=m.t0&&t<=m.t0+m.d){const u=(t-m.t0)/m.d;h=4*m.pk*u*(1-u)}
    if(m.k=='rocket'&&t>=m.t0&&t<m.t0+2.8)h=34*Math.pow(t-m.t0,1.55);
    if(m.k=='fall'&&t>=m.t0&&t<m.t0+m.d){const u=(t-m.t0)/m.d;h=m.from*(1-u*u)}
    if(m.k=='collapse'&&t>=m.t0){const u=t-m.t0;const top=m.from;const fallT=Math.sqrt((top-1)/15);h=u<fallT?top-15*u*u:1+Math.abs(Math.sin((u-fallT)*9))*.5*Math.exp(-(u-fallT)*5)}}
  return h}
const feetY=(n,t)=>BASE+(CHALL=='pillar'?towerAt(n,t):0)+airH(n,t);
const heightOf=(n,t)=>(CHALL=='pillar'?towerAt(n,t):0)+airH(n,t);
const airborne=(n,t)=>airH(n,t)>.02;
function landings(){const L=[];for(const n of LANES)for(const m of MOVES[n]){if(m.k=='jump')L.push([n,m.t0+m.d]);if(m.k=='fall')L.push([n,m.t0+m.d])}return L}
const LAND=landings();
function squash(n,t){if(CHALL!='launch')return 0;let k=0;
  for(const m of MOVES[n]){let a=null,b=null;if(m.k=='jump'){a=m.t0;b=m.t0+m.d}if(m.k=='rocket')a=m.t0;if(m.k=='fall')b=m.t0+m.d;
    if(a!=null&&t>=a-.28&&t<a)k=Math.max(k,.38*eout((t-(a-.28))/.28));if(b!=null&&t>=b&&t<b+.35){const u=(t-b)/.35;k=Math.max(k,.45*Math.exp(-u*3)*Math.abs(Math.cos(u*7)))}}
  const s=segAt(t);if(s.type=='charge'&&s.who==n)k=Math.max(k,.62*eout((t-s.t0)/.8));
  return k}
function wobble(n,t){for(const m of MOVES[n])if(m.wobble&&t>=m.t0){const u=t-m.t0;const col=MOVES[n].find(x=>x.k=='collapse');if(col&&t>=col.t0)return 0;return Math.sin(u*9)*Math.min(.16,u*.05)}return 0}
function best(n,t){let b=0;for(const [t0,v,k,s,d] of SCORE[n]){if(t<t0)continue;if(k=='live'){b=Math.max(b,t>=t0+d/2?v:4*v*((t-t0)/d)*(1-(t-t0)/d))}else if(k=='build')b=Math.max(b,towerAt(n,t));else if(k=='rocket')b=Infinity;else if(k=='x')b='X'}return b}

/* ---------- shots ---------- */
function shot(t){const s=segAt(t);const u=(t-s.t0)/Math.max(.01,s.t1-s.t0);const mid=(n,dy=.9)=>feetY(n,t)+dy;
  const maxH=Math.max(...LANES.map(n=>heightOf(n,Math.min(t,TOTAL))));
  const wide=()=>{const H=CHALL=='pillar'?Math.max(0,Math.min(maxH,RULER)):0;return {p:V3(0,BASE+2.2+H*.55,12.2+H*.62-u*.3),l:V3(0,BASE+1.1+H*.5,0),f:52,id:'wide'}};
  switch(s.type){
    case 'hook':case 'loop':return wide();
    case 'act':{const n=s.who;const y=Math.min(mid(n),RULER+2);return {p:V3(LX[n]+1.1,y+.6,10.4),l:V3(LX[n],y,0),f:55,id:'act_'+n}}
    case 'sly':case 'boast':{const n=s.who;return {p:V3(LX[n]+.6,mid(n,1.2),5.6-u*.6),l:V3(LX[n],mid(n,1.15),0),f:44,id:'sly_'+n}}
    case 'shock':{const n=s.who;const k=eout(u*3);return {p:V3(LX[n]+.1,mid(n,1.25),3.9),l:V3(LX[n],mid(n,1.15),0),f:46-k*10,id:'shock_'+n}}
    case 'laugh':{const [a,b]=s.who;const x=(LX[a]+LX[b])/2;const y=(mid(a,1)+mid(b,1))/2;return {p:V3(x,y+.25,8.6+Math.abs(mid(a)-mid(b))*.6),l:V3(x,y,0),f:50,id:'laugh'}}
    case 'charge':{const n=s.who;const k=ease(u);return {p:V3(LX[n],mid(n,.95),4.4-k*1.4),l:V3(LX[n],mid(n,.8),0),f:42-k*4,id:'charge'}}
    case 'rocket':{const n=s.who;const ty=Math.min(mid(n,0),RULER-1.5);const sh=t<s.t0+.35?shake(t,.25*(1-(t-s.t0)/.35)):V3(0,0,0);return {p:V3(LX[n]-.4,Math.max(ty-1.2,BASE+.6),7.5).add(sh),l:V3(LX[n],Math.max(ty+.9,BASE+1.1),0),f:58,id:'rocket'}}
    case 'greed':{const n=s.who;const y=Math.min(mid(n),RULER+2);return {p:V3(LX[n]+1.4,y+.4,11.5),l:V3(LX[n],y-.6,0),f:56,id:'greed'}}
    case 'collapse':{const n=s.who;const y=Math.max(BASE+1.5,feetY(n,t)+.4);const sh=u<.4?shake(t,.18*(1-u/.4)):V3(0,0,0);return {p:V3(LX[n]+1.2,y+2.5,14).add(sh),l:V3(LX[n],y-.4,0),f:60,id:'collapse'}}
    case 'wait':{const ns=s.frame||s.who;const xs=ns.map(n=>LX[n]),fy=ns.map(n=>feetY(n,t));
      const x=(Math.min(...xs)+Math.max(...xs))/2,lo=Math.min(...fy)-1.2,hi=Math.max(...fy)+2.3,cy=(lo+hi)/2;
      // fit everyone in the area under the title banner: half-FOV tan horizontal .30, vertical .53; content uses ~72% of the height
      const d=Math.max(7.6,((Math.max(...xs)-Math.min(...xs))/2+1.4)/.30,(hi-lo)/.6/1.06);
      return {p:V3(x,cy+.3,d-u*.9),l:V3(x,cy+.05*1.06*d,0),f:56,id:'wait'}}
    case 'return':return wide();
    case 'win':{const n=s.who;const k=eout(u*2);return {p:V3(LX[n]-.15,mid(n,1.0),5.6-k*.6),l:V3(LX[n],mid(n,1.05),0),f:46,id:'win_'+n}}}
  return wide()}

/* ---------- HUD-safe framing (QC s02: heads hidden under the title banner / score chips) ----------
   Every shot keeps the heads of the beat's characters below the HUD band (banner + chips end at ~y=530 px)
   and their feet above the bottom edge: crane the camera up when a head is too high, dolly back when both can't fit. */
const HUD_NDC=1-2*610/H,LOW_NDC=-1+2*110/H;
function focusOf(s){if(s.type=='wait')return s.frame||s.who;if(s.type=='laugh')return s.who;if(['hook','loop','return'].includes(s.type))return LANES;return s.who?[].concat(s.who):LANES}
const _v=new THREE.Vector3();
function safeShot(t){const s=segAt(t);const sh=shot(t);if(s.type=='rocket')return sh; // the rocket is meant to fly out of the top
  const p=sh.p.clone(),l=sh.l.clone();const ns=focusOf(s);
  const xOf=n=>{const col=MOVES[n].find(m=>m.k=='collapse');return col&&t>=col.t0?LX[n]+1.05:LX[n]};
  const win=SEG.find(x=>x.type=='win');const extra=n=>win&&n==WIN&&t>=win.t0?.6:0;
  const ndc=(x,y)=>{_v.set(x,y,0).project(camera);return _v.y};
  for(let it=0;it<14;it++){cam(p,l,sh.f);camera.updateMatrixWorld();
    const top=Math.max(...ns.map(n=>ndc(xOf(n),feetY(n,t)+2.05+extra(n)))),bot=Math.min(...ns.map(n=>ndc(xOf(n),feetY(n,t)-.1)));
    const lim=s.type=='win'?1-2*790/H:HUD_NDC; // the win banner sits under the chips, keep the crown below it
    if(top<=lim&&bot>=LOW_NDC)break;
    const d=p.distanceTo(l),visH=2*d*Math.tan(sh.f*Math.PI/360);
    if(top-bot>lim-LOW_NDC){p.sub(l).multiplyScalar(1.12).add(l);continue}           // cannot fit: dolly back
    const dy=(top>lim?(top-lim):-(LOW_NDC-bot))*visH/2*1.05;p.y+=dy;l.y+=dy}  // fits: crane up (or down)
  return {p,l,f:sh.f,id:sh.id}}

/* ---------- acting ---------- */
function act(n,t){const ch=CH[n];const s0=segAt(t);const h=airH(n,t),air=h>.02,sq=squash(n,t);const sc=ch.o.scale||1;
  let s={pos:[LX[n],feetY(n,t)-sq*.55,0],rot:0,anim:'idle',p:t,eyes:'normal',mouth:'closed',look:[0,0]};
  {const col=MOVES[n].find(m=>m.k=='collapse');if(col&&t>=col.t0){const ft=Math.sqrt((col.from-1)/15);s.pos[0]=LX[n]+1.05*eout(Math.min(1,(t-col.t0)/ft))}}
  const lookAt=m=>[clamp((LX[m]-LX[n])*.22,-.7,.7),clamp((feetY(m,t)-feetY(n,t))*-.08,-.6,.4)];
  const me=s0.who===n||(Array.isArray(s0.who)&&s0.who.includes(n));
  const active=SEG.find(x=>x.type=='act'&&t>=x.t0&&t<x.t1);
  if(active&&active.who!=n){s.look=lookAt(active.who);const b=best(active.who,t),mine=best(n,t);if(typeof b=='number'&&typeof mine=='number'&&b>mine){s.eyes='wide';s.mouth='O'}}
  if(active&&active.who==n){
    if(CHALL=='launch'){if(!air&&t<active.t0+.3){s.anim='hold';s.eyes='sly';s.mouth='smile'}else if(air){const up=airH(n,t+.02)>h;s.anim=up?'cheer':'fall';s.eyes=up?'happy':'wide';s.mouth=up?'grin':'O'}else{s.anim='cheer';s.eyes='happy';s.mouth='grin'}}
    else{const building=t>=active.t0+.25&&t<active.land;if(building){s.anim='place';s.eyes='normal';s.mouth='smile';s.look=[0,.35]}else if(t>=active.land){s.anim='cheer';s.eyes='happy';s.mouth='grin'}else{s.anim='hold';s.eyes='sly';s.mouth='smile'}}
    const a=att.find(x=>x.who==n&&x.style=='flop');if(a&&t>=active.land-.05){s.anim='sad';s.eyes='sad';s.mouth='frown'}}
  switch(s0.type){
    case 'sly':if(n==s0.who){s.anim='point';s.eyes='sly';s.mouth='smile'}else s.look=lookAt(s0.who);break;
    case 'boast':if(n==s0.who){s.anim='point';s.eyes='sly';s.mouth='grin'}else{s.look=lookAt(s0.who);s.eyes='wide';s.mouth='O'}break;
    case 'shock':if(n==s0.who){s.eyes='wide';s.mouth='O';s.look=[.25,-.05]}break;
    case 'laugh':if(s0.who.includes(n)){s.anim='cheer';s.eyes='happy';s.mouth='grin';s.look=lookAt(s0.butt)}else{s.anim='sad';s.eyes='sad';s.mouth='frown'}break;
    case 'charge':if(n==s0.who){s.anim='hold';s.eyes='glow';s.mouth='grin';s.glow=1.8}else{s.look=lookAt(s0.who);s.eyes='wide';s.mouth='O'}break;
    case 'rocket':if(n==s0.who){s.anim=air?'cheer':'hold';s.eyes='glow';s.mouth='grin';s.glow=1.4}else{s.anim='lookup';s.eyes='wide';s.mouth='O'}break;
    case 'greed':if(n==s0.who){s.anim='place';s.eyes='happy';s.mouth='grin';s.look=[0,.35]}else{s.look=lookAt(s0.who);s.eyes='wide';s.mouth='O'}break;
    case 'collapse':if(n==s0.who){const u=t-s0.t0;const ft=Math.sqrt((MOVES[n].find(m=>m.k=='collapse').from-1)/15);s.anim=u<ft?'fall':'sad';s.eyes=u<ft?'scared':'closed';s.mouth=u<ft?'O':'frown'}else{s.look=lookAt(s0.who);s.eyes='wide';s.mouth='O'}break;
    case 'wait':if(s0.frame){if(n==s0.up){s.anim='sad';s.eyes=(t-s0.t0)%.6<.3?'closed':'sad';s.mouth='frown'}else{s.look=lookAt(s0.up);s.eyes='sly';s.mouth='grin'}break}
      if(s0.who.includes(n)){const gl=(t-s0.t0)>.55&&(t-s0.t0)<1.0;s.anim='lookup';s.look=gl?[LX[n]<0?.55:-.55,-.1]:[0,-.5];s.eyes=gl?'sly':'normal';s.mouth=gl?'frown':'closed'}break;
    case 'return':s.eyes='wide';s.mouth='O';if(n==s0.who){s.eyes='glow';s.glow=1.4;s.anim='fall'}break;
    case 'win':if(n==s0.who){s.anim='cheer';s.eyes='star';s.mouth='grin'}else{s.look=lookAt(s0.who);s.eyes=n==SPEC.attempts[1].who&&twist.type=='backfire'?'sad':'happy';s.mouth=s.eyes=='sad'?'frown':'smile'}break;
    case 'loop':s.eyes='happy';s.mouth='smile';if(n==WIN){s.anim='cheer';s.eyes='star';s.mouth='grin'}break;
    case 'hook':if(n==AT1.who){s.anim='hold';s.eyes='sly';s.mouth='smile'}break}
  if(air&&s0.type=='return'&&n==s0.who)s.anim='fall';
  pose(ch,s);
  if(s.anim=='cheer'){ch.body.position.y=0;ch.legL.rotation.x=air?-.25:0;ch.legR.rotation.x=air?.25:0;if(!air)ch.root.position.y+=Math.abs(Math.sin(t*7))*.22}
  if(ch.glowEyes){const on=s.eyes=='glow';ch.glowEyes.forEach(m=>{m.scale.setScalar(on?1.9:1);m.material.color.setHex(0xFFF35C)})}
  const st=air&&CHALL=='launch'?Math.min(.18,Math.abs(airH(n,t+.02)-h)*.6):0;
  ch.root.scale.set(sc*(1+sq*.35-st*.4),sc*(1-sq*.45+st),sc*(1+sq*.35-st*.4));
  const wb=wobble(n,t);if(wb){ch.root.position.x+=Math.sin(wb)*towerAt(n,t)*.9;ch.root.rotation.z=wb}else ch.root.rotation.z=0;
  if(PAD[n]){const pd=PAD[n];pd.scale.set(1+sq*.12,1-sq*.55,1+sq*.12);pd.position.set(LX[n],.5+(1-sq*.55)/2,0)}}

/* ---------- towers and debris (pillar) ---------- */
function towers(t){if(CHALL!='pillar')return;
  for(const n of LANES){const im=TOWER[n];const col=MOVES[n].find(m=>m.k=='collapse');const wb=wobble(n,t);
    if(col&&t>=col.t0){const u=t-col.t0;const r=rng(17);let i=0;for(let k=0;k<col.from&&i<80;k++){const h0=BASE+k+.5;const vx=(r()-.5)*5,vz=(r()-.2)*2.5;const delay=k*.012;const uu=Math.max(0,u-delay);
        const T=Math.sqrt(h0/15);const vzz=Math.abs(vx*T-1.05)<.9?Math.min(vz,-(1.1+r()*.8)/T):vz;let y=h0-15*uu*uu;let x=LX[n]+vx*uu,z=vzz*uu;if(y<.0+(k%3)*.02){y=.0+(k%3)*.02;x=LX[n]+vx*T;z=vzz*T}
        setI(im,i++,x,y+.5,z,1,uu*vx*.7,0,uu*vzz*.9)}im.count=i;im.instanceMatrix.needsUpdate=true;continue}
    const h=towerAt(n,t);for(let k=0;k<h;k++){const sway=Math.sin(wb)*(k+1)*.9;setI(im,k,LX[n]+sway,BASE+k+.5,0,1,0,0,wb)}im.count=h;im.instanceMatrix.needsUpdate=true}}

/* ---------- particles ---------- */
function particles(t){let di=0;
  for(const [n,tl] of LAND){const u=t-tl;if(u<0||u>.6)continue;const r=rng(Math.round(tl*100));
    for(let i=0;i<12&&di<64;i++){const a=r()*Math.PI*2,sp=1.2+r()*1.6;setI(DUST,di++,LX[n]+Math.cos(a)*(.55+sp*u),BASE+.02+u*(1.4-u*2.2)*r(),Math.sin(a)*(.55+sp*u),(1-u/.6)*(.8+r()*.6),a,a,0)}}
  if(CHALL=='pillar')for(const n of LANES)for(const m of MOVES[n])if(m.k=='build'){const k=Math.floor((t-m.t0)/m.per);const u=t-(m.t0+k*m.per);if(k>=0&&k<m.to-m.from&&u<.12){const r=rng(k*31+7);for(let i=0;i<4&&di<64;i++){const a=r()*6.28;setI(DUST,di++,LX[n]+Math.cos(a)*.5,BASE+m.from+k-.05,Math.sin(a)*.5,.6*(1-u/.12),a,0,0)}}}
  DUST.count=di;DUST.instanceMatrix.needsUpdate=true;
  let si=0;const w=SEG.find(x=>x.type=='win');if(w&&t>=w.t0&&t<TOTAL){const n=w.who;const u=t-w.t0;const r=rng(77);for(let i=0;i<40;i++){const a=r()*Math.PI*2,b=r()*1.2;setI(SPARK,si++,LX[n]+Math.cos(a)*b*(.4+u*2),feetY(n,w.t0)+1.1+u*2.2-u*u*3+r()*.6,Math.sin(a)*b*(.4+u*2)+.3,(1-u/.6)*(r()*.8+.4),a,0,a)}}
  SPARK.count=si;SPARK.instanceMatrix.needsUpdate=true;
  let gi=0;const c=SEG.find(x=>x.type=='charge');if(c&&t>=c.t0+.2&&t<c.t1+.5){const n=c.who;const u=t-c.t0-.2;const r=rng(78);for(let i=0;i<36;i++){const a=r()*Math.PI*2,rad=.5+((u*1.8+r())%1)*.9;setI(GLOW,gi++,LX[n]+Math.cos(a)*rad,BASE+.1+((u*2.4+r()*2)%2.2),Math.sin(a)*rad,.9*Math.min(1,u*3),a,0,0)}}
  GLOW.count=gi;GLOW.instanceMatrix.needsUpdate=true}

/* ---------- overlay ---------- */
function chip(g,x,y,n,val,big,bad){const [nm,col]=CHIP[n];const s=big?1.12:.95;g.save();g.translate(x,y);g.scale(s,s);rr(g,-130,-46,260,92,26);g.fillStyle='#17181D';g.fill();g.lineWidth=6;g.strokeStyle=bad?'#E53935':col;g.stroke();
  g.textBaseline='middle';g.textAlign='left';outlined(g,nm,-112,4,50,col,'#000',10);g.textAlign='right';outlined(g,val,112,4,56,bad?'#FF5252':'#FFFFFF','#000',10);g.restore()}
function label(n,t){const b=best(n,t);if(b==='X')return 'X';if(b===Infinity){const r=SEG.find(x=>x.type=='rocket');const h=airH(n,Math.min(t,r.t1));if(h<RULER-2)return String(Math.max(1,Math.round(h)));const u=t-r.t0;return u<1.05?'99':u<1.3?'999':'∞'}return String(Math.round(b))}
function drawOverlay(t){const g=ov;g.clearRect(0,0,W,H);g.textAlign='center';g.textBaseline='middle';const s0=segAt(t);
  const pop=t<.25?.88+.12*eout(t/.25):1;g.save();g.translate(W/2,270);g.scale(pop,pop);g.rotate(-.025);rr(g,-470,-118,940,236,46);g.fillStyle=SPEC.banner_color||'#FFE14D';g.fill();g.lineWidth=12;g.strokeStyle='#000';g.stroke();
  outlined(g,SPEC.title[0],0,-46,86,'#FFFFFF','#000',20);outlined(g,SPEC.title[1],0,54,SPEC.title[1].length>13?82:98,'#FF5A1F','#000',22);g.restore();
  const firstT={};for(const n of LANES)firstT[n]=SCORE[n].length?SCORE[n][0][0]:1e9;
  const act_=SEG.find(x=>(x.type=='act'||x.type=='rocket'||x.type=='greed')&&t>=x.t0&&t<x.t1);
  LANES.forEach((n,i)=>{const v=t<firstT[n]?'?':label(n,t);chip(g,W/2+(i-(LANES.length-1)/2)*325,480,n,v,act_&&act_.who===n,v==='X')});
  if(act_&&t>=firstT[act_.who]){const n=act_.who;const txt=label(n,t);const col=CHIP[n][1];const k=1+.08*Math.sin(t*18);g.save();g.translate(W/2,1180);g.scale(k,k);outlined(g,txt,0,0,txt=='∞'?260:210,col,'#000',34);g.restore()}
  if(s0.type=='laugh'){g.save();g.translate(W/2,1700);outlined(g,'HA HA HA',0,0,120,'#FFFFFF','#000',24);g.restore()}
  if(s0.type=='boast'){g.save();g.translate(W/2,1420);outlined(g,SPEC.boast||'WATCH THIS!',0,0,110,'#FFFFFF','#000',24);g.restore()}
  const w=SEG.find(x=>x.type=='win');if(w&&t>=w.t0+.1&&t<Math.min(TOTAL,w.t1+.6)){const u=eout((t-w.t0-.1)/.2);g.save();g.translate(W/2,660);g.scale(u,u);g.rotate(.03);outlined(g,SPEC.win_text||(NAME[WIN]+' WINS?!'),0,0,150,'#3FDC6A','#000',30);g.restore()}}

/* ---------- render ---------- */
function renderAt(t){
  LANES.forEach(n=>act(n,t));towers(t);
  const w=SEG.find(x=>x.type=='win');crown.visible=!!w&&t>=w.t0+.05;if(crown.visible){if(crown.parent!==CH[WIN].head)CH[WIN].head.add(crown);const u=eout((t-w.t0-.05)/.25);crown.scale.setScalar(1.35*u);crown.position.y=.56+(1-u)*.8}
  particles(t);
  const s=safeShot(t);sunFollow(s.l.y);cam(s.p,s.l,s.f);
  renderer.render(scene,camera);drawOverlay(t)}
window.SHOT=t=>shot(t).id;
window.CUES_EXPORT=()=>({total:TOTAL,cues:CUES,seg:SEG.map(s=>({type:s.type,t0:+s.t0.toFixed(3),t1:+s.t1.toFixed(3),who:s.who}))});
window.init=async()=>{
  TL={beats:[],total:TOTAL};
  await document.fonts.load('800 80px Kid','WHO CAN');await document.fonts.ready;(window.NUMS||[]).forEach(p=>p.userData.draw());
  renderAt(0);return TOTAL};
window.renderAt=renderAt;
