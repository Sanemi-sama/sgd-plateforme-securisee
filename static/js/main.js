// ── Sidebar toggle (mobile) ──────────────────
const sidebar = document.getElementById('sidebar');
const toggle = document.getElementById('sidebarToggle');
if (toggle && sidebar) {
  toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ── Auto-dismiss alerts after 5s ────────────
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => el.style.opacity === '' && el.remove(), 5000);
});

// ── Confirm delete ───────────────────────────
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

// ── Charts (Chart.js via CDN, chargé dans les templates qui en ont besoin) ──
window.sgdChart = function(id, type, labels, datasets, options = {}) {
  const ctx = document.getElementById(id);
  if (!ctx) return;
  return new Chart(ctx, {
    type,
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#8899b4', font: { family: 'Outfit' } } },
        tooltip: {
          backgroundColor: '#111827',
          borderColor: '#1e2d45',
          borderWidth: 1,
          titleColor: '#e2e8f0',
          bodyColor: '#8899b4',
        }
      },
      scales: type !== 'doughnut' ? {
        x: { ticks: { color: '#4a5c78' }, grid: { color: '#1e2d45' } },
        y: { ticks: { color: '#4a5c78' }, grid: { color: '#1e2d45' }, beginAtZero: true }
      } : {},
      ...options
    }
  });
};
