const { chromium } = require('playwright');
(async()=>{
const [,, mode, ...ts] = process.argv;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' }).catch(()=>chromium.launch());
const p = await b.newPage({ viewport: { width: +(process.env.W||1920), height: +(process.env.H||1080) } });
await p.goto('file://' + process.cwd() + '/'+(process.env.HTML||'video.html'));
await p.evaluate(() => document.fonts.ready);
if (mode === 'boxes') {
  await p.evaluate(()=>render(12));
  for (const id of ['chipP','post','ab1','s0','s4','desc']) {
    if(id==='chipP'||id==='post'||id==='desc') await p.evaluate(()=>render(8));
    if(id==='ab1') await p.evaluate(()=>render(12));
    if(id[0]==='s') await p.evaluate(()=>render(16.6));
    console.log(id, JSON.stringify(await p.evaluate(i=>{const r=document.getElementById(i).getBoundingClientRect();return [Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)]},id)));
  }
} else if (mode === 'stills') {
  for (const t of ts) { await p.evaluate(x=>render(x), +t); await p.screenshot({ path: `st2_${t}.png` }); }
} else {
  const fps=30, N=Math.round((+process.env.DUR||21)*fps);
  for (let i=0;i<N;i++){ await p.evaluate(x=>render(x), i/fps); await p.screenshot({ path: (process.env.FR||'frames')+`/f${String(i).padStart(4,'0')}.png` }); }
}
await b.close();
})();
