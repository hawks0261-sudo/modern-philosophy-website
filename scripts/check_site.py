#!/usr/bin/env python3
"""Offline validation of every published HTML page, local URL and generated data.

Run build_site.py --check separately to check reproducibility. This checker does
not claim that external sites are reachable or that a search engine will index
metadata. No network requests or deployment are performed.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = []
        self.refs = []
        self.images = []
        self.metas = []
        self.links = []
        self.counts = Counter()
        self.lang = ''
        self.title = ''
        self.headings = []
        self.nav_counts = []
        self.script_blocks = []
        self.stack = []
        self.current_script = None
        self.data = {}
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        self.counts[tag] += 1
        if attr.get('id'):
            self.ids.append(attr['id'])
        if tag == 'html':
            self.lang = attr.get('lang', '')
        if tag == 'meta':
            self.metas.append(attr)
        if tag == 'link':
            self.links.append(attr)
        if tag == 'img':
            self.images.append(attr)
        if tag == 'nav' and ('data-primary-nav' in attr or 'data-mobile-nav' in attr):
            self.nav_counts.append([attr, 0])
        if tag == 'a' and any(t == 'nav' and ('data-primary-nav' in a or 'data-mobile-nav' in a) for t, a in self.stack) and self.nav_counts:
            self.nav_counts[-1][1] += 1
        if tag == 'script' and attr.get('type') in ('application/ld+json', 'application/json'):
            self.current_script = [attr, '']
        for key in ('href', 'src', 'poster'):
            if key in attr and attr[key] and not (tag == 'link' and attr.get('rel') in ('preconnect', 'dns-prefetch')):
                self.refs.append((tag + ':' + key, attr[key]))
        if attr.get('srcset'):
            for item in attr['srcset'].split(','):
                if item.strip():
                    self.refs.append((tag + ':srcset', item.strip().split()[0]))
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, attr))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == 'script' and self.current_script is not None:
            self.script_blocks.append(self.current_script)
            self.current_script = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, text):
        if self.current_script is not None:
            self.current_script[1] += text
        if self.stack and self.stack[-1][0] == 'title':
            self.title += text
        if self.stack and self.stack[-1][0] == 'h1':
            self.headings.append(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', default='', help='Optional repo-relative path prefix for partial authoring checks.')
    parser.add_argument('--json', type=Path, help='Write complete machine-readable results.')
    args = parser.parse_args()
    config = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
    base = urlsplit(config['base_url'])
    paths = sorted(p for p in ROOT.rglob('*.html') if not any(part.startswith('.') or part in ('node_modules', 'output') for part in p.relative_to(ROOT).parts))
    pages = {p.relative_to(ROOT).as_posix(): Page(p) for p in paths}
    errors = []
    warnings = []
    references = 0
    metadata_graphs = 0

    def error(path, issue):
        errors.append({'path': path, 'issue': issue})

    def local_target(source, url):
        value = urlsplit(url)
        if value.scheme in ('mailto', 'tel', 'data', 'javascript', 'blob'):
            return None
        if value.netloc:
            if value.netloc != base.netloc or not value.path.startswith(base.path):
                return None
            target = ROOT / unquote(value.path[len(base.path):])
        elif value.path.startswith('/'):
            # A project site root-absolute URL must include the project prefix.
            if not value.path.startswith(base.path):
                return ('__OUTSIDE_PROJECT__', value.fragment)
            target = ROOT / unquote(value.path[len(base.path):])
        else:
            target = (ROOT / source).parent / unquote(value.path) if value.path else ROOT / source
        target = target.resolve()
        if not target.is_relative_to(ROOT):
            return ('__OUTSIDE_PROJECT__', value.fragment)
        if target.is_dir():
            target /= 'index.html'
        return target.relative_to(ROOT).as_posix(), unquote(value.fragment)

    def check_ref(source, kind, url):
        nonlocal references
        if url.startswith('javascript:'):
            error(source, 'Executable URL: ' + url)
            return
        resolved = local_target(source, url)
        if resolved is None:
            return
        target, anchor = resolved
        references += 1
        if target == '__OUTSIDE_PROJECT__':
            error(source, 'URL leaves GitHub project path: ' + url)
        elif not (ROOT / target).is_file():
            error(source, 'Missing ' + kind + ' target: ' + url)
        elif anchor and target in pages and anchor not in pages[target].ids:
            error(source, 'Missing anchor: ' + url)

    for path, page in pages.items():
        if args.scope and not path.startswith(args.scope):
            continue
        if page.counts['title'] != 1 or not page.title.strip():
            error(path, 'Expected exactly one nonempty title')
        if page.counts['h1'] != 1:
            error(path, f"Expected one h1; found {page.counts['h1']}")
        if page.counts['main'] != 1:
            error(path, f"Expected one main landmark; found {page.counts['main']}")
        if not page.lang:
            error(path, 'Missing document language')
        if duplicate_ids := [key for key, count in Counter(page.ids).items() if count > 1]:
            error(path, 'Duplicate IDs: ' + ', '.join(duplicate_ids))
        descriptions = [m for m in page.metas if m.get('name') == 'description']
        canonicals = [link for link in page.links if link.get('rel') == 'canonical']
        if len(descriptions) != 1 or not descriptions[0].get('content'):
            error(path, 'Expected one nonempty meta description')
        if len(canonicals) != 1 or canonicals[0].get('href') != config['base_url'] + path:
            error(path, 'Canonical does not match the configured project URL')
        for prop in ('og:title', 'og:description', 'og:url', 'og:image', 'og:image:alt'):
            if not any(m.get('property') == prop and m.get('content') for m in page.metas):
                error(path, 'Missing ' + prop)
        for name in ('twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'):
            if not any(m.get('name') == name and m.get('content') for m in page.metas):
                error(path, 'Missing ' + name)
        if len(page.nav_counts) != 2 or any(count < 2 or 'data-static-nav' not in attrs for attrs, count in page.nav_counts):
            error(path, 'Primary/mobile navigation must contain generated static links')
        for img in page.images:
            if 'alt' not in img:
                error(path, 'Image has no alt attribute: ' + img.get('src', ''))
            if not img.get('width') or not img.get('height'):
                warnings.append({'path': path, 'issue': 'Image dimensions unavailable: ' + img.get('src', '')})
        for kind, url in page.refs:
            check_ref(path, kind, url)
        for attrs, raw in page.script_blocks:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                error(path, 'Invalid JSON script: ' + str(exc))
                continue
            if attrs.get('type') == 'application/ld+json':
                metadata_graphs += 1
                if data.get('@context') != 'https://schema.org':
                    error(path, 'Unexpected JSON-LD context')
                for item in data.get('@graph', []):
                    if item.get('@type') == 'Book' and not re.fullmatch(r'\d{4}-\d{2}', item.get('datePublished', '')):
                        error(path, 'Book date must preserve source month precision')
                    if item.get('@type') == 'Event':
                        for key in ('startDate', 'endDate'):
                            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', item.get(key, '')):
                                error(path, 'Event date missing or invented precision')
            elif attrs.get('id') == 'books-data':
                expected = json.loads((ROOT / 'data/books.json').read_text(encoding='utf-8'))
                if data != expected:
                    error(path, 'Embedded books differ from data/books.json')
        for link in page.links:
            if link.get('rel') != 'alternate' or not link.get('hreflang'):
                continue
            resolved = local_target(path, link.get('href', ''))
            if resolved and resolved[0] in pages:
                target = pages[resolved[0]]
                if not any(other.get('rel') == 'alternate' and other.get('href') == config['base_url'] + path for other in target.links):
                    error(path, 'Language pair is not reciprocal: ' + link.get('href', ''))

    if not args.scope:
        for css in ROOT.rglob('*.css'):
            if any(part.startswith('.') or part in ('node_modules', 'output') for part in css.relative_to(ROOT).parts):
                continue
            for url in re.findall(r'url\(\s*[\'"]?([^\)\'\"]+)[\'"]?\s*\)', css.read_text(encoding='utf-8')):
                check_ref(css.relative_to(ROOT).as_posix(), 'CSS asset', url.strip())
        for forbidden in ('pdf-render.html', 'uploads/index.html'):
            if (ROOT / forbidden).exists():
                error(forbidden, 'Archived maintenance page must not enter the publication tree')
        titles = Counter(page.title.strip() for page in pages.values())
        for title, count in titles.items():
            if count > 1:
                error('site', 'Duplicate page title: ' + title)
        if not (ROOT / 'sitemap.xml').exists():
            error('sitemap.xml', 'Missing sitemap')
        else:
            try:
                tree = ET.parse(ROOT / 'sitemap.xml')
                locs = [el.text for el in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
                expected = {config['base_url'] + path for path in pages}
                if set(locs) != expected or len(locs) != len(expected):
                    error('sitemap.xml', 'Sitemap URLs differ from published HTML pages')
            except ET.ParseError as exc:
                error('sitemap.xml', str(exc))
        books = json.loads((ROOT / 'data/books.json').read_text(encoding='utf-8'))
        if len({book['id'] for book in books}) != len(books):
            error('data/books.json', 'Duplicate book IDs')
        for book in books:
            path = 'publications/translation-series/' + book['id'] + '/index.html'
            if path not in pages or book['title'] not in pages[path].title:
                error(path, 'Missing book detail or title mismatch')
            for image in (book['cover'], book['cover'].replace('./covers/', './thumbs/')):
                check_ref('publications/translation-series/index.html', 'book image', image)
        people = json.loads((ROOT / 'data/people.json').read_text(encoding='utf-8'))
        directory = (ROOT / people['source']).read_text(encoding='utf-8')
        current_section = directory.split('id="international-advisers"', 1)[-1].split('id="honorary-memory"', 1)[0]
        for person in people['advisers']:
            if person['name'] not in current_section:
                error('data/people.json', 'Adviser absent from current source section: ' + person['name'])
    result = {'scope': args.scope or 'all', 'pages': sum(not args.scope or p.startswith(args.scope) for p in pages), 'localReferences': references, 'jsonLdPages': metadata_graphs, 'errors': errors, 'warnings': warnings}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
