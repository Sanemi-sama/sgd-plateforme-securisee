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

// ── System status (Wazuh) + critical banner ──
async function refreshSystemStatus() {
  const body = document.body;
  if (!body || body.dataset.auth !== '1' || body.dataset.isManager !== '1') return;

  const statusUrl = body.dataset.wazuhStatusUrl;
  if (!statusUrl) return;

  const dot = document.getElementById('systemStatusDot');
  const label = document.getElementById('systemStatusLabel');
  const banner = document.getElementById('criticalAlertBanner');
  const bannerText = document.getElementById('criticalAlertText');

  try {
    const resp = await fetch(statusUrl, { headers: { 'Accept': 'application/json' } });
    if (!resp.ok) throw new Error('bad_status');
    const data = await resp.json();

    const available = !!data.available;
    const critical = Number(data?.summary?.critical ?? 0);

    if (dot) {
      dot.classList.toggle('online', available);
      dot.classList.toggle('offline', !available);
    }
    if (label) {
      label.textContent = available
        ? `Wazuh connecté · Critiques: ${critical}`
        : 'Wazuh indisponible';
    }

    if (banner && bannerText) {
      if (available && critical > 0) {
        bannerText.textContent = `${critical} alerte${critical > 1 ? 's' : ''} critique${critical > 1 ? 's' : ''} détectée${critical > 1 ? 's' : ''} par Wazuh.`;
        banner.style.display = 'block';
      } else {
        banner.style.display = 'none';
      }
    }
  } catch (_e) {
    if (dot) {
      dot.classList.remove('online');
      dot.classList.add('offline');
    }
    if (label) label.textContent = 'Wazuh indisponible';
  }
}

// Refresh at load + every 60s (manager only)
document.addEventListener('DOMContentLoaded', () => {
  refreshSystemStatus();
  setInterval(refreshSystemStatus, 60000);
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
