(() => {
  const body = document.body;
  const menuButton = document.querySelector('[data-menu-toggle]');
  const navigation = document.querySelector('[data-navigation]');

  const setMenu = (open) => {
    if (!menuButton || !navigation) return;
    menuButton.setAttribute('aria-expanded', String(open));
    navigation.classList.toggle('is-open', open);
    body.classList.toggle('menu-open', open);
  };

  menuButton?.addEventListener('click', () => {
    setMenu(menuButton.getAttribute('aria-expanded') !== 'true');
  });

  navigation?.addEventListener('click', (event) => {
    if (event.target.closest('a')) setMenu(false);
  });

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setMenu(false);
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 720) setMenu(false);
  });

  document.querySelectorAll('a[target="_blank"]').forEach((link) => {
    const values = new Set((link.rel || '').split(/\s+/).filter(Boolean));
    values.add('noopener');
    values.add('noreferrer');
    link.rel = [...values].join(' ');
  });

  document.querySelectorAll('[data-current-year]').forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const revealItems = [...document.querySelectorAll('[data-reveal]')];

  if (!reduceMotion && revealItems.length && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('reveal-ready');
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.08 },
    );
    revealItems.forEach((item) => observer.observe(item));
  } else {
    revealItems.forEach((item) => item.classList.add('is-visible'));
  }

  const zoomButtons = [...document.querySelectorAll('[data-lightbox-src]')];
  if (!zoomButtons.length) return;

  const dialog = document.createElement('dialog');
  dialog.className = 'lightbox';
  dialog.setAttribute('aria-label', 'Image viewer');
  dialog.innerHTML = `
    <div class="lightbox-inner">
      <div class="lightbox-toolbar">
        <span class="lightbox-title">Drawing viewer</span>
        <button class="lightbox-close" type="button" aria-label="Close image viewer">Close</button>
      </div>
      <img src="" alt="">
      <p class="lightbox-caption"></p>
    </div>
  `;
  document.body.append(dialog);

  const dialogImage = dialog.querySelector('img');
  const dialogCaption = dialog.querySelector('.lightbox-caption');
  const closeButton = dialog.querySelector('.lightbox-close');

  zoomButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const thumbnail = button.querySelector('img');
      dialogImage.src = button.dataset.lightboxSrc;
      dialogImage.alt = thumbnail?.alt || '';
      dialogCaption.textContent = button.dataset.lightboxCaption || thumbnail?.alt || '';
      dialog.showModal();
    });
  });

  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
})();
