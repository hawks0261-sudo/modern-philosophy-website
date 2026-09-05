#!/usr/bin/env python3
"""Focused regression tests for content propagation; never writes site files."""
import copy
import html
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch
import build_site


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
