const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch({proxy:{server:process.env.HTTPS_PROXY},args:['--ignore-certificate-errors']});
for (const f of ['index.html','simulator.html']) for (const w of [360,375,390,412,768,1024,1280,1440]){
const p=await b.newPage({viewport:{width:w,height:900}});await p.goto('file://'+process.cwd()+'/'+f);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
const res=await p.evaluate(()=>{const out=[];for(const el of document.querySelectorAll('h1,h2,h3,h4,p,li,dd,dt,small,span,a,button,label,td,th,div')){
 if(![...el.childNodes].some(n=>n.nodeType==3&&n.textContent.trim()))continue; if(el.offsetParent===null)continue;
 // gather chars with their line top, splitting segments by <br>
 const lines=[];let seg=[];const r=document.createRange();
 const walk=(n)=>{for(const c of n.childNodes){if(c.nodeName=='BR'){lines.push(seg);seg=[];}else if(c.nodeType==3){for(let i=0;i<c.length;i++){if(!c.textContent[i].trim())continue;r.setStart(c,i);r.setEnd(c,i+1);const rc=r.getClientRects()[0];if(rc)seg.push([Math.round(rc.top),c.textContent[i]]);}}else if(c.nodeType==1&&getComputedStyle(c).display.startsWith('inline'))walk(c);}};
 walk(el);lines.push(seg);
 for(const s of lines){const tops=[...new Set(s.map(x=>x[0]))];if(tops.length<2)continue;const last=s.filter(x=>x[0]==tops[tops.length-1]);if(last.length<=2)out.push(el.tagName+'.'+el.className+' | '+s.map(x=>x[1]).join('').slice(0,40)+' -> 마지막줄: '+last.map(x=>x[1]).join(''));}
}return out;});
for(const x of res)console.log(f,w,x);await p.close();}
await b.close();})();
