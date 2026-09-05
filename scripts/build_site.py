#!/usr/bin/env python3
"""Deterministic static-site generation. Python 3.9+, no installed packages.

Default (or --all): books + marked content + static navigation + page metadata
+ sitemap. --books-only: only both-language book output; useful during editing.
--check: calculate exactly the same output and fail without changing any file.
Author-edited content outside explicit generated regions is retained.
"""
from __future__ import annotations
import argparse
import html
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import quote, urlsplit
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = 'publications/translation-series/'
METADATA_BEGIN = '<!-- BEGIN GENERATED: page-metadata -->'
METADATA_END = '<!-- END GENERATED: page-metadata -->'


def load(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))


def esc(value):
    return html.escape(str(value), quote=True)


def plain(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', '', value))).strip()


def excerpt(value, limit=150):
    return value if len(value) <= limit else value[:limit].rstrip() + '…'


def relative(source, target):
    path, sep, fragment = target.partition('#')
    if path == source and sep:
        return '#' + fragment
    out = posixpath.relpath(path or source, posixpath.dirname(source) or '.')
    return out + (sep + fragment if sep else '')


def absolute(config, path):
    # Keep index.html canonical form consistent with actual navigation and sitemap.
    return config['base_url'] + quote(path, safe='/#-._~')


def safe_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2).replace('<', '\\u003c')


def replace_region(text, name, body):
    start = '<!-- BEGIN GENERATED: ' + name + ' -->'
    end = '<!-- END GENERATED: ' + name + ' -->'
    pattern = re.escape(start) + r'.*?' + re.escape(end)
    if start not in text:
        return text
    return re.sub(pattern, lambda _: start + '\n' + body + '\n' + end, text, flags=re.S)


def creator_label(book):
    return '编' if book.get('creatorRole') == 'editor' else '著'


def creator_noun(book):
    return '编者' if book.get('creatorRole') == 'editor' else '作者'


def persons(names):
    values = [{'@type': 'Person', 'name': name.strip()} for name in names.split('、') if name.strip()]
    return values[0] if len(values) == 1 else values


def book_card(book):
    title = esc(book['title'])
    href = './' + book['id'] + '/index.html'
    thumb = book['cover'].replace('./covers/', './thumbs/')
    return f'''<article class="book-card" data-book-id="{esc(book['id'])}">
  <a class="book-cover book-cover-image book-detail-link" href="{href}" tabindex="-1" aria-hidden="true">
    <img src="{esc(thumb)}" alt="《{title}》封面" loading="lazy" decoding="async" />
    <span class="book-index">No. {book['number']:02d}</span>
  </a>
  <div class="book-card-body">
    <small><time datetime="{book['date'][:7]}">{esc(book['published'])}</time> · {esc(book['publisher'])}</small>
    <h3><a class="book-detail-link" href="{href}">{title}</a></h3>
    <p class="book-meta">{esc(book['author'])} {creator_label(book)} / {esc(book['translator'])} 译</p>
    <p class="book-summary">{esc(excerpt(book['description'], 96))}</p>
    <div class="book-actions"><a href="{href}">阅读详情 <span aria-hidden="true">→</span></a><button class="book-card-trigger" type="button" aria-haspopup="dialog" aria-controls="series-modal" aria-label="快速预览《{title}》" hidden>快速预览</button></div>
  </div>
</article>'''


def book_detail(book):
    root = '../../../'
    title = esc(book['title'])
    # Templates contain source-level original images. The final media hook derives
    # optimized variants, so the same build is reproducible after media changes.
    cover = '../' + book['cover'].removeprefix('./')
    return f'''<!DOCTYPE html>
<html lang="zh-CN" data-root="{root}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | 西方思想文化译丛 | 现代思想研究中心</title>
  <link rel="stylesheet" href="{root}site.css" />
  <link rel="stylesheet" href="../books.css" />
</head>
<body>
  <div class="masthead"><span>Yangzhou University</span><span>Modern Thought · Intellectual History · Global Dialogue</span><span>Academic Events · Publications · Notices</span></div>
  <header class="site-header">
    <a class="brand" href="{root}index.html"><img src="{root}logo.png" alt="现代思想研究中心标识"><div class="brand-text"><strong>现代思想研究中心</strong><span>Center of Modern Thought</span></div></a>
    <nav class="nav-links" data-primary-nav aria-label="主导航"></nav>
    <div class="header-right"><div class="lang-toggle"><a href="index.html" lang="zh-CN" aria-current="page">中文</a><a href="{root}en/publications/index.html" lang="en">EN</a></div></div>
    <button class="nav-toggle" type="button" aria-label="菜单" aria-expanded="false"><span></span><span></span><span></span></button>
  </header>
  <div class="mobile-nav-backdrop"></div><nav class="mobile-nav" data-mobile-nav aria-label="移动导航"></nav>
  <section class="page-hero"><div class="page-hero-inner">
    <nav class="book-breadcrumb" aria-label="面包屑"><a href="{root}index.html">首页</a><span aria-hidden="true"> / </span><a href="../index.html">西方思想文化译丛</a><span aria-hidden="true"> / </span><span>书目 {book['number']}</span></nav>
    <span class="page-kicker">Western Thought and Culture · No. {book['number']:02d}</span>
    <h1 class="page-title">{title}</h1>
    <p class="page-subtitle">{esc(book['author'])} {creator_label(book)} / {esc(book['translator'])} 译 · {esc(book['publisher'])} · {esc(book['published'])}</p>
  </div></section>
  <main class="page-shell" id="main-content">
    <article class="book-detail-layout">
      <figure class="book-detail-cover"><img src="{esc(cover)}" alt="《{title}》封面" decoding="async" /><figcaption>西方思想文化译丛 · 书目 {book['number']}</figcaption></figure>
      <div class="detail-card prose book-detail-copy"><h2>内容简介</h2><p>{esc(book['description'])}</p>
        <h2>书目信息</h2>
        <dl class="book-facts"><div><dt>{creator_noun(book)}</dt><dd>{esc(book['author'])}</dd></div><div><dt>译者</dt><dd>{esc(book['translator'])}</dd></div><div><dt>出版社</dt><dd>{esc(book['publisher'])}</dd></div><div><dt>出版时间</dt><dd><time datetime="{book['date'][:7]}">{esc(book['published'])}</time></dd></div></dl>
        <div class="cta-row"><a class="cta-button" href="../index.html">返回完整书目</a></div>
      </div>
    </article>
  </main>
  <script src="{root}site.js"></script>
</body>
</html>
'''


def render_books(books, outputs):
    catalogue_path = BOOK_DIR + 'index.html'
    catalogue = (ROOT / catalogue_path).read_text(encoding='utf-8')
    catalogue = replace_region(catalogue, 'book-cards', '\n'.join(book_card(book) for book in books))
    catalogue = replace_region(catalogue, 'book-data', '<script type="application/json" id="books-data">\n' + safe_json(books) + '\n</script>')
    outputs[catalogue_path] = catalogue
    for book in books:
        outputs[BOOK_DIR + book['id'] + '/index.html'] = book_detail(book)


def languages(path, config, paths):
    pairs = {zh: en for zh, en in config['language_pairs'].items() if zh in paths and en in paths}
    reverse = {en: zh for zh, en in pairs.items()}
    english = path.startswith('en/')
    if path in pairs:
        return path, pairs[path], True
    if path in reverse:
        return reverse[path], path, True
    fallback = config.get('language_fallbacks', {}).get(path)
    if fallback is None:
        if '/people/' in '/' + path:
            fallback = 'people/index.html' if english else 'en/people/index.html'
        elif '/activities/' in '/' + path:
            fallback = 'activities/index.html' if english else 'en/activities/index.html'
        elif '/publications/' in '/' + path:
            fallback = 'index.html#outcomes' if english else 'en/publications/index.html'
        else:
            fallback = 'index.html' if english else 'en/index.html'
    if fallback.split('#')[0] not in paths:
        fallback = 'index.html' if english else 'en/index.html'
    return (fallback, path, False) if english else (path, fallback, False)


def navigation(text, path, config, paths):
    english = path.startswith('en/')
    items = config['navigation']['en' if english else 'zh']
    links = []
    for item in items:
        target = item['href']
        if target.split('#')[0] not in paths:
            continue
        current = (path.startswith(('en/' if english else '') + item['key'] + '/') if item['key'] in ('activities', 'people') else '/publications/' in '/' + path if item['key'] == 'outcomes' else path == target and '#' not in target)
        attrs = ' class="is-current" aria-current="page"' if current else ''
        links.append(f'<a href="{esc(relative(path, target))}" data-nav="{esc(item["key"])}"{attrs}>{esc(item["label"])}</a>')
    def nav(match):
        attrs = re.sub(r'\s+data-static-nav(?:="[^"]*")?', '', match.group(1))
        return '<nav' + attrs + ' data-static-nav>\n' + '\n'.join(links) + '\n</nav>'
    text = re.sub(r'<nav\b([^>]*\bdata-(?:primary|mobile)-nav\b[^>]*)>.*?</nav>', nav, text, flags=re.S)
    zh, en, paired = languages(path, config, paths)
    zh_href, en_href = relative(path, zh), relative(path, en)
    def html_tag(match):
        attrs = re.sub(r'\s+data-language-(?:zh|en)="[^"]*"', '', match.group(1))
        return f'<html{attrs} data-language-zh="{esc(zh_href)}" data-language-en="{esc(en_href)}">'
    text = re.sub(r'<html\b([^>]*)>', html_tag, text, count=1)
    zh_active = ' class="active" aria-current="page"' if not english else ''
    en_active = ' class="active" aria-current="page"' if english else ''
    en_title = 'English version' if paired else 'English overview'
    lang_links = f'<a href="{esc(zh_href)}" lang="zh-CN" hreflang="zh-CN"{zh_active}>中文</a><a href="{esc(en_href)}" lang="en" hreflang="en" aria-label="{en_title}" title="{en_title}"{en_active}>EN</a>'
    text = re.sub(r'(<div\b[^>]*class="lang-toggle"[^>]*>).*?</div>', lambda m: m.group(1) + lang_links + '</div>', text, flags=re.S)
    return text


def find_tag(text, tag, class_name=None):
    attr = r'[^>]*' if class_name is None else r'[^>]*class="[^"]*\b' + re.escape(class_name) + r'\b[^"]*"[^>]*'
    match = re.search(r'<' + tag + attr + r'>(.*?)</' + tag + r'>', text, re.S | re.I)
    return plain(match.group(1)) if match else ''


def metadata(text, path, config, paths, events, books, english_books=None, page_titles=None):
    # Strip our old block before deriving the next one; stale generated text is
    # never treated as author input. Existing author descriptions are respected.
    text = re.sub(re.escape(METADATA_BEGIN) + r'.*?' + re.escape(METADATA_END) + r'\n?', '', text, flags=re.S)
    title = find_tag(text, 'title')
    heading = find_tag(text, 'h1') or title
    english = path.startswith('en/')
    event_path = path.removeprefix('en/')
    event = next((e for e in events if e['path'] == event_path), None)
    book = next((b for b in books if path.removeprefix('en/') == BOOK_DIR + b['id'] + '/index.html'), None)
    translated_book = (english_books or {}).get(book['id']) if english and book else None
    description = find_tag(text, 'p', 'home-overview-description') or find_tag(text, 'p', 'page-subtitle') or find_tag(text, 'p', 'home-hero-desc')
    if book:
        description = translated_book['description'] if translated_book else book['description']
    if not description:
        description = find_tag(text, 'p')
    if not description:
        description = heading + (' · Center of Modern Thought' if english else ' · 现代思想研究中心')
    description = excerpt(description, 260 if english else 150)
    canonical = absolute(config, path)
    image_path = BOOK_DIR + book['cover'].removeprefix('./') if book else event['poster'] if event else 'logo.png'
    image = absolute(config, image_path)
    # Delete duplicate unmanaged search/share tags on first migration only.
    text = re.sub(r'<meta\b[^>]*(?:name="(?:description|twitter:[^"]*)"|property="og:[^"]*")[^>]*>\s*\n?', '', text, flags=re.I | re.M)
    text = re.sub(r'<link\b[^>]*rel="(?:canonical|alternate)"[^>]*>\s*\n?', '', text, flags=re.I | re.M)
    graph = []
    if path in ('index.html', 'en/index.html'):
        graph.append({'@type': 'Organization', '@id': config['base_url'] + '#organization', 'name': config['name_zh'], 'alternateName': config['name_en'], 'url': absolute(config, 'index.html'), 'logo': absolute(config, 'logo.png'), 'email': 'modernphi24@163.com'})
    if book:
        book_canonical = absolute(config, BOOK_DIR + book['id'] + '/index.html')
        if translated_book:
            graph.append({'@type': 'WebPage', '@id': canonical + '#webpage', 'name': heading, 'inLanguage': 'en', 'url': canonical, 'description': description, 'mainEntity': {'@id': book_canonical + '#book'}})
        graph.append({'@type': 'Book', '@id': book_canonical + '#book', 'name': book['title'], ('editor' if book.get('creatorRole') == 'editor' else 'author'): persons(book['author']), 'translator': persons(book['translator']), 'publisher': {'@type': 'Organization', 'name': book['publisher']}, 'datePublished': book['date'][:7], 'inLanguage': 'zh-CN', 'description': translated_book['description'] if translated_book else book['description'], 'image': image, 'url': book_canonical})
    if event:
        graph.append({'@type': 'Event', '@id': canonical + '#event', 'name': heading, 'startDate': event['startDate'], 'endDate': event['endDate'], 'description': description, 'image': image, 'url': canonical, 'organizer': {'@type': 'Organization', '@id': config['base_url'] + '#organization', 'name': config['name_en'] if english else config['name_zh']}})
    if path not in ('index.html', 'en/index.html'):
        home = 'en/index.html' if english else 'index.html'
        crumbs = [{'@type': 'ListItem', 'position': 1, 'name': 'Home' if english else '首页', 'item': absolute(config, home)}]
        parent = posixpath.dirname(posixpath.dirname(path)) + '/index.html'
        if parent in paths and parent != home and parent != path:
            parent_title = (page_titles or {}).get(parent)
            if not parent_title and (ROOT / parent).exists():
                parent_title = find_tag((ROOT / parent).read_text(encoding='utf-8'), 'h1')
            parent_title = parent_title or ('Publications' if english else '书目')
            crumbs.append({'@type': 'ListItem', 'position': len(crumbs) + 1, 'name': parent_title, 'item': absolute(config, parent)})
        crumbs.append({'@type': 'ListItem', 'position': len(crumbs) + 1, 'name': heading, 'item': canonical})
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': crumbs})
    tags = [METADATA_BEGIN, f'<meta name="description" content="{esc(description)}" />', f'<link rel="canonical" href="{esc(canonical)}" />']
    zh, en, paired = languages(path, config, paths)
    if paired:
        tags += [f'<link rel="alternate" hreflang="zh-CN" href="{esc(absolute(config, zh))}" />', f'<link rel="alternate" hreflang="en" href="{esc(absolute(config, en))}" />']
    tags += [f'<meta property="og:type" content="{"article" if event or book else "website"}" />', f'<meta property="og:site_name" content="{esc(config["name_en"] if english else config["name_zh"])}" />', f'<meta property="og:title" content="{esc(title)}" />', f'<meta property="og:description" content="{esc(description)}" />', f'<meta property="og:url" content="{esc(canonical)}" />', f'<meta property="og:image" content="{esc(image)}" />', f'<meta property="og:image:alt" content="{esc(("Cover of the Chinese edition: " + translated_book["title"] if translated_book else book["title"] + " 封面") if book else event["posterAlt"] if event and not english else heading if event else config["name_en"] if english else config["name_zh"])}" />', f'<meta property="og:locale" content="{"en_GB" if english else "zh_CN"}" />', '<meta name="twitter:card" content="summary_large_image" />', f'<meta name="twitter:title" content="{esc(title)}" />', f'<meta name="twitter:description" content="{esc(description)}" />', f'<meta name="twitter:image" content="{esc(image)}" />']
    if graph:
        tags += ['<script type="application/ld+json">', safe_json({'@context': 'https://schema.org', '@graph': graph}), '</script>']
    tags += [METADATA_END]
    return text.replace('</head>', '\n'.join(tags) + '\n</head>', 1)


def content_regions(text, path, events, books, people):
    ordered = sorted(events, key=lambda event: (event['startDate'], event['id']), reverse=True)
    latest = []
    archive = []
    for event in ordered:
        href = relative(path, event['path'])
        poster = relative(path, event['poster'])
        latest.append(f'''<article class="home-activity" data-content-id="{esc(event['id'])}">
  <a href="{esc(href)}" tabindex="-1" aria-hidden="true"><img src="{esc(poster)}" alt="{esc(event['posterAlt'])}" loading="lazy" decoding="async"></a>
  <div><time datetime="{event['startDate']}">{esc(event['dateLabel'])}</time>
    <h3><a href="{esc(href)}">{esc(event['title'])}</a></h3>
    <p>{esc(event['summary'])}</p><a class="home-text-link" href="{esc(href)}">阅读活动总结 →</a>
  </div>
</article>''')
        archive.append(f'''<article class="archive-card" data-content-id="{esc(event['id'])}" data-date="{event['startDate']}" data-type="{esc(event['type'])}" data-year="{event['startDate'][:4]}">
  <img class="archive-poster poster-contain" src="{esc(poster)}" alt="{esc(event['posterAlt'])}" loading="lazy" decoding="async" />
  <div class="archive-body">
    <div class="archive-meta"><span class="archive-type">{'讲座' if event['type'] == 'lecture' else '研讨会'}</span><time class="archive-date" datetime="{event['startDate']}">{esc(event['dateLabel'])}</time></div>
    <h3 class="archive-title">{esc(event['title'])}</h3><p class="archive-copy">{esc(event['summary'])}</p>
    <div class="cta-row"><a class="archive-link" href="{esc(href)}">阅读活动总结 →</a></div>
  </div>
</article>''')
    text = replace_region(text, 'home-latest-activities', '\n'.join(latest[:3]))
    text = replace_region(text, 'activity-archive', '\n'.join(archive))
    if path == 'activities/index.html':
        years = sorted({event['startDate'][:4] for event in events})
        text = re.sub(r'\s*<input\b[^>]*id="filter-year-\d{4}"[^>]*>', '', text)
        inputs = '\n'.join(f'<input class="archive-filter-input" type="radio" name="archive-year" id="filter-year-{year}" aria-label="年份：{year}" />' for year in years)
        text = re.sub(r'(<input\b[^>]*id="filter-year-all"[^>]*>)', lambda m: m.group(1) + '\n' + inputs, text)
        labels = '<label for="filter-year-all">全部</label>\n' + '\n'.join(f'<label for="filter-year-{year}">{year}</label>' for year in years)
        text = re.sub(r'(<div\b[^>]*data-filter-group="year"[^>]*>).*?</div>', lambda m: m.group(1) + '\n' + labels + '\n</div>', text, flags=re.S)
        # Also derive no-JavaScript filtering and empty states for future years.
        # This overrides legacy fixed-year rules without editing shared CSS.
        rules = ['.archive-empty { display: none !important; }']
        for year in years:
            rules += [f'#filter-year-{year}:checked ~ .archive-controls label[for="filter-year-{year}"] {{ background: var(--navy); color: var(--cream); border-color: var(--navy); }}', f'#filter-year-{year}:focus-visible ~ .archive-controls label[for="filter-year-{year}"] {{ outline: 3px solid #806219; outline-offset: 3px; }}', f'#filter-year-{year}:checked ~ .archive-grid .archive-card:not([data-year="{year}"]) {{ display: none; }}']
            for kind in ('lecture', 'seminar'):
                if not any(event['type'] == kind and event['startDate'].startswith(year) for event in events):
                    rules.append(f'#filter-type-{kind}:checked ~ #filter-year-{year}:checked ~ .archive-empty {{ display: block !important; }}')
        block = '<style data-generated="archive-filters">\n' + '\n'.join(rules) + '\n</style>'
        text = re.sub(r'<style data-generated="archive-filters">.*?</style>\n?', '', text, flags=re.S)
        text = text.replace('</head>', block + '\n</head>', 1)
    counts = {'activities': len(events), 'books': len(books), 'advisers': len([p for p in people['advisers'] if p['status'] == 'current']), 'adviser-countries': len({p['institutionCountry'] for p in people['advisers'] if p['status'] == 'current'}), 'memorial-advisers': len(people['memorialAdvisers'])}
    for key, value in counts.items():
        text = re.sub(r'(<(?:strong|span|b)\b[^>]*data-stat="' + key + r'"[^>]*>)\d+(</(?:strong|span|b)>)', lambda m: m.group(1) + str(value) + m.group(2), text)
    return text


def build(books_only=False):
    books, events, people, config = load('books.json'), load('events.json'), load('people.json'), load('site.json')
    outputs = {}
    render_books(books, outputs)
    from english_books import render_english_books
    english_entries = load('books-en.json')
    english_books = {entry['id']: entry for entry in english_entries}
    outputs.update(render_english_books(books, english_entries))
    paths = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*.html') if not any(part.startswith('.') or part in ('node_modules', 'output') for part in p.relative_to(ROOT).parts)} | set(outputs)
    if not books_only:
        for path in sorted(paths):
            text = outputs.get(path, None)
            if text is None:
                text = (ROOT / path).read_text(encoding='utf-8')
            outputs[path] = content_regions(text, path, events, books, people)
    from journal_content import normalize_journal
    from atheneum_home import normalize_atheneum
    from site_theme import normalize_theme
    try:
        from page_assets import normalize_page
    except ImportError:
        normalize_page = lambda text, relative: text
    page_titles = {path: find_tag(text, 'h1') for path, text in outputs.items()}
    for path in sorted(outputs):
        text = normalize_journal(outputs[path], path)
        text = normalize_atheneum(text, path, events, books, english_books, page_titles)
        text = navigation(text, path, config, paths)
        text = metadata(text, path, config, paths, events, books, english_books, page_titles)
        text = normalize_theme(text, path)
        outputs[path] = normalize_page(text, path)
    if not books_only:
        urls = '\n'.join('  <url><loc>' + xml_escape(absolute(config, path)) + '</loc></url>' for path in sorted(paths))
        outputs['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n'
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true', help='Generate the complete static site (default).')
    parser.add_argument('--books-only', action='store_true', help='Generate only the Chinese and English catalogues and their standalone book pages.')
    parser.add_argument('--check', action='store_true', help='Fail if generated output differs; never write files.')
    args = parser.parse_args()
    outputs = build(args.books_only)
    changes = []
    for path, text in sorted(outputs.items()):
        target = ROOT / path
        if not target.exists() or target.read_text(encoding='utf-8') != text:
            changes.append(path)
            if not args.check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding='utf-8')
    print(json.dumps({'mode': 'check' if args.check else 'write', 'outputs': len(outputs), 'changed': changes}, ensure_ascii=False, indent=2))
    return 1 if args.check and changes else 0


if __name__ == '__main__':
    raise SystemExit(main())
