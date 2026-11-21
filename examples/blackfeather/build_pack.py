"""Image request pack for Blackfeather: new in-between shots in the look of the 11 approved scenes."""
import json, shutil, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

U = Path('user_art'); OUT = Path('request_pack'); shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()
SC = {i: f for i, f in enumerate(sorted(p.name for p in U.glob('*.jpg')), 1)}   # 1..11 -> file name

REFS = {  # name: (scene, crop box in 1672x941 pixels)
 'thomas_face': (6, (1040, 60, 1400, 420)), 'thomas_costume': (1, (780, 0, 1672, 941)),
 'helena': (4, (0, 40, 560, 941)), 'helena_face': (6, (200, 20, 560, 380)),
 'owlbear': (9, (1140, 120, 1672, 941)), 'owlbear_face': (2, (260, 0, 860, 500)),
 'box': (3, (220, 140, 1460, 941)), 'visiting_headmaster': (4, (1060, 240, 1672, 941)),
 'thorne': (9, (0, 60, 460, 941)), 'arena_instructor': (2, (920, 180, 1180, 480)),
 'classroom_professor': (1, (300, 120, 700, 700)), 'king_osric': (7, (300, 0, 1300, 941)),
 'malachar': (8, (368, 0, 1500, 770)), 'stinger_buyer': (11, (0, 220, 560, 941)), 'cub': (11, (680, 440, 960, 700)),
}

CHAR = {
 'thomas': "Thomas: a lanky teenage boy with a mop of curly auburn-brown hair, freckles and a long friendly face, wearing a navy-blue academy tunic with a small gold feather emblem on the chest, brown leather braces and a leather satchel strap.",
 'helena': "Helena Stitchwell: a warm, smiling Black woman in her thirties with her hair in a high braided updo and small gold earrings, wearing long cream-and-gold embroidered healer's robes with crimson cuffs, holding a slim wooden wand.",
 'owlbear': "The owlbear: a huge, heavy bear-shaped beast covered in layered brown, tawny and cream feathers like overlapping scales, with the face of a great horned owl, amber eyes, a hooked beak and long curved dark claws.",
 'box': "The box: a polished mahogany chest with brass straps and corners, a round gold owl medallion on the lid ringed with small glowing red runes, a brass latch and a small brass plaque on the front.",
 'visiting_headmaster': "The visiting headmaster: a stocky man in his forties with curly brown hair and a full brown beard, wearing a teal-green robe with gold embroidery over a mustard waistcoat.",
 'thorne': "Headmaster Aldric Thorne: a tall, dignified man in his sixties with swept-back silver hair and a short silver goatee, wearing a long crimson velvet robe with gold embroidery over a dark waistcoat.",
 'instructor': "The arena instructor: a muscular, dark-haired man in his thirties with a big grin, wearing a sleeveless red-brown leather training vest and leather bracers.",
 'buyer': "The new buyer: a thin, balding middle-aged headmaster with a narrow face, wearing a rust-brown robe with a gold trim.",
 'cub': "The cub: a small round owlbear cub covered in fluffy cream-and-brown down, with huge amber eyes and a tiny beak.",
}
STYLE = ("Style: match the attached approved scenes exactly: warm painterly digital illustration with soft visible brush texture, "
         "golden afternoon light, rich browns, golds and crimson with navy accents, realistic proportions and expressive comedic acting, "
         "cinematic depth of field. 16:9, 1920x1080 or larger.")
WORLD = ("World: Blackfeather Academy, a sunlit stone fantasy academy with tall arched windows, crimson banners with a gold feather emblem, "
         "a sand-floored circular training arena with brass rings set in the floor.")
AVOID = ("Avoid: no text, letters, captions, subtitles, numbers, watermarks, logos or borders anywhere (the box plaque may stay blank); "
         "no modern clothing; no extra fingers or limbs; no blood or injuries; don't change the named characters' faces.")

LEVEL = {'little': 'Little (about 30-40%): keep composition, faces and light.',
         'moderate': 'Moderate (about 50-60%): same faces, costumes and setting; new pose or framing.',
         'alot': 'A lot (about 65-75%, or reference mode): keep style, palette, faces and costumes; new composition.'}

R = [  # id, short name, for (script beat), between (scene a, scene b), start scene, level, chars, refs, shot, fallback
 ('P1-01', 'thomas_terrified', 'Shot 2 "WAIT, WHAT?" and Shot 6 "NOT AGAIN!"', (2, 6), 2, 'alot', ['thomas'], ['thomas_face', 'thomas_costume'],
  "Close-up of Thomas's face filling most of the frame: eyes wide with comic panic, eyebrows shot up, mouth open in a yelp, one hand half-raised. Soft, warm, out-of-focus stone background so the shot fits both the arena and the infirmary.",
  'crop of Thomas from scene 02'),
 ('P1-02', 'owlbear_charge', 'Shot 2, the roar right after "WAIT, WHAT?"', (2, 3), 2, 'moderate', ['owlbear'], ['owlbear', 'owlbear_face'],
  "Low-angle action shot in the sand arena: the owlbear lunges straight toward the viewer, beak wide open in a roar, one huge front paw reaching forward, sand and loose feathers flying, crimson banners behind.",
  'crop of the owlbear from scene 02'),
 ('P1-03', 'thomas_stretcher', 'Shot 2 "Now THAT\'S a lesson he\'ll never forget!"', (2, 3), 2, 'alot', ['thomas'], ['thomas_face', 'thomas_costume'],
  "Comedy aftermath at the edge of the sand arena: Thomas lies flat on his back on a thick padded white medical stretcher, dazed with a goofy unfocused look, hair full of loose feathers, a few feathers still drifting down. Unhurt, just very surprised.",
  'scene 02 held longer'),
 ('P1-04', 'helena_with_box', 'Shot 4 "Hello! I\'m Master Healer Helena Stitchwell..."', (3, 4), 4, 'alot', ['helena', 'box'], ['helena', 'helena_face', 'box'],
  "Medium shot in the sunlit academy hall from scene 04: Helena stands on the left beside the CLOSED box on its red velvet stand, smiling warmly straight at the viewer and giving a cheerful thumbs-up. The lid is shut and calm.",
  'crop of Helena from scene 04'),
 ('P1-05', 'headmaster_leans_in', 'Shot 4 "How dangerous could—"', (3, 4), 4, 'alot', ['visiting_headmaster', 'box'], ['visiting_headmaster', 'box'],
  "Medium shot: the visiting headmaster leans forward with curious, slightly smug interest toward the CLOSED box on its red velvet stand, one hand reaching for the latch, eyebrows raised. The runes on the lid glow a little brighter. Same hall as scene 04.",
  'crop of the headmaster from scene 04'),
 ('P1-06', 'thomas_dodges', 'Shot 5 montage, "...REAL practical experience" and "ADAPTABILITY!"', (5, 6), 5, 'alot', ['thomas', 'owlbear'], ['thomas_face', 'thomas_costume', 'owlbear'],
  "Dynamic action in the sand arena: Thomas dives sideways out of the way as the owlbear's big feathered paw sweeps through the air just behind him, while a glowing golden defensive rune circle blazes from his outstretched hand. Determined, wide-eyed face, motion and flying sand.",
  'scene 05 with a different crop'),
 ('P1-07', 'thomas_shield_dragon', 'Shot 9 "They should already know!"', (9, 10), 5, 'alot', ['thomas'], ['thomas_face', 'thomas_costume'],
  "Epic but calm: Thomas stands his ground on a rocky hillside and raises a glowing golden shield of light, completely unbothered, while a huge red dragon behind the shield breathes a wave of fire that splashes harmlessly off it. Golden sunset light.",
  'scene 09'),
 ('P1-08', 'thorne_with_box', 'Shot 10 "Blackfeather Academy. Where excellence isn\'t optional!"', (9, 10), 9, 'alot', ['thorne', 'box'], ['thorne', 'box'],
  "Medium shot in the marble hall from scene 09: Headmaster Thorne stands proudly beside the closed box on its marble pedestal, one hand resting on the lid, smiling confidently at the viewer like a company founder in an advert.",
  'crop of Thorne from scene 09'),
 ('P2-09', 'instructor_shouts', 'Shot 2 "Incorrect answer! Pet the owlbear!" and Shot 5 shouted questions', (2, 5), 2, 'alot', ['instructor'], ['arena_instructor'],
  "Medium shot: the arena instructor stands at the arena railing, one hand cupped to his mouth, shouting enthusiastically toward the sand below, pointing with the other hand. Crimson banners behind him.",
  'crop of the instructor from scene 02'),
 ('P2-10', 'montage_fireball', 'Shot 5 montage, "Why settle for theoretical knowledge..."', (4, 5), 5, 'alot', [], [],
  "Action shot: a young battlemage student in a navy academy tunic sprints through a burning obstacle course of wooden beams, blocking a big fireball with a shimmering golden shield of light. Flames and sparks, warm light.",
  'scene 05'),
 ('P2-11', 'montage_heal', 'Shot 5 montage, "REAL defensive skills"', (5, 6), 6, 'alot', ['helena'], ['helena', 'helena_face'],
  "Helena kneels in the sand arena beside a wincing student in a navy tunic and heals his arm with a bright flash of golden light from her wand. Warm, reassuring, no visible injury.",
  'scene 06'),
 ('P2-12', 'thomas_battlefield', 'Shot 5 montage, after "ADAPTABILITY!"', (5, 6), 5, 'alot', ['thomas'], ['thomas_face', 'thomas_costume'],
  "Thomas, a little older and confident, stands firm on a smoky open battlefield and blocks a charging horned red demon with a brilliant golden shield of light. Heroic, dramatic sky.",
  'scene 05'),
 ('P2-13', 'thomas_restored', 'Shot 6 "I feel amazing!"', (6, 6), 6, 'moderate', ['thomas', 'helena'], ['thomas_face', 'thomas_costume', 'helena'],
  "Same infirmary as scene 06: Thomas sits bolt upright in bed, completely healed, bandages falling away, both arms thrown up in joy with a huge grin, golden sparkles around him. Helena beams beside the bed.",
  'scene 06'),
 ('P2-14', 'owlbear_curtain', 'Shot 6, the growl before "NOT AGAIN!"', (6, 6), 6, 'alot', ['owlbear'], ['owlbear', 'owlbear_face'],
  "Inside the bright infirmary from scene 06: the huge backlit silhouette of the owlbear looms behind a white bed curtain, its two amber eyes glowing through the fabric, feathered claws curling around the curtain's edge. Funny-ominous.",
  'crop of the right edge of scene 06'),
 ('P2-15', 'battlemage_formation', 'Shot 7 "From the finest royal battlemages..."', (6, 7), 7, 'alot', [], [],
  "Wide shot: a disciplined formation of royal battlemages in crimson and gold robes on a grand sunlit palace plaza, staffs raised and glowing, a large crimson banner with a gold feather emblem.",
  'scene 07'),
 ('P2-16', 'dragon_retreats', 'Shot 7 "...deliver results!"', (7, 8), 7, 'alot', [], [],
  "Wide shot: a huge green dragon recoils and backs away in comic alarm from a crimson banner with a gold feather emblem planted on a rocky clifftop, golden sunset sky.",
  'scene 07'),
 ('P2-17', 'thorne_glances_down', 'Shot 10 "Neither is the owlbear."', (9, 10), 9, 'alot', ['thorne', 'box'], ['thorne', 'box'],
  "Close-up of Headmaster Thorne, still smiling but glancing down sideways at the box beside him, one eyebrow raised and a slightly nervous smile; red light from the box's runes glows on his face.",
  'crop of Thorne from scene 09'),
 ('P2-18', 'buyer_with_box', 'Stinger "Surely the stories are exaggerated."', (10, 11), 11, 'moderate', ['buyer', 'box'], ['stinger_buyer', 'box'],
  "Same cosy office as scene 11: the new buyer stands confidently in front of the freshly delivered CLOSED box, hands on hips, smug and unconcerned. No shadow yet.",
  'scene 11'),
 ('P3-19', 'eyes_in_the_box', 'Shot 4 "certified instructional monsters"', (3, 4), 3, 'moderate', ['box'], ['box', 'owlbear_face'],
  "Close-up of the box on its red velvet stand with the lid lifted open just a crack; two glowing amber owl eyes peer out from the darkness inside. Funny-ominous.",
  'scene 03'),
 ('P3-20', 'healers_field', 'Shot 7 "...the greatest healers in the multiverse"', (6, 7), 6, 'alot', [], [],
  "Healers in cream-and-gold robes kneel on a misty field, tending tired adventurers with warm golden healing light. Calm and heroic.",
  'scene 06'),
 ('P3-21', 'buyer_pets_cub', 'Stinger "Oh! You\'re actually rather cute!"', (11, 11), 11, 'moderate', ['buyer', 'cub'], ['stinger_buyer', 'cub'],
  "Same office as scene 11: the new buyer kneels and smiles, reaching out to pat the fluffy owlbear cub, which tilts its head at him. No shadow yet.",
  'crop of the cub from scene 11'),
]


def short(n): return SC[n].rsplit('.', 1)[0]


# character references
cr = OUT / 'character_refs'; cr.mkdir()
for k, (s, b) in REFS.items():
    Image.open(U / SC[s]).crop(b).convert('RGB').save(cr / f'{k}.jpg', quality=92)

blocks = []
for rid, name, used, (a, b), start, lvl, chars, refs, shot, fallback in R:
    d = OUT / f'{rid}_{name}'; d.mkdir()
    shutil.copy(U / SC[start], d / 'start.jpg')
    shutil.copy(U / SC[a], d / f'before_{short(a)}.jpg')
    if b != a: shutil.copy(U / SC[b], d / f'after_{short(b)}.jpg')
    for r in refs: shutil.copy(cr / f'{r}.jpg', d / f'ref_{r}.jpg')
    between = f'between approved scene {short(a)} and {short(b)}' if a != b else f'inside approved scene {short(a)}'
    prompt = ' '.join([shot] + [CHAR[c] for c in chars] + [STYLE, WORLD, AVOID])
    txt = (f"{rid}  {name}\nFor: {used}\nSits {between}. Start from: start.jpg ({short(start)}).\n"
           f"How much to change: {LEVEL[lvl]}\nAttach: start.jpg, " + ', '.join(f'ref_{r}.jpg' for r in refs) +
           (' and the before/after scenes for look and continuity.' if True else '') +
           f"\nIf it can't be made: {fallback} (no need to retry with darker wording).\n\nPROMPT:\n{prompt}\n")
    (d / 'prompt.txt').write_text(txt); blocks.append(txt)

(OUT / 'PROMPTS.md').write_text('# Blackfeather: image requests\n\n' + '\n---\n\n'.join(f'```\n{b}```' for b in blocks))
lines = '\n'.join(f'- {rid} {name}: {used}' for rid, name, used, *_ in R)
master = f"""I'm attaching a zip of image requests for "Blackfeather Academy in a Box", a comedy fantasy advert. The 11 approved scenes you already made set the look; these requests are in-between shots for the edit. Make one new image per request.

In the zip: one folder per request (prompt.txt, start.jpg = the approved scene to start from, before_/after_ = the approved scenes this shot sits between, ref_*.jpg = character references cut from the approved scenes), character_refs/ with every reference, and PROMPTS.md with all prompts. If you still have the painted cast sheet, attach it too.

Work in order: P1 first, then P2, then P3 (optional). Follow each prompt.txt exactly, including how much to change the start image (little = re-render; moderate = new pose, same faces and setting; a lot = new composition, same style, faces and costumes). Every image 16:9, 1920x1080 or larger, in exactly the same look as the approved scenes. Never put text, letters, captions, numbers, watermarks, logos or borders in an image. Don't change the named characters' faces or costumes.

Return: name each image by its number only (P1-01.png ...). After each, say in one line if anything didn't match (face, hands, framing). If you can't do one, skip it, say why, and move on.

{lines}

If you can't open zip files, tell me and I'll upload one request at a time.
"""
(OUT / 'MASTER_PROMPT.txt').write_text(master)

# overview sheet: start image of each request with its number
F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
W, H = 418, 235; cols = 4; rows = (len(R) + cols - 1) // cols
sheet = Image.new('RGB', (cols * W, rows * (H + 34)), (18, 18, 18)); dr = ImageDraw.Draw(sheet)
for i, (rid, name, used, ab, start, *_r) in enumerate(R):
    x, y = (i % cols) * W, (i // cols) * (H + 34)
    sheet.paste(Image.open(U / SC[start]).resize((W, H)).point(lambda v: int(v * .55)), (x, y + 34))
    dr.text((x + 6, y + 6), f'{rid} {name}', font=F, fill='yellow')
    dr.text((x + 10, y + 50), f'between {ab[0]:02d} and {ab[1]:02d}' if ab[0] != ab[1] else f'inside {ab[0]:02d}', font=F, fill='white', stroke_width=2, stroke_fill='black')
sheet.save(OUT / 'requests_overview.jpg', quality=88)

with zipfile.ZipFile('Blackfeather_image_requests.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file(): z.write(p, p.relative_to(OUT.parent))
print(len(R), 'requests')
