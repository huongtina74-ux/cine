// blockfilm factory renderer (headless Chromium + swiftshader, 1080x1920 @30).
//   node render.js WEB_DIR cues   out.json              -> {total, cues, seg} for the audio and the edit
//   node render.js WEB_DIR stills out_dir t1 t2 ...      -> jpg stills
//   node render.js WEB_DIR video  out.mp4 t0 t1          -> one segment
//   node render.js WEB_DIR pvideo out.mp4 WORKERS        -> whole Short, WORKERS segments in parallel, then concat
const {chromium}=require('playwright');const {spawn}=require('child_process');const fs=require('fs');const path=require('path');const http=require('http');
const [ROOTARG,mode,out,...rest]=process.argv.slice(2);const ROOT=path.resolve(ROOTARG);
const types={'.html':'text/html','.js':'application/javascript','.json':'application/json','.woff2':'font/woff2'};
async function page(){
  const srv=http.createServer((q,r)=>{const f=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end()}r.writeHead(200,{'content-type':types[path.extname(f)]||'application/octet-stream'});r.end(d)})});
  await new Promise(r=>srv.listen(0,r));const port=srv.address().port;
  const br=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const pg=await br.newPage({viewport:{width:1080,height:1920}});
  pg.on('console',m=>{if(m.type()=='error'||m.type()=='warning')console.log('PAGE',m.type(),m.text())});pg.on('pageerror',e=>{console.log('PAGEERR',e.message);process.exitCode=2});
  await pg.goto(`http://127.0.0.1:${port}/index.html`);const total=await pg.evaluate(()=>window.init());
  return {pg,total,close:async()=>{await br.close();srv.close()}}}
async function segment(pg,total,file,t0,t1){t1=Math.min(t1,total);const tmp=file.replace(/\.mp4$/,'.part.mp4');
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30',tmp],{stdio:['pipe','inherit','inherit']});
  const f0=Math.round(t0*30),f1=Math.round(t1*30);const st=Date.now();
  for(let i=f0;i<f1;i++){await pg.evaluate(t=>renderAt(t),i/30);const buf=await pg.screenshot({type:'jpeg',quality:92});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if((i-f0)%90==0)console.log(path.basename(file),i-f0,'/',f1-f0,((Date.now()-st)/1000/(i-f0+1)).toFixed(2),'s/frame')}
  ff.stdin.end();const code=await new Promise(r=>ff.on('close',r));if(code===0)fs.renameSync(tmp,file);return code}
(async()=>{
  if(mode=='pvideo'){ // probe the length, split into WORKERS child processes, concat
    const {pg,total,close}=await page();await close();const k=Math.max(1,+rest[0]||2);const step=Math.ceil(total*30/k)/30;const parts=[];const st=Date.now();
    await Promise.all([...Array(k).keys()].map(i=>new Promise((res,rej)=>{const f=out.replace(/\.mp4$/,`.seg${i}.mp4`);parts.push(f);
      const c=spawn(process.execPath,[__filename,ROOTARG,'video',f,String(i*step),String(Math.min(total,(i+1)*step))],{stdio:'inherit'});c.on('close',x=>x===0?res():rej(new Error('segment '+i+' failed')))})));
    const lst=out.replace(/\.mp4$/,'.concat.txt');fs.writeFileSync(lst,parts.map(p=>`file '${path.resolve(p)}'`).join('\n'));
    await new Promise((res,rej)=>{const c=spawn('ffmpeg',['-y','-loglevel','error','-f','concat','-safe','0','-i',lst,'-c','copy',out],{stdio:'inherit'});c.on('close',x=>x===0?res():rej(new Error('concat')))});
    parts.forEach(p=>fs.unlinkSync(p));fs.unlinkSync(lst);console.log('PVIDEO_OK',out,total,'s in',((Date.now()-st)/1000).toFixed(0),'s');return}
  const {pg,total,close}=await page();
  if(mode=='cues'){const c=await pg.evaluate(()=>window.CUES_EXPORT());fs.writeFileSync(out,JSON.stringify(c,null,1));console.log('CUES_OK',out,c.total)}
  else if(mode=='stills'){fs.mkdirSync(out,{recursive:true});for(const t of rest){await pg.evaluate(t=>renderAt(+t),t);await pg.screenshot({path:`${out}/f_${(+t).toFixed(2)}.jpg`,type:'jpeg',quality:85});console.log('still',t,await pg.evaluate(t=>SHOT(+t),t))}}
  else if(mode=='video'){const code=await segment(pg,total,out,+rest[0],+rest[1]);if(code!==0)process.exitCode=1}
  await close()})().catch(e=>{console.error(e);process.exit(1)});
