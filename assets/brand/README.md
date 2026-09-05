# 原始盾徽与古金适配

## 来源

- 原始矢量文件：`/Users/hawksky/Desktop/modern phi/logo-header`（无扩展名，内容为 SVG）。
- `logo-original.svg`：逐字节复制原始文件。
- `logo-heritage.svg`：从原始 SVG 仅替换两个 path 的 `fill` 为 `#d4b476`。
- 原始 `logo.png` 保留，未被修改或替换。

## 身份与使用说明

原有盾形、打开的书、羽毛笔、七道光芒、拉丁文 `Centrum Cogitationis Modernae` 全部来自原始矢量路径，未重新绘制或生成。

此 SVG 原本就是深色实底盾形和透明镂空图形；古金版本因此呈现金色实底，镂空书页、羽毛、文字和边线透出页面底色。建议在深棕背景中浏览实际效果。若视觉重量过强，应在实际页眉中调整尺寸或周围留白，而不是宣称此版本已改变为金色线稿。

原始 SVG 没有底部中文，两个导出文件也没有添加中文。网站在徽记旁另行显示中文品牌名称。现有 `logo.png` 的底部中文不属于此 SVG 的原始路径。

## 可逆性与校验

仅发生两处颜色字符串替换；根元素尺寸、viewBox、路径数量、路径 d、fill-rule 和 fill-opacity 均保留。可随时切回 `logo-original.svg`。

- viewBox：`0 0 646.7124 725.7636`
- width：`646.7124pt`
- height：`725.7636pt`
- path 数量：2
- 两版逐一比较 path `d`：完全一致
- 原始源文件 SHA-256：`10df70fb7362a99a4344edaa3f9aed9712c052307ae8232edb612fb6d78dd909`
- logo-original.svg SHA-256：`10df70fb7362a99a4344edaa3f9aed9712c052307ae8232edb612fb6d78dd909`
- logo-heritage.svg SHA-256：`cbbd84cb78252577375239619ec806d11d016e3b0c8ce45a34b0a408918a4a2a`
- path 1 d 的 SHA-256（两版相同）：`9c63a7c4d5a54c0bc4d701eed25bcbdd86b3dbfae0dc2be18528e0f386b886c8`
- path 2 d 的 SHA-256（两版相同）：`2d7fe7525513123fe645d26573d42366ec2c149ddde3a75a37946518851f7eca`

校验已执行：原样副本字节一致；两版根属性一致；两条路径的 d 及全部非 fill 属性一致；两处 fill 均为 `#d4b476`。本次没有调用图像生成或修改网站代码。
