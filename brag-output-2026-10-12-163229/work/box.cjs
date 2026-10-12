const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/video.html');await p.evaluate(()=>document.fonts.ready);
for(const t of [1.0]){await p.evaluate(x=>{render(x);$('cam').setAttribute('transform','')},t);
for(const id of ['fc','fc_milk','fc_esp','fc_ice1','fc_cond','sam_root','rus_root'])console.log(id,JSON.stringify(await p.evaluate(i=>{const r=document.getElementById(i).getBoundingClientRect();return [r.x,r.y,r.width,r.height].map(Math.round)},id)));}
await b.close();})();
