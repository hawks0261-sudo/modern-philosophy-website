#!/usr/bin/env python3
"""Prepare optional responsive assets; originals stay intact. Requires Pillow.

Run only when adding/changing source images. Ordinary build/check uses the
committed manifest and does not depend on Pillow or network services.
"""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'optimized'
MANIFEST = ROOT / 'data' / 'media.json'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    previous = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    result = {}
    for source in sorted(ROOT.rglob('*')):
        if source.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'} or 'assets/optimized/' in source.as_posix():
            continue
        key = source.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        old = previous.get(key, {})
        if old.get('sha256') == digest and all((ROOT / v['src']).exists() for v in old.get('variants', [])):
            result[key] = old
            continue
        with Image.open(source) as opened:
            image = ImageOps.exif_transpose(opened)
            width, height = image.size
            record = {'width': width, 'height': height, 'bytes': source.stat().st_size, 'sha256': digest, 'variants': []}
            is_logo = 'logo' in source.name.lower()
            targets = [48, 96] if is_logo else [384, 768, min(width, 1440)]
            if source.stat().st_size > 40000 or is_logo:
                for target in sorted(set(min(width, value) for value in targets)):
                    scaled = image.copy()
                    scaled.thumbnail((target, max(1, round(height * target / width))), Image.Resampling.LANCZOS)
                    filename = hashlib.sha256(key.encode()).hexdigest()[:12] + '-' + str(scaled.width) + '.webp'
                    dest = OUT / filename
                    scaled.save(dest, 'WEBP', quality=86, method=6)
                    record['variants'].append({'src': dest.relative_to(ROOT).as_posix(), 'width': scaled.width, 'height': scaled.height, 'bytes': dest.stat().st_size})
            result[key] = record
    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'Prepared {len(result)} image records, {sum(len(v["variants"]) for v in result.values())} variants.')


if __name__ == '__main__':
    main()
