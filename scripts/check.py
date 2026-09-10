"""Check generated routes, assets, translations and source-data coverage."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import datetime
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.images=[];self.lang=None;self.headings=[];self.main=0;self.title=False;self.description=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag=='img':self.images.append(a)
        if tag=='main':self.main+=1
        if tag=='h1':self.headings.append('h1')
        if tag=='title':self.title=True
        if tag=='meta' and a.get('name')=='description':self.description=True

files=list(ROOT.rglob('*.html'));pages={};errors=[];links=0
for f in files:
    p=Page();p.feed(f.read_text(encoding='utf8'));pages[f.resolve()]=p
    if p.lang not in ['ko','en']:errors.append(f'{f}: missing language')
    if p.main!=1 or len(p.headings)!=1:errors.append(f'{f}: expected one main and h1')
    if len(p.ids)!=len(set(p.ids)):errors.append(f'{f}: duplicate IDs')
    if not p.title:errors.append(f'{f}: missing title')
    if f.name!='404.html' and not p.description:errors.append(f'{f}: missing description')
    for image in p.images:
        if not image.get('alt'):errors.append(f'{f}: missing image alt')
        src=image.get('src','');target=ROOT/src.lstrip('/')
        if not target.is_file():errors.append(f'{f}: missing image {src}')
for f,p in pages.items():
    for href in p.links:
        links+=1;u=urlsplit(href)
        if u.scheme:
            if u.scheme not in ['https','mailto','tel']:errors.append(f'{f}: unexpected URL scheme {href}')
            continue
        target=(ROOT/unquote(u.path).lstrip('/')) if u.path.startswith('/') else (f.parent/unquote(u.path)) if u.path else f
        if target.is_dir():target=target/'index.html'
        if not target.exists():errors.append(f'{f}: broken route {href}')
        elif u.fragment and target.resolve() in pages and unquote(u.fragment) not in pages[target.resolve()].ids:errors.append(f'{f}: missing anchor {href}')
pr=json.loads((ROOT/'content/projects.json').read_text(encoding='utf8'));pub=json.loads((ROOT/'content/publications.json').read_text(encoding='utf8'));tr=json.loads((ROOT/'content/table-translations.json').read_text(encoding='utf8'))
if len(pr)!=13 or len(pub)!=33:errors.append('Content inventory changed unexpectedly')
domestic=[p for p in pub if p['group']=='domestic']
if len(domestic)!=13:errors.append('Expected 13 domestic conference papers')
if len({p['slug'] for p in pub})!=len(pub):errors.append('Duplicate publication slug')
publication_dates={}
for p in pub:
    try:
        date=datetime.strptime(p['date'],'%Y.%m' if '.' in p['date'] else '%Y')
        if date.year!=p['year']:errors.append('Publication year mismatch: '+p['slug'])
        publication_dates[p['slug']]=date
    except ValueError:errors.append('Publication date must use YYYY or YYYY.MM: '+p['slug'])
for p in domestic:
    if not all(p.get(k) for k in ['titleKo','venueEn','authors','figures','links']):errors.append('Incomplete domestic paper: '+p['slug'])
    position=int(p['role'][1])-1
    if p['authors']['ko'].split(', ')[position]!='김대현':errors.append('Author role mismatch: '+p['slug'])
for lang in ['', 'en/']:
    for group,rows in [('projects',pr),('publications',pub)]:
        for obj in rows:
            if not (ROOT/f'{lang}{group}/{obj["slug"]}/index.html').is_file():errors.append('Missing detail route: '+obj['slug'])
            else:
                html=(ROOT/f'{lang}{group}/{obj["slug"]}/index.html').read_text(encoding='utf8')
                breadcrumb=re.search(r'<nav class="breadcrumb".*?</nav>',html,re.S)
                if not breadcrumb or f'href="/{lang}{group}/"' not in breadcrumb.group():errors.append('Missing archive breadcrumb: '+lang+obj['slug'])
    archive=(ROOT/f'{lang}publications/index.html').read_text(encoding='utf8')
    listed=[]
    for group,body in re.findall(r'<section class="archive-group" id="([^"]+)">(.*?)</section>',archive,re.S):
        slugs=re.findall(r'<h3>\s*<a href="/(?:en/)?publications/([^/]+)/"',body)
        listed.extend(slugs)
        dates=[publication_dates[s] for s in slugs if s in publication_dates]
        if dates!=sorted(dates,reverse=True):errors.append('Publication archive is not newest first: '+lang+group)
    if sorted(listed)!=sorted(p['slug'] for p in pub):errors.append('Publication archive omits or duplicates papers: '+lang)
words=set()
for p in pr:
    for s in p['stages']:
        for tbl in s['tables']:
            words.update(c['text'] for row in tbl['rows'] for c in row)
        for c in s['charts']:
            words.add(c['title'])
            for series in c['series']:words.update(series['categories']+[series['name']])
for p in pub:
    for tbl in p.get('tables',[]):words.update(c['text'] for row in tbl['rows'] for c in row)
for word in words:
    if re.search('[가-힣]',word) and word not in tr:errors.append('Missing table/chart translation: '+word)
expected=2*(3+len(pr)+len(pub))+1
if len(files)!=expected:errors.append(f'Expected {expected} HTML documents, found {len(files)}')
result={'pages':len(files),'projects':len(pr),'publications':len(pub),'domestic_conference_papers':len(domestic),'internal_and_external_links_checked':links,'errors':errors}
print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(errors))
