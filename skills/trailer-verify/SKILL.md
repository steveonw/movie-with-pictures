---
name: "trailer-verify"
description: "Blind QA for a voiced video built from a motion-comic plan.json: one script checks picture, sound, speech, loudness, flashes and captions, writes a pass/warn/fail report, and fails the build."
---

# Trailer verify

Use this before handing over any voiced video built from a `plan.json` (motion-comic-video
format): a trailer, motion comic or drama. The agent cannot watch or listen to the result, so
this turns the problems it can't see into numbers, in one report, and exits 1 on any FAIL so a
build can refuse to ship. Run it on the rough cut and again on the final.

Validated on two cuts of the same 2-minute trailer. On the version a human panel had criticised,
it failed on exactly what they found: two face ping-pongs, a repeated two-shot, a repeated horde
shot, an over-zoomed strip, and no silence anywhere. On the fixed version it had no failures, and
its warnings were all true leftovers.

## Run
```bash
python trailer_verify.py plan.json final.mp4 --asr-dir models/sherpa-onnx-zipformer-small-en-2023-06-26 --out checks.md
```
- Reads the plan's `"audio"` (clean voices), `"timestamps"` (line labels), `"images"`, `"width"`,
  `"fps"`, and the bed from `"music": {"file"}` (or `--bed bed.wav`).
- Needs ffmpeg/ffprobe, numpy, Pillow, scipy; sherpa-onnx and the zipformer model for the two
  recognizer checks (the same model as `check_audio.py`). Takes about 20 s for a 2-minute video.
- Writes `checks.md` (FAIL, WARN, PASS, INFO, then what it cannot check) and prints the FAIL and
  WARN lines.

## What it checks
| Area | Check | Fails when |
|---|---|---|
| Picture | Same image, same crop, nearly the same framing within 4 lines (the face ping-pong) | Always |
| Picture | Magnification of source pixels: output width / visible source width | Over 3.0x (warn over 1.8x) |
| Picture | Bright flashes (mean-luma jump over 20% of full scale) | More than 3 in any second |
| Picture | Very dark frames mid-line; moving shots whose picture doesn't change | Warn only |
| Plan | Anchor words that appear twice in their line without `#2` | Warn only |
| Sound | Voice over bed per line, in the weakest quarter of its 50 ms voiced slices (150-6,000 Hz) | Under 0 dB **and** the recognizer mishears that line in the mix |
| Sound | Longest true silence (below -60 dBFS) | Warn if under 0.8 s |
| Speech | Recognizer per line on clean voices and on the final mix | A line over 50% wrong; total over 8%; mix more than 1.5 points worse than clean |
| Loudness | Integrated, true peak, loudness range (`ebur128=peak=true`) | Off -14 by more than 1 LUFS; true peak over -1 dBTP (warn LRA under 4 LU) |
| File | Video vs audio duration; bitrate | Durations differ by over 0.1 s (warn over 8 Mb/s) |
| Captions | Characters a second per line | Warn over 20 |

The masking rule needs both signals on purpose. A level measurement alone flags a boom that
only overlaps the end of a word the listener still hears; the recognizer alone misses a line
that is barely surviving. Together, the level reading flags the line and the recognizer decides
whether it is a failure.

## Thresholds and waivers
Override any default with a `"qc"` block in the plan, e.g. `"qc": {"lufs": -16, "mag_fail": 2.5}`.
Waive a check for one line or shot when the effect is deliberate, and say why in the plan:
- `"allow_soft": true`: a deliberately soft image (an abstract ember sky).
- `"allow_masking": true`: a hit is meant to cover the line.
- `"dark_ok": true`: a deliberately dark frame.

Shots on images named `BLACK` or `TITLE` are skipped by the picture checks. Never waive a
failure just to get a green report: fix it, or explain the waiver to the person.

## Reading the report
- **FAIL:** fix before handing over. The message says what to do (zoom out or use a sharper
  image; move the hit after the word; reframe one of the two repeated shots).
- **WARN:** tell the person in one line each, grouped. Recognizer quirks ("formed the line" for
  "Form the line") are usually fine; a quiet line heard wrong may be worth softening less.
- **INFO:** most-used images, the largest magnification, the voice-over-bed median. Useful in a
  write-up.
- The final section lists what no script checks: whether the story is clear, the ending is
  withheld and the pacing builds (a person watches a rough cut); whether the voices act and the
  layers blend (a person listens); contradictions in the script (a person or a model reads it).
  Say so in the handover instead of "all checks pass": "all automated checks pass" is the
  honest phrasing.

## trailer_verify.py

```python
#!/usr/bin/env python3
"""Blind QA for a voiced video built from a motion-comic plan.json: every check that stands in for
watching and listening, in one report. FAIL lines make the exit code 1, so a build can refuse to ship.

  python trailer_verify.py plan.json final.mp4 [--asr-dir DIR] [--bed bed.wav] [--out checks.md]

Reads the plan's "audio" (clean voices), "timestamps" (line labels), "words" (word times), "images",
"width", and optionally a "qc" block that overrides the thresholds below. Needs ffmpeg/ffprobe,
numpy, Pillow, scipy; sherpa-onnx and the zipformer model for the two recognizer checks.

Plan waivers (on a line, or on a shot inside it):
  "allow_soft": true      skip the magnification check for that shot (a deliberately soft image)
  "allow_masking": true   a hit is meant to cover that line: voice-over-bed is reported, not failed
  "dark_ok": true         a deliberately dark frame
Shots on images named BLACK or TITLE are skipped by the picture checks.
"""
import argparse, difflib, json, math, re, subprocess, sys, wave
from pathlib import Path
import numpy as np

QC = {  # defaults, overridable with plan["qc"]
    'repeat_window_lines': 4, 'repeat_center': .15, 'repeat_zoom': .15,
    'mag_warn': 1.8, 'mag_fail': 3.0,
    'vob_warn_db': 3.0, 'vob_fail_db': 0.0,      # 25th-percentile margin over 50 ms voiced slices
    'asr_line_warn': .2, 'asr_line_fail': .5, 'asr_total_fail': .08, 'asr_mix_extra': .015,
    'lufs': -14.0, 'lufs_tol': 1.0, 'true_peak_max': -1.0, 'lra_warn': 4.0,
    'flash_jump': .2, 'flash_per_s_max': 3,
    'dark_luma': 12, 'frozen_diff': .4, 'sync_tol_s': .1,
    'cps_warn': 20, 'bitrate_warn_mbps': 8.0, 'silence_db': -60, 'silence_min_s': .8,
}
R = []   # (level, area, message)
def add(level, area, msg): R.append((level, area, msg))


def norm(s): return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def read_labels(p):
    out = []
    for l in Path(p).read_text(encoding='utf-8-sig').splitlines():
        q = l.split('\t')
        if len(q) >= 2 and not l.startswith('\\'): out.append((float(q[0]), float(q[1]), q[2] if len(q) > 2 else ''))
    return out


def pcm(path, sr, mono=True):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def probe(path, entries):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', entries, '-of', 'json', str(path)], capture_output=True, text=True).stdout
    return json.loads(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path); ap.add_argument('video', type=Path)
    ap.add_argument('--asr-dir'); ap.add_argument('--bed'); ap.add_argument('--out', default='checks.md')
    a = ap.parse_args()
    base = a.plan.resolve().parent; plan = json.loads(a.plan.read_text(encoding='utf-8')); qc = {**QC, **plan.get('qc', {})}
    W = int(plan.get('width', 1280)); fps = int(plan.get('fps', 24))
    flat = [(sc, ln) for sc in plan['scenes'] for ln in sc['lines']]
    shots_of = lambda ln: ([ln['shot']] if ln.get('shot') else []) + list(ln.get('shots', []))
    imgs = plan.get('images', {})

    # ---- line times: match plan lines to the timestamp labels, in order
    labels = read_labels(base / plan['timestamps']); sp, j = [], 0
    for sc, ln in flat:
        best, br = None, 0
        for c in range(j, min(len(labels), j + 20)):
            r = difflib.SequenceMatcher(None, norm(ln['text']), norm(labels[c][2])).ratio()
            if r > br: best, br = c, r
        if best is None or br < .6: sys.exit(f'line not found in timestamps: {ln["text"][:50]}')
        sp.append(labels[best][:2]); j = best + 1

    # ---- PLAN: repeated framing, magnification, ambiguous anchors
    from PIL import Image
    sizes = {}
    def size(name):
        p = base / imgs.get(name, name)
        if p not in sizes:
            with Image.open(p) as im: sizes[p] = im.size
        return sizes[p]
    seq = [(k, ln, shots_of(ln)) for k, (sc, ln) in enumerate(flat)]
    rep = 0
    for i, (k, ln, shs) in enumerate(seq):
        for jj in range(i + 1, min(len(seq), i + 1 + qc['repeat_window_lines'])):
            for s1 in shs:
                for s2 in seq[jj][2]:
                    if s1['image'] != s2['image'] or s1['image'] in ('BLACK', 'TITLE') or s2.get('tr') == 'cont': continue
                    b1, b2 = s1.get('box', [0, 0, 1, 1]), s2.get('box', [0, 0, 1, 1])
                    if max(abs(p - q) for p, q in zip(b1, b2)) > .02: continue          # different crops (e.g. two panels of one sheet)
                    t1, f2 = s1.get('to', s1.get('from', [.5, .5, 1])), s2.get('from', [.5, .5, 1])
                    if math.hypot(t1[0] - f2[0], t1[1] - f2[1]) < qc['repeat_center'] and abs(t1[2] - f2[2]) < qc['repeat_zoom']:
                        add('FAIL', 'picture', f'same framing of "{s1["image"]}" on lines {k + 1} and {seq[jj][0] + 1}: '
                                               f'"{ln["text"][:30]}" / "{seq[jj][1]["text"][:30]}"'); rep += 1
    uses = {}
    for k, ln, shs in seq:
        for s in shs: uses.setdefault(s['image'] + ('' if s.get('box', [0, 0, 1, 1]) == [0, 0, 1, 1] else ' ' + str([round(v, 2) for v in s['box']])), []).append(k + 1)
    top = sorted(((len(v), n) for n, v in uses.items() if n not in ('BLACK', 'TITLE')), reverse=True)[:3]
    add('INFO', 'picture', 'most-used images: ' + ', '.join(f'{n} x{c}' for c, n in top))
    if not rep: add('PASS', 'picture', f'no repeated framing within {qc["repeat_window_lines"]} lines')
    worst = (0, '')
    for k, ln, shs in seq:
        for s in shs:
            if s['image'] in ('BLACK', 'TITLE') or s.get('fit') == 'contain': continue
            iw, ih = size(s['image']); x0, y0, x1, y1 = s.get('box', [0, 0, 1, 1]); bw, bh = (x1 - x0) * iw, (y1 - y0) * ih
            for key in ('from', 'to'):
                z = s.get(key, s.get('from', [.5, .5, 1]))[2]; view_w = min(bw, bh * 16 / 9) / z; mag = W / view_w
                if mag > worst[0]: worst = (mag, f'line {k + 1} "{s["image"]}"')
                if s.get('allow_soft') or ln.get('allow_soft'): continue
                lvl = 'FAIL' if mag > qc['mag_fail'] else 'WARN' if mag > qc['mag_warn'] else None
                if lvl: add(lvl, 'picture', f'line {k + 1} "{s["image"]}" ({key}): {mag:.2f}x magnification of source pixels '
                                            f'(view {view_w:.0f}px -> {W}px); zoom out or use a sharper image')
    add('INFO', 'picture', f'largest magnification {worst[0]:.2f}x at {worst[1]}')
    amb = 0
    for k, ln, shs in seq:
        toks = norm(ln['text']).split()
        for e in shs[1 if ln.get('shot') else 0:] + ln.get('fx', []) + ln.get('sfx', []) + ln.get('rocks', []):
            at = str(e.get('at') or '')
            m = re.match(r'^\s*([^#+\-]*?)\s*(#\d+)?\s*([+-]\s*[\d.]+)?\s*$', at)
            if m and m.group(1) and not m.group(2) and toks.count(norm(m.group(1))) > 1:
                add('WARN', 'plan', f'line {k + 1}: anchor "{at}" appears {toks.count(norm(m.group(1)))} times; name it "{m.group(1)}#2" etc.'); amb += 1
    if not amb: add('PASS', 'plan', 'every anchor word is unambiguous in its line')

    # ---- MEDIA basics: sync, bitrate
    pr = probe(a.video, 'stream=codec_type,duration:format=duration,bit_rate,size')
    durs = {s['codec_type']: float(s.get('duration', 0)) for s in pr['streams'] if s['codec_type'] in ('video', 'audio')}
    if 'video' in durs and 'audio' in durs:
        d = abs(durs['video'] - durs['audio'])
        add('FAIL' if d > qc['sync_tol_s'] else 'PASS', 'sync', f'video {durs["video"]:.2f}s, audio {durs["audio"]:.2f}s (difference {d:.3f}s)')
    mbps = float(pr['format'].get('bit_rate', 0)) / 1e6
    add('WARN' if mbps > qc['bitrate_warn_mbps'] else 'PASS', 'file', f'{int(pr["format"]["size"]) / 1e6:.1f} MB, {mbps:.1f} Mb/s'
        + (' (heavy grain or noise inflates this)' if mbps > qc['bitrate_warn_mbps'] else ''))

    # ---- AUDIO: loudness, true peak, range
    m = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-i', str(a.video), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', m)[-1]); LRA = float(re.findall(r'LRA:\s+(-?[\d.]+) LU', m)[-1])
    TP = float(re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', m)[-1])
    add('FAIL' if abs(I - qc['lufs']) > qc['lufs_tol'] else 'PASS', 'loudness', f'integrated {I:.1f} LUFS (target {qc["lufs"]:.0f})')
    add('FAIL' if TP > qc['true_peak_max'] else 'PASS', 'loudness', f'true peak {TP:.1f} dBTP (max {qc["true_peak_max"]:.1f})')
    add('WARN' if LRA < qc['lra_warn'] else 'PASS', 'loudness', f'loudness range {LRA:.1f} LU' + (' (reads flat; make quiet moments quieter)' if LRA < qc['lra_warn'] else ''))
    SR = 16000; mix = pcm(a.video, SR); env = 20 * np.log10(np.sqrt(np.convolve(mix ** 2, np.ones(800) / 800, 'same')) + 1e-9)
    quiet = env < qc['silence_db']; best = run = 0
    for q in quiet[::160]:
        run = run + 1 if q else 0; best = max(best, run)
    best_s = best * 160 / SR
    add('PASS' if best_s >= qc['silence_min_s'] else 'WARN', 'sound', f'longest true silence {best_s:.1f}s'
        + ('' if best_s >= qc['silence_min_s'] else ' (no silence anywhere: the rhythm will feel even)'))

    # ---- AUDIO: voice over bed per line (needs the clean voices and the bed)
    masked, mix_err = [], {}
    bed = a.bed or (plan.get('music') or {}).get('file')
    if bed and (base / bed).exists():
        from scipy.signal import butter, sosfilt
        band = lambda x: sosfilt(butter(2, [150, 6000], 'band', fs=SR, output='sos'), x)
        v = band(pcm(base / plan['audio'], SR)); b = band(pcm(base / bed, SR)); low = []
        db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
        hop = int(.05 * SR)
        for k, ((s0, s1), (sc, ln)) in enumerate(zip(sp, flat)):
            # margin in 50 ms slices where the voice is actually sounding; the 25th percentile fails a line
            # when about a quarter of it is covered, and ignores a hit that only overlaps the line's tail
            i0, i1 = int(s0 * SR), int(s1 * SR)
            fv = np.array([db(v[i:i + hop]) for i in range(i0, max(i0 + 1, i1 - hop), hop)])
            fb = np.array([db(b[i:i + hop]) for i in range(i0, max(i0 + 1, i1 - hop), hop)])
            voiced = fv > fv.max() - 20
            marg = float(np.percentile((fv - fb)[voiced], 25)) if voiced.any() else db(v[i0:i1]) - db(b[i0:i1]); low.append(marg)
            if marg < qc['vob_fail_db'] and not ln.get('allow_masking'):
                masked.append((k, marg))          # decided after the recognizer has listened to the mix
            elif marg < qc['vob_warn_db']:
                add('WARN', 'sound', f'line {k + 1} "{ln["text"][:35]}": voice {marg:.1f} dB over the bed in its weakest quarter' + (' (marked allow_masking)' if ln.get('allow_masking') else ''))
        add('INFO', 'sound', f'voice over bed (weakest quarter of each line): median {np.median(low):.1f} dB, lowest {min(low):.1f} dB')
    else:
        add('INFO', 'sound', 'voice-over-bed skipped (no bed file given)')

    # ---- AUDIO: recognizer on clean voices and on the final mix
    if a.asr_dir:
        import sherpa_onnx
        d = Path(a.asr_dir); pick = lambda p, alt: str((sorted(d.glob(p)) or sorted(d.glob(alt)))[0])
        rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=pick('encoder*.int8.onnx', 'encoder*.onnx'),
              decoder=pick('decoder*.onnx', 'decoder*.onnx'), joiner=pick('joiner*.int8.onnx', 'joiner*.onnx'),
              tokens=str(d / 'tokens.txt'), num_threads=2)
        words = lambda s: re.sub(r'[^a-z ]+', ' ', s.lower().replace('-', ' ')).split()
        def run_asr(x, tag):
            tot = err = 0
            for k, ((s0, s1), (sc, ln)) in enumerate(zip(sp, flat)):
                st = rec.create_stream(); st.accept_waveform(SR, x[int(s0 * SR):int(s1 * SR)]); rec.decode_stream(st)
                ref, hyp = words(ln['text']), words(st.result.text)
                e = len(ref) - sum(mm.size for mm in difflib.SequenceMatcher(None, ref, hyp).get_matching_blocks()); tot += len(ref); err += e
                if tag == 'final mix': mix_err[k] = (e / max(1, len(ref)), st.result.text.lower())
                if ref and e / len(ref) > qc['asr_line_fail']:
                    add('FAIL', 'speech', f'{tag}: line {k + 1} "{ln["text"][:35]}" heard as "{st.result.text.lower()[:35]}"')
                elif ref and e / len(ref) > qc['asr_line_warn']:
                    add('WARN', 'speech', f'{tag}: line {k + 1} "{ln["text"][:35]}" heard as "{st.result.text.lower()[:35]}" (often a recognizer quirk)')
            return err / max(1, tot)
        clean = run_asr(pcm(base / plan['audio'], SR), 'clean voices'); mixr = run_asr(mix, 'final mix')
        add('FAIL' if clean > qc['asr_total_fail'] else 'PASS', 'speech', f'clean voices: recognizer missed {clean * 100:.1f}% of words')
        add('FAIL' if mixr > max(qc['asr_total_fail'], clean + qc['asr_mix_extra']) else 'PASS', 'speech',
            f'final mix: missed {mixr * 100:.1f}% (clean {clean * 100:.1f}%; the music costs {max(0, mixr - clean) * 100:.1f} points)')
    else:
        add('INFO', 'speech', 'recognizer checks skipped (no --asr-dir)')
    for k, marg in masked:        # masking fails only if the recognizer also mishears the line in the mix (or did not run)
        t = flat[k][1]['text'][:35]
        if k in mix_err and mix_err[k][0] <= qc['asr_line_warn']:
            add('WARN', 'sound', f'line {k + 1} "{t}": a hit covers part of the line ({marg:.1f} dB in its weakest quarter), '
                                 f'but the recognizer still hears it in the mix ("{mix_err[k][1][:30]}")')
        else:
            add('FAIL', 'sound', f'line {k + 1} "{t}": a quarter of the line is under the bed ({marg:.1f} dB) and '
                                 + (f'the mix is heard as "{mix_err[k][1][:30]}"' if k in mix_err else 'no recognizer check ran')
                                 + '; move the hit after the word')

    # ---- PICTURE: flashes, dark frames, frozen shots (small grey frames)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(a.video), '-vf', 'scale=160:90,format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160).astype(np.float32); lum = fr.mean((1, 2))
    jumps = np.nonzero(np.diff(lum) > qc['flash_jump'] * 255)[0] / fps
    worst_s = max([int(((jumps >= t) & (jumps < t + 1)).sum()) for t in jumps] or [0])
    add('FAIL' if worst_s > qc['flash_per_s_max'] else 'PASS', 'picture', f'{len(jumps)} bright flashes, at most {worst_s} in any second (limit {qc["flash_per_s_max"]})')
    dark = frozen = 0
    for k, ((s0, s1), (sc, ln)) in enumerate(zip(sp, flat)):
        shs = shots_of(ln)
        if any(s['image'] in ('BLACK', 'TITLE') for s in shs[:1]): continue
        idx = [min(len(fr) - 1, int(t * fps)) for t in (s0 + .3, (s0 + s1) / 2, max(s0 + .4, s1 - .1))]
        if lum[idx[1]] < qc['dark_luma'] and not (ln.get('dark_ok') or any(s.get('dark_ok') for s in shs)):
            add('WARN', 'picture', f'line {k + 1} "{ln["text"][:30]}": frame very dark (mean luma {lum[idx[1]]:.0f}/255)'); dark += 1
        moving = any(s.get('from') != s.get('to') for s in shs)
        if moving and np.abs(fr[idx[0]] - fr[idx[2]]).mean() < qc['frozen_diff']:
            add('WARN', 'picture', f'line {k + 1} "{ln["text"][:30]}": picture does not change although the shot should move'); frozen += 1
    if not dark: add('PASS', 'picture', 'no unintended dark frames')
    if not frozen: add('PASS', 'picture', 'every moving shot moves')

    # ---- CAPTIONS: reading speed (the subtitle text shown for each spoken stretch)
    fast = 0
    for k, ((s0, s1), (sc, ln)) in enumerate(zip(sp, flat)):
        if ln.get('nocap'): continue
        cps = len(ln.get('display', ln['text'])) / max(.5, (s1 - s0) + .5)
        if cps > qc['cps_warn']: add('WARN', 'captions', f'line {k + 1}: {cps:.0f} characters a second (over {qc["cps_warn"]})'); fast += 1
    if not fast: add('PASS', 'captions', f'every caption readable (under {qc["cps_warn"]} characters a second)')

    # ---- report
    order = {'FAIL': 0, 'WARN': 1, 'PASS': 2, 'INFO': 3}; R.sort(key=lambda r: order[r[0]])
    n = {lv: sum(1 for r in R if r[0] == lv) for lv in order}
    md = [f'# Checks: {a.video.name}', '', f'**{n["FAIL"]} fail · {n["WARN"]} warn · {n["PASS"]} pass**', '']
    for lv in order:
        rows = [r for r in R if r[0] == lv]
        if rows: md += [f'## {lv}', ''] + [f'- **{ar}:** {msg}' for _, ar, msg in rows] + ['']
    md += ['## Not checked by this script', '', '- Whether the story is clear, the ending is withheld, and the pacing builds (watch a rough cut).',
           '- Whether the voices act, and whether recordings, designed sounds and score blend (listen).',
           '- Contradictions in the script (a person or a language model reads it).', '']
    Path(a.out).write_text('\n'.join(md), encoding='utf-8')
    print('\n'.join(md[:4])); [print(f'  {lv}: {ar}: {msg}') for lv, ar, msg in R if lv in ('FAIL', 'WARN')]
    print('wrote', a.out); sys.exit(1 if n['FAIL'] else 0)


if __name__ == '__main__':
    main()
```