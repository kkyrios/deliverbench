'use strict';

document.body.classList.add('js-enabled');
const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('#main-nav');
menuButton.hidden = false;
function closeMenu() { nav.classList.remove('open'); menuButton.setAttribute('aria-expanded', 'false'); }
menuButton.addEventListener('click', () => {
  const open = !nav.classList.contains('open');
  nav.classList.toggle('open', open);
  menuButton.setAttribute('aria-expanded', String(open));
});
nav.addEventListener('click', (event) => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && nav.classList.contains('open')) { closeMenu(); menuButton.focus(); } });
const mobileQuery = matchMedia('(max-width: 760px)');
mobileQuery.addEventListener('change', closeMenu);

const sortSelect = document.querySelector('#sort-by');
document.querySelector('#sort-control').hidden = false;
const body = document.querySelector('#leaderboard-body');
const rows = Array.from(body.rows);
sortSelect.addEventListener('change', () => {
  const key = sortSelect.value === 'pass_rate' ? 'pass' : 'final';
  const sorted = rows.slice().sort((a, b) => Number(b.dataset[key]) - Number(a.dataset[key]) || Number(b.dataset.final) - Number(a.dataset.final));
  sorted.forEach((row, index) => {
    row.querySelector('.rank').textContent = String(index + 1).padStart(2, '0');
    body.append(row);
    ['final', 'pass'].forEach((metric) => {
      const chart = document.querySelector(`#${metric}-chart`);
      const bar = chart.querySelector(`[data-system="${row.dataset.system}"]`);
      chart.append(bar);
    });
  });
  const isFinal = key === 'final';
  document.querySelector('#final-heading').setAttribute('aria-sort', isFinal ? 'descending' : 'none');
  document.querySelector('#pass-heading').setAttribute('aria-sort', isFinal ? 'none' : 'descending');
  document.querySelector('#table-caption').textContent = `Seven evaluated systems, ranked by ${isFinal ? 'final-delivery score' : 'subtask pass rate'}. Both charts follow this order.`;
});

const navLinks = Array.from(nav.querySelectorAll('a'));
const sections = navLinks.map(link => document.querySelector(link.getAttribute('href')));
let pendingFrame = false;
function updateNavigation() {
  let current = null;
  sections.forEach(section => { if (section.getBoundingClientRect().top < 180) current = section.id; });
  navLinks.forEach(link => {
    const active = link.getAttribute('href') === `#${current}`;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
  });
  pendingFrame = false;
}
window.addEventListener('scroll', () => { if (!pendingFrame) { pendingFrame = true; requestAnimationFrame(updateNavigation); } }, { passive: true });
updateNavigation();

const dialog = document.querySelector('#figure-dialog');
const dialogImage = document.querySelector('#dialog-image');
const viewport = document.querySelector('.figure-viewport');
const zoomLabel = document.querySelector('#zoom-level');
let opener = null;
let zoom = 1;
let fitWidth = 0;
function fitFigure() {
  zoom = 1;
  dialogImage.classList.add('fit');
  dialogImage.style.width = '';
  dialogImage.style.height = '';
  viewport.scrollTop = 0;
  viewport.scrollLeft = 0;
  zoomLabel.textContent = 'Fit';
  if (dialogImage.naturalWidth) {
    const availableW = viewport.clientWidth - 36;
    const availableH = viewport.clientHeight - 36;
    fitWidth = Math.min(availableW, availableH * dialogImage.naturalWidth / dialogImage.naturalHeight);
  }
}
function setZoom(value) {
  zoom = Math.max(1, Math.min(4, value));
  if (zoom === 1) { fitFigure(); return; }
  if (!fitWidth) fitFigure();
  dialogImage.classList.remove('fit');
  dialogImage.style.width = `${fitWidth * zoom}px`;
  dialogImage.style.height = 'auto';
  zoomLabel.textContent = `${Math.round(zoom * 100)}%`;
}
dialogImage.addEventListener('load', fitFigure);
document.querySelectorAll('[data-lightbox]').forEach(link => {
  link.addEventListener('click', event => {
    if (!dialog.showModal || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    document.querySelector('#figure-caption').textContent = link.dataset.caption;
    dialogImage.alt = link.querySelector('img').alt;
    dialogImage.src = link.href;
    dialog.showModal();
    document.body.classList.add('modal-open');
    fitFigure();
    document.querySelector('#close-figure').focus();
  });
});
document.querySelector('#close-figure').addEventListener('click', () => dialog.close());
document.querySelector('#zoom-in').addEventListener('click', () => setZoom(zoom + .5));
document.querySelector('#zoom-out').addEventListener('click', () => setZoom(zoom - .5));
document.querySelector('#zoom-fit').addEventListener('click', fitFigure);
dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
dialog.addEventListener('close', () => { document.body.classList.remove('modal-open'); dialogImage.removeAttribute('src'); opener?.focus(); });
window.addEventListener('resize', () => { if (dialog.open) fitFigure(); });
