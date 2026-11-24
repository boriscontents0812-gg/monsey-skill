// Run on https://rizz-template.vercel.app/ (tab in front) while card_server.py serves the post folder.
// Replace CHAT (the chat slide just before the card), LINE (the card's psychology line) and OUT.
const CHAT='slide-11.png', LINE="It's not about the like. It's about where your attention goes first.", OUT='rizz-card-raw.png';
let blob=null;for(let i=0;i<6&&!blob;i++){try{blob=await fetch('http://127.0.0.1:8766/'+CHAT).then(r=>{if(!r.ok)throw r.status;return r.blob()})}catch(e){await new Promise(r=>setTimeout(r,800))}}
if(!blob)throw 'no image';
const f=new File([blob],'chat.png',{type:'image/png'});const dt=new DataTransfer();dt.items.add(f);const inp=document.querySelector('#fileInput');inp.files=dt.files;inp.dispatchEvent(new Event('change',{bubbles:true}));
const ta=document.querySelector('textarea');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(ta,LINE);ta.dispatchEvent(new Event('input',{bubbles:true}));
await new Promise(r=>setTimeout(r,1500));
const el=document.getElementById('template');const pr=1320/el.offsetWidth;
const url=await Promise.race([htmlToImage.toPng(el,{cacheBust:true,pixelRatio:pr,style:{transform:'none',zoom:1}}),new Promise((_,rej)=>setTimeout(()=>rej('timeout'),40000))]);
const out=await fetch(url).then(r=>r.blob());
await fetch('http://127.0.0.1:8766/'+OUT,{method:'POST',body:out}).then(r=>r.text());
