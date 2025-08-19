document.addEventListener('DOMContentLoaded', () => {
  const btn = document.querySelector('.kw-nav__search-btn');
  const header = document.querySelector('.kw-nav');
  if (!btn || !header) return;

  btn.addEventListener('click', () => {
    const open = header.classList.toggle('kw-nav--search-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  document.addEventListener('click', (e) => {
    if (!header.contains(e.target)) header.classList.remove('kw-nav--search-open');
  });
});
