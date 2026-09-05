"""Render the bilingual homepage scene from the verified three-person catalogue.

The scene image is artwork; profiles, labels, sources and book links are HTML.
Only the named Atheneum regions on the two homepages are generated here.
"""
from pathlib import Path
import html
import json
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    return html.escape(str(value), quote=True)


def link(path, target):
    return posixpath.relpath(target.lstrip('/'), posixpath.dirname(path) or '.')


def render_scene(path, people):
    en = path.startswith('en/')
    lang = 'en' if en else 'zh'
    t = lambda zh, english: english if en else zh
    chosen = next(p for p in people if p['id'] == 'berkeley')
    buttons = []
    tabs = []
    records = []
    for p in people:
        identity, name, short = p['id'], p['name'][lang], p['shortName'][lang]
        pressed = str(identity == 'berkeley').lower()
        buttons.append(f'''<button type="button" class="atheneum-figure atheneum-figure--{identity}" data-select-person="{identity}" aria-pressed="{pressed}" aria-controls="atheneum-card" aria-label="{esc(t('选择', 'Select ') + name)}">
  <span class="atheneum-nameplate"><strong>{esc(short)}</strong><small lang="en">{esc(p['name']['en'])}</small></span>
</button>''')
        tabs.append(f'<button type="button" data-select-person="{identity}" aria-pressed="{pressed}" aria-controls="atheneum-card">{esc(short)}</button>')
        works = ''.join(f'<li>{esc(w[lang])} <span>({esc(w["year"])})</span></li>' for w in p['works'])
        related = []
        for item in p['relatedLinks']:
            target = item.get('hrefEn') if en else item['href']
            suffix = ''
            if not target:
                target = item['href']
                suffix = ' (Chinese)'
            related.append(f'<li><a href="{esc(link(path, target))}">{esc(item["label"][lang] + suffix)}</a></li>')
        related_html = f'<h3>{t("本站研究与出版", "Related research and publications")}</h3><ul>{"".join(related)}</ul>' if related else ''
        portrait = p['portrait']
        attribution = f'<details><summary>{t("肖像说明", "About this portrait")}</summary><p>{esc(portrait["attributionNote"][lang])}</p></details>'
        records.append(f'''<article class="atheneum-record" data-person-record="{identity}" {'hidden' if identity != 'berkeley' else ''}>
  <figure><img src="{link(path, portrait['image'])}" alt="{esc(portrait['sourceLabel'][lang])}" width="500" height="679" loading="lazy" decoding="async"><figcaption>{esc(portrait['caption'][lang])}<br><a href="{esc(portrait['sourceUrl'])}" target="_blank" rel="noopener">{t('查看馆藏或图像目录', 'View the portrait catalogue')}</a></figcaption></figure>
  <div><h2 id="person-title-{identity}">{esc(name)}</h2><p class="record-years">{esc(p['name']['en']) + ' · ' if not en else ''}{p['years']}</p>
    <p>{esc(p['bio'][lang])}</p><p class="record-themes">{' · '.join(esc(theme[lang]) for theme in p['themes'])}</p>
    <h3>{t('代表著作', 'Selected works')}</h3><ul>{works}</ul>{related_html}
    <a class="record-source" href="{esc(p['sources'][0]['url'])}" target="_blank" rel="noopener">{t('人物与著作资料：斯坦福哲学百科', 'Profile and works: Stanford Encyclopedia of Philosophy')}</a>
    {attribution}<p class="reconstruction-note">{t('殿堂中的人物为依据历史肖像创作的艺术形象；左侧展示其肖像依据。', 'The figure in the hall is an artistic reconstruction. The source portrait is shown alongside this profile.')}</p>
  </div>
</article>''')
    # This is public display data only; build-machine paths are never embedded.
    state = [{k: p[k] for k in ('id', 'name', 'years', 'themes', 'portrait', 'sources')} for p in people]
    return f'''<section class="atheneum-scene" aria-labelledby="atheneum-title">
  <div class="atheneum-heading"><h1 id="atheneum-title">{t('在思想之间，展开对话。', 'A conversation<br>across centuries.')}</h1><p>{t('以史照今，以今返史', 'Reading history. Thinking forward.')}</p></div>
  <div class="atheneum-world">
    <img class="atheneum-backdrop" src="{link(path, 'assets/optimized/7541e7aea1e0-1439.webp')}" srcset="{link(path, 'assets/optimized/7541e7aea1e0-768.webp')} 768w, {link(path, 'assets/optimized/7541e7aea1e0-1439.webp')} 1439w" sizes="100vw" width="1786" height="881" fetchpriority="high" loading="eager" decoding="async" alt="{t('古老殿堂中的笛卡尔、康德与贝克莱，依据历史肖像创作', 'Descartes, Kant and Berkeley in a historical hall, interpreted from their portraits')}" draggable="false">
    {''.join(buttons)}
  </div>
  <div class="atheneum-mobile-tabs" role="group" aria-label="{t('选择哲学家', 'Choose a philosopher')}">{''.join(tabs)}</div>
  <aside class="atheneum-card" id="atheneum-card" aria-label="{t('当前人物', 'Selected philosopher')}">
    <div class="person-summary" aria-live="polite" aria-atomic="true"><h2>{esc(chosen['name'][lang])}</h2><p class="person-years">{chosen['years']}</p><p class="person-themes">{' · '.join(esc(theme[lang]) for theme in chosen['themes'])}</p></div>
    <button class="atheneum-button" type="button" data-open-person aria-haspopup="dialog" aria-controls="atheneum-detail">{t('阅读人物介绍', 'Read profile')}</button>
    <a class="person-source" href="{esc(chosen['portrait']['sourceUrl'])}" target="_blank" rel="noopener">{t('肖像来源', 'Portrait source')}</a>
  </aside>
  <div class="atheneum-tools"><span class="atheneum-hint">{t('拖动查看 · 点击人物', 'Drag to look · Select a philosopher')}</span><button class="atheneum-motion" type="button" aria-pressed="true">{t('暂停景深', 'Pause motion')}</button></div>
</section>
<noscript><p class="atheneum-nojs">{t('阅读人物资料：', 'Read about the philosophers:')}{''.join(f'<a href="{esc(p["sources"][0]["url"])}">{esc(p["name"][lang])}</a>' for p in people)}</p></noscript>
<dialog class="atheneum-detail" id="atheneum-detail" aria-labelledby="person-title-berkeley">
  <div class="atheneum-detail-toolbar"><p>{t('人物 · 著作 · 肖像', 'Profile · Works · Portrait')}</p><button type="button" data-close-person autofocus>{t('关闭', 'Close')}</button></div>{''.join(records)}
</dialog>
<script id="atheneum-profiles" type="application/json">{json.dumps(state, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>'''


def render_featured(path, events, books, english_books, page_titles):
    en = path.startswith('en/')
    t = lambda zh, english: english if en else zh
    recent = sorted(events, key=lambda event: (event['startDate'], event['id']), reverse=True)[:3]
    rows = []
    for event in recent:
        target = event['path']
        title = esc(event['title'])
        language_attr = ''
        if en:
            translated_path = 'en/' + target
            translated_title = page_titles.get(translated_path)
            if translated_title:
                target, title = translated_path, esc(translated_title)
            else:
                title = f'<span lang="zh-CN">{title}</span> (Chinese)'
                language_attr = ' hreflang="zh-CN"'
        rows.append(f'<li><a href="{link(path, target)}"{language_attr}>{title}</a><time datetime="{event["startDate"]}">{event["startDate"].replace("-", ".")}</time></li>')
    book_imgs = []
    books_by_id = {book['id']: book for book in books}
    for number in ('25', '27', '29'):
        identity = 'series-' + number
        if identity not in books_by_id:
            continue
        book = books_by_id[identity]
        title = english_books[identity]['title'] if en else book['title']
        target = ('en/' if en else '') + f'publications/translation-series/{identity}/index.html'
        cover = 'publications/translation-series/' + book['cover'].removeprefix('./')
        book_imgs.append(f'<a href="{link(path, target)}"><img src="{link(path, cover)}" alt="{esc(title)}" data-home-shelf width="640" height="640" loading="lazy" decoding="async"></a>')
    journal = 'en/publications/journal/index.html' if en else 'publications/journal/issue-01/index.html'
    catalogue = ('en/' if en else '') + 'publications/translation-series/index.html'
    return f'''<section class="atheneum-featured" id="atheneum-content" tabindex="-1" aria-label="{t('中心动态与学术出版', 'News and scholarly publications')}">
  <article><h2>{t('中心动态', 'From the center')}</h2><ol class="atheneum-news-list">{''.join(rows)}</ol><a class="atheneum-inline-link" href="{link(path, ('en/' if en else '') + 'activities/index.html')}">{t('查看全部学术活动', 'All academic activities')}</a></article>
  <article><h2>{t('研究与出版', 'Research and publishing')}</h2><div class="atheneum-journal"><div><h3>{t('《近代哲学》第一期', 'Modern Philosophy · Issue 1')}</h3><p>{t('贝克莱作品的编纂和影响', 'George Berkeley’s Works and Legacy')}<br>2026 · {t('福建教育出版社', 'Fujian Education Press')}</p><a class="atheneum-button" href="{link(path, journal)}">{t('查看期刊', 'Explore the issue')}</a></div><a href="{link(path, journal)}" tabindex="-1" aria-hidden="true"><img src="{link(path, 'assets/optimized/b389b1633c2b-384.webp')}" alt="{t('《近代哲学》第一期书封', 'Cover of Modern Philosophy, Issue 1')}" width="1280" height="1636" loading="lazy" decoding="async"></a></div></article>
  <article class="atheneum-series"><h2>{t('西方思想文化译丛', 'Western Thought &amp; Culture Library')}</h2>{'<p class="series-english" lang="en">Western Thought &amp; Culture Library</p>' if not en else ''}<div class="atheneum-book-row">{''.join(book_imgs)}</div><p>{t('译介经典，推动思想对话。本站收录', 'Translations for an ongoing conversation. Explore')} <span data-stat="books">{len(books)}</span> {t('册图书。', 'volumes.')}</p><a class="atheneum-inline-link" href="{link(path, catalogue)}">{t('浏览全部书目', 'Browse the library')}</a></article>
</section>'''


def normalize_atheneum(text, path, events, books, english_books, page_titles):
    if path not in ('index.html', 'en/index.html') or 'BEGIN GENERATED: atheneum-scene' not in text:
        return text
    data = json.loads((ROOT / 'data/atheneum.json').read_text(encoding='utf-8'))
    regions = {'atheneum-scene': render_scene(path, data['philosophers']), 'atheneum-featured': render_featured(path, events, books, english_books, page_titles)}
    for name, contents in regions.items():
        pattern = r'(<!-- BEGIN GENERATED: ' + name + r' -->).*?(<!-- END GENERATED: ' + name + r' -->)'
        text = re.sub(pattern, lambda m: m.group(1) + '\n' + contents + '\n' + m.group(2), text, flags=re.S)
    return text
