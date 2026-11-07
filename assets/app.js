/* shared behaviour: themes, nav, TOC, progress, reveal, tabs. Vanilla JS, no deps. */
(function(){
  'use strict';
  var d=document, root=d.documentElement, body=d.body;
  root.classList.add('js');
  var store={get:function(k){try{return localStorage.getItem(k)}catch(e){return null}},set:function(k,v){try{localStorage.setItem(k,v)}catch(e){}}};
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* theme: parchment -> light -> dark */
  var themes=['parchment','light','dark'], names={parchment:'羊皮纸',light:'亮色',dark:'暗色'};
  function setTheme(t){root.setAttribute('data-theme',t);store.set('ld30-theme',t);var b=d.getElementById('theme-btn');if(b){var l=b.querySelector('.lbl');if(l)l.textContent=names[t];b.setAttribute('aria-label','切换主题（当前：'+names[t]+'）');}}
  var tb=d.getElementById('theme-btn');
  setTheme(root.getAttribute('data-theme')||'parchment');
  if(tb)tb.addEventListener('click',function(){var i=themes.indexOf(root.getAttribute('data-theme'));setTheme(themes[(i+1)%themes.length]);});

  /* mobile nav */
  var nb=d.getElementById('nav-btn');
  if(nb)nb.addEventListener('click',function(){var o=body.classList.toggle('nav-open');nb.setAttribute('aria-expanded',o?'true':'false');});
  d.addEventListener('click',function(e){if(body.classList.contains('nav-open')&&!e.target.closest('.nav')&&!e.target.closest('#nav-btn')){body.classList.remove('nav-open');if(nb)nb.setAttribute('aria-expanded','false');}});

  /* TOC */
  var toc=d.getElementById('toc'), tbtn=d.getElementById('toc-btn');
  if(toc){
    var wide=function(){return window.matchMedia('(min-width:1100px)').matches};
    var pref=store.get('ld30-toc');
    function setToc(open,save){body.setAttribute('data-toc',open?'open':'closed');if(tbtn){tbtn.setAttribute('aria-expanded',open?'true':'false');var l=tbtn.querySelector('.lbl');if(l)l.textContent=open?'隐藏目录':'显示目录';}if(save&&wide())store.set('ld30-toc',open?'open':'closed');}
    setToc(wide()?(pref!=='closed'):false,false);
    if(tbtn)tbtn.addEventListener('click',function(){setToc(body.getAttribute('data-toc')!=='open',true);});
    var sc=d.querySelector('.toc-scrim');if(sc)sc.addEventListener('click',function(){setToc(false,false)});
    var cl=toc.querySelector('.toc-close');if(cl)cl.addEventListener('click',function(){setToc(false,true)});
    toc.addEventListener('click',function(e){if(e.target.closest('a')&&!wide())setToc(false,false)});
    d.addEventListener('keydown',function(e){if(e.key==='Escape'){if(!wide())setToc(false,false);body.classList.remove('nav-open')}});
    var links=[].slice.call(toc.querySelectorAll('a[href^="#"]')), map={};
    links.forEach(function(a){var id=decodeURIComponent(a.getAttribute('href').slice(1));var el=d.getElementById(id);if(el)map[id]={a:a,el:el}});
    var ids=Object.keys(map);
    function spy(){var y=window.scrollY+90,cur=null;for(var i=0;i<ids.length;i++){if(map[ids[i]].el.getBoundingClientRect().top+window.scrollY<=y)cur=ids[i];else break;}
      links.forEach(function(a){a.classList.remove('on')});
      if(cur){var a=map[cur].a;a.classList.add('on');if(body.getAttribute('data-toc')==='open'){var r=a.getBoundingClientRect(),tr=toc.getBoundingClientRect();if(r.top<tr.top+40||r.bottom>tr.bottom-40)toc.scrollTop+=r.top-tr.top-tr.height/3;}}}
    var tk=false;window.addEventListener('scroll',function(){if(!tk){tk=true;requestAnimationFrame(function(){spy();tk=false})}},{passive:true});spy();
  }

  /* progress + back to top */
  var pg=d.getElementById('progress'), tt=d.getElementById('totop'), tick=false;
  function onScroll(){var h=root.scrollHeight-window.innerHeight;var p=h>0?Math.min(1,window.scrollY/h):0;if(pg)pg.style.transform='scaleX('+p+')';if(tt)tt.classList.toggle('show',window.scrollY>700);}
  window.addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(function(){onScroll();tick=false})}},{passive:true});onScroll();
  if(tt)tt.addEventListener('click',function(){window.scrollTo({top:0,behavior:reduce?'auto':'smooth'})});

  /* reveal on scroll */
  var rv=[].slice.call(d.querySelectorAll('.rv'));
  if('IntersectionObserver' in window&&!reduce){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -6% 0px',threshold:.04});rv.forEach(function(el){io.observe(el)});setTimeout(function(){rv.forEach(function(el){el.classList.add('in')})},4000);}else{rv.forEach(function(el){el.classList.add('in')})}
  /* anchors targeted directly must be visible */
  if(location.hash){var t=d.getElementById(decodeURIComponent(location.hash.slice(1)));if(t){var rr=t.closest('.rv');if(rr)rr.classList.add('in');var dd=t.closest('details');if(dd)dd.open=true;}}

  /* tabs */
  [].forEach.call(d.querySelectorAll('[data-tabs]'),function(box){
    var btns=[].slice.call(box.querySelectorAll('.tab-list button')), panels=[].slice.call(box.querySelectorAll('.tab-panel'));
    function show(i){btns.forEach(function(b,j){b.setAttribute('aria-selected',j===i?'true':'false')});panels.forEach(function(p,j){p.classList.toggle('on',j===i)});}
    btns.forEach(function(b,i){b.addEventListener('click',function(){show(i)});b.addEventListener('keydown',function(e){if(e.key==='ArrowRight'){btns[(i+1)%btns.length].focus();show((i+1)%btns.length)}if(e.key==='ArrowLeft'){btns[(i+btns.length-1)%btns.length].focus();show((i+btns.length-1)%btns.length)}})});
    show(0);
  });
  /* expand/collapse all details inside a container */
  [].forEach.call(d.querySelectorAll('[data-expand]'),function(b){b.addEventListener('click',function(){var open=b.getAttribute('data-expand')==='open';[].forEach.call(d.querySelectorAll(b.getAttribute('data-target')||'details.dq'),function(x){x.open=open})})});
  /* print button */
  [].forEach.call(d.querySelectorAll('[data-print]'),function(b){b.addEventListener('click',function(){window.print()})});

  /* optional read-aloud: browser speech only, never autoplay, not a human recording */
  var ra=d.getElementById('read-aloud'), rst=d.getElementById('read-status');
  function sayStatus(t){if(rst)rst.textContent=t;}
  if(ra){
    if(!window.speechSynthesis||typeof SpeechSynthesisUtterance==='undefined'){
      ra.disabled=true;
      sayStatus('此浏览器没有语音合成接口。请改用系统或阅读器的朗读。本站没有预录人声，也不会自动播放。');
    }else{
      ra.addEventListener('click',function(){
        if(window.speechSynthesis.speaking||window.speechSynthesis.pending){
          window.speechSynthesis.cancel();
          ra.setAttribute('aria-pressed','false');
          sayStatus('已停止。这是浏览器语音，不是人声录音。');
          return;
        }
        var main=d.getElementById('main');
        var text=(main?main.innerText:'').replace(/\s+/g,' ').trim();
        if(!text){sayStatus('没有可朗读的正文。');return;}
        if(text.length>6000)text=text.slice(0,6000);
        var u=new SpeechSynthesisUtterance(text);
        u.lang='zh-CN';
        u.rate=0.95;
        var voices=[];
        try{voices=window.speechSynthesis.getVoices()||[];}catch(e){voices=[];}
        var zh=voices.filter(function(v){return /zh|cmn/i.test(v.lang||'')});
        if(zh.length)u.voice=zh[0];
        u.onend=function(){ra.setAttribute('aria-pressed','false');sayStatus('朗读结束。这是浏览器语音，不是人声录音。');};
        u.onerror=function(){ra.setAttribute('aria-pressed','false');sayStatus('朗读未能开始。请改用系统朗读。本站没有预录人声。');};
        ra.setAttribute('aria-pressed','true');
        sayStatus(zh.length?'正在用浏览器语音朗读（非真人录音）。再点一次可停止。':'已请求朗读。若听不见，多半是系统没有中文语音包。这不是人声录音。');
        window.speechSynthesis.speak(u);
      });
    }
  }

  /* step highlight: labels stay visible; play is opt-in and not a flashing loop */
  [].forEach.call(d.querySelectorAll('[data-viz]'),function(box){
    var nodes=[].slice.call(box.querySelectorAll('[data-i]'));
    var notes=[].slice.call(box.querySelectorAll('[data-note]'));
    var buttons=[].slice.call(box.querySelectorAll('button[data-viz-i]'));
    var play=box.querySelector('[data-viz-play]');
    var reset=box.querySelector('[data-viz-reset]');
    var i=0, timer=null;
    var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
    var count=buttons.reduce(function(m,b){return Math.max(m,+b.getAttribute('data-viz-i')+1);},nodes.length||1);
    function show(n){
      if(!count)return;
      i=(n+count)%count;
      nodes.forEach(function(el){el.classList.toggle('is-on',el.getAttribute('data-i')===String(i));});
      buttons.forEach(function(b){b.setAttribute('aria-pressed',String(+b.getAttribute('data-viz-i'))===String(i)?'true':'false');});
      notes.forEach(function(p){p.hidden=p.getAttribute('data-note')!==String(i);});
    }
    function stop(){if(timer){clearInterval(timer);timer=null;}if(play)play.setAttribute('aria-pressed','false');}
    buttons.forEach(function(b){b.addEventListener('click',function(){stop();show(+b.getAttribute('data-viz-i'));});});
    if(play)play.addEventListener('click',function(){
      if(timer){stop();return;}
      play.setAttribute('aria-pressed','true');
      if(reduce){show(i+1);play.setAttribute('aria-pressed','false');return;}
      timer=setInterval(function(){show(i+1);},2800);
    });
    if(reset)reset.addEventListener('click',function(){
      stop();
      nodes.forEach(function(el){el.classList.remove('is-on');});
      buttons.forEach(function(b){b.setAttribute('aria-pressed','false');});
      notes.forEach(function(p){p.hidden=false;});
    });
    if(nodes.length)show(0);
  });
})();
