"""Render a typographic sharing card from the bundled release."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / 'static'
image = Image.new('RGB', (1200, 630), '#f1f0e9')
draw = ImageDraw.Draw(image)
def font(size, italic=False):
    style = 'Italic' if italic else 'Regular'
    return ImageFont.truetype(str(ROOT / f'fonts/FirmamentSans-{style}.ttf'), size)
draw.text((62, 45), 'WHEEL OF HEAVEN  /  AN OPEN-SOURCE TYPEFACE', font=font(20), fill='#26372f')
draw.line((62, 90, 1138, 90), fill='#c9cdc1', width=1)
draw.text((52, 115), 'Firmament.', font=font(210), fill='#26372f')
draw.text((62, 365), 'Yesterday’s clarity. Tomorrow’s possibilities.', font=font(41, True), fill='#26372f')
draw.rectangle((0, 505, 1200, 630), fill='#d9ee9b')
draw.text((62, 527), 'Ḥḥ    Ṣṣ    Ṭṭ    Ḫḫ    ʾʿ    Əə    Ṛṛ', font=font(59), fill='#26372f')
image.save(ROOT/'assets/social.png')
