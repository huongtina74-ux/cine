/* ===== Bin & Bo ep02 "Baby Zombie Lost His Home" — episode-specific code (assembled after the shared core) ===== */
T.roof=tex(16,16,(p)=>{const r=rng(41);for(let y=0;y<16;y++)for(let x=0;x<16;x++)p(x,y,shade('#D9483B',.85+r()*.25));for(let y=3;y<16;y+=4){p(0,y,'#8E2A22',16,1);for(let x=(y%8?2:6);x<16;x+=8)p(x,y-3,'#8E2A22',1,3)}});
T.wool=noiseTex('#F3F3F3',.08,42);T.redWool=noiseTex('#D32F2F',.12,43);
MAT.roof=M(T.roof);MAT.wool=M(T.wool);MAT.redWool=M(T.redWool);
MAT.glass=new THREE.MeshLambertMaterial({color:0xBFE8FF,transparent:true,opacity:.45});

/* ---------- world: meadow + Zu's site ---------- */
const world=new Map();const K=(x,y,z)=>x+','+y+','+z;
const set=(x,y,z,t)=>world.set(K(x,y,z),t);
const R=24;
const hgt=(x,z)=>{const r=Math.hypot(x,z);if(r<11)return 0;const n=Math.sin(x*.35)+Math.cos(z*.31)+Math.sin((x+z)*.2);return Math.max(0,Math.round((n+1.2)*clamp((r-11)/6)*1.4))};
for(let x=-R;x<=R;x++)for(let z=-R;z<=R;z++){const h=hgt(x,z);for(let y=-1;y<=h;y++)set(x,y,z,y==h?'grass':'dirt')}
for(let x=-14;x<=-10;x++)for(let z=-4;z<=-1;z++)if(hgt(x,z)==0)set(x,0,z,'sand');
const trees=[[-9,-7],[9,-8],[-13,1],[15,11],[-6,13],[10,15],[16,-3],[-17,-9],[2,-15],[-3,17],[-1,-9]];
trees.forEach(([x,z],i)=>{const b=hgt(x,z);const h=4+(i%2);for(let y=1;y<=h;y++)set(x,b+y,z,'log');
  for(let dx=-2;dx<=2;dx++)for(let dz=-2;dz<=2;dz++)for(let dy=h-1;dy<=h+1;dy++){if(Math.abs(dx)+Math.abs(dz)+(dy>h?1:0)>3)continue;if(dx==0&&dz==0&&dy<=h)continue;if(!world.has(K(x+dx,b+dy,z+dz)))set(x+dx,b+dy,z+dz,'leaves')}set(x,b+h+2,z,'leaves')});
const MESHER_HOOK=1;
