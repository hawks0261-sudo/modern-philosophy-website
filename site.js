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

  function resolve(href) {
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

  // —— 汉堡菜单开关 ——
  var toggle = document.querySelector(".nav-toggle");
  var backdrop = document.querySelector(".mobile-nav-backdrop");
  var drawer = document.querySelector(".mobile-nav");

  function closeNav() {
    document.body.classList.remove("nav-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }
  function openNav() {
    document.body.classList.add("nav-open");
    if (toggle) toggle.setAttribute("aria-expanded", "true");
  }
  if (toggle) {
    toggle.addEventListener("click", function () {
      document.body.classList.contains("nav-open") ? closeNav() : openNav();
    });
  }
  if (backdrop) backdrop.addEventListener("click", closeNav);
  if (drawer) {
    drawer.addEventListener("click", function (e) {
      if (e.target.tagName === "A") closeNav();
    });
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeNav();
  });

  // —— 语言切换占位（英文版暂不动）——
  // 若页面未自带 setLang（如各子页），提供一个仅切换高亮的安全占位
  if (typeof window.setLang !== "function") {
    window.setLang = function (l) {
      document.querySelectorAll(".lang-toggle button").forEach(function (b) {
        b.classList.remove("active");
      });
      var btn = document.querySelector(
        '.lang-toggle button[onclick="setLang(\'' + l + "')\"]"
      );
      if (btn) btn.classList.add("active");
    };
  }
})();
