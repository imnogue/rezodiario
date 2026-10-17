/* Rezo Diario · JS compartido por todas las páginas */
(function(){
"use strict";
const RD=window.RD||{};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const ROOT=document.body.dataset.root||"";const X=document.body.dataset.clean==="1"?"":".html";const IDX=X?"index.html":"";
const SYNC_KEYS=/^rd-(rezado|favs|nov-|reto-|mycandles)/;
const store={get(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}if(SYNC_KEYS.test(k)&&window.__rdSync)window.__rdSync()}};
function toast(t){let h=$("#toastHost");if(!h){h=document.createElement("div");h.id="toastHost";document.body.appendChild(h)}h.innerHTML="";const d=document.createElement("div");d.className="toast";d.setAttribute("role","status");d.textContent=t;h.appendChild(d);setTimeout(()=>d.remove(),3000)}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function norm(s){return String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"")}
function splitS(t){return t.split(/(?<=[.!?»])\s+/).filter(Boolean)}
const now=new Date();
const ISO=`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,"0")}-${String(now.getDate()).padStart(2,"0")}`;
const WEEK=RD.week||[];
const CFG=window.RD_CONFIG||{};
let todayIdx=WEEK.findIndex(d=>d.date===ISO);const isReal=todayIdx>=0;if(todayIdx<0){todayIdx=WEEK.findIndex(d=>d.date===CFG.today);if(todayIdx<0)todayIdx=Math.max(0,WEEK.length-1)}

/* ---------- Tema ---------- */
const root=document.documentElement;
const savedT=store.get("rd-tema",null);if(savedT)root.setAttribute("data-theme",savedT);
function isDark(){const t=root.getAttribute("data-theme");return t?t==="dark":matchMedia("(prefers-color-scheme: dark)").matches}
const tb=$("#btnTheme");if(tb)tb.onclick=()=>{const t=isDark()?"light":"dark";root.setAttribute("data-theme",t);store.set("rd-tema",t);document.dispatchEvent(new Event("rd-theme"))};

/* ---------- Idiomas ---------- */
const LANGS=[["es","Español","ES"],["ca","Català","CA"],["gl","Galego","GL"],["eu","Euskara","EU"],["en","English","EN"],["pt","Português","PT"],["it","Italiano","IT"],["fr","Français","FR"],["de","Deutsch","DE"],["pl","Polski","PL"]];
const I18N={
 es:{today:"Hoy",verses:"Versículos",prayers:"Oraciones",rosary:"Rosario",gospel:"Evangelio",saints:"Santos",novenas:"Novenas",candles:"Velas",donate:"Donar",listen:"Escuchar el rezo de hoy",light:"Enciende una vela",more:"Más",note:""},
 ca:{today:"Avui",verses:"Versicles",prayers:"Oracions",rosary:"Rosari",gospel:"Evangeli",saints:"Sants",novenas:"Novenes",candles:"Espelmes",donate:"Donar",listen:"Escolta la pregària d'avui",light:"Encén una espelma",more:"Més",note:"Les oracions en català arribaran aviat. De moment, el contingut és en castellà."},
 gl:{today:"Hoxe",verses:"Versículos",prayers:"Oracións",rosary:"Rosario",gospel:"Evanxeo",saints:"Santos",novenas:"Novenas",candles:"Velas",donate:"Doar",listen:"Escoita a oración de hoxe",light:"Acende unha vela",more:"Máis",note:"As oracións en galego chegarán pronto. Polo de agora, o contido está en castelán."},
 eu:{today:"Gaur",verses:"Bertsetak",prayers:"Otoitzak",rosary:"Arrosarioa",gospel:"Ebanjelioa",saints:"Santuak",novenas:"Bederatziurrenak",candles:"Kandelak",donate:"Dohaintza",listen:"Entzun gaurko otoitza",light:"Piztu kandela bat",more:"Gehiago",note:"Euskarazko otoitzak laster iritsiko dira. Oraingoz, edukia gaztelaniaz dago."},
 en:{today:"Today",verses:"Verses",prayers:"Prayers",rosary:"Rosary",gospel:"Gospel",saints:"Saints",novenas:"Novenas",candles:"Candles",donate:"Donate",listen:"Listen to today's prayer",light:"Light a candle",more:"More",note:"Prayers in English are coming soon. For now, the content is in Spanish."},
 pt:{today:"Hoje",verses:"Versículos",prayers:"Orações",rosary:"Terço",gospel:"Evangelho",saints:"Santos",novenas:"Novenas",candles:"Velas",donate:"Doar",listen:"Ouça a oração de hoje",light:"Acenda uma vela",more:"Mais",note:"As orações em português chegam em breve. Por enquanto, o conteúdo está em espanhol."},
 it:{today:"Oggi",verses:"Versetti",prayers:"Preghiere",rosary:"Rosario",gospel:"Vangelo",saints:"Santi",novenas:"Novene",candles:"Candele",donate:"Dona",listen:"Ascolta la preghiera di oggi",light:"Accendi una candela",more:"Altro",note:"Le preghiere in italiano arriveranno presto. Per ora i contenuti sono in spagnolo."},
 fr:{today:"Aujourd'hui",verses:"Versets",prayers:"Prières",rosary:"Chapelet",gospel:"Évangile",saints:"Saints",novenas:"Neuvaines",candles:"Bougies",donate:"Faire un don",listen:"Écouter la prière du jour",light:"Allumer une bougie",more:"Plus",note:"Les prières en français arrivent bientôt. Pour l'instant, le contenu est en espagnol."},
 de:{today:"Heute",verses:"Bibelverse",prayers:"Gebete",rosary:"Rosenkranz",gospel:"Evangelium",saints:"Heilige",novenas:"Novenen",candles:"Kerzen",donate:"Spenden",listen:"Gebet des Tages anhören",light:"Eine Kerze anzünden",more:"Mehr",note:"Gebete auf Deutsch folgen bald. Derzeit sind die Inhalte auf Spanisch."},
 pl:{today:"Dziś",verses:"Wersety",prayers:"Modlitwy",rosary:"Różaniec",gospel:"Ewangelia",saints:"Święci",novenas:"Nowenny",candles:"Świece",donate:"Wesprzyj",listen:"Posłuchaj dzisiejszej modlitwy",light:"Zapal świecę",more:"Więcej",note:"Modlitwy po polsku już wkrótce. Na razie treści są po hiszpańsku."}
};
let lang=store.get("rd-lang","es");if(!I18N[lang])lang="es";
function applyLang(){
 const d=I18N[lang];root.lang=lang;
 $$("[data-i18n]").forEach(el=>{const v=d[el.dataset.i18n];if(v)el.textContent=v});
 const lb=$("#langCode");if(lb)lb.textContent=lang.toUpperCase();
 $$("#langMenu button").forEach(b=>b.setAttribute("aria-checked",b.dataset.l===lang));
 let n=$("#langNote");
 if(lang!=="es"&&!store.get("rd-langnote-"+lang,false)){
  if(!n){n=document.createElement("div");n.id="langNote";n.className="lang-note";n.setAttribute("role","status");document.querySelector(".top").after(n)}
  n.innerHTML=`<div class="wrap"><span>${esc(d.note)}</span><button aria-label="Cerrar aviso">✕</button></div>`;
  n.querySelector("button").onclick=()=>{store.set("rd-langnote-"+lang,true);n.remove()};
 }else if(n)n.remove();
}
const lm=$("#langMenu"),lbtn=$("#btnLang");
if(lm&&lbtn){
 lm.innerHTML=LANGS.map(([c,n,code])=>`<button role="menuitemradio" data-l="${c}" aria-checked="false"><span>${n}</span><small>${code}</small></button>`).join("");
 lbtn.onclick=e=>{e.stopPropagation();lm.hidden=!lm.hidden;lbtn.setAttribute("aria-expanded",!lm.hidden)};
 lm.addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;lang=b.dataset.l;store.set("rd-lang",lang);applyLang();lm.hidden=true;lbtn.setAttribute("aria-expanded","false")});
 document.addEventListener("click",e=>{if(!lm.hidden&&!e.target.closest(".lang"))lm.hidden=true});
 document.addEventListener("keydown",e=>{if(e.key==="Escape")lm.hidden=true});
}
applyLang();

/* ---------- Menú lateral ---------- */
const dr=$("#drawer");
function openDrawer(){dr.hidden=false;document.body.style.overflow="hidden";setTimeout(()=>{const a=dr.querySelector("a");a&&a.focus({preventScroll:true})},60)}
function closeDrawer(){dr.hidden=true;document.body.style.overflow=""}
$$("[data-drawer]").forEach(b=>b.addEventListener("click",e=>{e.preventDefault();openDrawer()}));
if(dr){dr.querySelectorAll("[data-close]").forEach(b=>b.onclick=closeDrawer);document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!dr.hidden)closeDrawer()});
 dr.querySelectorAll("a").forEach(a=>a.addEventListener("click",closeDrawer))}

/* ---------- Animaciones al entrar ---------- */
const rv=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add("rise");rv.unobserve(e.target)}}),{threshold:.1});
$$(".reveal").forEach(el=>rv.observe(el));
function dragRail(el){if(!el)return;let down=false,x0=0,s0=0;
 el.addEventListener("pointerdown",e=>{if(e.pointerType!=="mouse")return;down=true;x0=e.clientX;s0=el.scrollLeft;el.dataset.moved="0"});
 window.addEventListener("pointermove",e=>{if(!down)return;const dx=e.clientX-x0;if(Math.abs(dx)>6){el.dataset.moved="1";el.classList.add("drag")}el.scrollLeft=s0-dx});
 window.addEventListener("pointerup",()=>{if(!down)return;down=false;el.classList.remove("drag");setTimeout(()=>el.dataset.moved="0",30)});
 el.addEventListener("click",e=>{if(el.dataset.moved==="1"){e.preventDefault();e.stopPropagation()}},true);
}
$$(".rail").forEach(dragRail);
$$("[data-scroll]").forEach(b=>b.onclick=()=>{const r=document.getElementById(b.dataset.scroll);r.scrollBy({left:+b.dataset.dir*r.clientWidth*.8,behavior:"smooth"})});
function swipe(el,onX){let x0=null,y0=0,t0=0;
 el.addEventListener("pointerdown",e=>{x0=e.clientX;y0=e.clientY;t0=Date.now()});
 el.addEventListener("pointerup",e=>{if(x0===null)return;const dx=e.clientX-x0,dy=e.clientY-y0;x0=null;if(Date.now()-t0>900)return;if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.4)onX(dx<0?1:-1)});
 el.addEventListener("pointercancel",()=>x0=null);
}

/* ---------- Voz ---------- */
const synth=("speechSynthesis" in window)?window.speechSynthesis:null;let voice=null;
function pickVoice(){if(!synth)return;const v=synth.getVoices();voice=v.find(x=>/es[-_]ES/i.test(x.lang))||v.find(x=>/^es/i.test(x.lang))||null}
if(synth){pickVoice();try{synth.onvoiceschanged=pickVoice}catch(e){}}
const sp={on:false,token:0};
function speakText(text,onEnd){
 if(!synth){toast("Tu navegador no puede leer en voz alta.");return false}
 if(P.playing)pauseP();
 const my=++sp.token;synth.cancel();const parts=splitS(text.replace(/\n+/g," "));let i=0;
 const next=()=>{if(my!==sp.token)return;if(i>=parts.length){sp.on=false;onEnd&&onEnd();return}const u=new SpeechSynthesisUtterance(parts[i++]);u.lang="es-ES";if(voice)u.voice=voice;u.rate=.92;u.onend=next;u.onerror=()=>{sp.on=false;onEnd&&onEnd()};synth.speak(u)};
 sp.on=true;next();return true;
}
function stopSpeech(){sp.token++;if(sp.on&&synth)try{synth.cancel()}catch(e){};sp.on=false}

/* ---------- Racha ---------- */
function doneDays(){return store.get("rd-rezado",[])}
function markDone(dt){const s=doneDays();const d=new Date(),t=d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");[dt,t].forEach(x=>{if(x&&!s.includes(x))s.push(x)});store.set("rd-rezado",s);renderWeek();document.dispatchEvent(new Event("rd-rezado"))}

/* ---------- Reproductor del rezo diario ---------- */
const P={items:[],segs:[],k:0,playing:false,token:0,timer:null,dog:null,rate:1,mus:store.get("rd-musica","calma"),voiceOn:store.get("rd-voz",true),done:false,day:null};
function est(t){return t.split(/\s+/).length*0.43/P.rate+1.2}
function isQ(t){return /\?$/.test(t)}
function segmentsFor(d){return [
 {name:"Entrar en silencio",text:"Busca un lugar tranquilo y ponte cómodo. Respira despacio: inspira… y suelta el aire. Estás en la presencia de Dios. Él te mira con cariño."},
 {name:"Evangelio · "+d.ref,text:d.sum+" «"+d.ex+"»"},
 {name:"Reflexión",text:d.refl+" "+d.qs.join(" ")},
 {name:"Oración final",text:d.fin+" "+RD.GL}]}
function totalMin(){return Math.max(1,Math.round(P.items.reduce((a,it)=>a+est(it.t)+(isQ(it.t)?25:1.6),0)/60+.6))}
function remaining(){let s=0;for(let i=P.k;i<P.items.length;i++)s+=est(P.items[i].t)+(isQ(P.items[i].t)?25:1.6);return Math.max(1,Math.round(s/60))}
function loadPlayer(d){
 stopPlayer();P.day=d;P.segs=segmentsFor(d);P.items=[];P.done=false;
 if(d.audio&&d.marcas&&d.marcas.length){d.marcas.forEach(m=>P.items.push({si:m[1],t:m[2],at:m[0]}))}else P.segs.forEach((s,si)=>splitS(s.text).forEach(t=>P.items.push({si,t})));P.k=0;
 if(AU&&AU.dataset.d!==d.date){AU.pause();AU=null}const pl=$("#player");if(pl)pl.classList.toggle("live",!!d.audio);
 $("#pills").innerHTML=P.segs.map((s,i)=>`<button class="pill" data-seg="${i}"><b></b><span>${s.name.split(" · ")[0]}</span></button>`).join("");
 $$("#pills .pill").forEach(b=>b.onclick=()=>jumpSeg(+b.dataset.seg));
 $("#pTitle").textContent=d.title;const fd=$("#fDur");if(fd)fd.textContent=(d.audio&&d.duracion)?d.duracion:totalMin()+" min";
 const tm=$("#tMusic"),tv=$("#tVoice");if(tm&&tv){const mixed=!!d.audio&&!d.audioVoz;tm.hidden=mixed;tv.hidden=mixed}
 renderP(true);
}
function renderP(first){
 if(!$("#player"))return;const it=P.items[P.k];
 $("#player").classList.toggle("playing",P.playing);
 $("#pSeg").textContent=P.segs[it.si].name;
 const el=$("#pText");const txt=P.done?"Amén. Gracias por rezar hoy.":(first&&!P.playing&&P.k===0?"Pulsa el botón y respira. Te acompañamos.":it.t);
 if(el.textContent!==txt){if(P.day&&P.day.audio){setText(el,txt)}else{el.classList.add("fade");setTimeout(()=>{el.textContent=txt;el.classList.remove("fade")},220)}}
 if(!(P.day&&P.day.audio&&AU))$$("#pills .pill").forEach((b,i)=>{const its=P.items.filter(x=>x.si===i);const idx=P.items.indexOf(its[0]);let w=P.k>idx?Math.min(1,(P.k-idx)/its.length):0;if(P.done)w=1;b.style.setProperty("--w",w*100+"%");b.classList.toggle("on",i===it.si)});
 $("#pTime").textContent=P.done?"Completado":(P.k===0&&!P.playing?totalMin()+" min":"Quedan "+remaining()+" min");
 $("#pPlay").innerHTML=P.playing?'<svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M7 5h4v14H7zM13 5h4v14h-4z"/></svg>':'<svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l12.5-7.5z"/></svg>';
 $("#pPlay").setAttribute("aria-label",P.playing?"Pausar":"Reproducir");
 const cta=$("#ctaPlay");if(cta)cta.lastChild.textContent=P.playing?"Pausar el rezo":(I18N[lang].listen||"Escuchar el rezo de hoy");
 const mt=$("#miniT");if(mt){mt.textContent=P.day.title;$("#miniS").textContent=P.segs[it.si].name}
 updateMini();
}
function clearT(){clearTimeout(P.timer);clearTimeout(P.dog)}
function speakCur(){
 clearT();const my=++P.token;const it=P.items[P.k];renderP();const dur=est(it.t)*1000;
 if(P.voiceOn&&synth){try{synth.cancel();const u=new SpeechSynthesisUtterance(it.t);u.lang="es-ES";if(voice)u.voice=voice;u.rate=P.rate*.92;u.pitch=.95;const t0=Date.now();
   u.onend=()=>{if(my!==P.token)return;if(Date.now()-t0<Math.min(600,dur/4)){P.timer=setTimeout(()=>advance(my),dur);return}advance(my)};
   u.onerror=()=>{if(my!==P.token)return;P.timer=setTimeout(()=>advance(my),dur)};
   synth.speak(u);P.dog=setTimeout(()=>{if(my===P.token)advance(my)},dur*2.4+4000)}catch(e){P.timer=setTimeout(()=>advance(my),dur)}}
 else P.timer=setTimeout(()=>advance(my),dur);
}
function advance(my){if(my!==P.token||!P.playing)return;clearT();const prev=P.items[P.k].si;if(P.k>=P.items.length-1){finishP();return}
 const q=isQ(P.items[P.k].t);P.k++;const gap=P.items[P.k].si!==prev?10000:(q?25000:1600);renderP();P.timer=setTimeout(()=>{if(my===P.token&&P.playing)speakCur()},gap)}
let AU=null,raf=0;
function setText(el,txt){el.textContent=txt;el.classList.remove("txtin");void el.offsetWidth;el.classList.add("txtin")}
function segBounds(){const D=AU&&AU.duration||0;const st=[0,0,0,0];for(let i=1;i<4;i++){const f=P.items.find(x=>x.si===i&&x.at!=null);st[i]=f?Math.max(0,f.at-1.5):D*i/4}return st.map((a,i)=>[a,i<3?st[i+1]:D])}
function tickAudio(){if(!AU||!AU.duration)return;const t=AU.currentTime,D=AU.duration;const hasM=P.items.length&&P.items[0].at!=null;
 let k=0;if(hasM){for(let i=0;i<P.items.length;i++){if(P.items[i].at<=t+0.15)k=i;else break}}else k=Math.min(P.items.length-1,Math.floor(t/D*P.items.length));
 const B=segBounds();let curSeg=0;$$("#pills .pill").forEach((b,i)=>{const[a,e]=B[i];const w=Math.max(0,Math.min(1,(t-a)/Math.max(.1,e-a)));b.style.setProperty("--w",(w*100).toFixed(2)+"%");if(t>=a)curSeg=i});
 $$("#pills .pill").forEach((b,i)=>b.classList.toggle("on",i===curSeg));
 const seg=$("#pSeg");if(seg&&P.segs[curSeg])seg.textContent=P.segs[curSeg].name;
 const before=hasM&&t+0.15<P.items[0].at;
 if(k!==P.k||P.__first){P.k=k;P.__first=false}const el=$("#pText");const txt=before?"Respira despacio…":P.items[k].t;if(el.textContent!==txt)setText(el,txt);
 $("#pTime").textContent="Quedan "+Math.max(1,Math.round((D-t)/60))+" min";
 const ms=$("#miniS");if(ms&&P.segs[curSeg])ms.textContent=P.segs[curSeg].name}
function loopAudio(){tickAudio();if(AU&&!AU.paused)raf=requestAnimationFrame(loopAudio)}
function auSrc(d){const u=d.audioVoz||d.audio;return (/^https?:/.test(u)?"":"/")+u.replace(/^\//,"")}
function playP(){acInit();if(P.day&&P.day.audio){playAudio();return}if(P.done){P.k=0;P.done=false}stopSpeech();P.playing=true;amb(true);speakCur()}
function playAudio(){stopSpeech();if(!AU||AU.dataset.d!==P.day.date){if(AU)AU.pause();AU=new Audio(auSrc(P.day));AU.dataset.d=P.day.date;AU.dataset.v=P.day.audioVoz?"1":"";AU.preload="auto";
  AU.addEventListener("play",()=>{cancelAnimationFrame(raf);loopAudio();if(AU.dataset.v)amb(true)});AU.addEventListener("pause",()=>{if(!P.playing)amb(false)});AU.addEventListener("seeked",tickAudio);AU.addEventListener("loadedmetadata",tickAudio);
  AU.addEventListener("ended",()=>{P.playing=false;finishP()});AU.addEventListener("error",()=>{toast("No se ha podido cargar el audio. Usamos la voz del navegador.");P.day=Object.assign({},P.day,{audio:""});playP()})}
 AU.playbackRate=P.rate;AU.muted=!!AU.dataset.v&&!P.voiceOn;P.playing=true;AU.play().catch(()=>{P.playing=false;renderP()});renderP()}
function stopPlayer(){P.playing=false;P.token++;clearT();if(synth)try{synth.cancel()}catch(e){};amb(false);if(AU)AU.pause()}
function pauseP(){stopPlayer();renderP()}
function finishP(){P.playing=false;P.done=true;P.token++;amb(false);markDone(P.day.date);renderP();toast("Rezo completado. Que tengas un buen día.")}
function jumpSeg(si){const idx=P.items.findIndex(x=>x.si===si);if(idx<0)return;P.done=false;P.k=idx;if(AU&&P.day.audio&&AU.duration){AU.currentTime=segBounds()[si][0];tickAudio();return}if(P.playing)speakCur();else{P.token++;renderP()}}
/* Música de fondo: bucles sin cortes con Web Audio (static/musica/*.mp3) */
const MUSICAS=[["calma","Calma"],["piano","Piano"],["organo","Órgano"],["campanas","Campanas"],["lluvia","Lluvia"],["no","Sin música"]];
let ac=null,master=null,msrc=null,mbuf={},mcur="";
async function musBuf(k){if(mbuf[k])return mbuf[k];const r=await fetch(ROOT+"musica/"+k+".mp3");const ab=await r.arrayBuffer();mbuf[k]=await new Promise((ok,ko)=>ac.decodeAudioData(ab,ok,ko));return mbuf[k]}
function acInit(){try{if(!ac){const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;ac=new AC();master=ac.createGain();master.gain.value=0;master.connect(ac.destination)}if(ac.state!=="running")ac.resume()}catch(e){}}
async function amb(on){try{
 const mixed=P.day&&P.day.audio&&!P.day.audioVoz;if(mixed||P.mus==="no")on=false;
 if(on)acInit();
 if(!ac)return;const now=ac.currentTime;master.gain.cancelScheduledValues(now);master.gain.setValueAtTime(master.gain.value,now);
 if(!on){master.gain.setTargetAtTime(0,now,.4);return}
 ac.resume();const k=P.mus;
 if(mcur!==k||!msrc){const buf=await musBuf(k);if(P.mus!==k||!P.playing)return;
  const old=msrc;if(old){const og=old.__g;og.gain.setTargetAtTime(0,ac.currentTime,.5);setTimeout(()=>{try{old.stop()}catch(e){}},2500)}
  const g=ac.createGain();g.gain.value=0;g.connect(master);const s=ac.createBufferSource();s.buffer=buf;s.loop=true;s.connect(g);s.__g=g;s.start(0,Math.random()*buf.duration*.8);g.gain.setTargetAtTime(1,ac.currentTime,.8);msrc=s;mcur=k}
 master.gain.setTargetAtTime(P.voiceOn||!P.day?.85:1.6,ac.currentTime,1.2)}catch(e){}}
function renderMus(){const l=$("#tMusicL");if(l)l.textContent=(MUSICAS.find(m=>m[0]===P.mus)||MUSICAS[0])[1];const mm=$("#musMenu");if(mm)mm.innerHTML=MUSICAS.map(([k,n])=>`<button role="menuitemradio" aria-checked="${k===P.mus}" data-mus="${k}">${k===P.mus?"✓ ":""}${n}</button>`).join("")}
let playerVisible=true;
function updateMini(){const m=$("#mini");if(m)m.hidden=!(P.playing&&!playerVisible)}
if($("#player")){
 const dayAttr=document.body.dataset.day;let di=dayAttr?WEEK.findIndex(d=>d.date===dayAttr):todayIdx;if(di<0)di=todayIdx;
 window.__rdDay=di;
 $("#pPlay").onclick=()=>P.playing?pauseP():playP();
 const cta=$("#ctaPlay");if(cta)cta.onclick=()=>{if(P.playing){pauseP();return}$("#player").scrollIntoView({behavior:"smooth",block:"center"});playP()};
 $("#pNext").onclick=()=>{const si=P.items[P.k].si;if(si<P.segs.length-1)jumpSeg(si+1)};
 $("#pPrev").onclick=()=>{const si=P.items[P.k].si;jumpSeg(Math.max(0,si-(P.items.findIndex(x=>x.si===si)===P.k?1:0)))};
 const RATES=[1,1.15,.85];let ri=0;
 $("#tSpeed").onclick=e=>{ri=(ri+1)%RATES.length;P.rate=RATES[ri];if(AU)AU.playbackRate=P.rate;e.currentTarget.textContent="Velocidad "+String(P.rate).replace(".",",")+"×"};
 const mm=$("#musMenu"),tmb=$("#tMusic");renderMus();
 tmb.onclick=e=>{e.stopPropagation();mm.hidden=!mm.hidden;tmb.setAttribute("aria-expanded",!mm.hidden)};
 mm.onclick=e=>{const b=e.target.closest("[data-mus]");if(!b)return;P.mus=b.dataset.mus;store.set("rd-musica",P.mus);renderMus();mm.hidden=true;tmb.setAttribute("aria-expanded","false");
  if(P.playing)amb(true);else if(P.mus!=="no"){toast("Música: "+(MUSICAS.find(m=>m[0]===P.mus)||[])[1]+". Suena al pulsar play.")}};
 document.addEventListener("click",e=>{if(!mm.hidden&&!e.target.closest(".mus")){mm.hidden=true;tmb.setAttribute("aria-expanded","false")}});
 const tvb=$("#tVoice");const paintV=()=>{tvb.setAttribute("aria-pressed",P.voiceOn);tvb.textContent=P.voiceOn?"Voz guía":"Sin voz"};paintV();
 tvb.onclick=()=>{const audioV=P.day&&P.day.audioVoz;if(!audioV&&!synth){toast("Tu navegador no tiene voz: el texto avanza solo.");return}
  P.voiceOn=!P.voiceOn;store.set("rd-voz",P.voiceOn);paintV();
  if(AU&&AU.dataset.v)AU.muted=!P.voiceOn;else if(P.playing)speakCur();
  if(P.playing)amb(true);toast(P.voiceOn?"Voz guía activada":"Sin voz: el texto avanza solo con la música")};
 new IntersectionObserver(es=>{playerVisible=es[0].isIntersecting;updateMini()},{threshold:.15}).observe($("#player"));
 const mb=$("#miniBtn");if(mb)mb.onclick=pauseP;
 selectDay(di);
}
function selectDay(i){
 const d=WEEK[i];if(!d)return;window.__rdDay=i;
 const set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v};
 set("hDate",`${d.wd}, ${d.n} de ${d.mes} de ${d.date.slice(0,4)}`);
 const hl=$("#hLit");if(hl)hl.innerHTML=`<i class="dot" style="background:${RD.LITC[d.color][0]}"></i><span>${esc(d.lit)}</span>`;
 set("fRef",d.ref);set("fSet","Misterios "+RD.SETS[d.set].name.toLowerCase());
 const gl=$("#gLink");if(gl)gl.href=ROOT+"evangelio/"+d.date+X;
 set("gTitle",d.title);set("gQuote",d.ex);set("gRefL",d.refL);
 loadPlayer(d);renderWeek();
}

/* ---------- Semana ---------- */
function renderWeek(){
 const w=$("#week");if(!w)return;const s=doneDays();const sel=window.__rdDay;
 const link=w.dataset.mode==="link";
 const lo=Math.max(0,todayIdx-6),hi=Math.min(WEEK.length,todayIdx+8);
 w.innerHTML=WEEK.map((d,i)=>{if(i<lo||i>=hi)return"";const inner=`<span class="wd">${d.wd}<i class="dot" style="background:${RD.LITC[d.color][0]}" title="${RD.LITC[d.color][1]}"></i></span><span class="num">${d.n} <small style="font-size:14px;font-family:var(--f-ui);color:var(--muted)">${d.mes.slice(0,3)}</small></span><span class="t">${esc(d.title)}</span><span class="r">${d.ref}</span><span class="tags">${i===todayIdx&&isReal?'<span class="tag today">Hoy</span>':""}${s.includes(d.date)?'<span class="tag">✓ Rezado</span>':""}</span>`;
  return link?`<a class="day${i===sel?" sel":""}" role="listitem" href="${ROOT}evangelio/${d.date}${X}" style="text-decoration:none;color:inherit">${inner}</a>`:`<button class="day${i===sel?" sel":""}" role="listitem" data-i="${i}" aria-pressed="${i===sel}">${inner}</button>`}).join("");
 if(!link)$$("#week .day").forEach(b=>b.onclick=()=>selectDay(+b.dataset.i));
 const st=$("#streak");if(st){let n=0;for(let i=todayIdx;i>=0;i--){if(s.includes(WEEK[i].date))n++;else if(i<todayIdx)break}st.innerHTML=n?`Llevas <b>${n} ${n===1?"día":"días"}</b> seguidos rezando`:"Empieza tu racha de oración hoy"}
}
if($("#week")&&!$("#player")){window.__rdDay=WEEK.findIndex(d=>d.date===document.body.dataset.day);renderWeek()}
setTimeout(()=>{const w=$("#week"),c=w&&w.querySelector(".day.sel");if(c)w.scrollLeft=Math.max(0,c.offsetLeft-w.offsetLeft-(w.clientWidth-c.offsetWidth)/2)},80);

/* ---------- ¿Qué llevas hoy en el corazón? · acompañante de oración ----------
   Todo se decide aquí, en el navegador, con el contenido de Rezo Diario: no se envía nada a ningún servidor
   y no se inventa ningún texto religioso. Cada «intención» tiene sus palabras clave, una frase de acogida
   escrita por el equipo, las oraciones que encajan, un versículo (si tiene sentido) y la categoría de la vela. */
if($("#askForm")){
 const PR=RD.prayers;const byS=s=>PR.find(p=>p.slug===s);
 const INT=[
  {k:"crisis",w:["suicid","quitarme la vida","no quiero vivir","no quiero seguir viviendo","matarme","hacerme dano","autolesi","acabar con todo","desaparecer para siempre"],p:["oracion-de-confianza","nada-te-turbe"],c:"otra"},
  {k:"duelo",w:["murio","muerto","muerte","fallec","difunt","luto","duelo","entierro","funeral","tanatorio","lo echo de menos","la echo de menos","se fue al cielo","perdi a"],l:"El amor no termina con la muerte. Puedes poner a quien echas de menos en las manos de Dios, que lo cuida.",p:["oracion-por-un-difunto","oracion-para-el-duelo","oracion-por-mi-madre-fallecida","oracion-por-mi-padre-fallecido"],v:"versiculos-para-cuando-estas-triste",c:"difuntos"},
  {k:"salud",w:["enferm","hospital","ingresad","urgencias","medico","diagnost","prueba medica","resultados","analisis","salud","dolor","opera","quirofano","cirug","cancer","quimio","tumor","uci","covid"],l:"Dios está junto a quien sufre y junto a quienes lo cuidan. Puedes confiarle esta enfermedad.",p:["oracion-por-un-enfermo","oracion-antes-de-una-operacion","oracion-por-un-enfermo-de-cancer","oracion-de-confianza"],v:"versiculos-sobre-la-proteccion",c:"salud"},
  {k:"crisisvida",w:["no puedo mas","no aguanto","estoy hundid","desesper","todo me sale mal","no tiene sentido"],l:"No tienes que poder con todo tú solo. Dios está a tu lado incluso cuando no lo sientes.",p:["oracion-de-confianza","nada-te-turbe","oracion-a-san-judas-tadeo"],v:"versiculos-para-momentos-dificiles",c:"otra"},
  {k:"estudios",w:["examen","examenes","prueba","oposic","selectividad","ebau","evau","pau","aprob","suspend","nota","estudi","universidad","instituto","clase","tfg","master","carrera"],l:"Lo que has preparado no se pierde. Pon tu esfuerzo en manos de Dios y respira.",p:["oracion-antes-de-un-examen","oracion-para-aprobar","oracion-para-estudiar","oracion-a-san-jose-de-cupertino"],v:"versiculos-para-el-miedo",c:"estudios"},
  {k:"trabajo",w:["trabajo","paro","empleo","despid","entrevista","jefe","contrato","curriculum","negocio","empresa","clientes","autonomo"],l:"Dios conoce tu trabajo y tus necesidades. Puedes pedirle luz y confianza para el camino.",p:["oracion-para-encontrar-trabajo","oracion-antes-de-una-entrevista","oracion-por-mi-negocio"],v:"versiculos-sobre-el-dinero",c:"trabajo"},
  {k:"dinero",w:["dinero","deuda","deudas","pagar","hipoteca","alquiler","factura","no llego a fin de mes","economic","banco","prestamo"],l:"Tu preocupación por llegar a fin de mes es real. Puedes ponerla en manos de Dios, que conoce lo que necesitas.",p:["oracion-de-confianza","oracion-para-encontrar-trabajo","nada-te-turbe"],v:"versiculos-sobre-el-dinero",c:"trabajo"},
  {k:"ruptura",w:["ruptura","me ha dejado","me dejo","lo hemos dejado","separac","divorc","mi ex","corazon roto","infiel","engan"],l:"Un corazón roto necesita tiempo y cuidado. Dios no te deja solo mientras sana.",p:["oracion-en-la-tristeza","oracion-para-perdonar","oracion-de-confianza"],v:"versiculos-para-superar-una-ruptura",c:"otra"},
  {k:"pareja",w:["pareja","matrimonio","marido","mujer","esposo","esposa","novio","novia","boda","casarnos"],l:"El amor también se cuida rezando. Pon vuestra relación en manos de Dios.",p:["oracion-por-mi-matrimonio","oracion-para-perdonar"],v:"versiculos-sobre-el-amor",c:"familia"},
  {k:"hijos",w:["mi hijo","mi hija","mis hijos","hijo","hija","adolescen","bebe","nino","nina","ninos","ninas"],l:"Tus hijos también están en el corazón de Dios. Él los cuida contigo.",p:["oracion-por-los-hijos","oracion-por-la-familia"],v:"versiculos-para-la-familia",c:"familia"},
  {k:"embarazo",w:["embaraz","parto","dar a luz","quedarme embarazada","fertilidad"],l:"La vida que esperas es un regalo. Pon este tiempo en manos de Dios y de la Virgen.",p:["oracion-por-una-embarazada","oracion-de-confianza"],v:"versiculos-sobre-la-proteccion",c:"familia"},
  {k:"familia",w:["familia","mi madre","mi padre","su madre","su padre","mama","papa","herman","abuel","tio","tia","primo","suegr","casa","discut"],l:"Tu familia también está en el corazón de Dios. Él la cuida contigo.",p:["oracion-por-la-familia","oracion-por-los-hijos"],v:"versiculos-para-la-familia",c:"familia"},
  {k:"enfado",w:["enfad","rabia","ira","furios","odio","me ha ofendido","me ofendio","traicion","rencor","no puedo perdonar","perdonar","perdon"],l:"Lo que sientes es comprensible. Puedes contárselo a Dios tal cual y pedirle un corazón en paz.",p:["oracion-para-perdonar","oracion-de-confianza"],v:"versiculos-para-el-enfado",c:"otra"},
  {k:"miedo",w:["miedo","asustad","temo","terror","me da panico"],l:"«No temas, que yo estoy contigo». Puedes dejar este miedo en manos de Dios.",p:["oracion-de-confianza","nada-te-turbe","oracion-para-la-ansiedad"],v:"versiculos-para-el-miedo",c:"otra"},
  {k:"ansiedad",w:["ansied","angust","agobi","estres","panico","nervio","preocup","inquiet","no se que hacer","agotad","bloquead","sobrepasad"],l:"Puedes poner esta preocupación en manos de Dios.",p:["oracion-para-la-ansiedad","nada-te-turbe","oracion-de-confianza"],v:"versiculos-para-la-ansiedad",c:"otra"},
  {k:"tristeza",w:["triste","tristeza","sola","solo","soledad","llor","deprim","vacio","desanim","apagad"],l:"Dios está cerca de los que tienen el corazón herido. No estás solo en esta tristeza.",p:["oracion-en-la-tristeza","oracion-de-confianza"],v:"versiculos-para-cuando-estas-triste",c:"otra"},
  {k:"dormir",w:["dormir","insomn","no duermo","desvel","de noche","pesadilla"],l:"Deja el día en manos de Dios. Él vela tu descanso.",p:["oracion-para-dormir","examen-del-dia"],v:"versiculos-para-dormir",c:"otra"},
  {k:"decision",w:["decid","decision","dudas","elegir","no se si","futuro","cambio","mudarme","discernir"],l:"Para decidir bien hace falta calma y luz. Pide al Espíritu Santo que te guíe.",p:["oracion-ante-una-decision","ven-espiritu-santo"],v:"versiculos-para-la-fe",c:"otra"},
  {k:"fe",w:["fe","no creo","dudo de dios","lejos de dios","no siento a dios","creer","volver a la iglesia","confesar","rezar no sirve"],l:"Buscar a Dios ya es una forma de rezar. Él te espera, incluso en la duda.",p:["ven-espiritu-santo","oracion-de-confianza","acordaos"],v:"versiculos-para-la-fe",c:"otra"},
  {k:"viaje",w:["viaje","viajar","avion","carretera","conducir","vuelo"],l:"Pon tu camino en manos de Dios: que te acompañe a la ida y a la vuelta.",p:["oracion-antes-de-un-viaje"],v:"versiculos-sobre-la-proteccion",c:"otra"},
  {k:"imposible",w:["imposible","urgente","milagro","causa perdida","ultima esperanza"],l:"Para Dios nada es imposible. Puedes pedir con confianza la intercesión de los santos de las causas difíciles.",p:["oracion-a-san-judas-tadeo","oracion-a-santa-rita","oracion-a-san-expedito"],v:"versiculos-para-momentos-dificiles",c:"otra"},
  {k:"perdido",w:["he perdido","se me ha perdido","no encuentro","perdi el","perdi la"],l:"San Antonio acompaña a quien busca algo perdido. Pídele ayuda con calma.",p:["oracion-a-san-antonio"],c:"otra"},
  {k:"gracias",w:["gracias","agradec","alegr","feliz","contento","celebr","logr","aprobe","me han dado","buena noticia","ha salido bien"],l:"Qué bonito empezar por dar gracias. La alegría compartida con Dios se multiplica.",p:["oracion-de-accion-de-gracias","el-angelus"],v:"versiculos-para-dar-gracias",c:"gracias"}
 ];
 const FEEL=[["Estoy preocupado","ansiedad"],["Alguien está enfermo","salud"],["He perdido a alguien","duelo"],["Tengo un examen","estudios"],["Busco trabajo","trabajo"],["Estoy triste","tristeza"],["Tengo que decidir","decision"],["Mi familia","familia"],["Quiero dar gracias","gracias"],["No puedo dormir","dormir"]];
 const KI=Object.fromEntries(INT.map(i=>[i.k,i]));
 const A=$("#answers"),inp=$("#askIn");
 const has=(n,w)=>{const k=norm(w);return k.length<=4?new RegExp("(^|[^a-z])"+k+"([^a-z]|$)").test(n):n.includes(k)};
 function classify(t){const n=" "+norm(t)+" ";const sc=INT.map((it,ord)=>({it,ord,s:it.w.filter(w=>has(n,w)).length})).filter(x=>x.s>0);
  sc.sort((a,b)=>(b.it.k==="crisis")-(a.it.k==="crisis")||b.s-a.s||a.ord-b.ord);return sc.map(x=>x.it)}
 let RDO=null;function loadPrayers(){if(window.RDO)return Promise.resolve(window.RDO);if(RDO)return RDO;const sv=(document.querySelector('script[src*="data.js"]')||{}).src||"";const v=(sv.split("v=")[1]||"");
  RDO=new Promise(ok=>{const s=document.createElement("script");s.src=ROOT+"assets/oraciones.js?v="+v;s.onload=()=>ok(window.RDO||{});s.onerror=()=>ok({});document.head.appendChild(s)});return RDO}
 const preview=t=>{const one=String(t||"").replace(/\s+/g," ").split(/(?<=[.;:!?])\s/).slice(0,2).join(" ");return one.length>220?one.slice(0,210).replace(/\s\S*$/,"")+"…":one};
 const muro=(cat,txt)=>`${ROOT}muro-de-intenciones${X}${txt?"?i="+encodeURIComponent(txt.slice(0,160)):""}#${cat}`;
 function verseFor(slug){const t=window.RDV&&RDV[slug];if(!t||!t.v.length)return null;const d=new Date();const i=(d.getFullYear()*372+d.getMonth()*31+d.getDate())%t.v.length;return{slug,t:t.t,ref:t.v[i][0],x:t.v[i][1]}}
 async function answer(text,fromChip){
  const its=fromChip?[KI[fromChip]]:classify(text);const main=its[0];
  const crisis=main&&main.k==="crisis";
  const slugs=[...new Set([...(main?main.p:["oracion-de-confianza","nada-te-turbe"]),...(its[1]&&!crisis?its[1].p.slice(0,1):[])])].filter(byS);
  const first=byS(slugs[0]),others=slugs.slice(1,3).map(byS);
  const line=crisis?"Gracias por contarlo. Lo que sientes importa, y no tienes que pasarlo solo.":main?main.l:"Gracias por confiarlo. Sea lo que sea, puedes ponerlo en manos de Dios con estas palabras.";
  const cat=main?main.c:"otra";const v=!crisis&&main&&main.v?verseFor(main.v):null;
  const said=fromChip?"":`<p class="heart-said"><span>Has escrito</span>«${esc(text)}»</p>`;
  A.innerHTML=`${said}<div class="heart-wait" aria-hidden="true"><i></i><i></i><i></i></div>`;
  const texts=await Promise.all([loadPrayers(),new Promise(r=>setTimeout(r,650))]).then(x=>x[0]);
  const url=p=>`${ROOT}oraciones/${p.slug}${X}`;
  A.innerHTML=said+(crisis?`<div class="heart-help"><strong>Si estás pensando en hacerte daño, habla ahora con alguien.</strong> Llama al <a href="tel:024">024</a> (gratuito, a cualquier hora, España) o al <a href="tel:112">112</a> si es una emergencia. También puedes hablar con un sacerdote o con alguien de confianza hoy mismo.</div>`:"")+
   `<article class="heart-card"><span class="eyebrow">Una oración para este momento</span><p class="heart-line">${esc(line)}</p>
    <h3>${esc(first.t)}</h3>${texts[first.slug]?`<p class="heart-pre">${esc(preview(texts[first.slug]))}</p>`:""}
    <div class="heart-acts"><button class="btn btn-accent sm" type="button" data-hlisten>Escuchar oración</button><a class="btn btn-ghost sm" href="${url(first)}">Leer oración</a><a class="btn btn-ghost sm" href="${muro(cat)}">Encender una vela</a><a class="btn btn-ghost sm" href="${muro(cat,fromChip?"":text)}">Dejar una intención</a></div>
    ${v?`<div class="heart-verse"><span class="eyebrow">Un versículo</span><blockquote>«${esc(v.x)}»</blockquote><cite>${esc(v.ref)}</cite><a href="${ROOT}${v.slug}${X}">Más ${esc(v.t.toLowerCase())}</a></div>`:""}
    ${others.length?`<div class="heart-more"><span>También puede acompañarte</span>${others.map(p=>`<a href="${url(p)}">${esc(p.t)}<small>${p.min} min</small></a>`).join("")}</div>`:""}
   </article><p class="heart-next">¿Quieres contar algo más? Puedes volver a escribir arriba.</p>`;
  const lb=A.querySelector("[data-hlisten]");lb.onclick=()=>{if(sp.on){stopSpeech();lb.textContent="Escuchar oración";return}const t=texts[first.slug];if(!t){location.href=url(first);return}
   if(speakText(first.t+". "+t,()=>{lb.textContent="Escuchar oración"}))lb.textContent="Detener"};
  if(innerWidth<860)A.scrollIntoView({behavior:"smooth",block:"start"})}
 $("#feel").innerHTML=FEEL.map(([n,k])=>`<button class="chip" type="button" data-k="${k}">${n}</button>`).join("");
 $$("#feel .chip").forEach(b=>b.onclick=()=>{$$("#feel .chip").forEach(x=>x.classList.toggle("on",x===b));answer(b.textContent,b.dataset.k)});
 $("#askForm").onsubmit=e=>{e.preventDefault();const t=inp.value.trim();if(!t){inp.focus();return}$$("#feel .chip").forEach(x=>x.classList.remove("on"));answer(t)};
 inp.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();$("#askForm").requestSubmit()}});
 A.innerHTML=`<div class="heart-empty"><span class="eyebrow">Cómo funciona</span><p>Escribe lo que te preocupa o lo que agradeces. Te proponemos una oración de Rezo Diario, un versículo de la Biblia si encaja, y la posibilidad de encender una vela para que otras personas recen contigo.</p></div>`;
}

/* ---------- Tu camino de oración (racha discreta, también sin registrarse) ---------- */
function isoD(d){return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0")}
function renderCamino(){const els=$$("[data-camino]");if(!els.length)return;const s=new Set(store.get("rd-rezado",[]));const now=new Date();
 const day=k=>{const d=new Date(now);d.setDate(d.getDate()-k);return d};const today=isoD(now);
 let n=0,k=s.has(today)?0:1;while(s.has(isoD(day(k)))){n++;k++}
 const L=["D","L","M","X","J","V","S"];
 const dots=Array.from({length:7},(_,i)=>{const d=day(6-i),iso=isoD(d),on=s.has(iso),t=iso===today;return `<li class="${on?"on":""}${t?" today":""}" title="${d.getDate()}/${d.getMonth()+1}${on?" · rezado":""}"><i></i><span>${L[d.getDay()]}</span></li>`}).join("");
 const prayedToday=s.has(today);
 const txt=n===0?"Cada día que reces quedará marcado aquí.":n===1?(prayedToday?"Hoy has rezado. Mañana seguimos.":"Ayer rezaste. Hoy puedes continuar."):(prayedToday?`${n} días de oración seguidos`:`${n} días de oración seguidos · hoy puedes continuar`);
 els.forEach(el=>{el.querySelector("[data-camino-dots]").innerHTML=dots;el.querySelector("[data-camino-n]").textContent=txt;const c=el.querySelector("[data-camino-cta]");if(c){c.hidden=prayedToday;c.href=$("#player")?"#player":ROOT+IDX+"#player"}})}
renderCamino();document.addEventListener("rd-rezado",renderCamino);

/* ---------- Biblioteca ---------- */
if($("#libGrid")){
 let cat=document.body.dataset.cat||"todos",q="";
 const cards=$$("#libGrid .card");
 function apply(){const n=norm(q.trim());let shown=0;cards.forEach(c=>{const ok=(cat==="todos"||c.dataset.cat===cat)&&(!n||norm(c.dataset.k).includes(n));c.hidden=!ok;if(ok)shown++});
  $("#libEmpty").hidden=shown>0;$("#libEmpty").textContent=`No hay oraciones con «${q}». Prueba con otra palabra, por ejemplo «familia» o «noche».`;const lc=$("#libCount");if(lc)lc.textContent=shown+" oraciones"}
 $$("#chips .chip").forEach(b=>b.addEventListener("click",e=>{if(b.tagName==="A"&&document.body.dataset.cat===undefined){}if(b.dataset.c){e.preventDefault();cat=b.dataset.c;$$("#chips .chip").forEach(x=>x.classList.toggle("on",x===b));apply()}}));
 const qi=$("#q");if(qi){qi.addEventListener("input",e=>{q=e.target.value;apply()});const u=new URLSearchParams(location.search).get("q");if(u){qi.value=u;q=u}}
 apply();
}
const sb=$("#btnSearch");if(sb)sb.onclick=()=>{const qi=$("#q");if(qi){qi.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(()=>qi.focus({preventScroll:true}),400)}else location.href=ROOT+"oraciones/"+IDX+"#buscar"};
if(location.hash==="#buscar"&&$("#q"))setTimeout(()=>$("#q").focus(),300);

/* ---------- Página de oración ---------- */
const pt=$("#prayText");
if(pt){
 const title=document.querySelector("h1").textContent;
 const bs=$("#btnSpeak");bs.onclick=()=>{if(sp.on){stopSpeech();bs.textContent="Escuchar";pt.classList.remove("speaking");return}if(speakText(title+". "+pt.textContent,()=>{bs.textContent="Escuchar";pt.classList.remove("speaking")})){bs.textContent="Detener";}};
 $("#btnCopy").onclick=()=>{const t=title+"\n\n"+pt.textContent+"\n\n"+(document.querySelector('link[rel=canonical]')||{}).href;
  const sel=()=>{const r=document.createRange();r.selectNodeContents(pt);const s=getSelection();s.removeAllRanges();s.addRange(r);toast("Texto seleccionado: cópialo con tu teclado")};
  navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(t).then(()=>toast("Oración copiada"),sel):sel()};
 const fav=$("#btnFav");if(fav){const id=document.body.dataset.slug;const f=()=>store.get("rd-favs",[]);const r=()=>{const on=f().includes(id);fav.setAttribute("aria-pressed",on);fav.textContent=on?"Guardada":"Guardar"};r();
  fav.onclick=()=>{let a=f();a=a.includes(id)?a.filter(x=>x!==id):[...a,id];store.set("rd-favs",a);r();toast(a.includes(id)?"Guardada en favoritos":"Quitada de favoritos")}}
}
const amen=$("#btnAmen");if(amen){const today=()=>{const d=new Date();return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0")};const paint=()=>{const on=doneDays().includes(today());amen.textContent=on?"Has rezado hoy":"Amén";amen.setAttribute("aria-pressed",on)};paint();amen.onclick=()=>{markDone(today());paint();toast("Gracias por rezar hoy. Mañana te espera un nuevo Evangelio.")}}
const favBox=$("#favList");if(favBox){const a=store.get("rd-favs",[]).map(s=>RD.prayers.find(p=>p.slug===s)).filter(Boolean);if(a.length){favBox.hidden=false;favBox.querySelector("ul").innerHTML=a.map(p=>`<li><a href="${ROOT}oraciones/${p.slug}${X}">${esc(p.t)}<small>${p.min} min</small></a></li>`).join("")}}

/* ---------- Rosario ---------- */
if($("#beads")){
 const R={steps:[],cur:0,voice:false,dir:1};const ORD=["Primer","Segundo","Tercer","Cuarto","Quinto"];const T=RD;
 function build(set){const S=T.SETS[set],st=[];
  st.push({b:"cross",k:"Inicio",t:"Señal de la cruz y Credo",x:T.SENAL+"\n\n"+T.CREDO});st.push({b:"p0",k:"Inicio",t:"Padre Nuestro",x:T.PN});
  ["Por la fe","Por la esperanza","Por la caridad"].forEach((s,i)=>st.push({b:"p"+(i+1),k:"Inicio · Ave María "+(i+1)+" de 3",t:"Ave María",m:[s],x:T.AM}));
  st.push({b:"p4",k:"Inicio",t:"Gloria",x:T.GL});
  S.list.forEach((my,m)=>{const big=m===0?"p4":"b"+(m-1);
   st.push({b:big,k:`Misterio ${m+1} de 5`,t:my[0],m:[ORD[m]+" misterio "+S.adj,my[1],"Fruto: "+my[2]],x:"Contempla en silencio este misterio.\n\n"+T.PN,ann:`${ORD[m]} misterio ${S.adj}: ${my[0]}.`});
   for(let j=0;j<10;j++)st.push({b:`d${m}-${j}`,k:`Misterio ${m+1} de 5 · Ave María ${j+1} de 10`,t:my[0],m:["Fruto: "+my[2]],x:T.AM,dec:[m,j]});
   st.push({b:m<4?"b"+m:"medal",k:`Misterio ${m+1} de 5`,t:"Gloria y Oh Jesús mío",x:T.GL+"\n\n"+T.OJ})});
  st.push({b:"medal",k:"Final",t:"Salve",x:T.SALVE+"\n\n"+T.SENAL});return st}
 function draw(){const svg=$("#beads"),NS="http://www.w3.org/2000/svg",cx=160,cy=150,Rr=126;svg.innerHTML="";
  const add=(tag,at)=>{const e=document.createElementNS(NS,tag);for(const k in at)e.setAttribute(k,at[k]);svg.appendChild(e);return e};
  add("circle",{cx,cy,r:Rr,class:"cord"});add("path",{d:`M${cx} ${cy+Rr} V ${cy+Rr+150}`,class:"cord"});
  const seq=[];for(let m=0;m<5;m++){for(let j=0;j<10;j++)seq.push({t:"s",id:`d${m}-${j}`});if(m<4)seq.push({t:"b",id:"b"+m})}
  const w=s=>s.t==="b"?1.8:1;let pos=[0];for(let i=1;i<seq.length;i++)pos.push(pos[i-1]+(w(seq[i-1])+w(seq[i]))/2);const tot=pos[pos.length-1],a0=101,a1=439;
  seq.forEach((s,i)=>{const a=(a0+(a1-a0)*pos[i]/tot)*Math.PI/180;add("circle",{cx:(cx+Rr*Math.cos(a)).toFixed(1),cy:(cy+Rr*Math.sin(a)).toFixed(1),r:s.t==="b"?8:5.3,class:"bead "+s.t,"data-b":s.id})});
  add("path",{d:`M${cx} ${cy+Rr-9} l9 9 -9 11 -9 -11z`,class:"bead b","data-b":"medal"});
  [["p4",cy+Rr+40,"b"],["p3",cy+Rr+60,"s"],["p2",cy+Rr+77,"s"],["p1",cy+Rr+94,"s"],["p0",cy+Rr+120,"b"]].forEach(([id,y,t])=>add("circle",{cx,cy:y,r:t==="b"?8:5.3,class:"bead "+t,"data-b":id}));
  const y=cy+Rr+142;add("path",{d:`M${cx-4} ${y} h8 v14 h12 v8 h-12 v26 h-8 v-26 h-12 v-8 h12z`,class:"cross bead","data-b":"cross",style:"stroke:none"});
  svg.querySelectorAll("[data-b]").forEach(el=>el.addEventListener("click",()=>{const i=R.steps.findIndex(s=>s.b===el.dataset.b);if(i>=0)go(i)}))}
 const todaySet=(WEEK[todayIdx]||{}).set||"gozosos";
 function setSet(set){R.steps=build(set);R.cur=0;
  $("#sets").innerHTML=Object.entries(T.SETS).map(([k,s])=>`<button class="set${k===set?" on":""}" data-s="${k}"><b>${s.name}${k===todaySet?" · hoy":""}</b><small>${s.days}</small></button>`).join("");
  $$("#sets .set").forEach(b=>b.onclick=()=>setSet(b.dataset.s));render()}
 function render(){const s=R.steps[R.cur],el=$("#step");
  $("#stK").textContent=s.k;$("#stT").textContent=s.t;$("#stX").textContent=s.x;$("#stM").innerHTML=(s.m||[]).map(x=>`<span>${esc(x)}</span>`).join("");
  $("#tens").innerHTML=s.dec?Array.from({length:10},(_,j)=>`<i class="${j<s.dec[1]?"done":j===s.dec[1]?"act":""}"></i>`).join(""):"";
  el.classList.remove("in-r","in-l");void el.offsetWidth;el.classList.add(R.dir>0?"in-r":"in-l");
  const doneB=new Set(R.steps.slice(0,R.cur).map(x=>x.b));$$("#beads [data-b]").forEach(b=>{const id=b.dataset.b;b.classList.toggle("act",id===s.b);b.classList.toggle("done",doneB.has(id)&&id!==s.b)});
  $("#rBar").style.width=(R.cur/(R.steps.length-1)*100)+"%";$("#rCount").textContent=`Paso ${R.cur+1} de ${R.steps.length}`;
  $("#rPrev").disabled=R.cur===0;$("#rNext").textContent=R.cur===R.steps.length-1?"Terminar":"Siguiente";
  if(R.voice)speakText((s.ann?s.ann+" ":"")+s.x)}
 function go(i){if(i<0||i>=R.steps.length)return;R.dir=i>=R.cur?1:-1;R.cur=i;render()}
 function next(){if(R.cur===R.steps.length-1){markDone(ISO);toast("Rosario completado. Que la Virgen te acompañe.");R.cur=0;R.dir=1;render();return}go(R.cur+1)}
 $("#rNext").onclick=next;$("#rPrev").onclick=()=>go(R.cur-1);$("#rReset").onclick=()=>go(0);
 $("#rVoice").onclick=e=>{R.voice=!R.voice;e.currentTarget.setAttribute("aria-pressed",R.voice);if(R.voice)render();else stopSpeech()};
 $("#step").addEventListener("keydown",e=>{if(e.key==="ArrowRight"||e.key===" "){e.preventDefault();next()}if(e.key==="ArrowLeft"){e.preventDefault();go(R.cur-1)}});
 swipe($("#step"),d=>d>0?next():go(R.cur-1));
 draw();setSet(todaySet);
}

/* ---------- Vía Crucis ---------- */
if($("#vc")){
 const V=RD.via;let i=0,dir=1;const seen=new Set();
 const path=$("#vcPath");path.innerHTML=V.map((s,k)=>(k?'<span class="vc-line"></span>':"")+`<button class="vc-dot" data-k="${k}" aria-label="Estación ${k+1}">${k+1}</button>`).join("");
 $$("#vcPath .vc-dot").forEach(b=>b.onclick=()=>go(+b.dataset.k));
 const ROM=["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV"];
 function render(){const s=V[i];seen.add(i);$("#vcNum").textContent=ROM[i];$("#vcT").textContent=s[0];$("#vcX").textContent=s[1];
  $$("#vcPath .vc-dot").forEach((b,k)=>{b.classList.toggle("on",k===i);b.classList.toggle("done",seen.has(k)&&k!==i)});
  const c=$("#vc");c.classList.remove("in-r","in-l");void c.offsetWidth;c.classList.add(dir>0?"in-r":"in-l");
  const on=$("#vcPath .vc-dot.on");if(on)on.scrollIntoView({block:"nearest",inline:"center",behavior:"smooth"});
  $("#vcPrev").disabled=i===0;$("#vcNext").textContent=i===V.length-1?"Terminar":"Siguiente estación"}
 function go(k){if(k<0||k>=V.length)return;dir=k>=i?1:-1;i=k;render()}
 $("#vcPrev").onclick=()=>go(i-1);$("#vcNext").onclick=()=>{if(i===V.length-1){markDone(ISO);toast("Vía Crucis completado.");return}go(i+1)};
 $("#vcSpeak").onclick=e=>{const b=e.currentTarget;if(sp.on){stopSpeech();b.textContent="Escuchar";return}if(speakText(`Estación ${i+1}. ${V[i][0]}. ${RD.VIA_ANT} ${V[i][1]}`,()=>b.textContent="Escuchar"))b.textContent="Detener"};
 $("#vc").addEventListener("keydown",e=>{if(e.key==="ArrowRight"){e.preventDefault();go(i+1)}if(e.key==="ArrowLeft"){e.preventDefault();go(i-1)}});
 swipe($("#vc"),d=>go(i+d));render();
}

/* ---------- Novena ---------- */
const nv=$("#novena");
if(nv){
 const N=RD.novenas.find(x=>x.slug===nv.dataset.slug);const key="rd-nov-"+N.slug;
 const start=new Date(N.start+"T00:00:00");const dayN=Math.floor((new Date(ISO+"T00:00:00")-start)/864e5);
 const todayK=dayN>=0&&dayN<9?dayN:-1;let cur=todayK>=0?todayK:0;
 const fmt=k=>{const d=new Date(start.getTime()+k*864e5);return d.getDate()+" "+["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"][d.getMonth()]};
 function render(){const done=store.get(key,[]);
  $("#novDays").innerHTML=N.days.map((d,k)=>`<button class="nov-day${k===cur?" on":""}${done.includes(k)?" done":""}${k===todayK?" today":""}" data-k="${k}" aria-label="Día ${k+1}"><small>Día</small><b>${k+1}</b><small>${k===todayK?"hoy":fmt(k)}</small></button>`).join("");
  $$("#novDays .nov-day").forEach(b=>b.onclick=()=>{cur=+b.dataset.k;render()});
  const d=N.days[cur];$("#novK").textContent=`Día ${cur+1} · ${fmt(cur)}`;$("#novT").textContent=d[0];$("#novX").textContent=d[1];
  const c=2*Math.PI*36,pct=done.length/9;$("#novRing").innerHTML=`<circle class="bg" cx="42" cy="42" r="36"/><circle class="fg" cx="42" cy="42" r="36" stroke-dasharray="${c}" stroke-dashoffset="${c*(1-pct)}"/><text x="42" y="48" text-anchor="middle">${done.length}/9</text>`;
  const b=$("#novDone");b.textContent=done.includes(cur)?"✓ Día rezado":"Marcar este día como rezado";b.setAttribute("aria-pressed",done.includes(cur));
  $("#novStatus").textContent=todayK>=0?`Hoy toca el día ${todayK+1}.`:(dayN<0?`Empieza el ${fmt(0)}. Puedes rezarla en cualquier momento del año.`:"La novena de este año ya ha terminado. Puedes rezarla en cualquier momento.")}
 $("#novDone").onclick=()=>{let d=store.get(key,[]);d=d.includes(cur)?d.filter(x=>x!==cur):[...d,cur];store.set(key,d);if(d.length===9)toast("¡Novena completada!");else if(d.includes(cur)&&cur<8){cur++;}render()};
 $("#novSpeak").onclick=e=>{const b=e.currentTarget;if(sp.on){stopSpeech();b.textContent="Escuchar";return}const d=N.days[cur];if(speakText(`${N.open} Día ${cur+1}. ${d[0]}. ${d[1]} ${N.close}`,()=>b.textContent="Escuchar"))b.textContent="Detener"};
 render();
}

/* ---------- Supabase (REST, sin librerías) ---------- */
const SB=CFG.supabaseUrl&&CFG.supabaseAnonKey?{u:CFG.supabaseUrl.replace(/\/$/,""),k:CFG.supabaseAnonKey}:null;
const AUTH={get token(){return (store.get("rd-auth",null)||{}).access_token||null}};
async function sbf(path,opt={}){const tok=(opt.auth&&AUTH.token)||(/^eyJ/.test(SB.k)?SB.k:null);const h={apikey:SB.k,"Content-Type":"application/json",...(tok?{Authorization:"Bearer "+tok}:{}),...(opt.headers||{})};
 const r=await fetch(SB.u+path,{method:opt.method||"GET",headers:h,body:opt.body?JSON.stringify(opt.body):undefined});const t=await r.text();if(!r.ok)throw new Error(r.status+" "+t);return t?JSON.parse(t):null}

/* ---------- Muro de velas ---------- */
const chapel=$("#chapel");
if(chapel){
 const LIMIT=+chapel.dataset.limit||36, FULL=chapel.dataset.full==="1";
 const VC={salud:["Salud","#2F8C84"],familia:["Familia","#C98A43"],difuntos:["Difuntos","#6B4E8C"],estudios:["Estudios","#3C6FA8"],trabajo:["Trabajo","#9A5470"],gracias:["Gracias","#C9A13A"],otra:["Otra intención","#B23A31"]};
 const WEEKMS=7*864e5;const cutoff=Date.now()-WEEKMS;
 let candles=[],prays=new Map(),flags=new Map(),myPrays=new Set(store.get("rd-myprays",[])),myFlags=new Set(store.get("rd-myflags",[])),mine=new Set(store.get("rd-mycandles",[]));
 let uid=store.get("rd-uid",null);if(!uid){uid="v"+Math.random().toString(36).slice(2,12);store.set("rd-uid",uid)}
 let db=null,mode="local",sel=null,auto=true,cat="otra",seenChecked=false;
 const setMode=t=>{const m=$("#vMode");if(m)m.textContent=t};
 setMode("Las velas se guardan en este dispositivo hasta que se conecte la capilla compartida.");
 const CC=$("#vCats");CC.innerHTML=Object.entries(VC).map(([k,[n,c]])=>`<button type="button" role="radio" data-c="${k}" aria-checked="${k===cat}" style="--cc:${c}"><i></i>${n}</button>`).join("");
 $$("#vCats button").forEach(b=>b.onclick=()=>{cat=b.dataset.c;$$("#vCats button").forEach(x=>x.setAttribute("aria-checked",x===b))});
 const h=(location.hash||"").slice(1);if(VC[h]){cat=h;$$("#vCats button").forEach(x=>x.setAttribute("aria-checked",x.dataset.c===h))}
 const ta=$("#vText");ta.addEventListener("input",()=>$("#vCount").textContent=`${ta.value.length}/160`);
 const qi=new URLSearchParams(location.search).get("i");if(qi){ta.value=qi.slice(0,160);ta.dispatchEvent(new Event("input"));setTimeout(()=>{const f=$("#vForm");if(f)f.scrollIntoView({behavior:"smooth",block:"center"});ta.focus({preventScroll:true})},500)}
 function clean(s,max){return String(s||"").replace(/https?:\/\/\S+|www\.\S+/gi,"").replace(/\S+@\S+\.\S+/g,"").replace(/(\+?\d[\d\s.-]{7,}\d)/g,"").replace(/\s+/g," ").trim().slice(0,max)}
 function ago(t){const m=Math.round((Date.now()-t)/6e4);if(m<1)return"ahora mismo";if(m<60)return`hace ${m} min`;const hh=Math.round(m/60);if(hh<24)return`hace ${hh} h`;const d=Math.round(hh/24);return d===1?"hace 1 día":`hace ${d} días`}
 function local(){candles=store.get("rd-velas-local",[]).filter(c=>c.at>cutoff);prays=new Map();store.get("rd-rezos-local",[]).forEach(p=>prays.set(p.c,(prays.get(p.c)||0)+1));render()}
 const visible=()=>candles.filter(c=>(flags.get(c.id)||0)<3&&!myFlags.has(c.id));
 function render(){
  const list=visible().sort((a,b)=>b.at-a.at);
  const lit=list.slice(0,LIMIT);const slots=Math.max(FULL?24:12,Math.ceil(lit.length/6)*6);
  $("#candles").innerHTML=lit.map(c=>{const age=Math.min(1,(Date.now()-c.at)/WEEKMS);const wh=Math.round(8+30*(1-age));const col=(VC[c.cat]||VC.otra)[1];
   return `<button class="candle${c.id===sel?" sel":""}${c._new?" new":""}" data-id="${esc(c.id)}" style="--cc:${col}" aria-label="Vela: ${esc(c.priv?"intención privada":c.text||"sin texto")}"><span class="halo"></span><span class="cup"><span class="wax" style="--wh:${wh}px"><span class="wick"></span><span class="flame"></span></span></span>${mine.has(c.id)?'<span class="mine">Tuya</span>':""}</button>`}).join("")
   +Array.from({length:Math.max(0,slots-lit.length)},()=>`<span class="candle unlit" aria-hidden="true" style="--cc:#6b5a45"><span class="cup"><span class="wax" style="--wh:36px"><span class="wick"></span></span></span></span>`).join("");
  lit.forEach(c=>delete c._new);
  $$("#candles .candle[data-id]").forEach(b=>{b.onclick=()=>{auto=false;select(b.dataset.id)};b.onmouseenter=()=>{if(matchMedia("(hover:hover)").matches){auto=false;select(b.dataset.id)}}});
  let pr=0;list.forEach(c=>pr+=prays.get(c.id)||0);
  $("#vStat1").textContent=list.length;$("#vStat2").textContent=pr;
  chapel.style.setProperty("--warm",Math.min(.32,.08+list.length*.006).toFixed(3));
  if(!sel||!list.find(c=>c.id===sel)){const pub=list.find(c=>!c.priv&&c.text);sel=pub?pub.id:(list[0]&&list[0].id)||null}
  showReader();
  const feed=$("#vFeed");if(feed){const pub=list.filter(c=>!c.priv&&c.text);feed.innerHTML=pub.slice(0,60).map(c=>`<li data-id="${esc(c.id)}"><q>${esc(c.text)}</q><small>${esc(c.name||"Anónimo")} · ${(VC[c.cat]||VC.otra)[0]} · ${ago(c.at)} · ${prays.get(c.id)||0} oraciones</small></li>`).join("");
   feed.querySelectorAll("li").forEach(li=>li.onclick=()=>{auto=false;select(li.dataset.id);$("#vReader").scrollIntoView({behavior:"smooth",block:"center"})})}
  if(!seenChecked&&mode!=="local"){seenChecked=true;let tot=0;candles.forEach(c=>{if(mine.has(c.id))tot+=prays.get(c.id)||0});const before=store.get("rd-myprays-seen",null);
   if(before!==null&&tot>before)setTimeout(()=>toast(`Desde tu última visita, ${tot-before} ${tot-before===1?"persona ha":"personas han"} rezado por tus velas.`),900);store.set("rd-myprays-seen",tot)}
 }
 function select(id){sel=id;$$("#candles .candle").forEach(b=>b.classList.toggle("sel",b.dataset.id===id));showReader()}
 function showReader(){const c=candles.find(x=>x.id===sel),R=$("#vReader");
  if(!c){R.innerHTML=`<span class="cat"><i style="background:var(--flame)"></i>La capilla está esperando</span><blockquote>Aún no hay velas encendidas esta semana. Enciende la primera y deja tu intención: otras personas rezarán por ti.</blockquote><div class="row"><a class="btn btn-flame sm" href="#vForm">Encender la primera vela</a></div>`;return}
  const n=prays.get(c.id)||0,pressed=myPrays.has(c.id),col=(VC[c.cat]||VC.otra);
  R.innerHTML=`<span class="cat"><i style="background:${col[1]}"></i>${col[0]}${mine.has(c.id)?" · tu vela":""}</span><blockquote>${c.priv||!c.text?"Intención privada. Solo Dios la conoce.":"«"+esc(c.text)+"»"}</blockquote><span class="who">${esc(c.name||"Anónimo")} · encendida ${ago(c.at)} · arde ${Math.max(0,Math.ceil((c.at+WEEKMS-Date.now())/864e5))} días más</span><div class="row"><button class="btn btn-wax sm" id="vPray" aria-pressed="${pressed}">${pressed?"✓ Has rezado por esta intención":"He rezado por ti"}</button><span class="who" id="vPrayN">${n===1?"1 persona ha rezado":n+" personas han rezado"}</span>${mine.has(c.id)||c.priv?"":'<button class="flag" id="vFlag" aria-label="Avisar de una intención inadecuada">Avisar</button>'}</div>`;
  $("#vPray").onclick=()=>pray(c.id);const fl=$("#vFlag");if(fl)fl.onclick=()=>flag(c.id)}
 async function pray(id){if(myPrays.has(id))return;myPrays.add(id);store.set("rd-myprays",[...myPrays]);prays.set(id,(prays.get(id)||0)+1);showReader();sparks($(`#candles .candle[data-id="${CSS.escape(id)}"]`),8);
  try{if(mode==="claude")await db.collection("rezos").doc(id+"--"+uid).set({c:id,at:Date.now()});else if(mode==="supabase")await sbf("/rest/v1/rezos",{method:"POST",headers:{Prefer:"return=minimal,resolution=ignore-duplicates"},body:{vela_id:id,visitante:uid}});else{const a=store.get("rd-rezos-local",[]);a.push({c:id});store.set("rd-rezos-local",a)}}catch(e){}}
 async function flag(id){if(myFlags.has(id))return;myFlags.add(id);store.set("rd-myflags",[...myFlags]);sel=null;render();toast("Gracias por avisar. Hemos ocultado esta vela para ti y la revisaremos.");
  try{if(mode==="claude")await db.collection("avisos").doc(id+"--"+uid).set({c:id,at:Date.now()});else if(mode==="supabase")await sbf("/rest/v1/rpc/reportar_vela",{method:"POST",body:{p_vela:id,p_visitante:uid}})}catch(e){}}
 function sparks(el,n){if(!el)return;const f=el.querySelector(".flame");if(!f)return;const r=f.getBoundingClientRect(),pr=chapel.getBoundingClientRect();
  for(let i=0;i<n;i++){const s=document.createElement("span");s.className="spark";s.style.left=(r.left-pr.left+r.width/2)+"px";s.style.top=(r.top-pr.top+r.height/2)+"px";const a=Math.random()*Math.PI*2,d=20+Math.random()*40;s.style.setProperty("--dx",Math.cos(a)*d+"px");s.style.setProperty("--dy",(Math.sin(a)*d-30)+"px");chapel.appendChild(s);setTimeout(()=>s.remove(),1000)}}
 const newId=()=>(crypto.randomUUID?crypto.randomUUID():"l"+Date.now().toString(36)+Math.random().toString(36).slice(2,8));
 $("#vForm").onsubmit=async e=>{e.preventDefault();
  const text=clean(ta.value,160),name=clean($("#vName").value,30),priv=$("#vPriv").checked;
  if(!text&&!priv){ta.focus();toast("Escribe tu intención o marca que sea privada.");return}
  const btn=$("#vSubmit");btn.disabled=true;
  const c={text:priv?"":text,name,cat,priv,at:Date.now(),by:uid};let id=newId();
  try{if(mode==="claude"){const ref=db.collection("velas").doc();id=ref.id;await ref.set(c)}
   else if(mode==="supabase"){await sbf("/rest/v1/velas",{method:"POST",headers:{Prefer:"return=minimal"},body:{id,texto:c.text,nombre:name,cat,privada:priv,visitante:uid}})}
   else{const a=store.get("rd-velas-local",[]);a.push({...c,id});store.set("rd-velas-local",a)}}
  catch(err){const a=store.get("rd-velas-local",[]);a.push({...c,id});store.set("rd-velas-local",a);toast(/40[0-9]|limite|límite/i.test(String(err))?"Has encendido muchas velas seguidas. Espera unos minutos.":"No se ha podido guardar en la capilla compartida. Tu vela se queda en este dispositivo.")}
  mine.add(id);store.set("rd-mycandles",[...mine]);
  const ex=candles.find(x=>x.id===id);if(!ex)candles.push({...c,id,_new:true});else ex._new=true;
  sel=id;auto=false;render();
  const el=$(`#candles .candle[data-id="${CSS.escape(id)}"]`);if(el){el.scrollIntoView({behavior:"smooth",block:"center"});setTimeout(()=>sparks(el,14),350)}
  ta.value="";$("#vCount").textContent="0/160";btn.disabled=false;toast("Tu vela está encendida. Arderá durante 7 días.")};
 setInterval(()=>{if(!auto||document.hidden)return;const pub=visible().filter(c=>!c.priv&&c.text).sort((a,b)=>b.at-a.at);if(pub.length<2)return;const i=pub.findIndex(c=>c.id===sel);select(pub[(i+1)%pub.length].id)},7000);
 local();
 async function sbLoad(){const rows=await sbf("/rest/v1/velas_semana?select=*&order=created_at.desc&limit=300");const keepNew=new Set(candles.filter(c=>c._new).map(c=>c.id));
  candles=rows.map(r=>({id:r.id,text:r.texto,name:r.nombre,cat:r.cat,priv:r.privada,at:Date.parse(r.created_at),_new:keepNew.has(r.id)}));prays=new Map(rows.map(r=>[r.id,r.rezos]));render()}
 (async()=>{
  try{if(window.claude&&window.claude.use){const d=await window.claude.use("db");if(d){db=d;mode="claude";
   try{const u=await window.claude.use("user");const real=u&&u.id?await u.id():null;if(real)uid=real}catch(e){}
   candles=[];
   db.collection("velas").where("at",">",cutoff).orderBy("at","desc").limit(300).onSnapshot(s=>{const keepNew=new Set(candles.filter(c=>c._new).map(c=>c.id));candles=s.docs.map(d=>({...d.data(),id:d.id,_new:keepNew.has(d.id)}));render()},()=>{});
   db.collection("rezos").limit(1000).onSnapshot(s=>{prays=new Map();s.docs.forEach(d=>{const x=d.data();prays.set(x.c,(prays.get(x.c)||0)+1)});render()},()=>{});
   db.collection("avisos").limit(1000).onSnapshot(s=>{flags=new Map();s.docs.forEach(d=>{const x=d.data();flags.set(x.c,(flags.get(x.c)||0)+1)});render()},()=>{});
   setMode("Capilla compartida: todos ven las velas encendidas esta semana.");return}}}catch(e){}
  if(SB){try{mode="supabase";await sbLoad();setMode("Capilla compartida: todos ven las velas encendidas esta semana.");setInterval(()=>{if(!document.hidden)sbLoad().catch(()=>{})},30000)}catch(e){mode="local";local()}}
 })();
}

/* ---------- Cuenta y sincronización ---------- */
(function(){
 const btn=$("#btnUser"),acc=$("#account");if(!SB||!btn||!acc)return;btn.hidden=false;
 const open=()=>{acc.hidden=false;renderAcc()},close=()=>{acc.hidden=true};btn.onclick=open;acc.querySelectorAll("[data-close]").forEach(b=>b.onclick=close);
 const msg=t=>{$("#accMsg").textContent=t};
 // vuelta desde el enlace mágico: #access_token=...&refresh_token=...
 const hp=new URLSearchParams(location.hash.slice(1));
 if(hp.get("access_token")){store.set("rd-auth",{access_token:hp.get("access_token"),refresh_token:hp.get("refresh_token"),exp:Date.now()+(+hp.get("expires_in")||3600)*1000});history.replaceState(null,"",location.pathname+location.search);setTimeout(()=>{toast("Has entrado en tu cuenta. Sincronizando…");pull()},300)}
 async function refresh(){const a=store.get("rd-auth",null);if(!a||!a.refresh_token)return null;if(a.exp>Date.now()+60000)return a;
  try{const r=await sbf("/auth/v1/token?grant_type=refresh_token",{method:"POST",body:{refresh_token:a.refresh_token}});const n={access_token:r.access_token,refresh_token:r.refresh_token,exp:Date.now()+r.expires_in*1000,email:r.user&&r.user.email};store.set("rd-auth",n);return n}catch(e){store.set("rd-auth",null);return null}}
 async function me(){const a=await refresh();if(!a)return null;try{const u=await sbf("/auth/v1/user",{auth:true});return u}catch(e){return null}}
 function snapshot(){const o={};try{for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(SYNC_KEYS.test(k))o[k]=JSON.parse(localStorage.getItem(k))}}catch(e){}return o}
 function merge(a,b){if(Array.isArray(a)&&Array.isArray(b))return[...new Set([...a,...b])];return b!==undefined?b:a}
 let busy=false,timer=null;
 async function pull(){const u=await me();if(!u)return;try{const rows=await sbf(`/rest/v1/progreso?select=datos&user_id=eq.${u.id}`,{auth:true});const remote=(rows[0]||{}).datos||{};const loc=snapshot();
  Object.keys(remote).forEach(k=>{if(SYNC_KEYS.test(k))try{localStorage.setItem(k,JSON.stringify(merge(remote[k],loc[k])))}catch(e){}});await push(true);renderWeek();document.dispatchEvent(new Event("rd-rezado"));toast("Tu progreso está sincronizado.")}catch(e){}}
 async function push(now){if(!now){clearTimeout(timer);timer=setTimeout(()=>push(true),2500);return}if(busy)return;busy=true;const u=await me();if(u){try{await sbf("/rest/v1/progreso",{method:"POST",auth:true,headers:{Prefer:"resolution=merge-duplicates,return=minimal"},body:{user_id:u.id,datos:snapshot(),updated_at:new Date().toISOString()}})}catch(e){}}busy=false}
 window.__rdSync=()=>{if(store.get("rd-auth",null))push(false)};
 async function renderAcc(){const u=await me();$("#accOut").hidden=!!u;$("#accIn").hidden=!u;msg("");
  if(u){$("#accWho").textContent=u.email||u.phone||"tu cuenta";const s=store.get("rd-rezado",[]).length,f=store.get("rd-favs",[]).length;$("#accStats").innerHTML=`<li><a>Días rezados<small>${s}</small></a></li><li><a>Oraciones guardadas<small>${f}</small></a></li>`}}
 $("#accForm").onsubmit=async e=>{e.preventDefault();const em=$("#accEmail").value.trim();if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em)){msg("Revisa el correo: falta la @ o el dominio.");return}
  try{await sbf("/auth/v1/otp?redirect_to="+encodeURIComponent(location.origin+location.pathname),{method:"POST",body:{email:em,create_user:true}});msg("Te hemos enviado un enlace. Ábrelo desde este dispositivo para entrar.")}
  catch(err){const t=String(err&&err.message||err);let m="No se ha podido enviar el enlace.";
   if(/rate|limit|429/i.test(t))m+=" Se han enviado demasiados correos en poco tiempo: espera un rato y vuelve a intentarlo.";
   else if(/not authorized|Email address not authorized/i.test(t))m+=" El servidor de correo de prueba de Supabase solo envía a direcciones autorizadas: hay que conectar un servicio de correo propio.";
   else if(/signups? (are )?(not allowed|disabled)/i.test(t))m+=" Los registros nuevos están desactivados en Supabase.";
   msg(m+" (Detalle: "+t.slice(0,160)+")")}};
 const back=()=>encodeURIComponent(location.origin+location.pathname);
 [["accGoogle","google"],["accApple","apple"],["accFacebook","facebook"]].forEach(([id,pv])=>{const b=$("#"+id);if(b)b.onclick=()=>{location.href=SB.u+"/auth/v1/authorize?provider="+pv+"&redirect_to="+back()}});
 // Solo mostramos los métodos que están activados en Supabase
 sbf("/auth/v1/settings").then(st=>{const ex=st.external||{};let any=false;
  [["accGoogle","google"],["accApple","apple"],["accFacebook","facebook"]].forEach(([id,pv])=>{const b=$("#"+id);if(b&&ex[pv]){b.hidden=false;any=true}});
  if(ex.phone){$("#accPhoneBtn").hidden=false;any=true}
  if(st.disable_signup)msg("Ahora mismo no se admiten cuentas nuevas.");
  if(ex.email===false){$("#accForm").hidden=true}else if(any)$("#accOr").hidden=false}).catch(()=>{});
 let tel="";const normTel=v=>{v=v.replace(/[^\d+]/g,"");if(!v.startsWith("+"))v="+34"+v.replace(/^0+/,"");return v};
 $("#accPhoneBtn").onclick=()=>{$("#accPhone").hidden=false;$("#accPhoneBtn").hidden=true;$("#accTel").focus()};
 $("#accPhone").onsubmit=async e=>{e.preventDefault();tel=normTel($("#accTel").value);if(tel.length<10){msg("Escribe tu número con prefijo, por ejemplo +34 600 000 000.");return}
  try{await sbf("/auth/v1/otp",{method:"POST",body:{phone:tel,create_user:true}});$("#accPhone").hidden=true;$("#accCode").hidden=false;$("#accOtp").focus();msg("Te hemos enviado un SMS con un código de 6 cifras.")}
  catch(err){msg("No se ha podido enviar el SMS. (Detalle: "+String(err.message||err).slice(0,160)+")")}};
 $("#accCode").onsubmit=async e=>{e.preventDefault();const code=$("#accOtp").value.replace(/\D/g,"");if(code.length<6){msg("El código tiene 6 cifras.");return}
  try{const r=await sbf("/auth/v1/verify",{method:"POST",body:{type:"sms",phone:tel,token:code}});
   store.set("rd-auth",{access_token:r.access_token,refresh_token:r.refresh_token,exp:Date.now()+(r.expires_in||3600)*1000});$("#accCode").hidden=true;toast("Has entrado en tu cuenta. Sincronizando…");pull();renderAcc()}
  catch(err){msg("El código no es correcto o ha caducado. Pide uno nuevo.")}};
 const he=new URLSearchParams(location.hash.slice(1));if(he.get("error_description")){setTimeout(()=>{open();msg("No se ha podido entrar: "+he.get("error_description"))},300);history.replaceState(null,"",location.pathname+location.search)}
 $("#accLogout").onclick=()=>{store.set("rd-auth",null);renderAcc();toast("Has cerrado sesión. Tu progreso sigue guardado en tu cuenta.")};
 if(store.get("rd-auth",null))refresh();
})();

/* ---------- Reto de Adviento ---------- */
const reto=$("#reto");
if(reto){const key=reto.dataset.key;const items=$$("#reto .reto-d");
 function r(){const done=store.get(key,[]);items.forEach(li=>{const k=+li.dataset.k,cb=li.querySelector("input");cb.checked=done.includes(k);li.classList.toggle("done",cb.checked);li.classList.toggle("today",li.dataset.date===ISO)});
  const c=2*Math.PI*36,pct=done.length/items.length;$("#retoRing").innerHTML=`<circle class="bg" cx="42" cy="42" r="36"/><circle class="fg" cx="42" cy="42" r="36" stroke-dasharray="${c}" stroke-dashoffset="${c*(1-pct)}"/><text x="42" y="48" text-anchor="middle">${done.length}</text>`;
  const t=items.find(li=>li.dataset.date===ISO);$("#retoStatus").textContent=t?`Hoy: ${t.querySelector("span").lastChild.textContent}`:(ISO<items[0].dataset.date?`Empieza el 29 de noviembre. Llevas ${done.length} de ${items.length}.`:`Llevas ${done.length} de ${items.length} gestos.`)}
 reto.addEventListener("change",e=>{const k=+e.target.dataset.k;let d=store.get(key,[]);d=e.target.checked?[...new Set([...d,k])]:d.filter(x=>x!==k);store.set(key,d);r();if(e.target.checked)toast(d.length===items.length?"¡Reto completado! Feliz Navidad.":"Gesto marcado. ¡Sigue así!")});
 r();const t=items.find(li=>li.dataset.date===ISO);if(t)setTimeout(()=>t.scrollIntoView({block:"center",behavior:"smooth"}),400)}

/* ---------- Página del widget ---------- */
if($("#wPreview")){let dark=false;const render=()=>{const w=WEEK[todayIdx];$("#wPreview").innerHTML=`<div style="max-width:420px;border-radius:18px;padding:20px;font-family:Georgia,serif;${dark?"background:#14302A;color:#EEF2EC":"background:#fff;color:#17211C;border:1px solid #CDD6CB"}"><div style="font:700 11px/1.3 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:${dark?"#D6B266":"#2C5D47"}">Evangelio de hoy · ${esc(w.wd)} ${w.n} de ${esc(w.mes)}</div><div style="font-size:20px;margin:8px 0">${esc(w.title)}</div><div style="font-style:italic;font-size:16px;line-height:1.5;opacity:.9">«${esc(w.ex)}»</div><div style="font:13px system-ui,sans-serif;margin-top:12px;opacity:.75">${esc(w.refL)} · Escuchar en Rezo Diario ›</div></div>`};render();
 $("#wDark").onclick=e=>{dark=!dark;e.currentTarget.setAttribute("aria-pressed",dark);const c=$("#wCode");c.textContent=c.textContent.replace(/<div id="rezodiario-evangelio"( data-tema="oscuro")?>/,dark?'<div id="rezodiario-evangelio" data-tema="oscuro">':'<div id="rezodiario-evangelio">');render()};
 $("#wCopy").onclick=()=>{const t=$("#wCode").textContent;const sel=()=>{const r=document.createRange();r.selectNodeContents($("#wCode"));const s=getSelection();s.removeAllRanges();s.addRange(r);toast("Código seleccionado: cópialo con tu teclado")};navigator.clipboard&&navigator.clipboard.writeText?navigator.clipboard.writeText(t).then(()=>toast("Código copiado"),sel):sel()}}

/* ---------- Donaciones ---------- */
if($("#give")){
 const AMTS=[5,10,25,50,100];let freq="once",amount=10,other=false;
 $("#amts").innerHTML=AMTS.map(a=>`<button class="amt" type="button" data-a="${a}">${a} €</button>`).join("")+`<button class="amt amt-o" type="button" data-a="o">Otra cantidad</button>`;
 $$("#amts .amt").forEach(b=>b.onclick=()=>{if(b.dataset.a==="o"){other=true;$("#otherBox").hidden=false;$("#otherAmt").focus();const v=Math.round(+$("#otherAmt").value);if(v>0)amount=v}else{other=false;$("#otherBox").hidden=true;amount=+b.dataset.a}r()});
 $("#otherAmt").addEventListener("input",e=>{const v=Math.round(+e.target.value);if(v>0){amount=v;r()}});
 $$("#give .seg button").forEach(b=>b.onclick=()=>{freq=b.dataset.f;$$("#give .seg button").forEach(x=>x.classList.toggle("on",x===b));r()});
 function r(){$$("#amts .amt").forEach(b=>b.classList.toggle("on",other?b.dataset.a==="o":+b.dataset.a===amount));$("#donBtn").textContent=`${freq==="month"?"Apoyar con":"Donar"} ${amount} €${freq==="month"?" al mes":""}`;$("#thanks").hidden=true}
 $("#donBtn").onclick=()=>{const pay=$("#give").dataset.pay;if(pay){const a=document.createElement("a");a.href=pay+(pay.includes("?")?"&":"?")+"amount="+amount+"&frecuencia="+freq;a.target="_blank";a.rel="noopener";document.body.appendChild(a);a.click();a.remove();return}const t=$("#thanks");t.hidden=false;t.innerHTML=`<strong>Gracias por querer aportar ${amount} €${freq==="month"?" al mes":""}.</strong><br>El pago seguro estará disponible muy pronto. Ahora mismo no se realiza ningún cobro.`};r();
}

/* ---------- Boletín ---------- */
const nf=$("#newsForm");if(nf)nf.onsubmit=e=>{e.preventDefault();const v=$("#email").value.trim(),m=$("#newsMsg");m.hidden=false;
 if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)){m.textContent="Revisa el correo: falta la @ o el dominio.";$("#email").focus();return}
 m.textContent="Apuntado. Recibirás el primer rezo a las 7:00 cuando el boletín esté conectado.";$("#email").value=""};

/* ---------- Vidriera gótica con cruz, rayos de luz y polvo ---------- */
const cv=$("#rose");
if(cv){const cx=cv.getContext("2d");let C={},W=0,H=0,on=true,motes=[];const reduce=matchMedia("(prefers-reduced-motion: reduce)").matches;
 const rc=()=>{const cs=getComputedStyle(root);C={gold:cs.getPropertyValue("--gold").trim(),ink:cs.getPropertyValue("--hero-ink").trim(),g:cs.getPropertyValue("--lit-green").trim(),r:cs.getPropertyValue("--lit-red").trim(),v:cs.getPropertyValue("--c-peace").trim(),b:cs.getPropertyValue("--c-study").trim(),hero:cs.getPropertyValue("--hero").trim()}};
 const size=()=>{const r=cv.getBoundingClientRect(),dpr=Math.min(2,devicePixelRatio||1);W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;cx.setTransform(dpr,0,0,dpr,0,0);
  motes=Array.from({length:W>700?46:22},()=>({x:Math.random(),y:Math.random(),s:.6+Math.random()*1.6,v:.2+Math.random()*.6,p:Math.random()*6.28}))};
 // geometría de la ventana
 const geo=()=>{const wide=W>940;if(!wide){const ww=Math.min(150,W*.36),wh=ww*2.1;return{X:W-ww*.75,top:-wh*.28,ww,wh}}
  const cr=cv.getBoundingClientRect(),st=cv.parentElement.querySelector(".stag"),pl=cv.parentElement.querySelector(".player");let a=W*.45,b=W*.6;
  if(st&&pl){a=Math.max(...[...st.children].map(e=>e.getBoundingClientRect().right))-cr.left;b=pl.getBoundingClientRect().left-cr.left}
  const ww=Math.max(110,Math.min(190,(b-a)*.8)),wh=Math.min(H*.78,ww*2.1);return{X:(a+b)/2,top:H*.5-wh*.5,ww,wh}};
 function arch(X,top,ww,wh){const l=X-ww/2,r=X+ww/2,spring=top+ww*.86,bot=top+wh;cx.beginPath();cx.moveTo(l,bot);cx.lineTo(l,spring);
  cx.arcTo(l,top+ww*.2,X,top,ww*.95);cx.lineTo(X,top);cx.arcTo(r,top+ww*.2,r,spring,ww*.95);cx.lineTo(r,bot);cx.closePath()}
 const draw=t=>{cx.clearRect(0,0,W,H);const {X,top,ww,wh}=geo();const tt=reduce?0:t;
  // rayos de luz que entran en diagonal
  const flick=.85+.15*Math.sin(tt*.0006);
  for(let k=0;k<3;k++){const off=(k-1)*ww*.32;const g=cx.createLinearGradient(X,top+wh*.3,X-W*.55,H*1.05);g.addColorStop(0,C.gold+Math.round((k===1?40:24)*flick).toString(16).padStart(2,"0"));g.addColorStop(1,"transparent");
   cx.fillStyle=g;cx.beginPath();cx.moveTo(X+off-ww*.16,top+wh*.25);cx.lineTo(X+off+ww*.16,top+wh*.3);cx.lineTo(X+off-W*.42+ww*.5,H*1.1);cx.lineTo(X+off-W*.62,H*1.1);cx.closePath();cx.fill()}
  // resplandor detrás de la ventana
  const halo=cx.createRadialGradient(X,top+wh*.45,0,X,top+wh*.45,ww*1.6);halo.addColorStop(0,C.gold+"26");halo.addColorStop(1,"transparent");cx.fillStyle=halo;cx.fillRect(0,0,W,H);
  // vidrios de colores
  cx.save();arch(X,top,ww,wh);cx.clip();
  const tints=[C.b,C.r,C.g,C.v,C.gold];const cols=4,rows=9,cw=ww/cols,ch=wh/rows;
  for(let i=0;i<cols;i++)for(let j=0;j<rows;j++){const k=(i*3+j*2)%5;const a=.10+.05*Math.sin(tt*.0008+i+j);cx.fillStyle=tints[k]+Math.round(a*255).toString(16).padStart(2,"0");cx.fillRect(X-ww/2+i*cw,top+j*ch,cw,ch)}
  // cruz luminosa
  const cxm=X,cyc=top+wh*.42,cl=wh*.5,cwid=ww*.13,arm=ww*.62;
  const cg=cx.createRadialGradient(cxm,cyc,0,cxm,cyc,wh*.45);cg.addColorStop(0,C.gold+"cc");cg.addColorStop(.6,C.gold+"66");cg.addColorStop(1,C.gold+"22");cx.fillStyle=cg;
  cx.fillRect(cxm-cwid/2,cyc-cl*.42,cwid,cl);cx.fillRect(cxm-arm/2,cyc-cl*.2,arm,cwid);
  // emplomado
  cx.strokeStyle=C.hero+"cc";cx.lineWidth=2;
  for(let i=1;i<cols;i++){cx.beginPath();cx.moveTo(X-ww/2+i*cw,top);cx.lineTo(X-ww/2+i*cw,top+wh);cx.stroke()}
  for(let j=1;j<rows;j++){cx.beginPath();cx.moveTo(X-ww/2,top+j*ch);cx.lineTo(X+ww/2,top+j*ch);cx.stroke()}
  cx.strokeStyle=C.gold+"55";cx.lineWidth=1.2;cx.strokeRect(cxm-cwid/2,cyc-cl*.42,cwid,cl);cx.strokeRect(cxm-arm/2,cyc-cl*.2,arm,cwid);
  // pequeño rosetón en la punta
  cx.beginPath();cx.arc(X,top+ww*.42,ww*.2,0,6.283);cx.strokeStyle=C.hero+"dd";cx.lineWidth=3;cx.stroke();
  for(let i=0;i<6;i++){const a=i*Math.PI/3+tt*.00004;cx.beginPath();cx.arc(X+Math.cos(a)*ww*.1,top+ww*.42+Math.sin(a)*ww*.1,ww*.07,0,6.283);cx.strokeStyle=C.gold+"66";cx.lineWidth=1.2;cx.stroke()}
  cx.restore();
  // marco de piedra
  arch(X,top,ww,wh);cx.strokeStyle=C.ink+"30";cx.lineWidth=6;cx.stroke();arch(X,top,ww,wh);cx.strokeStyle=C.gold+"55";cx.lineWidth=1.2;cx.stroke();
  // mainel central y alféizar
  cx.fillStyle=C.ink+"22";cx.fillRect(X-ww/2-14,top+wh,ww+28,7);
  // motas de polvo dentro de la luz
  motes.forEach(m=>{const y=((m.y+tt*.000015*m.v)%1);const px=X-ww*.2-(y*H*.9)*.62+m.x*ww*1.4-ww*.5;const py=top+wh*.35+y*(H-top-wh*.35);const a=.25+.35*Math.sin(tt*.002+m.p);
   cx.beginPath();cx.arc(px+Math.sin(tt*.0005+m.p)*6,py,m.s,0,6.283);cx.fillStyle=C.gold+Math.round(Math.max(0,a)*255).toString(16).padStart(2,"0");cx.fill()})};
 const loop=t=>{if(on)draw(t);if(!reduce)requestAnimationFrame(loop)};
 rc();size();addEventListener("resize",()=>{size();draw(performance.now())});document.addEventListener("rd-theme",()=>{rc();draw(performance.now())});
 matchMedia("(prefers-color-scheme: dark)").addEventListener("change",rc);new IntersectionObserver(e=>on=e[0].isIntersecting).observe(cv);requestAnimationFrame(loop);if(reduce)draw(0)}

/* ---------- Versículos: escuchar, compartir en imagen y «Necesito un versículo ahora» ---------- */
{
const MARK=[["#D9A441","M6.1 12.6A10 10 0 0 1 14.8 4.07V12.6Z"],["#E07A4F","M17.2 4.07A10 10 0 0 1 25.9 12.6H17.2Z"],["#2E8B67","M6 15H14.8V28H8a2 2 0 0 1-2-2Z"],["#3E72B0","M17.2 15H26V26a2 2 0 0 1-2 2H17.2Z"]];
const vOf=el=>{const c=el.closest("[data-ref]");return c?{ref:c.dataset.ref,x:c.dataset.x,tag:c.dataset.tag||""}:null};
function vSay(text,onend){if(!synth){toast("Tu navegador no puede leer en voz alta");return}synth.cancel();pickVoice();const u=new SpeechSynthesisUtterance(text);u.lang="es-ES";u.rate=.95;if(voice)u.voice=voice;if(onend)u.onend=onend;synth.speak(u)}
function wrap(ctx,text,maxW){const words=text.split(/\s+/),lines=[];let line="";for(const w of words){const t=line?line+" "+w:w;if(ctx.measureText(t).width>maxW&&line){lines.push(line);line=w}else line=t}if(line)lines.push(line);return lines}
async function vImage(v){
 const W=1080,H=1920,cv=document.createElement("canvas");cv.width=W;cv.height=H;const g=cv.getContext("2d");
 try{await Promise.all(["italic 400 60px Literata","400 40px Marcellus","800 40px Manrope","500 40px Manrope"].map(f=>document.fonts.load(f)))}catch(e){}
 const bg=g.createLinearGradient(0,0,0,H);bg.addColorStop(0,"#1B3D34");bg.addColorStop(1,"#0A1714");g.fillStyle=bg;g.fillRect(0,0,W,H);
 const gl=g.createRadialGradient(W/2,1010,0,W/2,1010,900);gl.addColorStop(0,"rgba(214,178,102,.28)");gl.addColorStop(1,"rgba(214,178,102,0)");g.fillStyle=gl;g.fillRect(0,0,W,H);
 g.strokeStyle="rgba(214,178,102,.22)";g.lineWidth=2;[440,600].forEach(r=>{g.beginPath();g.arc(W/2,1010,r,0,Math.PI*2);g.stroke()});
 const drawMark=(x,y,s)=>{g.save();g.translate(x,y);g.scale(s/32,s/32);MARK.forEach(([c,d])=>{g.fillStyle=c;g.fill(new Path2D(d))});g.restore()};
 drawMark(W/2-70,170,140);
 g.textAlign="center";g.fillStyle="rgba(238,242,236,.72)";g.font="800 30px Manrope";const tag=(v.tag||"Versículo de la Biblia").toUpperCase();
 g.save();g.letterSpacing="6px";g.fillText(tag,W/2,400);g.restore();
 let fs=78,lines;const maxW=W-200;
 do{g.font=`italic 400 ${fs}px Literata, Georgia, serif`;lines=wrap(g,"«"+v.x+"»",maxW);fs-=4}while(lines.length*fs*1.38>880&&fs>36);
 fs+=4;const lh=fs*1.38,blk=lines.length*lh+120,top=470+(1080-blk)/2+fs;g.fillStyle="#F3F1E8";
 lines.forEach((l,i)=>g.fillText(l,W/2,top+i*lh));
 const yRef=top+(lines.length-1)*lh+140;g.fillStyle="#D6B266";g.fillRect(W/2-40,yRef-50,80,3);g.font="800 46px Manrope";g.fillText(v.ref,W/2,yRef+20);
 g.font="800 44px Manrope";const a="rezo",b="diario",wa=g.measureText(a).width;g.font="500 44px Manrope";const wb=g.measureText(b).width;const tot=58+18+wa+wb,x0=W/2-tot/2;
 drawMark(x0,H-232,58);g.textAlign="left";g.fillStyle="#EEF2EC";g.font="800 44px Manrope";g.fillText(a,x0+76,H-186);g.fillStyle="#D6B266";g.font="500 44px Manrope";g.fillText(b,x0+76+wa,H-186);
 g.textAlign="center";g.fillStyle="rgba(238,242,236,.6)";g.font="600 28px Manrope";g.fillText("rezodiario.com · un momento con Dios cada día",W/2,H-120);
 return new Promise(r=>cv.toBlob(r,"image/png"));
}
let vModal=null;
function vPreview(blob,v){
 if(!vModal){vModal=document.createElement("div");vModal.className="vmodal";vModal.innerHTML='<div class="vmodal-bg" data-x></div><div class="vmodal-p" role="dialog" aria-modal="true" aria-label="Imagen del versículo"><img alt=""><div class="vacts"><a class="vbtn gold" download="versiculo-rezodiario.png">⬇️ Descargar imagen</a><button class="vbtn" type="button" data-share>Compartir</button><button class="vbtn" type="button" data-x>Cerrar</button></div><p class="note">Guárdala y súbela a tus Stories de Instagram, WhatsApp, TikTok o Pinterest.</p></div>';document.body.appendChild(vModal);
  vModal.addEventListener("click",e=>{if(e.target.closest("[data-x]")){vModal.hidden=true}});addEventListener("keydown",e=>{if(e.key==="Escape"&&vModal)vModal.hidden=true})}
 const u=URL.createObjectURL(blob);vModal.querySelector("img").src=u;vModal.querySelector("img").alt="«"+v.x+"» "+v.ref;vModal.querySelector("a[download]").href=u;
 const sb=vModal.querySelector("[data-share]");sb.hidden=!navigator.share;sb.onclick=()=>navigator.share({title:v.ref,text:"«"+v.x+"» "+v.ref+" · rezodiario.com",url:location.href.split("#")[0]}).catch(()=>{});
 vModal.hidden=false;
}
async function vShare(v,btn){
 if(btn){btn.disabled=true}const blob=await vImage(v);if(btn){btn.disabled=false}if(!blob)return;
 const f=new File([blob],"versiculo-rezodiario.png",{type:"image/png"});
 if(navigator.canShare&&navigator.canShare({files:[f]})&&matchMedia("(pointer:coarse)").matches){try{await navigator.share({files:[f],text:"«"+v.x+"» "+v.ref+" · rezodiario.com"});return}catch(e){if(e.name==="AbortError")return}}
 vPreview(blob,v);
}
document.addEventListener("click",e=>{
 const s=e.target.closest("[data-vspeak]"),i=e.target.closest("[data-vimg]"),c=e.target.closest("[data-vcopy]");if(!s&&!i&&!c)return;
 const v=vOf(e.target);if(!v)return;
 if(s)vSay(v.x+". "+v.ref.replace(/,/g," "));
 if(i)vShare(v,i);
 if(c)navigator.clipboard.writeText("«"+v.x+"» "+v.ref+" · "+location.href.split("#")[0]).then(()=>toast("Versículo copiado")).catch(()=>{});
});
const vl=$("#vListen");
if(vl){let on=false;const cards=$$(".vcard");vl.addEventListener("click",()=>{
 if(on){on=false;synth&&synth.cancel();vl.querySelector("span").textContent="Escuchar los versículos";$$(".vcard.reading").forEach(x=>x.classList.remove("reading"));return}
 on=true;vl.querySelector("span").textContent="Parar";let k=0;
 const next=()=>{if(!on||k>=cards.length){on=false;vl.querySelector("span").textContent="Escuchar los versículos";$$(".vcard.reading").forEach(x=>x.classList.remove("reading"));return}
  $$(".vcard.reading").forEach(x=>x.classList.remove("reading"));const cd=cards[k++];cd.classList.add("reading");cd.scrollIntoView({behavior:"smooth",block:"center"});
  vSay(cd.dataset.x+". "+cd.dataset.ref.replace(/,/g," "),()=>setTimeout(next,1200))};next()})}
const vn=$("#vNow");
if(vn&&window.RDV){let cur=null,last="";const show=slug=>{const t=RDV[slug];if(!t)return;cur=slug;let v;do{v=t.v[Math.floor(Math.random()*t.v.length)]}while(t.v.length>1&&v[0]===last);last=v[0];
  vn.dataset.ref=v[0];vn.dataset.x=v[1];vn.dataset.tag=t.t;$("#vNowTag").textContent=t.t;$("#vNowX").textContent="«"+v[1]+"»";$("#vNowR").textContent=v[0];$("#vNowE").textContent=v[2];
  $("#vNowWa").href="https://wa.me/?text="+encodeURIComponent("«"+v[1]+"» "+v[0]+" · https://rezodiario.com/"+slug);$("#vNowMore").href=ROOT+slug+X;$("#vNowMore").textContent="Ver los "+t.v.length+" "+t.t.toLowerCase()+" →";
  vn.hidden=false;vn.classList.remove("pop");void vn.offsetWidth;vn.classList.add("pop");
  $$(".mood").forEach(b=>b.classList.toggle("on",b.dataset.m===slug))};
 $$(".mood").forEach(b=>b.addEventListener("click",()=>{show(b.dataset.m);if(innerWidth<900)vn.scrollIntoView({behavior:"smooth",block:"nearest"})}));
 $("#vNowAgain").addEventListener("click",()=>cur&&show(cur));}
}

/* ---------- Web instalable (solo en el dominio real) ---------- */
if("serviceWorker" in navigator&&location.protocol==="https:"&&/rezodiario\.com$/.test(location.hostname)){navigator.serviceWorker.register("/sw.js").catch(()=>{})}
})();
