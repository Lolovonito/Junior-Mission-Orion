(()=>{
try{
const _noop=Object.freeze(()=>{});
['log','info','debug','dir','table'].forEach((m)=>{try{console[m]=_noop;}catch(_){}});
}catch(_){}
const _ed=(t)=>!!(t&&(t.tagName==='INPUT'||t.tagName==='TEXTAREA'||t.isContentEditable));
document.addEventListener('contextmenu',(e)=>{if(!_ed(e.target)){e.preventDefault();e.stopPropagation();}},true);
document.addEventListener('dragstart',(e)=>{e.preventDefault();},true);
document.addEventListener('keydown',(e)=>{
const k=String(e.key||'').toUpperCase(),kc=e.keyCode||0,mod=!!(e.ctrlKey||e.metaKey);
if(k==='F12'||kc===123||(mod&&e.shiftKey&&'IJCK'.indexOf(k)>=0)||(mod&&!e.shiftKey&&!e.altKey&&'USP'.indexOf(k)>=0)){
e.preventDefault();e.stopPropagation();
}
},true);
})();
(()=>{const _$=((t,k)=>{const d=new TextDecoder(),c=[];return i=>{if(c[i]!==undefined)return c[i];const a=t[i],u=new Uint8Array(a.length);for(let j=0;j<a.length;j++)u[j]=a[j]^k[(i+j)%k.length]^((i*17+j*31+73)&255);return(c[i]=d.decode(u));};})([[14,231,227,5,193,129,251,65,168,235,115,21,137,23,13,9,123,202,14,36,190,187,23,56,213,219,99,5,153,7,29,84],[203,14,40,129,185,24,99,155,206],[19,45,189,133,8,120,148],[213,137,223,61],[142,222,40,155,224,180,86,249,165,98,52,240,10],[255,69,165,94,206,60,214,84,91,74],[102,187,91,135,35,215,8,77,81,223,73,65],[145,121,117,29,161,58,191,111,161,123,179],[118,101,15,162,103],[116,24,170,16],[249,145,25,155,151],[128,7,147,150,152,135,47],[17,239,163,100,142,42],[160,164,118,154,56,182,74],[237,79,110,14,215,103,246,115,209,55,198,27,141,71,219,197,198,71,111,9],[15,120,1,147,50,241,122,139,125,175,183,132,43,186,98,250,55],[24,233,224,6,154,153,252,76,224,169,135,26,228,54,253,59,120,170,182,67,128,185],[253,237,11,195],[12,63,175,177,11,99],[43,170,190,10,110,134],[210,136,100,207,253,241,78,225,244,49,117,181,91,239,105,216,151],[195,38,149,161,243,83,226,165,122,63,252,2,134,62,194,64],[70,173,75,138,62,217,104,66,75,198,232,142,86,231],[168,78,150,32,198,88],[126,157,23,165,125,249,120,172,196,102,109,156,86,12,68],[120,27,173,97,170,114,190,192],[25,174,114,167,128,133],[213,26,159,144,136,237,71,146,185,60,43,143,184,16,73,235],[76,132,159,131,171,77,243,24,23,83,167,15,47,104,158,120,58,248,224,45,142,32,176,70,27,73,179,64,109,55,199,103,33,165],[253,179,113,143,34,181,113,1,65,176],[164,126,131,53,161,65,17,77,218,56,220],[95,119,0,205,102,244,96,215,37,202,1,161],[40,20,208,114,227,40,137,124,200,28,155,51,249,38,164,109,24,247,224,30,210,152,181,2,187,253,131,34,228],[245,224,23,219,130,250,86,250,228,142,58],[176,65,198,144],[119,244,183,10],[187,190,0,116,158,215,97,27,137,76,94,68,124,204,105,221,158,207,52,199,178,180,74,181,244,126,47,247,26,170,43,133,140,195,45,149,191,241,0,186,183,32,112,247,1,167,4,235,119,253,85,165,74,193,112,141,71],[206,56,133,177,183,85,229,186,123,39,245,25],[30,154,168,161,67,168,171,111,33,255,30,134],[185,85,147,49,193,73,87,73,219,241,134,77,221,115,225,94,178,93,146,54],[71,134,50,246,67,86,92],[151,41,143,82,163,96,170],[55,188,98,172,121],[174,110,234,103,185,185,87,142,168,42,53],[0,137,192,131,171,91,140,186,32],[128,131,150,186,82,132,230,16,75,185,8,48,48],[176,110,174,36,181],[108,139,43,188,78,13],[101,15,206,103],[22,211,103,230,109],[225,29,206,150,254,78],[11,220,158,236],[172,177,30,101,137,201],[162,6,105,129,208,104],[55,129,182,177],[132,164,185,65],[175,180,57,156,94,91,71,217],[136,55,210,94,74,91,207,225],[38,194,65,76],[248,118,181,118,180,128,112],[77,162,100,176,220,108,140,187,43,53,158,228,50,67,237,156,6,138,133,151],[150,148,134,186],[149,146,190,82,131,161],[110,155,61,170,68,20],[203,99,228,5,71,20,185,10,101,116,227,1,153,148,152,93,110],[9,198,121,253,98,221,43,207],[209,110,194,101,202],[22,219,185,242,88],[195,142,194,86,226,226,139],[184,30,107,138,209,117],[3,119,142,192,112,0],[118,178,160,87,242,170,102,35,224,22],[189,160,66,229,169,106],[245,82,224,81,91,79,201,248,128],[57,209,89,91,87],[192,71,83,86,216,199,111],[81,178,116,160,204],[173,122,186,207,118],[143,132,163,79,138,163,61],[186,187,90,146,178,36],[147,49,164,94,3,103,173,3,33,60,213],[103,239,28,83,11,254,69,106,106,156,91,142,134,148,27,36,95,159,46,184,38,136,126,135,91],[159,44,169,46,144,119,128,64,235,8,228,138,143,3,55,74,135,57,178,37,157,97,155,77,250],[102,224,124,198],[219,147,255,79],[130,238,74,234],[73,108,199,224,100,16,150,4,11,65,63,197,69,55,166,162,22,113,213,154,96,91,200,162,195,81,123,143,85,61,227,241,96,206,189,160,18,251,183,102,45,228,23,169,55,209,211,212,32,222,251,229,16,179],[100,132,217,97],[217,219,8,212,170,113,38,249,25,231,39,217,153,213,53,139,175,168,66,238,240,43,58,163,70,21,230,128,37,5,36,155,182,176,149,2,82,20,75,216,251,151,77,249,115,245,24],[175,84,222,190,109],[78,225,133,112,73],[221,87,78,65,207],[64,67,71,219,226,144,104,156],[254,196,116,156],[124,165,222,107,102,222,12,79,148,254,16,11,245,156,12,152,145,131,244,72,138,185,124,34,128,238,6,70,173,169,7,140,155,135,165,85,156,176,44,111,159,27,55,44,221,103,117,221,173,114,137,34,170,90,94,127,183,23,38,59,141,119,45,236,177,112,153,62,166,11,15,65,193,43,202,17],[142,168,89,143,187,50,51,143,233,4,89,171,149,4,134,212,152,161,77,155,183,35,105,129,227,52,41],[162,91,176,176,44,9,140,230,4],[4,161,90,7,89,182,0],[185,64,46,80,168,59,36,41,203],[126,245,72,214,36,214,14,175,94,254,211,204,76]],[111,255,22,198,98,0,138,16,196,249,105,239,65,168,147,119]);(()=>{
"use strict";
const reduceMotion=window.matchMedia(_$(0)).matches;
const toggle=document.getElementById(_$(1));
const menu=document.getElementById(_$(2));
const setMenu=(open)=>{
menu.classList.toggle(_$(3),open);
toggle.setAttribute(_$(4),String(open));
toggle.setAttribute(_$(5),open?_$(6):_$(7));
};
toggle.addEventListener(_$(8),()=>setMenu(!menu.classList.contains(_$(9))));
menu.addEventListener(_$(10),(e)=>{if(e.target.closest("a"))setMenu(false);});
document.addEventListener(_$(11),(e)=>{if(e.key===_$(12))setMenu(false);});
const reveals=document.querySelectorAll(_$(13));
if(_$(14)in window&&!reduceMotion){
const io=new IntersectionObserver((entries)=>{
entries.forEach((en)=>{
if(en.isIntersecting){en.target.classList.add("in");io.unobserve(en.target);}
});
},{threshold:0.12,rootMargin:_$(15)});
reveals.forEach((el)=>io.observe(el));
}else{
reveals.forEach((el)=>el.classList.add("in"));
}
const links=[...document.querySelectorAll(_$(16))];
const map=new Map(links.map((a)=>[a.getAttribute(_$(17)).slice(1),a]));
const spy=new IntersectionObserver((entries)=>{
entries.forEach((en)=>{
if(en.isIntersecting){
links.forEach((l)=>l.classList.remove(_$(18)));
const a=map.get(en.target.id);
if(a)a.classList.add(_$(19));
}
});
},{rootMargin:_$(20)});
document.querySelectorAll(_$(21)).forEach((s)=>spy.observe(s));
const bar=document.getElementById(_$(22));
const header=document.getElementById(_$(23));
const parallaxEls=document.querySelectorAll(_$(24));
let ticking=false;
const onScroll=()=>{
if(ticking)return;
ticking=true;
requestAnimationFrame(()=>{
const y=window.scrollY;
const max=document.documentElement.scrollHeight-window.innerHeight;
bar.style.transform=`scaleX(${max>0?y/max:0})`;
header.classList.toggle(_$(25),y>24);
if(!reduceMotion){
parallaxEls.forEach((el)=>{
el.style.transform=`translate3d(0, ${y*-parseFloat(el.dataset.parallax)}px, 0)`;
});
}
ticking=false;
});
};
window.addEventListener(_$(26),onScroll,{passive:true});
onScroll();
if(reduceMotion)document.querySelectorAll(_$(27)).forEach((s)=>s.pauseAnimations&&s.pauseAnimations());
const finePointer=window.matchMedia(_$(28)).matches;
if(finePointer&&!reduceMotion){
const glow=document.getElementById(_$(29));
window.addEventListener(_$(30),(e)=>{
glow.classList.add("on");
glow.style.transform=`translate3d(${e.clientX}px, ${e.clientY}px, 0)`;
},{passive:true});
document.addEventListener(_$(31),()=>glow.classList.remove("on"));
document.querySelectorAll(_$(32)).forEach((el)=>{
el.addEventListener(_$(33),(e)=>{
const r=el.getBoundingClientRect();
const px=(e.clientX-r.left)/r.width,py=(e.clientY-r.top)/r.height;
el.style.setProperty(_$(34),`${px*100}%`);
el.style.setProperty(_$(35),`${py*100}%`);
el.style.transition=_$(36);
el.style.transform=`perspective(800px) rotateX(${(0.5-py)*7}deg) rotateY(${(px-0.5)*9}deg) translateY(-6px)`;
});
el.addEventListener(_$(37),()=>{el.style.transition="";el.style.transform="";});
});
}
const counters=document.querySelectorAll(_$(38));
const runCount=(el)=>{
const target=parseInt(el.dataset.count,10)||0;
if(reduceMotion){el.textContent=target;return;}
const t0=performance.now(),dur=1400;
const step=(now)=>{
const p=Math.min(1,(now-t0)/dur);
el.textContent=Math.round(target*(1-Math.pow(1-p,3)));
if(p<1)requestAnimationFrame(step);
};
requestAnimationFrame(step);
};
if(_$(39)in window){
const co=new IntersectionObserver((es)=>es.forEach((e)=>{if(e.isIntersecting){runCount(e.target);co.unobserve(e.target);}}),{threshold:0.6});
counters.forEach((c)=>co.observe(c));
}else counters.forEach(runCount);
const rot=document.getElementById(_$(40));
if(rot&&!reduceMotion){
const words=[_$(41),_$(42),_$(43),_$(44),_$(45)];
let wi=0,ci=words[0].length,del=true,wait=0;
const tick=()=>{
const w=words[wi];
if(wait>0){wait--;return setTimeout(tick,60);}
if(del){
ci--;rot.textContent=w.slice(0,ci);
if(ci<=0){del=false;wi=(wi+1)%words.length;wait=4;}
return setTimeout(tick,55);
}
const nw=words[wi];
ci++;rot.textContent=nw.slice(0,ci);
if(ci>=nw.length){del=true;wait=32;}
setTimeout(tick,85);
};
setTimeout(tick,2200);
}
const toTop=document.getElementById(_$(46));
if(toTop){
window.addEventListener(_$(47),()=>toTop.classList.toggle(_$(48),window.scrollY>700),{passive:true});
toTop.addEventListener(_$(49),()=>{
toTop.classList.add(_$(50));
window.scrollTo({top:0,behavior:reduceMotion?_$(51):_$(52)});
setTimeout(()=>toTop.classList.remove(_$(53)),1100);
});
}
const boot=document.getElementById(_$(54));
if(boot){
const started=performance.now();
const closeBoot=()=>{
const wait=Math.max(0,1500-(performance.now()-started));
setTimeout(()=>{
boot.classList.add(_$(55));
try{sessionStorage.setItem(_$(56),"1");}catch(e){}
setTimeout(()=>boot.remove(),900);
},wait);
};
if(document.readyState===_$(57))closeBoot();else window.addEventListener(_$(58),closeBoot,{once:true});
}
const dotLinks=[...document.querySelectorAll(_$(59))];
if(dotLinks.length&&_$(60)in window){
const byId=new Map(dotLinks.map((a)=>[a.getAttribute(_$(61)).slice(1),a]));
const dio=new IntersectionObserver((entries)=>{
entries.forEach((en)=>{
if(en.isIntersecting){
dotLinks.forEach((d)=>d.classList.remove(_$(62)));
const a=byId.get(en.target.id);
if(a)a.classList.add(_$(63));
}
});
},{rootMargin:_$(64)});
byId.forEach((_,id)=>{const s=document.getElementById(id);if(s)dio.observe(s);});
}
const lb=document.getElementById(_$(65));
if(lb){
const lbImg=document.getElementById(_$(66)),lbCap=document.getElementById(_$(67)),lbClose=document.getElementById(_$(68));
let lastFocus=null;
const open=(img)=>{
lastFocus=document.activeElement;
lbImg.src=img.currentSrc||img.src;lbImg.alt=img.alt;
const cap=img.closest(_$(69))&&img.closest(_$(70)).querySelector(_$(71));
lbCap.textContent=cap?cap.textContent:"";
lb.hidden=false;document.body.style.overflow=_$(72);lbClose.focus();
};
const close=()=>{lb.hidden=true;document.body.style.overflow="";if(lastFocus)lastFocus.focus();};
document.querySelectorAll(_$(73)).forEach((img)=>{
img.addEventListener(_$(74),()=>open(img));
img.addEventListener(_$(75),(e)=>{if(e.key===_$(76)||e.key===" "){e.preventDefault();open(img);}});
});
lb.addEventListener(_$(77),(e)=>{if(e.target!==lbImg)close();});
document.addEventListener(_$(78),(e)=>{if(e.key===_$(79)&&!lb.hidden)close();});
}
const evEl=document.getElementById(_$(80));
if(evEl){
const START=Date.parse(_$(81));
const END=Date.parse(_$(82));
const pad=(n)=>String(n).padStart(2,"0");
const update=()=>{
const now=Date.now();
evEl.classList.remove(_$(83),_$(84));
if(now<START){
const s=Math.floor((START-now)/1000);
evEl.innerHTML=`Faltan <b>${Math.floor(s/86400)}d ${pad(Math.floor(s%86400/3600))}:${pad(Math.floor(s%3600/60))}:${pad(s%60)}</b> para el evento`;
}else if(now<=END){
evEl.classList.add(_$(85));
evEl.innerHTML=_$(86);
}else{
evEl.classList.add(_$(87));
evEl.innerHTML=_$(88);
}
};
update();
setInterval(update,1000);
}
const dlApk=document.getElementById(_$(89));
const dlExe=document.getElementById(_$(90));
if(dlApk&&dlExe&&_$(91)in window){
const formatSize=(bytes)=>{
if(!bytes)return"";
if(bytes<1024*1024)return`${Math.round(bytes/1024)} KB`;
return`${(bytes/(1024*1024)).toFixed(1)} MB`;
};
const applyAsset=(btn,metaEl,asset,platformLabel,tag)=>{
if(!btn||!asset||!asset.browser_download_url)return;
btn.href=asset.browser_download_url;
btn.setAttribute(_$(92),asset.name||"");
const sizeText=formatSize(asset.size);
const verLabel=tag?`${platformLabel} · ${tag}`:platformLabel;
if(metaEl)metaEl.textContent=verLabel;
btn.title=`Descargar ${asset.name} (${verLabel}${sizeText?_$(93)+sizeText:""})`;
};
fetch(_$(94),{
headers:{Accept:_$(95)}
})
.then((res)=>(res.ok?res.json():null))
.then((rel)=>{
if(!rel||!Array.isArray(rel.assets))return;
const tag=rel.tag_name||"";
const apk=rel.assets.find((a)=>/\.apk$/i.test(a.name||""));
const exe=rel.assets.find((a)=>/\.exe$/i.test(a.name||""));
applyAsset(dlApk,document.getElementById(_$(96)),apk,_$(97),tag);
applyAsset(dlExe,document.getElementById(_$(98)),exe,"PC",tag);
const relLink=document.getElementById(_$(99));
if(relLink&&tag&&rel.html_url){
relLink.href=rel.html_url;
relLink.textContent=tag;
}
})
.catch(()=>{});
}
})();})();