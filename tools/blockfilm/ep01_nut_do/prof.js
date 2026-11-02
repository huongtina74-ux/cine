const {chromium}=require('playwright');const fs=require('fs'),path=require('path'),http=require('http');
const ROOT=path.join(__dirname,'web');const srv=http.createServer((q,r)=>{fs.readFile(path.join(ROOT,q.url.split('?')[0]),(e,d)=>{if(e){r.writeHead(404);return r.end()}r.writeHead(200,{'content-type':q.url.split('?')[0].endsWith('.html')?'text/html':q.url.endsWith('.json')?'application/json':'application/octet-stream'});r.end(d)})});
(async()=>{await new Promise(r=>srv.listen(0,r));
const br=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const pg=await br.newPage({viewport:{width:1920,height:1080}});await pg.goto(`http://127.0.0.1:${srv.address().port}/index.html${process.env.Q||""}`);await pg.evaluate(()=>init());
for(const cfg of process.argv.slice(2)){
 const r=await pg.evaluate(cfg=>{eval(cfg);const gl=renderer.getContext();const px=new Uint8Array(4);let t0=performance.now();for(let i=0;i<4;i++){renderAt(6+i/30);gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px)}return (performance.now()-t0)/4},cfg);
 let t0=Date.now();for(let i=0;i<4;i++)await pg.screenshot({type:'jpeg',quality:92});
 console.log(cfg.slice(0,60),'render ms',r.toFixed(0),'shot ms',(Date.now()-t0)/4)}
await br.close();srv.close()})();
