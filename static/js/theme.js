/* Theme: light / dark — persists in localStorage */
const AFS_THEME = {
  KEY: 'afs-theme',
  DEFAULT: 'dark',

  get() {
    try {
      const t = localStorage.getItem(this.KEY);
      return t === 'light' || t === 'dark' ? t : this.DEFAULT;
    } catch {
      return this.DEFAULT;
    }
  },

  apply(theme) {
    const next = theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try {
      localStorage.setItem(this.KEY, next);
    } catch {
      /* ignore */
    }
    this.syncControls(next);
  },

  syncControls(theme) {
    document.querySelectorAll('[data-theme-option]').forEach((btn) => {
      const on = btn.getAttribute('data-theme-option') === theme;
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    document.querySelectorAll('.theme-select').forEach((sel) => {
      if (sel.value !== theme) sel.value = theme;
    });
  },

  renderControl() {
    return `
      <div class="theme-switch" role="group" aria-label="Mavzu">
        <button type="button" class="theme-option" data-theme-option="light" title="Yorug' mavzu" aria-pressed="false">
          <span class="theme-swatch theme-swatch-light"></span>
          <span>Yorug'</span>
        </button>
        <button type="button" class="theme-option" data-theme-option="dark" title="Qorong'u mavzu" aria-pressed="false">
          <span class="theme-swatch theme-swatch-dark"></span>
          <span>Qorong'u</span>
        </button>
      </div>`;
  },

  bind(root = document) {
    root.querySelectorAll('[data-theme-option]').forEach((btn) => {
      if (btn.dataset.themeBound) return;
      btn.dataset.themeBound = '1';
      btn.addEventListener('click', () => {
        this.apply(btn.getAttribute('data-theme-option'));
      });
    });

    root.querySelectorAll('.theme-select').forEach((sel) => {
      if (sel.dataset.themeBound) return;
      sel.dataset.themeBound = '1';
      sel.addEventListener('change', () => this.apply(sel.value));
    });

    this.syncControls(this.get());
  },

  mountFloating() {
    if (document.getElementById('theme-switch-host')) return;
    if (document.getElementById('header-right')) return;

    const host = document.createElement('div');
    host.id = 'theme-switch-host';
    host.className = 'theme-switch-float';
    host.innerHTML = this.renderControl();
    document.body.appendChild(host);
    this.bind(host);
  },

  init() {
    this.apply(this.get());
    this.bind();
    this.mountFloating();
  }
};

AFS_THEME.apply(AFS_THEME.get());

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => AFS_THEME.init());
} else {
  AFS_THEME.init();
}

// Register the root-scoped Django service worker for PWA/offline support.
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((error) => {
      console.error('Service worker registration failed:', error);
    });
  });
}

