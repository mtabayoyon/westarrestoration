(function(){
  var box=document.querySelector('[data-triage]'), dataEl=document.getElementById('triage-data');
  if(!box||!dataEl) return;
  var data; try{data=JSON.parse(dataEl.textContent)}catch(e){return}
  var out=box.querySelector('.triage-out'), h=out.querySelector('.triage-out-h'),
      list=out.querySelector('.triage-steps'), more=out.querySelector('.triage-more');
  box.querySelectorAll('.triage-opt').forEach(function(btn){
    btn.setAttribute('role','button');
    btn.addEventListener('click',function(ev){
      var d=data[btn.dataset.key]; if(!d) return;
      ev.preventDefault();
      box.querySelectorAll('.triage-opt').forEach(function(b){b.setAttribute('aria-pressed','false')});
      btn.setAttribute('aria-pressed','true');
      h.textContent=d.name+': do this before we arrive';
      list.innerHTML='';
      d.now.forEach(function(t){var li=document.createElement('li');li.textContent=t;list.appendChild(li)});
      more.href=d.url; out.hidden=false;
      if(window.gtag) gtag('event','triage_select',{damage_type:btn.dataset.key});
    });
  });
  document.querySelectorAll('a[href^="tel:"]').forEach(function(a){
    a.addEventListener('click',function(){ if(window.gtag) gtag('event','phone_click',{location:location.pathname}); });
  });
})();
