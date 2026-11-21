---
name: "motion-comic-video"
description: "Turn a story or script with characters into a motion comic video or cinematic trailer from painted or AI panels: moving shots, word-timed cuts and effects, character voices, music, recorded sound. For stories, not lessons."
---

# Motion comic video

Use this skill when the piece is a **story with characters** (a sketch, a parody ad, a short
drama) and the art is painted or image-generated panels: comic pages, storyboard sheets, hero
images. For lessons and explainers use **narrated-explainer-video** instead (still boards with
marks that point at what is said). Here every shot moves, cuts land on lines and words, effects
and sounds punctuate the gags, and a music bed runs under the dialogue.

**Tools.** The four scripts at the end (`motion_comic.py`, `voice_fx.py`, `word_times.py`,
`upscale.py`) were tested together on a 3-minute, 7-voice, 61-shot comedy. Narration and the
audio check come from the **narrated-explainer-video** skill: load it and write out its
`narrate.py` and `check_audio.py` (its step 6 and 9 rules on voices, caching and checks apply
here too). Write every script out exactly as given; do not tidy, shorten or "improve" them.
Needs ffmpeg (with rubberband for pitch), Pillow, numpy; `pip install onnxruntime
espeakng-loader phonemizer-fork sherpa-onnx` for narration and timing; torch only for upscaling.
Models: Kokoro v1.0 from Hugging Face `onnx-community/Kokoro-82M-v1.0-ONNX` (`onnx/model.onnx`,
`tokenizer.json`, `voices/<name>.bin`), and the sherpa-onnx GitHub release "asr-models" file
`sherpa-onnx-zipformer-small-en-2023-06-26.tar.bz2`.

Pipeline: **art -> (upscale) -> plan.json with shots -> check -> narrate.py -> voice_fx.py ->
word_times.py -> check_audio.py -> contact sheet -> MP4.**

**Done means:** `motion_comic.py plan.json --check` passes; `check_audio.py` reports no PROBLEM
except a one-word line you have tested alone (below); the contact sheet is opened and every
framing is clean; a frame from the middle of every line and one just after every word-anchored
gag have been looked at; `final.mp4` reports about -14 LUFS and its audio and video durations match.

**The one rule: anchor everything to lines and words, never to seconds.** A shot belongs to a
line; a cut, effect or sound inside a line names a word of it (`"at": "burst"`). Then a new
voice, a retake or a rewritten line re-times every cut, effect and music cue by itself. A
timeline pinned to seconds breaks the moment the narration changes.

**Work cheap first, polish last.** On a voiced drama the costly mistakes are editorial (the cut gives
the ending away, two faces ping-pong, it runs long), and no measurement catches them. Learned on a
2:33 war-fantasy trailer that was fully polished before anyone judged the edit:
1. Before writing, ask one question: is this an ad for the story (withhold the ending) or the story
   itself? Agree a target length. One plan can carry both cuts.
2. Write the script as a cut list, voice it (Kokoro is quick), lay it out and read the length before
   touching art.
3. Render a rough animatic (`"width": 640`, no finishing pass) and have the person watch it. Fix the
   edit there, where changes cost nothing.
4. Only then make a missing-shot list, get new art (see the image-request-pack skill), and polish.
5. Ask for taste as A/B/C: three short, loudness-matched clips of the moment in question. People
   pick far faster than they describe.
6. Before polishing, an outside review pays off: a one-document write-up (goal, inputs, pipeline,
   numbers, problems fixed, known weaknesses, numbered questions) plus a contact sheet of every line
   and a sound-layer map, sent to several other models. Act on what they agree on.

### Art
- Image generators are fine here (the painted look is the point), but ask for **one scene per
  image, 16:9, 1280x720 or larger, with no speech bubbles or lettering**. Painted-in dialogue
  repeats the subtitles and is often misspelt. Big ad-style headlines can stay as on-screen graphics.
- A sheet of many small panels also works: upscale it 4x with `upscale.py`, then crop each panel
  with a `box`. Panels under about 250 px tall in the original stay soft even after upscaling;
  use them for short reaction shots.
- **Find boxes from a grid, not by eye.** Draw a labelled grid every 50 px over the *original*
  sheet, read the panel edges off it, convert to fractions (x / width, y / height), and inset 3-4 px
  so gutters, panel numbers and section labels never show. Check every framing with `--contact-sheet`.
- **Character consistency:** if a character's outfit differs between sheets, take that
  character's wide shots from one sheet and use the off-model panels only for tight face close-ups.

### Script and voices
- One plan line per spoken sentence or reply, each with a `"speaker"` in the `"cast"`.
  `"text"` is what the voice says: normal case, words not digits (Kokoro reads ALL-CAPS words
  such as "US" as letters). `"display"` is what the subtitles show, e.g. the shouted ALL-CAPS version.
- Cast clearly different voices. Best Kokoro voices: af_heart, af_bella, bf_emma; usable:
  am_puck (energetic host), am_michael, am_fenrir, bm_fable, bm_george. Avoid am_adam (weakest).
- Give small or monstrous characters a colour with `voice_fx` instead of hunting for a new voice:
  `{"gnome": {"pitch": 5}, "wizard": {"pitch": 3}, "dragon": {"pitch": -5, "echo": true}}`.
- **Comic pace:** narrate at `--speed 1.08`, then `voice_fx.py --gap 0.3 --scene-gap 0.6`.
  Kokoro pads every sentence with about 0.8 s of silence, so even a small `--gap` in narrate.py
  plays as a 1.1 s pause. voice_fx.py trims that padding and lays the lines out again with exact
  pauses, writing new labels. Measured: 58 lines, 399 words came to 3.5 minutes untrimmed and
  2:58 trimmed. Put a beat before a payoff with `"pause_after": 0.7` on the setup line.
- Kokoro cannot act: delivery comes only from punctuation and speed. Say so to the user; if they
  have an expressive TTS (instruction or emotion control), its WAV plus labels drop straight in
  as `"audio"` + `"timestamps"` and everything re-times.

### Shots, effects and sound
- **A new shot on almost every line**; a long narrated line can take a second shot at a word
  (`"shots": [{"at": "coven", ...}]`). Every shot moves: push in (zoom 1.0 to 1.2-1.4), tilt down
  a tall panel (cy 0 to 1), pan a wide one (cx 0 to 1). Avoid holding still for more than about 4 s.
- Transitions: `"cut"` for punchlines and one-word reactions ("Oh?", "Why?"), `"static"` for
  interruptions and broadcast breaks, `"flash"` for explosions, `"cont"` to continue a move on the
  same panel, cross-fade otherwise.
- **Show the gag the narration describes.** If a line says a tower bursts through the ceiling,
  cut to the tower and put flash + shake + debris + crash on "burst". If the line names a small
  action (a gnome drops a biscuit), a `drop` effect on "dropped" plus a `tink` on "biscuit" sells it.
- Rhythms use `repeat` and `every`: hammering = shake and thud, `repeat` 21, `every` 0.17.
  Keep effects rare enough to land, roughly one per scene; a `"sting"` on ad-break scenes.
- `"lower_third"` on each main character's first line; `"bug"` gives a TV-channel corner logo.
  A drawn `"card"` (test-card style) suits "broadcast terminated" or "please stand by" moments.
- `--clip` renders a short stretch with real audio for checking a gag before the full render
  (about 75 s for 3 minutes at 1280x720 on 2 cores).

### Commands
```bash
python upscale.py realesr-general-x4v3.pth sheet.png art/sheet_x4.png      # optional, small panels
python motion_comic.py plan.json --check
python narrate.py plan.json --model-dir <kokoro folder> --speed 1.08        # cast from plan.json
python voice_fx.py plan.json --gap 0.3 --scene-gap 0.6                      # -> narration_fx.wav, labels_fx.txt
python word_times.py plan.json --asr-dir <sherpa zipformer folder>          # -> words.json
python check_audio.py plan.json --asr-dir <sherpa zipformer folder>
python motion_comic.py plan.json --contact-sheet                            # final_contact.png
python motion_comic.py plan.json --clip 60 75
python motion_comic.py plan.json                                            # final.mp4 + .srt, chapters
```
With `"audio": "narration_fx.wav", "timestamps": "labels_fx.txt", "words": "words.json"` in the plan.

### Checks
- `check_audio.py` reads the plan's audio and timestamps, so it checks the trimmed, coloured
  narration. A one-word line ("Oh?") can fail in context although it is clear alone: voice it by
  itself and transcribe it before respelling anything.
- The renderer prints a note for any anchor word the recognizer did not hear; that cue is then
  placed from the word's position in the sentence, which is close but not exact. Look at those frames.
- Pull frames with `ffmpeg -nostdin -ss T -i final.mp4 -frames:v 1 f.png` (in a shell loop,
  ffmpeg without `-nostdin` swallows the loop's input). Check the middle of every line (right
  panel, nothing clipped) and just after each gag (effect visible).

### Drama and cinematic trailers

Rules that held up on a dialogue-driven trailer (5 outside reviews agreed on most of them):

**Edit**
- Dialogue gets coverage, not portraits. Play about half the lines over other shots (the place, the
  people at stake, a two-shot, hands or props) and save each face for the line that needs it. One
  line = one face makes two stills ping-pong. Lint it: the same image with nearly the same framing
  (centre within 0.15, zoom within 0.15) inside four lines is a failure.
- Cap zoom: 1.4 on ~1600 px stills, 1.5 on 1920 px images, 1.15 on upscaled storyboard crops. Past
  that you are zooming into the upscaler.
- Silence is the strongest tool. End a trailer on its best line, cut the music, hold 1.5-2 s of true
  black and silence (no embers, no grain on black frames), then the title on one low hit. Do not speak
  the title. Shots for the black frame and title can hang off the last line: `"at": "stood+1.0"`,
  `"at": "stood+2.8"`, with a long `pause_after`.
- A countdown or montage speeds up with 2 shots per line at word anchors and 0.25 s pauses, then
  falls into silence before the quietest line.
- Effects are rarer than you think: embers only where there is fire, debris on the 2 biggest blasts,
  3 white flashes at most. Count bright-frame jumps (a mean-luma rise of 20% of full scale): no more
  than 3 a second.

**Sound**
- The renderer does not duck a music file: `"music": {"file"}` is only multiplied by 0.12 x volume.
  Build a pre-ducked bed yourself and pass it at unity (`"volume": 8.333`); see the
  cinematic-sound-design skill.
- Put a big boom 0.25-0.45 s after its word, never on it. Run the recognizer on the final mix (point a
  copy of the plan's `"audio"` at the MP4): a buried word shows up there and nowhere else.
- Place a pre-existing score by a word: its peak time = the climax word. Cut it to silence with a short
  fade instead of letting it trail on after the climax.
- Real recordings beat synthesis for gunfire, explosions and creatures. Synthesized drones, heartbeat,
  risers and sub drops blend fine; synthesized brass under a real orchestra does not.

**Voices**
- `narrate.py` uses one speed for everyone: voice two takes at different speeds and pick per role with
  `merge_takes.py` (below).
- Pitch a narrator lightly (-0.5 to -1 semitone, chosen by ear from samples); `narrator_booth.py` adds
  weight without pitch artefacts. Radio voices: `radio_fx.py`. Quiet, intimate lines: `"soft": true`
  plus `soft_lines.py` before `voice_fx.py`, and dip the bed under them.
- Kokoro cannot act. Say so first, and offer to drop in acted takes for the 4-6 emotional lines.

**Finishing (optional pass in code)** Grade (saturation 0.86, cool shadows, warm highlights, +6%
contrast), vignette, embers, letterbox (38 px at 720p), serif captions with the speaker's name. Keep grain
soft and refresh it every third frame: per-pixel grain every frame took a 2:33 720p file from 28 MB to
300 MB. Export a clean version (subtitle track) and a burned-caption version for muted feeds.

**Extra checks for dramas** Voice over bed per line in 150-6,000 Hz (flag under ~6 dB unless the hit
is meant); true peak at or under -1 dBTP and loudness range from `ebur128=peak=true` (under ~5 LU
reads flat: make the quiet moments quieter); silence frames and samples really are zero; a read of
the script for contradictions ("ten minutes" against "an hour").

## motion_comic.py

```python
#!/usr/bin/env python3
"""Motion comic: painted panels + multi-voice narration -> MP4 with moving shots, effects, music.

  python motion_comic.py plan.json --check            # lint (run before narrating)
  python motion_comic.py plan.json --contact-sheet    # every shot's start/end framing
  python motion_comic.py plan.json --clip 60 75       # quick check with real audio
  python motion_comic.py plan.json                    # final.mp4 (+ .srt, chapters)

Everything is anchored to LINES and WORDS, never to clock times, so new narration (another
voice, a retake, a rewritten line) re-times every cut, effect and music cue automatically.

plan.json (the narration fields are the same as render_video.py / narrate.py):
{
  "title": "...", "width": 1280, "fps": 24,
  "audio": "narration_fx.wav", "timestamps": "labels.txt", "words": "words.json",
  "cast": {"narrator": "af_heart", "hero": "am_puck"},            # narrate.py voices
  "voice_fx": {"dragon": {"pitch": -5, "echo": true}},             # voice_fx.py
  "images": {"B": "art/sheetB_x4.png"},                            # short names for images
  "music": {"bpm": 112, "volume": 0.84},                           # procedural jingle; or {"file": "bed.mp3"}; omit = none
  "bug": "ZORBLOOK TV",                                            # optional corner logo
  "scenes": [{"title": "Chapter title", "sting": true, "lines": [
     {"text": "Then call Zorblook's today!", "display": "THEN CALL ZORBLOOK'S TODAY!", "speaker": "hero",
      "shot": {"image": "B", "box": [0.1, 0.2, 0.5, 0.6], "from": [0.5, 0.5, 1.0], "to": [0.4, 0.4, 1.3], "tr": "x"},
      "shots": [{"at": "today", "image": "B", "box": [...], "from": [...], "to": [...], "tr": "cut"}],
      "fx":  [{"type": "shake", "at": "call", "dur": 0.5, "amp": 9}],
      "sfx": [{"type": "thud", "at": "today"}],
      "lower_third": ["BARNABY BLINT", "Spokesperson"]}]}]
}
- "text" is spoken (write it for the voice: normal case, words not digits); "display" (optional)
  is what the subtitles show, e.g. the shouted ALL-CAPS version.
- shot: starts at its line (just before the speech) or at "at": a word of that line ("burst",
  "burst#2" = second one, "+0.4" offsets allowed: "burst+0.4"). It runs until the next shot.
  box = the clean picture area on the image, fractions 0..1 (x0, y0, x1, y1). from/to = camera
  at the start/end as (cx, cy, zoom): cx, cy 0..1 slide the view across the box's spare room,
  zoom 1 = the largest 16:9 view that fits the box. "fit": "contain" shows the whole box over a
  blurred copy (for title cards that are not 16:9). "card": {"title", "subtitle", "footer"}
  instead of an image draws a TV test card. tr: "x" cross-fade (default), "cut", "static",
  "flash", "cont" (same as cut; for continuing a move on the same panel).
- fx types: shake (dur, amp px, freq, repeat, every), flash (dur), static (dur), debris (dur, n),
  drop (a crumb/biscuit falls; size). sfx types: thud, crash, static, tink, rumble, sting,
  whoosh, crunch, bell (vol, repeat, every). "at" omitted = when the line's speech starts.
- Scene "sting": true plays a short brass sting as the scene starts. Scene titles -> chapters.
Needs ffmpeg/ffprobe, Pillow, numpy. Mix is normalised to about -14 LUFS (online standard).
"""
import argparse, difflib, json, math, re, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

XF, STATIC_LEN, LEAD, SCENE_LEAD = 0.30, 0.45, 0.35, 0.60
SR = 48000
TR = {'x', 'cut', 'static', 'flash', 'cont'}
FX = {'shake', 'flash', 'static', 'debris', 'drop'}
SFX = {'thud', 'crash', 'static', 'tink', 'rumble', 'sting', 'whoosh', 'crunch', 'bell'}


def font(size, bold=True):
    for p in (['/usr/share/fonts/opentype/inter/InterDisplay-Black.otf', '/usr/share/fonts/opentype/inter/Inter-Black.otf']
              if bold else []) + ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
                                  'C:/Windows/Fonts/arialbd.ttf']:
        if Path(p).exists(): return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def norm(s): return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()
def ease(u): u = min(1, max(0, u)); return 0.5 - 0.5 * math.cos(math.pi * u)


def read_labels(p):
    out = []
    for l in Path(p).read_text(encoding='utf-8-sig').splitlines():
        q = l.split('\t')
        if len(q) >= 2 and not l.startswith('\\'):
            out.append((float(q[0]), float(q[1]), q[2] if len(q) > 2 else ''))
    return out


def probe(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                capture_output=True, text=True, check=True).stdout)


def flat_lines(plan):
    return [(si, li, sc, ln) for si, sc in enumerate(plan['scenes']) for li, ln in enumerate(sc['lines'])]


def all_shots(ln):
    return ([ln['shot']] if ln.get('shot') else []) + list(ln.get('shots', []))


def split_anchor(at):
    if at is None: return None, 1, 0.0
    m = re.match(r"^\s*([^#+\-]*?)\s*(?:#(\d+))?\s*([+-]\s*[\d.]+)?\s*$", str(at))
    if not m: return str(at), 1, 0.0
    return (m.group(1) or None), int(m.group(2) or 1), float((m.group(3) or '0').replace(' ', ''))


def lint(plan, base):
    out, imgs = [], plan.get('images', {})
    lines = flat_lines(plan)
    if not lines or not all_shots(lines[0][3]): out.append('the first line needs a "shot"')
    for si, li, sc, ln in lines:
        tag = f'S{si + 1}.{li + 1}'
        if re.search(r'[0-9%=^/\\$<>*_{}|#@&+]', ln.get('text', '')): out.append(f'{tag}: digits or symbols in spoken text')
        for sh in all_shots(ln):
            if sh.get('card'): continue
            im = imgs.get(sh.get('image'), sh.get('image'))
            if not im or not (base / im).is_file(): out.append(f'{tag}: image not found: {sh.get("image")}')
            b = sh.get('box', [0, 0, 1, 1])
            if len(b) != 4 or not (0 <= b[0] < b[2] <= 1 and 0 <= b[1] < b[3] <= 1): out.append(f'{tag}: box {b} must be x0<x1, y0<y1 in 0..1')
            for k in ('from', 'to'):
                c = sh.get(k, [.5, .5, 1])
                if len(c) != 3 or not (0 <= c[0] <= 1 and 0 <= c[1] <= 1 and c[2] >= 1): out.append(f'{tag}: {k} {c} needs cx,cy in 0..1, zoom >= 1')
            if sh.get('tr', 'x') not in TR: out.append(f'{tag}: unknown transition {sh.get("tr")}')
        for kind, ok in (('fx', FX), ('sfx', SFX)):
            for e in ln.get(kind, []):
                if e.get('type') not in ok: out.append(f'{tag}: unknown {kind} type {e.get("type")}')
        for e in all_shots(ln)[1 if ln.get('shot') else 0:] + ln.get('fx', []) + ln.get('sfx', []):
            w, n, _ = split_anchor(e.get('at'))
            if w and sum(1 for t in norm(ln['text']).split() if t == norm(w)) < n:
                out.append(f'{tag}: anchor word "{e.get("at")}" is not in the spoken text')
        spk = ln.get('speaker', sc.get('speaker'))
        if spk and spk not in plan.get('cast', {}): out.append(f'{tag}: speaker "{spk}" not in "cast"')
    return out


class Timeline:
    def __init__(self, plan, base, total=None):
        self.lines = flat_lines(plan)
        labels = read_labels(base / plan['timestamps'])
        idx, j = [], 0
        for k, (*_, ln) in enumerate(self.lines):
            best, br = None, 0
            for c in range(j, min(len(labels), j + 20)):
                r = difflib.SequenceMatcher(None, norm(ln['text']), norm(labels[c][2])).ratio()
                if r > br: best, br = c, r
            if best is None or br < 0.6: sys.exit(f'line {k + 1} not found in timestamps: "{ln["text"][:60]}"')
            idx.append(best); j = best + 1
        self.sp = [(labels[i][0], labels[i][1]) for i in idx]
        self.total = total or probe(base / plan['audio'])
        self.start = []
        for k, (si, li, *_) in enumerate(self.lines):
            if k == 0: self.start.append(0.0); continue
            prev_end = self.sp[k - 1][1]; s = self.sp[k][0]
            self.start.append(max(prev_end, s - (SCENE_LEAD if li == 0 else LEAD)))
        self.words = None
        if plan.get('words') and (base / plan['words']).exists():
            wl = json.loads((base / plan['words']).read_text())['lines']
            self.words = [wl[i]['words'] if i < len(wl) else [] for i in idx]
        self.warn = []

    def word(self, k, at):
        """Time a word of line k is spoken (recognised word, else position-in-sentence estimate)."""
        w, n, off = split_anchor(at)
        s0, s1 = self.sp[k]
        if not w: return s0 + off
        target = norm(w)
        if self.words and self.words[k]:
            hits = [t0 for ww, t0, _ in self.words[k] if difflib.SequenceMatcher(None, norm(ww), target).ratio() >= 0.75]
            if len(hits) >= n: return hits[n - 1] + off
        toks = norm(self.lines[k][3]['text']).split(); pos = [i for i, t in enumerate(toks) if t == target]
        if len(pos) < n: sys.exit(f'anchor "{at}" not in line {k + 1}')
        chars = [len(t) + 1 for t in toks]; frac = sum(chars[:pos[n - 1]]) / max(1, sum(chars))
        self.warn.append(f'estimated time for "{at}" in line {k + 1} (recognizer did not hear it)')
        return s0 + frac * (s1 - s0) + off


def build(plan, base, tl):
    imgs = plan.get('images', {})
    shots, fx, sfx, lts = [], [], [], []
    for k, (si, li, sc, ln) in enumerate(tl.lines):
        for j, sh in enumerate(all_shots(ln)):
            s = dict(sh)
            s['t0'] = tl.start[k] if (j == 0 and ln.get('shot') and not sh.get('at')) else max(tl.start[k], tl.word(k, sh.get('at')) - 0.08)
            if not s.get('card'): s['path'] = base / imgs.get(sh['image'], sh['image'])
            shots.append(s)
        for e in ln.get('fx', []):
            for r in range(int(e.get('repeat', 1))): fx.append(dict(e, t=tl.word(k, e.get('at')) + r * e.get('every', 0.2)))
        for e in ln.get('sfx', []):
            for r in range(int(e.get('repeat', 1))): sfx.append(dict(e, t=tl.word(k, e.get('at')) + r * e.get('every', 0.2)))
        if ln.get('lower_third'): lts.append(dict(t0=tl.sp[k][0] + .2, t1=tl.sp[k][0] + 3.8, name=ln['lower_third'][0], role=ln['lower_third'][1] if len(ln['lower_third']) > 1 else ''))
        if li == 0 and sc.get('sting'): sfx.append(dict(type='sting', t=tl.start[k] + .1))
    shots.sort(key=lambda s: s['t0'])
    for i, s in enumerate(shots): s['t1'] = shots[i + 1]['t0'] if i + 1 < len(shots) else tl.total
    for s in shots:
        if s.get('tr') == 'static': sfx.append(dict(type='static', t=s['t0'] - STATIC_LEN / 2, vol=.7))
        if s.get('tr') == 'flash': fx.append(dict(type='flash', t=s['t0'], dur=.55))
    return shots, fx, sfx, lts


# ------------------------------------------------------------------ pictures
class Pictures:
    def __init__(self, W, H):
        self.W, self.H, self.cache, self.bg = W, H, {}, {}
        self.rng = np.random.default_rng(7)

    def img(self, p):
        if p not in self.cache: self.cache[p] = Image.open(p).convert('RGB')
        return self.cache[p]

    def view(self, s, cam):
        im = self.img(s['path']); x0, y0, x1, y1 = s.get('box', [0, 0, 1, 1])
        x0, x1, y0, y1 = x0 * im.width, x1 * im.width, y0 * im.height, y1 * im.height
        bw, bh = x1 - x0, y1 - y0; cx, cy, z = cam
        w = min(bw, bh * 16 / 9) / z; h = w * 9 / 16
        l = x0 + (bw - w) * cx; t = y0 + (bh - h) * cy
        return im, (l, t, l + w, t + h)

    def shot(self, s, t):
        if s.get('card'): return self.card(s['card'], t - s['t0'])
        u = (t - s['t0']) / max(.1, s['t1'] - s['t0'] + XF)
        a, b = s.get('from', [.5, .5, 1.0]), s.get('to', s.get('from', [.5, .5, 1.0]))
        cam = [a[i] + (b[i] - a[i]) * ease(u) for i in range(3)]
        if s.get('fit') == 'contain': return self.contain(s, cam[2])
        im, box = self.view(s, cam)
        return im.resize((self.W, self.H), Image.BICUBIC, box=box)

    def contain(self, s, z):
        im = self.img(s['path']); x0, y0, x1, y1 = s.get('box', [0, 0, 1, 1])
        src = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
        key = id(s)
        if key not in self.bg:
            bg = src.resize((self.W, self.H)).filter(ImageFilter.GaussianBlur(28))
            self.bg[key] = Image.blend(bg, Image.new('RGB', (self.W, self.H), (6, 10, 26)), .55)
        out = self.bg[key].copy()
        fh = int(self.H * .92 * z); fw = int(fh * src.width / src.height)
        if fw > self.W * .96: fw = int(self.W * .96 * z); fh = int(fw * src.height / src.width)
        out.paste(src.resize((fw, fh), Image.LANCZOS), ((self.W - fw) // 2, (self.H - fh) // 2)); return out

    def card(self, c, u):
        W, H = self.W, self.H; im = Image.new('RGB', (W, H), (12, 14, 24)); d = ImageDraw.Draw(im)
        bw = W / 7
        for k, col in enumerate(['#C0C0C0', '#C0C000', '#00C0C0', '#00C000', '#C000C0', '#C00000', '#0000C0']):
            d.rectangle((k * bw, 0, (k + 1) * bw, H * .62), fill=col)
        d.rectangle((0, H * .70, W, H), fill='#101018')
        d.rounded_rectangle((W * .13, H * .30, W * .87, H * .65), radius=26, fill='#162139', outline='#FFF4C9', width=8)
        d.text((W / 2, H * .42), c.get('title', ''), font=font(int(H * .095)), fill='#FBE35C', anchor='mm')
        d.text((W / 2, H * .535), c.get('subtitle', ''), font=font(int(H * .045), False), fill='#FFF4C9', anchor='mm')
        d.text((W / 2, H * .83), c.get('footer', ''), font=font(int(H * .035), False), fill='#FFF4C9', anchor='mm')
        a = np.asarray(im).astype(np.int16)
        if u < 1.2 or int(u * 3) % 7 == 0: a = np.roll(a, int(6 * math.sin(u * 37)), axis=1)
        a[::3] = (a[::3] * .82).astype(np.int16); a += self.rng.integers(-14, 15, (H, W, 1), dtype=np.int16)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    def noise(self, t):
        g = self.rng.integers(0, 255, (self.H // 4, self.W // 4, 1), dtype=np.uint8)
        g = np.repeat(np.repeat(g, 4, 0), 4, 1).astype(np.int16)
        g += (np.sin(np.arange(self.H)[:, None, None] * .09 + t * 40) * 40).astype(np.int16)
        return np.clip(g, 0, 255).astype(np.uint8).repeat(3, 2)


def crumb(size):
    s = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(s); m = size // 14
    d.ellipse((m, m, size - m, size - m), fill='#D9A35B', outline='#5A3418', width=max(2, size // 18))
    for fx_, fy in [(.33, .33), (.6, .42), (.42, .64), (.66, .68), (.28, .53)]:
        r = size * .055; d.ellipse((fx_ * size - r, fy * size - r, fx_ * size + r, fy * size + r), fill='#6B3A1A')
    return s


def render_video(plan, shots, fx, lts, tl, pics, out, t0, t1, fps):
    W, H = pics.W, pics.H; rng = np.random.default_rng(3)
    debris = [dict(x=rng.uniform(0, W), y=rng.uniform(-400, -10), vy=rng.uniform(320, 720), vx=rng.uniform(-60, 60),
                   r=rng.uniform(3, 11) * W / 1280, c=tuple(int(v) for v in rng.choice([[214, 190, 150], [150, 120, 90], [235, 225, 205]])))
              for _ in range(120)]
    sprites = {}
    bug = plan.get('bug'); bug_on = shots[1]['t0'] if len(shots) > 1 else 0
    last_card = max([s['t0'] for s in shots if s.get('card')] + [tl.total])
    fb, fm = font(int(H * .047)), font(int(H * .031), False)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(int(round(t0 * fps)), int(round(t1 * fps))):
        t = n / fps
        k = max([i for i, s in enumerate(shots) if s['t0'] <= t + 1e-6] or [0]); s = shots[k]
        a = np.asarray(pics.shot(s, t)).astype(np.float32); since = t - s['t0']
        if k and s.get('tr', 'x') == 'x' and since < XF:
            m = ease(since / XF); a = a * m + np.asarray(pics.shot(shots[k - 1], t)).astype(np.float32) * (1 - m)
        img = Image.fromarray(a.astype(np.uint8))
        dx = dy = 0.0; flash = 0.0; stat = 0.0
        for e in fx:
            u = t - e['t']; d = e.get('dur', {'shake': .5, 'flash': .5, 'static': .45, 'debris': 3.0, 'drop': 1.6}[e['type']])
            if not 0 <= u < d: continue
            if e['type'] == 'shake':
                amp = e.get('amp', 9) * W / 1280 * (1 - u / d) ** 2; f = e.get('freq', 22)
                dx += amp * math.sin(2 * math.pi * f * u + 1.3); dy += amp * math.cos(2 * math.pi * f * .87 * u)
            elif e['type'] == 'flash': flash = max(flash, (1 - u / d) ** 1.5)
            elif e['type'] == 'static': stat = max(stat, min(1, (1 - abs(2 * u / d - 1)) * 1.6))
            elif e['type'] == 'debris':
                dr = ImageDraw.Draw(img)
                for q in debris[:int(e.get('n', 90))]:
                    y = q['y'] + q['vy'] * u + 260 * u * u; x = q['x'] + q['vx'] * u
                    if -20 < y < H + 20: dr.ellipse((x - q['r'], y - q['r'], x + q['r'], y + q['r']), fill=q['c'])
            elif e['type'] == 'drop':
                size = int(e.get('size', 90) * W / 1280)
                if size not in sprites: sprites[size] = crumb(size)
                sp = sprites[size].rotate(-400 * u, resample=Image.BICUBIC)
                y = int(-size + .5 * 1900 * H / 720 * u * u); x = int(W * e.get('x', .55) + 40 * u)
                if y < H: img.paste(sp, (x, y), sp)
        if dx or dy:
            z = img.resize((int(W * 1.04), int(H * 1.04)), Image.BILINEAR)
            ox, oy = (z.width - W) // 2 + int(dx), (z.height - H) // 2 + int(dy); img = z.crop((ox, oy, ox + W, oy + H))
        d = ImageDraw.Draw(img, 'RGBA')
        for lt in lts:
            u = t - lt['t0']; dur = lt['t1'] - lt['t0']
            if not 0 <= u < dur: continue
            sl = ease(min(u / .35, (dur - u) / .35, 1))
            bw = max(d.textbbox((0, 0), lt['name'], font=fb)[2], d.textbbox((0, 0), lt['role'], font=fm)[2]) + int(W * .047)
            x = int(-bw + (bw + W * .0375) * sl); y = int(H * .76); h1, h2 = int(H * .075), int(H * .125)
            d.rectangle((x, y, x + bw, y + h1), fill=(22, 33, 57, 235)); d.rectangle((x, y, x + int(W * .008), y + h2), fill=(251, 227, 92, 255))
            d.rectangle((x, y + h1, x + bw - int(W * .03), y + h2), fill=(244, 84, 93, 235))
            d.text((x + int(W * .022), y + int(h1 * .14)), lt['name'], font=fb, fill=(255, 244, 201))
            d.text((x + int(W * .022), y + h1 + int(H * .007)), lt['role'], font=fm, fill=(255, 255, 255))
        if bug and bug_on + .4 <= t < last_card and not s.get('card'):
            bx, by = int(W * .83), int(H * .92); fbug = font(int(H * .028))
            bw = d.textbbox((0, 0), bug, font=fbug)[2] + int(W * .045)
            d.rounded_rectangle((W - bw - int(W * .022), by, W - int(W * .022), by + int(H * .053)), radius=10, fill=(16, 24, 44, 150))
            on = int(t * 1.6) % 2 == 0; cx = W - bw - int(W * .022) + int(W * .012)
            d.ellipse((cx, by + int(H * .017), cx + int(H * .02), by + int(H * .037)), fill=(244, 84, 93, 255 if on else 90))
            d.text((cx + int(W * .02), by + int(H * .01)), bug, font=fbug, fill=(255, 244, 201, 220))
        o = np.asarray(img).astype(np.float32)
        if flash: o = o * (1 - flash) + 255 * flash
        for s2 in shots:
            if s2.get('tr') == 'static' and abs(t - s2['t0']) < STATIC_LEN / 2: stat = max(stat, min(1, (1 - abs(t - s2['t0']) / (STATIC_LEN / 2)) * 1.6))
        if stat: o = o * (1 - stat) + pics.noise(t) * stat
        if t < .25: o *= t / .25
        if t > tl.total - 1.6: o *= max(0, (tl.total - t) / 1.6)
        p.stdin.write(np.clip(o, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait(): sys.exit('ffmpeg failed')


# ------------------------------------------------------------------ sound
def tt(d): return np.arange(int(d * SR)) / SR


def synth(f, d, amp, kind):
    t = tt(d)
    if kind == 'brass': o = sum((1 / k) * np.sin(2 * np.pi * k * f * t + .17 * k * np.sin(2 * np.pi * 5 * t)) for k in range(1, 8)) / 2.7
    elif kind == 'bell': o = (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * f * 2.04 * t) + .18 * np.sin(2 * np.pi * f * 4.11 * t)) / 1.5
    elif kind == 'bass': o = (np.sin(2 * np.pi * f * t) + .22 * np.sin(2 * np.pi * f * 2 * t)) / .95
    else: o = (np.sin(2 * np.pi * f * t) + .37 * np.sin(2 * np.pi * f * 1.004 * t) + .16 * np.sin(2 * np.pi * f * 2 * t)) / 1.6
    a, r = min(.06, d * .23), min(.16, d * .24)
    env = np.maximum(0, np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)))
    if kind == 'bell': env *= np.exp(-t * 2.3 / max(d, .2))
    return (amp * o * env).astype(np.float32)


def put(buf, t, x):
    i = int(t * SR)
    if i < 0: x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i]


def midi(m): return 440 * 2 ** ((m - 69) / 12)


def sfx_sound(kind, rng):
    def noise(d): return rng.standard_normal(len(tt(d))).astype(np.float32)
    if kind == 'thud': t = tt(.5); return (.35 * np.sin(2 * np.pi * (70 - 30 * t / .5) * t) * np.exp(-t * 7)).astype(np.float32)
    if kind == 'crash':
        t = tt(1.0); q = np.convolve(noise(1.0), np.ones(120) / 120, 'same') * 8
        return ((.33 * q + .15 * np.sin(2 * np.pi * (125 - 55 * t) * t)) * np.exp(-t * 4)).astype(np.float32)
    if kind == 'static': t = tt(.45); return (.10 * np.convolve(noise(.45), [1., -.45], 'same') * np.exp(-t * 3)).astype(np.float32)
    if kind == 'tink': t = tt(.3); return (.12 * (np.sin(2 * np.pi * 1900 * t) + .6 * np.sin(2 * np.pi * 2550 * t)) * np.exp(-t * 18)).astype(np.float32)
    if kind == 'crunch': t = tt(.18); return (.10 * noise(.18) * (rng.random(len(t)) < .25) * np.exp(-t * 14)).astype(np.float32)
    if kind == 'rumble':
        t = tt(1.6); q = np.convolve(noise(1.6), np.ones(180) / 180, 'same') * 6
        return (.18 * q * np.minimum(1, t * 8) * np.exp(-t * 2.2)).astype(np.float32)
    if kind == 'whoosh':
        t = tt(.6); q = np.convolve(noise(.6), np.ones(30) / 30, 'same') * 3
        return (.12 * q * np.sin(np.pi * t / .6) ** 2).astype(np.float32)
    if kind == 'bell': return synth(midi(84), .5, .07, 'bell') + np.pad(synth(midi(88), .4, .05, 'bell'), (int(.12 * SR), 0))[:int(.5 * SR)]
    if kind == 'sting':
        out = np.zeros(int(1.0 * SR), np.float32)
        for dt, m in [(0, 72), (.15, 76), (.32, 79), (.48, 84)]: put(out, dt, synth(midi(m), .34, .11, 'brass'))
        return out
    raise ValueError(kind)


def music_bed(total, speech, bpm=112, rng=None):
    base = np.zeros(int((total + .1) * SR), np.float32); beat = 60 / bpm
    chords = [[48, 52, 55], [45, 48, 52], [53, 57, 60], [43, 47, 50]]
    for bar in range(int(total / (beat * 4)) + 1):
        t = bar * beat * 4; ch = chords[bar % 4]
        for k in ch: put(base, t, synth(midi(k), beat * 3.8, .012, 'pad'))
        for j in range(4):
            put(base, t + j * beat, synth(midi(ch[0] - 12), .20, .021, 'bass'))
            if j in (1, 3): x = tt(.07); put(base, t + j * beat, (rng.standard_normal(len(x)) * np.exp(-x * 65) * .014).astype(np.float32))
        if bar % 2 == 0:
            for off, m in [(.5, 67), (1.5, 72), (2.5, 76)]: put(base, t + beat * off, synth(midi(m), .15, .018, 'bell'))
    duck = np.full(len(base), .88, np.float32)
    for s0, s1 in speech: duck[max(0, int((s0 - .14) * SR)):int((s1 + .2) * SR)] = .40
    k = int(.085 * SR); duck = np.convolve(duck, np.ones(k) / k, 'same')
    base *= duck; base *= np.minimum(1, np.maximum(0, (total - np.arange(len(base)) / SR) / 1.6))
    return base


def mix_audio(plan, base, tl, sfx, tmp):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(base / plan['audio']), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    voice = np.frombuffer(pcm, np.float32).copy()
    n = max(len(voice), int(tl.total * SR)); mix = np.zeros(n, np.float32); mix[:len(voice)] += voice
    rng = np.random.default_rng(1307); m = plan.get('music')
    if m:
        if m.get('file'):
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-stream_loop', '-1', '-i', str(base / m['file']), '-t', f'{tl.total:.3f}', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                                 capture_output=True, check=True).stdout
            bed = np.frombuffer(raw, np.float32).copy() * .12
        else:
            bed = music_bed(tl.total, tl.sp, m.get('bpm', 112), rng)
        mix[:min(n, len(bed))] += bed[:n] * m.get('volume', .84)
    for e in sfx: put(mix, e['t'], sfx_sound(e['type'], rng) * e.get('vol', 1.0))
    raw_path = Path(tmp) / 'mix_raw.wav'
    with wave.open(str(raw_path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix / max(1, np.abs(mix).max() / .95), -1, 1) * 32767).astype(np.int16).tobytes())
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(raw_path), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', meas)[-1])
    return raw_path, -14 - I


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path); ap.add_argument('--out', type=Path)
    ap.add_argument('--check', action='store_true'); ap.add_argument('--contact-sheet', action='store_true')
    ap.add_argument('--clip', nargs=2, type=float)
    a = ap.parse_args()
    base = a.plan.resolve().parent; plan = json.loads(a.plan.read_text(encoding='utf-8'))
    probs = lint(plan, base)
    if a.check:
        for p in probs: print('PROBLEM:', p)
        print(f'plan check: {len(plan["scenes"])} scenes, {len(flat_lines(plan))} lines, '
              f'{sum(len(all_shots(l)) for *_, l in flat_lines(plan))} shots, {len(probs)} problems'); sys.exit(1 if probs else 0)
    if probs:
        for p in probs: print('PROBLEM:', p)
        sys.exit('fix the plan first (--check)')
    W = int(plan.get('width', 1280)); W -= W % 2; H = W * 9 // 16; H -= H % 2; fps = int(plan.get('fps', 24))
    out = a.out or base / 'final.mp4'; pics = Pictures(W, H)
    if a.contact_sheet:
        tl_shots = [sh for *_, ln in flat_lines(plan) for sh in all_shots(ln)]; tiles = []
        for i, sh in enumerate(tl_shots):
            if sh.get('card'): continue
            s = dict(sh, path=base / plan.get('images', {}).get(sh['image'], sh['image']))
            for key in ('from', 'to'):
                cam = s.get(key, s.get('from', [.5, .5, 1]))
                th = (pics.contain(s, cam[2]) if s.get('fit') == 'contain' else (lambda im_b: im_b[0].resize((W, H), Image.BICUBIC, box=im_b[1]))(pics.view(s, cam))).resize((320, 180))
                ImageDraw.Draw(th).text((4, 2), f'{i + 1} {key}', font=font(16), fill='yellow', stroke_width=2, stroke_fill='black'); tiles.append(th)
        cols = 6; sheet = Image.new('RGB', (cols * 320, math.ceil(len(tiles) / cols) * 180))
        for j, t in enumerate(tiles): sheet.paste(t, ((j % cols) * 320, (j // cols) * 180))
        p = out.with_name(out.stem + '_contact.png'); sheet.save(p); print('wrote', p); return
    tl = Timeline(plan, base); shots, fx, sfx, lts = build(plan, base, tl)
    t0, t1 = (a.clip[0], min(a.clip[1], tl.total)) if a.clip else (0.0, tl.total)
    for w in dict.fromkeys(tl.warn): print('  note:', w)
    with tempfile.TemporaryDirectory() as tmp:
        vid = Path(tmp) / 'video.mp4'
        render_video(plan, shots, fx, lts, tl, pics, vid, t0, t1, fps)
        raw, gain = mix_audio(plan, base, tl, sfx, tmp)
        def ts(x):
            ms = round(max(0, x) * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
            return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
        rows = [(max(tl.sp[k][0], t0) - t0, min(tl.sp[k][1], t1) - t0, ln.get('display', ln['text'])) for k, (*_, ln) in enumerate(tl.lines) if tl.sp[k][1] > t0 and tl.sp[k][0] < t1]
        srt = out.with_suffix('.srt'); srt.write_text('\n'.join(f'{i}\n{ts(s)} --> {ts(e)}\n{x}\n' for i, (s, e, x) in enumerate(rows, 1)), encoding='utf-8')
        meta = [';FFMETADATA1', f"title={plan.get('title', '')}"]; firsts = {}
        for k, (si, *_) in enumerate(tl.lines): firsts.setdefault(si, tl.start[k])
        for si, sc in enumerate(plan['scenes']):
            s, e = firsts[si], firsts.get(si + 1, tl.total)
            if e > t0 and s < t1:
                meta += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={round(max(0, s - t0) * 1000)}', f'END={round((min(e, t1) - t0) * 1000)}', f"title={si + 1:02d}. {sc.get('title', 'Scene')}"]
        mf = Path(tmp) / 'chapters.txt'; mf.write_text('\n'.join(meta) + '\n', encoding='utf-8')
        def mux(g):
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(vid), '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', str(raw), '-i', str(srt), '-i', str(mf),
                            '-map', '0:v', '-map', '1:a', '-map', '2:s', '-map_metadata', '3', '-map_chapters', '3',
                            '-af', f'volume={g:.2f}dB,alimiter=limit=0.84:level=false', '-ac', '2', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                            '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng', '-movflags', '+faststart', str(out)], check=True)
            m = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(out), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
            return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', m)[-1])
        got = mux(gain)
        if abs(got + 14) > 0.5: got = mux(gain - 14 - got)       # one correction pass
        print(f'loudness {got:.1f} LUFS')
    print(f'wrote {out} ({t1 - t0:.1f}s of {tl.total:.1f}s; {len(shots)} shots, {len(fx)} effects, {len(sfx)} sounds)')


if __name__ == '__main__':
    main()
```

## voice_fx.py

```python
#!/usr/bin/env python3
"""Per-character voice colour and tight comedy pauses for a narrate.py narration.

  python voice_fx.py plan.json                       # narration.wav + labels.txt -> narration_fx.wav + labels_fx.txt
  python voice_fx.py plan.json --gap 0.3 --scene-gap 0.6

plan.json:  "voice_fx": {"gnome": {"pitch": 5}, "dragon": {"pitch": -5, "echo": true}}
            "audio": "narration_fx.wav", "timestamps": "labels_fx.txt"

Each sentence is cut out of the narration using its label, trimmed of the silence the TTS
pads around it (Kokoro adds about 0.8 s per sentence), coloured if its speaker has an entry
(pitch in semitones with ffmpeg rubberband, duration kept; optional short echo), and laid out
again with exact pauses: --gap between lines, --scene-gap at scene changes, a line's own
"pause_after" wins. The new labels are exact by construction (sample counts). Run word_times.py
afterwards (it reads the plan's audio + timestamps). Needs ffmpeg with rubberband for pitch.
"""
import argparse, json, subprocess, tempfile, wave
from pathlib import Path
import numpy as np


def read_labels(p):
    out = []
    for l in Path(p).read_text(encoding='utf-8-sig').splitlines():
        q = l.split('\t')
        if len(q) >= 2 and not l.startswith('\\'):
            out.append((float(q[0]), float(q[1]), q[2] if len(q) > 2 else ''))
    return out


def rd(p):
    with wave.open(str(p)) as w:
        sr = w.getframerate(); n = w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return (x.reshape(-1, n).mean(1) if n > 1 else x), sr


def wr(p, x, sr):
    with wave.open(str(p), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def trim(x, sr, thr=0.002):
    idx = np.nonzero(np.abs(x) > thr)[0]
    if not len(idx): return x
    return x[max(0, idx[0] - int(.09 * sr)):min(len(x), idx[-1] + int(.08 * sr))]


def colour(x, sr, f):
    """-> (audio, tail samples after the speech, e.g. echo)."""
    flt = []
    if f.get('pitch'): flt.append(f"rubberband=pitch={2 ** (f['pitch'] / 12):.5f}:pitchq=quality")
    if f.get('echo'): flt.append('aecho=0.8:0.6:45|90:0.25|0.15')
    if not flt: return x, 0
    tail = int(.6 * sr) if f.get('echo') else 0
    with tempfile.TemporaryDirectory() as td:
        wr(Path(td) / 'i.wav', np.concatenate([x, np.zeros(tail, np.float32)]), sr)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(Path(td) / 'i.wav'), '-af', ','.join(flt),
                        '-ar', str(sr), '-ac', '1', str(Path(td) / 'o.wav')], check=True)
        y, _ = rd(Path(td) / 'o.wav')
    y = y[:len(x) + tail]
    y *= np.sqrt(np.mean(x ** 2)) / max(1e-9, np.sqrt(np.mean(y[:len(x)] ** 2)))   # keep the level
    return y, tail


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('plan', type=Path)
    ap.add_argument('--in', dest='src', default='narration.wav'); ap.add_argument('--labels-in', default='labels.txt')
    ap.add_argument('--out', default='narration_fx.wav'); ap.add_argument('--labels-out', default='labels_fx.txt')
    ap.add_argument('--gap', type=float, default=0.32); ap.add_argument('--scene-gap', type=float, default=0.6)
    ap.add_argument('--lead', type=float, default=0.25, help='silence before the first line')
    a = ap.parse_args()
    base = a.plan.resolve().parent; plan = json.loads(a.plan.read_text(encoding='utf-8'))
    fx = plan.get('voice_fx', {})
    x, sr = rd(base / a.src); labels = read_labels(base / a.labels_in)
    lines = [(ln, sc, li == len(sc['lines']) - 1) for sc in plan['scenes'] for li, ln in enumerate(sc['lines'])]
    if len(lines) != len(labels):
        raise SystemExit(f'{len(labels)} labels but {len(lines)} plan lines; re-narrate first')
    parts, out_labels, t, done = [], [], a.lead, 0
    for (s0, s1, text), (ln, sc, last) in zip(labels, lines):
        seg = trim(x[int(s0 * sr):int(s1 * sr)], sr)
        f = fx.get(ln.get('speaker', sc.get('speaker', 'narrator')), {})
        seg, tail = colour(seg, sr, f); done += bool(f)
        speech = len(seg) - tail
        parts.append((t, seg)); out_labels.append((t, t + speech / sr, text))
        t += speech / sr + float(ln.get('pause_after', a.scene_gap if last else a.gap))
    pcm = np.zeros(int((t + .5) * sr), np.float32)
    for t0, seg in parts:
        i = int(round(t0 * sr)); pcm[i:i + len(seg)] += seg[:len(pcm) - i]
    pcm *= min(1.0, 0.89 / max(1e-9, np.abs(pcm).max()))
    wr(base / a.out, pcm, sr)
    (base / a.labels_out).write_text(''.join(f'{s:.6f}\t{e:.6f}\t{x_}\n' for s, e, x_ in out_labels), encoding='utf-8')
    print(f'wrote {a.out} + {a.labels_out}: {len(out_labels)} lines, {len(pcm) / sr:.1f}s '
          f'(was {len(x) / sr:.1f}s), {done} coloured ({", ".join(sorted(fx)) or "none"})')


if __name__ == '__main__':
    main()
```

## word_times.py

```python
#!/usr/bin/env python3
"""Word start/end times for every narrated line -> words.json (for word-anchored shots and effects).

  python word_times.py plan.json --asr-dir models/sherpa-onnx-zipformer-small-en-2023-06-26

Uses the plan's "audio" + "timestamps" (from narrate.py). Each line's stretch of audio is
transcribed by the same small recognizer check_audio.py uses; its token timestamps give the
time each recognised word starts. The renderer matches an anchor word ("burst") against these
words, and falls back to an estimate from the word's position in the sentence if the
recognizer misheard it. Output: {"lines": [{"text", "start", "end", "words": [[w, t0, t1], ...]}]}
"""
import argparse, json, subprocess
from pathlib import Path
import numpy as np

SR, PAD = 16000, 0.25


def read_labels(p):
    out = []
    for l in Path(p).read_text(encoding='utf-8-sig').splitlines():
        q = l.split('\t')
        if len(q) >= 2 and not l.startswith('\\'):
            out.append((float(q[0]), float(q[1]), q[2] if len(q) > 2 else ''))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path); ap.add_argument('--asr-dir', required=True)
    ap.add_argument('--out', default='words.json'); ap.add_argument('--threads', type=int, default=2)
    a = ap.parse_args()
    import sherpa_onnx
    base = a.plan.resolve().parent; plan = json.loads(a.plan.read_text(encoding='utf-8'))
    d = Path(a.asr_dir)
    pick = lambda pat, alt: str((sorted(d.glob(pat)) or sorted(d.glob(alt)))[0])
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=pick('encoder*.int8.onnx', 'encoder*.onnx'), decoder=pick('decoder*.onnx', 'decoder*.onnx'),
        joiner=pick('joiner*.int8.onnx', 'joiner*.onnx'), tokens=str(d / 'tokens.txt'), num_threads=a.threads)
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(base / plan['audio']), '-ac', '1', '-ar', str(SR),
                          '-f', 's16le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    out = []
    for s0, s1, text in read_labels(base / plan['timestamps']):
        seg = x[int(s0 * SR):int(s1 * SR)]
        pad = np.zeros(int(PAD * SR), np.float32)
        st = rec.create_stream(); st.accept_waveform(SR, np.concatenate([pad, seg, pad])); rec.decode_stream(st)
        r = st.result; words = []
        for tok, t in zip(r.tokens, r.timestamps):
            t = round(max(s0, min(s1, s0 + t - PAD)), 3)
            if tok.startswith(' ') or not words: words.append([tok.strip().lower(), t, t])
            else: words[-1][0] += tok.lower()
        for k, w in enumerate(words):
            w[2] = words[k + 1][1] if k + 1 < len(words) else round(s1, 3)
        out.append(dict(text=text, start=s0, end=s1, words=words))
    (base / a.out).write_text(json.dumps({'lines': out}, indent=1), encoding='utf-8')
    print(f'wrote {a.out}: {len(out)} lines, {sum(len(l["words"]) for l in out)} words')


if __name__ == '__main__':
    main()
```

## upscale.py

```python
#!/usr/bin/env python3
"""4x upscale of painted art (storyboard sheets, small panels) with Real-ESRGAN general x4v3, CPU.

  python upscale.py realesr-general-x4v3.pth sheet.png sheet_x4.png

Weights (5 MB): GitHub xinntao/Real-ESRGAN release v0.2.5.0, realesr-general-x4v3.pth.
pip install torch (CPU build is enough). About 1 s per 256x256 tile on 2 cores; a 1672x941
sheet takes about a minute. Tiled with overlap, so any image size works.
"""
import sys, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from PIL import Image


class SRVGGNetCompact(nn.Module):
    def __init__(s, nin=3, nout=3, feat=64, nconv=32, up=4):
        super().__init__(); s.up = up
        b = [nn.Conv2d(nin, feat, 3, 1, 1), nn.PReLU(feat)]
        for _ in range(nconv): b += [nn.Conv2d(feat, feat, 3, 1, 1), nn.PReLU(feat)]
        b += [nn.Conv2d(feat, nout * up * up, 3, 1, 1)]
        s.body = nn.ModuleList(b); s.ps = nn.PixelShuffle(up)

    def forward(s, x):
        o = x
        for m in s.body: o = m(o)
        return s.ps(o) + F.interpolate(x, scale_factor=s.up, mode='nearest')


w, src, dst = sys.argv[1:4]
torch.set_num_threads(2)
net = SRVGGNetCompact(); sd = torch.load(w, map_location='cpu')
net.load_state_dict(sd.get('params', sd)); net.eval()
img = np.asarray(Image.open(src).convert('RGB'), np.float32) / 255
H, W, _ = img.shape; T, P, S = 256, 12, 4
out = np.zeros((H * S, W * S, 3), np.float32)
x = torch.from_numpy(img).permute(2, 0, 1)[None]
with torch.no_grad():
    for y0 in range(0, H, T):
        for x0 in range(0, W, T):
            ya, xa = max(0, y0 - P), max(0, x0 - P)
            yb, xb = min(H, y0 + T + P), min(W, x0 + T + P)
            r = net(x[:, :, ya:yb, xa:xb])[0].permute(1, 2, 0).numpy()
            ty, tx = min(T, H - y0), min(T, W - x0)
            oy, ox = (y0 - ya) * S, (x0 - xa) * S
            out[y0*S:(y0+ty)*S, x0*S:(x0+tx)*S] = r[oy:oy+ty*S, ox:ox+tx*S]
Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8)).save(dst)
print('wrote', dst, out.shape)
```

## merge_takes.py

```python
#!/usr/bin/env python3
"""Merge two narrate.py takes made at different speeds: lines of the named roles from take A, everyone
else from take B -> narration.wav + labels.txt (voice_fx.py then trims and re-spaces them).

  python merge_takes.py plan.json narration_100.wav labels_100.txt narration_094.wav labels_094.txt narrator
"""
import json, sys, wave
from pathlib import Path
import numpy as np

plan_p, a_wav, a_lab, b_wav, b_lab, roles = sys.argv[1:7]
roles = set(roles.split(','))
base = Path(plan_p).resolve().parent; plan = json.loads(Path(plan_p).read_text())
spk = [ln.get('speaker', sc.get('speaker', 'narrator')) for sc in plan['scenes'] for ln in sc['lines']]


def rd(p):
    with wave.open(str(base / p)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, w.getframerate()


def labs(p): return [l.split('\t') for l in (base / p).read_text().splitlines() if l.strip()]


A, sr = rd(a_wav); B, sr2 = rd(b_wav); assert sr == sr2
LA, LB = labs(a_lab), labs(b_lab); assert len(LA) == len(LB) == len(spk)
parts, out, n, gap = [], [], 0, np.zeros(int(.5 * sr), np.float32)
for s, la, lb in zip(spk, LA, LB):
    src, (s0, s1, text) = (A, la) if s in roles else (B, lb)
    seg = src[int(float(s0) * sr):int(float(s1) * sr)]
    out.append((n / sr, (n + len(seg)) / sr, text)); parts += [seg, gap]; n += len(seg) + len(gap)
x = np.concatenate(parts)
with wave.open(str(base / 'narration.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
(base / 'labels.txt').write_text(''.join(f'{a:.6f}\t{b:.6f}\t{t}\n' for a, b, t in out), encoding='utf-8')
print(f'merged {sum(s in roles for s in spk)} {"/".join(sorted(roles))} lines from {a_wav}, {sum(s not in roles for s in spk)} from {b_wav}')
```

## soft_lines.py

```python
#!/usr/bin/env python3
"""Soften lines marked "soft": true in plan.json: 7% slower (pitch kept), a little darker (-3 dB shelf
above 4.5 kHz, low-pass 9 kHz) and 4 dB quieter. Runs on the merged narration BEFORE voice_fx.py, so the
slower lines are laid out with exact timing:
  python soft_lines.py plan.json            # narration.wav + labels.txt, rewritten in place
"""
import json, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np

AF = "rubberband=tempo=0.93:pitchq=quality,highshelf=f=4500:g=-3,lowpass=f=9000"
plan_p = Path(sys.argv[1]); base = plan_p.resolve().parent; plan = json.loads(plan_p.read_text())
lines = [ln for sc in plan['scenes'] for ln in sc['lines']]
labels = [l.split('\t') for l in (base / 'labels.txt').read_text().splitlines() if l.strip()]
with wave.open(str(base / 'narration.wav')) as w:
    sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
parts, out, n, done = [], [], 0, 0
for k, (ln, (s0, s1, text)) in enumerate(zip(lines, labels)):
    seg = x[int(float(s0) * sr):int(float(s1) * sr)]
    if ln.get('soft'):
        with tempfile.TemporaryDirectory() as td:
            ip, op = Path(td) / 'i.raw', Path(td) / 'o.raw'; seg.tofile(ip)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', str(ip), '-af', AF,
                            '-f', 'f32le', '-ar', str(sr), '-ac', '1', str(op)], check=True)
            seg = np.fromfile(op, np.float32) * 10 ** (-4 / 20)
        done += 1
    gap = (float(labels[k + 1][0]) - float(s1)) if k + 1 < len(labels) else .5
    out.append((n / sr, (n + len(seg)) / sr, text)); parts += [seg, np.zeros(int(gap * sr), np.float32)]; n += len(seg) + int(gap * sr)
y = np.concatenate(parts)
with wave.open(str(base / 'narration.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
(base / 'labels.txt').write_text(''.join(f'{a:.6f}\t{b:.6f}\t{t}\n' for a, b, t in out), encoding='utf-8')
print(f'softened {done} line(s)')
```

## radio_fx.py

```python
#!/usr/bin/env python3
"""Radio colour for the speakers listed in plan["radio"]: band-pass, soft clip, crackle.
Edits the plan's narration audio in place, same length, so labels stay exact. Run after voice_fx.py.
  python radio_fx.py plan.json
"""
import json, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np

plan_p = Path(sys.argv[1]); base = plan_p.resolve().parent; plan = json.loads(plan_p.read_text())
radio = set(plan.get('radio', []))
lines = [ln for sc in plan['scenes'] for ln in sc['lines']]
labels = [tuple(l.split('\t')) for l in (base / plan['timestamps']).read_text().splitlines() if l.strip()]
with wave.open(str(base / plan['audio'])) as w:
    sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
x = x.copy(); rng = np.random.default_rng(5); n = 0
for ln, (s0, s1, _) in zip(lines, labels):
    if ln.get('speaker') not in radio: continue
    i0, i1 = int(float(s0) * sr), int(float(s1) * sr); seg = x[i0:i1]
    with tempfile.TemporaryDirectory() as td:
        ip, op = Path(td) / 'i.raw', Path(td) / 'o.raw'; seg.tofile(ip)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', str(ip),
                        '-af', 'highpass=f=450,highpass=f=450,lowpass=f=2800,lowpass=f=2800,acompressor=threshold=0.08:ratio=6',
                        '-f', 'f32le', '-ar', str(sr), '-ac', '1', str(op)], check=True)
        y = np.fromfile(op, np.float32)[:len(seg)]
    y = np.tanh(y * 3.0) / np.tanh(3.0)
    y *= np.sqrt(np.mean(seg ** 2)) / max(1e-9, np.sqrt(np.mean(y ** 2)))
    hiss = rng.standard_normal(len(y)).astype(np.float32) * .012
    crack = (rng.random(len(y)) < 0.0015) * rng.standard_normal(len(y)) * .25
    x[i0:i0 + len(y)] = y + hiss + crack.astype(np.float32); n += 1
x *= min(1.0, .89 / np.abs(x).max())
with wave.open(str(base / plan['audio']), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype(np.int16).tobytes())
print(f'radio colour on {n} line(s)')
```

## narrator_booth.py

```python
#!/usr/bin/env python3
"""Trailer-voice "booth" treatment for the narrator's lines: high-pass 80 Hz, 3:1 compression, +2.5 dB at
120 Hz, +2 dB at 4 kHz, light de-ess, then a short room (0.6 s, 25 ms pre-delay, about 11% wet). Edits the
plan's narration audio in place; each line keeps its level (RMS matched), so the balance between speakers is
unchanged. The room tail may run into the pause but stops 50 ms before the next line. Run after voice_fx.py
and radio_fx.py.
  python narrator_booth.py plan.json
"""
import json, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

BOOTH = ("highpass=f=80,acompressor=threshold=0.08:ratio=3:attack=15:release=120:makeup=1.5,"
         "equalizer=f=120:t=q:w=0.8:g=2.5,equalizer=f=4000:t=q:w=1.0:g=2,deesser=i=0.3")
plan_p = Path(sys.argv[1]); base = plan_p.resolve().parent; plan = json.loads(plan_p.read_text())
spk = [ln.get('speaker', sc.get('speaker', 'narrator')) for sc in plan['scenes'] for ln in sc['lines']]
labels = [(float(a), float(b)) for a, b, *_ in (l.split('\t') for l in (base / plan['timestamps']).read_text().splitlines() if l.strip())]
with wave.open(str(base / plan['audio'])) as w:
    sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
x = x.copy()
rng = np.random.default_rng(3); n = int(.9 * sr)
ir = rng.standard_normal(n) * np.exp(-np.arange(n) / sr * 6.9 / .6)
ir = sosfilt(butter(2, 4500, 'low', fs=sr, output='sos'), ir); ir = np.concatenate([np.zeros(int(.025 * sr)), ir]); ir /= np.sqrt((ir ** 2).sum())
done = 0
for k, (s, (a, b)) in enumerate(zip(spk, labels)):
    if s != 'narrator': continue
    i0, i1 = int(a * sr), int(b * sr); seg = x[i0:i1].copy()
    with tempfile.TemporaryDirectory() as td:
        ip, op = Path(td) / 'i.raw', Path(td) / 'o.raw'; seg.tofile(ip)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', str(ip), '-af', BOOTH,
                        '-f', 'f32le', '-ar', str(sr), '-ac', '1', str(op)], check=True)
        y = np.fromfile(op, np.float32)[:len(seg)]
    nxt = int(labels[k + 1][0] * sr) - int(.05 * sr) if k + 1 < len(labels) else len(x)
    room = fftconvolve(y, ir)[:max(len(y), min(len(y) + len(ir), nxt - i0))]
    room *= np.sqrt((y ** 2).mean()) / max(1e-9, np.sqrt((room[:len(y)] ** 2).mean()))
    out = np.zeros(len(room), np.float32); out[:len(y)] = y; out += .11 * room
    tail = np.ones(len(out), np.float32); m = len(out) - len(y)
    if m > 0: tail[len(y):] = np.linspace(1, 0, m) ** 2
    out *= tail
    out *= np.sqrt((seg ** 2).mean()) / max(1e-9, np.sqrt((out[:len(seg)] ** 2).mean()))
    x[i0:i0 + len(seg)] = out[:len(seg)]
    if len(out) > len(seg): x[i1:i0 + len(out)] += out[len(seg):]
    done += 1
x *= min(1.0, .89 / np.abs(x).max())
with wave.open(str(base / plan['audio']), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
print(f'booth treatment on {done} narrator line(s)')
```

Order with these: `narrate.py` (two takes) -> `merge_takes.py` -> `soft_lines.py` -> `voice_fx.py` ->
`radio_fx.py` -> `narrator_booth.py` -> `word_times.py` -> `check_audio.py`.