# Atheneum homepage assets

The user selected the warm historical hall composition on 5 September 2026. Its
light, parchment surfaces and Chinese heading remain the visual basis of the
homepage. The current homepage combines the twelve-person v5 background with the
retained, separately masked Berkeley head layer. Descartes, Spinoza, Leibniz, Kant,
Locke, Berkeley and Hume are joined by Pascal, Malebranche, Boyle, Comte and Bergson.
The figures read and converse in an artistic gathering across different centuries,
not a documented historical meeting. The selected visual reference is archived at
`output/atheneum-home-build-20260905/selected-reference.png` in the parent workspace.

- `hero-scene-v5.png`: current twelve-person ImageGen background, 1744 × 902 pixels,
  2,275,327 bytes. Two built-in image edits first added Pascal, Malebranche and
  Boyle, then Comte and Bergson, with historical portrait references for each.
  Existing seven figures visually retain their positions, poses and identity;
  generation does not guarantee identical pixels. Comte sits prominently in the
  left foreground, with his lower legs outside the frame; Bergson stands at the
  far right. This use of depth keeps all twelve faces separately visible.
  `hero-scene-v5-stage1-prompt.txt` and `hero-scene-v5-stage2-prompt.txt` preserve
  the actual prompts. The ten-person intermediate, original twelve-person output
  and inspection coordinates are archived in the parent workspace at
  `output/philosophers-wave2-20260905/`. No previous scene was overwritten.
- `hero-scene-v4.png`: retained previous seven-person ImageGen background, 1747 × 900 pixels,
  2,361,861 bytes. The second of two further ImageGen candidates was selected:
  Berkeley faces nearer the viewer, with both eyes clear, rounder cheeks and jaw,
  and a more relaxed expression around his brows, eyes and mouth. His open
  conversational hand gesture is retained. The source portrait remains
  `portrait-berkeley.jpg`; this is an artistic reconstruction, not an exact
  historical likeness, and some textures were redrawn. The archived v4 file was
  not changed by the separate head-layer refinement or by the later v5 generation.
- `berkeley-head-v1.png`: generated head layer, 1254 × 1254 pixels, 1,775,574 bytes.
  It refines Berkeley's facial likeness independently of the scene. The file is
  RGB: its checkerboard is painted into the image, not a true alpha channel.
  Do not display this PNG or its WebP variants without the matching contour mask.
  `portrait-berkeley.jpg` remains the unchanged historical source portrait.
- `berkeley-head-mask.svg`: contour mask with a matching 1254 × 1254 viewBox.
  White reveals the head; black and transparent areas hide the surrounding pixels.
  The CSS must retain `mask-mode: luminance`; using alpha mode would change the
  treatment of the black contour. If the head image changes, review the mask
  outline against that image before reusing it.
- `hero-scene-v3.png`: retained previous seven-person scene, 1747 × 900 pixels.
  A local head-and-face edit uses `portrait-berkeley.jpg` to adjust Berkeley's face
  shape, head turn, nose and mouth. The overall composition and other figures'
  positions remain broadly consistent with v2, though some fine details were
  lightly redrawn during generation. This is an artistic interpretation of the
  source portrait, not an exact reconstruction of Berkeley's appearance.
- `hero-scene-v2.png`: retained seven-person ImageGen scene, 1748 × 899 pixels;
  the source file is unchanged and remains available for comparison with later revisions.
  Historical portraits inform the figures; their poses and shared setting are an
  artistic composition, not a documented gathering or an exact reconstruction of
  each person's appearance.
- `hero-scene.png`: retained original three-person scene, 1786 × 881 pixels, made
  by editing the selected reference to remove interface text, plaques, profile
  card, footer and branding. It is preserved for comparison rather than overwritten
  by subsequent versions. Original generation ID: `01a071c2-1413-7bb2-b505-c2c0c9d70b81`.
- `parchment.png`: ImageGen parchment texture made for the selected warm book palette.
- `portrait-{id}.jpg`: twelve historical source portraits, separate from the
  generated scene and not AI edits. The first seven were copied unchanged from
  `prototypes/files/portraits/` in the parent workspace. Five more were prepared
  for v5 from the verified references documented below.
  Bilingual captions, catalogue links and attribution qualifications are maintained
  in `data/atheneum.json` and displayed in each profile dialog.
- `../optimized/e0799aec94b2-{384,768,1440}.webp`: current v5 background variants;
  the largest is 1440 × 745 pixels, 178,628 bytes (approximately 179 KB).
  The v4 `../optimized/f81677624738-*.webp`, v3
  `../optimized/9d6b3c23a6a7-*.webp`, v2
  `../optimized/c2c1cc2bc976-*.webp` and original three-person scene's
  `../optimized/7541e7aea1e0-*.webp` variants are retained. Paper variants use
  `../optimized/843b29caaa0a-*.webp`. `data/media.json` is the authoritative mapping
  for source dimensions and all responsive variants, including the portraits.
- `../optimized/ee8d73791954-{384,768,1254}.webp`: head-layer variants, respectively
  15,236, 45,848 and 98,832 bytes. `scripts/page_assets.py` gives this layer
  `sizes="5.6vw"`, eager loading and a preferred source width of 384 pixels.

The head and background share `.atheneum-world`, so scene transforms and responsive
scaling keep them together. `atheneum-scene.css` places the head at `left: 67.25%`,
`top: 37%`, `width: 5.6%` and applies `brightness(.95) saturate(.88)`. Keep placement,
mask and source dimensions coordinated when changing either layer. The head has
empty alternative text, `aria-hidden="true"` and `pointer-events: none`; the scene
description and existing philosopher buttons provide the accessible content and
interaction. Without support for CSS masking and luminance mode, the layer stays
hidden and the intact v5 background remains visible.

An unselected full-scene composite is archived outside the site tree at
`output/atheneum-berkeley-likeness-20260905/scene-composite-not-selected.png` in the
parent workspace. It is not part of the published scene or its media variants.

The four portrait sources added in v2 are:

- **Spinoza** — anonymous, circa 1665, Herzog August Library, Wolfenbüttel:
  [library catalogue](https://diglib.hab.de/varia/gemaelde/b-117/start.htm).
  The library's [conservation and X-ray record](https://www.deutsche-digitale-bibliothek.de/item/GDQILRNAJS2TSXNYQGE4KUJD6GCG2JGB)
  leaves unresolved whether this was painted from life or is an early copy.
- **Leibniz** — Christoph Bernhard Francke, circa 1695, Herzog Anton Ulrich Museum:
  [official painting collection](https://3landesmuseen-braunschweig.de/en/herzog-anton-ulrich-museum/collection/departments/painting-collection-old-masters).
- **Locke** — Godfrey Kneller, 1697, Hermitage version:
  [image catalogue](https://commons.wikimedia.org/wiki/File:Godfrey_Kneller_-_Portrait_of_John_Locke_(Hermitage).jpg).
  This catalogue cites Hermitage record 38692, accession ГЭ-1345. The museum's
  former detail link was unavailable at verification; the accessible catalogue is
  therefore used, without substituting another Kneller portrait of Locke.
- **Hume** — Allan Ramsay, 1766, Scottish National Portrait Gallery:
  [record supplied by National Galleries Scotland](https://artsandculture.google.com/asset/david-hume-allan-ramsay/KgH_IR3l3MzLIQ).
  This is the red-coat portrait, distinct from Ramsay's 1754 turban portrait.

The five portrait sources added in v5 are:

- **Pascal** — anonymous, after François II Quesnel, seventeenth century,
  Louvre RF 1479, on deposit at Versailles as MV 5527:
  [Louvre catalogue](https://collections.louvre.fr/ark:/53355/cl010389756).
  The attribution is “after”, not an autograph Quesnel painting. The digital image
  is Janmad's photograph of the work, supplied via Wikimedia Commons as PD-Art.
- **Malebranche** — Pierre de Rochefort, 1707–1733, etching and engraving,
  Rijksmuseum RP-P-OB-72.656:
  [museum catalogue](https://id.rijksmuseum.nl/200308917).
  The displayed source is a cropped version of this print; the museum marks the
  work public domain, and the Commons image is CC0.
- **Boyle** — Johann Kerseboom, 1689, the Shannon portrait:
  [Science History Institute collection](https://digital.sciencehistory.org/works/3r074v879).
  Courtesy of Science History Institute; its digital image is licensed under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This is the Shannon
  version, not the separate Royal Society version. The profile retains a visible
  licence link as well as the institutional credit.
- **Comte** — Johan Hendrick Hoffmeister, 1851 lithograph after an 1849
  daguerreotype, the “Dutch portrait”:
  [Maison d’Auguste Comte portrait catalogue](https://augustecomte.org/musee/visite/portraits-dauguste-comte/).
  The museum explains that the artist used the photograph without meeting Comte.
- **Bergson** — Bain News Service glass-negative archive, Library of Congress
  LC-DIG-ggbain-38388:
  [institutional record](https://www.loc.gov/item/2014718527/).
  No exact photographic date or individual photographer is supplied in the site's
  caption. His clothing details and standing pose in the hall are artistic additions.

The institutional logo and actual publication covers come from the existing site.
No generated logo, fictional event or invented book cover from the reference is
used as institutional content. Headlines, name plaques, buttons, sources and all
profile text are real HTML and JavaScript; they are not baked into the image.

The desktop effect is a small pointer-driven pan/zoom illusion (2.5D). The person
picker and selected profile appear below the artwork. At widths up to 1200 px,
the scene keeps its full aspect ratio without the motion transform, and its
heading moves above the image. Reduced-motion preferences also disable the
transform. This implementation covers these twelve figures; it does not provide
independent character meshes, free camera movement or a page-turning book.

`atheneum-scene.css` owns the v5 aspect ratio (1744 / 902), masked head placement,
twelve hotspots and responsive profile layout. Hotspots follow the rendered v5
positions rather than the approximate positions requested in the prompts. Pascal
is at the far left, Malebranche in the aisle between the left table and Kant,
Boyle behind Berkeley and Hume, Comte in the left foreground and Bergson at the
far right. Comte overlaps the lower left table and Leibniz's clothing; the Leibniz
hotspot is therefore restricted to his upper area. Boyle's hotspot likewise
covers his upper figure so it does not intercept Berkeley's selection. Recheck
both visible faces and overlapping clickable regions when changing the scene.

`atheneum-sections.css` owns the chapter divisions and readable paper
surfaces beneath the scene, including the warm beige-brown member sections
(`#people-preview` in Chinese and `#people` in English). See [the maintenance guide](../../scripts/README.md)
for their load order and the data requirements for adding a person.
