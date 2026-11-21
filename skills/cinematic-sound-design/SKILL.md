---
name: "cinematic-sound-design"
description: "Build the sound bed under a voiced video (trailer, drama, motion comic): recorded effects and designed layers anchored to words, a score placed by its climax word, ducking, silence, mix checks."
---

# Cinematic sound design for voiced videos

Use when a narrated or voiced video needs music, ambience, impacts, creatures or foley under the
dialogue. Distilled from building a 1:51 war-fantasy trailer; the numbers below are the ones that
worked there, so treat them as starting points.

## Order
1. Voices first, with line labels and word times. Every cue is anchored to a line or a word of it,
   never to a clock time, so re-voicing re-times the whole bed.
2. Pick the climax word. Place the score by it.
3. Recorded effects for anything real (guns, explosions, creatures, debris, radio, blades); designed
   layers only where nothing recorded exists (drones, heartbeat, risers, sub drops).
4. Duck under speech, make real silences, measure, then let a person judge short A/B/C clips.

## What makes an effect sound real
- **Gunshot:** crack (sharp transient), body (mid "thwack"), sub, mechanics (bolt, slide), tail
  (the place: a valley echo). Downrange, a supersonic round is crack then bang. For rapid fire keep
  the sub and tail short or it turns to mush.
- **Explosion:** crack, mid body, sub drop, debris (rock, gravel, glass), then tail and settling
  (stones falling, distant echo). The aftermath is what sells the size.
- One synthesized layer per effect sounds thin: that is the usual fault. Layer a recording over a
  quiet designed sub.

## Free sources you can use commercially
| Source | Licence | Notes |
|---|---|---|
| Sonniss GDC bundles (sonniss.com/gameaudiogdc) | Royalty-free, no attribution | Pro quality; big downloads; no AI training |
| Pixabay sound effects | Free, commercial use | Easiest to browse and preview |
| BigSoundBank | CC0 | Real field recordings |
| Freesound | Per sound | Filter to CC0 |

Avoid BBC Sound Effects for anything commercial (non-commercial licence). The workspace usually
cannot download from these sites: give the person a shopping list and ask them to attach files.
A good list for a battle piece: rifle shots with echo (3-4), a distant battle bed (30-60 s), big
explosions with debris (3), distant booms (2), rubble falling, a blade or sword draw, a creature
growl or roar, screams, radio static.

## Prepare the recordings
Convert each to 48 kHz mono WAV with a short name (`ffmpeg -i in.mp3 -ac 1 -ar 48000 battle.wav`),
then profile it: length, peak, a loudness envelope, and onsets, so each footstep or blast is cut
from its own start.

```python
import numpy as np, wave
def onsets(path, hop_s=.02, jump_db=9, floor_db=-30, min_gap=.6):
    w = wave.open(path); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
    hop = int(sr * hop_s)
    db = 20 * np.log10(np.array([np.sqrt((x[i:i + hop] ** 2).mean()) for i in range(0, len(x) - hop, hop)]) + 1e-9)
    out = []
    for i in range(5, len(db)):
        if db[i] - db[i - 5:i].mean() > jump_db and db[i] > floor_db and (not out or i * hop_s - out[-1] > min_gap):
            out.append(round(i * hop_s, 2))
    return out
```

A slice helper: cut, re-pitch, reverse, darken, fade.

```python
from scipy.signal import butter, sosfilt
SR = 48000
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x).astype(np.float32)
def rec(x, a=0.0, b=None, fade=.03, rate=1.0, rev=False, lowpass=None):
    x = x[int(a * SR):None if b is None else int(b * SR)].copy()
    if rate != 1.0: x = np.interp(np.arange(0, len(x) - 1, rate), np.arange(len(x)), x).astype(np.float32)
    if rev: x = x[::-1].copy()
    if lowpass: x = lp(x, lowpass)
    k = int(fade * SR)
    if k and len(x) > 2 * k: x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k)
    return x
```

## Placement rules
- Big impacts land 0.25-0.45 s after the word they illustrate, or just after the line ("Then a
  thousand." -> boom). On the word, they bury it.
- A growl or roar must not run over the next line: shorten it.
- Re-pitch repeats (0.85-1.06x) so no two explosions match. Five copies of one scream at
  0.78-1.25x, staggered by about 0.2 s, make a crowd.
- Reverse, slow (0.8x) and low-pass a roar for "something whispering".
- Let a battle bed drop to about 18% for a vision or memory, and fade it out a second before the
  quietest line, so the quiet moment arrives as a contrast.
- Distant explosions low-passed (500-900 Hz) before the battle reaches the characters tell the viewer
  it is coming.
- A pre-existing score: shift it so its peak lands on the climax word. Cut it to silence with a
  0.35 s fade rather than letting it fade on its own after the climax.
- Synthesized drones, heartbeat, risers and sub drops blend with real recordings. Synthesized brass
  next to a real orchestra does not: mute designed brass hits while the score plays.

## Buses, ducking and silence
Keep three buses: music (score, drone, pads), ambience (wind, battle), hits (impacts, creature,
blade). Duck each under speech; duck the music's voice band harder than the rest so the music stays
big.

```python
def duck_curve(speech, n, amount, pre=.15, post=.25, smooth=.12):
    c = np.ones(n, np.float32)
    for a, b in speech: c[max(0, int((a - pre) * SR)):int((b + post) * SR)] = amount
    k = int(smooth * SR); return np.convolve(c, np.ones(k) / k, 'same').astype(np.float32)

def bp(x, a, b): return sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x).astype(np.float32)
mid = bp(music, 900, 4000)
bed = ((music - mid) * duck_curve(sp, n, .6) + mid * duck_curve(sp, n, .35)
       + amb * .65 * duck_curve(sp, n, .35) + hits * .5 * duck_curve(sp, n, .6))

# real silence (e.g. before a title): gate the whole bed, then let the title hit start clean
gate = np.ones(n, np.float32); gate[int(s0 * SR):int(s1 * SR)] = 0
k = int(.25 * SR); gate = np.convolve(gate, np.ones(k) / k, 'same').astype(np.float32)
gate[int(s1 * SR) - 50:] = 1.0
bed *= gate
```

A quiet, intimate moment: dip the whole bed about 3.5 dB under those lines as well as softening
the voices. If the video tool only adds a music file without ducking it (motion_comic.py
multiplies `"music": {"file"}` by 0.12 x volume), write the finished bed to a WAV and pass it at
unity (`"volume": 8.333`).

## Checks
- **Voice over bed, per line,** in 150-6,000 Hz: a median of 12-16 dB works online. Flag any line under
  about 6 dB unless the hit is meant to cover it.
- **Recognizer on the finished mix,** not only on the clean voices. A masked word shows up there.
- **Loudness:** `ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`. Integrated -14 LUFS for online,
  true peak at or under -1 dBTP, and loudness range: under about 5 LU reads flat; quieter quiet
  moments raise it.
- **Silence is silence:** sample values at zero where you meant it.
- **Taste:** three short, loudness-matched A/B/C clips of the moment in question. The person picks.