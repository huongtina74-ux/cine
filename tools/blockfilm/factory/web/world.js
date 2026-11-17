/* ===== blockfilm factory — arena for "Who can …?" contests (assembled after the shared core). All textures drawn here; original, no Mojang assets. =====
   Reads SPEC (lanes, challenge, ruler). Feet rest at y=BASE: 1.5 on spring pads (launch), 0.5 on the grass (pillar). */
const LANES=SPEC.lanes||['bin','bo','zu'];
const LX={};LANES.forEach((n,i)=>LX[n]=(i-(LANES.length-1)/2)*2.1);
const CHALL=SPEC.challenge||'launch';
const BASE=CHALL=='launch'?1.5:0.5;
const RULER=SPEC.ruler||28;

T.flowerW=tex(4,4,(p)=>{p(0,0,'#FFFFFF',4,4);p(1,1,'#FFD54F',2,2)});
T.flowerP=tex(4,4,(p)=>{p(0,0,'#E879F9',4,4);p(1,1,'#FFF59D',2,2)});
T.padTop=tex(16,16,p=>{const r=rng(201);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#3DDC97',.92+r()*.12));p(0,0,'#1F9E6A',16,1);p(0,15,'#1F9E6A',16,1);p(0,0,'#1F9E6A',1,16);p(15,0,'#1F9E6A',1,16);
  for(const y0 of[3,8]){for(let i=0;i<5;i++){p(3+i,y0+i,'#FFE14D',2,1);p(11-i,y0+i,'#FFE14D',2,1)}}});
T.padSide=tex(16,16,p=>{const r=rng(202);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#2FC184',.9+r()*.12));p(0,0,'#A8F5D3',16,2);p(0,14,'#167A50',16,2);
  for(let y=4;y<13;y+=3){p(3,y,'#167A50',10,1);p(4,y+1,'#6FE8B5',8,1)}});
T.pole=[0,1].map(k=>tex(16,16,p=>{const r=rng(210+k);const c=k?'#FFFFFF':'#E53935';for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade(c,.9+r()*.12));p(0,0,shade(c,.75),16,1)}));
// soft landing bales: straw stripes, binding bands (our own design)
T.baleTop=tex(16,16,p=>{const r=rng(220);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#E7C35A',.85+r()*.25));for(let y=1;y<16;y+=3)p(0,y,'#C99A2E',16,1)});
T.baleSide=tex(16,16,p=>{const r=rng(221);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#DDB84F',.85+r()*.25));for(let x=1;x<16;x+=3)p(x,0,'#B88A24',1,16);p(0,3,'#8E5A2B',16,2);p(0,11,'#8E5A2B',16,2)});
MAT.flowerW=M(T.flowerW,{transparent:true});MAT.flowerP=M(T.flowerP,{transparent:true});
MAT.pad=[M(T.padSide),M(T.padSide),M(T.padTop),M(T.padSide),M(T.padSide),M(T.padSide)];
MAT.pole0=M(T.pole[0]);MAT.pole1=M(T.pole[1]);
MAT.bale=[M(T.baleSide),M(T.baleSide),M(T.baleTop),M(T.baleTop),M(T.baleSide),M(T.baleSide)];

/* ---------- world ---------- */
const world=new Map();const K=(x,y,z)=>x+','+y+','+z;
const set=(x,y,z,t)=>world.set(K(x,y,z),t);
const hill=(x,z)=>{const r=Math.hypot(x,z+4);if(r<13)return 0;const n=Math.sin(x*.33)+Math.cos(z*.29)+Math.sin((x-z)*.17);return Math.max(0,Math.round((r-13)*.35+n))};
for(let x=-30;x<=30;x++)for(let z=-34;z<=16;z++){const h=hill(x,z);for(let y=-1;y<=h;y++)set(x,y,z,y==h?'grass':'dirt')}
function tree(x,z,h){const g=hill(x,z);for(let y=1;y<=h;y++)set(x,g+y,z,'log');
  for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)for(let dy=h-1;dy<=h+1;dy++){if(Math.abs(dx)+Math.abs(dz)+(dy>h?1:0)>3)continue;if(!(dx==0&&dz==0&&dy<=h))set(x+dx,g+dy,z+dz,'leaves')}
  set(x,g+h+2,z,'leaves')}
[[-9,-7,5],[9,-8,6],[-15,-12,6],[15,-13,5],[-6,-15,5],[5,-17,6],[-20,-4,5],[20,-5,6]].forEach(a=>tree(...a));
// measuring tower behind the lanes: red/white rings every 4 blocks
for(let y=1;y<=RULER;y++)set(5,y,-2,(Math.floor((y-1)/4)%2)?'pole1':'pole0');

/* ---------- mesher with per-vertex ambient occlusion (soft corners like the real game look) ---------- */
(function(){
  const F=[{d:[1,0,0],c:[[.5,-.5,.5],[.5,-.5,-.5],[.5,.5,-.5],[.5,.5,.5]],i:0},{d:[-1,0,0],c:[[-.5,-.5,-.5],[-.5,-.5,.5],[-.5,.5,.5],[-.5,.5,-.5]],i:1},
    {d:[0,1,0],c:[[-.5,.5,.5],[.5,.5,.5],[.5,.5,-.5],[-.5,.5,-.5]],i:2},{d:[0,-1,0],c:[[-.5,-.5,-.5],[.5,-.5,-.5],[.5,-.5,.5],[-.5,-.5,.5]],i:3},
    {d:[0,0,1],c:[[-.5,-.5,.5],[.5,-.5,.5],[.5,.5,.5],[-.5,.5,.5]],i:4},{d:[0,0,-1],c:[[.5,-.5,-.5],[-.5,-.5,-.5],[-.5,.5,-.5],[.5,.5,-.5]],i:5}];
  const solid=(x,y,z)=>{const t=world.get(K(x,y,z));return t&&t!='leaves'?1:0};
  const AO=[1,.8,.66,.54];
  const bufs=new Map();const aoMat=new Map();
  const matOf=(t,fi)=>{const m=Array.isArray(MAT[t])?MAT[t][fi]:MAT[t];let a=aoMat.get(m);if(!a){a=m.clone();a.vertexColors=true;aoMat.set(m,a)}return a};
  for(const [k,t] of world){const [x,y,z]=k.split(',').map(Number);
    for(const f of F){const n=world.get(K(x+f.d[0],y+f.d[1],z+f.d[2]));if(n&&n!='leaves'&&t!='leaves')continue;if(n&&t=='leaves'&&n=='leaves')continue;
      const m=matOf(t,f.i);let b=bufs.get(m);if(!b){b={p:[],n:[],u:[],c:[],cast:t!='grass'&&t!='dirt'&&t!='sand'};bufs.set(m,b)}
      // AO per corner: look at the 3 cells next to the corner, one layer out along the face normal
      const ao=f.c.map(c=>{const ax=[0,1,2].filter(i=>f.d[i]==0);const o=[x+f.d[0],y+f.d[1],z+f.d[2]];
        const s1=[...o],s2=[...o],cr=[...o];s1[ax[0]]+=Math.sign(c[ax[0]]);s2[ax[1]]+=Math.sign(c[ax[1]]);cr[ax[0]]+=Math.sign(c[ax[0]]);cr[ax[1]]+=Math.sign(c[ax[1]]);
        const a=solid(...s1),bb=solid(...s2),cc=solid(...cr);return AO[a&&bb?3:a+bb+cc]});
      const flip=ao[0]+ao[2]<ao[1]+ao[3];const q=flip?[1,2,3,1,3,0]:[0,1,2,0,2,3],uv=[[0,0],[1,0],[1,1],[0,1]];
      for(const j of q){const c=f.c[j];b.p.push(x+c[0],y+c[1],z+c[2]);b.n.push(...f.d);b.u.push(...uv[j]);b.c.push(ao[j],ao[j],ao[j])}}}
  for(const [m,b] of bufs){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(b.p,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(b.n,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(b.u,2));g.setAttribute('color',new THREE.Float32BufferAttribute(b.c,3));
    const me=new THREE.Mesh(g,m);me.castShadow=b.cast;me.receiveShadow=true;scene.add(me)}
  window.FACES=[...bufs.values()].reduce((a,b)=>a+b.p.length/18,0)})();
