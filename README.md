# Firmament Sans specimen

The dedicated Zola showcase for [Firmament Sans](https://github.com/wheelofheaven/firmament-sans).
Public address: <https://firmament.wheelofheaven.world>.

## Development

```sh
mise run build
mise run check
mise run serve
```

Zola 0.22.1; no Node packages or external runtime services.
The interactive typesetter and searchable glyph explorer use small, dependency-free JavaScript.
All fonts and assets are self-hosted.
No analytics, accounts, cookies, or form submissions.

## Release assets

The bundled 0.1 font release contains four styles, each with 584 Unicode mappings and 60 scholarly additions.
The character explorer data is generated from the actual cmap; invisible controls and spaces are omitted.
Font data, licenses, and ZIP are tracked so a Pages build needs only Zola.

To refresh from a sibling `firmament-sans` checkout, use Python 3.13 with FontTools 4.60.2, Brotli 1.2.0, and Pillow 13.0.0:

```sh
python scripts/sync-fonts.py
python scripts/render-social.py
mise run build
mise run check
```

Review the statistics and release text when changing font versions.
The main Wheel of Heaven website's font selection is independent of this showcase.

## Design direction

The public story connects Jost’s 1920s German sans-serif roots with Bauhaus, New Typography, and New Objectivity.
Its outlook on knowledge transmission is Firmament’s contemporary design position; the historical movements remain distinct and linked to sources.
See [the script-expansion evaluation](docs/script-expansion.md) for the proposed Greek, Hebrew, Arabic, cuneiform, and CJK strategy.

## Cloudflare Pages

- Git repository: `wheelofheaven/firmament.wheelofheaven.world`
- Production branch: `main`
- Framework preset: Zola
- Build command: `zola build`
- Output directory: `public`
- Build environment: `ZOLA_VERSION=0.22.1`
- Custom domain: `firmament.wheelofheaven.world`

The site is connected and configured through the Cloudflare dashboard.
Do not add Worker code or an alternate hosting provider.

## License

Site code and original prose: CC0-1.0; see `LICENSE`.
Bundled fonts and their derivative outlines: SIL Open Font License 1.1, preserved in `static/downloads/OFL.txt`.
The OFL remains applicable to the fonts and is not replaced by the site's CC0 license.
Original Jost design: Owen Earl / indestructible type.
Firmament Sans extension: Wheel of Heaven contributors.
