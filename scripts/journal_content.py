"""Generate both language contents lists from the verified first-issue record."""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def normalize_journal(text, relative):
    if str(relative) not in ('publications/journal/issue-01/index.html', 'en/publications/journal/index.html'):
        return text
    data = json.loads((ROOT / 'data/journal-issue-01.json').read_text())
    english = str(relative).startswith('en/')
    parts = []
    for index, group in enumerate(data['groups']):
        if english:
            parts.append('<section class="section-block"><h3>' + escape(group['titleEn']) + '</h3><ol class="overview-events">')
        else:
            parts.append(f'<section class="section-card section-block toc-section" aria-labelledby="toc-group-{index}"><h2 id="toc-group-{index}">' + escape(group['title']) + '</h2><ol class="toc-list">')
        for entry in group['entries']:
            number = entry['page']
            if english:
                parts.append(f'<li id="page-{number}"><span class="page-kicker">Page {number}</span><h3>' + escape(entry['titleEn']) + '</h3><p>' + escape(entry['contributorsEn']) + '</p><p lang="zh-CN" class="language-original">' + escape(entry['title']) + ' · ' + escape(entry['contributors']) + f'</p><a href="../../../publications/journal/issue-01/index.html#page-{number:03d}" lang="zh-CN">Chinese contents entry →</a></li>')
            else:
                parts.append(f'<li class="toc-entry" id="page-{number:03d}"><span class="toc-page" aria-label="第 {number} 页">{number:03d}</span><div><h3><a href="#page-{number:03d}">' + escape(entry['title']) + '</a></h3><p>' + escape(entry['contributors']) + '</p></div></li>')
        parts.append('</ol></section>')
    begin = '<!-- BEGIN GENERATED: journal-toc -->'
    end = '<!-- END GENERATED: journal-toc -->'
    if begin not in text or end not in text:
        raise ValueError('Missing journal contents markers: ' + str(relative))
    return re.sub(re.escape(begin) + r'.*?' + re.escape(end), lambda _: begin + '\n' + '\n'.join(parts) + '\n' + end, text, flags=re.S)
