/* ===== MC-S1 Short #01 "Who can bounce the highest?" — world (assembled after the shared core). Every texture is drawn here; original, no Mojang assets. ===== */
T.flowerW=tex(4,4,(p)=>{p(0,0,'#FFFFFF',4,4);p(1,1,'#FFD54F',2,2)});
T.flowerP=tex(4,4,(p)=>{p(0,0,'#E879F9',4,4);p(1,1,'#FFF59D',2,2)});
// bounce pad: our own mint "spring pad" — chevrons on top, coil marks on the sides
T.padTop=tex(16,16,p=>{const r=rng(201);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#3DDC97',.92+r()*.12));p(0,0,'#1F9E6A',16,1);p(0,15,'#1F9E6A',16,1);p(0,0,'#1F9E6A',1,16);p(15,0,'#1F9E6A',1,16);
  for(const y0 of[3,8]){for(let i=0;i<5;i++){p(3+i,y0+i,'#FFE14D',2,1);p(11-i,y0+i,'#FFE14D',2,1)}}});
T.padSide=tex(16,16,p=>{const r=rng(202);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#2FC184',.9+r()*.12));p(0,0,'#A8F5D3',16,2);p(0,14,'#167A50',16,2);
  for(let y=4;y<13;y+=3){p(3,y,'#167A50',10,1);p(4,y+1,'#6FE8B5',8,1)}});
T.pole=[0,1].map(k=>tex(16,16,p=>{const r=rng(210+k);const c=k?'#FFFFFF':'#E53935';for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade(c,.9+r()*.12));p(0,0,shade(c,.75),16,1)}));
MAT.flowerW=M(T.flowerW,{transparent:true});MAT.flowerP=M(T.flowerP,{transparent:true});
MAT.pad=[M(T.padSide),M(T.padSide),M(T.padTop),M(T.padSide),M(T.padSide),M(T.padSide)];
MAT.pole0=M(T.pole[0]);MAT.pole1=M(T.pole[1]);

/* ---------- world ---------- */
const world=new Map();const K=(x,y,z)=>x+','+y+','+z;
const set=(x,y,z,t)=>world.set(K(x,y,z),t);
// meadow: flat play area, a gentle ring of hills behind, trees
const hill=(x,z)=>{const r=Math.hypot(x,z+4);if(r<13)return 0;const n=Math.sin(x*.33)+Math.cos(z*.29)+Math.sin((x-z)*.17);return Math.max(0,Math.round((r-13)*.35+n))};
for(let x=-30;x<=30;x++)for(let z=-34;z<=16;z++){const h=hill(x,z);for(let y=-1;y<=h;y++)set(x,y,z,y==h?'grass':'dirt')}
function tree(x,z,h){const g=hill(x,z);for(let y=1;y<=h;y++)set(x,g+y,z,'log');
  for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)for(let dy=h-1;dy<=h+1;dy++){if(Math.abs(dx)+Math.abs(dz)+(dy>h?1:0)>3)continue;if(!(dx==0&&dz==0&&dy<=h))set(x+dx,g+dy,z+dz,'leaves')}
  set(x,g+h+2,z,'leaves')}
[[-9,-7,5],[9,-8,6],[-15,-12,6],[15,-13,5],[-6,-15,5],[5,-17,6],[-20,-4,5],[20,-5,6]].forEach(a=>tree(...a));
// the measuring tower behind the pads: red/white rings every 4 blocks, up to 28
for(let y=1;y<=28;y++)set(5,y,-2,(Math.floor((y-1)/4)%2)?'pole1':'pole0');
const MESHER_HOOK=1;
