/* ---------- characters ---------- */
const CH={};
function makeChar(name,o){
  const ch={name,o,root:new THREE.Group(),state:''};
  const lam=t=>new THREE.MeshLambertMaterial({map:t});
  const face=tex(16,16,()=>{});ch.face=face;
  const hairT=tex(16,16,p=>{p(0,0,o.hair,16,16);const r=rng(o.seed);for(let i=0;i<20;i++)p(r()*16|0,r()*16|0,shade(o.hair,.85))});
  const sideT=tex(16,16,p=>{p(0,0,o.skin,16,16);p(0,0,o.hair,16,5);p(0,5,o.hair,3,4);p(13,5,o.hair,3,4)});
  const head=new THREE.Mesh(new THREE.BoxGeometry(.5,.5,.5),[lam(sideT),lam(sideT),lam(hairT),lam(tex(2,2,p=>p(0,0,o.skin,2,2))),lam(face),lam(hairT)]);
  const hs=o.headScale||1;head.scale.setScalar(hs);head.position.y=.25*hs;head.castShadow=true;
  const neck=new THREE.Group();neck.position.y=1.5;neck.add(head);
  if(o.spikes){const sm=lam(hairT);[[-.17,.55,0,.16],[0,.6,.05,.2],[.17,.55,-.02,.16],[-.08,.56,-.15,.15],[.1,.57,.14,.14]].forEach(([x,y,z,s])=>{const b=new THREE.Mesh(new THREE.BoxGeometry(s,s,s),sm);b.position.set(x,y,z);b.rotation.set(.3*x*5,0,.4*x*4);b.castShadow=true;neck.add(b)})}
  const shirtF=tex(8,12,p=>{p(0,0,o.shirt,8,12);o.shirtDeco&&o.shirtDeco(p)});
  const shirtS=tex(4,12,p=>{p(0,0,o.shirt,4,12);p(0,10,o.belt||shade(o.shirt,.8),4,2)});
  const shirtB=tex(8,12,p=>{p(0,0,shade(o.shirt,.92),8,12);p(0,10,o.belt||shade(o.shirt,.8),8,2)});
  const body=new THREE.Mesh(new THREE.BoxGeometry(.5,.75,.25),[lam(shirtS),lam(shirtS),lam(tex(2,2,p=>p(0,0,o.shirt,2,2))),lam(shirtS),lam(shirtF),lam(shirtB)]);
  body.position.y=1.125;body.castShadow=true;
  const armT=tex(4,12,p=>{p(0,0,o.sleeve||o.shirt,4,o.short?4:9);p(0,o.short?4:9,o.skin,4,o.short?8:3)});
  const legT=tex(4,12,p=>{p(0,0,o.pants,4,o.shorts?5:10);if(o.shorts)p(0,5,o.skin,4,5);p(0,10,o.shoe,4,2);p(0,11,o.sole||'#eee',4,1)});
  const mk=(t,isArm,x)=>{const piv=new THREE.Group();const m=new THREE.Mesh(new THREE.BoxGeometry(.25,.75,.25),lam(t));m.position.y=-.32;m.castShadow=true;piv.add(m);piv.position.set(x,isArm?1.45:.75,0);return piv};
  ch.armL=mk(armT,1,.375);ch.armR=mk(armT,1,-.375);ch.legL=mk(legT,0,.125);ch.legR=mk(legT,0,-.125);
  ch.body=new THREE.Group();ch.body.add(body,neck,ch.armL,ch.armR);
  ch.root.add(ch.body,ch.legL,ch.legR);ch.neck=neck;ch.head=head;
  // tears (children of the head, so they follow it)
  const tm=new THREE.MeshBasicMaterial({color:0x7FD3FF});ch.tears=[];
  for(let i=0;i<10;i++){const t=new THREE.Mesh(new THREE.BoxGeometry(.05,.08,.03),tm);t.visible=false;head.add(t);ch.tears.push(t)}
  // hand socket with props
  ch.hand=new THREE.Group();ch.hand.position.set(0,-.68,.02);ch.armR.add(ch.hand);
  const chipT=tex(8,10,p=>{p(0,0,'#E53935',8,10);p(0,0,'#B71C1C',8,1);p(0,9,'#B71C1C',8,1);p(1,3,'#FFEB3B',6,3);p(2,4,'#FB8C00',4,1)});const chips=new THREE.Mesh(new THREE.BoxGeometry(.26,.34,.1),new THREE.MeshLambertMaterial({map:chipT}));chips.position.set(0,-.1,.1);
  const bunny=new THREE.Group();{const w=new THREE.MeshLambertMaterial({map:noiseTex('#EEEAE4',.12,91)}),pk=new THREE.MeshLambertMaterial({color:0xF48FB1}),ey=new THREE.MeshBasicMaterial({color:0x111111});const bb=new THREE.Mesh(new THREE.BoxGeometry(.26,.24,.2),w);const bh=new THREE.Mesh(new THREE.BoxGeometry(.22,.2,.2),w);bh.position.y=.2;[-.06,.06].forEach(x=>{const e=new THREE.Mesh(new THREE.BoxGeometry(.06,.18,.04),w);e.position.set(x,.38,0);const ei=new THREE.Mesh(new THREE.BoxGeometry(.03,.12,.01),pk);ei.position.set(x,.38,.025);const d=new THREE.Mesh(new THREE.BoxGeometry(.035,.035,.01),ey);d.position.set(x,.22,.105);bunny.add(e,ei,d)});bunny.add(bb,bh);bunny.position.set(0,-.12,.12)}
  ch.props={chips,bunny};Object.values(ch.props).forEach(m=>{m.visible=false;m.traverse(x=>x.castShadow=true);ch.hand.add(m)});
  ch.root.scale.setScalar(o.scale||1);
  ch.mats=[];ch.root.traverse(m=>{if(m.isMesh&&!ch.tears.includes(m)){(Array.isArray(m.material)?m.material:[m.material]).forEach(mm=>ch.mats.push(mm))}});
  scene.add(ch.root);CH[name]=ch;return ch}
const BIN=makeChar('bin',{seed:3,skin:'#F4C9A0',hair:'#C6862A',spikes:true,shirt:'#FF8A1F',sleeve:'#FF8A1F',pants:'#6B4423',shorts:true,shoe:'#E53935',belt:'#E57212',
  shirtDeco:p=>{p(3,2,'#FFE14D',2,1);p(2,3,'#FFE14D',4,1);p(1,4,'#FFE14D',6,1);p(2,5,'#FFE14D',4,1);p(2,6,'#FFE14D',1,1);p(5,6,'#FFE14D',1,1);p(1,0,'#fff',1,3);p(6,0,'#fff',1,3);p(1,8,'#E57212',6,2)},freckles:true});
const BO=makeChar('bo',{seed:5,skin:'#E3AE84',hair:'#1F1A2B',shirt:'#6B4BD6',sleeve:'#6B4BD6',pants:'#3A3F4B',shoe:'#222',sole:'#ddd',belt:'#2B2F38',
  shirtDeco:p=>{p(2,0,'#fff',4,1);p(3,1,'#fff',2,1);p(3.5,1,'#F2C94C',1,4);p(1,6,'#5A3EC0',2,2)},glasses:true});
const ZU=makeChar('zu',{seed:9,skin:'#6DBE5A',hair:'#2F6B25',shirt:'#2BB3C0',short:true,pants:'#4B4FC2',shoe:'#3A3A3A',sole:'#555',belt:'#1E8C96',headScale:1.25,scale:.72,zombie:true,
  shirtDeco:p=>{p(1,8,'#6DBE5A',2,2);p(5,6,'#6DBE5A',2,1);p(6,9,'#1E8C96',2,1);p(0,11,'#6DBE5A',1,1);p(3,11,'#6DBE5A',2,1)}});

const ODD=makeChar('odd',{seed:13,skin:'#7E9C7A',hair:'#2E3A2C',shirt:'#3C414C',sleeve:'#3C414C',pants:'#23262D',shoe:'#1A1A1A',sole:'#333',belt:'#2B2F38',zombie:true,glowC:'#FFB300',scale:1.08,
  shirtDeco:p=>{p(2,0,'#2B2F38',4,2);p(3,2,'#2B2F38',2,1);p(1,7,'#2B2F38',6,3);p(0,4,'#7E9C7A',1,2);p(6,9,'#7E9C7A',2,1)}});
// faint eye light so the zombies' glowing eyes actually light their faces
[[ZU,0x7CFF4F],[ODD,0xFFB300]].forEach(([c,col])=>{const l=new THREE.PointLight(col,0,2.2,2);l.position.set(0,.3,.6);c.head.add(l);c.glowL=l;
  const gm=new THREE.MeshBasicMaterial({color:col});c.glowEyes=[-.094,.094].map(x=>{const m=new THREE.Mesh(new THREE.BoxGeometry(.066,.066,.01),gm);m.position.set(x,.031,.254);m.visible=false;c.head.add(m);return m})});
function drawFace(ch,eyes,mouth,mood){
  const key=eyes+mouth+mood;if(ch.state===key)return;ch.state=key;const o=ch.o;const f=ch.face;const g=f.g,p=f.p;
  g.clearRect(0,0,64,64);p(0,0,o.skin,16,16);
  if(o.spikes){p(0,0,o.hair,16,3);[0,3,6,9,12].forEach((x,i)=>p(x+1,3,o.hair,2,i%2?2:1));p(0,3,o.hair,1,3);p(15,3,o.hair,1,3)}
  else if(o.zombie){p(0,0,o.hair,16,2);p(0,2,o.hair,5,1);p(11,2,o.hair,5,1);p(2,9,shade(o.skin,.8),3,1);p(11,9,shade(o.skin,.8),3,1)}
  else{p(0,0,o.hair,16,3);p(0,3,o.hair,10,1);p(0,3,o.hair,2,3);p(14,3,o.hair,2,3)}
  const ex=[3,9],ey=5;const white='#fff',ink='#1b1b1b',tear='#6EC6FF';
  for(const x of ex){const inner=x<8?2:0;
    if(eyes=='normal'){p(x,ey,white,4,4);p(x+inner,ey+1,ink,2,3);p(x+inner,ey+1,'#3b6fd9',1,1)}
    else if(eyes=='wide'){p(x,ey-1,white,4,5);p(x+1,ey+1,ink,2,2)}
    else if(eyes=='happy'){p(x,ey+2,ink,1,1);p(x+1,ey+1,ink,2,1);p(x+3,ey+2,ink,1,1)}
    else if(eyes=='closed'){p(x,ey+2,ink,4,1)}
    else if(eyes=='angry'){p(x,ey+1,white,4,3);p(x+1,ey+2,ink,2,2);p(x,ey,ink,4,1);x<8?p(x+2,ey+1,ink,2,1):p(x,ey+1,ink,2,1)}
    else if(eyes=='sly'){p(x,ey+1,white,4,2);p(x+inner,ey+1,ink,2,2);p(x,ey,ink,4,1)}
    else if(eyes=='star'){p(x+1,ey,'#FFD600',2,4);p(x,ey+1,'#FFD600',4,2)}
    else if(eyes=='sad'){p(x,ey,white,4,4);p(x+1,ey+2,ink,2,2);x<8?(p(x,ey-1,ink,2,1),p(x+2,ey-2,ink,2,1)):(p(x+2,ey-1,ink,2,1),p(x,ey-2,ink,2,1))}
    else if(eyes=='cry'){p(x,ey+1,ink,1,1);p(x+1,ey+2,ink,2,1);p(x+3,ey+1,ink,1,1);p(x+1,ey+3,tear,2,4)}
    else if(eyes=='glow'){const gc=o.glowC||'#7CFF4F';p(x,ey,'#0b0b0b',4,4);p(x+(x<8?1:1),ey+1,gc,2,2);p(x+1,ey+1,'#ffffff',1,1)}
    else if(eyes=='scared'){p(x,ey-1,white,4,5);p(x+1,ey+1,ink,2,2);x<8?p(x,ey-2,ink,3,1):p(x+1,ey-2,ink,3,1)}
    else if(eyes=='hope'){p(x,ey,white,4,4);p(x+1,ey,ink,2,3);p(x+1,ey,'#fff',1,1);p(x+1,ey+3,tear,2,1)}
  }
  if(o.glasses){const gc='#111';for(const x of ex){p(x-1,ey-1,gc,6,1);p(x-1,ey+4,gc,6,1);p(x-1,ey-1,gc,1,6);p(x+4,ey-1,gc,1,6)}p(7,ey+1,gc,2,1)}
  if(o.freckles){p(2,11,'#D9895B');p(4,11,'#D9895B');p(11,11,'#D9895B');p(13,11,'#D9895B')}
  p(2,10,'rgba(255,120,120,.35)',2,1);p(12,10,'rgba(255,120,120,.35)',2,1);
  const mx=6,my=12;const dk='#4a1414',ln='#7a3b2e';
  if(mouth=='closed')p(mx,my,ln,4,1);
  else if(mouth=='open'){p(mx-1,my-1,dk,6,3);p(mx,my+1,'#E35D6A',4,1);p(mx-1,my-1,'#fff',6,1)}
  else if(mouth=='half'){p(mx,my-1,dk,4,2);p(mx,my-1,'#fff',4,1)}
  else if(mouth=='smile'){p(mx-1,my-1,ln,1,1);p(mx,my,ln,4,1);p(mx+4,my-1,ln,1,1)}
  else if(mouth=='grin'){p(mx-2,my-1,dk,8,3);p(mx-2,my-1,'#fff',8,1);p(mx-1,my+1,'#E35D6A',6,1)}
  else if(mouth=='O'){p(mx,my-1,dk,3,3);p(mx+1,my,'#E35D6A',1,1)}
  else if(mouth=='frown'){p(mx-1,my+1,ln,1,1);p(mx,my,ln,4,1);p(mx+4,my+1,ln,1,1)}
  else if(mouth=='wail'){p(mx-2,my-1,dk,8,3);p(mx-1,my+1,'#E35D6A',6,1);p(mx-3,my+1,ln,1,1);p(mx+6,my+1,ln,1,1)}
  else if(mouth=='chew'){p(mx-1,my-1,dk,5,2);p(mx,my,'#E53935',2,1)}
  f.needsUpdate=true}

// pose: {pos,rot,anim,p,eyes,mouth,look:[yaw,pitch],sit,hold,bite,tears,k}
function pose(ch,s){
  const r=ch.root;r.visible=s.visible!==false;if(!r.visible)return;
  const sc=ch.o.scale||1;
  r.position.set(s.pos[0],s.pos[1]-(s.sit?.6*sc:0),s.pos[2]);r.rotation.set(0,s.rot||0,0);
  const p=s.p||0,a=s.anim||'idle';
  let aL=0,aR=0,lL=0,lR=0,aLz=0,aRz=0,bob=0,lean=s.lean||0,hy=0,hp=0;
  if(a=='idle'){aL=Math.sin(p*2)*.05;aR=-aL;bob=Math.sin(p*2.4)*.01}
  if(a=='talk'){aL=-.25+Math.sin(p*5)*.18;aR=-.35-Math.sin(p*4.3)*.25;aLz=.15;aRz=-.15;bob=Math.abs(Math.sin(p*5))*.02}
  if(a=='walk'){const w=Math.sin(p*9);lL=w*.6;lR=-w*.6;aL=-w*.55;aR=w*.55;bob=Math.abs(Math.cos(p*9))*.06}
  if(a=='run'){const w=Math.sin(p*14);lL=w*1;lR=-w*1;aL=-w*.9;aR=w*.9;bob=Math.abs(Math.cos(p*14))*.1;lean+=.18}
  if(a=='point'){aR=-1.55+Math.sin(p*6)*.08;aL=Math.sin(p*3)*.08;bob=Math.abs(Math.sin(p*7))*.04}
  if(a=='yell'){aL=-1.5;aR=-1.5;aLz=.5;aRz=-.5;lean+=-.08}
  if(a=='cheer'){aL=-2.9+Math.sin(p*14)*.25;aR=-2.9-Math.sin(p*14)*.25;aLz=.25;aRz=-.25;bob=Math.abs(Math.sin(p*7))*.55;lL=-bob*.6;lR=-bob*.6}
  if(a=='hug'){aL=-1.25;aR=-1.25;aLz=-.35;aRz=.35;bob=Math.abs(Math.sin(p*4))*.02}
  if(a=='fall'){aL=-2.6;aR=-2.6;aLz=.6;aRz=-.6;lL=-.3;lR=.4}
  if(a=='nod'){hp=Math.max(0,Math.sin(p*9))*.35}
  if(a=='sitcry'){const sw=Math.sin(p*4.5)>0;const rub=Math.sin(p*16)*.12;aL=sw?-2.35+rub:-.35;aR=sw?-.35:-2.35+rub;aLz=sw?-.32:.1;aRz=sw?-.1:.32;hp=-.05;bob=Math.abs(Math.sin(p*13))*.025}
  if(a=='cower'){aL=-1.45;aR=-1.45;aLz=-.62;aRz=.62;lean+=-.14;hp=.12;hy=Math.sin(p*31)*.05}
  if(a=='give'){aR=-1.45;aL=.05;lean+=.06}
  if(a=='eat'){aL=-.35;aR=-1.72+Math.sin(p*14)*.08;aLz=.1;aRz=.5;hp=-.05;bob=Math.abs(Math.sin(p*12))*.02}
  if(a=='kick'){const k=s.k||0;lR=-Math.sin(clamp(k)*Math.PI)*1.4;aL=-Math.sin(clamp(k)*Math.PI)*.8;aR=Math.sin(clamp(k)*Math.PI)*.6;lean+=-.1*Math.sin(clamp(k)*Math.PI)}
  if(a=='place'){const w=Math.max(0,Math.sin(p*7));aR=-1.2-w*.9;aL=-.4;lean+=.12;bob=w*.02}
  if(a=='carry'){aR=-1.1;aL=-1.1;aLz=-.2;aRz=.2}
  if(a=='hopouch'){bob=Math.abs(Math.sin(p*8))*.32;lR=-1.0;lL=.05;aL=-.6;aR=-.6;aLz=.4;aRz=-.4;lean+=.25;hy=Math.sin(p*8)*.15}
  if(a=='facepalm'){aR=-2.55;aRz=.55;aL=.05;hp=.22}
  if(a=='present'){aL=-1.25;aR=-1.25;aLz=.95;aRz=-.95;bob=Math.abs(Math.sin(p*5))*.03}
  if(a=='ideaup'){aR=-2.95;aL=-.25;bob=Math.abs(Math.sin(p*9))*.06}
  if(a=='sad'){aL=.06;aR=-.06;hp=.32;lean+=.08}
  if(a=='lookup'){hp=-.3;aL=-.2;aR=-.2}
  if(a=='shamble'){const w=Math.sin(p*5);lL=w*.45;lR=-w*.45;aL=-1.45+Math.sin(p*3)*.06;aR=-1.5+Math.sin(p*3+1)*.06;bob=Math.abs(Math.cos(p*5))*.04;hy=Math.sin(p*1.7)*.18;lean+=.06}
  if(a=='bang'){const w=Math.max(0,Math.sin(p*9));aL=-1.6-w*.9;aR=-1.6-Math.max(0,Math.sin(p*9+2.2))*.9;lean+=.1;hy=Math.sin(p*2)*.1}
  if(a=='glass'){aR=-1.62;aRz=-.05;aL=.05;lean+=.05}
  if(a=='pull'){const k=clamp(s.k||0);aL=-2.9+k*1.5;aR=-2.9+k*1.5;aLz=.1;aRz=-.1;bob=-k*.15+Math.sin(clamp(k*1.3)*Math.PI)*.35;lean+=k*.15}
  if(a=='pant'){lean+=.32;aL=-.45;aR=-.45;bob=Math.sin(p*12)*.03;hp=-.25}
  if(a=='shush'){aR=-2.05;aRz=.62;aL=-.2;lean+=.08}
  if(a=='sneak'){const w=Math.sin(p*5);lL=w*.4;lR=-w*.4;aL=-.6;aR=-.6;lean+=.3;bob=-.08+Math.abs(Math.cos(p*5))*.03;hp=-.2}
  if(a=='grab'){aR=-1.75+Math.sin(p*3)*.05;aL=-.3;lean+=.04}
  if(a=='hold'){aR=-1.1;aL=-1.0;aLz=-.3;aRz=.3}
  if(a=='back'){const w=Math.sin(p*7);lL=w*.4;lR=-w*.4;aL=-1.1;aR=-1.1;aLz=-.3;aRz=.3;lean+=-.12}
  if(a=='raise'){aR=-1.62;aL=-.1}
  if(s.sit){lL=-1.5;lR=-1.5;if(a=='sitcry'||a=='eat'||a=='cower'||a=='sad'||a=='lookup'||a=='idle'){}}
  ch.armL.rotation.set(aL,0,aLz);ch.armR.rotation.set(aR,0,aRz);ch.legL.rotation.set(lL,0,0);ch.legR.rotation.set(lR,0,0);
  ch.body.position.y=bob;ch.body.rotation.x=lean;
  ch.neck.rotation.set((s.look?s.look[1]:0)+hp-lean*.6,(s.look?s.look[0]:0)+hy,0);
  // props
  ch.props.chips.visible=s.hold=='chips';ch.props.bunny.visible=s.hold=='bunny';
  ch.glowL&&(ch.glowL.intensity=s.glow||0);ch.glowEyes&&ch.glowEyes.forEach(m=>m.visible=s.eyes=='glow');
  // tears
  ch.tears.forEach((m,i)=>{if(!s.tears){m.visible=false;return}const side=i%2?1:-1;const ph=((p*1.4)+Math.floor(i/2)*.2)%1;
    m.visible=true;m.position.set(side*(.094+ph*.035),.0-ph*.3,.255+(ph>.8?(ph-.8)*.8:0))});
  drawFace(ch,s.eyes||'normal',s.mouth||'closed','')}

/* ---------- props, pools, particles ---------- */
const m4=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),sc3=new THREE.Vector3();
function setI(im,i,x,y,z,s=1,rx=0,ry=0,rz=0){e.set(rx,ry,rz);q.setFromEuler(e);sc3.set(s,s,s);m4.compose(V3(x,y,z),q,sc3);im.setMatrixAt(i,m4)}
function pool(n,mat,size=1,shadow=true){const im=new THREE.InstancedMesh(new THREE.BoxGeometry(size,size,size),mat,n);im.castShadow=shadow;im.receiveShadow=true;scene.add(im);im.count=0;return im}

/* ---------- timeline helpers ---------- */
let B,S,E;
function lineAt(t){for(const b of TL.beats){if(t>=b.start-.04&&t<=b.start+b.dur+.02)return b}return null}
function mouthOf(name,t,def){const b=lineAt(t);if(b&&b.who==name){const i=Math.floor((t-b.start)*30);const v=b.env[clamp(i,0,b.env.length-1)]||0;return v>.55?'open':v>.2?'half':'closed'}return def||'closed'}
function speaking(name,t){const b=lineAt(t);return b&&b.who==name}
function shake(t,amp){return V3(Math.sin(t*37.1)*amp+Math.sin(t*61.7)*amp*.5,Math.sin(t*43.3)*amp+Math.cos(t*71.9)*amp*.4,Math.sin(t*29.3)*amp*.6)}
function cam(pos,look,fov=50){camera.position.copy(pos);camera.fov=fov;camera.updateProjectionMatrix();camera.lookAt(look)}
const face=(from,to)=>Math.atan2(to[0]-from[0],to[2]-from[2]);
const headW=(ch)=>{const v=new THREE.Vector3();ch.head.getWorldPosition(v);return v};
const scr=(v)=>{const p=v.clone().project(camera);return {x:(p.x+1)/2*W,y:(1-p.y)/2*H,ok:p.z<1}};

const CHIP={bin:['BIN','#FF8A1F'],bo:['BO','#6B4BD6'],zu:['ZU','#3FA34D']};
function rr(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath()}
function outlined(g,txt,x,y,size,fill,stroke='#000',lw){g.font=`800 ${size}px Kid`;g.lineJoin='round';g.lineWidth=lw||size*.2;g.strokeStyle=stroke;g.strokeText(txt,x,y);g.fillStyle=fill;g.fillText(txt,x,y)}
function heart(g,x,y,s,col){g.save();g.translate(x,y);g.scale(s,s);g.beginPath();g.moveTo(0,12);g.bezierCurveTo(-26,-6,-14,-30,0,-14);g.bezierCurveTo(14,-30,26,-6,0,12);g.closePath();g.lineWidth=5;g.strokeStyle='#000';g.stroke();g.fillStyle=col;g.fill();g.restore()}
