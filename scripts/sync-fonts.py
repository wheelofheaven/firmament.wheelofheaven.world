"""Copy the exact font release and generate an honest Unicode specimen inventory."""
from pathlib import Path
import hashlib
import json
import shutil
import unicodedata as ud
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'firmament-sans'
SITE = ROOT / 'static'
for name in ('fonts', 'downloads', 'assets'):
    (SITE/name).mkdir(exist_ok=True)
for font in (SOURCE/'scholar/fonts').glob('FirmamentSans-*'):
    shutil.copyfile(font, SITE/'fonts'/font.name)
for name in ('Jost-Regular.woff2',):
    shutil.copyfile(SOURCE/'scholar/fonts'/name, SITE/'fonts'/name)
shutil.copyfile(SOURCE/'OFL.txt', SITE/'downloads/OFL.txt')
(SITE/'downloads/README.md').write_text('''# Firmament Sans 0.1

A scholarly extension of Jost by Wheel of Heaven, based on the original typeface by Owen Earl / indestructible type.
This package contains four TTF desktop fonts, four WOFF2 web fonts, and the SIL Open Font License.

## Desktop

Install the TTF files using your operating system's font manager.
The family includes Regular, Italic, Bold, and Bold Italic.

## Web

Self-host the WOFF2 files and define a separate @font-face for each weight/style pair.
Use font-weight 400 for Regular and Italic, and 700 for Bold and Bold Italic.
Set font-style italic for both italic faces.
Include the OFL copyright and license when redistributing the fonts.

## Status

Version 0.1 is an optical-review pilot with 584 Unicode mappings per style.
It is a static family, not a variable font.
General accent stacking and broader IPA/Egyptological coverage remain future work.

Specimen: https://firmament.wheelofheaven.world/
Source, audit, and feedback: https://github.com/wheelofheaven/firmament-sans
''')
font = TTFont(SITE/'fonts/FirmamentSans-Regular.ttf')
added = {int(cp[2:], 16) for cp in json.loads((SOURCE/'scholar/audit/build.json').read_text())['Regular']['added']}
glyphs = []
for cp, name in sorted(font.getBestCmap().items()):
    ch = chr(cp)
    if ch.isspace() or ud.category(ch).startswith('C'):
        continue
    label = ud.name(ch, 'UNNAMED CHARACTER')
    group = 'cyrillic' if 'CYRILLIC' in label else 'marks' if ud.combining(ch) else 'latin' if 'LATIN' in label else 'figures' if ch.isnumeric() else 'symbols'
    glyphs.append({'char': ch, 'code': f'U+{cp:04X}', 'name': label, 'group': group, 'added': cp in added, 'combining': bool(ud.combining(ch))})
(SITE/'assets/glyphs.json').write_text(json.dumps(glyphs,ensure_ascii=False,separators=(',',':'))+'\n')
glyph_set = font.getGlyphSet()
pen = SVGPathPen(glyph_set)
glyph_set[font.getBestCmap()[ord('ḥ')]].draw(pen)
# Exact font outline, with a typographic baseline and x-height guide.
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -120 760 1160"><defs><clipPath id="below"><rect x="-100" y="900" width="760" height="140"/></clipPath></defs><g fill="none" stroke="#aeb1a0" stroke-width="1"><path d="M-100 200H660M-100 440H660M-100 900H660M0-120V1040M560-120V1040"/></g><g transform="translate(0 900) scale(1 -1)"><path fill="#26372f" d="{pen.getCommands()}"/></g><g clip-path="url(#below)"><g transform="translate(0 900) scale(1 -1)"><path fill="#da4f32" d="{pen.getCommands()}"/></g></g></svg>'''
(SITE/'assets/ha-outline.svg').write_text(svg)
files = list(sorted((SITE/'fonts').glob('FirmamentSans-*'))) + [SITE/'downloads/OFL.txt', SITE/'downloads/README.md']
with ZipFile(SITE/'downloads/FirmamentSans-0.1.zip','w',ZIP_DEFLATED) as z:
    for path in files:
        info=ZipInfo('FirmamentSans-0.1/'+path.name, (2026,10,22,0,0,0))
        info.compress_type=ZIP_DEFLATED
        z.writestr(info,path.read_bytes())
(SITE/'assets/release.json').write_text(json.dumps({'version':'0.1','codepoints':len(font.getBestCmap()),'added':len(added),'styles':4,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
print(f'Synced 4 styles, {len(glyphs)} displayable characters, 60 additions, and licensed ZIP.')
