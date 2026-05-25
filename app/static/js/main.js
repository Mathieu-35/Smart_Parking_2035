// ─── Sidebar collapse ────────────────────────────────────
const sidebar     = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const toggleBtn   = document.getElementById('sidebarToggle');

function setSidebar(collapsed) {
  sidebar.classList.toggle('collapsed', collapsed);
  mainContent.classList.toggle('shifted', collapsed);
  localStorage.setItem('sidebar-collapsed', collapsed);
}

if (toggleBtn) {
  toggleBtn.addEventListener('click', () => {
    setSidebar(!sidebar.classList.contains('collapsed'));
  });
}

// Restore saved state
if (localStorage.getItem('sidebar-collapsed') === 'true') {
  setSidebar(true);
}

// ─── Delete confirmation ──────────────────────────────────
function confirmDelete(form) {
  if (confirm('Supprimer cet utilisateur ? Cette action est irreversible.')) {
    form.submit();
  }
  return false;
}

// ─── Auto-dismiss alerts ──────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const alert = document.querySelector('.alert');
  if (alert) {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  }
});
