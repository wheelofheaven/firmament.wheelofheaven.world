"""Build the script-companion proof: fetch pinned open fonts, instance them at 400/700,
subset them to their script, write WOFF2 files under static/fonts/companions/, measure
every face against the Firmament metric contract, and write static/assets/companions.json.

Nothing here edits, merges, or renames another designer's outlines. Each companion keeps
its own family name, authorship, and licence; the page only puts them next to Firmament.

Run:  python scripts/companions.py            (downloads land in .companions-cache/)
Deps: fonttools (with brotli), uharfbuzz, Pillow.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import unicodedata as ud
import urllib.request
from pathlib import Path

import uharfbuzz as hb
from fontTools import subset
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".companions-cache"
FONTS_OUT = ROOT / "static/fonts/companions"
DATA_OUT = ROOT / "static/assets/companions.json"
FIRMAMENT = ROOT / "static/fonts"

GF_COMMIT = "e7db6ca603fd4862010383ff17ffd6cc4ffac1c0"  # google/fonts main, 2026-10-24
GF_RAW = "https://raw.githubusercontent.com/google/fonts/{commit}/ofl/{dir}/{file}"
PRETENDARD = "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/{path}"
GENERATED = dt.date.today().isoformat()

# ---------------------------------------------------------------------------
# Corpus passages. Every string is copied verbatim from the Wheel of Heaven
# library JSON or site content named in `source`; nothing is invented here.
# ---------------------------------------------------------------------------
GEN = [
    {"ref": "GEN-WOH-1:1", "he": "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃",
     "en": "When the Elohim began to shape the skies and the land—",
     "ja": "エロヒムが天と地を形づくり始めたとき—", "ko": "엘로힘이 하늘과 땅을 빚기 시작했을 때—",
     "zh": "当厄罗音开始塑造诸天与大地之时——", "zh-Hant": "當厄羅音開始塑造諸天與大地之時—",
     "ru": "Когда Элохим начали придавать форму небесам и земле—"},
    {"ref": "GEN-WOH-1:3", "he": "וַיֹּ֥אמֶר אֱלֹהִ֖ים יְהִ֣י א֑וֹר וַֽיְהִי־אֽוֹר׃",
     "en": "The Elohim said, “Let there be light”; and there was light.",
     "ja": "エロヒムは言った、「光あれ」。すると光があった。", "ko": "엘로힘이 말하였다, \"빛이 있으라\"; 그러자 빛이 있었다.",
     "zh": "厄罗音说：「要有光」；于是有了光。", "zh-Hant": "厄羅音說：「要有光」；於是就有了光。",
     "ru": "Элохим сказали: «Да будет свет»; и стал свет."},
]
HE_PROSE = "אלוהים (עברית: אֱלֹהִים) הוא השם העברי בלשון רבים המשמש לאורך התורה כולה לדמויות המתורגמות באופן מקובל כ»אלוהים«."
LABELS = {
    "he": ["ויקי", "ציר זמן", "ספרייה", "מאמרים", "אודות", "חיפוש", "קראו עוד"],
    "ja": ["ウィキ", "タイムライン", "図書館", "記事", "私たちについて", "検索", "続きを読む"],
    "ko": ["위키", "타임라인", "도서관", "기사", "소개", "검색", "더 읽기"],
    "zh": ["百科", "时间线", "图书馆", "文章", "关于我们", "搜索", "阅读更多"],
    "zh-Hant": ["百科", "時間線", "圖書館", "文章", "關於我們", "搜尋", "閱讀更多"],
}
MATTHEW = {"ref": "MAT-WOH-1:1", "grc": "Βίβλος γενέσεως Ἰησοῦ χριστοῦ υἱοῦ Δαυὶδ υἱοῦ Ἀβραάμ.",
           "en": "The book of the genealogy of Jesus Christ, son of David, son of Abraham."}
THEOGONY = [{"ref": "THEO-1", "grc": "Μουσάων Ἑλικωνιάδων ἀρχώμεθʼ ἀείδειν,", "en": "From the Muses of Helikon let us begin to sing,"},
            {"ref": "THEO-2", "grc": "αἵθʼ Ἑλικῶνος ἔχουσιν ὄρος μέγα τε ζάθεόν τε", "en": "who hold the great and holy mountain of Helikon,"}]
HIDDEN = {"ref": "HWA-1", "ar": "﴿ يَا ابْنَ الرُّوْحِ ﴾ فِي أَوَّلِ القَوْلِ امْلِكْ قَلْبًا جَيِّدًا حَسَنًا مُنيرًا لِتَمْلِكَ مُلْكًا دائِمًا باقِيًا أَزَلًا قَدِيمًا.",
          "rasm": "يا ابن الروح في أول القول املك قلبا جيدا حسنا منيرا لتملك ملكا دائما باقيا أزلا قديما",
          "en": "O Son of the Spirit! First of all sayings: possess a heart that is good, comely, and luminous, that thou mayest possess a dominion enduring, everlasting, from all eternity, ancient."}
ENKI = {"ref": "ENH-WOH-1:1", "cun": "𒆬𒆬𒂵𒀀𒀭 𒂊𒉈 𒁀𒀀𒀭𒈨𒂗𒍢𒂗 𒆳 𒆬𒂵𒀀𒀭",
        "translit": "iri^ki kug-kug-ga-am3 e-ne ba-am3-me-en-ze2-en kur dilmun^ki kug-ga-am3",
        "en": "The city is pure — those who are you — the land of Dilmun is pure."}
BAAL = {"ref": "BCY-WOH-1.1-ii:1", "uga": "[𐎈𐎌𐎋𐎟𐎓𐎕𐎋𐎟𐎓𐎁𐎕𐎋𐎟𐎓]𐎎𐎊𐎟𐎔𐎓𐎐𐎋",
        "translit": "[ḥšk . ʿṣk . ʿbṣk . ʿ]my . pʿnk", "en": "[Hasten, urge, speed to] me, your feet —"}
INLINE = {
    "elohim": "Elohim (Hebrew: אֱלֹהִים) is the plural Hebrew name used throughout the Torah for the figures conventionally translated as God.",
    "apocalypse": "Apocalypse (Greek: ἀποκάλυψις, apokalypsis, ‘uncovering, unveiling, revelation’) is, in its plain Greek meaning, the disclosure of what has been concealed.",
}
CUN_SIGNS = "𒀭 𒆠 𒈗 𒂗 𒆤 𒀀 𒉡 𒁹 𒌋 𒐕"
UGA_ALPHABET = "𐎀𐎁𐎂𐎃𐎄𐎅𐎆𐎇𐎈𐎉𐎊𐎋𐎌𐎍𐎎𐎏𐎐𐎑𐎒𐎓𐎔𐎕𐎖𐎗𐎘𐎙𐎚𐎛𐎜𐎝𐎟"

# ---------------------------------------------------------------------------
# Script definitions: subset ranges, probes, samples, targets.
# ---------------------------------------------------------------------------
R = lambda a, b: list(range(a, b + 1))  # noqa: E731
SCRIPTS = {
    "hebrew": {
        "title": "Hebrew", "native": "עברית", "dir": "rtl", "lang": "he",
        "ranges": R(0x0590, 0x05FF) + R(0xFB1D, 0xFB4F) + R(0x200C, 0x200F) + [0x25CC],
        "stem": ("ו", 0.5), "heights": {"letter": "ב", "ascender": "ל", "descender": "ק"},
        "samples": {"pointed": GEN[0]["he"], "plain": HE_PROSE},
        "coverage": {"letters": R(0x05D0, 0x05EA), "points": R(0x05B0, 0x05BD) + [0x05BF, 0x05C1, 0x05C2, 0x05C7],
                     "cantillation": R(0x0591, 0x05AF), "presentation": R(0xFB1D, 0xFB4F)},
        "target": {"letter": 580, "note": "midpoint of the Latin x-height and cap height"},
    },
    "greek": {
        "title": "Greek", "native": "Ελληνικά", "dir": "ltr", "lang": "grc",
        "ranges": R(0x0370, 0x03FF) + R(0x1F00, 0x1FFF) + [0x25CC],
        "stem": ("ι", 0.45), "heights": {"x": "ο", "cap": "Ο", "descender": "ρ"},
        "samples": {"polytonic": THEOGONY[0]["grc"], "koine": MATTHEW["grc"]},
        "coverage": {"greek": R(0x0370, 0x03FF), "extended": R(0x1F00, 0x1FFF)},
        "target": {"x": 460, "cap": 700},
    },
    "arabic": {
        "title": "Arabic", "native": "العربية", "dir": "rtl", "lang": "ar",
        "ranges": R(0x0600, 0x06FF) + R(0x0750, 0x077F) + R(0xFB50, 0xFDFF) + R(0xFE70, 0xFEFF) + R(0x200C, 0x200F) + [0x25CC],
        "stem": ("ا", 0.5), "heights": {"alef": "ا", "loop": "ه", "descender": "ر"},
        "samples": {"vocalised": HIDDEN["ar"], "rasm": HIDDEN["rasm"]},
        "coverage": {"arabic": R(0x0600, 0x06FF), "supplement": R(0x0750, 0x077F), "presentation_a": R(0xFB50, 0xFDFF), "presentation_b": R(0xFE70, 0xFEFF)},
        "target": {"alef": 700, "loop": 460},
    },
    "cuneiform": {
        "title": "Cuneiform", "native": "𒀭", "dir": "ltr", "lang": "sux",
        "ranges": None,  # passage subset
        "stem": None, "heights": {"sign": "𒀭"},
        "samples": {"sumerian": ENKI["cun"]},
        "coverage": {"cuneiform": R(0x12000, 0x123FF), "numbers": R(0x12400, 0x1247F), "early_dynastic": R(0x12480, 0x12543), "ugaritic": R(0x10380, 0x1039F)},
        "target": {},
    },
    "cjk": {
        "title": "Chinese, Japanese, Korean", "native": "漢字 · かな · 한글", "dir": "ltr", "lang": "",
        "ranges": None,
        "stem": ("丨", 0.5), "heights": {"body": "国"},
        "samples": {},  # per language, see families
        "coverage": {"han": R(0x4E00, 0x9FFF), "hiragana": R(0x3040, 0x309F), "katakana": R(0x30A0, 0x30FF), "hangul": R(0xAC00, 0xD7A3)},
        "target": {},
    },
}

def gf(dir_, *files):
    return {"kind": "google-fonts", "dir": dir_, "files": list(files)}

FAMILIES = [
    # Hebrew -----------------------------------------------------------------
    dict(key="miriam-libre", name="Miriam Libre", script="hebrew", credit="Michal Sahar",
         origin="Revival of Raphael Frank’s monolinear Miriam, drawn in Germany in the early twentieth century; Latin drawn to match.",
         source=gf("miriamlibre", "MiriamLibre[wght].ttf"), faces={400: "MiriamLibre[wght].ttf", 700: "MiriamLibre[wght].ttf"}),
    dict(key="noto-sans-hebrew", name="Noto Sans Hebrew", script="hebrew", credit="Google / Noto",
         origin="Neutral grotesque with full point and cantillation coverage.",
         source=gf("notosanshebrew", "NotoSansHebrew[wdth,wght].ttf"), faces={400: "NotoSansHebrew[wdth,wght].ttf", 700: "NotoSansHebrew[wdth,wght].ttf"}),
    dict(key="ibm-plex-sans-hebrew", name="IBM Plex Sans Hebrew", script="hebrew", credit="Mike Abbink, Bold Monday",
         origin="Grotesque companion to IBM Plex, the family already used for the site’s citation serif and Korean display face.",
         source=gf("ibmplexsanshebrew", "IBMPlexSansHebrew-Regular.ttf", "IBMPlexSansHebrew-Bold.ttf"),
         faces={400: "IBMPlexSansHebrew-Regular.ttf", 700: "IBMPlexSansHebrew-Bold.ttf"}),
    dict(key="heebo", name="Heebo", script="hebrew", credit="Oded Ezer", origin="Hebrew companion to Roboto.",
         source=gf("heebo", "Heebo[wght].ttf"), faces={400: "Heebo[wght].ttf", 700: "Heebo[wght].ttf"}),
    dict(key="assistant", name="Assistant", script="hebrew", credit="Ben Nathan, Adobe", origin="Hebrew companion to Source Sans.",
         source=gf("assistant", "Assistant[wght].ttf"), faces={400: "Assistant[wght].ttf", 700: "Assistant[wght].ttf"}),
    dict(key="alef", name="Alef", script="hebrew", credit="Hagilda, Mushon Zer-Aviv", origin="Humanist Hebrew sans, two static weights.",
         source=gf("alef", "Alef-Regular.ttf", "Alef-Bold.ttf"), faces={400: "Alef-Regular.ttf", 700: "Alef-Bold.ttf"}),
    dict(key="rubik", name="Rubik", script="hebrew", credit="Hubert & Fischer, Meir Sadan, Cyreal", origin="Geometric sans with rounded corners.",
         source=gf("rubik", "Rubik[wght].ttf"), faces={400: "Rubik[wght].ttf", 700: "Rubik[wght].ttf"}),
    # Greek ------------------------------------------------------------------
    dict(key="gfs-neohellenic", name="GFS Neohellenic", script="greek", credit="Greek Font Society",
         origin="Digitisation of Victor Scholderer’s New Hellenic, cut by Monotype in 1927: round, nearly monolinear, with polytonic coverage.",
         source=gf("gfsneohellenic", "GFSNeohellenic.ttf", "GFSNeohellenicBold.ttf"), faces={400: "GFSNeohellenic.ttf", 700: "GFSNeohellenicBold.ttf"}),
    dict(key="didact-gothic", name="Didact Gothic", script="greek", credit="Daniel Johnson, Cyreal", origin="Single-weight geometric sans with polytonic Greek.",
         source=gf("didactgothic", "DidactGothic-Regular.ttf"), faces={400: "DidactGothic-Regular.ttf"}),
    dict(key="noto-sans", name="Noto Sans", script="greek", credit="Google / Noto", origin="Neutral humanist sans; full polytonic coverage.",
         source=gf("notosans", "NotoSans[wdth,wght].ttf"), faces={400: "NotoSans[wdth,wght].ttf", 700: "NotoSans[wdth,wght].ttf"}),
    # Arabic -----------------------------------------------------------------
    dict(key="cairo", name="Cairo", script="arabic", credit="Mohamed Gaber, Accademia di Belle Arti di Urbino",
         origin="Kufi-based Arabic drawn as the companion to a geometric Latin (Titillium Web).",
         source=gf("cairo", "Cairo[slnt,wght].ttf"), faces={400: "Cairo[slnt,wght].ttf", 700: "Cairo[slnt,wght].ttf"}),
    dict(key="noto-kufi-arabic", name="Noto Kufi Arabic", script="arabic", credit="Google / Noto", origin="Kufi-style sans for interface text.",
         source=gf("notokufiarabic", "NotoKufiArabic[wght].ttf"), faces={400: "NotoKufiArabic[wght].ttf", 700: "NotoKufiArabic[wght].ttf"}),
    dict(key="noto-naskh-arabic", name="Noto Naskh Arabic", script="arabic", credit="Google / Noto", origin="Naskh text face for extended reading.",
         source=gf("notonaskharabic", "NotoNaskhArabic[wght].ttf"), faces={400: "NotoNaskhArabic[wght].ttf", 700: "NotoNaskhArabic[wght].ttf"}),
    dict(key="ibm-plex-sans-arabic", name="IBM Plex Sans Arabic", script="arabic", credit="Mike Abbink, Bold Monday, Khajag Apelian, Wael Morcos",
         origin="Arabic companion to IBM Plex.", source=gf("ibmplexsansarabic", "IBMPlexSansArabic-Regular.ttf", "IBMPlexSansArabic-Bold.ttf"),
         faces={400: "IBMPlexSansArabic-Regular.ttf", 700: "IBMPlexSansArabic-Bold.ttf"}),
    # Cuneiform ----------------------------------------------------------------
    dict(key="noto-sans-cuneiform", name="Noto Sans Cuneiform", script="cuneiform", credit="Google / Noto",
         origin="Sumero-Akkadian signs, numbers and punctuation; already self-hosted on the main site.",
         source=gf("notosanscuneiform", "NotoSansCuneiform-Regular.ttf"), faces={400: "NotoSansCuneiform-Regular.ttf"},
         passage=ENKI["cun"] + CUN_SIGNS),
    dict(key="noto-sans-ugaritic", name="Noto Sans Ugaritic", script="cuneiform", credit="Google / Noto",
         origin="The thirty-letter Ugaritic abjad, encoded separately from Sumero-Akkadian cuneiform.",
         source=gf("notosansugaritic", "NotoSansUgaritic-Regular.ttf"), faces={400: "NotoSansUgaritic-Regular.ttf"},
         passage=BAAL["uga"] + UGA_ALPHABET, heights={"sign": "𐎀"}, sample_key="ugaritic", sample=BAAL["uga"]),
    # CJK ----------------------------------------------------------------------
    dict(key="noto-sans-jp", name="Noto Sans JP", script="cjk", lang="ja", credit="Google / Adobe (Source Han Sans)", origin="Pan-CJK sans, Japanese glyph forms.",
         source=gf("notosansjp", "NotoSansJP[wght].ttf"), faces={400: "NotoSansJP[wght].ttf", 700: "NotoSansJP[wght].ttf"}),
    dict(key="zen-kaku-gothic-new", name="Zen Kaku Gothic New", script="cjk", lang="ja", credit="Yoshimichi Ohira", origin="Current body face for the Japanese locale.",
         source=gf("zenkakugothicnew", "ZenKakuGothicNew-Regular.ttf", "ZenKakuGothicNew-Bold.ttf"), faces={400: "ZenKakuGothicNew-Regular.ttf", 700: "ZenKakuGothicNew-Bold.ttf"}),
    dict(key="m-plus-1p", name="M PLUS 1p", script="cjk", lang="ja", credit="Coji Morishita, M+ Fonts Project", origin="Geometric gothic; current Japanese display face.",
         source=gf("mplus1p", "MPLUS1p-Regular.ttf", "MPLUS1p-Bold.ttf"), faces={400: "MPLUS1p-Regular.ttf", 700: "MPLUS1p-Bold.ttf"}),
    dict(key="noto-sans-sc", name="Noto Sans SC", script="cjk", lang="zh", credit="Google / Adobe (Source Han Sans)", origin="Simplified Chinese glyph forms; current body face.",
         source=gf("notosanssc", "NotoSansSC[wght].ttf"), faces={400: "NotoSansSC[wght].ttf", 700: "NotoSansSC[wght].ttf"}),
    dict(key="noto-sans-tc", name="Noto Sans TC", script="cjk", lang="zh-Hant", credit="Google / Adobe (Source Han Sans)", origin="Traditional Chinese glyph forms; current body face.",
         source=gf("notosanstc", "NotoSansTC[wght].ttf"), faces={400: "NotoSansTC[wght].ttf", 700: "NotoSansTC[wght].ttf"}),
    dict(key="noto-sans-kr", name="Noto Sans KR", script="cjk", lang="ko", credit="Google / Adobe (Source Han Sans)", origin="Korean glyph forms.",
         source=gf("notosanskr", "NotoSansKR[wght].ttf"), faces={400: "NotoSansKR[wght].ttf", 700: "NotoSansKR[wght].ttf"}),
    dict(key="pretendard", name="Pretendard", script="cjk", lang="ko", credit="Kil Hyung-jin", origin="Current body face for the Korean locale.",
         source={"kind": "url", "files": {"Pretendard-Regular.woff2": PRETENDARD.format(path="packages/pretendard/dist/web/static/woff2/Pretendard-Regular.woff2"),
                                           "Pretendard-Bold.woff2": PRETENDARD.format(path="packages/pretendard/dist/web/static/woff2/Pretendard-Bold.woff2"),
                                           "LICENSE": PRETENDARD.format(path="LICENSE")}, "version": "v1.3.9"},
         faces={400: "Pretendard-Regular.woff2", 700: "Pretendard-Bold.woff2"}),
    dict(key="ibm-plex-sans-kr", name="IBM Plex Sans KR", script="cjk", lang="ko", credit="Mike Abbink, Bold Monday", origin="Current Korean display face.",
         source=gf("ibmplexsanskr", "IBMPlexSansKR-Regular.ttf", "IBMPlexSansKR-Bold.ttf"), faces={400: "IBMPlexSansKR-Regular.ttf", 700: "IBMPlexSansKR-Bold.ttf"}),
]
CJK_SAMPLE = {"ja": GEN[0]["ja"], "ko": GEN[0]["ko"], "zh": GEN[0]["zh"], "zh-Hant": GEN[0]["zh-Hant"]}
# CSS unicode-range for each script-block subset (empty: passage subsets, no range), and the
# word each companion sets on the metric rail next to Firmament’s "Eb … hl".
CSS_RANGES = {"hebrew": "U+0590-05FF, U+FB1D-FB4F, U+200C-200F, U+25CC", "greek": "U+0370-03FF, U+1F00-1FFF, U+25CC",
              "arabic": "U+0600-06FF, U+0750-077F, U+FB50-FDFF, U+FE70-FEFF, U+200C-200F, U+25CC",
              "cuneiform": "U+10380-1039F, U+12000-1254F", "cjk": ""}
RAIL_WORDS = {"hebrew": "אֱלֹהִים", "greek": "ἀποκάλυψις", "arabic": "الرُّوْحِ", "cuneiform": "𒀭𒆠",
              "ugaritic": "𐎛𐎍", "ja": "エロヒム", "ko": "엘로힘", "zh": "厄罗音", "zh-Hant": "厄羅音"}
CJK_STEM = {"ko": ("ㅣ", 0.5)}
CJK_BODY = {"ko": "한"}
LATIN_SAMPLE = GEN[0]["en"]
CYRILLIC_SAMPLE = GEN[0]["ru"]

# ---------------------------------------------------------------------------
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fetch(fam) -> Path:
    d = CACHE / fam["key"]; d.mkdir(parents=True, exist_ok=True)
    src = fam["source"]
    if src["kind"] == "google-fonts":
        targets = {f: GF_RAW.format(commit=GF_COMMIT, dir=src["dir"], file=f) for f in src["files"] + ["OFL.txt", "METADATA.pb"]}
    else:
        targets = src["files"]
    for name, url in targets.items():
        out = d / name
        if out.exists() and out.stat().st_size > 1024:
            continue
        print(f"  fetch {fam['key']}/{name}")
        req = urllib.request.Request(url, headers={"User-Agent": "firmament-companions/0.1"})
        with urllib.request.urlopen(req, timeout=120) as r:
            out.write_bytes(r.read())
    return d

def designer_from_metadata(d: Path) -> str:
    m = d / "METADATA.pb"
    if not m.exists():
        return ""
    hit = re.search(r'^designer: "(.*)"$', m.read_text(encoding="utf-8"), re.M)
    return hit.group(1) if hit else ""

def load_static(path: Path, wght: int) -> TTFont:
    f = TTFont(path)
    if "fvar" in f:
        loc = {a.axisTag: (min(max(wght, a.minValue), a.maxValue) if a.axisTag == "wght" else a.defaultValue) for a in f["fvar"].axes}
        f = instancer.instantiateVariableFont(f, loc, inplace=False)
    f.flavor = None
    return f

def version_of(f: TTFont) -> str:
    for n in f["name"].names:
        if n.nameID == 5:
            return n.toUnicode().replace("Version ", "").strip()
    return ""

def bounds(f: TTFont, gs, cmap, ch):
    name = cmap.get(ord(ch))
    if not name:
        return None
    pen = BoundsPen(gs); gs[name].draw(pen)
    if not pen.bounds:
        return None
    s = 1000.0 / f["head"].unitsPerEm
    xmin, ymin, xmax, ymax = pen.bounds
    return {"ymin": round(ymin * s), "ymax": round(ymax * s), "width": round((xmax - xmin) * s)}

def stem(ttf_path: Path, ch: str, frac: float):
    """Widest ink run on the scanline at `frac` of the glyph’s own height, rendered at 1000 px/em."""
    font = ImageFont.truetype(str(ttf_path), 1000)
    mask = font.getmask(ch, mode="1")
    w, h = mask.size
    if not w or not h:
        return None
    rows = [[mask.getpixel((x, y)) for x in range(w)] for y in range(h)]
    inked = [y for y in range(h) if any(rows[y])]
    if not inked:
        return None
    y = inked[0] + int((inked[-1] - inked[0]) * frac)
    runs, run = [], 0
    for px in rows[y]:
        if px:
            run += 1
        elif run:
            runs.append(run); run = 0
    if run:
        runs.append(run)
    return max(runs) if runs else None

def density(path: Path, text: str):
    """Filled outline area per em of advance, in ‰ of an em square, after HarfBuzz shaping."""
    f = TTFont(path); upm = f["head"].unitsPerEm; gs = f.getGlyphSet(); order = f.getGlyphOrder()
    face = hb.Face(path.read_bytes()); hf = hb.Font(face); hf.scale = (upm, upm)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hf, buf)
    area = adv = 0; missing = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        if info.codepoint == 0:
            missing += 1
        pen = AreaPen(gs); gs[order[info.codepoint]].draw(pen)
        area += abs(pen.value); adv += pos.x_advance
    return {"per_mille": round(area / (adv * upm) * 1000, 1) if adv else None, "missing": missing, "glyphs": len(buf.glyph_infos)}

def measure(ttf_path: Path, script: str, fam) -> dict:
    f = TTFont(ttf_path); s = 1000.0 / f["head"].unitsPerEm
    cmap = f.getBestCmap(); gs = f.getGlyphSet(); os2 = f["OS/2"]; hh = f["hhea"]
    spec = SCRIPTS[script]
    m = {
        "upm": f["head"].unitsPerEm, "weight_class": os2.usWeightClass,
        "ascender": round(hh.ascent * s), "descender": round(hh.descent * s),
        "typo_ascender": round(os2.sTypoAscender * s), "typo_descender": round(os2.sTypoDescender * s), "use_typo_metrics": bool(os2.fsSelection & 128),
        "x_height": round(getattr(os2, "sxHeight", 0) * s), "cap_height": round(getattr(os2, "sCapHeight", 0) * s),
        "glyphs": len(f.getGlyphOrder()), "codepoints": len(cmap),
        "heights": {}, "density": {}, "coverage": {}, "stem": None, "latin_stem": None, "latin_x": None, "latin_cap": None,
    }
    heights = dict(spec["heights"]); heights.update(fam.get("heights", {}))
    if script == "cjk" and fam.get("lang") in CJK_BODY:
        heights = {"body": CJK_BODY[fam["lang"]]}
    for k, ch in heights.items():
        b = bounds(f, gs, cmap, ch)
        if b:
            m["heights"][k] = b
    probe = spec["stem"]
    if script == "cjk" and fam.get("lang") in CJK_STEM:
        probe = CJK_STEM[fam["lang"]]
    if probe and ord(probe[0]) in cmap:
        m["stem"] = stem(ttf_path, *probe)
    if ord("l") in cmap:
        m["latin_stem"] = stem(ttf_path, "l", 0.5)
        lb = bounds(f, gs, cmap, "o"); cb = bounds(f, gs, cmap, "O")
        m["latin_x"] = lb["ymax"] if lb else None; m["latin_cap"] = cb["ymax"] if cb else None
    samples = dict(spec["samples"])
    if script == "cjk":
        samples = {fam["lang"]: CJK_SAMPLE[fam["lang"]]}
    if fam.get("sample_key"):
        samples = {fam["sample_key"]: fam["sample"]}
    for k, text in samples.items():
        m["density"][k] = density(ttf_path, text)
    if ord("l") in cmap:
        m["density"]["latin"] = density(ttf_path, LATIN_SAMPLE)
    for k, cps in spec["coverage"].items():
        m["coverage"][k] = {"present": sum(1 for cp in cps if cp in cmap), "of": len(cps)}
    gsub = f.get("GSUB"); gpos = f.get("GPOS")
    m["features"] = sorted({r.FeatureTag for t in (gsub, gpos) if t for r in t.table.FeatureList.FeatureRecord})
    return m

def subset_font(static: TTFont, out: Path, script: str, fam) -> dict:
    opts = subset.Options()
    opts.flavor = "woff2"; opts.layout_features = ["*"]; opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    opts.notdef_outline = True; opts.recommended_glyphs = True; opts.hinting = False; opts.desubroutinize = True
    sub = subset.Subsetter(opts)
    spec = SCRIPTS[script]
    if spec["ranges"] is not None:
        sub.populate(unicodes=spec["ranges"]); kind = "script blocks"
    else:
        text = fam.get("passage") or (CJK_SAMPLE[fam["lang"]] + GEN[1][fam["lang"]] + "".join(LABELS[fam["lang"]]) + "。、「」！？，：；（）—")
        sub.populate(text=text); kind = "proof passages only"
    sub.subset(static)
    static.flavor = "woff2"; static.save(out)
    return {"kind": kind, "glyphs": len(static.getGlyphOrder())}

def firmament_contract() -> dict:
    out = {}
    for style, wght in (("Regular", 400), ("Bold", 700)):
        p = FIRMAMENT / f"FirmamentSans-{style}.ttf"
        f = TTFont(p); os2 = f["OS/2"]; hh = f["hhea"]; gs = f.getGlyphSet(); cmap = f.getBestCmap()
        out[str(wght)] = {
            "file": p.name, "sha256": sha(p), "upm": f["head"].unitsPerEm,
            "ascender": hh.ascent, "descender": hh.descent, "x_height": os2.sxHeight, "cap_height": os2.sCapHeight,
            "o_top": bounds(f, gs, cmap, "o")["ymax"], "O_top": bounds(f, gs, cmap, "O")["ymax"], "l_top": bounds(f, gs, cmap, "l")["ymax"], "p_bottom": bounds(f, gs, cmap, "p")["ymin"],
            "stem": stem(p, "l", 0.5), "cyrillic_stem": stem(p, "п", 0.5),
            "density": {"latin": density(p, LATIN_SAMPLE), "cyrillic": density(p, CYRILLIC_SAMPLE)},
        }
    return out

def main() -> None:
    CACHE.mkdir(exist_ok=True)
    if FONTS_OUT.exists():
        shutil.rmtree(FONTS_OUT)
    FONTS_OUT.mkdir(parents=True)
    firm = firmament_contract()
    data = {
        "generated": GENERATED,
        "firmament": firm,
        "contract": {
            "upm": 1000, "x_height": firm["400"]["x_height"], "cap_height": firm["400"]["cap_height"],
            "ascender": firm["400"]["ascender"], "descender": firm["400"]["descender"],
            "stem": {"400": firm["400"]["stem"], "700": firm["700"]["stem"]},
            "density": {"400": firm["400"]["density"]["latin"]["per_mille"], "700": firm["700"]["density"]["latin"]["per_mille"]},
            "baseline_from_top": round((1000 + firm["400"]["ascender"] + firm["400"]["descender"]) / 2),
        },
        "method": {
            "stem": "Widest horizontal ink run on the scanline at a fixed fraction of the glyph’s own height, rasterised at 1000 px per em (FreeType via Pillow); probes: Latin l, Hebrew vav, Greek iota, Arabic alef, Han 丨, Hangul ㅣ.",
            "density": "Filled outline area of the HarfBuzz-shaped sample divided by total advance × em, in ‰ of an em square. Marks count as ink; counters are subtracted.",
            "heights": "Glyph bounding boxes from the outlines, scaled to 1000 units per em. Overshoot is included, so round letters read about ten units above the nominal line.",
            "faces": "Variable fonts are instanced at wght 400 and 700 with fontTools; static families use their Regular and Bold files. Measurements come from the full instanced font; the served WOFF2 files are subsets.",
            "subsets": "Hebrew, Greek and Arabic files keep their whole script blocks plus presentation forms and bidi controls; cuneiform and CJK files contain only the proof passages, so they are not production fonts.",
        },
        "ranges": CSS_RANGES, "words": RAIL_WORDS,
        "passages": {"genesis": GEN, "hebrew_prose": HE_PROSE, "labels": LABELS, "matthew": MATTHEW, "theogony": THEOGONY, "hidden_words": HIDDEN, "enki": ENKI, "baal": BAAL, "inline": INLINE, "cuneiform_signs": CUN_SIGNS, "ugaritic_alphabet": UGA_ALPHABET},
        "scripts": [],
    }
    by_script = {k: {"key": k, **{kk: vv for kk, vv in v.items() if kk in ("title", "native", "dir", "lang", "target")}, "candidates": []} for k, v in SCRIPTS.items()}
    for fam in FAMILIES:
        print(fam["name"])
        d = fetch(fam)
        designer = designer_from_metadata(d) or fam["credit"]
        rec = {"key": fam["key"], "name": fam["name"], "credit": fam["credit"], "designer": designer, "origin": fam["origin"], "lang": fam.get("lang", SCRIPTS[fam["script"]]["lang"]),
               "license": "SIL Open Font License 1.1", "source": {}, "faces": []}
        src = fam["source"]
        if src["kind"] == "google-fonts":
            rec["source"] = {"repository": "google/fonts", "commit": GF_COMMIT, "path": f"ofl/{src['dir']}", "files": {f: sha(d / f) for f in src["files"]}}
            (FONTS_OUT / fam["key"]).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(d / "OFL.txt", FONTS_OUT / fam["key"] / "OFL.txt")
        else:
            rec["source"] = {"repository": "orioncactus/pretendard", "release": src["version"], "files": {f: sha(d / f) for f in src["files"] if f != "LICENSE"}}
            (FONTS_OUT / fam["key"]).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(d / "LICENSE", FONTS_OUT / fam["key"] / "OFL.txt")
        for wght, fname in sorted(fam["faces"].items()):
            static = load_static(d / fname, wght)
            inst_path = CACHE / fam["key"] / f"{fam['key']}-{wght}.ttf"
            static.save(inst_path)
            rec.setdefault("version", version_of(static))
            out = FONTS_OUT / fam["key"] / f"{fam['key']}-{wght}.woff2"
            sub_info = subset_font(TTFont(inst_path), out, fam["script"], fam)
            m = measure(inst_path, fam["script"], fam)
            rec["faces"].append({"weight": wght, "source_file": fname, "variable_source": "fvar" in TTFont(d / fname),
                                 "file": f"fonts/companions/{fam['key']}/{out.name}", "bytes": out.stat().st_size, "sha256": sha(out),
                                 "subset": sub_info, "metrics": m})
            heights = ", ".join("%s %s" % (k, v["ymax"]) for k, v in m["heights"].items())
            dens = ", ".join("%s %s" % (k, v["per_mille"]) for k, v in m["density"].items())
            print("  %s: stem %s latin_stem %s heights {%s} density {%s} -> %s %d KB" % (wght, m.get("stem"), m.get("latin_stem"), heights, dens, out.name, out.stat().st_size // 1024))
        by_script[fam["script"]]["candidates"].append(rec)
    data["scripts"] = list(by_script.values())
    DATA_OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    total = sum(p.stat().st_size for p in FONTS_OUT.rglob("*.woff2"))
    print(f"Wrote {DATA_OUT.relative_to(ROOT)} and {sum(1 for _ in FONTS_OUT.rglob('*.woff2'))} WOFF2 files ({total // 1024} KB).")

if __name__ == "__main__":
    main()
