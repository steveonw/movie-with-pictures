#!/usr/bin/env python3
"""Render a motion_comic plan with lip-sync. While a mapped picture's speaker is talking, the picture is swapped
frame by frame for its mouth version (<mouths>/<picture>__<shape>.png) from lipsync.json. The camera moves, cuts,
effects and sound are untouched, because only the picture file changes.

Same arguments as motion_comic.py:   LIPSYNC=lipsync.json python3 render_lipsync.py plan.json --out final.mp4
"""
import json, os
from pathlib import Path
import motion_comic as mc

L = json.loads(Path(os.environ.get('LIPSYNC', 'lipsync.json')).read_text())
FPS, PICS, FR, MDIR = L['fps'], L['pictures'], L['frames'], Path(L['mouths'])
_shot = mc.Pictures.shot


def shot(self, s, t):
    p = s.get('path')
    if p is not None:
        name = Path(p).stem; spk = PICS.get(name)
        if spk:
            f = int(round(t * FPS)); seq = FR[spk]
            k = seq[f] if 0 <= f < len(seq) else None
            if k: s = dict(s, path=MDIR / f'{name}__{k}.png')
    return _shot(self, s, t)


mc.Pictures.shot = shot
if __name__ == '__main__':
    mc.main()
