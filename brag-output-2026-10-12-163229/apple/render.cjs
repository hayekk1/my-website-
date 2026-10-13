const { chromium } = require('playwright'); const fs = require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/apple.html');await p.evaluate(()=>document.fonts.ready);
const js=JSON.parse(fs.readFileSync('assets/laptop.json'));await p.evaluate(s=>setScreen(s),js.screen);
const mode=process.argv[2],fps=30,DUR=14.5;
const times=mode==='stills'?process.argv.slice(3).map(Number):[...Array(Math.round(DUR*fps)).keys()].map(i=>i/fps);
fs.mkdirSync('frames',{recursive:true});
for(let i=0;i<times.length;i++){const t=times[i];await p.evaluate(x=>render(x),t);
 await p.waitForFunction(()=>[...document.images].every(im=>im.complete&&im.naturalWidth>0));
 await p.screenshot({path:mode==='stills'?`st_${t}.png`:`frames/f${String(i).padStart(4,'0')}.png`});}
await b.close();})();
