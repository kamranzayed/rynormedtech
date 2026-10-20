"""Cross-page catalogue checks, using only Python's standard library."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,urlencode
from hashlib import sha256
import json,re
ROOT=Path(__file__).resolve().parents[1]
products=json.loads((ROOT/'content/products.json').read_text(encoding='utf-8'))
assert len(products)==5
assert {p['category'] for p in products if p['availability']=='available'}=={'bags','tubing'}
assert next(p for p in products if p['category']=='transfer-sets')['availability']=='enquire'
assert len({p['topic'] for p in products})==len(products)
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.cards={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for key in ('href','src','poster'):
            if key in a:self.links.append(a[key])
        if tag=='article' and 'data-category' in a:self.cards[a['data-category']]=a['data-availability']
count=0
for file in ['index.html','machine.html','supplies.html','pd-at-home.html','about.html','contact.html','privacy.html']:
    html=(ROOT/file).read_text(encoding='utf-8');p=Page();p.feed(html)
    assert len(p.ids)==len(set(p.ids)),f'Duplicate IDs: {file}'
    for value in p.links:
        u=urlsplit(value)
        if u.scheme or u.netloc:continue
        target=ROOT/unquote(u.path) if u.path else ROOT/file
        assert target.exists(),f'Missing {file}: {value}'
        count+=1
    assert 'CAPD fluid bags and tubing are available for sale.' in html,file
    for stale in ['Machine and supplies are in development and are not yet available for sale.','None of the products shown are currently offered for sale.','The complete range is in development and is not yet available for sale.']:
        assert stale not in html,(file,stale)
    if file=='supplies.html':
        assert p.cards=={x['category']:x['availability'] for x in products}
        for product in products:
            assert 'contact.html?'+urlencode({'topic':product['topic']}) in html
            assert re.fullmatch('[a-z-]+',product['category'])
            assert (ROOT/'assets/illustrations'/f"{product['image']}.svg").exists()
    if file in ['index.html','machine.html']:
        assert 'machine-viewer__loading' in html and 'data-machine-viewer' in html
        assert 'fetchpriority="high"' not in html
assert sha256((ROOT/'assets/models/rynor-machine-concept.glb').read_bytes()).hexdigest()=='520b660dff10665e302222e9e763eee529a63dda65fc09e3052aa9bd3aac0dd9'
print(f'PASS: five catalogue categories, explicit availability, correct enquiry topics, {count} local links/assets, unique IDs, consistent sale copy and unchanged 3D model.')
