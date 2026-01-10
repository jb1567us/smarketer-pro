(function(){
  function qs(sel, ctx){ return (ctx||document).querySelector(sel); }
  var btn = qs('[data-ttp-navtoggle]');
  var menu = qs('[data-ttp-mobilemenu]');
  if(!btn || !menu) return;
  btn.addEventListener('click', function(){
    var open = menu.classList.toggle('is-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();