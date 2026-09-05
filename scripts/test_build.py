#!/usr/bin/env python3
"""Focused regression tests for content propagation; never writes site files."""
import copy
import html
import hashlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import build_site
from atheneum_home import render_scene
from site_theme import normalize_theme


class ProfileMarkup(HTMLParser):
    """Collect generated controls and profile descendants without a browser."""
    def __init__(self):
        super().__init__()
        self.elements = []
        self.record = None

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == 'article' and 'data-person-record' in attributes:
            self.record = attributes['data-person-record']
        self.elements.append((tag, attributes, self.record))

    def handle_endtag(self, tag):
        if tag == 'article':
            self.record = None


class GenerationTests(unittest.TestCase):
    def changed_build(self, name, change):
        original_load = build_site.load
        def load(filename):
            value = copy.deepcopy(original_load(filename))
            if filename == name:
                change(value)
            return value
        with patch.object(build_site, 'load', side_effect=load):
            return build_site.build()

    def test_event_change_reaches_home_archive_and_future_year_filter(self):
        def change(events):
            event = next(e for e in events if e['id'] == 'seminar-09')
            event.update(summary='Propagation test: one source, two lists.', startDate='2027-08-06', endDate='2027-08-06', dateLabel='2027.08.06')
        outputs = self.changed_build('events.json', change)
        for path in ('index.html', 'activities/index.html'):
            self.assertIn('Propagation test: one source, two lists.', outputs[path])
        archive = outputs['activities/index.html']
        self.assertIn('id="filter-year-2027"', archive)
        self.assertIn('for="filter-year-2027"', archive)
        self.assertIn('#filter-year-2027:checked ~ .archive-grid', archive)
        self.assertIn('#filter-type-lecture:checked ~ #filter-year-2027:checked ~ .archive-empty', archive)
        self.assertIn('"startDate": "2027-08-06"', outputs['activities/seminar-09/index.html'])

    def test_book_change_reaches_catalogue_detail_and_json_without_markup_injection(self):
        title = 'Test <script>alert(1)</script> & "book"'
        outputs = self.changed_build('books.json', lambda books: books[0].update(title=title))
        for path in ('publications/translation-series/index.html', 'publications/translation-series/series-01/index.html'):
            text = outputs[path]
            self.assertIn('Test &lt;script&gt;alert(1)&lt;/script&gt; &amp; &quot;book&quot;', text)
            self.assertNotIn('<script>alert(1)</script>', text)
            self.assertIn('\\u003cscript>', text)
        detail = outputs['publications/translation-series/series-01/index.html']
        data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', detail, re.S).group(1))
        book = next(item for item in data['@graph'] if item['@type'] == 'Book')
        self.assertEqual(book['name'], title)
        self.assertEqual(book['datePublished'], '2013-10')

    def test_fallback_language_is_not_an_equivalence_claim(self):
        config = build_site.load('site.json')
        paths = set(build_site.build())
        zh, en, paired = build_site.languages('people/member-directory/li-daiwei/index.html', config, paths)
        self.assertEqual(en, 'en/people/index.html')
        self.assertFalse(paired)
        self.assertEqual(build_site.languages('activities/seminar-09/index.html', config, paths), ('activities/seminar-09/index.html', 'en/activities/seminar-09/index.html', True))

    def test_english_book_has_direct_language_pair_and_describes_chinese_edition(self):
        config = build_site.load('site.json')
        outputs = build_site.build()
        zh = 'publications/translation-series/series-01/index.html'
        en = 'en/' + zh
        self.assertEqual(build_site.languages(zh, config, set(outputs)), (zh, en, True))
        self.assertEqual(build_site.languages(en, config, set(outputs)), (zh, en, True))
        self.assertIn('The heading is a translation of its Chinese title.', outputs[en])
        graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', outputs[en], re.S).group(1))['@graph']
        book = next(item for item in graph if item['@type'] == 'Book')
        page = next(item for item in graph if item['@type'] == 'WebPage')
        self.assertEqual(book['inLanguage'], 'zh-CN')
        self.assertEqual(page['inLanguage'], 'en')
        self.assertEqual(book['name'], build_site.load('books.json')[0]['title'])
        self.assertEqual(book['url'], config['base_url'] + zh)

    def test_changed_chinese_description_requires_english_review(self):
        with self.assertRaisesRegex(ValueError, 'review English translation'):
            self.changed_build('books.json', lambda books: books[0].update(description=books[0]['description'] + ' Updated source.'))

    def test_base_url_change_reaches_sitemap_and_canonical(self):
        base = 'https://example.org/review/'
        outputs = self.changed_build('site.json', lambda config: config.update(base_url=base))
        self.assertIn('<loc>' + base + 'index.html</loc>', outputs['sitemap.xml'])
        self.assertIn('rel="canonical" href="' + base + 'publications/translation-series/series-01/index.html"', outputs['publications/translation-series/series-01/index.html'])

    def test_new_book_count_reaches_both_atheneum_homepages(self):
        original_load = build_site.load
        expected_count = len(original_load('books.json')) + 1
        def load(filename):
            value = copy.deepcopy(original_load(filename))
            if filename in ('books.json', 'books-en.json'):
                added = copy.deepcopy(value[0])
                added['id'] = 'series-30'
                if filename == 'books.json':
                    added['number'] = 30
                value.append(added)
            return value
        with patch.object(build_site, 'load', side_effect=load):
            outputs = build_site.build()
        for path in ('index.html', 'en/index.html'):
            counts = re.findall(r'data-stat="books">(\d+)', outputs[path])
            self.assertTrue(counts)
            self.assertEqual(set(counts), {str(expected_count)})

    def test_atheneum_english_event_title_follows_existing_english_page(self):
        original_read = Path.read_text
        source = build_site.ROOT / 'en/activities/seminar-09/index.html'
        title = 'A revised heading: editions & correspondence'
        def read(path, *args, **kwargs):
            text = original_read(path, *args, **kwargs)
            if path == source:
                text = re.sub(r'(<h1\b[^>]*>).*?(</h1>)', lambda m: m.group(1) + html.escape(title) + m.group(2), text, count=1, flags=re.S)
            return text
        with patch.object(Path, 'read_text', new=read):
            outputs = build_site.build()
        self.assertIn('<a href="activities/seminar-09/index.html">' + html.escape(title) + '</a>', outputs['en/index.html'])

    def test_atheneum_english_event_without_translation_is_marked_chinese(self):
        def change(events):
            event = next(e for e in events if e['id'] == 'seminar-06')
            event.update(title='待译活动 <新标题>', startDate='2027-01-01', endDate='2027-01-01')
        outputs = self.changed_build('events.json', change)
        self.assertIn('<a href="../activities/seminar-06/index.html" hreflang="zh-CN"><span lang="zh-CN">待译活动 &lt;新标题&gt;</span> (Chinese)</a>', outputs['en/index.html'])

    def test_atheneum_book_link_names_follow_bilingual_catalogue_titles(self):
        for filename, path, title in (
            ('books.json', 'index.html', '新版《贝克莱的世界》 & "书名"'),
            ('books-en.json', 'en/index.html', 'A revised Berkeley title & "edition"'),
        ):
            def change(books):
                next(book for book in books if book['id'] == 'series-25')['title'] = title
            outputs = self.changed_build(filename, change)
            row = re.search(r'<div class="atheneum-book-row">(.*?)</div>', outputs[path], re.S).group(1)
            self.assertIn('alt="' + html.escape(title, quote=True) + '"', row)
            self.assertNotIn('alt="Library volume ', row)
            self.assertNotIn('alt="译丛书目 ', row)

    def test_all_philosophers_have_matching_controls_records_and_portraits(self):
        source = build_site.ROOT / 'data/atheneum.json'
        original_read = Path.read_text
        catalogue = build_site.load('atheneum.json')
        changed = copy.deepcopy(catalogue)
        # Change size, order and names so fixed reader counts or labels cannot pass.
        removed = next(p['id'] for p in changed['philosophers'] if p['id'] != 'berkeley')
        changed['philosophers'] = [p for p in reversed(changed['philosophers']) if p['id'] != removed]
        for person in changed['philosophers']:
            person['shortName'] = {language: name + ' <reader> & "label"' for language, name in person['shortName'].items()}

        for case, data in (('current catalogue', catalogue), ('reordered subset', changed)):
            people = data['philosophers']
            identities = [person['id'] for person in people]
            self.assertEqual(len(identities), len(set(identities)))
            def read(path, *args, **kwargs):
                return json.dumps(data, ensure_ascii=False) if path == source else original_read(path, *args, **kwargs)
            with patch.object(Path, 'read_text', new=read):
                outputs = build_site.build()
            for path, language in (('index.html', 'zh'), ('en/index.html', 'en')):
                with self.subTest(case=case, path=path):
                    text = outputs[path]
                    parser = ProfileMarkup()
                    parser.feed(text)
                    tags = parser.elements
                    state = json.loads(re.search(r'<script\b[^>]*id="atheneum-profiles"[^>]*>(.*?)</script>', text, re.S).group(1))
                    self.assertEqual([person['id'] for person in state], identities)
                    self.assertEqual([person['shortName'] for person in state], [person['shortName'] for person in people])
                    records = [attrs for tag, attrs, _ in tags if 'data-person-record' in attrs]
                    self.assertCountEqual([attrs['data-person-record'] for attrs in records], identities)
                    visible = [attrs['data-person-record'] for attrs in records if 'hidden' not in attrs]
                    self.assertEqual(len(visible), 1)
                    controls = [attrs for tag, attrs, _ in tags if tag == 'button' and 'data-select-person' in attrs]
                    ids = [attrs['id'] for _, attrs, _ in tags if 'id' in attrs]
                    for is_hotspot, target in ((True, 'atheneum-detail'), (False, 'atheneum-card')):
                        group = [attrs for attrs in controls if ('atheneum-figure' in attrs.get('class', '').split()) == is_hotspot]
                        self.assertEqual(Counter(attrs['data-select-person'] for attrs in group), Counter(identities))
                        for control in group:
                            self.assertEqual(control['aria-controls'], target)
                            self.assertIn(target, ids)
                            self.assertEqual(control['aria-pressed'], str(control['data-select-person'] == visible[0]).lower())
                            if is_hotspot:
                                self.assertEqual(control.get('aria-haspopup'), 'dialog')
                    picker_labels = re.findall(r'<button\b(?=[^>]*data-select-person="([^"]+)")(?=[^>]*aria-controls="atheneum-card")[^>]*>(.*?)</button>', text, re.S)
                    self.assertEqual(dict(picker_labels), {p['id']: html.escape(p['shortName'][language], quote=True) for p in people})
                    chosen = next(person for person in people if person['id'] == visible[0])
                    reader_name = re.findall(r'<strong\b[^>]*data-reader-name[^>]*>(.*?)</strong>', text, re.S)
                    self.assertEqual(reader_name, [html.escape(chosen['shortName'][language], quote=True)])
                    reader_count = re.findall(r'<span\b[^>]*data-reader-count[^>]*>(.*?)</span>', text, re.S)
                    self.assertEqual(len(reader_count), 1)
                    self.assertEqual(re.findall(r'\d+', reader_count[0]), [str(identities.index(visible[0]) + 1), str(len(people))])
                    dialog = next(attrs for tag, attrs, _ in tags if tag == 'dialog' and attrs.get('id') == 'atheneum-detail')
                    self.assertEqual(dialog['aria-labelledby'], 'person-title-' + visible[0])
                    for person in people:
                        self.assertEqual(ids.count('person-title-' + person['id']), 1)
                        portrait = next(attrs for tag, attrs, owner in tags if tag == 'img' and owner == person['id'])
                        resolved = (build_site.ROOT / Path(path).parent / portrait['src']).resolve()
                        self.assertTrue(resolved.is_file(), str(resolved))
                        portrait_source = portrait.get('data-media-source')
                        if portrait_source:
                            self.assertEqual(portrait_source, person['portrait']['image'])
                        else:
                            self.assertEqual(resolved, (build_site.ROOT / person['portrait']['image']).resolve())

    def test_philosopher_directory_stays_collapsed_as_catalogue_grows(self):
        people = build_site.load('atheneum.json')['philosophers']
        expanded = copy.deepcopy(people)
        # Exercise dozens of entries without tying the control count to seven.
        for number in range(25):
            person = copy.deepcopy(people[0])
            person['id'] = 'added-philosopher-' + str(number)
            expanded.append(person)
        for catalogue in (people, expanded):
            for path, label, hint in (
                ('index.html', '选择哲学家', '选择人物，走近他的思想'),
                ('en/index.html', 'Choose a philosopher', 'Choose a philosopher to explore their ideas'),
            ):
                with self.subTest(path=path, count=len(catalogue)):
                    text = render_scene(path, catalogue)
                    parser = ProfileMarkup()
                    parser.feed(text)
                    choosers = [attrs for tag, attrs, _ in parser.elements
                                if tag == 'details' and 'atheneum-chooser' in attrs.get('class', '').split()]
                    self.assertEqual(len(choosers), 1)
                    self.assertNotIn('open', choosers[0])
                    chooser = re.search(r'<details\b[^>]*class="atheneum-chooser"[^>]*>(.*?)</details>', text, re.S).group(1)
                    self.assertIn('<summary>' + label, chooser)
                    self.assertIn('aria-label="' + label + '"', chooser)
                    self.assertEqual(re.findall(r'class="atheneum-chooser-count">(\d+)</span>', chooser), [str(len(catalogue))])
                    # Every alternate selection entry belongs to the disclosure;
                    # an accidentally restored permanent row must fail this test.
                    directory_ids = re.findall(r'data-select-person="([^"]+)"', chooser)
                    self.assertEqual(directory_ids, [person['id'] for person in catalogue])
                    remaining = text.replace(chooser, '', 1)
                    self.assertNotIn('class="atheneum-person-picker"', remaining)
                    self.assertNotIn('aria-controls="atheneum-card"', remaining)
                    self.assertEqual(re.findall(r'class="atheneum-hint">([^<]+)</span>', text), [hint])

    def test_philosopher_work_date_notes_propagate_in_each_language_safely(self):
        original_read = Path.read_text
        source = build_site.ROOT / 'data/atheneum.json'
        data = json.loads(original_read(source))
        # Change a note belonging to an added philosopher, retaining other notes.
        person = next(p for p in data['philosophers'] if p['id'] == 'leibniz')
        person['works'][0]['dateNote'] = {
            'zh': '写成 <年份> 与首刊不同 & "需区分"',
            'en': 'Composition <date> differs from publication & "needs context"',
        }
        def read(path, *args, **kwargs):
            return json.dumps(data, ensure_ascii=False) if path == source else original_read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', new=read):
            outputs = build_site.build()
        for path, language in (('index.html', 'zh'), ('en/index.html', 'en')):
            text = outputs[path]
            expected_notes = [work['dateNote'][language] for p in data['philosophers'] for work in p['works'] if work.get('dateNote', {}).get(language)]
            emitted_notes = re.findall(r'<small\b[^>]*class="work-date-note"[^>]*>(.*?)</small>', text, re.S)
            self.assertCountEqual(emitted_notes, [html.escape(note, quote=True) for note in expected_notes])
            self.assertNotIn(person['works'][0]['dateNote'][language], text)

    def test_theme_normalization_is_idempotent_and_preserves_content_media(self):
        content_image = '<img src="photos/non-logo.png" alt="Research image" width="900" loading="lazy">'
        metadata = '<meta property="og:image" content="https://example.org/logo.png">'
        source = ('<html><head><link rel="stylesheet" href="old/site.css"><style>.local { color: red; }</style>' + metadata +
                  '</head><body class="english-page atheneum-page" id="top"><header>'
                  '<img src="old/optimized.webp" data-media-source="logo.png" srcset="old/large.webp 96w" sizes="42px" alt="Center &amp; research">'
                  '<img src="../logo.png?v=1" alt="Original logo"></header><main>' + content_image + '</main></body></html>')
        for path in ('index.html', 'en/index.html', 'activities/index.html', 'en/publications/translation-series/series-25/index.html'):
            with self.subTest(path=path):
                text = normalize_theme(source, path)
                self.assertEqual(normalize_theme(text, path), text)
                self.assertIn(content_image, text)
                self.assertIn(metadata, text)
                self.assertIn('<style>.local { color: red; }</style>', text)
                parser = ProfileMarkup()
                parser.feed(text)
                attrs = next(attrs for tag, attrs, _ in parser.elements if tag == 'body')
                self.assertIn('english-page', attrs['class'].split())
                self.assertEqual(attrs['class'].split().count('atheneum-page'), int(path not in ('index.html', 'en/index.html')))
                logos = [attrs for tag, attrs, _ in parser.elements if tag == 'img' and attrs.get('data-media-source') == 'assets/brand/logo-heritage.svg']
                self.assertEqual(len(logos), 2)
                for logo in logos:
                    self.assertEqual((build_site.ROOT / Path(path).parent / logo['src']).resolve(), build_site.ROOT / 'assets/brand/logo-heritage.svg')
                    self.assertEqual((logo['width'], logo['height'], logo['loading']), ('647', '726', 'eager'))
                    self.assertNotIn('srcset', logo)
                    self.assertNotIn('sizes', logo)

    def test_shared_theme_reaches_all_pages_and_survives_rebuilding(self):
        outputs = build_site.build()
        expected_pages = {p.relative_to(build_site.ROOT).as_posix() for p in build_site.ROOT.rglob('*.html')
                          if not any(part.startswith('.') or part in ('node_modules', 'output') for part in p.relative_to(build_site.ROOT).parts)}
        self.assertEqual({path for path in outputs if path.endswith('.html')}, expected_pages)
        original_read = Path.read_text
        def read(path, *args, **kwargs):
            relative = path.relative_to(build_site.ROOT).as_posix() if path.is_relative_to(build_site.ROOT) else None
            return outputs[relative] if relative in outputs else original_read(path, *args, **kwargs)
        with patch.object(Path, 'read_text', new=read):
            rebuilt = build_site.build()
            books_only = build_site.build(books_only=True)
        self.assertEqual(rebuilt, outputs)
        book_pages = {'publications/translation-series/index.html', 'en/publications/translation-series/index.html'}
        book_pages.update(prefix + f'publications/translation-series/{book["id"]}/index.html' for prefix in ('', 'en/') for book in build_site.load('books.json'))
        self.assertEqual(set(books_only), book_pages)
        for mode, pages in (('all', outputs), ('books only', books_only)):
            for path, text in pages.items():
                if not path.endswith('.html'):
                    continue
                with self.subTest(mode=mode, path=path):
                    parser = ProfileMarkup()
                    parser.feed(text)
                    head = text.split('</head>', 1)[0]
                    stylesheets = [attrs for tag, attrs, _ in parser.elements if tag == 'link' and attrs.get('rel') == 'stylesheet']
                    theme_links = [attrs for attrs in stylesheets if attrs.get('data-generated') == 'site-theme']
                    expected_styles = ['atheneum-brand.css'] + ([] if path in ('index.html', 'en/index.html') else ['atheneum-pages.css'])
                    resolved_styles = [(build_site.ROOT / Path(path).parent / urlsplit(attrs['href']).path).resolve() for attrs in theme_links]
                    self.assertEqual(resolved_styles, [build_site.ROOT / name for name in expected_styles])
                    self.assertEqual(stylesheets[-len(theme_links):], theme_links)
                    for attrs in theme_links:
                        self.assertIn('href="' + attrs['href'] + '"', head)
                    body = next(attrs for tag, attrs, _ in parser.elements if tag == 'body')
                    self.assertEqual(body.get('class', '').split().count('atheneum-page'), int(path not in ('index.html', 'en/index.html')))
                    images = [attrs for tag, attrs, _ in parser.elements if tag == 'img']
                    self.assertFalse(any(attrs.get('data-media-source') == 'logo.png' for attrs in images))
                    logos = [attrs for attrs in images if attrs.get('data-media-source') == 'assets/brand/logo-heritage.svg']
                    self.assertTrue(logos)
                    for logo in logos:
                        self.assertEqual((build_site.ROOT / Path(path).parent / logo['src']).resolve(), build_site.ROOT / 'assets/brand/logo-heritage.svg')
                        self.assertEqual((logo['width'], logo['height'], logo['loading']), ('647', '726', 'eager'))
                        self.assertNotIn('srcset', logo)
                        self.assertNotIn('sizes', logo)

    def test_asset_versions_refresh_generated_pages_when_file_content_changes(self):
        assets = ('site.css', 'atheneum-pages.css', 'atheneum-scene.css', 'atheneum.js')
        original_read = Path.read_bytes

        def references(outputs):
            found = {asset: {} for asset in assets}
            for path, text in outputs.items():
                if not path.endswith('.html'):
                    continue
                parser = ProfileMarkup()
                parser.feed(text)
                for tag, attrs, _ in parser.elements:
                    value = attrs.get('src' if tag == 'script' else 'href', '')
                    url = urlsplit(value)
                    target = (build_site.ROOT / Path(path).parent / url.path).resolve()
                    for asset in assets:
                        if tag in ('link', 'script') and not url.scheme and target == build_site.ROOT / asset:
                            found[asset][path] = value
            return found

        before = references(build_site.build())
        for asset in assets:
            with self.subTest(asset=asset):
                source = build_site.ROOT / asset
                new_content = original_read(source) + b'\n/* Updated asset content */\n'
                def read(path):
                    return new_content if path == source else original_read(path)
                with patch.object(Path, 'read_bytes', new=read):
                    after = references(build_site.build())
                self.assertTrue(before[asset])
                self.assertEqual(before[asset].keys(), after[asset].keys())
                for page, old_url in before[asset].items():
                    updated = urlsplit(after[asset][page])
                    self.assertEqual(updated.path, urlsplit(old_url).path)
                    self.assertNotEqual(after[asset][page], old_url)
                    self.assertEqual(parse_qs(updated.query)['v'], [hashlib.sha256(new_content).hexdigest()[:12]])
                for unchanged in set(assets) - {asset}:
                    self.assertEqual(after[unchanged], before[unchanged])

    def test_asset_versioning_preserves_paths_other_queries_and_external_urls(self):
        external = '<script src="https://example.org/atheneum.js?v=external"></script>'
        source = ('<html><head><link rel="stylesheet" href="../site.css?theme=sepia%20ink&amp;v=old&amp;flag#print">'
                  '<link rel="stylesheet" href="../atheneum-pages.css?custom=%2F&amp;v=old#paper">'
                  '</head><body><script defer src="../atheneum.js?mode=reader&amp;v=old#start"></script>' + external + '</body></html>')
        text = normalize_theme(source, 'people/index.html')
        self.assertEqual(normalize_theme(text, 'people/index.html'), text)
        self.assertIn(external, text)
        parser = ProfileMarkup()
        parser.feed(text)
        urls = {urlsplit(value).path: urlsplit(value) for tag, attrs, _ in parser.elements
                for value in [attrs.get('src' if tag == 'script' else 'href', '')]
                if value and not urlsplit(value).scheme}
        self.assertEqual(urls['../site.css'].query.split('&')[:-1], ['theme=sepia%20ink', 'flag'])
        self.assertEqual(urls['../site.css'].fragment, 'print')
        self.assertEqual(urls['../atheneum-pages.css'].query.split('&')[:-1], ['custom=%2F'])
        self.assertEqual(urls['../atheneum-pages.css'].fragment, 'paper')
        self.assertEqual(urls['../atheneum.js'].query.split('&')[:-1], ['mode=reader'])
        self.assertEqual(urls['../atheneum.js'].fragment, 'start')


if __name__ == '__main__':
    unittest.main(verbosity=2)
