document.addEventListener('DOMContentLoaded', function () {
  // Old home menu toggle (kept for safety if still used anywhere)
  const legacyToggle = document.querySelector('.home-menu-toggle');
  const legacyMenu = document.getElementById('home-menu');
  if (legacyToggle && legacyMenu) {
    legacyToggle.addEventListener('click', function (event) {
      event.stopPropagation();
      legacyMenu.classList.toggle('open');
    });
    document.addEventListener('click', function (event) {
      if (!legacyMenu.contains(event.target) && !legacyToggle.contains(event.target)) {
        legacyMenu.classList.remove('open');
      }
    });
  }

  // New landing page nav menu (only runs on home when elements exist)
  const menuBtn = document.getElementById('menu-btn');
  const navLinks = document.getElementById('nav-links');
  if (menuBtn && navLinks) {
    const menuBtnIcon = menuBtn.querySelector('i');
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      if (menuBtnIcon) {
        menuBtnIcon.setAttribute('class', isOpen ? 'ri-close-line' : 'ri-menu-4-line');
      }
    });
    navLinks.addEventListener('click', () => {
      navLinks.classList.remove('open');
      if (menuBtnIcon) {
        menuBtnIcon.setAttribute('class', 'ri-menu-4-line');
      }
    });
  }

  // ScrollReveal animations (home only, guarded if library not loaded)
  if (typeof ScrollReveal !== 'undefined') {
    const scrollRevealOption = {
      distance: '50px',
      origin: 'bottom',
      duration: 1000,
    };

    ScrollReveal().reveal('.header__image img', {
      ...scrollRevealOption,
      origin: 'right',
    });
    ScrollReveal().reveal('.header__content h2', {
      ...scrollRevealOption,
      delay: 500,
    });
    ScrollReveal().reveal('.header__content h1', {
      ...scrollRevealOption,
      delay: 1000,
    });
    ScrollReveal().reveal('.header__content p', {
      ...scrollRevealOption,
      delay: 1500,
    });
    ScrollReveal().reveal('.header__btn', {
      ...scrollRevealOption,
      delay: 2000,
    });
    ScrollReveal().reveal('.header__socials li', {
      ...scrollRevealOption,
      delay: 2500,
      interval: 500,
    });
  }

  // Subtle intro-style fade/slide for app panels on authenticated pages
  const appPanels = document.querySelectorAll('.app-panel');
  appPanels.forEach((panel, index) => {
    panel.style.opacity = '0';
    panel.style.transform = 'translateY(12px)';
    setTimeout(() => {
      panel.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
      panel.style.opacity = '1';
      panel.style.transform = 'translateY(0)';
    }, 120 + index * 120);
  });

  // Auto-fade flash messages after a short delay
  const flashMessages = document.querySelectorAll('.flashes .flash');
  if (flashMessages.length > 0) {
    setTimeout(() => {
      flashMessages.forEach((el) => {
        el.classList.add('flash-fade-out');
        // Remove from DOM after fade-out completes
        setTimeout(() => {
          if (el.parentNode) {
            el.parentNode.removeChild(el);
          }
        }, 450);
      });
    }, 3500);
  }

  // Profile dropdown in authenticated header
  const profileToggle = document.querySelector('.app-profile-toggle');
  const profileMenu = document.querySelector('.app-profile-menu');
  if (profileToggle && profileMenu) {
    profileToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      const isOpen = profileMenu.classList.toggle('open');
      profileToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      profileToggle.classList.toggle('open', isOpen);
    });

    document.addEventListener('click', (event) => {
      if (!profileMenu.contains(event.target) && !profileToggle.contains(event.target)) {
        profileMenu.classList.remove('open');
        profileToggle.setAttribute('aria-expanded', 'false');
        profileToggle.classList.remove('open');
      }
    });
  }

  // Notification bell dropdown in authenticated header
  const notifyToggle = document.querySelector('.app-notify-toggle');
  const notifyMenu = document.querySelector('.app-notify-menu');
  if (notifyToggle && notifyMenu) {
    notifyToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      const isOpen = notifyMenu.classList.toggle('open');
      notifyToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');

      // Once opened, clear the badge to indicate notifications are read
      if (isOpen) {
        const badge = notifyToggle.querySelector('.app-notify-badge');
        if (badge) {
          badge.remove();
        }
      }
    });

    document.addEventListener('click', (event) => {
      if (!notifyMenu.contains(event.target) && !notifyToggle.contains(event.target)) {
        notifyMenu.classList.remove('open');
        notifyToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Theme toggle (dark blue / rainbow / light) stored in localStorage
  const body = document.body;
  const THEME_KEY = 'neu_theme';
  const applyTheme = (theme) => {
    body.classList.remove('theme-darkblue', 'theme-rainbow', 'theme-light');
    if (theme === 'rainbow') {
      body.classList.add('theme-rainbow');
      body.dataset.theme = 'rainbow';
    } else if (theme === 'light') {
      body.classList.add('theme-light');
      body.dataset.theme = 'light';
    } else {
      body.classList.add('theme-darkblue');
      body.dataset.theme = 'darkblue';
    }

    const themeButtons = document.querySelectorAll('.app-profile-theme-btn');
    themeButtons.forEach((btn) => {
      if (btn.dataset.theme === theme) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  };

  // Initialize theme from storage
  const storedTheme = window.localStorage ? localStorage.getItem(THEME_KEY) : null;
  if (storedTheme === 'rainbow' || storedTheme === 'darkblue' || storedTheme === 'light') {
    applyTheme(storedTheme);
  } else {
    applyTheme(body.dataset.theme || 'darkblue');
  }

  const themeButtons = document.querySelectorAll('.app-profile-theme-btn');
  themeButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const allowed = ['darkblue', 'rainbow', 'light'];
      const theme = allowed.includes(btn.dataset.theme) ? btn.dataset.theme : 'darkblue';
      applyTheme(theme);
      if (window.localStorage) {
        localStorage.setItem(THEME_KEY, theme);
      }
    });
  });

  // Home hero icon-driven animation modes
  const homeRoot = document.body;
  if (homeRoot && homeRoot.classList.contains('home-body')) {
    const modeLinks = document.querySelectorAll('.header__socials a.home-mode-trigger');
    const MODE_CLASSES = ['home-mode-shield', 'home-mode-bug', 'home-mode-terminal'];

    const setMode = (modeClass) => {
      MODE_CLASSES.forEach((cls) => homeRoot.classList.remove(cls));
      if (modeClass) {
        homeRoot.classList.add(modeClass);
      }
    };

    modeLinks.forEach((link) => {
      const mode = link.dataset.mode;
      const modeClass = mode ? `home-mode-${mode}` : null;

      link.addEventListener('click', (event) => {
        event.preventDefault();
        if (!modeClass) return;

        // Toggle off if already active; otherwise activate this mode
        if (homeRoot.classList.contains(modeClass)) {
          homeRoot.classList.remove(modeClass);
        } else {
          setMode(modeClass);
        }
      });
    });
  }
});

