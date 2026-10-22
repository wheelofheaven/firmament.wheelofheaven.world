"""Render README identity artwork from the release outlines; no installed fonts needed."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/images'
OUTPUT.mkdir(parents=True, exist_ok=True)
PAPER, INK, ACCENT = '#f1f0e9', '#26372f', '#a74732'


def outlines(text, style='Regular'):
    path = ROOT / f'static/fonts/FirmamentSans-{style}.ttf'
    font = TTFont(path)
    glyphs = font.getGlyphSet()
    face = hb.Face(path.read_bytes())
    shaper = hb.Font(face)
    shaper.scale = (face.upem, face.upem)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(shaper, buffer)
    cursor = 0
    paths = []
    bounds = []
    for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
        name = font.getGlyphName(info.codepoint)
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        box = BoundsPen(glyphs)
        glyphs[name].draw(box)
        x, y = cursor + pos.x_offset, pos.y_offset
        if box.bounds:
            left, bottom, right, top = box.bounds
            bounds.append((left + x, bottom + y, right + x, top + y))
        color = ACCENT if text[info.cluster] == '.' else INK
        paths.append(f'<path fill="{color}" transform="translate({x} {y})" d="{pen.getCommands()}"/>')
        cursor += pos.x_advance
    return ''.join(paths), (min(b[0] for b in bounds), min(b[1] for b in bounds), max(b[2] for b in bounds), max(b[3] for b in bounds))


def artwork(filename, label, text, width, height, margin, style='Regular', dot=False):
    paths, (left, bottom, right, top) = outlines(text, style)
    scale = min((width - 2 * margin) / (right - left), (height - 2 * margin) / (top - bottom))
    x = (width - (right - left) * scale) / 2 - left * scale
    y = (height - (top - bottom) * scale) / 2 + top * scale
    extra = f'<circle cx="115" cy="112" r="6" fill="{ACCENT}"/>' if dot else ''
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
<title id="title">{label}</title>
<rect width="{width}" height="{height}" fill="{PAPER}"/>
<g transform="translate({x:.4f} {y:.4f}) scale({scale:.6f} {-scale:.6f})">{paths}</g>
{extra}
</svg>
'''
    (OUTPUT / filename).write_text(svg)


artwork('brandmark.svg', 'Firmament Sans brandmark: italic f and a rust-coloured dot', 'f', 160, 160, 28, 'Italic', True)
artwork('brandtype.svg', 'Firmament Sans wordmark', 'Firmament.', 1000, 220, 38)
print('Rendered brandmark.svg and brandtype.svg from Firmament release outlines.')
