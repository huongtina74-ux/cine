/* ---------- decor: flowers, clouds, sky, lights ---------- */
const SITE={x:4,z:0};
const inSite=(x,z)=>x>=0&&x<=8&&z>=-4&&z<=5;
const onPath=(x,z)=>Math.abs(z-6.6)<1.6&&x>-16&&x<8;
(function(){const r=rng(21);for(let i=0;i<90;i++){const x=(r()*40-20)|0,z=(r()*40-20)|0;if(hgt(x,z)>0||world.get(K(x,1,z))||inSite(x,z)||onPath(x,z))continue;
  const f=new THREE.Mesh(new THREE.BoxGeometry(.22,.22,.22),M(r()<.5?T.flowerR:T.flowerY));f.position.set(x+r()*.6-.3,.72,z+r()*.6-.3);
  const st=new THREE.Mesh(new THREE.BoxGeometry(.06,.3,.06),new THREE.MeshLambertMaterial({color:0x2E7D32}));st.position.set(f.position.x,.6,f.position.z);scene.add(f,st)}})();
const clouds=[];(function(){const r=rng(31);const m=new THREE.MeshLambertMaterial({color:0xffffff,emissive:0xffffff,emissiveIntensity:.55,transparent:true,opacity:.92});
  for(let i=0;i<14;i++){const c=new THREE.Mesh(new THREE.BoxGeometry(6+r()*10,1.2,4+r()*6),m);c.position.set(r()*140-70,26+r()*6,r()*140-70);c.userData.v=.4+r()*.5;scene.add(c);clouds.push(c)}})();
const hemi=new THREE.HemisphereLight(0xCFE8FF,0x5a7a3a,.7);scene.add(hemi);
const sun=new THREE.DirectionalLight(0xFFF2D6,1.05);sun.position.set(-14,30,22);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);
Object.assign(sun.shadow.camera,{left:-16,right:16,top:16,bottom:-16,near:1,far:90});sun.shadow.bias=-.0006;sun.shadow.normalBias=.02;scene.add(sun);sun.target.position.set(2,0,2);scene.add(sun.target);
const skyC=document.createElement('canvas');skyC.width=4;skyC.height=256;{const g=skyC.getContext('2d');const gr=g.createLinearGradient(0,0,0,256);gr.addColorStop(0,'#3D8BFF');gr.addColorStop(.65,'#9FD4FF');gr.addColorStop(1,'#DFF3FF');g.fillStyle=gr;g.fillRect(0,0,4,256)}
const skyT=new THREE.CanvasTexture(skyC);skyT.encoding=THREE.sRGBEncoding;
scene.background=skyT;scene.fog=new THREE.Fog(0xBFE4FF,35,85);

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
  const apple=new THREE.Group();const appT=tex(8,8,p=>{p(0,0,'#C40000',8,8);p(1,1,'#FF3B30',3,2);p(2,1,'#FFB3A8',1,1);p(5,5,'#8E0000',3,3)});const ab=new THREE.Mesh(new THREE.BoxGeometry(.3,.3,.3),new THREE.MeshLambertMaterial({map:appT,emissive:0x330000}));const al=new THREE.Mesh(new THREE.BoxGeometry(.05,.12,.05),new THREE.MeshLambertMaterial({color:0x5D4037}));al.position.y=.2;const lf=new THREE.Mesh(new THREE.BoxGeometry(.13,.05,.03),new THREE.MeshLambertMaterial({color:0x2E9E3A}));lf.position.set(.08,.22,0);apple.add(ab,al,lf);apple.position.y=-.12;
  const blk=new THREE.Mesh(new THREE.BoxGeometry(.34,.34,.34),MAT.plank);blk.position.y=-.12;
  ch.props={apple,block:blk};Object.values(ch.props).forEach(m=>{m.visible=false;m.traverse(x=>x.castShadow=true);ch.hand.add(m)});
  ch.root.scale.setScalar(o.scale||1);
  ch.mats=[];ch.root.traverse(m=>{if(m.isMesh&&!ch.tears.includes(m)){(Array.isArray(m.material)?m.material:[m.material]).forEach(mm=>ch.mats.push(mm))}});
  scene.add(ch.root);CH[name]=ch;return ch}
const BIN=makeChar('bin',{seed:3,skin:'#F4C9A0',hair:'#C6862A',spikes:true,shirt:'#FF8A1F',sleeve:'#FF8A1F',pants:'#6B4423',shorts:true,shoe:'#E53935',belt:'#E57212',
  shirtDeco:p=>{p(3,2,'#FFE14D',2,1);p(2,3,'#FFE14D',4,1);p(1,4,'#FFE14D',6,1);p(2,5,'#FFE14D',4,1);p(2,6,'#FFE14D',1,1);p(5,6,'#FFE14D',1,1);p(1,0,'#fff',1,3);p(6,0,'#fff',1,3);p(1,8,'#E57212',6,2)},freckles:true});
const BO=makeChar('bo',{seed:5,skin:'#E3AE84',hair:'#1F1A2B',shirt:'#6B4BD6',sleeve:'#6B4BD6',pants:'#3A3F4B',shoe:'#222',sole:'#ddd',belt:'#2B2F38',
  shirtDeco:p=>{p(2,0,'#fff',4,1);p(3,1,'#fff',2,1);p(3.5,1,'#F2C94C',1,4);p(1,6,'#5A3EC0',2,2)},glasses:true});
const ZU=makeChar('zu',{seed:9,skin:'#6DBE5A',hair:'#2F6B25',shirt:'#2BB3C0',short:true,pants:'#4B4FC2',shoe:'#3A3A3A',sole:'#555',belt:'#1E8C96',headScale:1.25,scale:.72,zombie:true,
  shirtDeco:p=>{p(1,8,'#6DBE5A',2,2);p(5,6,'#6DBE5A',2,1);p(6,9,'#1E8C96',2,1);p(0,11,'#6DBE5A',1,1);p(3,11,'#6DBE5A',2,1)}});

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
  if(s.sit){lL=-1.5;lR=-1.5;if(a=='sitcry'||a=='eat'||a=='cower'||a=='sad'||a=='lookup'||a=='idle'){}}
  ch.armL.rotation.set(aL,0,aLz);ch.armR.rotation.set(aR,0,aRz);ch.legL.rotation.set(lL,0,0);ch.legR.rotation.set(lR,0,0);
  ch.body.position.y=bob;ch.body.rotation.x=lean;
  ch.neck.rotation.set((s.look?s.look[1]:0)+hp-lean*.6,(s.look?s.look[0]:0)+hy,0);
  // props
  ch.props.apple.visible=s.hold=='apple';ch.props.block.visible=s.hold=='block';
  if(s.hold=='apple'){const b=1-clamp(s.bite||0)*.75;ch.props.apple.scale.set(b,b,b)}
  // tears
  ch.tears.forEach((m,i)=>{if(!s.tears){m.visible=false;return}const side=i%2?1:-1;const ph=((p*1.4)+Math.floor(i/2)*.2)%1;
    m.visible=true;m.position.set(side*(.094+ph*.035),.0-ph*.3,.255+(ph>.8?(ph-.8)*.8:0))});
  drawFace(ch,s.eyes||'normal',s.mouth||'closed','')}

/* ---------- props, pools, particles ---------- */
const m4=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),sc3=new THREE.Vector3();
function setI(im,i,x,y,z,s=1,rx=0,ry=0,rz=0){e.set(rx,ry,rz);q.setFromEuler(e);sc3.set(s,s,s);m4.compose(V3(x,y,z),q,sc3);im.setMatrixAt(i,m4)}
function pool(n,mat,size=1,shadow=true){const im=new THREE.InstancedMesh(new THREE.BoxGeometry(size,size,size),mat,n);im.castShadow=shadow;im.receiveShadow=true;scene.add(im);im.count=0;return im}
const P_={plank:pool(140,MAT.plank),log:pool(40,MAT.log[0]),roof:pool(90,MAT.roof),dirt:pool(20,MAT.dirt),glass:pool(6,MAT.glass,1,false),redWool:pool(2,MAT.redWool),wool:pool(2,MAT.wool)};
const dust=pool(90,new THREE.MeshLambertMaterial({color:0x9a8f80}),.14,false);
const smokeMat=new THREE.MeshLambertMaterial({color:0xdddddd,transparent:true,opacity:.8,depthWrite:false});
const smoke=[];for(let i=0;i<24;i++){const m=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),smokeMat.clone());m.visible=false;scene.add(m);smoke.push(m)}
const sparkT=(()=>{const c=document.createElement('canvas');c.width=c.height=64;const g=c.getContext('2d');g.fillStyle='#fff';g.fillRect(28,4,8,56);g.fillRect(4,28,56,8);g.fillStyle='#FFF59D';g.fillRect(24,24,16,16);return new THREE.CanvasTexture(c)})();
const sparks=[];{const r=rng(55);for(let i=0;i<30;i++){const s=new THREE.Sprite(new THREE.SpriteMaterial({map:sparkT,blending:THREE.AdditiveBlending,transparent:true,depthWrite:false}));
  s.position.set(SITE.x+(r()-.5)*7,.8+r()*5,SITE.z+(r()-.5)*7+.5);s.userData.ph=r()*10;s.userData.sp=2+r()*3;s.visible=false;scene.add(s);sparks.push(s)}}
// ball
const ballT=tex(16,8,p=>{p(0,0,'#FF7043',16,8);p(0,3,'#fff',16,2);p(3,0,'#fff',2,8);p(11,0,'#fff',2,8)});
const ball=new THREE.Mesh(new THREE.SphereGeometry(.22,16,12),new THREE.MeshLambertMaterial({map:ballT}));ball.castShadow=true;scene.add(ball);
// front-yard flowers that appear at "ta-da"
const yardFlowers=[];[[2.2,3.1],[2.8,3.4],[5.2,3.4],[5.8,3.1],[1.6,2.4],[6.4,2.4]].forEach(([x,z],i)=>{const g=new THREE.Group();const f=new THREE.Mesh(new THREE.BoxGeometry(.24,.24,.24),M(i%2?T.flowerR:T.flowerY));f.position.y=.42;const st=new THREE.Mesh(new THREE.BoxGeometry(.06,.34,.06),new THREE.MeshLambertMaterial({color:0x2E7D32}));st.position.y=.17;g.add(f,st);g.position.set(x,.5,z);g.visible=false;scene.add(g);yardFlowers.push(g)});

/* old hut (3x3, patchy) and its collapse */
const OLD=[];{const r=rng(88);for(let y=1;y<=3;y++)for(let x=3;x<=5;x++)for(let z=-1;z<=1;z++){
  const edge=x==3||x==5||z==-1||z==1;if(y<3&&!edge)continue;if(z==1&&x==4&&y<3)continue;
  const dx=x-4,dz=z;const n=Math.hypot(dx,dz)||1;const sp=1.2+r()*2.2;
  OLD.push({p:[x,y,z],m:r()<.55?'plank':'dirt',v:[dx/n*sp+(r()-.5),2+r()*2.5,(dz/n*sp+(r()-.5))*.55-.4],spin:[(r()-.5)*9,(r()-.5)*9,(r()-.5)*9],rest:[(r()-.5)*.5,0,(r()-.5)*.5]})}}
OLD.forEach(b=>{const vy=b.v[1],y0=b.p[1];b.tl=(vy+Math.sqrt(vy*vy+4*4.9*(y0-1)))/9.8;})
function oldHut(t,tC,tClear,im){ // im: {plank,dirt}
  if(t>=tClear)return;
  OLD.forEach(b=>{const u=t-tC;const P=P_[b.m];let x=b.p[0],y=b.p[1],z=b.p[2],rx=0,ry=0,rz=0,s=1;
    if(u>0){const uu=Math.min(u,b.tl);x+=b.v[0]*uu;z+=b.v[2]*uu;y=Math.max(1,b.p[1]+b.v[1]*uu-4.9*uu*uu);const sp=Math.min(u,b.tl);rx=b.spin[0]*sp;ry=b.spin[1]*sp;rz=b.spin[2]*sp;
      if(u>=b.tl){rx=Math.round(rx/(Math.PI/2))*(Math.PI/2);rz=Math.round(rz/(Math.PI/2))*(Math.PI/2)}}
    else if(u>-0.35){const w=(u+.35)/.35;rz=Math.sin(t*40)*.04*w;x+=Math.sin(t*33+b.p[0])*.03*w}
    const cl=t-(tClear-.25);if(cl>0)s=Math.max(0,1-cl/.25);
    setI(P,P.count++,x,y,z,s,rx,ry,rz)})}

/* new house: 5x5 walls (x2..6, z-2..2), log corners, door at front (x4,z2), windows, roof in two layers */
const NEW=[];{const add=(x,y,z,m)=>NEW.push({p:[x,y,z],m});
  for(let y=1;y<=3;y++){const ring=[];for(let x=2;x<=6;x++)ring.push([x,2]);for(let z=1;z>=-2;z--)ring.push([6,z]);for(let x=5;x>=2;x--)ring.push([x,-2]);for(let z=-1;z<=1;z++)ring.push([2,z]);
    ring.forEach(([x,z])=>{if(x==4&&z==2&&y<3)return;const corner=(x==2||x==6)&&(z==2||z==-2);const win=y==2&&((z==2&&(x==3||x==5))||(x==6&&z==0)||(x==2&&z==0));add(x,y,z,corner?'log':win?'glass':'plank')})}
  for(let x=1;x<=7;x++)for(let z=-3;z<=3;z++)add(x,4,z,'roof');
  for(let x=2;x<=6;x++)for(let z=-2;z<=2;z++)add(x,5,z,'roof');
  for(let x=3;x<=5;x++)for(let z=-1;z<=1;z++)add(x,6,z,'roof');
  add(3,1,-1,'redWool');add(3,1,0,'wool');}
function newHouse(t,t0,t1){ // blocks pop in one by one between t0 and t1
  const dt=(t1-t0)/NEW.length;let placed=0;
  NEW.forEach((b,i)=>{const u=t-(t0+i*dt);if(u<0)return;placed++;const k=u<.14?1.25*Math.sin(clamp(u/.14)*Math.PI/2)+.0:1;const s=u<.14?k:1;
    const P=P_[b.m];setI(P,P.count++,b.p[0],b.p[1]+(u<.14?(1-u/.14)*.35:0),b.p[2],Math.min(1.12,s))});
  return placed}
function smokePuff(f,cx,cy,cz,n=12,spread=2.6){for(let i=0;i<n&&i<smoke.length;i++){const s=smoke[i];const a=i/n*Math.PI*2;const rr=(1-Math.exp(-f*3))*spread*(.6+(i%3)*.2);s.visible=f<1.6;
  s.position.set(cx+Math.cos(a)*rr,cy+f*1.2+(i%4)*.3,cz+Math.sin(a)*rr);s.scale.setScalar(.5+f*1.1);s.material.opacity=Math.max(0,.8-f*.5)}}
function dustBurst(f,cx,cz){const r=rng(9);for(let i=0;i<80;i++){const vx=(r()-.5)*6,vy=1+r()*4,vz=(r()-.5)*6;const y=.6+vy*f-4.9*f*f;if(y<.55||f<0)continue;setI(dust,dust.count++,cx+vx*f,y,cz+vz*f,1,f*vx,f*vz)}}

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

/* ---------- main render ---------- */
let tNow=0;
function SH(){ // shot boundaries, all derived from the recorded lines
  return {s1:S('hook')-.15, s2:E('hook')+.55, s3:S('kick')-.2, s4:S('huh')-.3, s5:S('cry')-.15, s6:S('okay')-.2, s7:S('hide')-.15, s8:S('apple')-.25,
    s9:S('yum')-.4, s10:S('gone')-.2, s11:S('idea')-.2, s12:S('build')-.05, s13:E('build')+.15, s14:S('ouch')-.55, s15:E('ouch')+1.3, s16:S('tada')-.15,
    s17:S('yay')-.4, s18:S('hug')-.3, s19:E('hug')+.9};
}
function renderAt(t){
  tNow=t;const X=SH();
  Object.values(P_).forEach(p=>p.count=0);dust.count=0;smoke.forEach(s=>s.visible=false);sparks.forEach(s=>s.visible=false);
  clouds.forEach((c,i)=>{c.position.x=((i*23+t*c.userData.v+70)%140)-70});
  const tC=.42, tClear=X.s13+.15, tB0=X.s13+.35, tB1=S('tada')-.35;
  oldHut(t,tC,tClear);
  if(t>=tB0)newHouse(t,tB0,tB1);
  if(t>tC&&t<tC+1.6){dustBurst(t-tC-.15,4,0);smokePuff(t-tC,4,.8,0,10,2.2)}
  if(t>tClear-.3&&t<tClear+1.4)smokePuff(t-tClear+.3,4,.8,0,14,2.8);
  yardFlowers.forEach((f,i)=>{const u=t-(S('tada')-.1+i*.07);f.visible=u>0;f.scale.setScalar(u<.2?eout(u/.2)*1.2:1)});
  if(t>S('tada')-.2&&t<S('yay')+.5)sparks.forEach(s=>{s.visible=true;const v=Math.max(0,Math.sin(t*s.userData.sp+s.userData.ph));s.scale.setScalar(.1+v*.6);s.material.opacity=v});
  Object.values(P_).forEach(p=>p.instanceMatrix.needsUpdate=true);dust.instanceMatrix.needsUpdate=true;

  const b={},o={},z={};const ov2={};let sh=V3(0,0,0);
  // ---- default blocking (overridden per shot) ----
  const ZSIT=[4,.5,3.0];
  // Zu
  Object.assign(z,{pos:ZSIT,rot:0,sit:true,anim:'sitcry',p:t,eyes:'cry',mouth:mouthOf('zu',t,'wail'),tears:true});
  // Bin & Bo walking in from the left with the ball
  const walk0=X.s2, kickT=S('kick')-.15;
  const binRun=vl([-10,.5,6.4],[-1.7,.5,6.4],clamp((t-walk0+.6)/(kickT-walk0+.4)));
  const boRun=vl([-12.5,.5,7.7],[-3.2,.5,7.7],clamp((t-walk0+.6)/(kickT-walk0+.3)));
  const toZu1=clamp((t-(S('huh')-.6))/1.6), toZu2=clamp((t-(S('okay')-1.0))/1.0);
  const binP=t<kickT+.4?binRun:vl([-1.7,.5,6.4],[2.6,.5,4.9],ease(toZu1));
  const boP=t<kickT+.4?boRun:vl([-3.2,.5,7.7],[2.0,.5,5.8],ease(Math.max(toZu1*.55,toZu2)));
  const runPhase=t<kickT;
  Object.assign(b,{pos:binP.toArray(),rot:runPhase?Math.PI/2:face(binP.toArray(),ZSIT),anim:runPhase?'run':(toZu1>0&&toZu1<1?'walk':(speaking('bin',t)?'talk':'idle')),p:t,eyes:'normal',mouth:mouthOf('bin',t,'smile')});
  Object.assign(o,{pos:boP.toArray(),rot:runPhase?Math.PI/2:face(boP.toArray(),ZSIT),anim:runPhase?'run':((toZu2>0&&toZu2<1)||(toZu1>0&&toZu1<1)?'walk':(speaking('bo',t)?'talk':'idle')),p:t+.4,eyes:'normal',mouth:mouthOf('bo',t,'smile')});
  if(t>kickT-.35&&t<kickT+.5){b.anim='kick';b.k=(t-kickT+.35)/.6}
  if(t>kickT+.2&&t<S('huh')-.6){b.eyes='wide';b.mouth='O';o.eyes='sly';o.rot=Math.PI/2;b.rot=Math.PI/2;o.anim=speaking('bo',t)?'talk':'idle'}
  // ball
  let bp;const kb=kickT+.05, land=kb+1.15;
  if(t<kb){bp=[binP.x+.55,.72,binP.z+.15]}
  else if(t<land){const u=(t-kb)/(land-kb);bp=[lerp(binP.x+.55,5.4,u),.72+Math.sin(u*Math.PI)*4.2,lerp(6.55,2.6,u)]}
  else{const u=t-land;bp=[5.4+Math.min(u,.6)*.5,.72+Math.abs(Math.sin(Math.min(u,1.2)*7))*.45*Math.exp(-u*3),2.6-Math.min(u,.6)*.3]}
  ball.position.set(...bp);ball.rotation.set(t*9,0,t*4);
  // Zu reactions over the story
  if(t<tC+.25){Object.assign(z,{pos:[4,.5,2.0],sit:false,anim:'idle',eyes:'happy',mouth:'smile',tears:false})}
  else if(t<tC+.85){const u=(t-tC-.25)/.6;Object.assign(z,{pos:[4,.5+Math.sin(u*Math.PI)*.6,lerp(2.0,3.0,u)],sit:u>.8,anim:'fall',eyes:'wide',mouth:'O',tears:false})}
  else if(t<S('hook')){z.mouth='frown';z.eyes='sad';z.tears=false;z.anim='sad'}
  if(t>X.s2&&t<X.s4){z.mouth=t>S('kick')+.9?'O':'frown';z.anim=t>S('kick')+.9?'cower':'sitcry';z.eyes=t>S('kick')+.9?'wide':'cry';z.tears=!(t>S('kick')+.9)}
  if(t>=X.s7&&t<X.s8+.6){z.anim='cower';z.eyes='wide';z.mouth=mouthOf('zu',t,'O');z.tears=false}
  if(t>=X.s8+.6&&t<X.s9){z.anim='lookup';z.eyes='hope';z.mouth='O';z.tears=false;z.rot=face(ZSIT,binP.toArray())*.6}
  if(t>=X.s9&&t<X.s10){z.anim='eat';z.hold='apple';z.bite=clamp((t-X.s9-.3)/1.4);z.eyes=t>S('yum')-.05?'star':'happy';z.mouth=speaking('zu',t)?mouthOf('zu',t,'chew'):(Math.sin(t*18)>0?'chew':'closed');z.tears=false}
  if(t>=X.s10&&t<X.s11){z.anim='sad';z.eyes='sad';z.mouth=mouthOf('zu',t,'frown');z.tears=t>S('gone')+.6;z.rot=Math.PI*.92}
  if(t>=X.s11&&t<X.s13){z.anim='lookup';z.eyes='hope';z.mouth='O';z.tears=false;z.rot=face(ZSIT,boP.toArray())*.5}
  if(t>=X.s13){Object.assign(z,{pos:[4,.5,3.6],rot:0,sit:true,anim:'idle',eyes:'happy',mouth:'smile',tears:false});if(t>tB0+2.5){z.anim='cheer';z.sit=false;z.p=t}}
  // Bin offers the apple
  if(t>=X.s8&&t<X.s9+.35){b.anim='give';b.hold='apple';b.pos=vl([2.6,.5,4.9],[3.2,.5,4.25],ease((t-X.s8)/.8)).toArray();b.rot=face(b.pos,ZSIT);b.eyes='happy';b.mouth=mouthOf('bin',t,'smile')}
  if(t>=X.s9+.35&&t<X.s11){b.pos=[3.0,.5,4.4];b.rot=face(b.pos,ZSIT);b.anim='idle';b.eyes='happy';b.mouth='smile'}
  if(t>=X.s10&&t<X.s11){b.eyes='sad';b.mouth='frown';o.eyes='sad';o.mouth='frown'}
  // Bo's idea
  if(t>=X.s11&&t<X.s12){o.anim='ideaup';o.eyes='star';o.mouth=mouthOf('bo',t,'grin');o.pos=[2.0,.5,5.8];o.rot=.2;ov2.bulb=t-X.s11}
  if(t>=X.s12&&t<X.s13){b.anim='cheer';b.eyes='star';b.mouth=mouthOf('bin',t,'grin');o.anim='cheer';o.eyes='happy';o.mouth='grin';b.pos=[3.0,.5,4.4];o.pos=[2.0,.5,5.8]}
  // build montage
  if(t>=X.s13&&t<X.s16){
    const sideB=[1.1,.5,lerp(1.5,-1.5,(Math.sin(t*.7)+1)/2)], sideO=[6.9,.5,lerp(-1.5,1.5,(Math.sin(t*.6)+1)/2)];
    Object.assign(b,{pos:sideB,rot:Math.PI/2,anim:'place',p:t,eyes:'happy',mouth:'grin',hold:'block'});
    Object.assign(o,{pos:sideO,rot:-Math.PI/2,anim:'place',p:t+.4,eyes:'normal',mouth:'smile',hold:'block'});
    if(t>=X.s14&&t<X.s15){const tDrop=S('ouch')-.12;b.pos=[1.1,.5,1.6];b.rot=-.69;
      if(t<tDrop){b.anim='carry';b.hold='block';b.eyes='happy';b.mouth='grin'}
      else{b.anim='hopouch';b.hold=null;b.eyes='closed';b.mouth=mouthOf('bin',t,'wail');b.p=t;
        const u=t-tDrop;ov2.ouch=u;}
      if(t>S('ouch')+.4){o.anim='facepalm';o.eyes='closed';o.mouth='frown';o.pos=[2.4,.5,3.1];o.rot=face(o.pos,b.pos);o.hold=null}}
  }
  // the dropped block (on Bin's foot)
  const tDrop=S('ouch')-.12;
  if(t>=tDrop-.3&&t<X.s15){const u=t-tDrop;const P=P_.plank;const bx=1.1+Math.sin(-.69)*.32+.12,bz=1.6+Math.cos(-.69)*.32;
    if(u>-.3&&u<0){}else if(u>=0){const y=Math.max(.68,1.15-4.9*u*u*3);setI(P,P.count++,bx-.1,y,bz+.15,.34,0,.3,0);P.instanceMatrix.needsUpdate=true}}
  // ta-da / yay / hug
  if(t>=X.s16){Object.assign(b,{pos:[5.6,.5,4.4],rot:-.25,anim:'present',p:t,eyes:'happy',mouth:mouthOf('bin',t,'grin'),hold:null});
    Object.assign(o,{pos:[2.4,.5,4.4],rot:.25,anim:'present',p:t,eyes:'happy',mouth:mouthOf('bo',t,'grin'),hold:null});
    Object.assign(z,{pos:[4,.5,3.6],rot:0,sit:false,anim:t>S('yay')-.5?'cheer':'lookup',p:t,eyes:t>S('yay')-.5?'star':'wide',mouth:mouthOf('zu',t,t>S('yay')-.5?'grin':'O'),tears:false});
    if(t>=X.s18){Object.assign(b,{pos:[4.62,.5,4.05],rot:-1.05,anim:'hug',mouth:mouthOf('bin',t,'grin'),eyes:'happy'});Object.assign(o,{pos:[3.38,.5,4.05],rot:1.05,anim:'hug',eyes:'happy',mouth:'grin'});
      Object.assign(z,{pos:[4,.5,4.25],rot:0,anim:'hug',eyes:'happy',mouth:'grin'});ov2.hearts=t-X.s18}
    if(t>=X.s19){b.anim='idle';o.anim='idle';z.anim='cheer';b.rot=0;o.rot=0;b.pos=[5.0,.5,4.2];o.pos=[3.0,.5,4.2];z.pos=[4,.5,4.4]}}

  /* ---------- cameras ---------- */
  if(t<X.s1){ // HOOK: Zu's tiny hut collapses
    const u=t/X.s1;cam(V3(lerp(5.6,5.3,u),1.9,lerp(8.6,8.0,u)).add(t>tC&&t<tC+.6?shake(t,.08):V3(0,0,0)),V3(4,1.4,.8),46);
  } else if(t<X.s2){ // close: Zu crying in the rubble
    const u=(t-X.s1)/(X.s2-X.s1);cam(V3(lerp(4.4,4.3,u),1.3,lerp(5.4,4.9,u)),V3(4,1.22,2.9),40);
  } else if(t<X.s3){ // Bin & Bo arrive with the ball (tracking)
    cam(V3(binP.x-1.2,1.9,binP.z+5.6),V3(binP.x+.4,1.1,binP.z+.2),44);
  } else if(t<X.s4){ // the kick and the ball arc
    const u=(t-X.s3)/(X.s4-X.s3);cam(V3(lerp(-3.2,-2.8,u),2.0,lerp(13.5,13,u)),V3(lerp(0,2.4,ease(u)),lerp(1.6,2.4,u),lerp(6.2,4.6,ease(u))),54);
  } else if(t<X.s5){ // over Bin's shoulder: "Huh?"
    const bh=binP;cam(V3(bh.x-1.7,2.2,bh.z+2.7),V3(4,1,2.8),44);
  } else if(t<X.s6){ // close Zu crying
    cam(V3(4.6,1.3,5.2),V3(4,1.2,3.0),38);
  } else if(t<X.s7){ // three-shot side
    cam(V3(8.4,2.2,5.6),V3(2.7,1.05,4.6),40);
  } else if(t<X.s8){ // Zu cowers (low, front)
    cam(V3(3.5,1.0,5.0),V3(4,1.2,3.0),40);
  } else if(t<X.s9){ // the apple offer, two-shot from the side
    cam(V3(7.8,1.95,7.0),V3(3.6,1.35,3.7),42);
  } else if(t<X.s10){ // Yum! close
    cam(V3(4.65,1.4,5.1),V3(4,1.2,3.0),36);
  } else if(t<X.s11){ // over Zu's shoulder to the rubble
    cam(V3(4.5,1.25,4.9),V3(4,.9,0),42);
  } else if(t<X.s12){ // Bo's idea, close
    cam(V3(2.8,1.7,9.6),V3(2.0,2.15,5.8),42);
  } else if(t<X.s13){ // group, wide
    cam(V3(4.2,2.0,10.5),V3(4,1.2,3.8),42);
  } else if(t<X.s14||(t>=X.s15&&t<X.s16)){ // montage orbit
    const u=(t-X.s13)/(X.s16-X.s13);const a=lerp(-.35,1.15,u);const rad=10.5;
    cam(V3(SITE.x+Math.sin(a)*rad,lerp(5.5,7.5,u),SITE.z+Math.cos(a)*rad),V3(SITE.x,2.2,SITE.z+.5),44);
  } else if(t<X.s15){ // Ow! my foot
    cam(V3(-1.8,1.6,5.1),V3(1.6,1.0,1.9),40);
  } else if(t<X.s17){ // TA-DA: crane up reveal
    const u=ease((t-X.s16)/(X.s17-X.s16));cam(V3(4,lerp(1.2,3.2,u),lerp(10.6,10.2,u)),V3(4,lerp(1.5,2.5,u),0.8),50);
  } else if(t<X.s18){ // Yay!
    cam(V3(4.1,1.0,6.7),V3(4,1.35,3.6),40);
  } else if(t<X.s19){ // group hug
    const u=(t-X.s18)/(X.s19-X.s18);cam(V3(4,1.6,lerp(8.6,7.6,u)),V3(4,1.15,4.1),40);
  } else { // crane out + end card
    const u=ease(clamp((t-X.s19)/3.5));cam(V3(lerp(4,3,u),lerp(2,8,u),lerp(9.5,18,u)),V3(4,2.2,1),46);
    ov2.end=clamp((t-S('end')+.3)/.4);
  }
  pose(BIN,b);pose(BO,o);pose(ZU,z);
  renderer.render(scene,camera);
  drawOverlay(t,ov2);
}

/* ---------- overlay ---------- */
const CHIP={bin:['BIN','#FF8A1F'],bo:['BO','#6B4BD6'],zu:['ZU','#3FA34D']};
function rr(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath()}
function outlined(g,txt,x,y,size,fill,stroke='#000',lw){g.font=`800 ${size}px Kid`;g.lineJoin='round';g.lineWidth=lw||size*.2;g.strokeStyle=stroke;g.strokeText(txt,x,y);g.fillStyle=fill;g.fillText(txt,x,y)}
function heart(g,x,y,s,col){g.save();g.translate(x,y);g.scale(s,s);g.beginPath();g.moveTo(0,12);g.bezierCurveTo(-26,-6,-14,-30,0,-14);g.bezierCurveTo(14,-30,26,-6,0,12);g.closePath();g.lineWidth=5;g.strokeStyle='#000';g.stroke();g.fillStyle=col;g.fill();g.restore()}
function drawOverlay(t,o){
  const g=ov;g.clearRect(0,0,W,H);g.textBaseline='alphabetic';
  const vg=g.createRadialGradient(W/2,H/2,H*.45,W/2,H/2,H*1.05);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,.32)');g.fillStyle=vg;g.fillRect(0,0,W,H);
  const bt=lineAt(t);
  if(bt&&bt.id!='end'){
    const cap=bt.cap||bt.text;const words=cap.split(' ');const lens=words.map(w=>w.length+1);const tot=lens.reduce((a,c)=>a+c,0);
    let acc=0;const times=lens.map(l=>{const s=bt.start+bt.dur*acc/tot;acc+=l;return s-.06});
    const size=84;g.font=`800 ${size}px Kid`;const sp=g.measureText(' ').width+30;
    const lines=[[]];let lw=0;words.forEach((w,i)=>{const ww=g.measureText(w).width;if(lw+ww>1450&&lines[lines.length-1].length){lines.push([]);lw=0}lines[lines.length-1].push(i);lw+=ww+sp});
    const baseY=H-70-(lines.length-1)*96;
    lines.forEach((ln,li)=>{const widths=ln.map(i=>g.measureText(words[i]).width);const total=widths.reduce((a,c)=>a+c,0)+sp*(ln.length-1);let x=W/2-total/2;const y=baseY+li*96;
      ln.forEach((i,k)=>{const age=t-times[i];if(age>=0){const pop=age<.12?1.35-age/.12*.35:1;const cur=(i==words.length-1?t<bt.start+bt.dur:t<times[i+1]);g.save();g.translate(x+widths[k]/2,y);const k2=pop*(cur?1.08:1);g.scale(k2,k2);g.textAlign='center';outlined(g,words[i],0,0,size,'#FFE600','#000',18);g.restore()}x+=widths[k]+sp})});
    if(CHIP[bt.who]){const [n,c]=CHIP[bt.who];g.font='800 44px Kid';const w=g.measureText(n).width+44;const y=baseY-size-52;rr(g,W/2-w/2,y,w,58,16);g.fillStyle=c;g.fill();g.lineWidth=6;g.strokeStyle='#000';g.stroke();g.textAlign='center';g.fillStyle='#fff';g.fillText(n,W/2,y+46)}
    g.textAlign='left';
  }
  if(o.bulb!==undefined){const h=scr(headW(BO).add(V3(0,.75,0)));const k=o.bulb<.15?o.bulb/.15*1.2:1+Math.sin(o.bulb*8)*.05;g.save();g.translate(h.x,h.y);g.scale(k,k);
    g.strokeStyle='rgba(255,235,59,.9)';g.lineWidth=8;for(let i=0;i<8;i++){const a=i/8*Math.PI*2;g.beginPath();g.moveTo(Math.cos(a)*62,Math.sin(a)*62-10);g.lineTo(Math.cos(a)*84,Math.sin(a)*84-10);g.stroke()}
    g.beginPath();g.arc(0,-10,44,0,Math.PI*2);g.fillStyle='#FFEB3B';g.fill();g.lineWidth=7;g.strokeStyle='#000';g.stroke();g.fillStyle='#9E9E9E';g.fillRect(-20,34,40,22);g.strokeRect(-20,34,40,22);g.restore()}
  if(o.ouch!==undefined&&o.ouch<1.2){const h=scr(V3(1.3,.9,1.9));const u=o.ouch;g.save();g.translate(h.x+260,h.y-60);g.rotate(-.12);const k=u<.1?u/.1*1.3:1.1;g.scale(k,k);g.textAlign='center';outlined(g,'BONK!',0,0,120,'#FF5722','#000',24);g.restore()}
  if(o.hearts!==undefined){for(let i=0;i<9;i++){const f=((o.hearts*.45+i/9)%1);const x=W/2+Math.sin(i*2.3)*420+Math.sin(o.hearts*2+i)*30;const y=H*.62-f*H*.6;g.globalAlpha=Math.min(1,(1-f)*2);heart(g,x,y,1.4+(i%3)*.5,i%2?'#FF5C8A':'#FF2D55')}g.globalAlpha=1}
  if(o.end){const a=o.end;g.save();g.globalAlpha=a;g.fillStyle='rgba(0,0,0,.35)';g.fillRect(0,0,W,250);
    const bounce=1+Math.max(0,Math.sin(t*6))*.05;g.translate(W/2,165);g.scale(bounce*(.6+.4*a),bounce*(.6+.4*a));g.textAlign='center';outlined(g,'NEXT: THE ZOMBIE BIRTHDAY!',0,0,104,'#FFE600','#000',24);g.restore();
    g.save();g.globalAlpha=a;const bx=W-460,by=300;const pressed=(t%2)>1.55&&(t%2)<1.75;rr(g,bx,by+(pressed?6:0),390,110,55);g.fillStyle=pressed?'#9e9e9e':'#E53935';g.fill();g.lineWidth=8;g.strokeStyle='#000';g.stroke();
    g.textAlign='center';g.font='800 60px Kid';g.fillStyle='#fff';g.fillText(pressed?'SUBSCRIBED':'SUBSCRIBE',bx+195,by+76+(pressed?6:0));
    const cx=bx+270+Math.cos(t*2)*10,cy=by+100+Math.sin(t*2)*6+(pressed?8:0);g.fillStyle='#fff';g.strokeStyle='#000';g.lineWidth=5;g.beginPath();g.moveTo(cx,cy);g.lineTo(cx+18,cy+62);g.lineTo(cx+30,cy+44);g.lineTo(cx+52,cy+68);g.lineTo(cx+62,cy+58);g.lineTo(cx+40,cy+36);g.lineTo(cx+60,cy+28);g.closePath();g.fill();g.stroke();g.restore()}
}

window.renderThumb=()=>{
  const t=S('apple')+.6;renderAt(t);
  pose(ZU,{pos:[4,.5,3.0],rot:0,sit:true,anim:'sitcry',p:.3,eyes:'cry',mouth:'wail',tears:true});
  pose(BIN,{pos:[2.55,.5,3.35],rot:1.35,anim:'give',hold:'apple',p:0,eyes:'happy',mouth:'smile'});
  pose(BO,{pos:[5.55,.5,3.75],rot:-1.15,anim:'idle',p:0,eyes:'sad',mouth:'frown'});
  ball.position.set(6.3,.72,4.3);
  cam(V3(4.0,1.55,7.7),V3(4.0,1.2,3.2),44);
  renderer.render(scene,camera);
  const g=ov;g.clearRect(0,0,W,H);g.textAlign='center';
  g.save();g.translate(W*.5,H-70);g.rotate(-.025);outlined(g,'BABY ZOMBIE LOST HIS HOME',0,0,128,'#FFE600','#000',30);g.restore();
};
/* ---------- init ---------- */
window.init=async()=>{
  TL=await (await fetch('timeline.json')).json();
  B=id=>TL.beats.find(b=>b.id===id);S=id=>B(id).start;E=id=>B(id).start+B(id).dur;
  await document.fonts.load('800 80px Kid','BABY ZOMBIE ăâêôơưđ');await document.fonts.ready;
  renderAt(0);return TL.total};
window.renderAt=renderAt;
</script>
</body></html>
