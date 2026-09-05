/* Shared enhancement for the Chinese and English Atheneum homepages. */
(function () {
  'use strict';
  const scene = document.querySelector('.atheneum-scene');
  if (!scene) return;
  const data = JSON.parse(document.querySelector('#atheneum-profiles').textContent);
  const language = document.documentElement.lang.startsWith('en') ? 'en' : 'zh';
  const english = language === 'en';
  const selectors = [...document.querySelectorAll('[data-select-person]')];
  const card = document.querySelector('.atheneum-card');
  const dialog = document.querySelector('#atheneum-detail');
  const world = scene.querySelector('.atheneum-world');
  const motionButton = scene.querySelector('.atheneum-motion');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width: 1200px)');
  let selected = 'berkeley';
  let returnFocus = null;
  let motion = !reduced.matches;
  let dragStart = null;
  let dragged = false;
  let suppressClick = false;

  function selectPerson(id) {
    const person = data.find(person => person.id === id);
    if (!person) return;
    selected = id;
    selectors.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.selectPerson === id)));
    card.querySelector('h2').textContent = person.name[language];
    card.querySelector('.person-years').textContent = person.years;
    card.querySelector('.person-themes').textContent = person.themes.map(theme => theme[language]).join(' · ');
    card.querySelector('.person-source').href = person.portrait.sourceUrl;
    card.querySelector('[data-open-person]').setAttribute('aria-label', (english ? 'Read about ' : '阅读') + person.name[language] + (english ? '' : '的人物介绍'));
    document.querySelectorAll('[data-person-record]').forEach(record => { record.hidden = record.dataset.personRecord !== id; });
    dialog.setAttribute('aria-labelledby', 'person-title-' + id);
  }
  selectors.forEach(button => {
    button.addEventListener('click', () => {
      if (suppressClick) { suppressClick = false; return; }
      selectPerson(button.dataset.selectPerson);
    });
    button.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      const ids = data.map(person => person.id);
      const index = ids.indexOf(button.dataset.selectPerson);
      const next = ids[(index + (event.key === 'ArrowRight' ? 1 : -1) + ids.length) % ids.length];
      selectPerson(next);
      const container = button.closest('.atheneum-person-picker') || world;
      container.querySelector('[data-select-person="' + next + '"]').focus({ preventScroll: true });
    });
  });
  const closeButton = dialog.querySelector('[data-close-person]');
  card.querySelector('[data-open-person]').addEventListener('click', () => {
    returnFocus = document.activeElement;
    selectPerson(selected);
    if (typeof dialog.showModal === 'function') {
      dialog.showModal();
      document.body.classList.add('atheneum-dialog-open');
      closeButton.focus();
    } else {
      window.location.href = data.find(person => person.id === selected).sources[0].url;
    }
  });
  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('atheneum-dialog-open');
    if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
  });

  function resetView() {
    world.style.setProperty('--scene-x', '0px');
    world.style.setProperty('--scene-y', '0px');
  }
  function updateMotion() {
    const available = !reduced.matches && !compact.matches;
    motionButton.disabled = !available;
    motionButton.setAttribute('aria-pressed', String(motion && available));
    motionButton.textContent = !available ? (english ? 'Still view' : '静态视图') : motion ? (english ? 'Pause motion' : '暂停景深') : (english ? 'Enable motion' : '开启景深');
    scene.querySelector('.atheneum-hint').textContent = !available || !motion ? (english ? 'Choose a philosopher to explore' : '选择人物，走近他的思想') : (english ? 'Drag to look · Select a philosopher' : '拖动查看 · 点击人物');
    if (!motion || !available) resetView();
  }
  motionButton.addEventListener('click', () => { motion = !motion; updateMotion(); });
  reduced.addEventListener('change', () => { motion = !reduced.matches; updateMotion(); });
  compact.addEventListener('change', updateMotion);
  world.addEventListener('pointerdown', event => {
    if (!motion || reduced.matches || compact.matches || event.button !== 0) return;
    dragStart = { x: event.clientX, y: event.clientY, pointerId: event.pointerId };
    dragged = false;
    suppressClick = false;
  });
  world.addEventListener('pointermove', event => {
    if (!motion || reduced.matches || compact.matches) return;
    const bounds = world.getBoundingClientRect();
    if (dragStart && Math.hypot(event.clientX - dragStart.x, event.clientY - dragStart.y) > 6) dragged = true;
    const gain = dragStart ? 17 : 7;
    const x = (event.clientX - bounds.left) / bounds.width - .5;
    const y = (event.clientY - bounds.top) / bounds.height - .5;
    world.style.setProperty('--scene-x', (-x * gain).toFixed(2) + 'px');
    world.style.setProperty('--scene-y', (-y * gain * .65).toFixed(2) + 'px');
  });
  window.addEventListener('pointerup', () => {
    if (dragStart && dragged) {
      suppressClick = true;
      setTimeout(() => { suppressClick = false; }, 0);
    }
    dragStart = null;
  });
  world.addEventListener('pointercancel', () => { dragStart = null; resetView(); });
  world.addEventListener('pointerleave', () => { if (!dragStart) resetView(); });
  updateMotion();
  selectPerson(selected);
}());
