"""Copy the chosen takes into art/ and draw the on-screen text variants (spelled right, crisp)."""
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PICKS = {
 'classroom_wide': 2, 'professor_class': 1, 'thomas_bored': 1, 'arena_wide': 0, 'owlbear_claws': 1, 'professor_arena': 1,
 'thomas_eyes': 1, 'owlbear_charge': 2, 'thomas_stretcher': 1, 'box_hero': 2, 'box_label_base': 1, 'helena_box': 2,
 'owlbear_peek': 1, 'headmaster_lean': 2, 'box_explode': 0, 'owlbear_tackle': 0, 'helena_smile': 0, 'montage_a': 2,
 'montage_b': 2, 'montage_c': 1, 'montage_d': 0, 'montage_e': 2, 'ward_bandaged': 1, 'helena_wand': 1,
 'ward_restored': 2, 'owlbear_curtain': 1, 'battlemages': 2, 'healers_field': 1, 'dragon_flag': 1, 'osric': 0,
 'malachar_wide': 1, 'malachar_close': 2, 'box_pedestal': 0, 'dragon_shield': 1, 'thorne_box': 2, 'thorne_down': 0,
 'title_bg': 2, 'stinger_box': 1, 'stinger_open': 0, 'cub': 2, 'stinger_reach': 1, 'stinger_shadow': 0,
}
SRC, ART = Path('takes_dl/takes'), Path('art')
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
BLACK = next(p for p in [Path('/usr/share/fonts/truetype/inter/InterDisplay-Black.ttf'), Path('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf')] if p.exists()) \
    if any(p.exists() for p in [Path('/usr/share/fonts/truetype/inter/InterDisplay-Black.ttf'), Path('/usr/share/fonts/opentype/inter/InterDisplay-Black.otf')]) else SERIF

for n, k in PICKS.items():
    shutil.copy(SRC / f'{n}__{k}.png', ART / f'{n}.png')


def font(p, s): return ImageFont.truetype(str(p), s)


def banner(im, lines, y, size, fill=(255, 225, 120), box=(110, 10, 20, 215)):
    """Infomercial headline: bold text on a translucent crimson band."""
    im = im.convert('RGBA'); W, H = im.size; ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    f = font(BLACK, size); hs = [d.textbbox((0, 0), t, font=f) for t in lines]
    lh = max(b[3] - b[1] for b in hs); gap = int(size * .35); total = len(lines) * lh + (len(lines) - 1) * gap
    pad = int(size * .45); top = int(y * H - total / 2)
    d.rectangle([0, top - pad, W, top + total + pad], fill=box)
    d.rectangle([0, top - pad, W, top - pad + 5], fill=(255, 200, 80, 255)); d.rectangle([0, top + total + pad - 5, W, top + total + pad], fill=(255, 200, 80, 255))
    for i, t in enumerate(lines):
        d.text((W / 2, top + i * (lh + gap) + lh / 2), t, font=f, fill=fill, anchor='mm', stroke_width=3, stroke_fill=(40, 0, 0))
    return Image.alpha_composite(im, ov).convert('RGB')


# warning label on the blank parchment (box_label_base take 1)
im = Image.open(ART / 'box_label_base.png').convert('RGB'); W, H = im.size; d = ImageDraw.Draw(im)
cx, cy = int(.665 * W), int(.43 * H)
d.text((cx, cy - 80), 'WARNING', font=font(SERIF, 70), fill=(120, 15, 15), anchor='mm')
for i, t in enumerate(['MAY CONTAIN LIVE', 'EDUCATIONAL', 'OPPORTUNITIES']):
    d.text((cx, cy + 5 + i * 50), t, font=font(SERIF, 42), fill=(55, 30, 15), anchor='mm')
im.save(ART / 'box_label.png')

banner(Image.open(ART / 'box_hero.png'), ['NOW AVAILABLE ACROSS', '700+ DIMENSIONS!'], .80, 64).save(ART / 'box_dimensions.png')
banner(Image.open(ART / 'box_pedestal.png'), ['INCLUDES CERTIFIED HEALER', 'INCLUDES INSTRUCTIONAL OWLBEAR', 'NOW SHIPPING INTERDIMENSIONALLY'], .855, 38).save(ART / 'box_pedestal_text.png')

# end card: crest dimmed and pushed up, title and tagline under it
bg = Image.open(ART / 'title_bg.png').convert('RGB'); W, H = bg.size
bg = bg.point(lambda v: int(v * .7)); d = ImageDraw.Draw(bg)
d.rectangle([0, int(.66 * H), W, H], fill=(18, 4, 6))
d.text((W / 2, int(.75 * H)), 'BLACKFEATHER ACADEMY IN A BOX™', font=font(SERIF, 50), fill=(245, 205, 110), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0))
d.text((W / 2, int(.86 * H)), 'RESULTS GUARANTEED.  LIMBS OPTIONAL.  HEALERS INCLUDED.', font=font(BLACK, 30), fill=(255, 245, 225), anchor='mm')
bg.save(ART / 'final_title.png')
print('art ready:', len(list(ART.glob('*.png'))), 'files')
