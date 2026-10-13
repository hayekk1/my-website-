const { chromium } = require('playwright'); const fs = require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/comp.html');await p.evaluate(()=>document.fonts.ready);
const pts=fs.existsSync('out/orbit_pts.json')?JSON.parse(fs.readFileSync('out/orbit_pts.json')):[];
await p.evaluate(d=>{PTS=d;},pts);
const mode=process.argv[2];const fps=30;
const times=mode==='stills'?process.argv.slice(3).map(Number):[...Array(Math.round(22.2*fps)).keys()].map(i=>i/fps);
fs.mkdirSync('comp',{recursive:true});
const lo=+(process.env.LO||0),hi=+(process.env.HI||1e9);
for(let i=0;i<times.length;i++){if(mode!=='stills'&&(i<lo||i>hi))continue;const t=times[i];await p.evaluate(x=>render(x),t);
 await p.waitForFunction(()=>[...document.images].filter(im=>im.style.display!=='none'&&im.getAttribute('src')).every(im=>im.complete&&im.naturalWidth>0));
 await p.screenshot({path:mode==='stills'?`still_${t}.png`:`comp/f${String(i).padStart(4,'0')}.png`});}
await b.close();})();
