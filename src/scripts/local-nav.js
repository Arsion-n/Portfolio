const localnav = document.querySelector('[data-localnav]');
const toggle = localnav?.querySelector('[data-localnav-toggle]');
const tray = localnav?.querySelector('#localnav-menu-tray');

if (localnav && toggle && tray) {
  const chevronExpand = document.getElementById('localnav-chevron-expand');
  const chevronCollapse = document.getElementById('localnav-chevron-collapse');

  const closeMenu = () => {
    localnav.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    tray.setAttribute('aria-hidden', 'true');
    chevronCollapse?.beginElement();
  };

  const openMenu = () => {
    localnav.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
    tray.setAttribute('aria-hidden', 'false');
    chevronExpand?.beginElement();
  };

  toggle.addEventListener('click', () => {
    if (localnav.classList.contains('is-open')) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  tray.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const id = link.getAttribute('href')?.slice(1);
      const target = id && document.getElementById(id);
      if (target) {
        e.preventDefault();
        const offset = localnav.offsetHeight;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
      closeMenu();
    });
  });

  document.addEventListener('click', (event) => {
    if (!localnav.contains(event.target)) {
      closeMenu();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });

  /* Highlight current section link based on scroll position */
  const sectionLinks = [...tray.querySelectorAll('a[href^="#"]')];
  const sectionIds = sectionLinks.map((a) => a.getAttribute('href').slice(1));

  function updateCurrentLink() {
    const scrollY = window.scrollY;
    const offset = localnav.offsetHeight + 8;
    let activeId = sectionIds[0];

    for (const id of sectionIds) {
      const el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top + window.scrollY - offset <= scrollY) {
        activeId = id;
      }
    }

    sectionLinks.forEach((a) => {
      a.classList.toggle('current', a.getAttribute('href') === `#${activeId}`);
    });
  }

  window.addEventListener('scroll', updateCurrentLink, { passive: true });
  updateCurrentLink();
}
