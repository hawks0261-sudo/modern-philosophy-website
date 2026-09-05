# 全站古籍主题与原标识融合验收 · 2026-09-05

final result: passed

## 结果

93 个中英文页面统一采用深棕页头、古金矢量 Logo 和相同的导航样式；其中 91 个二级页面接入暖纸背景、宋体 / Georgia 标题、方形阅读面板与双线章节分隔。首页继续保留七人思想殿堂及原交互。二级页采用适合阅读正文、活动资料和书目信息的布局。

`atheneum-brand.css` 管理全站页头，`atheneum-pages.css` 仅作用于 `body.atheneum-page`。`scripts/site_theme.py` 在构建末尾、图片归一化之前接入主题；新页面、全量重建、books-only 都继承主题，链接置于旧内嵌样式之后。

Logo 来自 `/Users/hawksky/Desktop/modern phi/logo-header` 原始 SVG。`assets/brand/logo-original.svg` 保留原件，`logo-heritage.svg` 仅把两个 fill 改为 #d4b476，盾徽、书本、羽毛笔、拉丁文路径及 viewBox 不变。清晰呈现原图的金色实底与透明镂空；页头无蓝底、边框或图片滤色。原 SVG 不含 PNG 底部的小型中文字符，中心中文名称由旁边的文字标识完整呈现。原 logo.png、favicon 和分享图片保留。

本轮仅保存本地工作树与预览，没有部署或更新 Figma。

## 对照依据

输出目录：`/Users/hawksky/Desktop/modern phi/output/atheneum-site-theme-20260905/`。

- 同尺寸 1448 × 1086、页面顶部：before-activities / after-activities、before-books / after-books、before-people / after-people、before-event-detail / after-event-detail、before-journal / after-journal，均为 PNG，已在同一次工具输入中分别并置查看。
- 首页：上一轮 `../atheneum-reading-20260905/desktop-home.png` 与本轮 `desktop-home.png` 并置。最终比较为相同 1448 × 1086、scrollY=0、休谟选中、资料关闭。早一次点击选择器引发滚动的截图未作为最终对照；回到 #top 后覆盖保存。
- 英文桌面代表页：desktop-en-activities.png、desktop-en-event.png、desktop-en-publications.png、desktop-en-book.png。
- 手机 390 × 844：mobile-activities.png、mobile-menu.png、mobile-en-activities.png、mobile-en-book.png、mobile-home.png、mobile-home-en.png、mobile-journal-anchor.png。
- 图书弹窗：book-modal-desktop.png 为 1448 × 1086；book-modal-landscape.png 为 667 × 375。真实封面保留比例和原色，关闭按钮在浅封面边缘仍清楚可见。
- 额外现场查看 320 × 740 英文长书名和 Logo；1025 × 800 桌面导航与 1024 × 800 移动菜单临界状态。
- 截图直接来自当前浏览器，未重绘图片。最初个别已打开页面命中旧缓存；全部最终对照均刷新后核对 body class、新 Logo 与主题颜色。

## 发现与修复

| 优先级 | 问题 | 本轮修改 | 验证 |
| --- | --- | --- | --- |
| P1 | 91 个二级页沿用旧蓝白配色，与首页割裂 | 添加统一二级主题，覆盖活动、成员、出版总览、图书及期刊 | 9 种代表页面实际截图，93 页静态覆盖检查 |
| P2 | 蓝底 Logo 在深棕页头显得独立、缩放清晰度有限 | 使用原始路径的古金 SVG，统一尺寸、间距与中英文字标识 | 桌面与 390 / 320 手机实际查看，图片成功加载 |
| P2 | 英文书目内嵌样式可能盖过共用主题 | 构建把新 CSS 放在 head 最后；补足按钮文字及书目 muted 变量 | 英文长书名、正文、面包屑、按钮在桌面和窄屏可读 |
| P2 | 旧圆角胶囊、面板线条和章节边界不协调 | 方形页签、暖纸面板、双线章节边界与深浅分区 | 活动、成员、译丛和期刊前后并置 |
| P2 | 多行期刊条目链接仅文字行可点，中间行距点击不到 | 目录标题链接改为 block，至少 44px 高 | 原中心点击命中 h3；修改后相同点击进入 #page-015、距视口顶120px并高亮 |

## 五项视觉检查

- **排版**：中文标题使用宋体，英文使用 Georgia；正文维持清楚的阅读字号与行距。390px 和320px长英文书名正常换行。页头标识与菜单不重叠。
- **间距与层次**：深棕标题区与浅纸阅读区明显分开；章节双线、面板边框与元数据横线各有层级。正文区纸纹较弱，长文阅读未被背景干扰。
- **颜色与状态**：筛选选中为深棕浅字，未选中为浅纸深字；按钮与当前导航保持可辨识。文字对比度代表样本为5.77–12.09。深色页头焦点用浅金色，浅纸区域焦点用深棕色。
- **图像**：全部活动海报、人物照片和真实图书封面保持原色与比例；没有生成新面貌或替换原有内容图。原 Logo 矢量形状不变。
- **内容**：学术正文和书目不在本轮改写范围；导航目标、语言链接、SEO与原分享图保持。新增页面继承样式而非手工逐页改色。

## 交互与技术检查

- 中文活动组合筛选：讲座 + 2026 正确显示空状态，恢复全部正常；选中颜色为 rgb(67,46,29) / rgb(246,235,213)。
- 390px 菜单打开、Escape 关闭、中文活动切到英文活动成功；英文活动的报告入口正常。
- 1025px 显示五项桌面导航且无横向溢出；1024px 移动菜单可打开。
- 图书快速预览正常打开；Escape 关闭后焦点回原预览按钮。667px横屏关闭按钮为44×44、深棕底浅字。
- 期刊完整目录、直接深链接、键盘 Enter 与鼠标点击条目正常；目标高亮及标题不被固定页头遮挡。最后新增 block 点击区域后重新查看手机与桌面目录。
- 93 页主题覆盖、Logo 路径、重建幂等、books-only 的14项生成测试通过（子代理执行）。
- build_site.py --check：94 outputs，changed=[]。
- check_site.py：93 pages，4019 localReferences，93 jsonLdPages，errors=[]，warnings=[]。
- 全部实际查看尺寸无横向溢出；浏览器 error / warn 日志为空。
- git diff --check 通过。

当前预览：http://127.0.0.1:62027/index.html。上一轮验收已归档为本输出目录的 previous-design-qa.md。
