# Firmament beyond Latin and Cyrillic

Evaluation, 22 October 2026. This is a proposed direction, not a release commitment.
Firmament 0.1 remains the four-style, 584-codepoint Latin/Cyrillic pilot.
No additional fonts are bundled by this study.

## Recommendation

Build a coordinated family, with each script designed for its readers.
Extend Firmament itself with Greek; develop Hebrew and Arabic as separately built companions if commissioning original designs.
Initially pair cuneiform and CJK with established specialist fonts under their original names.
The shared identity should come from compatible visual weight, proportions, spacing, and reading rhythm, not from forcing Latin geometry onto other writing systems.

There are two different milestones: reliable script coverage through curated companions, and original Firmament designs.
The first is achievable much sooner.
An open font can be a production companion without being renamed or described as our design.

## Evidence from the existing corpus audit

The committed [coverage inventory](https://github.com/wheelofheaven/firmament-sans/blob/main/scholar/audit/coverage.json) already contains all the requested script groups.
These figures were aggregated from its `characters` entries, summing `count` and counting distinct entries per `category`:

| Audit category | Distinct codepoints observed | Occurrences |
| --- | ---: | ---: |
| Greek | 174 | 283,346 |
| Hebrew | 76 | 3,417,466 |
| Arabic | 73 | 683,729 |
| Cuneiform | 275 | 10,843 |
| East Asian | 7,383 | 9,911,303 |

This is the existing source-text snapshot, not a fresh crawl or a measurement of browser fallback.
It combines published Markdown with library JSON strings, including translations, and groups characters by Unicode-name heuristics.
The East Asian group combines Han, kana, Hangul, and related names; it is not a complete CJK repertoire.
Common punctuation and combining marks can sit outside these groups.
The audit also separates 30 Ugaritic codepoints from its cuneiform category.
Observed characters are useful test material, not a sufficient font specification: readers need unobserved letters, punctuation, combinations, and future texts too.

## Script-by-script assessment

| Script | Proposed route | Main work | Relative original-design effort |
| --- | --- | --- | --- |
| Greek | Add a native Greek design to Firmament Sans | Modern and polytonic Greek, accents/breathings, iota subscript, spacing, four-style proofs | Medium; best first original extension |
| Hebrew | Dedicated Firmament Hebrew companion; use Noto Sans Hebrew for initial pairing tests | Final letters, niqqud, cantillation, mark collisions, mixed-direction text | High for scholarly coverage |
| Arabic | Dedicated Firmament Arabic companion; compare Noto Sans Arabic and Noto Naskh Arabic | Joining forms, cursive attachment, ligatures, stacked marks, language-specific forms | Very high; specialist-led |
| Cuneiform | Curated Noto Sans Cuneiform companion before any bespoke design | Define periods/sign tradition, complete relevant blocks, dense wedge legibility, specialist proofreading | High for a new scholarly design |
| CJK | Source Han Sans or Noto Sans CJK companions selected by language/region | Regional Han forms, kana, Hangul, punctuation, layout, large-font delivery | Very high; a separate major programme |

These effort bands are design judgments, not quotes or calendar estimates.
Scope, available source masters, and access to native readers determine the actual schedule.
Start with a representative regular-weight proof before commissioning a full family.

### Greek: the closest extension

Greek can share Firmament's general texture while retaining native forms, especially in lowercase.
Cover modern monotonic Greek and the polytonic needs of ancient texts from the start.
Test canonically equivalent precomposed and decomposed text; stacked breathing/accent combinations must remain clear in both capitals and lowercase.
Do not confuse Greek letters with visually similar Latin characters, or mathematical symbol coverage with Greek text coverage.
Use [Unicode's Greek and Greek Extended specification](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-7/) to define the repertoire, and [Noto's Latin/Greek/Cyrillic sources](https://github.com/notofonts/latin-greek-cyrillic) as a comparison family.
Commission Greek-reader review of paragraphs, not just alphabet sheets.

### Hebrew: prioritize the pointed text

The existing Hebrew site and source material give this work immediate value.
A bare alphabet is a small part of the scholarly requirement: vowel points and cantillation need tested positioning around each letter and around one another.
Final forms and Hebrew punctuation also belong in the scope.
The font supplies glyphs and positioning; the application must supply correct right-to-left direction and isolation for embedded Latin text and numbers.
See [W3C's Hebrew resources](https://www.w3.org/TR/hebr-lreq/) and [Noto Hebrew](https://github.com/notofonts/hebrew).
Use an upright design with a reviewed emphasis strategy; Latin-style artificial italics should not be the default.

### Arabic: design the connected word

Arabic needs contextual joining, cursive positioning, and mark handling as a system.
Copying isolated letters into a font does not produce readable Arabic.
Begin with a defined Arabic repertoire; Persian, Urdu, and Qur'anic notation require explicit additional scope and reviewers.
Compare Noto Sans Arabic for interface pairing and Noto Naskh Arabic for extended reading before choosing a design direction.
A geometric or Kufic-influenced direction is worth prototyping, but suitability for dense scholarly reading must decide it.
Do not carry the Latin specimen's tracking controls into Arabic: ordinary letter spacing can disrupt connected writing.
See [W3C's Arabic and Persian layout requirements](https://www.w3.org/TR/alreq/) and the [Noto Arabic sources](https://github.com/notofonts/arabic).

### Cuneiform: preserve the sign distinctions

Start with Sumero-Akkadian coverage and document the intended sign-form tradition.
Historical and regional variants need scholarly judgment; reducing wedges to a geometric motif can erase meaningful distinctions.
Consider the main cuneiform block, numbers and punctuation, and Early Dynastic Cuneiform separately.
Ugaritic and Old Persian have separate encodings and must not silently count as covered by a Sumero-Akkadian font.
[Unicode's cuneiform chapter](https://www.unicode.org/versions/Unicode17.0.0/core-spec/chapter-11/) defines these distinctions.
[Noto Sans Cuneiform](https://github.com/notofonts/cuneiform) is a candidate companion; verify its chosen release against the corpus and scholarly sign forms before adopting it.
Prefer a readable regular style with sufficient size and line spacing over automatically generated bold or italic forms.

### CJK: a family of regional solutions

CJK means Chinese, Japanese, and Korean; it spans several writing systems.
Chinese needs an explicit simplified/traditional and regional policy; Japanese needs kana alongside kanji, and Korean needs Hangul alongside any required Hanja.
Shared Unicode Han characters can require different regional glyph forms.
Set correct language tags and select the intended regional fonts; a single generic fallback cannot make those choices reliably.

[Source Han Sans](https://github.com/adobe-fonts/source-han-sans) offers an established Pan-CJK family with source files and several deployment configurations.
It is a strong first candidate for this geometric sans context, subject to visual pairing tests.
Use language-specific web bundles and measured subsetting rather than downloading the entire family on every Latin page.
Preserve characters needed for future content and search results; a current-page subset alone is insufficient for an editable typesetter.
Japanese punctuation, line-breaking, ruby, and vertical composition require layout work beyond a font's character map; see [W3C's Japanese layout requirements](https://www.w3.org/TR/jlreq/).

## Proof 01 — companions measured against the contract (24 October 2026)

Step 1 of the sequence below is done and published at
<https://firmament.wheelofheaven.world/companions/>, generated by
`scripts/companions.py` from pinned sources.

**The metric contract.** What "harmonious with Firmament" means in numbers,
read from the 0.1 outlines: units per em 1000; x-height 460; cap height 700;
ascender 1070 / descender −375; stem 80 ‰ at Regular and 152 ‰ at Bold
(Latin l, scanline at mid-height); typographic colour 184.6 ‰ / 283.9 ‰ of an
em square (HarfBuzz-shaped Genesis 1:1, filled area per em of advance). A
companion fits when its stem is within a tenth of the contract at the same
nominal weight, its working letter height sits between x-height and cap
height, its colour is within a tenth, and its marks and joins survive shaping.
Futura's geometry does not transfer between scripts; these measurements do.

**Findings.**

| Script | Fit | What the numbers say |
| --- | --- | --- |
| Hebrew | Miriam Libre | Stem 78/120 (0.98×/0.79×), letter height 579, colour 163–199 ‰. IBM Plex Sans Hebrew also fits (1.02×/0.99×) but is a grotesque. Noto Sans Hebrew is the only candidate with cantillation and runs 15 % heavier. No open candidate carries cantillation except Noto; pointed source text stays in the citation serif. |
| Greek | none | GFS Neohellenic (1927 New Hellenic) is the design relative but measures 0.65× stem and x-height 394; Didact Gothic 0.85×, single weight; Noto Sans fits the stem but its x-height 546 reads a size larger. This is the argument for drawing Firmament Greek; the brief is in `firmament-sans/scholar/greek/`. |
| Arabic | Cairo (interface) | Stem 77/133 (0.96×/0.88×), alef 717 against cap 700, colour 190–204 ‰. Noto Naskh Arabic at 0.79× remains the reading-text candidate. The main site has no Arabic web font today; adoption waits for native-reader review of a full Hidden Words chapter. |
| Cuneiform | Noto Sans Cuneiform, Noto Sans Ugaritic | Not stylised. Sign height 736 above cap height; colour 233 ‰ at the interlinear size; both already self-hosted on the main site. |
| CJK | current regional pairings | Noto Sans JP/SC/TC/KR stems 81–83 (1.0×), ideograph body 795–826; Zen Kaku Gothic New runs light (67, 0.84×); M PLUS 1p 84; Pretendard 77; IBM Plex Sans KR 77. Written down with measurements as the pairing specification; no CJK outlines are drawn. |

**Decision for the main site.** Companions join the typographic layer they
belong to. Hebrew and Greek citations inside Latin prose stay in the citation
layer (Frank Ruhl Libre, GFS Didot). The Hebrew locale, which until now set
every element in the citation serif and fell to system fonts in component
headings, gets Miriam Libre as its body and display companion, bounded by
`unicode-range` so Latin keeps coming from Firmament Sans and Space Grotesk.
The library reader's scripture text keeps the citation serif. Arabic, cuneiform
and CJK are unchanged on the main site.

## Implementation sequence

1. **Build a companion proof page.** *Done, 24 October 2026: see Proof 01 above.* Pin candidate releases and checksums; retain each name, authorship, and license. Use representative source passages, mixed-script lines, and paragraphs at actual reading sizes. Compare optical size, darkness, baseline, line height, and punctuation. No automatic outline scaling or merging.
2. **Ship reliable reading support.** *Hebrew locale done with Miriam Libre; Arabic pending native-reader review.* Introduce reviewed companions where the relevant script appears. Hebrew and CJK have immediate whole-site value; Greek, Arabic, and cuneiform also matter in source passages. Keep downloads modular and label which font renders each proof.
3. **Draw Firmament Greek.** Begin with a regular proof, including polytonic text, then extend through the four styles after reader review. Develop editable source masters; the current scripted Latin accent additions are not a substitute for a multiscript source design.
4. **Commission Hebrew, then Arabic proofs.** Work with script specialists. Prioritize pointed Hebrew for the existing corpus; define the Arabic language and notation scope before drawing. Let review determine the production weights and emphasis styles.
5. **Reassess bespoke cuneiform and CJK.** Retain the specialist companions unless an identified reading problem justifies a substantial original-design project. A unified visual system does not require every outline to share one author or filename.

## Release gates

- Declare a precise repertoire and supported languages/notation; measure the remaining corpus gaps without claiming universal coverage.
- Shape representative strings with HarfBuzz and proof them in browsers. Check missing glyphs, joining, marks, canonical-equivalence behavior, clipping, and selection/copy fidelity.
- Test complete grapheme clusters. Do not split a base letter and its combining marks across independent font subsets. Preserve layout-table dependencies during subsetting.
- Review right-to-left paragraphs and mixed-script spans with explicit `lang`, `dir`, and bidirectional isolation where appropriate. Keep logical Unicode order in the source.
- Review CJK regional forms and punctuation in every supported locale. Test horizontal reading first; claim vertical layout only after it has been implemented and checked.
- Require native-reader or relevant scholarly review at reading sizes, plus accessibility checks and PDF/desktop proofs when those outputs are supported.
- Keep copyright, license, reserved-name requirements, source provenance, and build instructions with every redistributed font. Check the exact release's license before modification; adding companions is preferable to silently merging or relabeling them.
- Measure actual transfer size and font-loading behavior on a mobile connection. Add script fonts on demand and keep the Latin-only path small.

The design principle remains practical: form follows the function of the particular script, language, and reader.
