#!/usr/bin/env python3
"""Sound bed for Blackfeather: music + recorded effects, anchored to the plan's words, music ducked
under speech. Writes bed.wav (mono 48 kHz) to pass to motion_comic.py as "music": {"file": "bed.wav",
"volume": 8.333} (renderer multiplies a music file by 0.12, so 8.333 = unity).

Cues live on plan lines as "bed": [{"file", "at", "vol", ...}]:
  music=True, start=s   start a music track (s seconds into it) at the cue; runs until the next music
                        cue or STOP_MUSIC (short fade).
  file="STOP_MUSIC"     music stops dead (0.06 s fade).
  file="DUCK", dur=d    pull the music down for d seconds (under a big effect).
  dur=d, fade=f         play only d seconds of an effect/ambience, fading out over f.
"""
import json, sys, wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt, resample_poly

sys.path.insert(0, str(Path(__file__).parent))
import motion_comic as mc

SR = 48000
SFX = Path(__file__).parent / 'sfx'


def load(name):
    with wave.open(str(SFX / f'{name}.wav')) as w:
        ch = w.getnchannels(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x.reshape(-1, ch).mean(1)


def norm_peak(x, db=-3):
    return x * (10 ** (db / 20) / max(1e-9, np.abs(x).max()))


def norm_rms(x, db=-24):
    return x * (10 ** (db / 20) / max(1e-9, np.sqrt((x ** 2).mean())))


def pitch(x, semis):  # resample: changes length too, fine for creatures
    r = 2 ** (semis / 12); up, down = (100, int(round(100 * r)))
    return resample_poly(x, up, down).astype(np.float32)


def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x).astype(np.float32)
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x).astype(np.float32)


def seg(x, a, b=None, fade=.03):
    y = x[int(a * SR): None if b is None else int(b * SR)].copy(); n = int(fade * SR)
    if n and len(y) > 2 * n: y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
    return y


def layer(*parts):  # (signal, offset_s, gain)
    n = max(int(o * SR) + len(s) for s, o, g in parts); out = np.zeros(n, np.float32)
    for s, o, g in parts: i = int(o * SR); out[i:i + len(s)] += s * g
    return out


def designed():
    S = {k: load(k) for k in ['monster_roar', 'tiger_roar', 'hawk_cry', 'bear_growl', 'beast_snarl', 'screech', 'boom',
                              'explosion_debris', 'crate_smash', 'wood_smash', 'fall_impact', 'bottle_shatter', 'shimmer',
                              'wind_gust', 'fire_fx', 'small_scream']}
    shimmer = norm_peak(S['shimmer'])
    d = {
        'owlbear_roar': norm_peak(layer((norm_peak(S['monster_roar']), 0, .9), (norm_peak(S['tiger_roar']), .05, .7),
                                        (norm_peak(pitch(S['hawk_cry'], -3)), .25, .45))),
        'owlbear_screech': norm_peak(layer((norm_peak(seg(S['screech'], 0)), 0, .9), (norm_peak(S['monster_roar']), .1, .5),
                                           (norm_peak(S['hawk_cry']), 0, .5))),
        'growl_low': norm_peak(layer((norm_peak(pitch(S['bear_growl'], -2)), 0, .8), (norm_peak(S['beast_snarl']), .1, .6))),
        'growl_mix': norm_peak(layer((norm_peak(S['beast_snarl']), 0, .7), (norm_peak(seg(S['monster_roar'], 0, 2.0, .4)), .1, .4))),
        'crash_mix': norm_peak(layer((norm_peak(S['wood_smash']), 0, .9), (norm_peak(S['fall_impact']), 0, .8),
                                     (norm_peak(S['bottle_shatter']), .12, .35))),
        'explosion_mix': norm_peak(layer((norm_peak(S['boom']), 0, 1.0), (norm_peak(S['explosion_debris']), .02, .7),
                                         (norm_peak(S['crate_smash']), .08, .6))),
        'shield_hit': norm_peak(layer((norm_peak(hp(seg(S['boom'], 0, .6, .05), 150)), 0, .8),
                                      (norm_peak(seg(shimmer, 33.0, 34.2, .05)), 0, .6))),
        'shimmer_hit': norm_peak(seg(shimmer, 32.6, 35.0, .2)),
        'heal_spell': norm_peak(seg(shimmer, 31.5, 33.5, .3)),
        'wand_cast': norm_peak(layer((norm_peak(seg(shimmer, 33.0, 34.0, .1)), 0, .7), (norm_peak(seg(S['wind_gust'], .3, 1.3, .1)), 0, .6))),
        'fireball': norm_peak(layer((norm_peak(seg(S['wind_gust'], .2, 2.2, .2)), 0, .8), (norm_peak(seg(S['fire_fx'], 6.0, 8.5, .3)), .1, .7))),
        'demon_roar': norm_peak(pitch(S['monster_roar'], -4)),
        'cub_squeak': norm_peak(S['small_scream']),
    }
    big = layer((d['owlbear_roar'], 0, .9), (norm_peak(pitch(S['bear_growl'], -3)), .05, .6), (norm_peak(lp(S['boom'], 200)), 0, .7))
    d['owlbear_roar_big'] = norm_peak(pitch(big, -2))
    return d


def main():
    plan_p = Path(sys.argv[1] if len(sys.argv) > 1 else 'plan.json'); base = plan_p.resolve().parent
    plan = json.loads(plan_p.read_text()); tl = mc.Timeline(plan, base)
    total = tl.total; n = int(total * SR) + SR
    D = designed(); cache = {}

    def get(name):
        if name in D: return D[name]
        if name not in cache: cache[name] = load(name)
        return cache[name]

    music_events, stops, ducks, fx = [], [], [], []
    for k, (si, li, sc, ln) in enumerate(tl.lines):
        for c in ln.get('bed', []):
            t = tl.word(k, c.get('at'))
            if c['file'] == 'STOP_MUSIC': stops.append(t)
            elif c['file'] == 'DUCK': ducks.append((t, c.get('dur', 1.5)))
            elif c.get('music'): music_events.append((t, c))
            else: fx.append((t, c))

    # music: each track runs from its cue to the next music cue / stop
    music = np.zeros(n, np.float32)
    ends = sorted([t for t, _ in music_events] + stops + [total])
    for t, c in music_events:
        end = min([e for e in ends if e > t + 1e-3] or [total])
        x = norm_rms(get(c['file']), -22)
        y = seg(x, c.get('start', 0), c.get('start', 0) + (end - t) + .06, fade=0)
        fi = int(.25 * SR) if c.get('start', 0) > 0 else 0
        if fi and len(y) > fi: y[:fi] *= np.linspace(0, 1, fi)
        fo = int(.06 * SR) if end in stops else int(.4 * SR)
        y = y[:int((end - t) * SR) + (int(.4 * SR) if end not in stops else 0)]
        if len(y) > fo: y[-fo:] *= np.linspace(1, 0, fo)
        i = int(t * SR); music[i:i + len(y)] += y[:n - i] * c.get('vol', 1.0)

    # duck music under speech (-10 dB) and under DUCK cues (-14 dB), smoothed
    g = np.ones(n, np.float32)
    for s0, s1 in tl.sp: g[int(max(0, s0 - .08) * SR):int((s1 + .15) * SR)] = 10 ** (-13 / 20)
    for t, d in ducks: g[int(t * SR):int((t + d) * SR)] = np.minimum(g[int(t * SR):int((t + d) * SR)], 10 ** (-14 / 20))
    k = int(.12 * SR); g = np.convolve(g, np.ones(k) / k, mode='same').astype(np.float32)
    bed = music * g

    for t, c in fx:
        x = get(c['file'])
        if c['file'].startswith('amb_') or c['file'] == 'battle': x = norm_rms(x, -26)
        elif c['file'] not in D: x = norm_peak(x)
        if c.get('dur'):
            x = x[:int(c['dur'] * SR)].copy(); f = int(c.get('fade', .3) * SR)
            if len(x) > f: x[-f:] *= np.linspace(1, 0, f)
        x = x * .5 * c.get('vol', 1.0)  # effects sit about 6 dB under full scale before the final loudness pass
        i = int(t * SR); bed[i:i + len(x)] += x[:n - i]

    bed = bed[:int(total * SR)]
    with wave.open(str(base / 'bed.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(bed, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f'bed.wav {total:.1f}s: {len(music_events)} music cues, {len(stops)} stops, {len(fx)} effects; peak {20*np.log10(np.abs(bed).max()+1e-9):.1f} dBFS')
    for w_ in tl.warn: print('  note:', w_)


if __name__ == '__main__':
    main()
