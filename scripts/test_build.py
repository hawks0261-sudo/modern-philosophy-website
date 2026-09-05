#!/usr/bin/env python3
"""Focused regression tests for content propagation; never writes site files."""
import copy
import json
import re
import unittest
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
