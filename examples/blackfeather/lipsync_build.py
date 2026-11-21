"""1) Mouth versions of every speaking picture (same crops as compose_user.py) -> art_user_mouth/<image>__<A-F>.png
2) Mouth timing for every on-screen spoken line with Rhubarb -> lipsync.json (per speaker, per frame at 24 fps)."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, '.')
import motion_comic as mc

FPS = 24
RHUBARB = os.environ.get('RHUBARB', 'rhubarb')            # path to the Rhubarb Lip Sync binary
MO = Path(os.environ.get('MOUTHS', 'mouths_in')); HEL = Path(os.environ.get('HELENA_MOUTHS', 'helena_mouths'))  # returned mouth images
files = {p.name: p for p in MO.rglob('*.png')}

# art_user crops (same as compose_user.py)
src = open('compose_user.py').read().split('for name, (src, box) in MAP.items():')[0].replace('import compose_art as ca', '')
ns = {}; exec(src, ns); MAP = ns['MAP']

LIP = {  # picture in the edit -> (mouth set, speaker)
 'helena_box': ('HELENA_P1-04', 'healer'), 'professor_class': ('01_professor', 'professor'), 'thomas_bored': ('01_thomas', 'thomas'),
 'professor_arena': ('P2-09_instructor', 'instructor'), 'thomas_eyes': ('P1-01_thomas', 'thomas'), 'headmaster_lean': ('P1-05_headmaster', 'headmaster'),
 'helena_smile': ('04_helena', 'healer'), 'montage_d': ('P1-06_thomas', 'thomas'), 'ward_restored': ('P2-13_thomas', 'thomas'),
 'helena_wand': ('06_helena', 'healer'), 'osric': ('07_osric', 'osric'), 'malachar_wide': ('08_malachar', 'malachar'),
 'malachar_close': ('08_malachar', 'malachar'), 'thorne_box': ('P1-08_thorne', 'thorne'), 'thorne_down': ('P2-17_thorne', 'thorne'),
 'stinger_box': ('P2-18_buyer', 'buyer'), 'stinger_open': ('P2-18_buyer', 'buyer'), 'stinger_reach': ('P3-21_buyer', 'buyer'),
}

out = Path('art_user_mouth'); out.mkdir(exist_ok=True)
for name, (mset, spk) in LIP.items():
    srcfile, box = MAP[name]
    for k in 'ABCDEF':
        mp = HEL / f'{k}.png' if mset == 'HELENA_P1-04' else files[f'{mset}_{k}.png']
        im = Image.open(mp).convert('RGB')
        if box:
            W, H = im.size; im = im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))
        im.save(out / f'{name}__{k}.png')
print('mouth pictures:', len(list(out.glob('*.png'))))

# timing
plan = json.load(open('plan_user.json')); tl = mc.Timeline(plan, Path('.').resolve())
speakers = {s for _, s in LIP.values()}
SHAPE = {'X': None, 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'B', 'H': 'C'}
n = int(tl.total * FPS) + 1
frames = {s: [None] * n for s in speakers}
tmp = Path(tempfile.mkdtemp())
for k, (si, li, sc, ln) in enumerate(tl.lines):
    if ln['speaker'] not in speakers: continue
    s0, s1 = tl.sp[k]; a = max(0, s0 - .1)
    wav, txt, js = tmp / f'{k}.wav', tmp / f'{k}.txt', tmp / f'{k}.json'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-to', f'{s1 + .15:.3f}', '-i', plan['audio'], '-ac', '1', '-ar', '48000', str(wav)], check=True)
    txt.write_text(ln['text'])
    subprocess.run([str(RHUBARB), '-q', '-f', 'json', '--dialogFile', str(txt), '-o', str(js), str(wav)], check=True, capture_output=True)
    cues = json.loads(js.read_text())['mouthCues']
    seq = []
    f0, f1 = int(a * FPS), min(n, int((s1 + .15) * FPS) + 1)
    for f in range(f0, f1):
        t = f / FPS - a; v = 'X'
        for c in cues:
            if c['start'] <= t < c['end']: v = c['value']
        seq.append(SHAPE[v])
    held = [seq[0]]; hold = 1                      # animate on twos: every mouth stays at least 2 frames
    for v in seq[1:]:
        if v != held[-1] and hold < 2: held.append(held[-1]); hold += 1
        elif v != held[-1]: held.append(v); hold = 1
        else: held.append(v); hold += 1
    frames[ln['speaker']][f0:f0 + len(held)] = held
    print(f"line {k + 1:2d} {ln['speaker']:10s} {sum(1 for x, y in zip(held, held[1:]) if x != y):3d} mouth changes  {ln['text'][:45]}")
json.dump({'fps': FPS, 'pictures': {k: v[1] for k, v in LIP.items()}, 'frames': frames}, open('lipsync.json', 'w'))
print('saved lipsync.json')
