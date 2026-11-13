/* ===== MC-S1 Short #01 "Who can bounce the highest?" — lights, props, shots, overlay (18 s, 1080x1920) ===== */
const TOTAL=18;
/* ---------- lights, sky ---------- */
const hemi=new THREE.HemisphereLight(0xCFE8FF,0x5A6B3A,.72);scene.add(hemi);
const sun=new THREE.DirectionalLight(0xFFF2DA,.78);sun.position.set(10,26,18);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
Object.assign(sun.shadow.camera,{left:-14,right:14,top:22,bottom:-6,near:1,far:80});sun.shadow.bias=-.0006;sun.shadow.normalBias=.03;scene.add(sun);sun.target.position.set(0,0,-1);scene.add(sun.target);
(function(){const c=document.createElement('canvas');c.width=4;c.height=256;const g=c.getContext('2d');const gr=g.createLinearGradient(0,0,0,256);
  [[0,'#2F86E0'],[.55,'#7CC2F5'],[1,'#D7F0FF']].forEach(([o,col])=>gr.addColorStop(o,col));g.fillStyle=gr;g.fillRect(0,0,4,256);const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;scene.background=t})();
scene.fog=new THREE.Fog(0xCDEBFF,38,95);
ODD.root.visible=false;

/* ---------- props ---------- */
const PADX={bin:-2.1,bo:0,zu:2.1};
const PAD={};for(const k in PADX){const m=new THREE.Mesh(box1,MAT.pad);m.castShadow=true;m.receiveShadow=true;scene.add(m);PAD[k]=m}
// tower numbers (front face of the pole every 4 blocks)
for(let y=4;y<=28;y+=4){const c=document.createElement('canvas');c.width=c.height=128;const g=c.getContext('2d');g.font='800 92px Kid';g.textAlign='center';g.textBaseline='middle';
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;const pl=new THREE.Mesh(new THREE.PlaneGeometry(.9,.9),new THREE.MeshBasicMaterial({map:t,transparent:true}));pl.position.set(5,y,-1.48);scene.add(pl);
  pl.userData.draw=()=>{g.clearRect(0,0,128,128);g.lineWidth=14;g.strokeStyle='#000';g.strokeText(String(y),64,70);g.fillStyle='#FFE14D';g.fillText(String(y),64,70);t.needsUpdate=true};(window.NUMS=window.NUMS||[]).push(pl)}
// clouds
const cloudM=new THREE.MeshLambertMaterial({color:0xFFFFFF,emissive:0xBFD9F0,emissiveIntensity:.35});
const CLOUD=pool(90,cloudM,1,false);{const r=rng(301);let i=0;for(let c=0;c<14;c++){const cx=r()*44-22,cz=-r()*22+4,cy=23+r()*6;const n=4+(r()*4|0);
  for(let k=0;k<n&&i<90;k++){e.set(0,0,0);q.setFromEuler(e);sc3.set(2+r()*3,1+r()*.6,2+r()*2.5);m4.compose(V3(cx+r()*4-2,cy+r()*.8,cz+r()*3-1.5),q,sc3);CLOUD.setMatrixAt(i++,m4)}}CLOUD.count=i;CLOUD.instanceMatrix.needsUpdate=true}
// flowers (crossed planes)
{const r=rng(302);for(let i=0;i<46;i++){const x=(r()*22-11)|0,z=(r()*14-9)|0;if(Math.abs(z)<2&&Math.abs(x)<5)continue;const m=r()<.5?MAT.flowerW:MAT.flowerP;
  for(const a of[0,Math.PI/2]){const pl=new THREE.Mesh(new THREE.PlaneGeometry(.45,.45),m);pl.position.set(x+.5*(r()-.5),.72,z+.5*(r()-.5));pl.rotation.y=a+.6;scene.add(pl)}}}
// crown for the winner (child of Zu's head)
const crown=new THREE.Group();{[[0,0,0,.42,.1,.42],[-.16,.12,0,.08,.16,.08],[.16,.12,0,.08,.16,.08],[0,.15,.16,.08,.2,.08],[0,.12,-.16,.08,.16,.08]].forEach(([x,y,z,w,h,d])=>{const b=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),MAT.gold);b.position.set(x,y,z);b.castShadow=true;crown.add(b)})}
crown.position.y=.62;crown.visible=false;ZU.head.add(crown);
// landing dust
const DUST=pool(48,new THREE.MeshLambertMaterial({color:0xE8E2D0}),.14,false);
const SPARK=pool(40,new THREE.MeshBasicMaterial({color:0xFFF59D}),.12,false);

/* ---------- motion ---------- */
// jumps: [t0, dur, peak] above the pad top. Zu's big launch is handled separately.
const JUMPS={bin:[[.30,2.2,8]],bo:[[4.40,.8,3],[5.20,2.2,16]],zu:[[9.00,.5,1]]};
const ZL=12.40,ZOFF=15.0,ZBACK=17.0,ZLAND=17.45;
function jumpH(name,t){for(const [t0,d,pk] of JUMPS[name]){if(t>=t0&&t<=t0+d){const u=(t-t0)/d;return 4*pk*u*(1-u)}}return 0}
function zuH(t){if(t>=ZL&&t<ZBACK)return 34*Math.pow(t-ZL,1.55)+jumpH('zu',t);if(t>=ZBACK&&t<ZLAND){const u=(t-ZBACK)/(ZLAND-ZBACK);return 46*(1-u*u)}return jumpH('zu',t)}
const heightOf=(n,t)=>n=='zu'?zuH(t):jumpH(n,t);
function airborne(n,t){return heightOf(n,t)>.02}
// pad squash 0..1: crouch before each take-off, rebound after each landing
function squash(n,t){let k=0;const evs=JUMPS[n].map(j=>[j[0],j[0]+j[1]]);if(n=='zu'){evs.push([ZL,1e9]);evs.push([1e9,ZLAND])}
  for(const [a,b] of evs){if(t>=a-.28&&t<a)k=Math.max(k,.38*eout((t-(a-.28))/.28));if(t>=b&&t<b+.35){const u=(t-b)/.35;k=Math.max(k,.45*Math.exp(-u*3)*Math.abs(Math.cos(u*7)))}}
  if(n=='zu'&&t>=11.6&&t<ZL)k=Math.max(k,.62*eout((t-11.6)/.8));
  if(n=='bin'&&t<.3)k=Math.max(k,.25+.13*eout(t/.3));if(n=='bin'&&t>17.72)k=Math.max(k,.25*eout((t-17.72)/.28));
  return k}
function landings(){const L=[];for(const n in JUMPS)for(const [t0,d] of JUMPS[n])L.push([n,t0+d]);L.push(['zu',ZLAND]);return L}
const LAND=landings();

/* ---------- shots ---------- */
function shot(t){
  if(t<.4||t>=ZBACK){const u=t<.4?t/.4:(t-ZBACK);return {p:V3(0,3.7,12.2-u*.3),l:V3(0,2.6,0),f:52,id:'wide'}}
  if(t<3.6){const y=jumpH('bin',t);const ty=2.4+y;return {p:V3(-.9,ty+.6,10.4),l:V3(-2.0,ty,0),f:55,id:'bin'}}
  if(t<4.4){const u=(t-3.6)/.8;return {p:V3(.6,2.7,5.6-u*.6),l:V3(0,2.65,0),f:44,id:'bo_sly'}}
  if(t<7.8){const y=jumpH('bo',t);const ty=2.4+y;return {p:V3(1.3,ty+.6,11.4),l:V3(.2,ty,0),f:56,id:'bo'}}
  if(t<8.6){const u=eout((t-7.8)/.25);return {p:V3(-2.0,3.15,3.9),l:V3(-2.1,3.05,0),f:46-u*10,id:'bin_shock'}}
  if(t<10){const y=jumpH('zu',t);return {p:V3(1.85,2.3+y*.5,6.4),l:V3(2.1,1.95+y*.6,0),f:46,id:'zu_hop'}}
  if(t<11){return {p:V3(-1.05,3.0,8.6),l:V3(-1.05,2.75,0),f:50,id:'laugh'}}
  if(t<ZL){const u=ease((t-11)/1.4);return {p:V3(2.1,2.35,4.4-u*1.4),l:V3(2.1,2.2-u*.15,0),f:42-u*4,id:'zu_charge'}}
  if(t<ZOFF){const y=zuH(t);const ty=Math.min(1.5+y,26.5);const sh=t<ZL+.35?shake(t,.25*(1-(t-ZL)/.35)):V3(0,0,0);return {p:V3(1.7,ty-1.6,10.5).add(sh),l:V3(2.1,ty+1.2,0),f:58,id:'zu_rocket'}}
  return {p:V3(-1.05,1.05,5.8),l:V3(-1.05,5.2,0),f:62,id:'look_up'}}

/* ---------- per-character acting ---------- */
function act(n,t){const ch=CH[n];const h=heightOf(n,t),air=h>.02,sq=squash(n,t);const sc=ch.o.scale||1;
  let s={pos:[PADX[n],1.5-sq*1+h,0],rot:0,anim:'idle',p:t,eyes:'normal',mouth:'closed',look:[0,0]};
  const lookAt=m=>[clamp((PADX[m]-PADX[n])*.22,-.7,.7),0];
  if(air){const up=(heightOf(n,t+.02)-h)>0;s.anim=up?'cheer':'fall';s.eyes=up?'happy':'wide';s.mouth=up?'grin':'O'}
  if(n=='bin'){
    if(!air&&t<.3){s.anim='hold';s.eyes='sly';s.mouth='smile'}
    else if(!air&&t<3.6){s.anim='cheer';s.eyes='happy';s.mouth='grin'}
    else if(t<7.8&&!air){s.look=lookAt('bo');s.eyes=t>5.2?'wide':'normal';s.mouth=t>5.2?'O':'smile'}
    else if(t<8.6){s.anim='idle';s.eyes='wide';s.mouth='O';s.look=[.25,-.05]}
    else if(t<10){s.look=lookAt('zu')}
    else if(t<11){s.anim='cheer';s.eyes='happy';s.mouth='grin'}
    else if(t<ZL){s.look=lookAt('zu');s.eyes='wide';s.mouth='O'}
    else if(t<ZBACK){s.anim='lookup';s.look=[.15,-.5];s.eyes=t<ZOFF?'wide':'normal';s.mouth=t<ZOFF?'O':'closed'}
    else{s.look=lookAt('zu');s.eyes='wide';s.mouth='O';if(t>17.72){s.anim='hold';s.eyes='sly';s.mouth='smile';s.look=[0,0]}}}
  if(n=='bo'){
    if(t<3.6&&!air){s.look=lookAt('bin');s.eyes=t>.6&&t<3?'wide':'normal';s.mouth=t>.6&&t<3?'O':'closed'}
    else if(t<4.4){s.anim='present';s.eyes='sly';s.mouth='smile'}
    else if(t<7.8&&!air){s.anim='cheer';s.eyes='happy';s.mouth='grin'}
    else if(t<10){s.look=lookAt('zu')}
    else if(t<11){s.anim='cheer';s.eyes='happy';s.mouth='grin'}
    else if(t<ZL){s.look=lookAt('zu');s.eyes='wide';s.mouth='O'}
    else if(t<ZBACK){s.anim='lookup';s.look=[-.1,-.5];s.eyes=t<ZOFF?'wide':'normal';s.mouth=t<ZOFF?'O':'closed'}
    else{s.look=lookAt('zu');s.eyes='wide';s.mouth='O'}}
  if(n=='zu'){
    if(t<8.6){s.look=lookAt(t<4.4?'bin':'bo');if(t>.6&&t<3||t>5.2&&t<7.6){s.eyes='star';s.mouth='O'}}
    else if(!air&&t<9.5){s.anim='hold';s.eyes='happy';s.mouth='smile'}
    else if(!air&&t<10){s.anim='cheer';s.eyes='happy';s.mouth='grin'}
    else if(t<11){s.look=lookAt('bin');s.eyes='normal';s.mouth='frown'}
    else if(t<11.6){s.anim='sad';s.eyes='sad';s.mouth='frown'}
    else if(t<ZL){s.anim='hold';s.eyes='glow';s.mouth='grin';s.glow=1.6}
    else if(t>=ZLAND){s.anim='cheer';s.eyes='star';s.mouth='grin'}
    if(air&&t>=ZL){s.eyes='glow';s.glow=1.4}}
  pose(ch,s);
  // squash & stretch on top of the pose
  const st=air?Math.min(.18,Math.abs(heightOf(n,t+.02)-h)*.6):0;
  ch.root.scale.set(sc*(1+sq*.35-st*.4),sc*(1-sq*.45+st),sc*(1+sq*.35-st*.4));
  const pd=PAD[n];pd.scale.set(1+sq*.12,1-sq*.55,1+sq*.12);pd.position.set(PADX[n],.5+(1-sq*.55)/2,0)}

/* ---------- particles ---------- */
function particles(t){let di=0;
  for(const [n,tl] of LAND){const u=t-tl;if(u<0||u>.6)continue;const r=rng(Math.round(tl*100));
    for(let i=0;i<12&&di<48;i++){const a=r()*Math.PI*2,sp=1.2+r()*1.6;setI(DUST,di++,PADX[n]+Math.cos(a)*(.55+sp*u),1.52+u*(1.4-u*2.2)*r(),Math.sin(a)*(.55+sp*u),(1-u/.6)*(.8+r()*.6),a,a,0)}}
  DUST.count=di;DUST.instanceMatrix.needsUpdate=true;
  let si=0;if(t>=ZLAND&&t<TOTAL){const u=t-ZLAND;const r=rng(77);for(let i=0;i<40;i++){const a=r()*Math.PI*2,b=r()*1.2;setI(SPARK,si++,PADX.zu+Math.cos(a)*b*(.4+u*2),2.6+u*2.2-u*u*3+r()*.6,Math.sin(a)*b*(.4+u*2)+.3,(1-u/.6)*(r()*.8+.4),a,0,a)}}
  if(t>=11.6&&t<ZL+.5){const u=t-11.6;const r=rng(78);for(let i=0;i<24&&si<40;i++){const a=r()*Math.PI*2,rad=.6+((u*1.8+r())%1)*.9;setI(SPARK,si++,PADX.zu+Math.cos(a)*rad,1.6+((u*2+r()*2)%2),Math.sin(a)*rad,.7,a,0,0)}}
  SPARK.count=si;SPARK.instanceMatrix.needsUpdate=true}

/* ---------- overlay ---------- */
const BEST={bin:0,bo:0,zu:0};
function best(n,t){let b=0;for(const [t0,d,pk] of JUMPS[n]){if(t>=t0+d/2)b=Math.max(b,pk);else if(t>=t0)b=Math.max(b,jumpH(n,t))}return b}
function zuLabel(t){if(t<ZL)return String(Math.round(best('zu',t)));const h=zuH(Math.min(t,ZOFF));if(h<26)return String(Math.round(h));if(t<13.6)return '99';if(t<14.2)return '999';return '∞'}
function chip(g,x,y,n,val,big){const [nm,col]=CHIP[n];const s=big?1.25:1;g.save();g.translate(x,y);g.scale(s,s);rr(g,-130,-46,260,92,26);g.fillStyle='rgba(0,0,0,.55)';g.fill();g.lineWidth=6;g.strokeStyle=col;g.stroke();
  g.textBaseline='middle';g.textAlign='left';outlined(g,nm,-112,4,50,col,'#000',10);g.textAlign='right';outlined(g,val,112,4,56,'#FFFFFF','#000',10);g.restore()}
function drawOverlay(t){const g=ov;g.clearRect(0,0,W,H);g.textAlign='center';g.textBaseline='middle';
  // question banner (kept clear of the top UI and the bottom title area)
  const pop=t<.25?.88+.12*eout(t/.25):1;g.save();g.translate(W/2,250);g.scale(pop,pop);g.rotate(-.025);rr(g,-470,-118,940,236,46);g.fillStyle='#FFE14D';g.fill();g.lineWidth=12;g.strokeStyle='#000';g.stroke();
  outlined(g,'WHO CAN BOUNCE',0,-46,86,'#FFFFFF','#000',20);outlined(g,'THE HIGHEST?',0,54,98,'#FF5A1F','#000',22);g.restore();
  // scoreboard
  const sb={bin:t<.3?'?':String(Math.round(best('bin',t))),bo:t<4.4?'?':String(Math.round(best('bo',t))),zu:t<9?'?':zuLabel(t)};
  const act_=t<3.6?'bin':t<7.8?'bo':t>=8.6&&t<ZOFF?'zu':null;
  ['bin','bo','zu'].forEach((n,i)=>chip(g,190+i*350,470,n,sb[n],n===act_));
  // big live counter during flights
  const live=t>=.3&&t<3.6?['bin',best('bin',t)]:t>=4.4&&t<7.8?['bo',best('bo',t)]:t>=9&&t<10?['zu',best('zu',t)]:t>=ZL&&t<ZOFF?['zu',null]:null;
  if(live){const [n,v]=live;const txt=v===null?zuLabel(t):String(Math.round(v));const col=CHIP[n][1];const k=1+.08*Math.sin(t*18);g.save();g.translate(W/2,1180);g.scale(k,k);outlined(g,txt,0,0,txt=='∞'?260:210,col,'#000',34);g.restore()}
  if(t>=10&&t<11){g.save();g.translate(W/2,1420);outlined(g,'HA HA HA',0,0,120,'#FFFFFF','#000',24);g.restore()}
  if(t>=ZOFF&&t<ZBACK){const n=1+Math.floor((t-ZOFF)/.5)%4;g.save();g.translate(W/2,820);outlined(g,'.'.repeat(Math.min(n,3)),0,0,200,'#FFFFFF','#000',30);g.restore()}
  if(t>=17.5){const u=eout((t-17.5)/.2);g.save();g.translate(W/2,820);g.scale(u,u);g.rotate(.03);outlined(g,'ZU WINS?!',0,0,150,'#3FDC6A','#000',30);g.restore()}}

/* ---------- render ---------- */
let tNow=0;
function renderAt(t){tNow=t;
  ['bin','bo','zu'].forEach(n=>act(n,t));
  crown.visible=t>=ZLAND+.05;if(crown.visible){const u=eout((t-ZLAND-.05)/.25);crown.scale.setScalar(u);crown.position.y=.62+(1-u)*.6}
  particles(t);
  const s=shot(t);cam(s.p,s.l,s.f);
  renderer.render(scene,camera);drawOverlay(t)}
window.SHOT=t=>shot(t).id;

/* ---------- init ---------- */
window.init=async()=>{
  TL={beats:[],total:TOTAL};
  await document.fonts.load('800 80px Kid','WHO CAN BOUNCE');await document.fonts.ready;(window.NUMS||[]).forEach(p=>p.userData.draw());
  renderAt(0);return TOTAL};
window.renderAt=renderAt;
