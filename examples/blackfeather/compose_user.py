"""art_user/: every plan image built from the user's 11 approved scenes and 21 inserts (crops where one picture
covers two beats), plus the two text banners. Crops are fractions of the source: [left, top, right, bottom]."""
from pathlib import Path
from PIL import Image
import compose_art as ca   # font(), banner()

U, I, OUT = Path('user_art'), Path('user_inserts'), Path('art_user'); OUT.mkdir(exist_ok=True)
SC = {i: U / f for i, f in enumerate(sorted(p.name for p in U.glob('[0-9]*.jpg')), 1)}

MAP = {
 'classroom_wide': (SC[1], None), 'professor_class': (SC[1], [0.05, 0.0, 0.55, 0.85]), 'thomas_bored': (SC[1], [0.45, 0.0, 1.0, 1.0]),
 'arena_wide': (SC[2], None), 'owlbear_claws': (SC[2], [0.0, 0.4, 0.62, 1.0]), 'professor_arena': (I / 'P2-09.png', None),
 'thomas_eyes': (I / 'P1-01.png', None), 'owlbear_charge': (I / 'P1-02.png', None), 'thomas_stretcher': (I / 'P1-03.png', None),
 'box_hero': (SC[3], None), 'box_label': (SC[3], [0.25, 0.45, 0.78, 1.0]),
 'helena_box': (I / 'P1-04.png', None), 'owlbear_peek': (I / 'P3-19.png', None), 'headmaster_lean': (I / 'P1-05.png', None),
 'box_explode': (SC[4], None), 'owlbear_tackle': (SC[4], [0.45, 0.15, 1.0, 1.0]), 'helena_smile': (SC[4], [0.0, 0.0, 0.52, 1.0]),
 'montage_a': (I / 'P2-10.png', None), 'montage_b': (SC[5], None), 'montage_c': (I / 'P2-11.png', None),
 'montage_d': (I / 'P1-06.png', None), 'montage_e': (I / 'P2-12.png', None),
 'ward_bandaged': (SC[6], None), 'helena_wand': (SC[6], [0.0, 0.0, 0.6, 1.0]), 'ward_restored': (I / 'P2-13.png', None),
 'owlbear_curtain': (I / 'P2-14.png', None), 'battlemages': (I / 'P2-15.png', None), 'healers_field': (I / 'P3-20.png', None),
 'dragon_flag': (I / 'P2-16.png', None), 'osric': (SC[7], None),
 'malachar_wide': (SC[8], None), 'malachar_close': (SC[8], [0.2, 0.0, 0.8, 0.62]),
 'box_pedestal': (SC[9], None), 'dragon_shield': (I / 'P1-07.png', None),
 'thorne_box': (I / 'P1-08.png', None), 'thorne_down': (I / 'P2-17.png', None), 'final_title': (SC[10], None),
 'stinger_box': (I / 'P2-18.png', None), 'stinger_open': (I / 'P2-18.png', [0.0, 0.0, 0.6, 0.85]),
 'cub': (I / 'P3-21.png', [0.42, 0.3, 0.92, 1.0]), 'stinger_reach': (I / 'P3-21.png', None), 'stinger_shadow': (SC[11], None),
}

for name, (src, box) in MAP.items():
    im = Image.open(src).convert('RGB')
    if box:
        W, H = im.size; im = im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))
    im.save(OUT / f'{name}.png')

ca.banner(Image.open(SC[3]), ['NOW AVAILABLE ACROSS', '700+ DIMENSIONS!'], .14, 76).save(OUT / 'box_dimensions.png')
ca.banner(Image.open(SC[9]), ['INCLUDES CERTIFIED HEALER', 'INCLUDES INSTRUCTIONAL OWLBEAR', 'NOW SHIPPING INTERDIMENSIONALLY'], .88, 46).save(OUT / 'box_pedestal_text.png')
Image.new('RGB', (1920, 1080)).save(OUT / 'black.png')
print('art_user ready:', len(list(OUT.glob('*.png'))), 'files')
