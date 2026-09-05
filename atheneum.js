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
  const hotspots = [...world.querySelectorAll('[data-select-person]')];
  const picker = scene.querySelector('.atheneum-person-picker');
  const chooser = scene.querySelector('.atheneum-chooser');
  const chooserToggle = chooser.querySelector('summary');
  const readerBody = dialog.querySelector('.atheneum-reader-body');
  const readerName = dialog.querySelector('[data-reader-name]');
  const readerCount = dialog.querySelector('[data-reader-count]');
  const readerSteps = [...dialog.querySelectorAll('[data-person-step]')];
  const ids = data.map(person => person.id);
  const motionButton = scene.querySelector('.atheneum-motion');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width: 1200px)');
  const smallScreen = matchMedia('(max-width: 680px)');
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
    const index = ids.indexOf(id);
    readerName.textContent = person.shortName[language];
    readerCount.textContent = english ? (index + 1) + ' / ' + data.length : '第 ' + (index + 1) + ' / ' + data.length + ' 位';
    readerSteps.forEach(button => {
      const step = Number(button.dataset.personStep);
      const next = data[(index + step + data.length) % data.length];
      button.setAttribute('aria-label', (step < 0 ? (english ? 'Previous philosopher: ' : '上一位：') : (english ? 'Next philosopher: ' : '下一位：')) + next.name[language]);
    });
  }
  function resetReaderScroll() {
    readerBody.scrollTop = 0;
    dialog.scrollTop = 0;
  }
  function openPerson(id, trigger) {
    if (!ids.includes(id)) return;
    chooser.open = false;
    returnFocus = trigger;
    selectPerson(id);
    if (typeof dialog.showModal === 'function') {
      if (!dialog.open) dialog.showModal();
      document.body.classList.add('atheneum-dialog-open');
      resetReaderScroll();
      closeButton.focus({ preventScroll: true });
    } else {
      window.location.href = data.find(person => person.id === id).sources[0].url;
    }
  }
  function focusReturnTarget(trigger) {
    if (!trigger || !trigger.isConnected) return;
    const hiddenHotspot = smallScreen.matches && hotspots.includes(trigger);
    const hiddenChoice = picker.contains(trigger) && !chooser.open;
    const target = hiddenHotspot || hiddenChoice
      ? chooserToggle
      : trigger;
    if (target) target.focus({ preventScroll: true });
  }
  function updateHotspotAccess() {
    // Move focus before hiding a hotspot from the accessibility tree. When a
    // reader is open, leave its focus alone; the close handler resolves the
    // original hotspot to the visible chooser at the current viewport.
    if (smallScreen.matches && hotspots.includes(document.activeElement)) {
      focusReturnTarget(document.activeElement);
    }
    hotspots.forEach(button => {
      if (smallScreen.matches) {
        button.setAttribute('tabindex', '-1');
        button.setAttribute('aria-hidden', 'true');
      } else {
        button.removeAttribute('tabindex');
        button.removeAttribute('aria-hidden');
      }
    });
  }
  selectors.forEach(button => {
    button.addEventListener('click', () => {
      if (suppressClick) { suppressClick = false; return; }
      if (hotspots.includes(button)) openPerson(button.dataset.selectPerson, button);
      else {
        selectPerson(button.dataset.selectPerson);
        chooser.open = false;
        chooserToggle.focus({ preventScroll: true });
      }
    });
    button.addEventListener('keydown', event => {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
      event.preventDefault();
      const index = ids.indexOf(button.dataset.selectPerson);
      const next = ids[(index + (event.key === 'ArrowRight' ? 1 : -1) + ids.length) % ids.length];
      selectPerson(next);
      const container = button.closest('.atheneum-person-picker') || world;
      // A long directory scrolls its focused choice into view; scene hotspots
      // keep the hall still when moving between figures with the arrow keys.
      container.querySelector('[data-select-person="' + next + '"]').focus({ preventScroll: container === world });
    });
  });
  chooser.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !chooser.open) return;
    event.preventDefault();
    chooser.open = false;
    chooserToggle.focus({ preventScroll: true });
  });
  chooser.addEventListener('focusout', event => {
    if (event.relatedTarget && !chooser.contains(event.relatedTarget)) chooser.open = false;
  });
  document.addEventListener('click', event => {
    if (!chooser.open || chooser.contains(event.target)) return;
    const focusWasInPicker = picker.contains(document.activeElement);
    chooser.open = false;
    if (focusWasInPicker) chooserToggle.focus({ preventScroll: true });
  });
  const closeButton = dialog.querySelector('[data-close-person]');
  card.querySelector('[data-open-person]').addEventListener('click', event => {
    openPerson(selected, event.currentTarget);
  });
  readerSteps.forEach(button => {
    button.addEventListener('click', () => {
      const index = ids.indexOf(selected);
      const step = Number(button.dataset.personStep);
      selectPerson(ids[(index + step + ids.length) % ids.length]);
      resetReaderScroll();
      button.focus({ preventScroll: true });
    });
  });
  closeButton.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('atheneum-dialog-open');
    focusReturnTarget(returnFocus);
    returnFocus = null;
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
    scene.querySelector('.atheneum-hint').textContent = english ? 'Choose a philosopher to explore their ideas' : '选择人物，走近他的思想';
    if (!motion || !available) resetView();
  }
  motionButton.addEventListener('click', () => { motion = !motion; updateMotion(); });
  reduced.addEventListener('change', () => { motion = !reduced.matches; updateMotion(); });
  compact.addEventListener('change', updateMotion);
  smallScreen.addEventListener('change', updateHotspotAccess);
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
  updateHotspotAccess();
  selectPerson(selected);
}());
