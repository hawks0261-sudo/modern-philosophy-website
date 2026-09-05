"""Static English catalogue pages for the same Chinese editions in books.json."""
from html import escape
import calendar
import hashlib
import posixpath
import re

BOOK_DIR = 'publications/translation-series/'
EN_BOOK_DIR = 'en/' + BOOK_DIR
SERIES_NAME = 'Western Thought & Culture Library'


def esc(value):
    return escape(str(value), quote=True)


def rel(path, target):
    return posixpath.relpath(target, posixpath.dirname(path) or '.')


def named(value):
    # Preserve unverified spellings in the supplied Chinese form; do not invent
    # romanization merely to make an English page look fully Latin-script.
    language = ' lang="zh-CN"' if re.search(r'[\u3400-\u9fff]', value) else ''
    return f'<span{language}>{esc(value)}</span>'


def published(book):
    year, month = book['date'].split('-')[:2]
    return f'{calendar.month_name[int(month)]} {year}'


def role(book):
    return 'Edited by' if book.get('creatorRole') == 'editor' else 'By'


def stylesheet():
    return '''<style>
.english-books .page-hero { padding: 0; }
.english-books .page-hero-inner { padding-top: 42px; padding-bottom: 36px; }
.english-books .page-title { max-width: 25ch; font-family: Georgia, serif; font-size: clamp(29px, 4.1vw, 50px); line-height: 1.18; overflow-wrap: anywhere; }
.english-books .page-subtitle { max-width: 78ch; font-size: 16px; line-height: 1.65; }
.en-book-original { margin: 14px 0; font-family: "Songti SC", STSong, SimSun, serif; line-height: 1.65; }
.page-hero .en-book-original { color: var(--cream); }
.en-books-note { margin: 0 0 28px; max-width: 88ch; line-height: 1.7; color: var(--muted); }
.en-book-card h3 { font-family: Georgia, serif; font-size: 21px; line-height: 1.3; }
.en-book-card .book-meta { line-height: 1.65; }
.en-book-card .en-book-original { color: var(--text); font-size: 14px; }
.en-book-card .book-summary { line-height: 1.7; }
.english-books .book-detail-copy h2 { font-family: Georgia, serif; font-size: 28px; line-height: 1.35; }
.english-books .book-detail-copy > p { max-width: 74ch; }
.english-books .book-facts > div { grid-template-columns: 130px minmax(0, 1fr); }
.english-books .book-facts dt { color: #806219; }
.english-books .book-breadcrumb { font-size: 13px; line-height: 1.65; }
.english-books .book-actions a { font-size: 14px; }
.english-books .cta-row a.cta-button { color: var(--cream); }
.english-books .site-footer { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px 28px; padding: 24px max(20px, calc((100vw - 1180px) / 2)); border-top: 1px solid var(--border); color: var(--muted); font-size: 13px; line-height: 1.6; }
@media (max-width: 680px) {
 .english-books .page-hero-inner { padding-top: 28px; padding-bottom: 24px; }
 .english-books .book-facts > div { grid-template-columns: 95px minmax(0, 1fr); gap: 12px; }
 .en-book-card h3 { font-size: 22px; }
}
</style>'''


def shell(path, title, hero, main):
    root = rel(path, 'site.css').removesuffix('site.css')
    en_home = rel(path, 'en/index.html')
    css = rel(path, BOOK_DIR + 'books.css')
    return f'''<!DOCTYPE html>
<html lang="en" data-root="{root}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Center of Modern Thought</title>
<link rel="stylesheet" href="{root}site.css"><link rel="stylesheet" href="{css}">
{stylesheet()}
</head>
<body class="english-overview english-page english-books" id="top">
<a class="overview-skip" href="#main-content">Skip to content</a>
<div class="masthead"><span>Yangzhou University</span><span>Modern Thought · Intellectual History · Global Dialogue</span></div>
<header class="site-header"><a class="brand" href="{en_home}"><img src="{root}logo.png" alt="Center of Modern Thought"><div class="brand-text"><strong>Center of Modern Thought</strong><span>Yangzhou University</span></div></a><nav class="nav-links" data-primary-nav aria-label="Main navigation"></nav><div class="header-right"><div class="lang-toggle" aria-label="Page language"></div></div><button class="nav-toggle" type="button" aria-label="Open navigation menu" aria-expanded="false"><span></span><span></span><span></span></button></header>
<nav class="mobile-nav" data-mobile-nav aria-label="Mobile navigation"></nav>
<section class="page-hero"><div class="page-hero-inner">{hero}</div></section>
<main class="page-shell" id="main-content">{main}</main>
<footer class="site-footer"><span>© 2026 Center of Modern Thought</span><a href="{rel(path, EN_BOOK_DIR+'index.html')}">{esc(SERIES_NAME)}</a></footer>
<script src="{root}site.js"></script>
</body>
</html>
'''


def catalogue(books, english):
    path = EN_BOOK_DIR + 'index.html'
    cards = []
    for book in books:
        en = english[book['id']]
        detail = book['id'] + '/index.html'
        cover = rel(path, BOOK_DIR + book['cover'].removeprefix('./').replace('covers/', 'thumbs/'))
        summary = en['description'] if len(en['description']) <= 190 else en['description'][:190].rsplit(' ', 1)[0] + '…'
        cards.append(f'''<article class="book-card en-book-card" data-book-id="{esc(book['id'])}">
<a class="book-cover book-cover-image" href="{detail}" tabindex="-1" aria-hidden="true"><img src="{cover}" alt="Cover of the Chinese edition: {esc(en['title'])}" loading="lazy" decoding="async"><span class="book-index">No. {book['number']:02d}</span></a>
<div class="book-card-body"><small><time datetime="{book['date'][:7]}">{published(book)}</time> · Chinese edition</small>
<h3><a class="book-detail-link" href="{detail}">{esc(en['title'])}</a></h3>
<p class="en-book-original" lang="zh-CN">{esc(book['title'])}</p>
<p class="book-meta">{role(book)} {named(en['authorDisplay'])}<br>Chinese translation by {named(en['translatorDisplay'])}</p>
<p class="book-summary">{esc(summary)}</p><div class="book-actions"><a href="{detail}">Read book details <span aria-hidden="true">→</span></a></div></div>
</article>''')
    hero = f'''<span class="page-kicker">A Chinese translation series</span><h1 class="page-title">{esc(SERIES_NAME)}</h1><p class="en-book-original" lang="zh-CN">西方思想文化译丛</p><p class="page-subtitle">Explore the {len(books)} Chinese-language volumes in this website catalogue, with English introductions and bibliographic details. Published by Fujian Education Press.</p>'''
    cards_html = '\n'.join(cards)
    main = f'''<section class="section-block"><h2>Browse the catalogue</h2><p class="en-books-note">English titles translate the Chinese titles; publication details refer to the Chinese editions. Volumes of multi-volume works are listed separately.</p><div class="catalog-grid" id="english-series-grid">{cards_html}</div></section>'''
    return shell(path, SERIES_NAME, hero, main)


def detail(book, en):
    path = EN_BOOK_DIR + book['id'] + '/index.html'
    zh_path = BOOK_DIR + book['id'] + '/index.html'
    cover = rel(path, BOOK_DIR + book['cover'].removeprefix('./'))
    hero = f'''<nav class="book-breadcrumb" aria-label="Breadcrumb"><a href="{rel(path, 'en/index.html')}">Home</a><span aria-hidden="true"> / </span><a href="../index.html">{esc(SERIES_NAME)}</a><span aria-hidden="true"> / </span><span>Entry {book['number']:02d}</span></nav><span class="page-kicker">Chinese edition · Entry {book['number']:02d}</span><h1 class="page-title">{esc(en['title'])}</h1><p class="en-book-original" lang="zh-CN">{esc(book['title'])}</p><p class="page-subtitle">{role(book)} {named(en['authorDisplay'])}. Chinese translation by {named(en['translatorDisplay'])}.</p>'''
    main = f'''<article class="book-detail-layout"><figure class="book-detail-cover"><img src="{cover}" alt="Cover of the Chinese edition: {esc(en['title'])}" decoding="async"><figcaption>Chinese edition · {published(book)}</figcaption></figure><div class="detail-card prose book-detail-copy"><p class="en-books-note">This English guide describes the Chinese edition. The heading is a translation of its Chinese title.</p><h2>About this volume</h2><p data-book-description>{esc(en['description'])}</p><h2>Publication details</h2><dl class="book-facts"><div><dt>Chinese title</dt><dd lang="zh-CN">{esc(book['title'])}</dd></div><div><dt>{'Editors' if book.get('creatorRole') == 'editor' else 'Author'}</dt><dd>{named(en['authorDisplay'])}</dd></div><div><dt>Chinese translation</dt><dd>{named(en['translatorDisplay'])}</dd></div><div><dt>Publisher</dt><dd>Fujian Education Press <span lang="zh-CN">（{esc(book['publisher'])}）</span></dd></div><div><dt>Published</dt><dd><time datetime="{book['date'][:7]}">{published(book)}</time></dd></div><div><dt>Edition language</dt><dd>Chinese</dd></div></dl><div class="cta-row"><a class="cta-button" href="../index.html">Back to the catalogue</a><a class="ghost-button" href="{rel(path, zh_path)}" lang="zh-CN">中文书目与简介 →</a></div></div></article>'''
    return shell(path, en['title'] + ' | ' + SERIES_NAME, hero, main)


def render_english_books(books, entries):
    if len({entry['id'] for entry in entries}) != len(entries):
        raise ValueError('English catalogue contains duplicate book IDs')
    english = {entry['id']: entry for entry in entries}
    if {book['id'] for book in books} != set(english):
        raise ValueError('English and Chinese catalogue IDs differ')
    chinese = {book['id']: book for book in books}
    for entry in entries:
        expected_hash = hashlib.sha256(chinese[entry['id']]['description'].encode('utf-8')).hexdigest()
        if entry.get('sourceDescriptionSha256') != expected_hash:
            raise ValueError('Chinese description changed; review English translation and update sourceDescriptionSha256: ' + entry['id'])
        if entry.get('titleKind') != 'website_translation':
            raise ValueError('English book titles require explicit website_translation provenance')
        if any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in ('title', 'description', 'authorDisplay', 'translatorDisplay')):
            raise ValueError('Missing English book content: ' + entry['id'])
    outputs = {EN_BOOK_DIR + 'index.html': catalogue(books, english)}
    outputs.update({EN_BOOK_DIR + book['id'] + '/index.html': detail(book, english[book['id']]) for book in books})
    return outputs
