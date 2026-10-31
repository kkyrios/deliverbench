#!/usr/bin/env python3
"""Check published numbers, local links, disclosure boundaries, and static assets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json, math, re
R = Path(__file__).resolve().parents[1]
D = R / 'dist'
results=json.loads((R/'data/results.json').read_text())
projects=json.loads((R/'data/projects.json').read_text())
assert len(results['systems']) == 7 and len(results['final_matrix']) == 11
assert len(projects) == 11 and sum(p['subtasks'] for p in projects)==150
assert len({r['project'] for r in results['final_matrix']}) == 11
for s in results['systems']:
    assert math.isclose(s['final'],sum(p[s['id']] for p in results['final_matrix'])/11,abs_tol=1e-10)
    assert math.isclose(s['pass_rate'],100*s['passed']/150,abs_tol=1e-10)
    assert 0 <= s['final'] <= 100
html=(D/'index.html').read_text()
class Audit(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='img':assert a.get('alt') is not None
        if tag in ['a','link','script','img']:
            url=a.get('href',a.get('src',''))
            if url:self.links.append(url)
        if tag=='a' and a.get('target')=='_blank':assert 'noopener' in a.get('rel','')
a=Audit();a.feed(html)
assert len(a.ids)==len(set(a.ids)), 'Duplicate ids'
for link in a.links:
    url=urlparse(link)
    if url.scheme or url.netloc:continue
    if url.path:assert (D/unquote(url.path)).is_file(),f'Missing asset: {link}'
    if not url.path and url.fragment:assert url.fragment in a.ids,f'Bad anchor: {link}'
for file in D.rglob('*'):
    if not file.is_file():continue
    assert file.suffix.lower() not in {'.pdf','.zip','.docx','.xlsx','.tex','.bib','.toml'},f'Unapproved publication: {file}'
    if file.suffix in {'.html','.js','.json','.css','.txt','.svg'}:
        text=file.read_text()
        assert not re.search(r'/Users/|feishu\.cn|overleaf\.com|wxid_|humanlaya-backup|sk-[A-Za-z0-9]{20}',text),f'Internal information: {file}'
assert '{{' not in html
assert (D/'assets/fonts/dm-sans-400.ttf').is_file()
for s in results['systems']:assert f'{s["final"]:.2f}' in html
assert 'Humanlaya Data' in html and 'Theseus Lab' in html
print('PASS: 7 leaderboard rows, 77 project scores, 11 project profiles, all local assets/anchors, and publication boundary.')

# The showcase is a versioned project example, separate from the results snapshot.
showcase=json.loads((R/'data/p02-showcase.json').read_text())
tasks={t['id']:t for t in showcase['tasks']}
assert list(tasks)==[f'T{i:02}' for i in range(1,14)] and len(showcase['tasks'])==13
assert showcase['version']=='3.1.0'
assert {t['phase'] for t in tasks.values()}=={1,2,3,4}
node_ids=set(tasks)|{'LENDER','FINAL'}
edges=showcase['edges']
assert len({(e['from'],e['to']) for e in edges})==len(edges), 'Duplicate dependency'
assert all(e['from'] in node_ids and e['to'] in node_ids for e in edges)
assert all(e['kind'] in {'artifact','context','feedback'} for e in edges)
assert {e['from'] for e in edges if e['to']=='LENDER'}=={'T05','T07','T10'}
assert {e['to'] for e in edges if e['from']=='LENDER'}=={'T11'}
visited=set()
def visit(node, trail):
    assert node not in trail, f'Cyclic project dependency: {node}'
    if node in visited:return
    for edge in edges:
        if edge['from']==node:visit(edge['to'],trail|{node})
    visited.add(node)
for node in node_ids:visit(node,set())
assert [(o['label'],o['from']) for o in showcase['deliverables']]==[
    ('Base-case model','T09'),('Assumptions memo','T09'),('Syndication update','T11'),
    ('Valuation summary','T12'),('Signature page','T13'),('Draft commitment letter','T13')]
for task in tasks:
    assert html.count(f'id="p02-{task}"')==1
    assert f'aria-label="Explore {task}:' in html
assert 'id="p02-LENDER"' in html and 'id="p02-FINAL"' in html
assert html.count('class="case-figure-card"')==4
assert html.index('id="project-example-title"') < html.index('id="cases-title"')
assert 'The final submitted package is evaluated independently' in html
assert 'earlier checkpoint scores remain unchanged' in html
print('PASS: P02 has 13 unique tasks, an acyclic graph, verified lender-feedback sources, six mapped outputs, and separate checkpoint/final evaluation.')
