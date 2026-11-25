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
(()=>{const _$=((t,k)=>{const d=new TextDecoder(),c=[];return i=>{if(c[i]!==undefined)return c[i];const a=t[i],u=new Uint8Array(a.length);for(let j=0;j<a.length;j++)u[j]=a[j]^k[(i+j)%k.length]^((i*17+j*31+73)&255);return(c[i]=d.decode(u));};})([[63,123,218,50,69,184,219,67,86,94,36,146,24,164,4,158,74,86,55,19,58,130,55,58,43,110,52,130,8,180,20,195],[87,55,31,5,128,56,97,101,123],[42,26,57,188,40,122,106],[226,13,230,29],[10,231,8,153,30,1,1,126,52,209,61,103,59],[198,101,167,160,123,107,81,197,232,67],[70,176,184,51,112,2,212,246,83,83],[157,149,215,77,116,230,4,109,45],[136,208,88,37,246],[193,79,45,129],[174,22,136,40,158],[7,150,32,159,15,182,179],[128,92,170,243,191,182],[19,173,225,171,164,143,125],[228,216,95,146,238,80,114,74,241,53,56,174,218,192,74,118,207,208,94,149],[152,73,157,170,5,117,67,171,127,81,2,211,172,43,209,243,160],[41,117,217,49,30,160,220,78,30,28,208,157,117,133,244,172,73,54,143,116,4,128],[97,212,60,71],[53,8,43,136,43,97],[28,46,135,42,108,120],[86,177,68,205,3,68,25,102,101,130,124,34,106,115,80,239,19],[250,6,151,95,70,4,101,52,201,54,107,51,26,7,245,196],[102,175,181,63,105,94,249,241,66,81,217,18,111,208],[170,176,35,119,65,201],[128,40,64,34,236,74,113,59,245,250,84,171,210,53,100],[205,76,42,240,25,123,41,241],[78,41,227,20,137,18],[82,139,44,153,31,220,219,171,142,184,18,175,186,238,252,188],[221,55,150,20,154,209,202,47,147,106,135,13,209,221,201,255,171,75,233,186,191,188,137,113,159,112,147,66,147,130,144,224,176,22],[78,186,230,190,190,140,70,133,120,144],[173,233,178,169,152,118,149,116,250,58,34],[200,70,156,244,81,112,89,247,39,52,180,246],[25,136,233,69,103,17,169,126,54,169,204,180,104,149,173,250,41,107,217,41,86,161,149,0,69,72,212,165,117],[105,217,32,95,187,218,84,4,81,217,189],[137,118,66,169],[64,112,142,42],[63,135,32,118,96,98,54,156,24,255,87,211,77,80,80,234,26,246,20,197,76,1,29,50,101,205,38,96,43,54,18,178,8,250,13,151,65,68,87,61,38,147,121,96,48,59,61,220,243,196,117,167,180,116,39,10,214],[247,24,135,79,2,2,98,43,200,46,98,40],[62,152,86,20,20,47,58,220,40,104,47,26],[187,171,38,102,70,216,228,64,76,192,26,116,234,247,216,126,176,163,39,97],[185,51,101,113,210,229,85],[58,119,77,175,40,104,51,235],[96,59,243,24],[56,251,28,59,53,143,212,164,136,175,16,182],[156,32,156,0,207,213,181,139,190,7,164],[51,154,19,221,214,161,131,149,99,132],[185,249,159,184,140],[251,186,183,133,121,137],[84,147,247,80],[138,234,80,98,84],[216,42,74,175,222,76],[60,88,167,204],[40,136,62,103,119,124],[155,38,107,127,101,63],[23,131,72,4],[134,90,12,22],[81,1,110,27,207,232,78,78],[61,96,85,207,249,82,88,208],[113,69,208,255],[127,231,6,127,35,177,236],[220,17,109,39,237,240,181,140,175,12,190,230,204,246,186,27,151,57,140,0],[37,157,17,139],[156,5,143,206,186,150],[249,170,161,147,115,144],[250,255,221,50,195,45,153,8,155,193,180,134,8,39,145,202,95],[149,255,78,121,91,253,41,49],[232,89,70,92,234],[33,95,128,210,90],[71,183,226,84,28,87,220],[129,62,105,116,100,34],[35,117,112,117,39,135],[116,76,21,0,117,59,213,42,119,39],[67,21,21,98,56,217],[64,5,103,192,232,70,94,201,28],[110,86,200,232,94],[71,214,224,95,79,246,243],[192,1,125,55,253],[30,115,45,254,234],[134,19,146,211,179,148,185],[45,138,198,171,133,160],[162,173,157,105,135,94,141,1,223,137,130],[251,214,43,215,50,222,71,148,223,203,220,31,53,157,140,21,195,166,25,60,31,168,124,121,238],[166,27,45,23,176,117,126,245,188,143,117,57,134,148,6,214,190,14,54,28,189,99,101,248,173],[81,100,69,230],[95,170,223,77],[187,206,72,20],[105,110,57,85,51,151,7,183,77,159,5,23,44,17,56,142,55,121,100,115,105,205,27,237,93,36,204,7,2,28,49,156,24,142,66,2,69,35,125,65,205,133,122,98,80,163,69,185,87,202],[102,122,108,54],[39,110,95,83,59,194,47,110,103,56,23,234,3,225,28,148,78,24,77,41,63,137,113,200,224,107,5,254,16,238,0,159,85,76,96,85,206,232,76,74,203,18,107,207,246,201,56],[80,11,125,50,218,122,109,54,61,15,246,15,236,79,216,91,26,17,38,198,246,10,79,202,22,120],[30,102,56,216,78],[78,204,252,95,85,252,12,114],[150,237,86,87,203,6,124,166,205,32],[78,125,59,248,229,91,147,198,52,76,219,133],[51,52,244,242,88,182,138,55,186,232,226],[12,155,212,180,150,179,4,169,239],[133,206,169,148,171,24,173],[170,149,123,158,99,147],[150,126,156,120,151,17],[69,104,71,222,47,57],[99,64,229,28,58,183,237],[162,217,3,52,101],[236,82,3,69,199,177,124,144,233,175,116,105,227,49,84,188,39,122,98,98],[115,71,81,7,177,45,134,43,177,35,126,22,40,27,164,11,83,71,81,7,177,45,134,43,177,35,21,123,71,118,207,126,36,18,74,90,55,110,135,108,36,119],[106,110,56,135,80,187,16,136,18,71],[32,44,141,44,209,46,115,43,116,30,236,16,235,95,200,76,7,10,122,45,218,32],[5,117,44,206],[68,28,244,30],[196,237,70,71,219],[205,109,107,247,36,77,229],[98,52,225,242,95,183,222,63,64,207],[7,219,207,111,150,241,18,125,247,214],[149,212,173,147,182],[251,137,172,149,58],[156,100,136],[85,162,68,195,51,233,202,172,195,129,114,136],[111,64,242,32],[99,194,29,25,136,216,236,120,90,230],[193,73,6,93],[118,48,99,254],[31,73,44,153],[90,10,181,48],[51,139,2,186],[82,2,250,10,48,2,29,35,222,40,179,34,170,109,57],[38,218,58,118,48,49,88,218,255],[196,65,64,200,3,109,196,234,195,110,177,191,9,117,83,210,239,73,65,207],[19,85,222,4,120,220,245,148,91,195],[118,250,240,89,177,218,57,22,204,148,207,86],[255,228,69,178],[148,251,154,180,12,171,233,251,179,167],[162,151,174,2,165],[107,145,98,128,2],[198,33,212,93,147,212,137,246,245,18,236,178,250,227,160,95,99],[110,249,58,36,164,244,213,68,121,198,219,67,190,252,82,108,69,241,59,35],[234,58,49,237,230,193,75,118,216,200],[96,80,2,211,172,43,209,243,160],[6,93,216,168,61,201,177,185,114,104,220,62,76,179,133,16,29,67,46,130,8,181],[0,220,164,6,181],[41,159,12,164,35,135,23,74,43],[154,26,189,30,143],[41,192,40,118,42,55,13,250,31,244,5,153,71,5],[201,54,105,56,52,30,245,248,211,114],[78,90,194,20,119],[73,204,17,101],[244,246,87,168,199,37],[234,67,183,213,58,93],[164,132,182,15,169,225,253,253,163,14,132,57],[141,162,26,173,238,248,248,183,9,146,47,158],[178,107,133,13,209,135,140,253,177,70,166,252,128,177,147,122,153,99,132,10],[45,143,17,199,131,133]],[94,99,47,241,230,57,170,18,58,76,62,104,208,27,154,224]);(()=>{
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
evEl.innerHTML=`<b>${Math.floor(s/86400)}d ${pad(Math.floor(s%86400/3600))}:${pad(Math.floor(s%3600/60))}:${pad(s%60)}</b> until the event starts`;
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
document.querySelectorAll(_$(89)).forEach((b)=>{
b.addEventListener(_$(90),(e)=>e.preventDefault());
});
const routeMap=document.getElementById(_$(91));
if(routeMap){
const live=routeMap.querySelector(_$(92));
const rocket=routeMap.querySelector(_$(93));
const nodes=[...routeMap.querySelectorAll(_$(94))];
const total=live.getTotalLength();
live.style.strokeDasharray=total;
const at=nodes.map((n)=>{
const cx=+n.dataset.cx,cy=+n.dataset.cy;
let best=0,bd=Infinity;
for(let l=0;l<=total;l+=3){const pt=live.getPointAtLength(l);const d=(pt.x-cx)**2+(pt.y-cy)**2;if(d<bd){bd=d;best=l;}}
return best/total;
});
const draw=(p)=>{
live.style.strokeDashoffset=total*(1-p);
const l=total*p,a=live.getPointAtLength(l),b=live.getPointAtLength(Math.min(total,l+3));
const ang=Math.atan2(b.y-a.y,b.x-a.x)*180/Math.PI;
rocket.setAttribute(_$(95),`translate(${a.x} ${a.y}) rotate(${ang}) scale(1.15)`);
nodes.forEach((n,i)=>n.classList.toggle(_$(96),p>=at[i]-0.01));
};
const onRoute=()=>{
const r=routeMap.getBoundingClientRect(),vh=window.innerHeight;
const p=Math.max(0,Math.min(1,(vh*0.85-r.top)/(vh*0.85-r.height*0.1+r.height*0.4)));
draw(reduceMotion?1:p);
};
let routeTick=false;
window.addEventListener(_$(97),()=>{if(routeTick)return;routeTick=true;requestAnimationFrame(()=>{routeTick=false;onRoute();});},{passive:true});
window.addEventListener(_$(98),onRoute);
onRoute();
}
const hudMet=document.getElementById(_$(99)),hudDist=document.getElementById(_$(100));
if(hudMet&&hudDist&&!reduceMotion){
const t0=performance.now(),D0=367200,V=10700/3600;
const pad2=(n)=>String(n).padStart(2,"0");
setInterval(()=>{
const s=(performance.now()-t0)/1000;
hudMet.textContent=`MET T+${pad2(Math.floor(s/3600))}:${pad2(Math.floor(s%3600/60))}:${pad2(Math.floor(s%60))}`;
hudDist.textContent=`${Math.max(0,Math.round(D0-s*V)).toLocaleString(_$(101))} km TO GO`;
},250);
}
if(!reduceMotion&&_$(102)in window){
const glyphs=_$(103);
const decode=(el)=>{
const finalTxt=el.textContent;el.setAttribute(_$(104),finalTxt);
let f=0;const steps=24;
const id=setInterval(()=>{
f++;
el.textContent=[...finalTxt].map((ch,i)=>(ch===" "||i<(f/steps)*finalTxt.length)?ch:glyphs[(Math.random()*glyphs.length)|0]).join("");
if(f>=steps){clearInterval(id);el.textContent=finalTxt;}
},32);
};
const eio=new IntersectionObserver((es)=>es.forEach((e)=>{if(e.isIntersecting){decode(e.target);eio.unobserve(e.target);}}),{threshold:0.8});
document.querySelectorAll(_$(105)).forEach((el)=>eio.observe(el));
}
const SECTORS=[
[_$(106),_$(107),200],[_$(108),_$(109),188],[_$(110),_$(111),268],[_$(112),_$(113),28],
[_$(114),_$(115),168],[_$(116),_$(117),238],[_$(118),_$(119),318],[_$(120),_$(121),205],[_$(122),_$(123),46],
];
const hud=document.getElementById(_$(124));
if(hud&&_$(125)in window){
const noEl=hud.querySelector(_$(126)),nameEl=hud.querySelector(_$(127));
let current=_$(128);
const setSector=(id)=>{
const i=SECTORS.findIndex((s)=>s[0]===id);
if(i<0||id===current)return;
current=id;
noEl.textContent=`SECTOR ${String(i+1).padStart(2,"0")}`;
nameEl.textContent=SECTORS[i][1];
document.documentElement.style.setProperty(_$(129),SECTORS[i][2]);
hud.classList.remove(_$(130));void hud.offsetWidth;hud.classList.add(_$(131));
};
const sio=new IntersectionObserver((es)=>es.forEach((e)=>{if(e.isIntersecting)setSector(e.target.id);}),{rootMargin:_$(132)});
SECTORS.forEach(([id])=>{const el=document.getElementById(id);if(el)sio.observe(el);});
}
if(_$(133)in window){
const oio=new IntersectionObserver((es)=>es.forEach((e)=>e.target.classList.toggle(_$(134),!e.isIntersecting)),{rootMargin:_$(135)});
document.querySelectorAll(_$(136)).forEach((s)=>oio.observe(s));
}
const clipBtns=[...document.querySelectorAll(_$(137))];
const mainVideo=document.getElementById(_$(138));
if(clipBtns.length){
const vids=clipBtns.map((b)=>b.querySelector(_$(139)));
clipBtns.forEach((b,i)=>{
const vid=vids[i],s=+b.dataset.start,e=+b.dataset.end;
vid.addEventListener(_$(140),()=>{vid.currentTime=s;});
vid.addEventListener(_$(141),()=>{if(vid.currentTime>=e||vid.currentTime<s-0.4)vid.currentTime=s;});
b.addEventListener(_$(142),()=>{
if(!mainVideo)return;
mainVideo.currentTime=s;mainVideo.play().catch(()=>{});
mainVideo.scrollIntoView({behavior:reduceMotion?_$(143):_$(144),block:_$(145)});
});
b.addEventListener(_$(146),()=>{if(!reduceMotion)vid.play().catch(()=>{});});
b.addEventListener(_$(147),()=>{if(!b._vis)vid.pause();});
});
if(!reduceMotion&&_$(148)in window){
const MAX=3;
const refresh=()=>{
let n=0;
clipBtns.forEach((b,i)=>{
if(b._vis&&n<MAX){n++;vids[i].play().catch(()=>{});}
else if(!b.matches(_$(149)))vids[i].pause();
});
};
const cio=new IntersectionObserver((es)=>{es.forEach((en)=>{en.target._vis=en.isIntersecting;});refresh();},{threshold:0.35});
clipBtns.forEach((b)=>cio.observe(b));
}
}
})();})();