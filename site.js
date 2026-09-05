/* ============================================================
   site.js — 全站共享导航 + 移动端汉堡菜单
   导航/语言数据：data/site.json；生成：scripts/build_site.py
   每个页面 <html> 需设置 data-root（相对站点根的前缀）
   例：根目录 ""，activities/ 用 "../"，
       activities/lecture-01/ 用 "../../"，
       people/member-directory/li-daiwei/ 用 "../../../"
   首页另设 data-current="home"
   ============================================================ */
(function () {
  var rootEl = document.documentElement;
  var root = rootEl.getAttribute("data-root") || "";
  var isHome = rootEl.getAttribute("data-current") === "home";
  var isEnglish = rootEl.lang.indexOf("en") === 0;
  var path = location.pathname;

  // Navigation and language destinations are generated as HTML by scripts/build_site.py.
  // JavaScript enhances interactions; links remain readable without it.
  function languageLinks() {
    var source = document.querySelector('.header-right .lang-toggle');
    return source ? source.innerHTML : '';
  }
  var primaryNav = document.querySelector('[data-primary-nav]');
  var mobileNav = document.querySelector('[data-mobile-nav]');
  if (primaryNav && mobileNav && !mobileNav.querySelector('a[href]')) {
    mobileNav.innerHTML = primaryNav.innerHTML;
  }

  // —— 移动菜单置于原生模态层：背景不可交互，闭合后不进入 Tab 顺序 ——
  var toggle = document.querySelector(".nav-toggle");
  var backdrop = document.querySelector(".mobile-nav-backdrop");
  var drawer = document.querySelector(".mobile-nav");
  if (toggle && drawer) {
    var dialog = document.createElement('dialog');
    if (typeof dialog.showModal !== 'function') return;
    document.documentElement.classList.add('nav-enhanced');
    dialog.id = 'mobile-nav-dialog';
    dialog.className = 'mobile-nav-dialog';
    dialog.setAttribute('aria-labelledby', 'mobile-nav-title');
    var toolbar = document.createElement('div');
    toolbar.className = 'mobile-nav-toolbar';
    toolbar.innerHTML = '<strong id="mobile-nav-title">' + (isEnglish ? 'Navigation' : '网站导航') +
      '</strong><button type="button" class="mobile-nav-close" autofocus>' +
      (isEnglish ? 'Close ×' : '关闭 ×') + '</button>';
    var mobileLanguage = document.createElement('div');
    mobileLanguage.className = 'lang-toggle mobile-language';
    mobileLanguage.setAttribute('aria-label', isEnglish ? 'Page language' : '页面语言');
    mobileLanguage.innerHTML = languageLinks();
    drawer.parentNode.insertBefore(dialog, drawer);
    dialog.appendChild(toolbar);
    dialog.appendChild(drawer);
    drawer.appendChild(mobileLanguage);
    if (backdrop) backdrop.remove();
    toggle.setAttribute('aria-controls', dialog.id);
    toggle.setAttribute('aria-haspopup', 'dialog');
    toggle.setAttribute('aria-label', isEnglish ? 'Open navigation menu' : '打开导航菜单');
    var closeButton = toolbar.querySelector('button');
    var oldOverflow = '';
    var scrollLocked = false;
    var returnFocus = true;
    var mobileViewport = window.matchMedia('(max-width: 1024px)');

    function closeNav(restoreFocus) {
      if (!dialog.open) return;
      returnFocus = restoreFocus !== false;
      dialog.close();
      restoreNav();
    }
    function openNav() {
      if (!mobileViewport.matches || dialog.open) return;
      oldOverflow = document.body.style.overflow;
      scrollLocked = true;
      returnFocus = true;
      dialog.showModal();
      document.body.classList.add('nav-open');
      document.body.style.overflow = 'hidden';
      toggle.setAttribute('aria-expanded', 'true');
      closeButton.focus();
    }
    function restoreNav() {
      if (dialog.open || !scrollLocked) return;
      scrollLocked = false;
      document.body.classList.remove('nav-open');
      document.body.style.overflow = oldOverflow;
      toggle.setAttribute('aria-expanded', 'false');
      if (returnFocus && mobileViewport.matches) toggle.focus({ preventScroll: true });
    }
    dialog.addEventListener('close', restoreNav);
    closeButton.addEventListener('click', function () { closeNav(); });
    dialog.addEventListener('cancel', function (event) {
      event.preventDefault();
      closeNav();
    });
    // ::backdrop is outside the right-hand panel but dispatches clicks to the dialog.
    dialog.addEventListener('click', function (event) {
      if (event.target !== dialog) return;
      var bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right ||
          event.clientY < bounds.top || event.clientY > bounds.bottom) closeNav();
    });
    dialog.addEventListener('keydown', function (event) {
      if (event.key !== 'Tab') return;
      var controls = Array.from(dialog.querySelectorAll('a[href], button:not([disabled])'));
      var first = controls[0];
      var last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    });
    drawer.addEventListener('click', function (event) {
      if (event.target.closest('a[href]')) closeNav(false);
    });
    mobileViewport.addEventListener('change', function (event) {
      if (!event.matches && dialog.open) {
        closeNav(false);
        document.querySelector('.brand').focus({ preventScroll: true });
      }
    });
    toggle.addEventListener("click", function () {
      dialog.open ? closeNav() : openNav();
    });
  }
})();
