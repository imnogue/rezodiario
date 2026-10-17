/* Widget «Evangelio de hoy» de Rezo Diario. Uso:
   <div id="rezodiario-evangelio"><a href="https://rezodiario.com/evangelio-de-hoy.html">Evangelio de hoy en Rezo Diario</a></div>
   <script src="https://rezodiario.com/widget/evangelio.js" async></script>
   Añade data-tema="oscuro" al div para la versión oscura. */
(function(){
  var s=document.currentScript, base=(s&&s.src)?s.src.replace(/widget\/evangelio\.js.*$/,""):"https://rezodiario.com/";
  var box=document.getElementById("rezodiario-evangelio"); if(!box) return;
  var dark=box.getAttribute("data-tema")==="oscuro";
  var d=new Date(), iso=d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
  var LIT={green:"#3F8A5F",white:"#C9BFA3",red:"#B23A31",violet:"#6B4E8C",rose:"#D98BA6",blue:"#5B8FD1"};
  function esc(t){return String(t).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  fetch(base+"api/evangelio/"+iso+".json").then(function(r){return r.ok?r.json():null}).then(function(j){
    if(!j) return;
    var bg=dark?"#14302A":"#ffffff", fg=dark?"#EEF2EC":"#17211C", ac=dark?"#D6B266":"#2C5D47", bd=dark?"transparent":"#CDD6CB";
    box.innerHTML='<div style="box-sizing:border-box;max-width:100%;border-radius:18px;padding:20px;background:'+bg+';color:'+fg+';border:1px solid '+bd+';font-family:Georgia,serif">'+
      '<div style="font:700 11px/1.3 system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:'+ac+';display:flex;align-items:center;gap:8px"><span style="width:9px;height:9px;border-radius:50%;background:'+(LIT[j.color]||ac)+'"></span>Evangelio de hoy · '+esc(j.dia)+'</div>'+
      '<div style="font-size:20px;margin:8px 0">'+esc(j.titulo)+'</div>'+
      '<div style="font-style:italic;font-size:16px;line-height:1.5;opacity:.92">«'+esc(j.frase)+'»</div>'+
      '<a href="'+esc(j.url)+'" style="display:inline-block;margin-top:12px;font:600 13px system-ui,sans-serif;color:'+ac+';text-decoration:none">'+esc(j.cita)+' · Escuchar en Rezo Diario ›</a></div>';
  }).catch(function(){});
})();
