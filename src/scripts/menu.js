const menu = document.querySelector('.menu-btn');
const curtain = document.querySelector('.mobile-nav-curtain');

/* ── Mobile burger menu ── */

function collapseAllAccordions() {
  document.querySelectorAll('.mobile-nav-group.expanded').forEach((group) => {
    group.classList.remove('expanded');
    group.querySelector('.mobile-nav-trigger')?.setAttribute('aria-expanded', 'false');
  });
}

function closeMenu() {
  if (!menu) return;
  menu.setAttribute('aria-expanded', 'false');

  const header = menu.closest('.site-header');
  header?.classList.remove('menu-open');

  document.getElementById('menu-bread-top-close')?.beginElement();
  document.getElementById('menu-bread-bottom-close')?.beginElement();

  collapseAllAccordions();
}

menu?.addEventListener('click', () => {
  const isExpanded = menu.getAttribute('aria-expanded') === 'true';
  const nextExpanded = !isExpanded;
  menu.setAttribute('aria-expanded', `${nextExpanded}`);

  const header = menu.closest('.site-header');
  header?.classList.toggle('menu-open', nextExpanded);

  if (nextExpanded) {
    document.getElementById('menu-bread-top-open')?.beginElement();
    document.getElementById('menu-bread-bottom-open')?.beginElement();
  } else {
    document.getElementById('menu-bread-top-close')?.beginElement();
    document.getElementById('menu-bread-bottom-close')?.beginElement();
    collapseAllAccordions();
  }
});

curtain?.addEventListener('click', closeMenu);

document.querySelectorAll('.mobile-nav-trigger').forEach((trigger) => {
  trigger.addEventListener('click', () => {
    const group = trigger.closest('.mobile-nav-group');
    if (!group) return;
    const wasExpanded = group.classList.contains('expanded');
    group.classList.toggle('expanded');
    trigger.setAttribute('aria-expanded', `${!wasExpanded}`);
  });
});

/* ── Desktop flyout (shared container, JS-driven hover) ── */

const header = document.querySelector('.site-header');
const flyoutTriggers = document.querySelectorAll('[data-flyout]');
const flyoutContainer = document.querySelector('.flyout-container');
const flyoutPanels = document.querySelectorAll('.flyout-panel');
const nonFlyoutLinks = document.querySelectorAll('.nav-desktop > a:not([data-flyout])');
const siteBrand = document.querySelector('.site-brand');

let hideTimer = null;

function isFlyoutActive() {
  return flyoutContainer?.classList.contains('active');
}

function isInsideHoverZone(el) {
  return el && (header?.contains(el) || flyoutContainer?.contains(el));
}

function showFlyout(targetId) {
  clearTimeout(hideTimer);
  flyoutPanels.forEach(panel => {
    panel.classList.toggle('active', panel.id === `flyout-${targetId}`);
  });
  flyoutContainer?.classList.add('active');
  flyoutContainer?.setAttribute('aria-hidden', 'false');
}

function hideFlyout() {
  hideTimer = setTimeout(() => {
    flyoutContainer?.classList.remove('active');
    flyoutContainer?.setAttribute('aria-hidden', 'true');
    flyoutPanels.forEach(panel => panel.classList.remove('active'));
  }, 200);
}

function hideFlyoutNow() {
  clearTimeout(hideTimer);
  flyoutContainer?.classList.remove('active');
  flyoutContainer?.setAttribute('aria-hidden', 'true');
  flyoutPanels.forEach(panel => panel.classList.remove('active'));
}

flyoutTriggers.forEach(trigger => {
  trigger.addEventListener('mouseenter', () => {
    const target = trigger.getAttribute('data-flyout');
    if (target) showFlyout(target);
  });
});

nonFlyoutLinks.forEach(link => {
  link.addEventListener('mouseenter', hideFlyoutNow);
});

siteBrand?.addEventListener('mouseenter', () => {
  if (isFlyoutActive()) hideFlyoutNow();
});

header?.addEventListener('mouseleave', (e) => {
  if (!isFlyoutActive()) return;
  if (isInsideHoverZone(e.relatedTarget)) return;
  hideFlyout();
});

flyoutContainer?.addEventListener('mouseleave', (e) => {
  if (isInsideHoverZone(e.relatedTarget)) return;
  hideFlyout();
});
