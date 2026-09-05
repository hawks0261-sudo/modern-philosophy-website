# Atheneum homepage assets

The user selected the warm historical hall composition on 5 September 2026. Its
layout, light, three figures, parchment surfaces and Chinese heading are the visual
basis of this homepage. The reference is archived in the local review output at
`output/atheneum-home-build-20260905/selected-reference.png` in the parent workspace.

- `hero-scene.png`: ImageGen edit of that selected reference, with interface text,
  plaques, profile card, footer and branding removed. The hall and three figures
  remain an artistic reconstruction, not a documented historical gathering or
  independent 3D models. Original generation ID: `01a071c2-1413-7bb2-b505-c2c0c9d70b81`.
- `parchment.png`: ImageGen parchment texture made for the selected warm book palette.
- `portrait-descartes.jpg`, `portrait-kant.jpg`, `portrait-berkeley.jpg`: existing
  project portrait assets, copied from the earlier prototype. Source catalogue
  references and careful attributions are recorded in `data/atheneum.json` and shown
  in the profile dialog. The original source portraits are not AI edits.
- `../optimized/7541e7aea1e0-*.webp` and `../optimized/843b29caaa0a-*.webp` are the
  prepared responsive scene and paper assets. `data/media.json` records dimensions
  and variants. The scene's largest web variant is approximately 210 KB.

The institutional logo and actual publication covers come from the existing site.
No generated logo, fictional event or invented book cover from the reference is
used as institutional content. Headlines, name plaques, buttons, sources and all
profile text are real HTML and JavaScript; they are not baked into the image.

The desktop effect is a small pointer-driven pan/zoom illusion (2.5D). At widths
up to 1024 px, the image keeps its full aspect ratio and the profile appears below
it. Reduced-motion preferences disable the transform. This implementation does
not provide free camera movement, a 3D mesh or a page-turning book.
