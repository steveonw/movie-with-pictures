"""HiDream version of the art: picks from the reference run (hd_shots) and the no-reference action run (hd_action),
a colour pass to lift the haze, then the same on-screen text cards. Writes art_hd/."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw
import compose_art as ca   # reuses font(), banner(), fonts (also rebuilds the FLUX art/ — harmless)

S, A, OUT = Path('takes_dl/hd_shots'), Path('takes_dl/hd_action'), Path('art_hd')
OUT.mkdir(exist_ok=True)
PICK = {  # shot: (folder, file stem)
 'classroom_wide': (S, 'classroom_wide__1'), 'professor_class': (S, 'professor_class__1'), 'thomas_bored': (A, 'thomas_bored_act__0'),
 'arena_wide': (S, 'arena_wide__1'), 'owlbear_claws': (A, 'owlbear_claws_act__1'), 'professor_arena': (S, 'professor_arena__0'),
 'thomas_eyes': (A, 'thomas_eyes_act__0'), 'owlbear_charge': (A, 'owlbear_charge_act__0'), 'thomas_stretcher': (A, 'thomas_stretcher_act__1'),
 'box_hero': (S, 'box_hero__1'), 'box_label_base': (S, 'box_label_base__1'), 'helena_box': (S, 'helena_box__1'),
 'owlbear_peek': (S, 'owlbear_peek__1'), 'headmaster_lean': (S, 'headmaster_lean__1'), 'box_explode': (A, 'box_explode_act__1'),
 'owlbear_tackle': (A, 'owlbear_charge_act__1'), 'helena_smile': (S, 'helena_smile__0'), 'montage_a': (S, 'montage_a__0'),
 'montage_b': (A, 'montage_b_act__1'), 'montage_c': (S, 'montage_c__1'), 'montage_d': (A, 'montage_d_act__0'),
 'montage_e': (A, 'montage_e_act__1'), 'ward_bandaged': (S, 'ward_bandaged__0'), 'helena_wand': (S, 'helena_wand__0'),
 'ward_restored': (A, 'ward_restored_act__0'), 'owlbear_curtain': (S, 'owlbear_curtain__1'), 'battlemages': (S, 'battlemages__0'),
 'healers_field': (S, 'healers_field__0'), 'dragon_flag': (S, 'dragon_flag__0'), 'osric': (S, 'osric__0'),
 'malachar_wide': (S, 'malachar_wide__0'), 'malachar_close': (S, 'malachar_close__0'), 'box_pedestal': (S, 'box_pedestal__0'),
 'dragon_shield': (A, 'dragon_shield_act__1'), 'thorne_box': (S, 'thorne_box__1'), 'thorne_down': (S, 'thorne_down__1'),
 'title_bg': (S, 'title_bg__0'), 'stinger_box': (S, 'stinger_box__0'), 'stinger_open': (S, 'stinger_open__1'),
 'cub': (S, 'cub__0'), 'stinger_reach': (S, 'stinger_reach__1'), 'stinger_shadow': (S, 'stinger_shadow__0'),
}


def grade(im):
    a = np.asarray(im.convert('RGB')).astype(np.float32); lum = a.mean(2)
    lo, hi = np.percentile(lum, 0.8), np.percentile(lum, 99.5)
    im = Image.fromarray(np.clip((a - lo) / max(1, hi - lo) * 255, 0, 255).astype(np.uint8))
    return ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.25)).enhance(1.08)


for n, (d, f) in PICK.items():
    grade(Image.open(d / f'{f}.png')).save(OUT / f'{n}.png')

# text cards, same wording as the FLUX version
im = Image.open(OUT / 'box_label_base.png').convert('RGB'); W, H = im.size; d = ImageDraw.Draw(im)
cx, cy = int(.585 * W), int(.70 * H)
d.text((cx, cy - 95), 'WARNING', font=ca.font(ca.SERIF, 82), fill=(120, 15, 15), anchor='mm')
for i, t in enumerate(['MAY CONTAIN LIVE', 'EDUCATIONAL', 'OPPORTUNITIES']):
    d.text((cx, cy + 5 + i * 58), t, font=ca.font(ca.SERIF, 50), fill=(55, 30, 15), anchor='mm')
im.save(OUT / 'box_label.png')
ca.banner(Image.open(OUT / 'box_hero.png'), ['NOW AVAILABLE ACROSS', '700+ DIMENSIONS!'], .82, 110).save(OUT / 'box_dimensions.png')
ca.banner(Image.open(OUT / 'box_pedestal.png'), ['INCLUDES CERTIFIED HEALER', 'INCLUDES INSTRUCTIONAL OWLBEAR', 'NOW SHIPPING INTERDIMENSIONALLY'], .855, 68).save(OUT / 'box_pedestal_text.png')
bg = Image.open(OUT / 'title_bg.png').convert('RGB'); W, H = bg.size
bg = bg.point(lambda v: int(v * .7)); d = ImageDraw.Draw(bg)
d.rectangle([0, int(.66 * H), W, H], fill=(18, 4, 6))
d.text((W / 2, int(.75 * H)), 'BLACKFEATHER ACADEMY IN A BOX™', font=ca.font(ca.SERIF, 96), fill=(245, 205, 110), anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0))
d.text((W / 2, int(.86 * H)), 'RESULTS GUARANTEED.  LIMBS OPTIONAL.  HEALERS INCLUDED.', font=ca.font(ca.BLACK, 56), fill=(255, 245, 225), anchor='mm')
bg.save(OUT / 'final_title.png')
Image.new('RGB', (2560, 1440)).save(OUT / 'black.png')
print('art_hd ready:', len(list(OUT.glob('*.png'))), 'files')
