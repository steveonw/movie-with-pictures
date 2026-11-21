"""Re-aim every shot so the important heads stay whole: slide the view (cx, cy) to include them, and zoom out
when they can't all fit. Important = the biggest head in the picture plus any head at least 60% its height.
Uses faces.json from face_audit.py. Rewrites the plan in place and lists what moved."""
import json, os, sys
from PIL import Image

path = sys.argv[1]; plan = json.load(open(path)); faces = json.load(open('faces.json'))
M = 0.02   # margin around a head, as a fraction of the image
sizes = {}


def fit(name, box, cam):
    if name not in sizes: sizes[name] = Image.open(plan['images'][name]).size
    W, H = sizes[name]; x0, y0, x1, y1 = box
    fs = [f for f in faces.get(name, []) if f[0] >= x0 - .01 and f[2] <= x1 + .01 and f[1] >= y0 - .01 and f[3] <= y1 + .01]
    if not fs: return cam
    big = max(f[3] - f[1] for f in fs); imp = [f for f in fs if f[3] - f[1] >= .6 * big]
    bw, bh = (x1 - x0) * W, (y1 - y0) * H; cx, cy, z = cam

    def need(group):
        return (max(0, min(f[0] for f in group) - M) * W, max(0, min(f[1] for f in group) - M) * H,
                min(1, max(f[2] for f in group) + M) * W, min(1, max(f[3] for f in group) + M) * H)

    for group in (imp, [max(fs, key=lambda f: f[3] - f[1])]):
        L, T, R, B = need(group)
        zz = z
        while True:
            w = min(bw, bh * 16 / 9) / zz; h = w * 9 / 16
            if (R - L <= w and B - T <= h) or zz <= 1.0: break
            zz = max(1.0, zz - .02)
        if R - L <= w and B - T <= h: break
    # slide the view the least distance that brings [L,R]x[T,B] inside it
    l = x0 * W + (bw - w) * cx; t = y0 * H + (bh - h) * cy
    if B - T > h: t = T                      # head taller than the frame: keep the top of it (deliberate close-up)
    else:
        if T < t: t = T
        if B > t + h: t = B - h
    if R - L <= w:
        if L < l: l = L
        if R > l + w: l = R - w
    ncx = 0.5 if bw - w < 1 else min(1, max(0, (l - x0 * W) / (bw - w)))
    ncy = 0.5 if bh - h < 1 else min(1, max(0, (t - y0 * H) / (bh - h)))
    return [round(ncx, 3), round(ncy, 3), round(zz, 3)]


moved = 0; prev = None
for sc in plan['scenes']:
    for ln in sc['lines']:
        for s in [ln.get('shot')] + ln.get('shots', []):
            if not s: continue
            if s['image'] == 'black': prev = s; continue
            a = s.get('from', [.5, .5, 1.0]); b = s.get('to', a)
            na = fit(s['image'], s.get('box', [0, 0, 1, 1]), a); nb = fit(s['image'], s.get('box', [0, 0, 1, 1]), b)
            if s.get('tr') == 'cont' and prev and prev['image'] == s['image']:
                na = list(prev['to'])                     # a continued move starts where the last one ended
            prev = s
            if na != a or nb != b:
                moved += 1
                print(f"{s['image']:18s} {a} -> {na}   |   {b} -> {nb}")
            s['from'], s['to'] = na, nb
json.dump(plan, open(path, 'w'), indent=1, ensure_ascii=False)
print(moved, 'shots re-aimed')
