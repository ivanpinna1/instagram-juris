const {chromium}=require('playwright');
const [,,a,b,step,outdir,mode]=process.argv;
(async()=>{const br=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await br.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
p.on('console',m=>{if(m.type()=='error')console.log('ERR',m.text())});p.on('pageerror',e=>console.log('PAGEERR',e.message));
await p.goto('http://127.0.0.1:8765/index.html');await p.waitForFunction('window.ready===true',{timeout:120000});
const fs=require('fs');fs.mkdirSync(outdir,{recursive:true});
if(mode=='list'){for(const t of a.split(',')){await p.evaluate(t=>window.frame(t),+t);await p.screenshot({path:`${outdir}/t${(+t).toFixed(2)}.jpg`,type:'jpeg',quality:85})}}
else{const fps=30;for(let i=+a;i<+b;i++){await p.evaluate(t=>window.frame(t),i/fps);await p.screenshot({path:`${outdir}/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92})}}
await br.close()})();
