(function(){
  const html = document.documentElement;
  const toggle = document.getElementById('themeToggle');
  if (!toggle) return;
  toggle.addEventListener('click', async () => {
    const next = html.classList.contains('dark') ? 'light' : 'dark';
    try{
      const res = await fetch('/set_theme', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({mode: next})
      });
      const data = await res.json();
      if (data.status === 'ok') {
        if (next === 'dark') html.classList.add('dark');
        else html.classList.remove('dark');
        toggle.textContent = next === 'dark' ? '🌙' : '☀️';
      }
    }catch(e){
      console.warn('theme toggle failed', e);
    }
  });
})();
