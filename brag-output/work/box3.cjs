const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/video3.html');await p.evaluate(()=>document.fonts.ready);
for(const [id,t] of [['post',9.2],['ab0',11.4]]){await p.evaluate(x=>render(x),t);
console.log(id,JSON.stringify(await p.evaluate(i=>{const r=document.getElementById(i).getBoundingClientRect();return [Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)]},id)));}
await b.close();})();
