---
name: "narrated-explainer-video"
description: "Make a narrated slideshow video (explainer, lesson, training, story) from a topic or notes: TTS-ready script, code-drawn boards or 4-panel comic pages, markers that point at what is being said, local Kokoro narration with exact timestamps, synced MP4."
---

# Narrated explainer video

A video built like a teacher at a board: a **few high-resolution still boards**, a **TTS-ready
script**, and **markers** (a box, underline or ring) that appear on whatever each sentence talks
about. The view holds still; it only moves to the next board or panel between topics. TTS audio
and its sentence timestamps set all timing: narrate it yourself with a local voice (`narrate.py`),
or use the user's own TTS export.

Pipeline: **source -> scenes -> boards -> checks -> plan.json (text + marks) -> narration + timestamps -> contact sheet -> MP4.**

**Done means all of these exist and pass:** boards (opened and looked at), `plan.json` passing
`render_video.py --check`, `validation.md` from `validate.py`, the contact sheet (opened, every mark
on its item), narration with `check_audio.py` reporting no PROBLEM, then `final.mp4`.

The three scripts at the end (`render_video.py`, `narrate.py`, `check_audio.py`) are tested tools:
write them out exactly as given and do not tidy, shorten or "improve" them while copying.

## 1. Pick a layout and plan the scenes

| Layout | Board | Scene | Good for |
|---|---|---|---|
| **Single board** | one 16:9 board per idea, 3840x2160 | the whole board, 4-8 sentences | short pieces, 1-5 minutes |
| **Panel pages** (manga/comic) | one 16:9 page with a 2x2 grid of 16:9 panels, 5120x2880 | one panel, 4-8 sentences | longer reviews, stories; 4 scenes per image |

- Panel pages are usually best past ~5 minutes: few images, consistent style. The view glides to
  the next panel at each scene change; a new page cross-fades in.
- Use a **fixed layout inside every board/panel** (e.g. title top-left, graph left, equations right,
  bullet notes under them, takeaway line at the bottom), so marks are easy to place.
- Read the source material. Ask about length, audience and look only if they are unclear.
  Give each scene a title (it becomes a chapter marker) and a one-line purpose.
- **Size it from the word count, as a ballpark.** Kokoro Heart at speed 1.0 measured 159 words per
  minute while speaking and about 144 with the default pauses: 5 minutes is about 700 words,
  50-55 sentences, 7-8 boards of 6-9 sentences; 10 minutes is about 1,450 words.
- **A requested length is a target, not a contract.** Within about 15% is fine (a "ten minute"
  video can run 8:30 to 11:30). Don't cut useful content just to hit an exact number; trim only
  when the narration is clearly out of range, and say what length it came out at.
- **Measure the pace before writing the whole script.** Write the first scene or two into
  `plan.json` and run `narrate.py plan.json --model-dir <voice folder> --sample 8`. It voices those
  lines into the cache (the full run reuses them), prints the words per minute, and writes no audio
  files. Size the rest of the script from that number, especially for a voice or speed other than
  Kokoro Heart at 1.0.
- A strong shape for teaching: hook question, building blocks one per board, the payoff with real
  numbers, recap, a test-yourself question, then the answer (plus an optional bonus fact).
- Time budget for a 5-minute video: writing and boards take most of the work; narration about
  2 minutes and the 1080p render under 2 minutes on a 2-core machine.

## 2. Write the narration in `plan.json`

`plan.json` is the single source of truth for narration. TTS text files are exported from it,
so the script and the plan cannot drift apart.

- One sentence per line. Each sentence should point at one thing on the board.
- Write it exactly as spoken: "x cubed minus three halves x squared", "one comma negative one half",
  "f double prime of x". No symbols, markdown, bullets, abbreviations or digits that could be misread.
- Short sentences (about 6-25 words); budget words by the measured pace (step 1).
- Fix errors in the source rather than repeating them, and tell the user what you corrected.
- **Use one spelling variant everywhere** (e.g. "color" on the boards if the narration says color),
  matching the viewer's locale.
- **Quiz: question on one board, answer on the next**, so the answer isn't visible while the viewer
  thinks. Give the question line `"pause_after": 5`. On panel pages put the answer on a new page,
  not the neighbouring panel: the glide between panels can show it early.
- **One narrator by default.** Use several voices only when the piece has dialogue or characters
  (a student asking, a teacher answering, a story): add a `"cast"` and put `"speaker"` on those
  lines or scenes (step 6). Keep speaker names out of the spoken text.

## 3. Draw the boards with code

- **Everything the narration names must be on the board.** If a sentence states a formula, a rule
  or a domain, draw it; otherwise the viewer hears something they can't see and there is nothing to mark.
- **All text, equations, numbers, labels and charts are drawn with code** (matplotlib with mathtext,
  Pillow, or HTML/SVG screenshotted with Playwright). Image generators garble text and math, so use
  them only for decorative art with no lettering, and add any words on top with code.
- Compute every plotted value from the real data or formula (e.g. sympy -> lambdify), never by eye.
  Put the formulas and numbers in **one module** (e.g. `physics.py`, `data.py`) that the boards, the
  script numbers and `validate.py` all import, so they can never disagree.
- **Label simplified models on the board** ("Model: clean air, Rayleigh scattering only") when a
  number comes from an idealised calculation.
- **Keep diagrams simple**: one idea per drawing, few arrows, lots of empty space. A busy diagram
  hides what the marker points at.
- Consistent style: dark "chalkboard" background, one accent color per concept, generous margins,
  space between rows so a box fits around each line without touching its neighbours.
- The whole panel is on screen and viewers can go fullscreen, so normal readable sizes are fine;
  avoid tiny tick numbers.
- Captions are usually off (`"captions": false`) since the board carries the content; the `.srt` is given separately.
- Name files `board01.png`, `board02.png`, ... Save the drawing script so boards can be rebuilt.
- Open every board image and look at it: nothing overlapping, clipped, or too small.

**Draw with the board helper below; it records where everything is.** Name each element a sentence
may point at while you draw it; after layout its exact box (or a graph point's position) is read
back from matplotlib, so marks come from the drawing itself, with no guessing or pixel searching.
It handles single boards and 2x2 panel pages the same way: coordinates are always relative to one
panel, and `save()` returns marks ready to paste into each scene.

```python
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
BG, INK, ACCENT = "#0B1015", "#F0F0E7", "#FFD36F"
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "text.color": INK})


class Board:
    """A board image whose named elements become plan.json marks, read back from the drawing.

    Single board: Board("board01.png") -> 3840x2160. Panel page: Board("page01.png", grid=(2, 2))
    -> 5120x2880, four 16:9 panels. Every coordinate is relative to ONE panel (0..1, matplotlib
    style: x right, y UP), so drawing a panel is the same as drawing a single board.
    save() returns the marks dict for a single board, or {(col, row): marks} for a panel page,
    already panel-relative and top-left based, ready to paste into each scene's "marks".
    """
    def __init__(self, path, grid=(1, 1)):
        self.path, self.cols, self.rows, self.reg = path, grid[0], grid[1], []
        self.dpi = 240 if grid == (1, 1) else 160
        self.fig = plt.figure(figsize=(16 * self.cols, 9 * self.rows), dpi=self.dpi, facecolor=BG)

    def _fig(self, x, y, panel):                     # panel coords -> figure coords
        c, r = panel
        return (c + x) / self.cols, (self.rows - 1 - r + y) / self.rows

    def text(self, x, y, s, size=24, color=INK, name=None, panel=(0, 0), **kw):
        t = self.fig.text(*self._fig(x, y, panel), s, fontsize=size, color=color, va="center", **kw)
        if name: self.reg.append((name, "box", t, panel))
        return t

    def title(self, s, panel=(0, 0)):
        return self.text(.045, .905, s, 34, weight="bold", panel=panel)

    def axes(self, rect, panel=(0, 0)):              # rect = [left, bottom, width, height] in the panel
        x, y = self._fig(rect[0], rect[1], panel)
        ax = self.fig.add_axes([x, y, rect[2] / self.cols, rect[3] / self.rows]); ax.set_facecolor(BG)
        return ax

    def box(self, name, artist, panel=(0, 0)):       # any drawn thing: image, axes, patch, legend
        self.reg.append((name, "box", artist, panel))

    def ring(self, name, ax, x, y, r=.035, panel=(0, 0)):   # a point in the axes' DATA coordinates
        self.reg.append((name, "ring", (ax, x, y, r), panel))

    def save(self, pad=.008):
        self.fig.canvas.draw(); rr = self.fig.canvas.get_renderer()
        W, H = self.fig.canvas.get_width_height()     # real pixel size, whatever the grid
        pw, ph = W / self.cols, H / self.rows         # one panel in pixels
        px = lambda X, c: X / pw - c                  # pixel -> panel fraction (x)
        py = lambda Y, r: (H - Y) / ph - r            # pixel (bottom-up) -> panel fraction (y, top-down)
        padv = pad * pw / ph                          # same padding in pixels on every side
        out = {}
        for name, kind, o, (c, r) in self.reg:
            m = out.setdefault((c, r), {})
            if kind == "box":
                b = o.get_window_extent(rr)
                m[name] = {"box": [*(float(round(v, 4)) for v in (px(b.x0, c) - pad, py(b.y1, r) - padv,
                                                                px(b.x1, c) + pad, py(b.y0, r) + padv))]}
            else:
                ax, x, y, rad = o; X, Y = ax.transData.transform((x, y))
                m[name] = {"ring": [float(round(px(X, c), 4)), float(round(py(Y, r), 4))], "r": rad}
        self.fig.savefig(self.path, dpi=self.dpi, facecolor=BG); plt.close(self.fig)
        return out.get((0, 0), {}) if (self.cols, self.rows) == (1, 1) else out

# single board
b = Board("board01.png")
b.title("Turning points")
b.text(.56, .70, r"$f(x)=x^3-\frac{3}{2}x^2$", 30, ACCENT, name="E1")
ax = b.axes([.06, .22, .42, .52])
# ... plot computed data on ax ...
b.ring("G:max", ax, 0, 0)
marks = b.save()                      # {"E1": {"box": [...]}, "G:max": {"ring": [...], "r": .035}}

# panel page: the same calls with panel=(col, row); scene "panel" for (col, row) is
# [col * 0.5, row * 0.5, 0.5, 0.5]
page = Board("page01.png", grid=(2, 2))
page.title("Second derivative", panel=(1, 0))
page.text(.56, .70, r"$f''(x)=6x-3$", 30, ACCENT, name="E2", panel=(1, 0))
marks = page.save()                   # {(1, 0): {"E2": {...}}, ...}
```

- A phrase drawn as two text lines is one item: merge the two boxes into one mark.
- `axes(rect)` takes [left, bottom, width, height] inside the panel; use it instead of
  `fig.add_axes` so graphs land in the right panel.

## 4. Check the content

- Write a small `validate.py` that re-checks every fact shown on the boards and said in the script
  (for math: sympy derivatives, roots, coordinates, signs, domains; for data: totals against the source).
  It should fail loudly. Make sure the board and the narration say the same values.
- Check the **spoken** form too: compute the number, then assert the narration contains the matching
  words (25.0% -> "a quarter", 37.9 -> "thirty eight").
- Structure is checked by the tool: `python render_video.py plan.json --check` fails on missing
  images, unknown marks or speakers, marks outside 0..1, digits or symbols in spoken text, and quiz
  questions without `"pause_after"` of 4 or more. Run it before narrating; fix every PROBLEM.
- Save a short `validation.md` listing what was checked and any source errors corrected.

## 5. `plan.json` and marks

```json
{
  "title": "Derivative tests",
  "width": 1920, "fps": 24, "captions": false,
  "audio": "narration.wav", "timestamps": "labels.txt",
  "scenes": [
    {"title": "Turning points", "image": "board01.png",
     "marks": {"E1": {"box": [0.54, 0.25, 0.79, 0.33]},
               "E2": {"box": [0.54, 0.37, 0.76, 0.45]},
               "F":  {"box": [0.04, 0.90, 0.42, 0.96]},
               "G:max": {"ring": [0.18, 0.40], "r": 0.032},
               "G:min": {"ring": [0.38, 0.62], "r": 0.032}},
     "lines": [
       {"text": "Consider f of x equals x cubed minus three halves x squared.", "mark": "E1"},
       {"text": "Its first derivative factors as three x times the quantity x minus one.", "mark": "E2"},
       {"text": "The critical numbers are zero and one.", "mark": "E2"},
       {"text": "So zero comma zero is a local maximum, and one comma negative one half is a local minimum.", "mark": ["G:max", "G:min"]},
       {"text": "Neither point is an absolute extremum.", "mark": "F"},
       {"text": "Keep that in mind for the next example."}
     ]},
    {"title": "Concavity", "image": "page01.png", "panel": [0.5, 0, 0.5, 0.5],
     "marks": {"E2": {"box": [0.55, 0.25, 0.74, 0.34]}},
     "lines": [
       {"text": "The second derivative is six x minus three.", "mark": "E2"}
     ]}
  ]
}
```

- `panel` = [left, top, width, height] of the scene's region on the image (0-1). Omit it for single boards.
  2x2 panels: [0,0,.5,.5], [.5,0,.5,.5], [0,.5,.5,.5], [.5,.5,.5,.5] in reading order.
  Keep panels 16:9 shaped; a board image that is not 16:9 is letterboxed and its panels and marks
  are moved to match automatically.
- All mark coordinates are **panel-relative** (0-1 from the panel's top-left). Shapes:
  `{"box": [x0, y0, x1, y1]}`, `{"underline": [x0, y, x1]}`, `{"ring": [x, y], "r": 0.032}` (r = fraction of panel height).
- A line's `"mark"` is a name, a list of names (several things at once), or an inline shape. No mark = nothing highlighted.
- Scene `"title"` becomes a chapter marker in the MP4. Defaults: width 1920, fps 24, captions off.

### Marking rules

- **Mark what the sentence names**, chosen by meaning: a sentence stating a formula marks that
  formula; one about a point on the curve rings that point; one restating a bullet boxes that note;
  the moral boxes the takeaway line. Several items named = several marks.
- **General sentences get no mark** (introductions, transitions, anything not on the board). Never
  add a mark just to have one.
- Repeating the same mark on consecutive sentences keeps it solid (no flicker).
- Marks appear when that sentence's own speech starts (not during a spoken scene title) and fade
  when the next sentence starts, so a mark stays up through a pause (a quiz question stays marked
  while viewers think). At a scene change the old board leaves in the pause, before the next speech.
- **Take mark positions from the drawing** (the `Board` helper in step 3). Only for boards you did
  not draw yourself (someone else's images), fit boxes to the ink: search a region of the board image
  for non-background pixels and pad the bounding box by ~0.01:

```python
import numpy as np
def ink_box(panel_img, x0, y0, x1, y1, pad=0.01):
    """Panel-relative search region -> tight panel-relative box around the ink drawn there."""
    W, H = panel_img.size
    rgb = panel_img.convert('RGB'); bg = np.array(rgb.getpixel((2, 2)))   # board background colour
    a = np.asarray(rgb.crop((int(x0*W), int(y0*H), int(x1*W), int(y1*H)))).astype(int)
    ys, xs = np.nonzero(np.abs(a - bg).max(axis=2) > 45)
    if not len(xs): raise ValueError(f'no ink in region {x0, y0, x1, y1}; widen it')
    return [x0 + xs.min()/W - pad, y0 + ys.min()/H - pad, x0 + (xs.max()+1)/W + pad, y0 + (ys.max()+1)/H + pad]
```

- **Place rings from the math**: `Board.ring` with the point's data coordinates does this for you.
  By hand: with the axes rectangle (left, top, width, height in panel coordinates) and axis limits,
  `x_panel = left + width*(x - xmin)/(xmax - xmin)`, `y_panel = top + height*(ymax - y)/(ymax - ymin)`.
- Camera: leave `camera` out entirely. Each scene shows its whole panel, still. Only add a
  `camera` close-up ([center_x, center_y, zoom] inside the panel, or a preset name) if the user asks
  for zooming; then move only when the subject changes and never back-and-forth.

## 6. Timing: how the audio drives the video

Best to worst:

1. **One audio file + timestamps** (`"audio"` + `"timestamps"` at plan level). Every sentence starts
   exactly on its own timestamp. Accepts Audacity labels (start, end, text separated by tabs), SRT,
   VTT, or JSON `[{"start", "end", "text"}]`. Entries are matched to plan lines by text in order,
   so the timestamp file may contain extra entries (e.g. spoken scene titles); they are folded into
   the start of the next line, and listed in the console. A plan line with no match stops the render
   and names the line, so fix the plan text or the timestamps.
2. **One audio file per scene** (`"audio"` per scene or `--audio-dir` with `scene01.wav`, ...).
   Scene changes are exact; lines inside a scene are split by word count unless `"seconds"` is given.
3. **No audio**: `--preview` estimates at 150 words per minute.

Prefer **WAV**. MP3 encoders add ~25-50 ms of silence at the start; if only MP3 exists, set
`"audio_offset"` to that delay (measure it against a WAV if one exists, or use 0.046 for LAME).

### Narrate it yourself (draft or final)

`narrate.py` (below) voices `plan.json` locally, the way the Read Aloud app does: one sentence at a
time, joined with pauses, plus an Audacity label file with exact times. Then set
`"audio": "narration.wav", "timestamps": "labels.txt"` and render. Use it for every preview so
timing and pauses are real, and as the final narration when the user wants it.

```bash
python narrate.py plan.json --model-dir <voice folder> --voice af_heart   # -> narration.wav + labels.txt
python narrate.py plan.json --model-dir <voice folder> --sample 8          # pace check, no audio files
python narrate.py --list-voices --model-dir <voice folder>
```

Every run prints the pace (words per minute while speaking and with pauses) and the total length.

Voices, best first:
1. **The user's own Read Aloud voice folder** if they provide it: `voices/kokoro-gpu-v1-0`
   (Kokoro v1.0, 54 voices; speaker numbers match the app, 0 = Heart). Measured at about
   1.5-2.5x real time on a 2-core CPU. `pip install onnxruntime espeakng-loader phonemizer-fork numpy`
2. **The same Kokoro v1.0 downloaded** (326 MB) from Hugging Face `onnx-community/Kokoro-82M-v1.0-ONNX`:
   `onnx/model.onnx`, `tokenizer.json`, `voices/<name>.bin` into one folder (layout as above).
3. **Kitten TTS micro 0.8** for a fast, small (63 MB) draft: sherpa package `tecmage/kitten-micro-en-v0_8`
   on Hugging Face; needs `pip install sherpa-onnx==1.13.4` (2.x asks for a lexicon file). About 2x real time.
4. **Piper Amy** (Read Aloud's default voice): `vits-piper-en_US-amy-medium.tar.bz2` from the
   sherpa-onnx GitHub `tts-models` release.

- **Several voices**: put a cast in `plan.json` and `"speaker"` on a line (that line only) or a scene
  (its default); untagged lines use `"narrator"`. A cast entry is one voice or one per engine, so the
  plan works with Kokoro or Kitten:
  `"cast": {"narrator": "af_heart", "student": {"kokoro": "am_adam", "kitten": 3}, "teacher": {"kokoro": "bf_emma", "kitten": 2}}`.
  Unknown speakers or voices stop before any audio is made. Pick voices that differ clearly
  (e.g. a male and a female voice, or US and UK); British Kokoro voices (`bf_`, `bm_`) get British
  pronunciation. Speakers are level-matched automatically (one gain per speaker). `check_audio.py`
  prints each speaker's pitch and loudness so you can confirm the change is audible.
- With no `--voice` and no cast, Kokoro uses Heart (`af_heart`). Speaker numbers (0 = Heart) only
  work with the Read Aloud voice folder, which has the numbering in `voice.json`.
- **Sentence cache** (like Read Aloud's Render / Update): every voiced sentence is kept in
  `tts_cache/`, keyed by code version, engine, model, voice, speed and text. After editing the
  script, rerun `narrate.py` and only the changed lines are voiced again; each run lists the lines
  it re-voiced. The labels are rebuilt for the whole narration, so timing stays exact.
- **If it isn't broken, don't fix it.** Edit only the lines that need it (a wrong fact, a
  mispronunciation, a mark that needs a sentence); untouched lines keep their audio. A board or
  mark fix needs no new narration at all: rebuild the board and re-render.
- Never hand over a video whose narration is missing sentences or failed a check; fix and re-narrate.
  `narrate.py` warns when Kokoro drops sounds it cannot say or cuts off an over-long sentence: respell
  or split that line.
- Scene changes get a longer pause (sentence gap + 0.4 s, like Read Aloud's paragraph pause).
- **Give viewers time to think:** any "pause and answer" moment (quiz question, "try it yourself")
  needs `"pause_after": 4` or more on that line. A normal sentence gap (~1 s) is too short to recall anything.
- Listen-free check: run `check_audio.py` (step 9) on every narration.

## 7. Render

Write the renderer below to `render_video.py` next to `plan.json`. Needs ffmpeg/ffprobe and Pillow.

```bash
python render_video.py plan.json --check               # lint the plan (run before narrating)
python render_video.py plan.json --export-tts tts      # tts/scene01.txt ... + narration_all.txt
python render_video.py plan.json --contact-sheet       # final_contact.png: every line's view with its marks
python render_video.py plan.json --preview             # preview.mp4, silent, estimated timing
python render_video.py plan.json --clip 300 330        # quick 30 s check with real audio
python render_video.py plan.json                       # final.mp4 (+ .srt, _timing.json, chapters)
python render_video.py plan.json --audio-dir audio     # final, from per-scene files
```

- **Always open the contact sheet** and check every mark sits on the item its sentence names.
  Render a `--clip` across a scene change before the full render.
- Speed: roughly 3-5 minutes for a 16-minute video at 1920x1080, 24 fps. Run long renders in the background.
- A final render refuses to run without narration for every scene; `--preview` is the silent draft
  (it includes each `pause_after`).
- The MP4 carries chapters and a subtitle track viewers can switch on; captions burned into the
  picture are off unless `"captions": true`. Options: `--out name.mp4`, `--no-captions`.

## 8. Hand off for TTS

If you narrated it yourself, the video is already complete; offer the hand-off below only if the
user wants their own voice or app for the final.

Deliver the boards, `tts/` folder, preview, contact sheet, `plan.json`, `render_video.py`, `narrate.py`, `check_audio.py`,
the drawing and validation scripts, and a short `README` / audio checklist telling the user:
- Best: read `tts/narration_all.txt` as **one WAV plus a timestamp file** (labels/SRT/VTT/JSON), if the TTS can export one.
  For the Read Aloud app: paste `narration_all.txt`, set the sentence pause, Render, turn on the label
  track and export WAV; it writes `read-aloud-narration.wav` and `read-aloud-narration-labels.txt`
  with exact sentence times.
- Otherwise: one file per scene, `tts/scene01.txt` -> `scene01.wav`, and so on. Same voice and speed throughout.
- Scene titles may be spoken or not; both work.
Also give a human-readable `script_with_scene_headings.md` (titles + narration) for review.
If audio is already supplied, skip straight to the final render.

## 9. Check the final

- Confirm the video and audio durations match (`ffprobe`) and read `final_timing.json`.
- Run `check_audio.py plan.json --asr-dir <speech recognizer folder>` (below). It finds every plan
  line in the timestamps (any format), transcribes that stretch of audio and compares it with the
  **plan** text, so narration made from an older script fails. It also reports silence, overlaps,
  clipping, pauses, quiz think time (4 s or more) and, with several speakers, each one's pitch and
  loudness. PROBLEM lines are failures (exit code 1): fix every one before the final render.
  "check" lines are for review only.
- The recognizer is a proxy, not a listener. It cannot judge how natural the voice sounds, and it
  mishears some clear speech (single-letter math names like "x" heard as "ex", "sky blue" as
  "skyblue"). Respell a word only when a real word is consistently misheard; never bend the script
  to please the recognizer. When the user can listen, their ear wins.
- Pull frames a second or two into a few sentences (`ffmpeg -ss T -i final.mp4 -frames:v 1 f.png`)
  and check the marked item is the one being said.
- If a mark is wrong, fix it in `plan.json` and re-render; with timestamps no new audio is needed.

## render_video.py

```python
#!/usr/bin/env python3
"""Narrated slideshow renderer: still boards + narration -> MP4.

  python render_video.py plan.json                    # final video
  python render_video.py plan.json --audio-dir audio  # per-scene files sceneNN.wav/.mp3/...
  python render_video.py plan.json --preview          # silent, estimated timing
  python render_video.py plan.json --clip 300 330     # render only 300-330 s (quick check)
  python render_video.py plan.json --contact-sheet    # one thumbnail per line's camera target
  python render_video.py plan.json --export-tts tts   # write tts/sceneNN.txt + narration_all.txt
  python render_video.py plan.json --check            # lint the plan before making any audio

plan.json:
{
  "title": "My video",
  "width": 1920, "fps": 24, "captions": false,       # optional (these are the defaults)
  "presets": {"graph": [0.28, 0.55, 1.7]},           # optional named cameras
  "audio": "narration.wav",                          # optional: ONE file for the whole video...
  "timestamps": "labels.txt",                        # ...with per-sentence times
  "audio_offset": 0.0,                               # optional seconds to skip (e.g. MP3 delay)
  "mark_color": "#FFD36F",                           # optional marker colour
  "scenes": [
    {"image": "board01.png",
     "panel": [0, 0, 0.5, 0.5],                      # optional [left, top, width, height]
     "audio": "audio/scene01.wav",                   # optional per-scene audio instead
     "marks": {"E1": {"box": [0.54, 0.25, 0.80, 0.33]},     # panel-relative shapes
               "max": {"ring": [0.21, 0.42], "r": 0.032},
               "key": {"underline": [0.05, 0.95, 0.60]}},
     "lines": [
       {"text": "Sentence spoken by the TTS."},
       {"text": "Next sentence.", "mark": "E1"},
       {"text": "Another.", "mark": ["E1", "max"], "seconds": 4.2},
       {"text": "Rare close-up.", "camera": [0.3, 0.4, 1.5]}
     ]}
  ]
}
Marks (the default way to point): a box, underline or ring drawn over the board for the
sentence that names it. It fades in when that sentence starts speaking and out when the
next sentence starts (so it stays up through a pause, e.g. a quiz question's think time),
and stays solid across consecutive sentences with the same mark. "marks" can be given per
scene or for the whole plan; a line's "mark" is a name, a list of names, or an inline shape.
Timing, best first: (1) one audio file + "timestamps" (Audacity labels, SRT, VTT or JSON
[{start,end,text}]); entries are matched to plan lines by text, and unmatched entries
(e.g. spoken scene titles) are absorbed into the next line. A new scene appears in the
pause before its first speech (at most 1.2 s early, so a quiz think pause keeps the old
board up), and its cross-fade or glide finishes before that speech starts.
(2) per-scene audio: scene length = file length, lines split by word count unless "seconds"
is given. (3) estimate (--preview), including each line's "pause_after".
A final render needs narration for every scene; use --preview for a silent draft.
Boards that are not 16:9 are letterboxed and their panels/marks are moved to match.
camera = [center_x, center_y, zoom] inside the scene's panel (or whole image): 0..1 from
top-left, zoom 1 = whole panel; or a preset name ("wide" = [0.5, 0.5, 1] is built in).
No camera (or "hold") = stay where the previous line was; a scene's first line defaults
to wide, so a plan with no cameras shows each whole panel, still. When a line does set a
camera it moves once at the start of the line, then holds, and never shows neighbouring
panels. Scenes sharing an image glide across it; a new image cross-fades in.
Scene "title" fields become chapter markers. Paths relative to plan.json.
Needs: ffmpeg/ffprobe, Pillow.  Writes <out>.mp4 (with chapters and a subtitle track viewers
can switch on), <out>.srt, <out>_timing.json.
"""
import argparse, difflib, json, math, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WPM = 150          # speaking-rate guess when there is no audio
LINE_PAD = 0.42    # pause per line in estimated timing
FADE = 0.6         # cross-fade seconds when the image changes
SCENE_LEAD = 1.2   # a new scene appears at most this long before its first speech
AUDIO_EXT = ('.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac')
QUIZ = re.compile(r'quiz|test yourself|question|your turn|pause|think|try it', re.I)
SPOKEN_BAD = re.compile(r'[0-9%=^/\\$<>*_{}|#@&+]')   # digits/symbols a TTS may misread


def words(s):
    return max(1, len(re.findall(r"[\w'-]+", s)))


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=nw=1:nk=1', str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def find_font(size):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
              '/System/Library/Fonts/Supplemental/Arial.ttf', 'C:/Windows/Fonts/arial.ttf',
              '/usr/share/fonts/TTF/DejaVuSans.ttf']:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def read_timestamps(path):
    """Audacity labels / SRT / VTT / JSON -> [(start, end, text)]."""
    raw = path.read_text(encoding='utf-8-sig')
    if path.suffix.lower() == '.json':
        d = json.loads(raw)
        d = d.get('segments', d.get('sentences', d)) if isinstance(d, dict) else d
        return [(float(e['start']), float(e['end']), e.get('text', '')) for e in d]
    def sec(t):
        h, m, s = (['0'] + t.replace(',', '.').split(':'))[-3:]
        return int(h) * 3600 + int(m) * 60 + float(s)
    if '-->' in raw:                                           # SRT / VTT
        out = []
        for block in re.split(r'\n\s*\n', raw.strip()):
            ls = [l for l in block.splitlines() if l.strip()]
            for k, l in enumerate(ls):
                if '-->' in l:
                    a, b = [x.strip().split()[0] for x in l.split('-->')]
                    out.append((sec(a), sec(b), ' '.join(ls[k + 1:])))
                    break
        return out
    out = []                                                   # Audacity: start<TAB>end<TAB>text
    for l in raw.splitlines():
        p = l.split('\t')
        if len(p) >= 2 and not l.startswith('\\'):
            out.append((float(p[0]), float(p[1]), p[2] if len(p) > 2 else ''))
    return out


def match_lines(plan_lines, labels):
    """Match plan lines to timestamp entries in order. Returns entry index per line."""
    idx, j, report = [], 0, []
    for k, text in enumerate(plan_lines):
        best, best_r = None, 0.0
        for c in range(j, min(len(labels), j + 20)):
            r = difflib.SequenceMatcher(None, norm(text), norm(labels[c][2])).ratio()
            if r > best_r: best, best_r = c, r
        if best is None or best_r < 0.6:
            sys.exit(f'line {k + 1} not found in timestamps near entry {j + 1}: "{text[:70]}"')
        if best_r < 0.9: report.append(f'loose match ({best_r:.2f}): "{text[:50]}" ~ "{labels[best][2][:50]}"')
        report += [f'extra entry absorbed: "{labels[c][2][:60]}"' for c in range(j, best)]
        idx.append(best); j = best + 1
    report += [f'extra entry absorbed: "{labels[c][2][:60]}"' for c in range(j, len(labels))]
    return idx, report


def to_abs(cam, panel, presets):
    """Panel-relative camera (list or preset name) -> absolute [cx, cy, zoom] on the image."""
    if isinstance(cam, str):
        if cam not in presets:
            sys.exit(f'unknown camera preset: {cam}')
        cam = presets[cam]
    l, t, w, h = panel
    cx, cy, z = (float(v) for v in cam)
    z = max(1.0, z / max(w, h))
    hw = 0.5 / z                                       # keep the view inside the panel
    cx = l + w / 2 if 2 * hw >= w else min(max(l + cx * w, l + hw), l + w - hw)
    cy = t + h / 2 if 2 * hw >= h else min(max(t + cy * h, t + hw), t + h - hw)
    return [cx, cy, z]


def fit_panel(size, panel):
    """Panel on the original image -> panel on its 16:9 letterboxed canvas (see load_16x9)."""
    w0, h0 = size
    if abs(w0 / h0 - 16 / 9) <= 0.01:
        return list(panel)
    W = max(w0, round(h0 * 16 / 9)); H = round(W * 9 / 16)
    ox, oy, sx, sy = (W - w0) // 2 / W, (H - h0) // 2 / H, w0 / W, h0 / H
    l, t, w, h = panel
    return [ox + l * sx, oy + t * sy, w * sx, h * sy]


def lint(plan, base):
    """Problems in plan.json that would waste a narration or a render."""
    out, cast = [], plan.get('cast', {})
    for si, sc in enumerate(plan['scenes']):
        tag = f"S{si + 1}"
        if not (base / sc.get('image', '')).is_file():
            out.append(f"{tag}: image not found: {sc.get('image')}")
        p = sc.get('panel', [0, 0, 1, 1])
        if len(p) != 4 or min(p) < 0 or p[0] + p[2] > 1.001 or p[1] + p[3] > 1.001:
            out.append(f'{tag}: panel {p} is not inside the image')
        named = {**plan.get('marks', {}), **sc.get('marks', {})}
        for name, m in named.items():
            vals = m.get('box') or m.get('underline') or m.get('ring')
            if not vals or any(not 0 <= v <= 1 for v in vals[:4]):
                out.append(f'{tag}: mark "{name}" needs box/underline/ring with values in 0..1')
        prev = ''
        for li, ln in enumerate(sc.get('lines', [])):
            t, where = ln.get('text', ''), f'{tag}.{li + 1}'
            if not t.strip(): out.append(f'{where}: empty text')
            if SPOKEN_BAD.search(t): out.append(f'{where}: digits or symbols in spoken text: "{t[:50]}"')
            for m in (ln.get('mark') or []) if isinstance(ln.get('mark'), list) else [ln.get('mark')]:
                if isinstance(m, str) and m not in named: out.append(f'{where}: unknown mark "{m}"')
            spk = ln.get('speaker', sc.get('speaker'))
            if spk is not None and spk not in cast: out.append(f'{where}: speaker "{spk}" not in "cast"')
            if t.rstrip().endswith('?') and (QUIZ.search(t) or QUIZ.search(prev)) \
                    and ln.get('pause_after', 0) < 4:
                out.append(f'{where}: quiz question needs "pause_after": 4 or more')
            prev = t
    return out


def scene_audio(sc, idx, base, audio_dir):
    if sc.get('audio'):
        return base / sc['audio']
    if audio_dir:
        for ext in AUDIO_EXT:
            p = audio_dir / f'scene{idx + 1:02d}{ext}'
            if p.exists():
                return p
    return None


def timeline(plan, base, use_audio, audio_dir):
    """-> rows (one per line, absolute start/end), audio [(path|None, seconds, offset)], total, notes."""
    presets = {'wide': [0.5, 0.5, 1.0], **plan.get('presets', {})}
    flat = [(si, li, sc, ln) for si, sc in enumerate(plan['scenes']) for li, ln in enumerate(sc['lines'])]
    times, audio, notes = None, [], []
    if use_audio and plan.get('audio') and not plan.get('timestamps'):
        sys.exit('plan has "audio" but no "timestamps"; add the timestamp file or use per-scene audio')
    if use_audio and plan.get('audio') and plan.get('timestamps'):      # one file + timestamps
        a = base / plan['audio']; off = float(plan.get('audio_offset', 0))
        if not a.exists(): sys.exit(f'missing audio: {a}')
        labels = read_timestamps(base / plan['timestamps'])
        idx, notes = match_lines([ln['text'] for *_, ln in flat], labels)
        total = probe(a) - off
        # a line starts with the entry after the previous line (spoken titles fold in); a new
        # scene starts inside the pause before it, at most SCENE_LEAD s early, so the move
        # happens in silence but a long pause (quiz think time) keeps the old board up
        starts = [0.0 if k == 0 else
                  max(labels[idx[k - 1]][1], labels[idx[k - 1] + 1][0] - SCENE_LEAD) if flat[k][1] == 0
                  else labels[idx[k - 1] + 1][0] for k in range(len(idx))]
        times = [(starts[k], starts[k + 1] if k + 1 < len(starts) else total) for k in range(len(starts))]
        speech = [labels[i][0] for i in idx]           # when this sentence itself begins
        audio = [(a, total, off)]
    else:                                                               # per-scene or estimated
        times, t = [], 0.0
        for si, sc in enumerate(plan['scenes']):
            lines = sc['lines']
            est = [ln.get('seconds', LINE_PAD + words(ln['text']) * 60 / WPM + ln.get('pause_after', 0))
                   for ln in lines]
            a = scene_audio(sc, si, base, audio_dir) if use_audio else None
            if a is not None and not a.exists():
                sys.exit(f'missing audio: {a}')
            if a is not None:
                dur = probe(a)
                fixed = sum(ln['seconds'] for ln in lines if 'seconds' in ln)
                free = sum(words(ln['text']) for ln in lines if 'seconds' not in ln)
                rest = max(0.0, dur - fixed)
                per = ([ln['seconds'] if 'seconds' in ln else rest * words(ln['text']) / free
                        for ln in lines] if free else [d * dur / sum(est) for d in est])
            else:
                per, dur = est, sum(est)
            audio.append((a, dur, 0.0))
            for d in per:
                times.append((t, t + d)); t += d
        total = t
        speech = [s for s, _ in times]
    rows, sizes = [], {}
    for (si, li, sc, ln), (s, e), sp in zip(flat, times, speech):
        if sc['image'] not in sizes:
            with Image.open(base / sc['image']) as im: sizes[sc['image']] = im.size
        panel = fit_panel(sizes[sc['image']], sc.get('panel', [0, 0, 1, 1]))
        named = {**presets, **sc.get('presets', {})}   # scene presets override plan presets
        wide = to_abs('wide', panel, named)
        cam = ln.get('camera', 'hold')                 # no camera = stay where we are
        if cam == 'hold':
            cam_abs = rows[-1]['cam'] if li else wide
        else:
            cam_abs = to_abs(cam, panel, named)
        marks = {**plan.get('marks', {}), **sc.get('marks', {})}
        rows.append(dict(scene=si, line=li, image=sc['image'], text=ln['text'], start=s, end=e,
                         speech=sp, cam=cam_abs, wide=wide,
                         marks=resolve_marks(ln.get('mark'), panel, marks)))
    return rows, audio, total, notes


def resolve_marks(spec, panel, named):
    """Mark name(s) or inline shapes (panel-relative) -> absolute shapes on the image."""
    if not spec:
        return []
    out = []
    for m in (spec if isinstance(spec, list) else [spec]):
        if isinstance(m, str):
            if m not in named:
                sys.exit(f'unknown mark: {m}')
            m = named[m]
        l, t, w, h = panel
        X = lambda v: l + v * w
        Y = lambda v: t + v * h
        if 'box' in m:
            x0, y0, x1, y1 = m['box']; out.append(('box', X(x0), Y(y0), X(x1), Y(y1)))
        elif 'underline' in m:
            x0, y, x1 = m['underline']; out.append(('underline', X(x0), Y(y), X(x1)))
        elif 'ring' in m:
            x, y = m['ring'][:2]; out.append(('ring', X(x), Y(y), m.get('r', 0.035) * h))
        else:
            sys.exit(f'mark needs box, underline or ring: {m}')
    return out


def motion_report(rows):
    """Count camera moves and flag restless patterns."""
    moves, flips, quick = 0, 0, []
    for i in range(1, len(rows)):
        a, b = rows[i - 1], rows[i]
        if a['scene'] != b['scene'] or a['cam'] == b['cam']:
            continue
        moves += 1
        if i >= 2 and rows[i - 2]['scene'] == b['scene'] and rows[i - 2]['cam'] == b['cam']:
            flips += 1
        if b['end'] - b['start'] < 2.5:
            quick.append(f"S{b['scene']+1}.{b['line']+1}")
    mins = max(1e-9, (rows[-1]['end'] - rows[0]['start']) / 60)
    msg = f'camera: {moves} moves inside scenes ({moves / mins:.1f}/min), {flips} back-and-forth (A-B-A)'
    if quick: msg += f', moves on short lines (<2.5 s): {", ".join(quick[:12])}'
    return msg


def load_16x9(path):
    im = Image.open(path).convert('RGB')
    target = 16 / 9
    if abs(im.width / im.height - target) > 0.01:      # letterbox, never stretch (fit_panel matches)
        bg = im.getpixel((2, 2))
        W = max(im.width, round(im.height * target)); H = round(W * 9 / 16)
        canvas = Image.new('RGB', (W, H), bg)
        canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
        im = canvas
    return im


def smooth(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


def glide(a, b, v):
    """Pan linearly, zoom in log space so zooming feels even."""
    return [a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v,
            math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * v)]


def camera_at(rows, i, t):
    """Move once at the start of a line, then hold still on the subject."""
    r = rows[i]
    p = rows[i - 1] if i else None
    old = p['cam'] if p and p['image'] == r['image'] else r['wide']
    new = r['cam']
    if old == new:
        return new
    zmax = max(old[2], new[2])
    dist = math.hypot(old[0] - new[0], old[1] - new[1]) * zmax       # in screen widths
    span = r['end'] - r['start']
    T = max(0.4, min(0.7 * span, 1.2 + 0.4 * min(dist, 2.5)))        # ~1.2-2.2 s
    if p and p['scene'] != r['scene']:                               # panel move ends before speech
        T = max(0.8, min(T, r['speech'] - r['start']))
    u = smooth((t - r['start']) / T)
    if p and p['scene'] != r['scene'] and dist > 1.2:                # panel to panel: lift, glide, settle
        mid = [(old[0] + new[0]) / 2, (old[1] + new[1]) / 2, max(1.0, min(old[2], new[2]) * 0.8)]
        return glide(old, mid, u * 2) if u < 0.5 else glide(mid, new, u * 2 - 1)
    return glide(old, new, u)


def view_rect(im, cam):
    """Pixel rectangle of the image that the camera shows: (x0, y0, width, height)."""
    cx, cy, z = cam
    cw, ch = im.width / z, im.height / z
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    return x0, y0, cw, ch


def crop(im, cam, w, h, resample=Image.BILINEAR):
    x0, y0, cw, ch = view_rect(im, cam)
    return im.resize((w, h), resample, box=(x0, y0, x0 + cw, y0 + ch))


def mark_layer(shapes, im, cam, W, H, color):
    """Draw marks once (anti-aliased) -> (RGBA patch, (x, y)) to paste onto the frame."""
    x0, y0, cw, ch = view_rect(im, cam)
    sx = lambda X: (X * im.width - x0) / cw * W
    sy = lambda Y: (Y * im.height - y0) / ch * H
    lw = max(2.0, H / 300)
    items, xs, ys = [], [], []
    for s in shapes:
        if s[0] == 'box':
            a, b, c, d = sx(s[1]), sy(s[2]), sx(s[3]), sy(s[4]); items.append(('box', a, b, c, d))
            xs += [a, c]; ys += [b, d]
        elif s[0] == 'underline':
            a, b, c = sx(s[1]), sy(s[2]), sx(s[3]); items.append(('line', a, b, c))
            xs += [a, c]; ys += [b, b]
        else:
            x, y, r = sx(s[1]), sy(s[2]), s[3] * im.height / ch * H; items.append(('ring', x, y, r))
            xs += [x - r, x + r]; ys += [y - r, y + r]
    if not items:
        return None
    pad = int(lw * 4)
    bx0, by0 = int(max(0, min(xs) - pad)), int(max(0, min(ys) - pad))
    bx1, by1 = int(min(W, max(xs) + pad)), int(min(H, max(ys) + pad))
    if bx1 <= bx0 or by1 <= by0:
        return None
    SS = 3                                              # supersample for smooth edges
    layer = Image.new('RGBA', ((bx1 - bx0) * SS, (by1 - by0) * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = Image.new('RGB', (1, 1), color).getpixel((0, 0))
    P = lambda v, o: (v - o) * SS
    for it in items:
        if it[0] == 'box':
            box = [P(it[1], bx0), P(it[2], by0), P(it[3], bx0), P(it[4], by0)]
            rad = int(min(box[2] - box[0], box[3] - box[1]) * 0.18)
            d.rounded_rectangle(box, radius=rad, fill=rgb + (34,))
            d.rounded_rectangle(box, radius=rad, outline=rgb + (235,), width=int(lw * SS))
        elif it[0] == 'line':
            w = int(lw * 1.6 * SS); y = P(it[2], by0)
            d.line([P(it[1], bx0), y, P(it[3], bx0), y], fill=rgb + (240,), width=w)
            for xe in (P(it[1], bx0), P(it[3], bx0)):
                d.ellipse([xe - w / 2, y - w / 2, xe + w / 2, y + w / 2], fill=rgb + (240,))
        else:
            x, y, r = P(it[1], bx0), P(it[2], by0), it[3] * SS
            d.ellipse([x - r * 1.25, y - r * 1.25, x + r * 1.25, y + r * 1.25], outline=rgb + (70,), width=int(lw * 2 * SS))
            d.ellipse([x - r, y - r, x + r, y + r], fill=rgb + (30,), outline=rgb + (240,), width=int(lw * SS))
    return layer.resize((bx1 - bx0, by1 - by0), Image.LANCZOS), (bx0, by0)


MARK_IN, MARK_OUT = 0.25, 0.2                           # fade seconds


def mark_alpha(rows, i, t):
    """Fade in when the sentence starts speaking, out at its end; no flicker if the mark repeats."""
    r = rows[i]
    if not r['marks'] or t < r['speech']:
        return 0.0
    same_prev = i and rows[i - 1]['marks'] == r['marks'] and rows[i - 1]['scene'] == r['scene']
    same_next = i + 1 < len(rows) and rows[i + 1]['marks'] == r['marks'] and rows[i + 1]['scene'] == r['scene']
    a_in = 1.0 if same_prev else min(1.0, (t - r['speech']) / MARK_IN)
    a_out = 1.0 if same_next else min(1.0, max(0.0, (r['end'] - t) / MARK_OUT))
    return smooth(min(a_in, a_out))


def apply_marks(frame, rows, i, t, img, cam, color, cache):
    a = mark_alpha(rows, i, t)
    if a <= 0:
        return frame
    key = (i, tuple(round(v, 5) for v in cam))
    if key not in cache:
        if len(cache) > 64: cache.clear()
        cache[key] = mark_layer(rows[i]['marks'], img, cam, frame.width, frame.height, color)
    got = cache[key]
    if not got:
        return frame
    patch, pos = got
    if a < 0.999:
        patch = patch.copy(); patch.putalpha(patch.getchannel('A').point(lambda v: int(v * a)))
    frame.paste(patch, pos, patch)
    return frame


def caption(text, w, font):
    pad = int(font.size * 0.6)
    d = ImageDraw.Draw(Image.new('RGB', (2, 2)))
    lines, cur = [], ''
    for word in text.split():
        trial = (cur + ' ' + word).strip()
        if d.textlength(trial, font=font) <= w - 8 * pad: cur = trial
        else: lines.append(cur); cur = word
    lines.append(cur)
    lh = int(font.size * 1.3); bh = lh * len(lines) + 2 * pad
    band = Image.new('RGBA', (w, bh), (0, 0, 0, 0)); dd = ImageDraw.Draw(band)
    dd.rounded_rectangle([3 * pad, 0, w - 3 * pad, bh], radius=pad, fill=(8, 12, 16, 190))
    for j, ln in enumerate(lines):
        dd.text((w / 2, pad + j * lh), ln, font=font, fill=(250, 248, 238, 255), anchor='mt')
    return band


def srt(rows, path, t0=0.0, t1=1e9):
    def ts(s):
        ms = round(s * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    keep = [r for r in rows if r['end'] > t0 and r['start'] < t1]   # caption from its own speech
    path.write_text('\n'.join(f"{k}\n{ts(max(r['speech'], t0) - t0)} --> {ts(min(r['end'], t1) - t0)}\n{r['text']}\n"
                              for k, r in enumerate(keep, 1)), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--audio-dir', type=Path, help='folder with scene01.wav/.mp3/... (scene number order)')
    ap.add_argument('--preview', action='store_true', help='ignore audio, silent estimated timing')
    ap.add_argument('--clip', nargs=2, type=float, metavar=('START', 'END'), help='render only this time range')
    ap.add_argument('--contact-sheet', action='store_true', help="PNG of every line's camera target")
    ap.add_argument('--export-tts', type=Path, metavar='DIR', help='write sceneNN.txt files for TTS')
    ap.add_argument('--no-captions', action='store_true')
    ap.add_argument('--check', action='store_true', help='lint plan.json and exit (non-zero on problems)')
    a = ap.parse_args()
    base = a.plan.resolve().parent
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    problems = lint(plan, base)
    if a.check:
        for p in problems: print('PROBLEM:', p)
        n = sum(len(sc['lines']) for sc in plan['scenes'])
        print(f'plan check: {len(plan["scenes"])} scenes, {n} lines, {len(problems)} problems')
        sys.exit(1 if problems else 0)
    for p in problems: print('  warning:', p)

    if a.export_tts:
        a.export_tts.mkdir(parents=True, exist_ok=True)
        texts = ['\n'.join(ln['text'] for ln in sc['lines']) for sc in plan['scenes']]
        for k, txt in enumerate(texts, 1):
            (a.export_tts / f'scene{k:02d}.txt').write_text(txt + '\n', encoding='utf-8')
        (a.export_tts / 'narration_all.txt').write_text('\n\n'.join(texts) + '\n', encoding='utf-8')
        print(f'wrote {len(texts)} scene files to {a.export_tts}'); return

    W = int(plan.get('width', 1920)); W -= W % 2; H = W * 9 // 16; H -= H % 2
    fps = int(plan.get('fps', 24))
    out = a.out or base / ('preview.mp4' if a.preview else 'final.mp4')
    audio_dir = (a.audio_dir.resolve() if a.audio_dir else None)
    rows, audio, total, notes = timeline(plan, base, not a.preview, audio_dir)
    for n in notes: print('  note:', n)
    if any(r['cam'] != r['wide'] for r in rows): print(motion_report(rows))
    if not a.preview and not a.contact_sheet:          # a final render must have narration
        missing = [f'S{k + 1}' for k, (p, *_) in enumerate(audio) if p is None]
        if missing:
            sys.exit(f'no narration for {", ".join(missing) if len(missing) < len(audio) else "the video"}; '
                     'give "audio" + "timestamps", per-scene audio, or use --preview for a silent draft')
    cache = {}
    def img(name):
        if name not in cache:
            cache[name] = load_16x9(base / name)
        return cache[name]
    font = find_font(max(18, H // 26))
    mark_color = plan.get('mark_color', '#FFD36F')

    if a.contact_sheet:
        tw, th = 480, 270; cols = 4; n = len(rows)
        sheet = Image.new('RGB', (cols * tw, math.ceil(n / cols) * (th + 44)), (20, 20, 20))
        d = ImageDraw.Draw(sheet); f = find_font(15)
        for k, r in enumerate(rows):
            x, y = (k % cols) * tw, (k // cols) * (th + 44)
            thumb = crop(img(r['image']), r['cam'], tw, th)
            got = mark_layer(r['marks'], img(r['image']), r['cam'], tw, th, mark_color) if r['marks'] else None
            if got: thumb.paste(got[0], got[1], got[0])
            sheet.paste(thumb, (x, y))
            d.text((x + 6, y + th + 4), f"S{r['scene']+1}.{r['line']+1}  {r['text'][:52]}", font=f, fill='white')
        p = out.with_name(out.stem + '_contact.png'); sheet.save(p); print('wrote', p); return

    t0, t1 = (max(0.0, a.clip[0]), min(total, a.clip[1])) if a.clip else (0.0, total)
    has_audio = any(p for p, *_ in audio)
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(fps), '-i', 'pipe:0']
    parts, flt = [], []
    for k, (p, d, off) in enumerate(audio if has_audio else [(None, total, 0.0)]):
        if p: cmd += (['-ss', f'{off:.4f}'] if off else []) + ['-i', str(p)]
        else: cmd += ['-f', 'lavfi', '-t', f'{d:.3f}', '-i', 'anullsrc=r=48000:cl=stereo']
        flt.append(f'[{k+1}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,'
                   f'apad,atrim=0:{d:.4f},asetpts=PTS-STARTPTS[a{k}]')
        parts.append(f'[a{k}]')
    flt.append(''.join(parts) + f'concat=n={len(parts)}:v=0:a=1,'
               f'atrim={t0:.4f}:{t1:.4f},asetpts=PTS-STARTPTS[aout]')
    chapters = []
    titles = [sc.get('title') for sc in plan['scenes']]
    if any(titles) and not a.clip:                     # chapter markers from scene titles
        starts = {}
        for r in rows: starts.setdefault(r['scene'], r['start'])
        meta = [';FFMETADATA1', f"title={plan.get('title', '')}"]
        for si in range(len(titles)):
            s = starts[si]; e = starts.get(si + 1, total)
            meta += ['[CHAPTER]', 'TIMEBASE=1/1000', f'START={round(s * 1000)}', f'END={round(e * 1000)}',
                     f"title={si + 1:02d}. {titles[si] or 'Scene ' + str(si + 1)}"]
        mf = out.with_name(out.stem + '_chapters.txt'); mf.write_text('\n'.join(meta) + '\n', encoding='utf-8')
        cmd += ['-f', 'ffmetadata', '-i', str(mf)]     # inputs must come before output options
        chapters = ['-map_chapters', str(len(parts) + 1), '-map_metadata', str(len(parts) + 1)]
    srt(rows, out.with_suffix('.srt'), t0, t1)          # also muxed as a switchable subtitle track
    cmd += ['-i', str(out.with_suffix('.srt'))]
    subs = str(len(parts) + 1 + (1 if chapters else 0))
    cmd += ['-filter_complex', ';'.join(flt), '-map', '0:v', '-map', '[aout]', '-map', f'{subs}:s', *chapters]
    cmd += ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '128k', '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng',
            '-t', f'{t1 - t0:.3f}', '-movflags', '+faststart', str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    show_caps = plan.get('captions', False) and not a.no_captions
    caps = {k: caption(r['text'], W, font) for k, r in enumerate(rows)} if show_caps else {}
    first = {}                                   # first row index of each scene
    for k, r in enumerate(rows):
        first.setdefault(r['scene'], k)
    i, held, mcache = 0, (None, None), {}
    for f in range(math.ceil((t1 - t0) * fps)):
        t = t0 + f / fps
        while i < len(rows) - 1 and t >= rows[i]['end']: i += 1
        r = rows[i]
        cam = camera_at(rows, i, t)
        key = (r['image'], tuple(cam))
        if held[0] != key:                         # camera holds most of the time: reuse the crop
            sharp = Image.LANCZOS if cam == r['cam'] else Image.BILINEAR   # settled view: best quality
            held = (key, crop(img(r['image']), cam, W, H, sharp))
        frame = held[1].copy()
        k0 = first[r['scene']]
        if k0 and rows[k0 - 1]['image'] != r['image'] and t - rows[k0]['start'] < FADE:
            prev = rows[k0 - 1]                    # new image: cross-fade from the last view
            old = crop(img(prev['image']), prev['cam'], W, H)
            frame = Image.blend(old, frame, smooth((t - rows[k0]['start']) / FADE))
        if r['marks']:
            frame = apply_marks(frame, rows, i, t, img(r['image']), cam, mark_color, mcache)
        if caps and t >= r['speech']:
            c = caps[i]; frame.paste(c, (0, H - c.height - H // 30), c)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait(): sys.exit('ffmpeg failed')
    (out.with_name(out.stem + '_timing.json')).write_text(json.dumps(rows, indent=1))
    mode = ('timestamps' if plan.get('timestamps') and has_audio and len(audio) == 1 and plan.get('audio')
            else 'per-scene audio' if has_audio else 'silent/estimated')
    print(f'wrote {out}  ({t1 - t0:.1f}s of {total:.1f}s, {len(plan["scenes"])} scenes, {len(rows)} lines, '
          f'{len(cache)} images, {mode})')


if __name__ == '__main__':
    main()
```

## narrate.py

```python
#!/usr/bin/env python3
"""Draft narration from plan.json with a local TTS -> narration.wav + Audacity labels.

Works like the Read Aloud app: each sentence is synthesized separately, joined with
silence, and the label file records each sentence's exact start/end (computed from
sample counts, so it is exact by construction). The renderer reads both directly.

  python narrate.py plan.json --model-dir voices/kokoro-gpu-v1-0 --voice af_heart
  python narrate.py plan.json --model-dir models/kitten-micro-0.8 --voice 0
  python narrate.py plan.json --model-dir models/vits-piper-en_US-amy-medium
  python narrate.py --list-voices --model-dir voices/kokoro-gpu-v1-0
  python narrate.py plan.json --model-dir voices/kokoro-gpu-v1-0 --sample 8   # measure the pace

Pace: every run prints words per minute (while speaking, and with pauses) and, for the
whole plan, the projected length. --sample N voices only the first N lines (into the
cache, so the full run reuses them), prints the pace and the projected length of the
whole script, and writes no audio files: use it to size the script before writing it all.

Engines (picked from what is in --model-dir):
  * Kokoro v1.0 (onnx-community layout: onnx/model.onnx, voices/*.bin, tokenizer.json),
    the Read Aloud "Kokoro" voice: runs on CPU with onnxruntime + espeak phonemes.
    pip install onnxruntime espeakng-loader phonemizer-fork numpy
  * sherpa-onnx packages (model.onnx/.int8.onnx + tokens.txt [+ voices.bin] + espeak-ng-data):
    Kitten (needs sherpa-onnx 1.13.x), Kokoro (sherpa export), Piper/VITS (Amy, Lessac).
    pip install sherpa-onnx==1.13.4 numpy

Pauses: --gap after each sentence (Read Aloud's sentence pause), scene changes get
gap + 0.4 s (Read Aloud's paragraph pause); a line can set "pause_after": seconds,
e.g. 4 after a quiz question. --speed 1.0 = normal.

Several voices (dialogue, characters): give plan.json a "cast" and put "speaker" on a
line (that line only) or a scene (its default). Untagged lines use "narrator" from the
cast, or --voice. A cast entry is one voice, or one per engine:
  "cast": {"narrator": "af_heart", "student": {"kokoro": "am_adam", "kitten": 3}}
Unknown speakers stop before any audio is made. Each speaker is level-matched to the
others (one gain per speaker, so natural emphasis inside a voice is kept); --no-level skips it.
Kokoro British voices (bf_*, bm_*) use British pronunciation.

Cache: every sentence is kept in --cache (default tts_cache/ next to plan.json), keyed by
code version, engine, model, voice, speed and text, so after an edit only changed lines are
re-voiced (like Read Aloud's Render / Update). Each run lists the lines it re-voiced.
"""
import argparse, hashlib, json, re, sys, time, wave
from pathlib import Path
import numpy as np

CACHE_VERSION = 3          # bump when phoneme rules or synthesis change, so old audio is not reused
WARN = []


class KokoroV1:
    """Kokoro-82M v1.0 ONNX (same model/voices as Read Aloud's GPU voice), on CPU."""
    def __init__(self, d, threads):
        import onnxruntime as ort, espeakng_loader, os
        from phonemizer.backend.espeak.wrapper import EspeakWrapper
        from phonemizer.backend import EspeakBackend
        EspeakWrapper.set_library(espeakng_loader.get_library_path())
        os.environ['ESPEAK_DATA_PATH'] = espeakng_loader.get_data_path()
        EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
        so = ort.SessionOptions(); so.intra_op_num_threads = threads
        self.sess = ort.InferenceSession(str(d / 'onnx' / 'model.onnx'), so, providers=['CPUExecutionProvider'])
        self.vocab = json.load(open(d / 'tokenizer.json'))['model']['vocab']
        self.voices_dir = d / 'voices'
        self.speakers = [s['name'] for s in json.load(open(d / 'voice.json')).get('speakers', [])] \
            if (d / 'voice.json').exists() else []
        self.names = sorted(p.stem for p in self.voices_dir.glob('*.bin'))
        self.backend = lambda lang: EspeakBackend(lang, preserve_punctuation=True, with_stress=True,
                                                  language_switch='remove-flags')
        self.espeak = {}
        self.sample_rate = 24000
        self.kind = 'kokoro'
        self.default = 'af_heart' if 'af_heart' in self.names else self.names[0]
        self.model_file = d / 'onnx' / 'model.onnx'

    def resolve(self, voice):
        """Voice name, or Read Aloud speaker number (needs its voice.json) -> file name, else None."""
        v = str(voice)
        if v.isdigit() and self.speakers and int(v) < len(self.speakers):
            first = self.speakers[int(v)].split(' (')[0].lower()
            return next((n for n in self.names if n.split('_', 1)[-1] == first), None)
        return v if v in self.names else None

    def voice_file(self, voice):
        return np.fromfile(self.voices_dir / f'{voice}.bin', dtype=np.float32).reshape(-1, 256)

    def phonemes(self, text, voice=''):
        text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
        lang = 'en-gb' if voice[:1] == 'b' else 'en-us'          # bf_/bm_ voices are British
        if lang not in self.espeak: self.espeak[lang] = self.backend(lang)
        ps = self.espeak[lang].phonemize([text], strip=True)[0]
        ps = (ps.replace('ʲ', 'j').replace('r', 'ɹ').replace('x', 'k').replace('ɬ', 'l'))
        ps = re.sub(r'(?<=[a-zɹː])(?=hˈʌndɹɪd)', ' ', ps)
        ps = re.sub(r' z(?=[;:,.!?¡¿—…"«»“” ]|$)', 'z', ps)
        ps = re.sub(r'(?<=nˈaɪn)ti(?!ː)', 'di', ps)
        return ps.strip()

    def say(self, text, voice, speed):
        ps = self.phonemes(text, voice)
        ids = [self.vocab[c] for c in ps if c in self.vocab]
        dropped = len(ps) - len(ids)
        if dropped > max(2, len(ps) // 20):
            WARN.append(f'{dropped} sounds dropped (unknown to Kokoro) in "{text[:50]}"; respell it')
        if len(ids) > 510:
            WARN.append(f'too long for Kokoro, end cut off: "{text[:50]}"; split the sentence')
            ids = ids[:510]
        style = self.voice_file(voice)[min(len(ids), 509)][None, :]
        wav = self.sess.run(None, {'input_ids': np.array([[0, *ids, 0]], dtype=np.int64),
                                   'style': style.astype(np.float32),
                                   'speed': np.array([speed], dtype=np.float32)})[0]
        return wav.reshape(-1).astype(np.float32)


class Sherpa:
    """sherpa-onnx package: Kitten, Kokoro (sherpa export) or Piper/VITS."""
    def __init__(self, d, threads):
        import sherpa_onnx as s
        model = next(p for p in (d / 'model.onnx', d / 'model.int8.onnx', *sorted(d.glob('*.onnx'))) if p.exists())
        mc = s.OfflineTtsModelConfig(num_threads=threads, provider='cpu')
        data = str(d / 'espeak-ng-data') if (d / 'espeak-ng-data').exists() else ''
        if (d / 'voices.bin').exists():
            common = dict(model=str(model), voices=str(d / 'voices.bin'), tokens=str(d / 'tokens.txt'), data_dir=data)
            if 'kokoro' in d.name.lower():
                mc.kokoro = s.OfflineTtsKokoroModelConfig(**common); self.kind = 'kokoro'
            else:                                   # Kitten; sherpa-onnx 2.x wants a lexicon file instead
                mc.kitten = s.OfflineTtsKittenModelConfig(**common); self.kind = 'kitten'
        else:
            mc.vits = s.OfflineTtsVitsModelConfig(model=str(model), tokens=str(d / 'tokens.txt'), data_dir=data)
            self.kind = 'vits'
        self.tts = s.OfflineTts(s.OfflineTtsConfig(model=mc, max_num_sentences=1))
        self.sample_rate = self.tts.sample_rate
        self.names = [str(i) for i in range(self.tts.num_speakers)]
        self.default, self.model_file = '0', model

    def resolve(self, voice):
        """Speaker number -> itself if this model has it, else None (sherpa voices are numbered)."""
        v = str(voice)
        return v if v in self.names else None

    def say(self, text, voice, speed):
        return np.asarray(self.tts.generate(text, sid=int(voice or 0), speed=speed).samples, dtype=np.float32)


def count_words(text):
    return len(re.findall(r"[\w'-]+", text))


def pace(words, speech_s, total_s):
    """Words per minute while speaking and with pauses (the number to size a script by)."""
    return (f'{words} words: {words / max(speech_s, 1e-9) * 60:.0f} wpm while speaking, '
            f'{words / max(total_s, 1e-9) * 60:.0f} wpm with pauses')


def load_engine(d, threads):
    d = Path(d)
    return KokoroV1(d, threads) if (d / 'onnx' / 'model.onnx').exists() else Sherpa(d, threads)


def resolve_voices(plan, eng, default):
    """Voice for every line from the cast (line "speaker" > scene "speaker" > narrator)."""
    cast = plan.get('cast', {})
    def pick(role):
        v = cast[role]
        if isinstance(v, dict):
            if eng.kind not in v:
                sys.exit(f'cast "{role}" has no voice for the {eng.kind} engine')
            v = v[eng.kind]
        return str(v)
    base = default if default is not None else (pick('narrator') if 'narrator' in cast else eng.default)
    out, bad = [], []
    for si, sc in enumerate(plan['scenes']):
        for li, ln in enumerate(sc['lines']):
            role = ln.get('speaker', sc.get('speaker'))
            if role is None: out.append(('narrator', base)); continue
            if role not in cast: bad.append(f'S{si + 1}.{li + 1} speaker "{role}"'); continue
            out.append((role, pick(role)))
    names = {v: eng.resolve(v) for _, v in out}
    bad += [f'voice "{v}" ({r})' for r, v in set(out) if names[v] is None]
    if bad:
        sys.exit('not in the cast or not a voice of this model: ' + '; '.join(sorted(set(bad)))
                 + f'\n  voices here: {", ".join(eng.names[:12])}{" ..." if len(eng.names) > 12 else ""}')
    return [(r, names[v]) for r, v in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path, nargs='?')
    ap.add_argument('--model-dir', required=True)
    ap.add_argument('--voice', help='narrator voice name (af_heart) or speaker number; default: cast "narrator" or 0')
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--gap', type=float, default=0.45, help='seconds after each sentence')
    ap.add_argument('--scene-gap', type=float, help='seconds between scenes (default gap + 0.4)')
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--out', default='narration.wav'); ap.add_argument('--labels', default='labels.txt')
    ap.add_argument('--cache', type=Path, help='sentence cache folder (default tts_cache next to plan.json)')
    ap.add_argument('--no-level', action='store_true', help='do not level-match speakers')
    ap.add_argument('--list-voices', action='store_true')
    ap.add_argument('--sample', type=int, metavar='N',
                    help='voice only the first N lines, print the pace, write no audio files')
    a = ap.parse_args()
    eng = load_engine(a.model_dir, a.threads)
    if a.list_voices:
        print(', '.join(eng.names)); return
    plan = json.loads(a.plan.read_text(encoding='utf-8'))
    base = a.plan.resolve().parent
    voices = resolve_voices(plan, eng, a.voice)
    cache = a.cache or base / 'tts_cache'; cache.mkdir(parents=True, exist_ok=True)
    mf = Path(eng.model_file)
    model_id = f'{Path(a.model_dir).resolve().name}:{mf.stat().st_size}'     # same name, other weights -> new id
    scene_gap = a.scene_gap if a.scene_gap is not None else a.gap + 0.4
    sr = eng.sample_rate
    parts, labels, n, t0, made, reused, k, spoken = [], [], 0, time.time(), 0, 0, 0, []
    revoiced, nwords, speech = [], 0, 0
    all_words = sum(count_words(ln['text']) for sc in plan['scenes'] for ln in sc['lines'])
    for si, sc in enumerate(plan['scenes']):
        if a.sample and k >= a.sample: break
        for li, ln in enumerate(sc['lines']):
            if a.sample and k >= a.sample: break
            role, voice = voices[k]; k += 1
            key = hashlib.sha1(f'{CACHE_VERSION}|{eng.kind}|{model_id}|{voice}|{a.speed}|{ln["text"]}'
                               .encode()).hexdigest()[:20]
            cf = cache / f'{key}.npy'
            if cf.exists():
                audio = np.load(cf); reused += 1
            else:
                audio = eng.say(ln['text'], voice, a.speed); made += 1
                np.save(cache / f'{key}.tmp.npy', audio); (cache / f'{key}.tmp.npy').replace(cf)
                revoiced.append(f'S{si + 1}.{li + 1}  {ln["text"][:70]}')
            if not len(audio) or np.abs(audio).max() < 1e-3:
                sys.exit(f'no speech came out for S{si + 1}.{li + 1}: "{ln["text"][:60]}"')
            nwords += count_words(ln['text']); speech += len(audio)
            labels.append((n / sr, (n + len(audio)) / sr, ln['text']))
            spoken.append((len(parts), role)); parts.append(audio); n += len(audio)
            gap = ln.get('pause_after', scene_gap if li == len(sc['lines']) - 1 else a.gap)
            parts.append(np.zeros(int(gap * sr), np.float32)); n += int(gap * sr)
    for w in dict.fromkeys(WARN): print('  warning:', w)
    if a.sample:                                   # pace check only: no audio files written
        wpm = nwords / max(n / sr, 1e-9) * 60
        print(f'sample of {k} lines, {made} voiced, {reused} from cache; {pace(nwords, speech / sr, n / sr)}')
        print(f'whole script: {all_words} words -> about {all_words / wpm:.1f} min at this pace')
        return
    roles = {r for _, r in spoken}
    if len(roles) > 1 and not a.no_level:          # one gain per speaker toward the common level
        db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
        level = {r: np.median([db(parts[i]) for i, rr in spoken if rr == r]) for r in roles}
        target = np.median(list(level.values()))
        gains = {r: 10 ** ((target - level[r]) / 20) for r in roles}
        for i, r in spoken: parts[i] = parts[i] * gains[r]
        print('level-matched: ' + ', '.join(f'{r} {20 * np.log10(g):+.1f} dB' for r, g in sorted(gains.items())))
    pcm = np.concatenate(parts)
    peak = np.abs(pcm).max()
    if peak > 0.89: pcm = pcm * (0.89 / peak)      # keep 1 dB of headroom, never clip
    with wave.open(str(base / a.out), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((pcm * 32767).astype(np.int16).tobytes())
    (base / a.labels).write_text(''.join(f'{s:.6f}\t{e:.6f}\t{t}\n' for s, e, t in labels), encoding='utf-8')
    took = time.time() - t0
    cast = sorted({f'{r}={v}' for r, v in voices})
    print(f'wrote {a.out} ({n / sr:.1f}s, {len(labels)} sentences, {sr} Hz) and {a.labels}; '
          f'{made} voiced, {reused} from cache, {took:.1f}s; voices: {", ".join(cast)}')
    print(f'pace: {pace(nwords, speech / sr, n / sr)}; length {n / sr / 60:.1f} min')
    if revoiced:
        print(f're-voiced {len(revoiced)} line(s):')
        for r in revoiced[:40]: print('  ', r)
        if len(revoiced) > 40: print(f'   ... and {len(revoiced) - 40} more')


if __name__ == '__main__':
    main()
```

## check_audio.py

```python
#!/usr/bin/env python3
"""Listen-free narration check: does the audio match plan.json, and is it clear?

  python check_audio.py plan.json --asr-dir models/sherpa-onnx-zipformer-small-en-2023-06-26

Uses the plan's "audio" + "timestamps" (Audacity labels, SRT, VTT or JSON; any audio format
ffmpeg reads; "audio_offset" honoured). Each plan line is found in the timestamps and a small
speech recognizer transcribes that stretch of audio, which is compared with the PLAN text, so
narration made from an older script is caught. Also: silence, overlaps, loudness, peak, pauses,
quiz think time and, with several speakers, each speaker's pitch and loudness.
Every PROBLEM line is a failure (exit code 1); "check" lines are for review. The recognizer is a
proxy, not a listener: it can
mishear clear speech (single-letter math names like "x" -> "ex" are fine to ignore) and miss
unnatural speech. Respell a word only when a real word is consistently misheard.
ASR model (about 100 MB): sherpa-onnx GitHub release "asr-models",
sherpa-onnx-zipformer-small-en-2023-06-26.tar.bz2.  pip install sherpa-onnx numpy; needs ffmpeg.
"""
import argparse, difflib, json, re, subprocess, sys
from pathlib import Path
import numpy as np

SR = 16000
QUIZ = re.compile(r'quiz|test yourself|question|your turn|pause|think|try it', re.I)


def read_timestamps(path):
    """Audacity labels / SRT / VTT / JSON -> [(start, end, text)] (same as render_video.py)."""
    raw = path.read_text(encoding='utf-8-sig')
    if path.suffix.lower() == '.json':
        d = json.loads(raw)
        d = d.get('segments', d.get('sentences', d)) if isinstance(d, dict) else d
        return [(float(e['start']), float(e['end']), e.get('text', '')) for e in d]
    def sec(t):
        h, m, s = (['0'] + t.replace(',', '.').split(':'))[-3:]
        return int(h) * 3600 + int(m) * 60 + float(s)
    if '-->' in raw:
        out = []
        for block in re.split(r'\n\s*\n', raw.strip()):
            ls = [l for l in block.splitlines() if l.strip()]
            for k, l in enumerate(ls):
                if '-->' in l:
                    a, b = [x.strip().split()[0] for x in l.split('-->')]
                    out.append((sec(a), sec(b), ' '.join(ls[k + 1:])))
                    break
        return out
    out = []
    for l in raw.splitlines():
        p = l.split('\t')
        if len(p) >= 2 and not l.startswith('\\'):
            out.append((float(p[0]), float(p[1]), p[2] if len(p) > 2 else ''))
    return out


def norm_text(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def pitch(seg):
    """Median voice pitch in Hz (autocorrelation on loud 40 ms frames), 0 if unvoiced."""
    f, out = int(.04 * SR), []
    lo, hi = int(SR / 400), int(SR / 70)
    for i in range(0, len(seg) - f, f):
        w = seg[i:i + f] - seg[i:i + f].mean()
        if np.sqrt((w ** 2).mean()) < .02: continue
        ac = np.correlate(w, w, 'full')[f - 1:]
        lag = lo + int(np.argmax(ac[lo:hi]))
        if ac[lag] > .3 * ac[0]: out.append(SR / lag)
    return float(np.median(out)) if out else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('plan', type=Path); ap.add_argument('--asr-dir', required=True)
    ap.add_argument('--threads', type=int, default=2)
    args = ap.parse_args()
    import sherpa_onnx
    base = args.plan.resolve().parent; plan = json.loads(args.plan.read_text(encoding='utf-8'))
    if not plan.get('audio') or not plan.get('timestamps'):
        sys.exit('plan needs "audio" and "timestamps" to check')
    d = Path(args.asr_dir); enc = sorted(d.glob('encoder*.int8.onnx')) or sorted(d.glob('encoder*.onnx'))
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(enc[0]), decoder=str(sorted(d.glob('decoder*.onnx'))[0]),
        joiner=str((sorted(d.glob('joiner*.int8.onnx')) or sorted(d.glob('joiner*.onnx')))[0]),
        tokens=str(d / 'tokens.txt'), num_threads=args.threads)
    off = float(plan.get('audio_offset', 0))
    pcm = subprocess.run(['ffmpeg', '-v', 'error', *(['-ss', f'{off}'] if off else []),
                          '-i', str(base / plan['audio']), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    labels = read_timestamps(base / plan['timestamps'])
    lines = [(ln.get('speaker', sc.get('speaker', 'narrator')), ln['text'], ln)
             for sc in plan['scenes'] for ln in sc['lines']]
    dur, problems = len(x) / SR, []
    if not labels: sys.exit('no entries in the timestamp file')
    if any(b[0] < p[1] - 1e-3 or b[0] < p[0] for p, b in zip(labels, labels[1:])):
        problems.append('timestamps overlap or go backwards')
    if labels[-1][1] > dur + .05:
        problems.append(f'last timestamp {labels[-1][1]:.2f}s is past the audio end {dur:.2f}s')

    # find every plan line in the timestamps, in order (extra entries such as spoken titles are fine)
    found, j = [], 0
    for k, (_, text, _) in enumerate(lines):
        best, br = None, 0.0
        for c in range(j, min(len(labels), j + 20)):
            r = difflib.SequenceMatcher(None, norm_text(text), norm_text(labels[c][2])).ratio()
            if r > br: best, br = c, r
        if best is None or br < 0.6:
            problems.append(f'line {k + 1} is not in the narration (out of date?): "{text[:50]}"')
            found.append(None); continue
        if br < 0.97:
            problems.append(f'line {k + 1} was narrated from different text: "{labels[best][2][:40]}" '
                            f'vs plan "{text[:40]}"; re-narrate')
        found.append(best); j = best + 1

    words = lambda s: re.sub(r'[^a-z ]+', ' ', s.lower().replace('-', ' ')).split()
    tot = err = 0; loud = []; by_role = {}; misheard = []
    for k, ((role, text, ln), c) in enumerate(zip(lines, found)):
        if c is None: continue
        s0, s1, _ = labels[c]
        seg = x[int(s0 * SR):int(s1 * SR)]
        db = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9) if len(seg) else -120
        loud.append(db)
        if db < -50: problems.append(f'line {k + 1} is silent: "{text[:50]}"'); continue
        by_role.setdefault(role, []).append((db, seg))
        st = rec.create_stream(); st.accept_waveform(SR, seg); rec.decode_stream(st)
        ref, hyp = words(text), words(st.result.text)
        e = len(ref) - sum(m.size for m in difflib.SequenceMatcher(None, ref, hyp).get_matching_blocks())
        tot += len(ref); err += e
        if ref and e / len(ref) > 0.2:
            msg = f'line {k + 1}: "{text[:55]}"  heard as  "{st.result.text.lower()[:55]}"'
            if e / len(ref) > 0.5: problems.append(f'mostly unrecognisable {msg}')
            else: misheard.append(msg)
        nxt = labels[c + 1][0] if c + 1 < len(labels) else dur
        prev = lines[k - 1][1] if k else ''
        if text.rstrip().endswith('?') and (QUIZ.search(text) or QUIZ.search(prev)):
            print(f'  quiz question at {s0:.1f}s -> {nxt - s1:.1f}s to think')
            if nxt - s1 < 4: problems.append(f'line {k + 1}: quiz think time {nxt - s1:.1f}s; needs 4 s or more')

    miss = err / max(tot, 1) * 100
    gaps = [labels[i + 1][0] - labels[i][1] for i in range(len(labels) - 1)]
    print(f'{len(found)} plan lines, {len(labels)} timestamps; recognizer missed {miss:.1f}% of words '
          '(a rough clarity signal; usually under 8% for clear speech)')
    print(f'loudness spread {np.std(loud):.2f} dB; peak {20 * np.log10(np.abs(x).max() + 1e-9):.1f} dBFS')
    if np.abs(x).max() > .999: problems.append('audio clips (peak at full scale)')
    if gaps: print(f'pauses: min {min(gaps):.2f}s, typical {np.median(gaps):.2f}s, max {max(gaps):.2f}s')
    if miss > 8: problems.append(f'recognizer missed {miss:.1f}% of words; see the check lines')
    for m in misheard: print('  check (often a recognizer quirk, fix only real mispronunciations):', m)
    if len(by_role) > 1:                               # several voices: did they really differ?
        print('voices (a role change should move pitch or loudness):')
        for role, v in by_role.items():
            ps = [p for p in (pitch(s) for _, s in v) if p]
            print(f'  {role:12s} {len(v):3d} lines, {np.mean([l for l, _ in v]):6.1f} dB, '
                  f'pitch {np.median(ps) if ps else 0:5.0f} Hz')
    for p in problems: print('PROBLEM:', p)
    print('OK: no problems' if not problems else f'{len(problems)} problems')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
```