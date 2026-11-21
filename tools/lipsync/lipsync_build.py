#!/usr/bin/env python3
"""Mouth timing for every on-screen spoken line of a motion_comic plan.

Inputs
  plan.json      the motion_comic plan (after narration: needs "audio" and its label file)
  map.json       which plan picture shows which speaker, e.g. {"osric": "osric", "helena_box": "healer"}
  mouths/        six versions of each mapped picture, only the mouth changed, named <picture>__A.png .. __F.png
                 (A closed M/B/P, B teeth S/EE, C half-open EH, D wide AH, E round O, F pucker OO).
                 Same size and crop as the picture in the plan.

Output
  lipsync.json   per speaker, the mouth shape for every frame (null = the picture's own resting mouth)

Uses Rhubarb Lip Sync (https://github.com/DanielSWolf/rhubarb-lip-sync); set RHUBARB=/path/to/rhubarb if it is not on PATH.
Needs motion_comic.py (from skills/motion-comic-video) importable, for the plan's timeline.

  python3 lipsync_build.py plan.json map.json mouths/ [--fps 24] [--out lipsync.json]
"""
import argparse, json, os, subprocess, tempfile
from pathlib import Path
import motion_comic as mc

SHAPE = {'X': None, 'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'B', 'H': 'C'}  # G (F/V) -> teeth, H (L) -> half-open


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path); ap.add_argument('map', type=Path); ap.add_argument('mouths', type=Path)
    ap.add_argument('--fps', type=int, default=24); ap.add_argument('--out', type=Path, default=Path('lipsync.json'))
    ap.add_argument('--min-hold', type=int, default=2, help='frames each mouth stays on screen (2 = "on twos")')
    a = ap.parse_args()
    rhubarb = os.environ.get('RHUBARB', 'rhubarb')
    plan = json.loads(a.plan.read_text()); pics = json.loads(a.map.read_text())
    for pic in pics:
        missing = [k for k in 'ABCDEF' if not (a.mouths / f'{pic}__{k}.png').exists()]
        if missing: raise SystemExit(f'{pic}: missing mouths {missing} in {a.mouths}')
    tl = mc.Timeline(plan, a.plan.resolve().parent)
    speakers = set(pics.values()); n = int(tl.total * a.fps) + 1
    frames = {s: [None] * n for s in speakers}
    tmp = Path(tempfile.mkdtemp())
    for k, (si, li, sc, ln) in enumerate(tl.lines):
        if ln['speaker'] not in speakers: continue
        s0, s1 = tl.sp[k]; t0 = max(0, s0 - .1)
        wav, txt, js = tmp / f'{k}.wav', tmp / f'{k}.txt', tmp / f'{k}.json'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t0:.3f}', '-to', f'{s1 + .15:.3f}', '-i',
                        str(a.plan.resolve().parent / plan['audio']), '-ac', '1', '-ar', '48000', str(wav)], check=True)
        txt.write_text(ln['text'])
        subprocess.run([rhubarb, '-q', '-f', 'json', '--dialogFile', str(txt), '-o', str(js), str(wav)], check=True, capture_output=True)
        cues = json.loads(js.read_text())['mouthCues']
        f0, f1 = int(t0 * a.fps), min(n, int((s1 + .15) * a.fps) + 1)
        seq = []
        for f in range(f0, f1):
            t = f / a.fps - t0; v = 'X'
            for c in cues:
                if c['start'] <= t < c['end']: v = c['value']
            seq.append(SHAPE[v])
        held, hold = [seq[0]], 1
        for v in seq[1:]:
            if v != held[-1] and hold < a.min_hold: held.append(held[-1]); hold += 1
            elif v != held[-1]: held.append(v); hold = 1
            else: held.append(v); hold += 1
        frames[ln['speaker']][f0:f0 + len(held)] = held
        print(f"line {k + 1:3d} {ln['speaker']:12s} {sum(x != y for x, y in zip(held, held[1:])):3d} mouth changes  {ln['text'][:50]}")
    a.out.write_text(json.dumps({'fps': a.fps, 'mouths': str(a.mouths.resolve()), 'pictures': pics, 'frames': frames}))
    print('wrote', a.out)


if __name__ == '__main__':
    main()
