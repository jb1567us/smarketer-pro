(function(){
  const btn = document.querySelector('.ttp-navtoggle');
  const menu = document.getElementById('ttp-mobilemenu');
  if(!btn || !menu) return;
  btn.addEventListener('click', function(){
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
    menu.hidden = expanded ? true : false;
  });
})();