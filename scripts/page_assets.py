"""Idempotent image/font normalization for build_site.py (standard library)."""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import json
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]


class Attributes(HTMLParser):
    def handle_starttag(self, tag, attrs):
        self.attrs = dict(attrs)


def normalize_page(text, relative):
    manifest_path = ROOT / 'data' / 'media.json'
    media = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    relative = str(relative).replace('\\', '/')
    parent = posixpath.dirname(relative)
    first_content_image = True
    text = re.sub(r'<link\b[^>]*https://fonts\.(?:googleapis|gstatic)\.com[^>]*>\s*', '', text, flags=re.I)
    icon = posixpath.relpath('assets/favicon.png', parent or '.')
    text = re.sub(r'<link\b[^>]*href=[\"\'][^\"\']*assets/favicon\.png[\"\'][^>]*>\s*', '', text, flags=re.I)
    if not re.search(r'<link\b[^>]*rel=[\"\'](?:shortcut )?icon[\"\']', text, re.I):
        text = text.replace('</head>', f'<link rel="icon" type="image/png" href="{icon}">\n</head>')

    def image(match):
        nonlocal first_content_image
        original = match.group(0)
        parser = Attributes()
        parser.feed(original)
        attrs = getattr(parser, 'attrs', {})
        src = attrs.get('src', '')
        if not src or '${' in src or urlsplit(src).scheme or src.startswith('//'):
            return original
        key = attrs.get('data-media-source') or posixpath.normpath(posixpath.join(parent, unquote(urlsplit(src).path)))
        record = media.get(key)
        if not record:
            return original
        attrs['data-media-source'] = key
        attrs['width'] = str(record['width'])
        attrs['height'] = str(record['height'])
        attrs['decoding'] = 'async'
        is_logo = 'logo' in key.lower()
        is_home_shelf = 'data-home-shelf' in attrs
        attrs['loading'] = 'eager' if is_logo or first_content_image or is_home_shelf else 'lazy'
        if not is_logo:
            first_content_image = False
        variants = record.get('variants', [])
        if variants:
            sizes = '(max-width: 680px) calc(100vw - 32px), (max-width: 1024px) 75vw, 760px'
            preferred_width = 768
            if 'atheneum-berkeley-head' in attrs.get('class', '').split():
                sizes, preferred_width = '5.6vw', 384
                attrs['loading'] = 'eager'
            elif 'atheneum-backdrop' in attrs.get('class', '').split():
                sizes, preferred_width = '100vw', 1440
            elif is_logo:
                sizes, preferred_width = '42px', 96
            elif relative == 'activities/index.html':
                sizes, preferred_width = '(max-width: 680px) 88px, 124px', 384
            elif relative == 'index.html':
                if is_home_shelf:
                    sizes, preferred_width = '(max-width: 680px) 30vw, 180px', 384
                elif key.startswith('posters/seminar-'):
                    sizes, preferred_width = '88px', 384
                elif key in ('uploads/journal-issue-01-cover.jpg', 'posters/xifang-yicong.png'):
                    sizes, preferred_width = '130px', 384
                else:
                    sizes = '(max-width: 680px) calc(100vw - 36px), (max-width: 1024px) calc(100vw - 44px), 520px'
            elif '/translation-series/' in relative and ('/thumbs/' in key or '/covers/' in key):
                sizes = '(max-width: 680px) 70vw, 320px'
            chosen = next((v for v in variants if v['width'] >= preferred_width), variants[-1])
            attrs['src'] = posixpath.relpath(chosen['src'], parent or '.')
            attrs['srcset'] = ', '.join(posixpath.relpath(v['src'], parent or '.') + ' ' + str(v['width']) + 'w' for v in variants)
            attrs['sizes'] = sizes
        return '<img ' + ' '.join(k if v is None else f'{k}="{escape(str(v), quote=True)}"' for k, v in attrs.items()) + '>'

    text = re.sub(r'<img\b[^>]*>', image, text, flags=re.I)
    return text
