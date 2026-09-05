"""Idempotent shared branding and secondary-page theme for static HTML."""
from html import escape
from html.parser import HTMLParser
import posixpath
import re
from urllib.parse import unquote, urlsplit


HOME_PAGES = {'index.html', 'en/index.html'}
BRAND_LOGO = 'assets/brand/logo-heritage.svg'
THEME_STYLESHEETS = {'atheneum-brand.css', 'atheneum-pages.css'}


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


def normalize_theme(text, path):
    """Refresh managed styles and logo references without changing content media."""
    path = str(path).replace('\\', '/')
    parent = posixpath.dirname(path) or '.'
    is_home = path in HOME_PAGES
    stylesheet_names = ['atheneum-brand.css']
    if not is_home:
        stylesheet_names.append('atheneum-pages.css')

    def head(match):
        def remove_theme_link(link_match):
            attrs = attributes(link_match.group(0))
            href = urlsplit(attrs.get('href', ''))
            managed = attrs.get('data-generated') == 'site-theme'
            local_theme = not href.scheme and not href.netloc and posixpath.basename(href.path) in THEME_STYLESHEETS
            return '' if attrs.get('rel') == 'stylesheet' and (managed or local_theme) else link_match.group(0)

        existing = re.sub(r'<link\b[^>]*>\s*', remove_theme_link, match.group(2), flags=re.I).rstrip()
        links = [tag('link', {'rel': 'stylesheet', 'href': posixpath.relpath(name, parent), 'data-generated': 'site-theme'}) for name in stylesheet_names]
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

    return re.sub(r'<img\b[^>]*>', logo, text, flags=re.I)
