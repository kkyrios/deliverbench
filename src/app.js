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
const leaderboard = document.querySelector('.leaderboard');
sortSelect.addEventListener('change', () => {
  const key = sortSelect.value === 'pass_rate' ? 'pass' : 'final';
  const sorted = rows.slice().sort((a, b) => Number(b.dataset[key]) - Number(a.dataset[key]) || Number(b.dataset.final) - Number(a.dataset.final));
  sorted.forEach((row, index) => {
    row.querySelector('.rank').textContent = String(index + 1).padStart(2, '0');
    body.append(row);
  });
  const isFinal = key === 'final';
  leaderboard.dataset.primary = isFinal ? 'final' : 'pass_rate';
  document.querySelector('#final-heading').setAttribute('aria-sort', isFinal ? 'descending' : 'none');
  document.querySelector('#pass-heading').setAttribute('aria-sort', isFinal ? 'none' : 'descending');
  const message = `Ranked by ${isFinal ? 'final delivery' : 'subtask pass rate'}. The selected metric is emphasized.`;
  document.querySelector('#table-caption').textContent = `Seven evaluated systems. ${message}`;
  document.querySelector('#sort-status').textContent = message;
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

// P02 exploration enhances fully rendered task and dependency content.
const projectDataElement = document.querySelector('#p02-data');
if (projectDataElement) {
  const projectData = JSON.parse(projectDataElement.textContent);
  const showcase = document.querySelector('.project-showcase');
  const projectMap = showcase.querySelector('.project-map');
  const projectDetail = showcase.querySelector('#project-detail');
  const resetProject = showcase.querySelector('#project-reset');
  const projectNodes = new Map([...projectData.tasks, projectData.feedback].map(task => [task.id, task]));
  let selectedTask = null;
  showcase.classList.add('project-interactive');
  showcase.querySelectorAll('button[data-project-select]').forEach(button => { button.disabled = false; });
  projectDetail.hidden = false;
  resetProject.hidden = false;
  showcase.querySelector('.project-interaction-hint').hidden = false;

  function relatedLinks(containerId, ids) {
    const container = document.getElementById(containerId);
    container.replaceChildren();
    ids.forEach(id => {
      const link = document.createElement('a');
      link.href = `#p02-${id}`;
      link.textContent = id === 'LENDER' ? 'Lender questions' : id === 'FINAL' ? 'Final package' : id;
      if (projectNodes.has(id)) {
        link.dataset.projectSelect = id;
        link.title = projectNodes.get(id).label;
      }
      container.append(link);
    });
  }

  function selectProjectTask(id) {
    selectedTask = id;
    const task = projectNodes.get(id);
    const incoming = task ? projectData.edges.filter(edge => edge.to === id).map(edge => edge.from) : [];
    const outgoing = task ? projectData.edges.filter(edge => edge.from === id).map(edge => edge.to) : [];
    const related = new Set([...incoming, ...outgoing]);
    projectMap.classList.toggle('has-selection', Boolean(task));
    showcase.querySelectorAll('[data-project-node]').forEach(node => {
      const nodeId = node.dataset.projectNode;
      node.classList.toggle('is-selected', nodeId === id);
      node.classList.toggle('is-related', related.has(nodeId));
      node.classList.toggle('is-dimmed', Boolean(task) && nodeId !== id && !related.has(nodeId));
      node.querySelector('button')?.setAttribute('aria-pressed', String(nodeId === id));
    });
    showcase.querySelectorAll('.project-edge').forEach(path => {
      const active = path.dataset.from === id || path.dataset.to === id;
      path.classList.toggle('edge-active', active);
    });
    showcase.querySelectorAll('[data-output-source]').forEach(output => {
      output.classList.toggle('output-related', output.dataset.outputSource === id || id === 'T13');
    });
    showcase.querySelectorAll('.checkpoint-list a').forEach(link => {
      if (link.dataset.projectSelect === id) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
    document.querySelector('#project-detail-title').textContent = task ? `${id === 'LENDER' ? 'Business feedback' : id} · ${task.label}` : 'Explore the dependencies';
    document.querySelector('#project-detail-hint').textContent = task ? 'Highlighted connections show the selected task’s immediate inputs and handoffs.' : 'Select a task to trace the work it uses and the deliverables it informs.';
    document.querySelector('#project-detail-uses').textContent = task?.uses || 'Diligence, financing terms and models become inputs to later tasks.';
    document.querySelector('#project-detail-produces').textContent = task?.produces || 'Each submission becomes part of the agent’s persistent project workspace.';
    document.querySelector('#project-detail-feeds').textContent = task ? outgoing.map(target => target === 'FINAL' ? 'The six-file final delivery package' : projectNodes.get(target).label).join('; ') + '.' : 'Later reviews, lender responses and the final delivery package.';
    relatedLinks('project-detail-incoming', incoming);
    relatedLinks('project-detail-outgoing', outgoing);
    document.querySelector('#project-selection-status').textContent = task ? `${id}: ${task.label}. ${incoming.length} upstream and ${outgoing.length} downstream connections. Details updated below the map.` : 'All project connections shown.';
  }
  showcase.addEventListener('click', event => {
    const control = event.target.closest('[data-project-select]');
    if (!control) return;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    const id = control.dataset.projectSelect;
    selectProjectTask(id);
    if (control.tagName === 'A') {
      const node = document.getElementById(`p02-${id}`);
      node.querySelector('button')?.focus({ preventScroll: true });
      node.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    }
  });
  resetProject.addEventListener('click', () => selectProjectTask(null));
  showcase.addEventListener('keydown', event => {
    if (event.key === 'Escape' && selectedTask) { selectProjectTask(null); }
  });
}
