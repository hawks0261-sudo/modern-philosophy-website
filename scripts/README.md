# 静态站点维护

网站继续直接发布静态 HTML，不需要前端框架、服务器端程序或在线数据库。生成和检查只使用 Python 3.9 及以上的标准库；图片转码是单独的准备步骤，日常检查读取已经保存的图片和映射。

```sh
python3 scripts/build_site.py --all
python3 scripts/test_build.py
python3 scripts/build_site.py --check
python3 scripts/check_site.py
```

`--check` 只计算并比较预期结果；输出 `changed: []` 表示提交中的生成文件与数据一致。检查不上传、不提交、不部署；检查成功后仍应在浏览器看桌面、手机、键盘和无 JavaScript 页面。GitHub Actions 执行相同的三项检查，并只有仓库读取权限；它不发布网站。

## 修改入口

- `data/books.json`：本站收录的 29 册译丛图书的字段。原目录人名与责任方式中四册有确证更正，见 `data/book-corrections.json`；只对 08/09 两册登记编者。修改一次，生成器同步书目卡片、快速预览数据、每册书的独立详情页和 Book 元数据。`date` 保留原排序值；公开 `<time>` 和 `datePublished` 只使用资料实际显示的月份，不能把原有每月 `01` 解释为确切出版日。
- `data/books-en.json`：按相同 ID 维护 29 册英文标题、完整简介与作者显示名，生成 `en/publications/translation-series/index.html` 和 29 册英文详情；目录与每册中英文页互相直达。个别书名为网站译名，页面并列中文题名；出版时间、译者和 Book 结构化数据始终指中文版本，不表示另有英文版图书。作者外文署名须有来源，未知拼写保留中文。`sourceDescriptionSha256` 是对应中文简介的 UTF-8 SHA-256；中文简介更改后构建会报错，应先审核并更新英文翻译，再重新记录指纹，不能只为通过检查而改指纹。系列名依据现有海报使用 **Western Thought & Culture Library**。
- `data/events.json`：11 场既往活动的日期、标题、摘要、海报、详情地址与来源。修改一次，同步首页最新三场、中文活动归档、年份筛选和各活动的日期元数据。完整报告正文仍由对应详情 HTML 维护，英文正文也需按原始报告翻译审核；不能由摘要反推或自动扩写报告。
- `data/people.json`：现任国际顾问姓名、原文姓名、任职机构所在国与来源，以及单列的纪念顾问。首页 `data-stat` 统计由此计算。现职、身份和成员分类仍以成员详情页及可靠来源核验，不从国家字段推断国籍。维护名单时同时更新成员页；检查器会检查当前顾问是否出现在该页现任区。
- `data/site.json`：已验证的站点基址、双语主导航、真实中英页面对应关系、无全文对应时的概览入口。`language_pairs` 生成互相对应的 `hreflang`；`language_fallbacks` 只生成可用的语言入口，明确标为概览，不会向搜索引擎宣称两个页面等价。
- `data/journal-issue-01.json`：依据第一期现有目录核验的分组、起始页码、篇名、作者与译者。`scripts/journal_content.py` 同步中文完整目录和英文目录；链接定位的是 HTML 目录条目，不假装定位到文章 PDF。
- `data/media.json` 与 `scripts/page_assets.py`：图片变体、原尺寸及最终 HTML 规范化。由图片准备工具维护；构建最后调用 `normalize_page(text, relative)`。

页面中 `BEGIN GENERATED` / `END GENERATED` 之间的区域由数据生成，应修改数据或生成模板；其他正文和局部样式仍可直接编辑。主导航、语言链接、元数据和 `sitemap.xml` 在构建时统一输出。独立图书详情页整体由生成器维护，直接修改会被下次构建覆盖。

## 全站主题与标识

`atheneum-brand.css` 覆盖当前全部 93 个 HTML 页面，统一页头、导航和 Logo 的呈现；`atheneum-pages.css` 覆盖其中 91 个二级页，统一深棕标题区、浅纸色正文和栏目分隔。两份中英文首页保留七人殿堂主题，不添加二级页的 `atheneum-page` 类。

`scripts/site_theme.py` 的 `normalize_theme(text, path)` 在 `build_site.py` 构建末尾、`metadata()` 后及 `normalize_page()` 前执行，`--books-only` 同样生效。它使用各页相对路径，将主题样式放在已有样式之后，并为二级页幂等添加 body 类。新增页面会随构建挂载主题，无需逐页手写链接。

`assets/brand/logo-original.svg` 原样保留项目原矢量文件 `/Users/hawksky/Desktop/modern phi/logo-header`；`logo-heritage.svg` 只将其中两条路径的填充色改为古金色 `#d4b476`，沿用原有盾徽、书页、羽毛笔和拉丁文路径。原 `logo.png` 继续保留，favicon 和分享元数据仍使用原资源；具体出处与校验见[品牌素材说明](../assets/brand/README.md)。构建时会同时更新页面 Logo 的 `src` 与 `data-media-source`，清除旧的 `srcset`、`sizes`，防止图片规范化重新引用旧 PNG 的变体。

## 思想殿堂首页

`scripts/atheneum_home.py` 生成中英文首页的 `atheneum-scene` 和 `atheneum-featured` 区域。当前 v3 场景包括笛卡尔、斯宾诺莎、莱布尼茨、康德、洛克、贝克莱与休谟七人，使用 `assets/atheneum/hero-scene-v3.png`（1747 × 900）；七人 v2 原图 `hero-scene-v2.png` 和最初三人场景 `hero-scene.png` 均保留，供比较与追溯。v3 参考 `portrait-berkeley.jpg`，通过 ImageGen 局部调整贝克莱的脸型、侧转和鼻口；其余人物位置与整体构图未明显改变，部分细节有轻微重绘。

场景人物仍是依据历史肖像创作的艺术形象，并非精确复原；详情中另行展示原肖像及归属说明。原肖像与出处见[素材说明](../assets/atheneum/README.md)。当前网页变体为 `9d6b3c23a6a7-384/768/1440.webp`，最大一幅为 1440 × 742、205,916 字节；旧 v2 变体保留。图片路径与尺寸以 `data/media.json` 为准，构建时统一规范化。

`data/atheneum.json` 的 `philosophers` 数组维护人物内容。`id` 需唯一且稳定；`name`、`shortName`、`bio`、每个 `themes` 项及著作标题分别维护 `zh`、`en`。`portrait` 中的 `image`、`sourceUrl`、双语 `sourceLabel`、`caption`、`attributionNote` 保留肖像路径和准确出处；`sources` 登记人物及著作资料，当前第一项为对应的斯坦福哲学百科条目。`relatedLinks` 只填真实本站内容，没有相关记录时用空数组；英文链接 `hrefEn` 缺省时使用中文 `href` 并在英文页面标注 `(Chinese)`。

数组顺序同步决定人物选择按钮、详情记录与前端状态的顺序，也决定弹窗上一位／下一位的循环顺序；人数与当前序号从数组读取。新增人物需要补齐双语字段、来源与原肖像，并准备对应的场景人物和 `.atheneum-figure--{id}` 热点位置；只追加数据不会自动在画面中生成新人物。更换场景时同时检查图像宽高比、替代文字和全部热点的实际位置。当前默认选择贝克莱；如需更改或移除他，须同步调整生成模板中的默认卡片、选中状态和弹窗初始 `aria-labelledby`、`atheneum.js` 中的 `selected`，并更新回归测试。

`works[].year` 表示页面显示的作品年代。需要区分写成年份、首刊年份或书名页年份时，可增加双语 `works[].dateNote`，例如：

```json
{
  "zh": "单子论",
  "en": "Monadology",
  "year": "1714",
  "dateNote": {
    "zh": "1714年写成；不是首刊年份。",
    "en": "Composed in 1714; not the date of first publication."
  }
}
```

生成器只在当前语言有非空说明时输出日期注释，并按普通文本转义；没有说明的著作可以省略整个 `dateNote`。新增需要解释的年代时应同时审核中英文，不把手稿写成日期直接当作出版日期。

首页样式按 `site.css` → `atheneum.css` → `atheneum-scene.css` → `atheneum-sections.css` → `atheneum-brand.css` 加载；最后一份维护全站品牌，三份首页专用样式职责如下：

- `atheneum.css`：殿堂首页的基础配色、字体、页头、通用按钮和人物详情弹窗；后两份文件覆盖其中早期的场景与栏目布局。
- `atheneum-scene.css`：v3 场景宽高比（1747 / 900）、七个人物热点与名牌、画面下方的人物选择栏及摘要卡、连续阅读弹窗工具条与正文、著作日期注释和响应式布局。宽度不超过 1200 px 时保持完整画面，标题移至画面上方，关闭景深变换。
- `atheneum-sections.css`：画面下方的三栏精选内容及其余首页栏目，统一章节分隔、纸面底色、标题层级和中英阅读宽度；中文 `#people-preview` 与英文 `#people` 的成员栏目采用暖米褐色 `#e4d4b8`，延续旧书纸色。活动照片与真实书封保留原有颜色，纸纹加载失败时仍有纯色底。

`atheneum.js` 按人物数据和 `data-select-person` 处理鼠标与键盘选择、原生详情弹窗、焦点返回和景深开关，并遵循减弱动态偏好。这是平面场景的轻微视差效果，并非独立人物模型或可翻页立体书。人物阅读流程须保持如下约定：

- 图中热区点击或使用原生按钮的 Enter／空格激活后，直接打开对应人物资料；热区的 `aria-haspopup="dialog"`、`aria-controls="atheneum-detail"` 及“阅读人物介绍”名称应与动作一致。画面下方人名选择器的点击和左右方向键仅预览摘要，使用“阅读人物介绍”按钮再进入弹窗。
- 弹窗工具条内的 `.atheneum-reader-nav` 包含 `data-person-step="-1"`／`"1"` 按钮，以及 `.atheneum-reader-position` 中的短姓名与当前位置。前端状态需保留双语 `shortName`。切换人物时同步资料记录、弹窗标题、摘要和画面选中态，将 `.atheneum-reader-body` 与弹窗滚动位置归零，并把焦点留在所用导航按钮；连续阅读不应重新记录最初的打开入口。
- 关闭按钮、Esc 和点击弹窗外背景均沿用原生弹窗关闭流程，关闭后回到最初触发元素。若该入口为图中热区且当前宽度不超过 680 px，则回到同一人物的可见人名按钮。点击弹窗正文、工具条或内部留白不应关闭。
- 宽度不超过 680 px 时，图中热区设置 `tabindex="-1"` 与 `aria-hidden="true"`，保留指针点击，但不再作为键盘或辅助技术入口；可见人名选择器提供替代入口。恢复桌面宽度时移除这两个属性。缩至小屏时若焦点正在热区上，应先移至对应人名按钮；若焦点在打开的弹窗内，应保持其位置，直到关闭时再解析返回目标。
- 场景工具区的 `.atheneum-content-link` 是原生 `href="#atheneum-content"` 锚点，显示“浏览中心内容”／“Explore the center”，直接进入场景下方内容，不依赖人物弹窗或新增路由。

现有回归测试覆盖全部人物的按钮、记录、肖像引用与可访问名称关联，以及双语日期注释的传递和文本转义；视觉、热点位置和键盘实际操作仍需浏览器验收。交互修改后重点检查直接打开、连续切人后的回顶、三种关闭方式、原入口焦点恢复，以及弹窗打开和关闭时跨越 680 px 断点的行为。

首页三栏的首列标题为“活动速览”／“Recent activities”，展示最近三条活动；它与下方完整学术活动栏目、其中的中心动态分开命名，修改生成模板时保留这一区别。首页图书数量直接取 `books.json` 的记录数；精选书封目前采用 25、27、29 三册，其链接的替代文字从中英文书目标题读取，不在模板另写书名。调整精选书目时修改模板中的 ID，封面仍取书目记录的 `cover` 字段。英文最新活动使用对应英文详情页的 `<h1>`，因此审核并更新英文活动页标题后，重新构建即可同步首页；尚无英文标题时保留中文标题并标注 `(Chinese)`、`lang` 与 `hreflang`，不自动生成未经审核的英文标题。新增回归测试覆盖数量变化、双语书名、英文标题同步和中文活动回退。

新增活动时先准备真实详情页、日期与海报，再向 `events.json` 加入记录。首页按 `startDate` 倒序选前三条；归档年份、筛选与空状态随数据更新。新增或调整年份无需再改共享 CSS 中的历史筛选规则。新增英文对应页面后再加入 `language_pairs`，不要把尚无对应正文的英文概览登记为全文翻译。

## 搜索、分享与部署边界

每个页面有独立标题、从可见内容提取的描述、canonical、Open Graph 与 Twitter 分享标签。首页有 Organization，详情页有 Breadcrumb，译丛详情有 Book，已记录的历史活动有 Event。没有来源的字段不填；本次没有虚构 ISBN、报价、评分、地址、活动具体时刻或正式项目状态。结构化数据可被解析并不保证搜索富结果资格。

`data/site.json` 当前基址为 `https://hawks0261-sudo.github.io/modern-philosophy-website/`。将来绑定正式域名时改此处，再构建、核验重定向与线上结果。项目子路径下的 `robots.txt` 不控制整个 `hawks0261-sudo.github.io` 来源根目录，因此本次不创建一个无效的子目录爬虫规则文件。站点地图与 canonical 的存在也不能证明已经被收录。

`check_site.py` 检查本地链接、资源、锚点、唯一标题、语言、主标题和主内容区域、静态导航、元数据、双语对应关系、JSON 数据和站点地图，不检查外部个人主页的当前可达性，也不替代内容来源审核。

GitHub Action 固定为官方 `actions/checkout` v7.0.1 的提交，关闭凭据持久化；版本依据：[官方仓库](https://github.com/actions/checkout)。
