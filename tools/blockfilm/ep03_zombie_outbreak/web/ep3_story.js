/* ---------- lights, sky ---------- */
const hemi=new THREE.HemisphereLight(0x5a6f9a,0x141418,.32);scene.add(hemi);
const moon=new THREE.DirectionalLight(0x9fb4ff,.45);moon.position.set(-18,30,26);moon.castShadow=true;moon.shadow.mapSize.set(2048,2048);
Object.assign(moon.shadow.camera,{left:-26,right:26,top:24,bottom:-24,near:1,far:110});moon.shadow.bias=-.0007;moon.shadow.normalBias=.03;scene.add(moon);moon.target.position.set(0,0,2);scene.add(moon.target);
const lampL=new THREE.PointLight(0xFFB062,1.2,18,1);lampL.position.set(-10,5.6,2.4);scene.add(lampL);
const lampR=new THREE.PointLight(0xFFB062,1.2,18,1);lampR.position.set(12,5.6,2.4);scene.add(lampR);
const alarm=new THREE.PointLight(0xFF1A1A,0,14,1);alarm.position.set(0,4.1,1.4);scene.add(alarm);
const inLight=new THREE.PointLight(0xCFE3FF,.5,22,1);inLight.position.set(0,6.2,-7);scene.add(inLight);
function skyTex(stops){const c=document.createElement('canvas');c.width=4;c.height=256;const g=c.getContext('2d');const gr=g.createLinearGradient(0,0,0,256);stops.forEach(([o,col])=>gr.addColorStop(o,col));g.fillStyle=gr;g.fillRect(0,0,4,256);
  const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;return t}
const SKY={night:skyTex([[0,'#04060E'],[.6,'#0E1730'],[1,'#1F2B45']]),day:skyTex([[0,'#6F7F93'],[.7,'#A9B4BF'],[1,'#C9CFD3']])};
// moon disc
const moonDisc=new THREE.Mesh(new THREE.BoxGeometry(3,3,.1),new THREE.MeshBasicMaterial({color:0xDDE6FF,fog:false}));moonDisc.position.set(-30,34,60);moonDisc.lookAt(0,4,0);scene.add(moonDisc);
let ENV='';const FOG=new THREE.Fog(0x0B1222,16,62);scene.fog=FOG;
function setEnv(m){if(m===ENV)return;ENV=m; // one Fog object for the whole film: swapping Fog objects recompiles every shader
  if(m=='day'){scene.background=SKY.day;FOG.color.set(0xA9B4BF);FOG.near=24;FOG.far=75;hemi.color.set(0xC4CED8);hemi.groundColor.set(0x55524C);hemi.intensity=.78;
    moon.color.set(0xFFF1DC);moon.intensity=.55;moon.position.set(14,22,40);lampL.intensity=0;lampR.intensity=0;inLight.intensity=.25;moonDisc.visible=false}
  else{scene.background=SKY.night;FOG.color.set(m=='rain'?0x0D1424:0x0B1222);FOG.near=m=='rain'?10:16;FOG.far=m=='rain'?46:62;hemi.color.set(0x5a6f9a);hemi.groundColor.set(0x141418);hemi.intensity=m=='rain'?.26:.32;
    moon.color.set(0x9fb4ff);moon.intensity=m=='rain'?.22:.45;moon.position.set(-18,30,26);moonDisc.visible=m!='rain'}}
const flick=(t,s)=>{const a=Math.sin(t*23+s)*Math.sin(t*7.3+s*2)*Math.sin(t*3.1+s);return a>.55?.15:1};

/* ---------- set dressing: roll-up door, sign, street lamps, rain ---------- */
const doorT=tex(16,16,p=>{const r=rng(95);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#8C939B',.9+r()*.15));for(let y=1;y<16;y+=2)p(0,y,'#5C636B',16,1);p(6,14,'#2A2D31',4,1)});
const door=new THREE.Mesh(new THREE.BoxGeometry(5,4,.12),new THREE.MeshLambertMaterial({map:doorT}));door.castShadow=true;door.receiveShadow=true;scene.add(door);
function setDoor(f,wob){const h=Math.max(.02,4*(1-f));door.scale.y=h/4;door.position.set(0,4.5-h/2,.38+(wob||0)*.06);door.rotation.x=(wob||0)*.02;doorT.repeat.set(1,h/4)}
const signC=document.createElement('canvas');signC.width=1024;signC.height=160;
const signT=new THREE.CanvasTexture(signC);signT.encoding=THREE.sRGBEncoding;
const sign=new THREE.Mesh(new THREE.PlaneGeometry(11,1.72),new THREE.MeshBasicMaterial({map:signT}));sign.position.set(0,5.5,.53);scene.add(sign);
function drawSign(){const g=signC.getContext('2d');g.fillStyle='#7A1414';g.fillRect(0,0,1024,160);g.fillStyle='#4A0A0A';g.fillRect(0,140,1024,20);g.font='800 118px Kid';g.textAlign='center';g.textBaseline='middle';
  g.lineWidth=14;g.strokeStyle='#2A0505';g.strokeText('BLOCK MART',512,76);g.fillStyle='#FFE7B0';g.fillText('BLOCK MART',512,76);signT.needsUpdate=true}
const poleM=new THREE.MeshLambertMaterial({color:0x3C4046});const bulbM=new THREE.MeshBasicMaterial({color:0xFFD08A});
[[-10,2.6],[12,2.6]].forEach(([x,z])=>{const p=new THREE.Mesh(new THREE.BoxGeometry(.25,5.6,.25),poleM);p.position.set(x,3.3,z+.6);p.castShadow=true;const a=new THREE.Mesh(new THREE.BoxGeometry(.2,.2,1),poleM);a.position.set(x,6,z+.2);
  const b=new THREE.Mesh(new THREE.BoxGeometry(.5,.18,.5),bulbM.clone());b.position.set(x,5.85,z-.1);scene.add(p,a,b);(x<0?lampL:lampR).bulb=b});
const rain=new THREE.InstancedMesh(new THREE.BoxGeometry(.025,.55,.025),new THREE.MeshBasicMaterial({color:0x9fb7d6,transparent:true,opacity:.32,depthWrite:false}),300);rain.count=0;scene.add(rain);
const RAIN=[];{const r=rng(97);for(let i=0;i<300;i++)RAIN.push([r()*30-15,r()*13+.6,r()*12])}

/* ---------- the horde: one instanced block zombie, 64 copies (own design: torn clothes, sunken eyes) ---------- */
const HN=64;
const zSkin=noiseTex('#6E9461',.16,101),zHair=noiseTex('#33402E',.2,102);
const zFace=tex(16,16,p=>{const r=rng(103);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#6E9461',.85+r()*.25));p(0,0,'#33402E',16,2);p(0,2,'#33402E',4,1);p(12,2,'#33402E',4,1);
  p(3,5,'#141A12',4,3);p(9,5,'#141A12',4,3);p(4,6,'#3A0B0B',2,1);p(10,6,'#3A0B0B',2,1);p(5,11,'#1E120E',6,2);p(6,12,'#5A2A22',4,1);p(12,9,'#4F6B45',2,2)});
const zSide=tex(16,16,p=>{const r=rng(104);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#6E9461',.85+r()*.25));p(0,0,'#33402E',16,3);p(0,3,'#33402E',4,3)});
const zShirt=tex(8,12,p=>{const r=rng(105);for(let y=0;y<12;y++)for(let x=0;x<8;x++)p(x,y,shade('#E6E6E6',.85+r()*.2));p(1,9,'#6E9461',2,2);p(5,4,'#6E9461',2,1);p(6,10,'#6E9461',2,2);p(0,11,'#6E9461',1,1)});
const zArm=tex(4,12,p=>{const r=rng(106);for(let y=0;y<12;y++)for(let x=0;x<4;x++)p(x,y,shade('#6E9461',.85+r()*.25))});
const zLeg=tex(4,12,p=>{const r=rng(107);for(let y=0;y<10;y++)for(let x=0;x<4;x++)p(x,y,shade('#E0E0E0',.85+r()*.2));p(0,10,'#2A2A2A',4,2);p(1,7,'#6E9461',2,1)});
const zl=t=>new THREE.MeshLambertMaterial({map:t});
const ZG={head:new THREE.BoxGeometry(.5,.5,.5).translate(0,.25,0),body:new THREE.BoxGeometry(.5,.75,.25),limb:new THREE.BoxGeometry(.25,.75,.25).translate(0,-.32,0)};
const ZI={head:new THREE.InstancedMesh(ZG.head,[zl(zSide),zl(zSide),zl(zHair),zl(zSkin),zl(zFace),zl(zSide)],HN),body:new THREE.InstancedMesh(ZG.body,zl(zShirt),HN),
  armL:new THREE.InstancedMesh(ZG.limb,zl(zArm),HN),armR:new THREE.InstancedMesh(ZG.limb,zl(zArm),HN),legL:new THREE.InstancedMesh(ZG.limb,zl(zLeg),HN),legR:new THREE.InstancedMesh(ZG.limb,zl(zLeg),HN)};
const ZR=(()=>{const R=new THREE.Object3D(),B=new THREE.Object3D(),bm=new THREE.Object3D(),N=new THREE.Object3D(),hd=new THREE.Object3D(),aL=new THREE.Object3D(),aR=new THREE.Object3D(),lL=new THREE.Object3D(),lR=new THREE.Object3D();
  bm.position.y=1.125;N.position.y=1.5;aL.position.set(.375,1.45,0);aR.position.set(-.375,1.45,0);lL.position.set(.125,.75,0);lR.position.set(-.125,.75,0);
  N.add(hd);B.add(bm,N,aL,aR);R.add(B,lL,lR);return {R,B,bm,N,hd,aL,aR,lL,lR}})();
const SHIRTS=['#6D5D4B','#7A2E2E','#4E5B6E','#5B6B3A','#8A7F6A','#3E3E46','#6B4E7A','#2F5E5A'],PANTS=['#2E3440','#4A3B2E','#3B4A5A','#2A2A2A','#5A4A3A'];
const HZ=[];{const r=rng(111);const col=new THREE.Color();
  for(let i=0;i<HN;i++){const front=i<24;const fromR=false;
    let tx,tz;if(front){tx=-9.2+(i/23)*18.4+(r()-.5)*.4;tz=1.08+r()*.08}else{tx=-11+r()*22;tz=1.8+r()*3.2}
    const door=front&&Math.abs(tx)<2.6;const ta=door?10.55+r()*1.3:9.0+r()*5.5;
    const sx=fromR?24+r()*10:-30+r()*10,sz=4.2+r()*7;const d=Math.hypot(tx-sx,tz-sz);
    HZ.push({front,tx,tz,ta,v:1.25+r()*.5,dx:(tx-sx)/d,dz:(tz-sz)/d,ph:r()*10,s:.94+r()*.14,
      d2x:-15+r()*30,d2z:2.2+r()*6,d2r:r()*6.28,d2tx:-9+(i%12)/11*5+(r()-.5)*.3,d2front:i%3==0,
      d4x:-9+r()*18,d4z:6+r()*6});
    const k=.82+r()*.3;col.setRGB(k,k,k);['head','armL','armR'].forEach(n=>ZI[n].setColorAt(i,col));
    col.set(SHIRTS[i%SHIRTS.length]).multiplyScalar(.9+r()*.25);ZI.body.setColorAt(i,col);col.set(PANTS[(i*7)%PANTS.length]);ZI.legL.setColorAt(i,col);ZI.legR.setColorAt(i,col)}}
Object.values(ZI).forEach(m=>{m.castShadow=true;m.receiveShadow=true;m.count=0;scene.add(m)});
let zc=0;
function zput(x,z,rot,s,st){const R=ZR;R.R.position.set(x,.5,z);R.R.rotation.set(0,rot,0);R.R.scale.setScalar(s);
  R.B.position.y=st.bob||0;R.B.rotation.x=st.lean||0;R.N.rotation.set(st.hp||0,st.hy||0,0);
  R.aL.rotation.set(st.aL,0,st.aLz||0);R.aR.rotation.set(st.aR,0,st.aRz||0);R.lL.rotation.set(st.lL||0,0,0);R.lR.rotation.set(st.lR||0,0,0);
  R.R.updateMatrixWorld(true);ZI.head.setMatrixAt(zc,R.hd.matrixWorld);ZI.body.setMatrixAt(zc,R.bm.matrixWorld);ZI.armL.setMatrixAt(zc,R.aL.matrixWorld);ZI.armR.setMatrixAt(zc,R.aR.matrixWorld);
  ZI.legL.setMatrixAt(zc,R.lL.matrixWorld);ZI.legR.setMatrixAt(zc,R.lR.matrixWorld);zc++}
const zWalk=(p,sp=1)=>{const w=Math.sin(p*5*sp);return {lL:w*.45,lR:-w*.45,aL:-1.45+Math.sin(p*3)*.07,aR:-1.5+Math.sin(p*3+1)*.07,bob:Math.abs(Math.cos(p*5*sp))*.04,hy:Math.sin(p*1.7)*.2,lean:.06}};
const zBang=(p)=>{const w=Math.max(0,Math.sin(p*9)),w2=Math.max(0,Math.sin(p*9+2.2));return {aL:-1.55-w*.85,aR:-1.55-w2*.85,lean:.12-w*.05,hy:Math.sin(p*2)*.12,hp:-.1}};
const zStand=(p)=>({aL:-1.2+Math.sin(p*1.3)*.08,aR:-1.3+Math.sin(p*1.1+1)*.08,lean:.1+Math.sin(p*.9)*.04,hy:Math.sin(p*.7)*.35,hp:.25+Math.sin(p*.8)*.08});
let BANGS=[];// times the horde hits the glass/door, for the overlay/shake (audio.py derives the same)
function horde(t,X){zc=0;
  if(t<X.day2){ // night 1: march up the street, then pile on the glass and the door
    HZ.forEach(z=>{const left=z.ta-t;const p=t*1.15+z.ph;
      if(left>0){const x=z.tx-z.dx*z.v*left,zz=z.tz-z.dz*z.v*left;if(Math.abs(x)>36)return;zput(x,zz,Math.atan2(z.dx,z.dz),z.s,zWalk(p))}
      else zput(z.tx,z.tz,Math.PI,z.s,z.front?zBang(p+z.ph):zWalk(p*.4))})}
  else if(t<X.day3){ // day 2: spread out and calm ... until the crunch
    const tc=X.crunch,go=tc+.75;
    HZ.forEach((z,i)=>{const p=t*.8+z.ph;if(i>=48)return;let x=z.d2x,zz=z.d2z,rot=z.d2r;let st=zStand(p);
      if(t>tc+.2){const snap=clamp((t-tc-.2-(i%7)*.05)/.18);const tr=Math.atan2(-x,-zz);rot=lerp(z.d2r,tr+Math.round((z.d2r-tr)/6.283)*6.283,eout(snap));st.hy=0;st.hp=-.05}
      if(t>go){const tx=z.d2front?z.d2tx:x*.85,tz=z.d2front?1.08:Math.max(1.8,zz-2.5);const d=Math.hypot(tx-z.d2x,tz-z.d2z);const u=clamp((t-go)*2.4/d);
        x=lerp(z.d2x,tx,u);zz=lerp(z.d2z,tz,u);rot=Math.atan2(tx-z.d2x,tz-z.d2z);st=u<1?zWalk(t*1.6+z.ph,1.5):(z.d2front?zBang(t+z.ph):zStand(p));if(u>=1)rot=Math.PI}
      zput(x,zz,rot,z.s,st)})}
  else if(t>X.p0){ // the end sting: they are all standing in the rain behind him
    HZ.forEach((z,i)=>{if(i>=18)return;const rise=clamp((t-X.p0-.6-(i%6)*.12)/.5);if(rise<=0)return;zput(z.d4x,z.d4z,Math.PI+Math.sin(i)*.3,z.s*(.7+.3*rise),zStand(t+z.ph))})}
  Object.values(ZI).forEach(m=>{m.count=zc;m.instanceMatrix.needsUpdate=true})}

/* ---------- paths ---------- */
const hd2=(a,b)=>Math.atan2(b[1]-a[1],b[2]-a[2]);
function path(t,pts){if(t<=pts[0][0])return {p:[pts[0][1],.5,pts[0][2]],rot:hd2(pts[0],pts[1]),mv:false};
  for(let i=0;i<pts.length-1;i++){const a=pts[i],b=pts[i+1];if(t<=b[0]){const u=(t-a[0])/(b[0]-a[0]);return {p:[lerp(a[1],b[1],u),.5,lerp(a[2],b[2],u)],rot:hd2(a,b),mv:b[1]!=a[1]||b[2]!=a[2]}}}
  const L=pts[pts.length-1],P=pts[pts.length-2];return {p:[L[1],.5,L[2]],rot:hd2(P,L),mv:false}}

/* ---------- shots (all cut points derived from the recorded lines) ---------- */
function SH(){const tClose=E('door')+.5;
  return {a1:3.0, b1:S('run')-.35, c1:S('door')-.4, tClose, d1:tClose+.6, e1:S('hungry')-.3, f1:S('hungry')+1.2, f2:S('rules')-.25, g1:S('thirty')-.1, g2:E('thirty')+.6,
    day2:E('thirty')+.6, h0:E('day2')+.7, crunch:S('shh')-1.6, i0:S('shh')-1.45, j0:S('shh')-.15, j1:S('sorry')-.15, j2:E('sorry')+.5,
    day3:E('sorry')+.5, k0:E('day3')+.7, knock:E('day3')+1.25, k1:E('day3')+2.1, l0:S('bunny')-.3, m0:S('how')-.25, n0:S('know')-.3, o0:S('home')-.3, p0:S('end')-.4}}
let tNow=0;
function renderAt(t){
  tNow=t;const X=SH();const ov2={};let sh=V3(0,0,0);
  rain.count=0;
  // environment by act
  setEnv(t<X.day2?'night':t<X.day3?'day':'rain');
  if(ENV!='day'){const fl=flick(t,1);lampL.intensity=1.25*fl;lampL.bulb.material.color.setScalar(fl);lampR.intensity=ENV=='rain'?.9:0;lampR.bulb.material.color.setScalar(ENV=='rain'?.9:.08);
    inLight.intensity=ENV=='rain'?.38:.5;if(ENV=='rain'&&t>X.p0+2.6)inLight.intensity=Math.max(0,.42-(t-X.p0-2.6)*1.4)}
  alarm.intensity=t<X.d1+4?(Math.sin(t*9)>0?2.4:.25):0;
  sign.material.color.setScalar(ENV=='day'?.75:.22+(.55*flick(t*.7,4)));
  if(ENV=='rain'){RAIN.forEach((d,i)=>{const y=d[1]-((t*13+i*.37)%13);setI(rain,rain.count++,d[0],(y<.5?y+13:y),d[2]+.5,1)});rain.instanceMatrix.needsUpdate=true}
  // door: open until Bin pulls it down
  const pull0=X.tClose-.75;let f=t<pull0?1:t<X.tClose?1-ein((t-pull0)/.75):0;let wob=0;
  BANGS=[];if(t<X.day2){HZ.forEach(z=>{if(z.front&&Math.abs(z.tx)<2.6)for(let k=0;k<6;k++)BANGS.push(z.ta+.25+k*.7+z.ph%.3)})}
  if(t>X.tClose&&t<X.day2){wob=Math.sin((t-X.tClose)*38)*Math.exp(-(t-X.tClose)*5)*2;BANGS.forEach(b=>{const u=t-b;if(u>0&&u<.25)wob+=Math.sin(u*60)*(1-u/.25)})}
  setDoor(f,wob);
  horde(t,X);

  const b={},o={},z={},d={visible:false};
  // ---- night 1: run for the store ----
  const BINp=[[X.b1-.2,17,2.2],[8.7,1.0,2.2],[9.35,.5,-2.0],[9.55,.3,-1.0]],BOp=[[X.b1-.2,19.2,2.95],[8.85,2.2,2.95],[9.45,1.9,-3.4]],ZUp=[[X.b1-.2,18.1,2.55],[8.8,-.4,2.55],[9.4,-.7,-2.8]];
  const pb=path(t,BINp),po=path(t,BOp),pz=path(t,ZUp);
  Object.assign(b,{pos:pb.p,rot:pb.rot,anim:pb.mv?'run':'idle',p:t,eyes:'scared',mouth:mouthOf('bin',t,'O')});
  Object.assign(o,{pos:po.p,rot:po.rot,anim:po.mv?'run':'idle',p:t+.3,eyes:'scared',mouth:mouthOf('bo',t,'O')});
  Object.assign(z,{pos:pz.p,rot:pz.rot,anim:pz.mv?'run':'idle',p:t+.6,eyes:'scared',mouth:'O'});
  if(t>=S('door')-.1&&t<9.45&&po.mv){o.look=[2.4,0];o.anim='run'}
  if(t>=9.45&&t<X.d1){o.rot=0;o.anim='yell';o.mouth=mouthOf('bo',t,'open')}
  if(t>=9.4&&t<X.d1){z.rot=0;z.anim='cower'}
  if(t>=9.55&&t<X.tClose+.15){const k=clamp((t-pull0)/.75);Object.assign(b,{pos:[.3,.5,-.95],rot:0,anim:t<pull0?'pull':'pull',k:t<pull0?0:k,eyes:'angry',mouth:'grin'})}
  if(t>=X.tClose+.15&&t<X.e1){const u=ease((t-X.tClose-.15)/1.4);
    Object.assign(b,{pos:[lerp(.3,.9,u),.5,lerp(-.95,-4.0,u)],rot:0,anim:u<1?'back':'pant',p:t,eyes:'wide',mouth:mouthOf('bin',t,'O')});
    Object.assign(o,{pos:[lerp(1.9,-1.3,u),.5,lerp(-3.4,-4.3,u)],rot:0,anim:u<1?'back':'pant',p:t+.4,eyes:'scared',mouth:'O'});
    Object.assign(z,{pos:[lerp(-.7,-.2,u),.5,lerp(-2.8,-4.9,u)],rot:0,anim:'cower',p:t,eyes:'scared',mouth:'O'});
    if(speaking('bin',t))b.anim='pant'}
  // ---- rules ----
  const ZUs=[-.2,.5,-5.2],BINs=[.95,.5,-3.85],BOs=[-1.35,.5,-3.95];
  if(t>=X.e1&&t<X.day2){Object.assign(z,{pos:ZUs,rot:Math.PI*.0+.05,anim:'idle',p:t,eyes:t<X.f1+.2?'glow':'normal',mouth:mouthOf('zu',t,'closed'),glow:t<X.f1+.2?.8:0});
    Object.assign(b,{pos:BINs,rot:face(BINs,ZUs),anim:'idle',p:t,eyes:'normal',mouth:mouthOf('bin',t,'frown')});
    Object.assign(o,{pos:BOs,rot:face(BOs,ZUs),anim:speaking('bo',t)?'talk':'idle',p:t,eyes:'normal',mouth:mouthOf('bo',t,'closed')});
    if(t>=X.f1&&t<X.f2){b.eyes='sad';o.eyes='sad';b.look=[-.9,0];o.look=[.9,0]}
    if(t>=X.g1){o.rot=face(BOs,[.2,.5,-6.6]);o.eyes='angry';ov2.rules=t-X.g1}}
  // ---- day 2: the crunch ----
  if(t>=X.day2&&t<X.day3){const ZUa=[-6.5,.5,-12.5],ZUb=[-6.4,.5,-7.6];
    const u=clamp((t-X.h0+.4)/1.6);const zp=vl(ZUa,ZUb,ease(u)).toArray();
    Object.assign(z,{pos:zp,rot:u<1?0:Math.PI/2,anim:u<1?'sneak':(t<X.crunch-.35?'grab':'hold'),p:t,eyes:t<X.crunch?'sly':'wide',mouth:t<X.crunch?'smile':'O',hold:t>X.crunch-.35?'chips':null,glow:0});
    Object.assign(b,{pos:[-4.4,.5,-4.2],rot:-2.3,anim:'idle',p:t,eyes:'closed',mouth:'closed'});
    Object.assign(o,{pos:[1.5,.5,-9.5],rot:0,sit:true,anim:'idle',p:t,eyes:'closed',mouth:'closed'});
    if(t>=X.j0-.4){const v=ease((t-X.j0+.4)/.6);b.pos=[lerp(-4.4,-5.5,v),.5,lerp(-4.2,-5.6,v)];b.rot=face(b.pos,ZUb);b.anim=v<1?'run':'shush';b.eyes='angry';b.mouth=mouthOf('bin',t,'O');
      z.rot=face(ZUb,b.pos);z.anim='hold'}
    if(t>=X.j1){z.eyes='sad';z.mouth=mouthOf('zu',t,'frown');b.anim='idle';b.eyes='scared';b.look=[.8,0];b.mouth='frown'}
    if(t>X.crunch&&t<X.crunch+.7)ov2.crunch=t-X.crunch}
  // ---- day 3: someone at the glass ----
  if(t>=X.day3){const ZUk=[3.1,.5,-7.3],BINk=[2.3,.5,-6.6],BOk=[4.1,.5,-6.8];const up=t>X.k1-.3;
    Object.assign(z,{pos:ZUk,rot:0,sit:!up,anim:up?'idle':'idle',p:t,eyes:t<X.knock?'closed':'wide',mouth:'closed',glow:0});
    Object.assign(b,{pos:BINk,rot:.25,sit:!up,anim:'idle',p:t,eyes:t<X.knock?'closed':'wide',mouth:mouthOf('bin',t,'O')});
    Object.assign(o,{pos:BOk,rot:-.15,sit:!up,anim:'idle',p:t,eyes:t<X.knock?'closed':'scared',mouth:mouthOf('bo',t,'O')});
    if(t>X.knock&&!up){b.look=[.5,.1];o.look=[.4,.1];z.look=[.5,.1]}
    if(t>=X.l0&&t<X.n0){z.eyes='wide';z.mouth=mouthOf('zu',t,'O');z.anim=speaking('zu',t)?'point':'idle'}
    if(t>=X.m0){o.anim=speaking('bo',t)?'talk':'idle';o.eyes='scared'}
    if(t>=X.n0){const ZUg=[5.75,.5,-1.12];const v=ease(clamp((t-X.n0-.5)/2.4));z.pos=vl(ZUk,ZUg,v).toArray();z.rot=face(ZUk,ZUg)*(1-v);z.anim=v>0&&v<1?'walk':'idle';z.eyes='hope';z.mouth=mouthOf('zu',t,'closed');
      b.rot=face(BINk,z.pos);b.eyes='sad';b.mouth=mouthOf('bin',t,'frown');b.anim=speaking('bin',t)?'talk':'idle';o.rot=face(BOk,z.pos);o.eyes='sad'}
    if(t>=X.o0){z.pos=[5.75,.5,-1.12];z.rot=0;z.anim=t>X.o0+.5?'glass':'idle';z.eyes=speaking('zu',t)?'sad':'hope';z.mouth=mouthOf('zu',t,'closed');z.tears=t>E('home')-.3}
    // the stranger
    const DOg=[5.9,.5,1.16];Object.assign(d,{visible:t>X.knock-.8,pos:DOg,rot:Math.PI,anim:'idle',p:t*.6,eyes:'glow',mouth:'closed',glow:1.1,hold:null});
    if(t>X.knock-.8&&t<X.knock+.7){d.anim='bang';d.p=t*.5}
    if(t>=X.k1-.2&&t<X.o0+.5){d.anim='raise';d.hold='bunny'}
    if(t>=X.o0+.5){d.anim='glass';d.hold=null}
    if(t>=X.p0){d.anim='idle'}}

  /* ---------- cameras ---------- */
  if(t<X.a1){ // HOOK: high wide of the dead street, the horde coming, the store alarm
    const u=t/X.a1;cam(V3(lerp(13,11,u),lerp(10,8,u),lerp(11.5,11,u)),V3(lerp(-6,-4,u),1.2,lerp(4,3,u)),50);
  } else if(t<X.b1){ // ground level: feet of the horde shuffle past
    const u=(t-X.a1)/(X.b1-X.a1);cam(V3(lerp(-6.5,-5.5,u),.75,10.6),V3(-12,1.3,7.2),52);
  } else if(t<X.c1){ // tracking: the three of them sprint for the store
    const x=b.pos[0];cam(V3(Math.max(x-4.2,.8),1.45,1.25),V3(Math.max(x,5)+1.2,1.25,2.6),52);
  } else if(t<X.d1){ // inside, looking out the open door: in, then Bin pulls it down
    const k=t>X.tClose&&t<X.tClose+.5?shake(t,.07):V3(0,0,0);cam(V3(-1.6,1.7,-6.2).add(k),V3(.4,1.6,1.4),52);
  } else if(t<X.e1){ // wide from the back of the store: silhouettes banging on the glass
    const u=(t-X.d1)/(X.e1-X.d1);cam(V3(lerp(2.6,1.6,u),2.3,lerp(-11.5,-10.6,u)),V3(0,1.5,-1),48);
  } else if(t<X.f1){ // Zu, close: glowing eyes, "I'm hungry"
    const u=(t-X.e1)/(X.f1-X.e1);cam(V3(.15,1.8,lerp(-3.5,-3.8,u)),V3(-.2,1.72,-5.2),34);
  } else if(t<X.f2){ // Bin & Bo look at each other over Zu's head
    cam(V3(-.15,1.05,-7.1),V3(-.2,1.55,-3.9),44);
  } else if(t<X.g1){ // Bo: "Okay. New rules."
    cam(V3(-.35,1.65,-6.7),V3(-1.35,1.65,-3.95),40);
  } else if(t<X.day2){ // push in on Bo as the rules land
    const u=(t-X.g1)/(X.day2-X.g1);cam(V3(lerp(-.6,-.85,u),1.85,lerp(-6.5,-5.9,u)),V3(-1.35,1.8,-3.95),lerp(42,37,u));
  } else if(t<X.h0){ // DAY 2 card over the store at dawn
    const u=(t-X.day2)/(X.h0-X.day2);cam(V3(lerp(9,7,u),3.2,16),V3(0,3,0),44);
  } else if(t<X.i0){ // the aisle: Zu sneaks to the snacks
    const k=t>X.crunch&&t<X.crunch+.3?shake(t,.04):V3(0,0,0);const zoom=t>X.crunch?lerp(46,36,eout((t-X.crunch)/.2)):46;cam(V3(-6.4,1.5,-4.4).add(k),V3(-6.4,1.55,-9),zoom);
  } else if(t<X.j0){ // outside: every head turns to the store
    const u=(t-X.i0)/(X.j0-X.i0);cam(V3(-4,1.25,lerp(12.6,12.2,u)),V3(-5.5,1.6,0),44);
  } else if(t<X.j1){ // Bin: "Zu! Shhh!" — hands hit the glass behind
    cam(V3(-6.7,1.75,-11.4),V3(-5.8,1.35,-3),46);
  } else if(t<X.day3){ // Zu, sorry
    cam(V3(-5.75,1.75,-5.9),V3(-6.4,1.65,-7.6),38);
  } else if(t<X.k0){ // DAY 3 card over the store in the rain
    const u=(t-X.day3)/(X.k0-X.day3);cam(V3(lerp(-7,-5,u),2.8,15),V3(2,2.4,0),44);
  } else if(t<X.k1){ // asleep on the floor... knock, knock
    const u=(t-X.k0)/(X.k1-X.k0);cam(V3(lerp(-.6,-.2,u),1.7,-9.6),V3(5,1.1,-1),44);
  } else if(t<X.l0){ // through the glass: a stranger holding Zu's bunny
    const u=(t-X.k1)/(X.l0-X.k1);cam(V3(lerp(4.4,4.9,u),1.3,lerp(-5.6,-4.4,u)),V3(5.9,1.75,1.2),lerp(40,30,u));
  } else if(t<X.m0){ // Zu: "That's my bunny!"
    cam(V3(3.0,1.75,-5.6),V3(3.1,1.62,-7.3),38);
  } else if(t<X.n0){ // Bin and Bo
    cam(V3(3.0,1.55,-3.9),V3(3.2,1.45,-6.7),40);
  } else if(t<X.o0){ // over Bin's shoulder: Zu walks to the glass
    cam(V3(1.6,1.95,-8.4),V3(5.4,1.15,-1.6),40);
  } else if(t<X.p0){ // the two hands on the glass
    const u=(t-X.o0)/(X.p0-X.o0);cam(V3(lerp(8.9,8.3,u),1.35,lerp(-2.6,-2.0,u)),V3(5.85,1.35,0),lerp(42,34,u));
  } else { // pull out into the rain: he is not alone
    const u=ease(clamp((t-X.p0)/4.5));cam(V3(lerp(7.5,2.5,u),lerp(1.8,5.8,u),lerp(5.5,12,u)),V3(lerp(5.9,3,u),lerp(1.8,2.2,u),0),48);
    ov2.end=clamp((t-S('end')+.2)/.4);ov2.fade=clamp((t-(TL.total-1.0))/.8);
  }
  pose(BIN,b);pose(BO,o);pose(ZU,z);pose(ODD,d);
  renderer.render(scene,camera);
  ov2.X=X;drawOverlay(t,ov2);
}

/* ---------- overlay ---------- */
function dayOf(t,X){return t<X.day2?1:t<X.day3?2:3}
function drawOverlay(t,o){
  const g=ov;g.clearRect(0,0,W,H);g.textBaseline='alphabetic';const X=o.X;
  const vg=g.createRadialGradient(W/2,H/2,H*.38,W/2,H/2,H*1.0);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,.55)');g.fillStyle=vg;g.fillRect(0,0,W,H);
  // HUD: clock in the cold open, then the day counter
  if(t<X.c1+1){const a=clamp(t/.3)*clamp((X.c1+1-t)/.4);g.globalAlpha=a;rr(g,60,52,330,74,14);g.fillStyle='rgba(0,0,0,.55)';g.fill();g.fillStyle=Math.sin(t*6)>0?'#FF3B30':'#7a1a16';g.beginPath();g.arc(100,89,14,0,7);g.fill();
    g.font='800 50px Kid';g.textAlign='left';g.fillStyle='#fff';g.fillText('9:00 PM'.slice(0,Math.ceil(clamp((t-.3)/.8)*7)),130,107);g.globalAlpha=1}
  const card=t>=X.day2&&t<X.h0?['2',(t-X.day2)/(X.h0-X.day2)]:t>=X.day3&&t<X.k0?['3',(t-X.day3)/(X.k0-X.day3)]:null;
  if(t>X.g2-.2||card){const n=card?+card[0]:dayOf(t,X);rr(g,60,52,300,74,14);g.fillStyle='rgba(0,0,0,.55)';g.fill();g.font='800 50px Kid';g.textAlign='left';outlined(g,'DAY '+n,88,108,50,'#FFE600','#000',10);
    g.font='800 40px Kid';g.fillStyle='#ccc';g.fillText('/ 30',236,106)}
  if(card){const [n,u]=card;const a=clamp(u/.15)*clamp((1-u)/.18);g.globalAlpha=a*.78;g.fillStyle='#000';g.fillRect(0,0,W,H);g.globalAlpha=a;
    const k=1+(1-eout(u/.3))*.25;g.save();g.translate(W/2,H/2+40);g.scale(k,k);g.textAlign='center';outlined(g,'DAY '+n,0,0,250,'#FFFFFF','#000',30);g.restore();
    g.fillStyle='#333';g.fillRect(W/2-450,H/2+120,900,26);g.fillStyle='#E53935';g.fillRect(W/2-450,H/2+120,900*((+n-1)+eout(u*1.4))/30,26);g.lineWidth=5;g.strokeStyle='#000';g.strokeRect(W/2-450,H/2+120,900,26);
    g.font='800 46px Kid';g.textAlign='center';g.fillStyle='#ddd';g.fillText((30-+n)+' DAYS TO GO',W/2,H/2+210);g.globalAlpha=1}
  // the rules board
  if(o.rules!==undefined){const bt=B('thirty');const fr=[0,.31,.55];const rows=['1. SURVIVE 30 DAYS','2. NO NOISE','3. NOBODY SEES ZU'];const a=clamp(o.rules/.25);
    g.globalAlpha=a;rr(g,W-760,150,690,330,24);g.fillStyle='rgba(12,12,16,.78)';g.fill();g.lineWidth=6;g.strokeStyle='#E53935';g.stroke();
    g.textAlign='left';outlined(g,'THE RULES',W-720,226,64,'#E53935','#000',10);
    rows.forEach((r,i)=>{const ti=bt.start+bt.dur*fr[i]-.05;const age=t-ti;if(age<0)return;const k=age<.12?1.5-age/.12*.5:1;g.save();g.translate(W-720,310+i*72);g.scale(k,k);outlined(g,r,0,0,52,i==2?'#7CFF4F':'#FFFFFF','#000',10);g.restore()});
    g.globalAlpha=1}
  // captions (word pop), not for the day cards / end
  const bt=lineAt(t);
  if(bt&&!['day2','day3','end'].includes(bt.id)){
    const cap=bt.cap||bt.text;const words=cap.split(' ');const lens=words.map(w=>w.length+1);const tot=lens.reduce((a,c)=>a+c,0);
    let acc=0;const times=lens.map(l=>{const s=bt.start+bt.dur*acc/tot;acc+=l;return s-.06});
    const size=80;g.font=`800 ${size}px Kid`;const sp=g.measureText(' ').width+26;
    const lines=[[]];let lw=0;words.forEach((w,i)=>{const ww=g.measureText(w).width;if(lw+ww>1450&&lines[lines.length-1].length){lines.push([]);lw=0}lines[lines.length-1].push(i);lw+=ww+sp});
    const baseY=H-70-(lines.length-1)*92;
    lines.forEach((ln,li)=>{const widths=ln.map(i=>g.measureText(words[i]).width);const total=widths.reduce((a,c)=>a+c,0)+sp*(ln.length-1);let x=W/2-total/2;const y=baseY+li*92;
      ln.forEach((i,k)=>{const age=t-times[i];if(age>=0){const pop=age<.12?1.35-age/.12*.35:1;const cur=(i==words.length-1?t<bt.start+bt.dur:t<times[i+1]);g.save();g.translate(x+widths[k]/2,y);const k2=pop*(cur?1.08:1);g.scale(k2,k2);g.textAlign='center';
        const hot=/^[A-Z0-9!.]+$/.test(words[i].replace(/[^A-Za-z0-9!.]/g,''))&&words[i].length>2;outlined(g,words[i],0,0,size,hot?'#FF5A3C':'#FFFFFF','#000',16);g.restore()}x+=widths[k]+sp})});
    if(CHIP[bt.who]){const [n,c]=CHIP[bt.who];g.font='800 42px Kid';const w=g.measureText(n).width+44;const y=baseY-size-50;rr(g,W/2-w/2,y,w,56,16);g.fillStyle=c;g.fill();g.lineWidth=6;g.strokeStyle='#000';g.stroke();g.textAlign='center';g.fillStyle='#fff';g.fillText(n,W/2,y+44)}
    g.textAlign='left'}
  // sound words
  const pop=(txt,x,y,age,col,size=130,rot=-.1)=>{if(age<0||age>.7)return;const k=age<.08?age/.08*1.3:1.1-age*.1;g.save();g.globalAlpha=clamp((.7-age)/.2);g.translate(x,y);g.rotate(rot);g.scale(k,k);g.textAlign='center';outlined(g,txt,0,0,size,col,'#000',size*.18);g.restore();g.globalAlpha=1};
  if(t>X.tClose-.05&&t<X.tClose+.7)pop('SLAM!',W*.5,H*.36,t-X.tClose,'#FFE600',170);
  if(t>X.d1&&t<X.e1){[X.d1+.25,X.d1+.95,X.d1+1.9].forEach((b,i)=>pop('BANG!',[W*.26,W*.74,W*.4][i],[H*.3,H*.26,H*.36][i],t-b,'#FF5A3C',120,i%2?.12:-.12))}
  if(o.crunch!==undefined)pop('CRUNCH!',W*.62,H*.3,o.crunch,'#FFB300',170,.08);
  if(t>X.j0&&t<X.j1){[X.j0+.35,X.j0+.9].forEach((b,i)=>pop('BANG!',[W*.2,W*.34][i],H*.3,t-b,'#FF5A3C',110,-.1))}
  if(t>X.knock-.05&&t<X.knock+1.2){pop('knock',W*.72,H*.3,t-X.knock,'#FFFFFF',90,-.08);pop('knock',W*.8,H*.4,t-X.knock-.4,'#FFFFFF',90,.08)}
  if(o.end){const a=o.end;g.save();g.globalAlpha=a;g.fillStyle='rgba(0,0,0,.45)';g.fillRect(0,0,W,260);
    g.textAlign='center';outlined(g,'DAY 4: SOMEONE WANTS ZU BACK...',W/2,170,96,'#FFFFFF','#000',20);g.restore();
    g.save();g.globalAlpha=a;const bx=W-460,by=320;const pressed=(t%2)>1.55&&(t%2)<1.75;rr(g,bx,by+(pressed?6:0),390,110,55);g.fillStyle=pressed?'#9e9e9e':'#E53935';g.fill();g.lineWidth=8;g.strokeStyle='#000';g.stroke();
    g.textAlign='center';g.font='800 60px Kid';g.fillStyle='#fff';g.fillText(pressed?'SUBSCRIBED':'SUBSCRIBE',bx+195,by+76+(pressed?6:0));g.restore()}
  if(o.fade){g.globalAlpha=o.fade;g.fillStyle='#000';g.fillRect(0,0,W,H);g.globalAlpha=1}
}

window.renderThumb=()=>{
  const X=SH();renderAt(X.e1+1.5);
  pose(ZU,{pos:[-.2,.5,-5.2],rot:0,anim:'idle',p:0,eyes:'glow',mouth:'grin',glow:1.2});
  pose(BIN,{pos:[1.3,.5,-5.6],rot:-.6,anim:'yell',p:0,eyes:'scared',mouth:'open'});
  pose(BO,{pos:[-1.7,.5,-5.7],rot:.6,anim:'cower',p:0,eyes:'scared',mouth:'O'});
  cam(V3(-.1,1.45,-8.6),V3(-.2,1.5,-3),46);
  renderer.render(scene,camera);
  const g=ov;g.clearRect(0,0,W,H);g.textAlign='center';
  g.save();g.translate(W*.5,170);g.rotate(-.02);outlined(g,'OUR BROTHER IS A ZOMBIE',0,0,124,'#FFE600','#000',28);g.restore();
  g.save();g.translate(W*.5,H-60);outlined(g,'30 DAYS LOCKED IN',0,0,96,'#FFFFFF','#000',22);g.restore();
};
/* ---------- init ---------- */
window.init=async()=>{
  TL=await (await fetch('timeline.json')).json();
  B=id=>TL.beats.find(b=>b.id===id);S=id=>B(id).start;E=id=>B(id).start+B(id).dur;
  await document.fonts.load('800 80px Kid','ZOMBIE OUTBREAK');await document.fonts.ready;drawSign();
  scene.traverse(m=>{if(m.isMesh&&m.material===MAT.glass){m.castShadow=false;m.renderOrder=2}});
  renderAt(0);return TL.total};
window.renderAt=renderAt;
</script>
</body></html>
