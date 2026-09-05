"""Idempotent shared branding and secondary-page theme for static HTML."""
from html import escape
from html.parser import HTMLParser
import hashlib
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit, urlunsplit


HOME_PAGES = {'index.html', 'en/index.html'}
ROOT = Path(__file__).resolve().parents[1]
BRAND_LOGO = 'assets/brand/logo-heritage.svg'
THEME_STYLESHEETS = {'atheneum-brand.css', 'atheneum-pages.css'}
VERSIONED_ASSETS = {'site.css', 'atheneum-pages.css', 'atheneum-scene.css', 'atheneum.js'}


class TagAttributes(HTMLParser):
    def handle_starttag(self, tag, attributes):
        self.attributes = dict(attributes)


def attributes(markup):
    parser = TagAttributes()
    parser.feed(markup)
    return parser.attributes


def tag(name, attrs):
    values = ' '.join(key if value is None else f'{key}="{escape(str(value), quote=True)}"' for key, value in attrs.items())
    return '<' + name + (' ' + values if values else '') + '>'


def version_asset_urls(text, parent):
    """Refresh local asset versions while retaining paths and unrelated queries."""
    def version(match):
        name = match.group(1).lower()
        attrs = attributes(match.group(0))
        key = 'src' if name == 'script' else 'href'
        url = urlsplit(attrs.get(key, ''))
        if url.scheme or url.netloc or not url.path:
            return match.group(0)
        target = posixpath.normpath(posixpath.join(parent, unquote(url.path)))
        if target not in VERSIONED_ASSETS:
            return match.group(0)
        digest = hashlib.sha256((ROOT / target).read_bytes()).hexdigest()[:12]
        query = [part for part in url.query.split('&') if part and unquote(part.partition('=')[0]) != 'v']
        query.append('v=' + digest)
        attrs[key] = urlunsplit((url.scheme, url.netloc, url.path, '&'.join(query), url.fragment))
        return tag(name, attrs)

    return re.sub(r'<(link|script)\b[^>]*>', version, text, flags=re.I)


def normalize_theme(text, path):
    """Refresh managed styles and logo references without changing content media."""
    path = str(path).replace('\\', '/')
    parent = posixpath.dirname(path) or '.'
    is_home = path in HOME_PAGES
    stylesheet_names = ['atheneum-brand.css']
    if not is_home:
        stylesheet_names.append('atheneum-pages.css')

    def head(match):
        previous_urls = {}
        def remove_theme_link(link_match):
            attrs = attributes(link_match.group(0))
            href = urlsplit(attrs.get('href', ''))
            managed = attrs.get('data-generated') == 'site-theme'
            local_theme = not href.scheme and not href.netloc and posixpath.basename(href.path) in THEME_STYLESHEETS
            if local_theme and attrs.get('rel') == 'stylesheet':
                previous_urls.setdefault(posixpath.basename(href.path), href)
            return '' if attrs.get('rel') == 'stylesheet' and (managed or local_theme) else link_match.group(0)

        existing = re.sub(r'<link\b[^>]*>\s*', remove_theme_link, match.group(2), flags=re.I).rstrip()
        links = []
        for name in stylesheet_names:
            previous = previous_urls.get(name)
            href = urlunsplit(('', '', posixpath.relpath(name, parent), previous.query if previous else '', previous.fragment if previous else ''))
            links.append(tag('link', {'rel': 'stylesheet', 'href': href, 'data-generated': 'site-theme'}))
        return match.group(1) + existing + '\n' + '\n'.join(links) + '\n' + match.group(3)

    text = re.sub(r'(<head\b[^>]*>)(.*?)(</head\s*>)', head, text, count=1, flags=re.I | re.S)

    def body(match):
        attrs = attributes(match.group(0))
        classes = [value for value in attrs.get('class', '').split() if value != 'atheneum-page']
        if not is_home:
            classes.append('atheneum-page')
        if classes:
            attrs['class'] = ' '.join(classes)
        else:
            attrs.pop('class', None)
        return tag('body', attrs)

    text = re.sub(r'<body\b[^>]*>', body, text, count=1, flags=re.I)

    def logo(match):
        attrs = attributes(match.group(0))
        basename = posixpath.basename(unquote(urlsplit(attrs.get('src', '')).path))
        if attrs.get('data-media-source') != 'logo.png' and basename != 'logo.png':
            return match.group(0)
        attrs['src'] = posixpath.relpath(BRAND_LOGO, parent)
        attrs['data-media-source'] = BRAND_LOGO
        attrs.pop('srcset', None)
        attrs.pop('sizes', None)
        attrs.update(width='647', height='726', loading='eager')
        return tag('img', attrs)

    text = re.sub(r'<img\b[^>]*>', logo, text, flags=re.I)
    return version_asset_urls(text, parent)
