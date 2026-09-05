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

新增活动时先准备真实详情页、日期与海报，再向 `events.json` 加入记录。首页按 `startDate` 倒序选前三条；归档年份、筛选与空状态随数据更新。新增或调整年份无需再改共享 CSS 中的历史筛选规则。新增英文对应页面后再加入 `language_pairs`，不要把尚无对应正文的英文概览登记为全文翻译。

## 搜索、分享与部署边界

每个页面有独立标题、从可见内容提取的描述、canonical、Open Graph 与 Twitter 分享标签。首页有 Organization，详情页有 Breadcrumb，译丛详情有 Book，已记录的历史活动有 Event。没有来源的字段不填；本次没有虚构 ISBN、报价、评分、地址、活动具体时刻或正式项目状态。结构化数据可被解析并不保证搜索富结果资格。

`data/site.json` 当前基址为 `https://hawks0261-sudo.github.io/modern-philosophy-website/`。将来绑定正式域名时改此处，再构建、核验重定向与线上结果。项目子路径下的 `robots.txt` 不控制整个 `hawks0261-sudo.github.io` 来源根目录，因此本次不创建一个无效的子目录爬虫规则文件。站点地图与 canonical 的存在也不能证明已经被收录。

`check_site.py` 检查本地链接、资源、锚点、唯一标题、语言、主标题和主内容区域、静态导航、元数据、双语对应关系、JSON 数据和站点地图，不检查外部个人主页的当前可达性，也不替代内容来源审核。

GitHub Action 固定为官方 `actions/checkout` v7.0.1 的提交，关闭凭据持久化；版本依据：[官方仓库](https://github.com/actions/checkout)。
