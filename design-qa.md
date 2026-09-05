# 贝克莱画像与成员栏目配色验收 · 2026-09-05

final result: passed

## 本轮修改

- 使用内置 ImageGen，参照 `assets/atheneum/portrait-berkeley.jpg` 对原七人场景中的贝克莱头脸进行局部校准。新图为 `assets/atheneum/hero-scene-v3.png`，1747×900；旧 v2（1748×899）及原肖像均保留。
- 贝克莱的脸颊、下颌更饱满圆润，鼻尖突出与鼻口挤压感减轻，侧转幅度减小。头颈、衣领和暖窗光衔接自然。其余六人位置、姿态与三组构图未出现明显变化；生成过程有细部纹理重绘，不能称像素完全保持。
- 新场景仍是参考历史肖像校准的艺术化形象，脸颊阴影和嘴角表情与原肖像存在细微差别，不声称精确复原。
- 中文 `#people-preview` 与英文 `#people` 从灰绿 #dfe1d3 改为暖米褐 #e4d4b8；深棕字 #3e2d1d、正文 #615039、小标题 #77542c，褐金规则线 #8f6b3d / #b5986c。仅改变该区域色彩变量，不改布局或内容。
- 渲染器、两种响应式宽高比和中英文首页同步新资源；生成384、768、1440宽WebP，最大205916字节。

## 图像与页面对照

输出目录：`/Users/hawksky/Desktop/modern phi/output/atheneum-berkeley-fix-20260905/`。

- ImageGen编辑输入：`hero-scene-v2.png`；参考输入：`portrait-berkeley.jpg`。生成结果原件位于 `/Users/hawksky/.codex/generated_images/01a070f9-2e5e-71c1-a03e-f57cc09b7ffb/exec-15a92438-314c-42d4-96bd-b3937b8bb0a4.png`。
- 精确工具提示词和输入/输出路径已保存：[imagegen-prompt.txt](/Users/hawksky/Desktop/modern%20phi/output/atheneum-berkeley-fix-20260905/imagegen-prompt.txt)。
- 原始v2、v3与贝克莱参考肖像经根代理及独立子代理查看。新图面部有改善、无明显贴脸边缘；也记录了仍有场景化差异的局限。
- 首页 `home-before.png` 与 `home-after.png` 在同一次浏览器工具输入中并置，1448×1086、页面顶部、贝克莱选中、资料面板关闭。对照验证场景构图、光线、标题覆盖与人物点击区域。对照时场景容器均使用新资源比例，避免用容器形变制造效果。
- 成员栏 `people-before.png` 与 `people-after.png` 在同一次输入中并置，750×746，目标区域距顶部约24px，对应用户标注的尺寸。暖米褐与相邻深棕联系区衔接，双线章节界限仍清楚。
- `home-mobile-en.png` 与 `people-mobile-en.png` 检查390×844的英文场景和成员章节；长标题正常换行，无横向溢出。
- 本地服务器在会话恢复后已退出，一次旧图捕获因资源未加载而无效；重启62027预览服务、确认naturalWidth>0后覆盖保存有效对照。本轮最终使用已加载图像的截图。

## 五项视觉与交互检查

- **图像**：新图中贝克莱的面颊、下颌、鼻口关系更自然；衣着、身体与椅子保持构图。没有把真实肖像平贴在场景上。
- **排版**：无文字和字体变更。成员栏目仍采用原三栏桌面结构，英文手机正文可读。
- **间距**：保留栏目间距和边界；新图宽高比直接对应实际文件，桌面与手机均按比例展示。
- **颜色**：成员区消除灰绿偏色，背景、标题、正文和规则线统一暖色；文字对比度样本4.66–9.02。
- **内容**：全部成员资料、哲学家介绍、肖像来源及书目信息保留。
- 桌面点击贝克莱热点，当前可见资料标题为“乔治·贝克莱”，原肖像加载成功；Escape关闭后焦点回同一热点。
- 静态图更新不改变人物坐标和交互脚本。初次检查直接读取面板第一个h2时得到隐藏的笛卡尔记录；随后按可见元素复核，实际激活人物正确，没有人物错配。

## 技术检查

- `prepare_media.py`：132 source records / 334 variants；仅新增v3记录与三张对应WebP。
- `build_site.py --all`：仅修改中英文首页图像行。
- `build_site.py --check`：94 outputs，changed=[]。
- `check_site.py`：93 pages，4019 localReferences，93 jsonLdPages，errors=[]，warnings=[]。
- 页面与图片资源在本地预览加载成功；新场景和成员区无横向溢出；最终浏览器error/warn日志为空。
- `git diff --check`通过。此轮为图像与配色调整，没有新增实现镜像测试。

本轮未部署。上一轮全站主题验收存入本输出目录的 `previous-design-qa.md`。
