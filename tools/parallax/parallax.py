"""Multiplane parallax shot from three layers (background, character, foreground).
Slow push-in and drift with depth, swaying foreground plants, a little cape and hair movement,
a pulsing sun glow and drifting light motes. Writes meadow.mp4 (1920x1080, 24 fps)."""
import subprocess, sys
import numpy as np, cv2
from PIL import Image

W, H, FPS, DUR = 1920, 1080, 24, 12.0
CW, CH = 1672, 941                                  # canvas = size of the source pictures
S, X0, Y0 = 0.76, 216, 120                           # matched size; moved 150px left so the peak stays visible (bg layer is framed differently)
FOCUS = (665, 520)
SHIFT = -150                                        # after matching her light, move her left so the peak stays visible                                  # camera pushes toward her
rng = np.random.default_rng(7)


def load(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.float32) / 255


bg = load('bg.png'); fg = load('fg_white.png'); comp = load('composite.png')
ch_src = load('char_white.png')

# --- character into canvas space at her matched size and position
ch = np.zeros((CH, CW, 4), np.float32)
small = cv2.resize(ch_src, (int(CW * S), int(CH * S)), interpolation=cv2.INTER_AREA)
h, w = small.shape[:2]; ch[Y0:Y0 + h, X0:X0 + w] = small[:CH - Y0, :CW - X0]

# --- light her like the combined picture: per-channel gain/offset fitted where she is solid
m = ch[..., 3] > 0.95
for c in range(3):
    A = np.stack([ch[..., c][m], np.ones(m.sum())], 1)
    g, o = np.linalg.lstsq(A, comp[..., c][m], rcond=None)[0]
    ch[..., c] = np.clip(ch[..., c] * g + o, 0, 1)
    print(f'channel {"RGB"[c]}: gain {g:.2f} offset {o:+.3f}')
# warm rim on the sun side (right): edge pixels whose outside neighbour is to the right
al = ch[..., 3]
edge = np.clip(al - cv2.warpAffine(al, np.float32([[1, 0, -6], [0, 1, 0]]), (CW, CH)), 0, 1)
edge = cv2.GaussianBlur(edge, (0, 0), 2.0) * al
rim = np.array([1.0, .78, .45], np.float32)
ch[..., :3] = np.clip(ch[..., :3] + edge[..., None] * rim * .55, 0, 1)

# now move her left (lighting was matched at the measured position)
ch = np.roll(ch, SHIFT, axis=1); ch[:, SHIFT:] = 0
al = ch[..., 3]; X0 = X0 + SHIFT
# contact shadow under her boots, painted onto the background
ys, xs = np.where(al > .5); foot_y = ys.max(); fx0, fx1 = xs[ys > foot_y - 40].min(), xs[ys > foot_y - 40].max()
sh = np.zeros((CH, CW), np.float32)
cv2.ellipse(sh, ((fx0 + fx1) // 2, foot_y - 4), ((fx1 - fx0) // 2 + 40, 16), 0, 0, 360, 1.0, -1)
sh = cv2.GaussianBlur(sh, (0, 0), 10) * .45
bg[..., :3] *= (1 - sh[..., None] * np.array([.55, .6, .7], np.float32))

yy, xx = np.mgrid[0:CH, 0:CW].astype(np.float32)
# foreground sway: anchored at the bottom edge (grass) and the side edges (branches)
w_fg = np.clip((CH - yy) / 380, 0, 1) ** 1.2 * np.clip(np.minimum(xx, CW - xx) / 260, 0, 1)
# cape: the flowing part left of her body, stronger further out and lower
cx0 = X0 + 760 * S
w_cape = np.clip((cx0 - xx) / (150 * S), 0, 1) * np.clip((yy - (Y0 + 260 * S)) / (120 * S), 0, 1) * (yy < Y0 + 600 * S)
# hair: the loose sides of her hair, not the face
hx0, hx1 = X0 + 735 * S, X0 + 845 * S
w_hair = ((xx < hx0) | (xx > hx1)).astype(np.float32) * np.clip((yy - (Y0 + 60 * S)) / (120 * S), 0, 1) * (yy < Y0 + 270 * S) * (xx > X0 + 640 * S) * (xx < X0 + 960 * S)
w_cape = cv2.GaussianBlur(w_cape.astype(np.float32), (0, 0), 12); w_hair = cv2.GaussianBlur(w_hair.astype(np.float32), (0, 0), 8)

# light motes: depth between her and the foreground
N = 46
mx, my = rng.uniform(0, CW, N), rng.uniform(150, CH - 120, N)
mv = rng.uniform(6, 18, N); msz = rng.uniform(1.5, 4.5, N); mph = rng.uniform(0, 6.28, N)
SUN = (1225, 293)
sun_d = np.sqrt((xx - SUN[0]) ** 2 + (yy - SUN[1]) ** 2)
sun_glow = np.exp(-(sun_d / 210) ** 2)[..., None] * np.array([1.0, .75, .4], np.float32)


def ease(u): return u * u * (3 - 2 * u)


def place(layer, z, f, pan, t_extra=1.0):
    """Scale about the focus point by 1+(z-1)*f, shift by pan*f, map canvas -> output frame."""
    k = (1 + (z - 1) * f) * t_extra; sx = W / CW
    M = np.float32([[k * sx, 0, (FOCUS[0] - k * FOCUS[0] + pan * f) * sx + (1 - t_extra) * 0],
                    [0, k * sx, (FOCUS[1] - k * FOCUS[1]) * sx]])
    return cv2.warpAffine(layer, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE if layer.shape[2] == 3 else cv2.BORDER_CONSTANT)


def over(dst, src):
    a = src[..., 3:4]; return dst * (1 - a) + src[..., :3] * a


ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', 'meadow_silent.mp4'], stdin=subprocess.PIPE)
n = int(DUR * FPS)
for i in range(n):
    t = i / FPS; u = ease(i / (n - 1))
    z = 1.0 + .11 * u; pan = -40 + 80 * u                # push in, drifting right
    # background: far, moves little; slightly oversized so drift never shows an edge
    b = bg[..., :3] + sun_glow * (.16 + .06 * np.sin(2 * np.pi * t / 4.0))
    frame = place(np.clip(b, 0, 1), z, .35, pan, t_extra=1.04)
    # character with cape and hair moving
    gust = .6 + .4 * np.sin(2 * np.pi * t / 5.5)
    dx = (3.2 * np.sin(2 * np.pi * .55 * t) * gust) * w_cape + (1.4 * np.sin(2 * np.pi * .7 * t + 1.0) * gust) * w_hair
    dy = (1.6 * np.sin(2 * np.pi * .55 * t + 1.3) * gust) * w_cape
    c = cv2.remap(ch, (xx - dx).astype(np.float32), (yy - dy).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    frame = over(frame, place(c, z, 1.0, pan))
    # motes
    mot = np.zeros((CH, CW, 4), np.float32)
    for j in range(N):
        px = (mx[j] + mv[j] * t * 1.3) % CW; py = my[j] - mv[j] * t * .6 + 6 * np.sin(t * .8 + mph[j])
        a = .35 + .35 * np.sin(t * 1.7 + mph[j])
        cv2.circle(mot, (int(px), int(py)), int(msz[j] * 2.2), (1.0, .85, .55, a * .35), -1, cv2.LINE_AA)
        cv2.circle(mot, (int(px), int(py)), max(1, int(msz[j] * .8)), (1.0, .95, .8, a), -1, cv2.LINE_AA)
    mot = cv2.GaussianBlur(mot, (0, 0), 1.2)
    frame = over(frame, place(mot, z, 1.25, pan))
    # foreground plants swaying, closest layer moves most
    sway = 4.5 * np.sin(2 * np.pi * .42 * t + xx * .006 + yy * .004) * gust + 1.5 * np.sin(2 * np.pi * 1.1 * t + xx * .02)
    f2 = cv2.remap(fg, (xx - sway * w_fg).astype(np.float32), yy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    frame = over(frame, place(f2, z, 1.6, pan, t_extra=1.02))
    # fade in / out
    fade = min(1, t / .8, (DUR - t) / .8)
    ff.stdin.write((np.clip(frame * fade, 0, 1) * 255).astype(np.uint8).tobytes())
    if i % 48 == 0: print(f'frame {i}/{n}', flush=True)
ff.stdin.close(); ff.wait()
print('done')
