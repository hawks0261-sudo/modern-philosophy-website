# Atheneum homepage assets

The user selected the warm historical hall composition on 5 September 2026. Its
light, parchment surfaces and Chinese heading remain the visual basis of the
homepage. The current v4 artwork retains the seven figures introduced in v2, reading and
conversing: Descartes, Spinoza, Leibniz, Kant, Locke, Berkeley and Hume. The selected
reference is archived in the local review output at
`output/atheneum-home-build-20260905/selected-reference.png` in the parent workspace.

- `hero-scene-v4.png`: current seven-person ImageGen scene, 1747 × 900 pixels,
  2,361,861 bytes. The second of two further ImageGen candidates was selected:
  Berkeley faces nearer the viewer, with both eyes clear, rounder cheeks and jaw,
  and a more relaxed expression around his brows, eyes and mouth. His open
  conversational hand gesture is retained. The source portrait remains
  `portrait-berkeley.jpg`; this is an artistic reconstruction, not an exact
  historical likeness, and some textures were redrawn.
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
- `portrait-{id}.jpg`: seven source portraits copied unchanged from
  `prototypes/files/portraits/` in the parent workspace. The Descartes, Kant and
  Berkeley files are retained; Spinoza, Leibniz, Locke and Hume were added for v2.
  These source portraits are separate from the generated scene and are not AI edits.
  Bilingual captions, catalogue links and attribution qualifications are maintained
  in `data/atheneum.json` and displayed in each profile dialog.
- `../optimized/f81677624738-{384,768,1440}.webp`: current v4 scene variants;
  the largest is 1440 × 742 pixels, 196,746 bytes (approximately 197 KB).
  The v3 `../optimized/9d6b3c23a6a7-*.webp`, v2
  `../optimized/c2c1cc2bc976-*.webp` and original three-person scene's
  `../optimized/7541e7aea1e0-*.webp` variants are retained. Paper variants use
  `../optimized/843b29caaa0a-*.webp`. `data/media.json` is the authoritative mapping
  for source dimensions and all responsive variants, including the portraits.

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

The institutional logo and actual publication covers come from the existing site.
No generated logo, fictional event or invented book cover from the reference is
used as institutional content. Headlines, name plaques, buttons, sources and all
profile text are real HTML and JavaScript; they are not baked into the image.

The desktop effect is a small pointer-driven pan/zoom illusion (2.5D). The person
picker and selected profile appear below the artwork. At widths up to 1200 px,
the scene keeps its full aspect ratio without the motion transform, and its
heading moves above the image. Reduced-motion preferences also disable the
transform. This implementation covers these seven figures; it does not provide
independent character meshes, free camera movement or a page-turning book.

`atheneum-scene.css` owns the v4 aspect ratio (1747 / 900), hotspots and responsive profile
layout. `atheneum-sections.css` owns the chapter divisions and readable paper
surfaces beneath the scene, including the warm beige-brown member sections
(`#people-preview` in Chinese and `#people` in English). See [the maintenance guide](../../scripts/README.md)
for their load order and the data requirements for adding a person.
