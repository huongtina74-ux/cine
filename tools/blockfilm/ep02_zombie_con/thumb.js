const {chromium}=require('playwright');const fs=require('fs'),path=require('path'),http=require('http');
const ROOT=path.join(__dirname,'web');const T={'.html':'text/html','.json':'application/json','.js':'application/javascript','.woff2':'font/woff2'};
const srv=http.createServer((q,r)=>{const f=path.join(ROOT,q.url.split('?')[0]);fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end()}r.writeHead(200,{'content-type':T[path.extname(f)]||'application/octet-stream'});r.end(d)})});
(async()=>{await new Promise(r=>srv.listen(0,r));const br=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const pg=await br.newPage({viewport:{width:1920,height:1080}});pg.on('pageerror',e=>console.log(e.message));await pg.goto(`http://127.0.0.1:${srv.address().port}/index.html`);await pg.evaluate(()=>init());
await pg.evaluate(()=>renderThumb());await pg.screenshot({path:'out/thumb_full.png'});await br.close();srv.close()})();
