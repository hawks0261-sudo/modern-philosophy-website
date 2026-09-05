# 贝克莱高清头像与场景融合 · 2026-09-05

final result: passed for this visual iteration

## 当前结果

首页保留 `hero-scene-v4.png` 背景，新增 `berkeley-head-v1.png` 高清头像与 `berkeley-head-mask.svg` 轮廓遮罩。额头与眉眼位置、眼睑、鼻唇关系和下颊体积更接近历史肖像，避免整幅重绘时再次泛化五官。中文和英文共用同一图层。头部大小与身体协调，头颈衔接自然；其他六人、身体、家具和建筑继续使用原v4背景，其源文件未改动。

人物仍是依据原肖像创作的艺术形象。新脸的眉毛、眼睛与嘴唇比原画更清晰，材质稍细致、肤色稍中性；放大后可见这种差别，不声称精确复原。

## 图像与实现

- 内置ImageGen先以原肖像生成1254×1254头像母版，再试自动回融。回融结果丢失部分脸型和身份特征，没有接入，也没有继续整幅生成。
- 头像输出为RGB，棋盘格已烘焙，并非真正透明。浏览器使用SVG轮廓的luminance mask去掉背景，生成头像文件本身未改动。早期帽檐白线及下颌边缘经放大检查后收紧；最终对照无明显棋盘格、白边、双头或额头遮挡。
- 头像与背景共用`.atheneum-world`：left67.25%、top37%、width5.6%，brightness(.95)、saturate(.88)。不支持mask/luminance时隐藏头像，保留完整v4背景。
- 装饰图层空alt、aria-hidden=true、pointer-events=none；不增加读屏内容或拦截原人物热点。加载策略为eager、sizes=5.6vw，首选384pxWebP仅15,236字节。
- 根代理与独立代理都比较了原肖像、v4、高清母版、未采用回融及最终网页组合，确认独立图层比整图回融更有效地保留面貌特征。

## 对照档案

目录：`/Users/hawksky/Desktop/modern phi/output/atheneum-berkeley-likeness-20260905/`。

- `portrait-comparison.html` / `portrait-comparison.png`：原肖像、上一版、当前网页图层并列放大。右侧采用与网页一致的原图、遮罩、位置和滤镜，并非另画的效果稿；最终1060×570视口。
- `home-before.png` / `home-after.png`：顶部、贝克莱选中、资料关闭，按1448×1086视口对比并在同一次工具输入中查看；后期系统滚动条占用少量横向宽度，因此局部头像比较以专门对照板为准。
- `home-tablet.png`：750×746；`home-mobile-en.png`：390×844英文首页。头像和身体保持对齐。
- `imagegen-prompts.txt`：两次工具提示词、输入角色、源图与最终路径、RGB与遮罩限制。
- `berkeley-head-reference.png`：未改动的高清母版副本。
- `scene-composite-not-selected.png`和`rejected-variants/`：未采用的自动回融，位于站点树外，不进入发布资源。
- `previous-design-qa.md`：上轮验收归档。

## 技术与交互验证

- `test_build.py`：现有14项生成与内容回归全部通过。
- `build_site.py --check`：94 outputs，changed=[]。
- `check_site.py`：93 pages、4028 localReferences、93 jsonLdPages，errors=[]，warnings=[]。
- 图片准备共134 records / 340 variants；仅新增头像一组记录，没有留下未采用的整幅回融记录。
- 桌面、750宽、390宽头像加载成功，百分比坐标误差均小于0.00002；无横向溢出。
- 景深暂停/开启前后头像相对背景的坐标和尺寸比例一致；点击贝克莱正确打开“乔治·贝克莱”，Escape关闭。
- 最终浏览器error/warn日志为空。遮罩轮廓最终细调后完成对照板和实际首页视觉复核。
- `git diff --check`通过。原肖像和v4背景未变；仅本地保存，未部署。
