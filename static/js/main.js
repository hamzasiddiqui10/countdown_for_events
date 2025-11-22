// Theme handling
function applyTheme(theme) {
  document.body.classList.remove('theme-dark', 'theme-light');
  if (theme === 'dark') document.body.classList.add('theme-dark');
  else document.body.classList.add('theme-light');
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
  const current = localStorage.getItem('theme') || (document.body.classList.contains('theme-dark') ? 'dark' : 'light');
  const next = current === 'dark' ? 'light' : 'dark';
  localStorage.setItem('theme', next);
  applyTheme(next);
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  applyTheme(theme);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.addEventListener('click', toggleTheme);
}

// Finds all elements with class 'countdown' and updates them every second.
function startCountdowns() {
  const els = document.querySelectorAll('.countdown');
  function update() {
    const now = new Date();
    els.forEach(el => {
      const t = el.getAttribute('data-time');
      if (!t) return;
      const target = new Date(t);
      let diff = Math.floor((target - now) / 1000);
      if (diff <= 0) {
        el.textContent = 'Happening now or passed';
        return;
      }
      const days = Math.floor(diff / 86400); diff %= 86400;
      const hours = Math.floor(diff / 3600); diff %= 3600;
      const minutes = Math.floor(diff / 60); const seconds = diff % 60;
      el.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    });
  }
  update();
  setInterval(update, 1000);
}

document.addEventListener('DOMContentLoaded', function(){
  initTheme();
  startCountdowns();
});
