"""Find faces in every plan image, then test every shot's opening and closing frame: a face that is only
partly inside the view (and not deliberately an extreme close-up) is reported. Writes faces.json."""
import json, os, sys
import cv2, numpy as np

plan = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'plan_user.json'))
det = None
faces = {}
for name, path in plan['images'].items():
    img = cv2.imread(path)
    if img is None or img.mean() < 3: faces[name] = []; continue
    h, w = img.shape[:2]
    if det is None or det.getInputSize() != (w, h):
        det = cv2.FaceDetectorYN.create(os.environ.get('YUNET', 'models/yunet/yunet.onnx'), '', (w, h), 0.6, 0.3, 5000)
    _, f = det.detect(img)
    out = []
    for r in (f if f is not None else []):
        x, y, fw, fh = r[:4]
        if fw < 0.025 * w: continue                      # background extras
        # the whole head: detector box grown for hair and chin
        out.append([float(v) for v in [max(0, x - .25 * fw) / w, max(0, y - .45 * fh) / h, min(w, x + 1.25 * fw) / w, min(h, y + 1.2 * fh) / h]])
    faces[name] = out
json.dump(faces, open('faces.json', 'w'), indent=1)


def window(name, box, cam):
    """Same maths as motion_comic.view, in 0..1 image fractions."""
    from PIL import Image
    W, H = Image.open(plan['images'][name]).size
    x0, y0, x1, y1 = box; bw, bh = (x1 - x0) * W, (y1 - y0) * H; cx, cy, z = cam
    w = min(bw, bh * 16 / 9) / z; h = w * 9 / 16
    l = x0 * W + (bw - w) * cx; t = y0 * H + (bh - h) * cy
    return [l / W, t / H, (l + w) / W, (t + h) / H]


problems = []
for si, sc in enumerate(plan['scenes']):
    for li, ln in enumerate(sc['lines']):
        for k, s in enumerate([ln.get('shot')] + ln.get('shots', [])):
            if not s or s['image'] not in faces: continue
            for end in ('from', 'to'):
                cam = s.get(end, s.get('from', [.5, .5, 1.0]))
                v = window(s['image'], s.get('box', [0, 0, 1, 1]), cam)
                for f in faces[s['image']]:
                    ix = max(0, min(v[2], f[2]) - max(v[0], f[0])); iy = max(0, min(v[3], f[3]) - max(v[1], f[1]))
                    inside = ix * iy / ((f[2] - f[0]) * (f[3] - f[1]))
                    big = (f[3] - f[1]) > 0.75 * (v[3] - v[1])          # face bigger than the frame: a deliberate extreme close-up
                    if 0.05 < inside < 0.97 and not big:
                        problems.append((si, li, k, end, s['image'], round(inside, 2), [round(c, 2) for c in f], [round(c, 2) for c in v]))
print(sum(len(v) for v in faces.values()), 'faces in', sum(1 for v in faces.values() if v), 'images')
for p in problems:
    print(f'scene {p[0]} line {p[1]} shot {p[2]} {p[3]:4s} {p[4]:18s} face {int(p[5]*100)}% in view  face={p[6]} view={p[7]}')
print(len(problems), 'cut faces')
