"""Verify the built page's internal links, glyph data, and release archive."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
from zipfile import ZipFile
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT/'public'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = set(); self.links = []; self.headings = []
    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if 'id' in a:
            assert a['id'] not in self.ids, ('duplicate ID', a['id'])
            self.ids.add(a['id'])
        if tag in ('a', 'link', 'img', 'script'):
            self.links.extend(a[k] for k in ('href', 'src') if k in a)
        if tag == 'h1': self.headings.append(tag)
        if tag == 'img': assert a.get('alt'), 'Image missing alt text'
page = Page(); page.feed((PUBLIC/'index.html').read_text())
assert len(page.headings) == 1
companions = Page(); companions.feed((PUBLIC/'companions/index.html').read_text())
assert len(companions.headings) == 1
IDS = {'/': page.ids, '/companions/': companions.ids}
def check_links(page, here):
    for link in page.links:
        url = urlparse(link)
        if url.netloc and url.netloc != 'firmament.wheelofheaven.world': continue
        if url.scheme and url.scheme not in ('http', 'https'): continue
        target = url.path or ('/' if url.netloc else here)
        if url.fragment: assert url.fragment in IDS.get(target, set()), ('missing anchor', link)
        path = PUBLIC/unquote(url.path).lstrip('/')
        if not url.path or url.path.endswith('/'): path = path/'index.html'
        assert path.is_file(), ('missing resource', link)
check_links(companions, '/companions/')
data = json.loads((PUBLIC/'assets/companions.json').read_text())
faces = [face for script in data['scripts'] for cand in script['candidates'] for face in cand['faces']]
assert len(data['scripts']) == 5 and faces, 'companion data incomplete'
for face in faces:
    path = PUBLIC/face['file']
    assert path.is_file(), ('missing companion font', face['file'])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == face['sha256'], ('companion checksum', face['file'])
    samples = face['metrics']['density']
    assert samples, ('unmeasured face', face['file'])
    # Every face must shape at least one proof sample completely; samples with
    # missing glyphs (e.g. cantillation in a font without it) are flagged on the page.
    assert any(sample['missing'] == 0 for key, sample in samples.items() if key != 'latin'), ('no complete proof sample', face['file'])
check_links(page, '/')
glyphs = json.loads((PUBLIC/'assets/glyphs.json').read_text())
assert len({g['code'] for g in glyphs}) == len(glyphs)
assert sum(g['added'] for g in glyphs) == 60
release = json.loads((PUBLIC/'assets/release.json').read_text())
assert release['codepoints'] == 584 and release['styles'] == 4
with ZipFile(PUBLIC/'downloads/FirmamentSans-0.1.zip') as archive:
    assert len(archive.namelist()) == 10
    for name in archive.namelist():
        basename = Path(name).name
        assert hashlib.sha256(archive.read(name)).hexdigest() == release['sha256'][basename]
print(f'Passed: all local resources/anchors, {len(glyphs)} visible characters, 60 additions, 10 licensed archive files, and {len(faces)} companion faces.')
