// usage: node render.js mode args
// mode stills: node render.js stills out_dir t1 t2 ...
// mode video:  node render.js video out.mp4 t0 t1
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');const path=require('path');const http=require('http');
const ROOT=path.join(__dirname,'web');
const types={'.html':'text/html','.js':'application/javascript','.json':'application/json','.woff2':'font/woff2'};
const srv=http.createServer((q,r)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end()}r.writeHead(200,{'content-type':types[path.extname(f)]||'application/octet-stream'});r.end(d)})});
(async()=>{
  await new Promise(r=>srv.listen(0,r));const port=srv.address().port;
  const br=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const pg=await br.newPage({viewport:{width:1080,height:1920}});
  pg.on('console',m=>{if(m.type()=='error'||m.type()=='warning')console.log('PAGE',m.type(),m.text())});pg.on('pageerror',e=>console.log('PAGEERR',e.message));
  await pg.goto(`http://127.0.0.1:${port}/index.html`);
  const total=await pg.evaluate(()=>window.init());
  const [mode,out,...rest]=process.argv.slice(2);
  if(mode=='overlay'){ // overlay canvas only (no 3D), transparent PNG frames -> .mov (png codec, alpha) for compositing over a Mine-imator render
    const t0=+rest[0],t1=Math.min(+rest[1],total);const n=Math.round((t1-t0)*30);
    const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','png','-i','-','-c:v','png','-pix_fmt','rgba',out],{stdio:['pipe','inherit','inherit']});
    for(let i=0;i<n;i++){const url=await pg.evaluate(t=>{drawOverlay(t);return ov.canvas.toDataURL('image/png')},t0+i/30);const buf=Buffer.from(url.split(',')[1],'base64');if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%90==0)console.log('overlay',i,'/',n)}
    ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));console.log('done',out,code)}
  else if(mode=='stills'){fs.mkdirSync(out,{recursive:true});for(const t of rest){await pg.evaluate(t=>renderAt(+t),t);await pg.screenshot({path:`${out}/f_${(+t).toFixed(2)}.jpg`,type:'jpeg',quality:85});console.log('still',t)}}
  else{const t0=+rest[0],t1=Math.min(+rest[1],total);const tmp=out.replace(/\.mp4$/,'.part.mp4');
    const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30',tmp],{stdio:['pipe','inherit','inherit']});
    const n=Math.round((t1-t0)*30);const st=Date.now();
    for(let i=0;i<n;i++){const t=t0+i/30;await pg.evaluate(t=>renderAt(t),t);const buf=await pg.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%60==0)console.log(out,i,'/',n,((Date.now()-st)/1000/(i+1)).toFixed(2),'s/frame')}
    ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));if(code===0)fs.renameSync(tmp,out);console.log('done',out,code)}
  console.log('TOTAL',total);await br.close();srv.close()})();
