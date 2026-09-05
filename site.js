/* ============================================================
   site.js — 全站共享导航 + 移动端汉堡菜单
   单一来源：以后改导航项只改这里
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

  // —— 唯一一套导航 ——
  var NAV = [
    { label: "首页", href: "index.html", key: "home" },
    { label: "中心简介", href: "index.html#about", key: "about" },
    { label: "研究方向", href: "index.html#research", key: "research" },
    { label: "学术活动", href: "activities/index.html", key: "activities", match: "/activities/" },
    { label: "中心成员", href: "people/index.html", key: "people", match: "/people/" },
    { label: "研究成果", href: "index.html#outcomes", key: "outcomes", match: "/publications/" },
    { label: "中心动态", href: "index.html#news", key: "news" },
    { label: "联系我们", href: "index.html#contact", key: "contact" }
  ];
  if (isEnglish) {
    NAV = [
      { label: "Home", href: "#top", key: "home" },
      { label: "About", href: "#about", key: "about" },
      { label: "Research", href: "#research", key: "research" },
      { label: "Activities", href: "#activities", key: "activities" },
      { label: "People", href: "#people", key: "people" },
      { label: "Publications", href: "#publications", key: "outcomes" },
      { label: "Contact", href: "#contact", key: "contact" }
    ];
  }

  function resolve(href) {
    if (isEnglish) return href;
    // 首页内部锚点：把 index.html#x 变成 #x，平滑滚动
    if (isHome && href.indexOf("index.html") === 0) {
      var hash = href.slice("index.html".length);
      return hash || "#top";
    }
    return root + href;
  }

  function isCurrent(item) {
    return item.match ? path.indexOf(item.match) !== -1 : false;
  }

  var linksHtml = NAV.map(function (it) {
    return (
      '<a href="' + resolve(it.href) + '"' +
      (it.key ? ' data-nav="' + it.key + '"' : "") +
      (isCurrent(it) ? ' class="is-current"' : "") +
      ">" + it.label + "</a>"
    );
  }).join("");

  document.querySelectorAll("[data-primary-nav]").forEach(function (el) {
    el.innerHTML = linksHtml;
  });
  document.querySelectorAll("[data-mobile-nav]").forEach(function (el) {
    el.innerHTML = linksHtml;
  });

  // —— 语言入口：英文概览有独立 URL，不再只切换标题或按钮高亮 ——
  function languageLinks() {
    return '<a href="' + (isEnglish ? root + 'index.html' : location.href) +
      '" lang="zh-CN" hreflang="zh-CN"' + (!isEnglish ? ' class="active" aria-current="page"' : '') +
      '>中文</a><a href="' + root + 'en/index.html" lang="en" hreflang="en" ' +
      'aria-label="English overview" title="English overview"' +
      (isEnglish ? ' class="active" aria-current="page"' : '') + '>EN</a>';
  }
  document.querySelectorAll('.lang-toggle').forEach(function (el) {
    el.setAttribute('aria-label', isEnglish ? 'Page language' : '页面语言');
    el.innerHTML = languageLinks();
  });

  // —— 移动菜单置于原生模态层：背景不可交互，闭合后不进入 Tab 顺序 ——
  var toggle = document.querySelector(".nav-toggle");
  var backdrop = document.querySelector(".mobile-nav-backdrop");
  var drawer = document.querySelector(".mobile-nav");
  if (toggle && drawer) {
    var dialog = document.createElement('dialog');
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
    var returnFocus = true;
    var mobileViewport = window.matchMedia('(max-width: 1024px)');

    function closeNav(restoreFocus) {
      if (!dialog.open) return;
      returnFocus = restoreFocus !== false;
      dialog.close();
    }
    function openNav() {
      if (!mobileViewport.matches || dialog.open) return;
      oldOverflow = document.body.style.overflow;
      returnFocus = true;
      dialog.showModal();
      document.body.classList.add('nav-open');
      document.body.style.overflow = 'hidden';
      toggle.setAttribute('aria-expanded', 'true');
      closeButton.focus();
    }
    dialog.addEventListener('close', function () {
      document.body.classList.remove('nav-open');
      document.body.style.overflow = oldOverflow;
      toggle.setAttribute('aria-expanded', 'false');
      if (returnFocus && mobileViewport.matches) toggle.focus({ preventScroll: true });
    });
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
