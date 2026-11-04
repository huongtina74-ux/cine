/* ===== Bin & Bo & Zu — "Zombie Outbreak: Locked in a Supermarket" (trial) — episode code, assembled after the shared core ===== */
/* Store front is the plane z=0: inside is z<0, the street is z>0. Every texture is drawn here (original, no Mojang assets). */
T.asphalt=noiseTex('#2E3034',.25,61,(p,r)=>{for(let i=0;i<10;i++)p(r()*16|0,r()*16|0,'#3E4146')});
T.lane=tex(16,16,p=>{const r=rng(62);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#2E3034',.85+r()*.3));p(1,6,'#C9A227',14,4)});
T.walk=tex(16,16,p=>{const r=rng(63);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#9A9890',.88+r()*.2));p(0,0,'#7A7870',16,1);p(0,0,'#7A7870',1,16)});
T.tile=tex(16,16,p=>{const r=rng(64);for(let y=0;y<16;y++)for(let x=0;x<16;x++){const c=((x<8)^(y<8))?'#D9DCD6':'#B9BEB8';p(x,y,shade(c,.94+r()*.1))}p(0,0,'#8E938D',16,1);p(0,0,'#8E938D',1,16)});
T.concrete=noiseTex('#A7A49B',.16,65,(p,r)=>{for(let i=0;i<4;i++)p(r()*15|0,r()*15|0,'#8F8C84',2,1)});
T.paint=tex(16,16,p=>{const r=rng(66);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade(y>11?'#2E7D74':'#D8D2BF',.93+r()*.1));p(0,11,'#1F5B54',16,1)});
T.metal=tex(16,16,p=>{const r=rng(67);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#9AA3AD',.9+r()*.15));p(0,0,'#C9D1DA',16,1);p(0,15,'#6E7680',16,1)});
const prodColors=[['#E53935','#FFEB3B','#1E88E5','#43A047','#FB8C00'],['#8E24AA','#FDD835','#00ACC1','#F4511E','#FFFFFF'],['#6D4C41','#C0CA33','#D81B60','#3949AB','#FFB300']];
const prodTex=k=>tex(16,16,p=>{const r=rng(70+k);p(0,0,'#5F6770',16,16);
  for(const y0 of[1,6,11]){p(0,y0+4,'#C9D1DA',16,1);let x=0;while(x<16){const w=2+(r()*3|0),h=2+(r()*2|0);const c=prodColors[k][r()*5|0];p(x,y0+4-h,c,Math.min(w-0,16-x),h);p(x,y0+4-h,shade(c,1.25),Math.min(w,16-x),1);x+=w}}});
T.prod=[prodTex(0),prodTex(1),prodTex(2)];
T.counter=tex(16,16,p=>{const r=rng(71);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#37474F',.9+r()*.2));p(0,0,'#ECEFF1',16,3);p(2,6,'#E53935',12,2)});
T.brickR=tex(16,16,p=>{const r=rng(72);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#7B3B2E',.85+r()*.25));for(let y=0;y<16;y+=4){p(0,y+3,'#4A2A22',16,1);const o=(y/4)%2?0:8;p(o,y,'#4A2A22',1,3)}});
T.winDark=tex(16,16,p=>{const r=rng(73);p(0,0,'#3D4148',16,16);p(2,3,'#0E1420',5,9);p(9,3,'#0E1420',5,9);p(2,3,'#1B2638',5,1);p(9,3,'#1B2638',5,1)});
T.winLit=tex(16,16,p=>{p(0,0,'#3D4148',16,16);p(2,3,'#FFCF70',5,9);p(9,3,'#0E1420',5,9);p(3,4,'#FFE6A8',2,3)});
T.car=noiseTex('#B23A3A',.12,74);T.carB=noiseTex('#2F5FA8',.12,75);T.tire=noiseTex('#1A1A1A',.2,76);
MAT.asphalt=M(T.asphalt);MAT.lane=[M(T.asphalt),M(T.asphalt),M(T.lane),M(T.asphalt),M(T.asphalt),M(T.asphalt)];MAT.walk=M(T.walk);MAT.tile=M(T.tile);
MAT.concrete=M(T.concrete);MAT.paint=M(T.paint);MAT.metal=M(T.metal);MAT.counter=M(T.counter);MAT.brickR=M(T.brickR);
MAT.winDark=M(T.winDark);MAT.winLit=M(T.winLit,{emissive:0xffffff,emissiveMap:T.winLit,emissiveIntensity:.0});
T.prod.forEach((t,k)=>{MAT['shelf'+k]=[M(t),M(t),M(T.metal),M(T.metal),M(T.metal),M(T.metal)]});
MAT.car=M(T.car);MAT.carB=M(T.carB);MAT.tire=M(T.tire);
MAT.glass=new THREE.MeshLambertMaterial({color:0x9FC9DD,transparent:true,opacity:.22,depthWrite:false});

/* ---------- world ---------- */
const world=new Map();const K=(x,y,z)=>x+','+y+','+z;
const set=(x,y,z,t)=>world.set(K(x,y,z),t);
const inStore=(x,z)=>x>=-11&&x<=11&&z>=-17&&z<=0;
for(let x=-34;x<=34;x++)for(let z=-17;z<=22;z++){
  let t='walk';if(inStore(x,z))t='tile';else if(z>=4&&z<=11)t=(z==8&&((x+40)%5)<3)?'lane':'asphalt';else if(z>=14)t='concrete';
  set(x,0,z,t);if(!inStore(x,z))set(x,-1,z,'concrete')}
// store shell
for(let y=1;y<=6;y++){for(let x=-11;x<=11;x++){
    const win=y<=3&&((x>=-9&&x<=-4)||(x>=4&&x<=9));const door=x>=-2&&x<=2&&y<=4;
    if(!door)set(x,y,0,win?'glass':'concrete');set(x,y,-17,'paint')}
  for(let z=-16;z<=-1;z++){set(-11,y,z,'paint');set(11,y,z,'paint')}}
for(let x=-11;x<=11;x++)for(let z=-17;z<=0;z++)set(x,7,z,'concrete');
// aisles (product faces look into the aisles) and checkouts
[[-8,0],[-5,1],[5,2],[8,0]].forEach(([x,k])=>{for(let z=-14;z<=-6;z++)for(let y=1;y<=3;y++)set(x,y,z,'shelf'+k)});
for(let x=-9;x<=-6;x++)set(x,1,-3,'counter');for(let x=6;x<=9;x++)set(x,1,-3,'counter');
// the block across the street: dark towers, a few lit windows
[[-30,-19,9],[-18,-9,13],[-8,-1,7],[0,8,11],[9,18,15],[19,30,8]].forEach(([a,b,h],bi)=>{const r=rng(80+bi);
  for(let x=a;x<=b;x++)for(let y=1;y<=h;y++){const edge=x==a||x==b;const w=!edge&&y%3==2&&(x-a)%3==1;set(x,y,14,w?(r()<.12?'winLit':'winDark'):'brickR');
    if(edge||y==h)for(let z=15;z<=19;z++)set(x,y,z,'brickR')}});
// two crashed cars
function car(x0,z0,m){for(let x=x0;x<x0+4;x++)for(let z=z0;z<z0+2;z++)set(x,1,z,m);set(x0+1,2,z0,m);set(x0+2,2,z0,m);set(x0+1,2,z0+1,m);set(x0+2,2,z0+1,m)}
car(-17,5,'car');car(13,9,'carB');
const MESHER_HOOK=1;
