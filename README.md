# movie-with-pictures

Make short narrated films from still pictures: motion comics, parody ads, trailers and explainers. Pictures come
from any image tool; everything else (voices, timing, camera moves, sound, lip-sync, checks) is done in code, mostly
for free.

The first project built with it, *Blackfeather Academy in a Box*, is a 2:49 parody ad: 44 voiced lines, 9 voices,
67 shots, recorded sound design, lip-sync on every on-screen speaker, rendered at 1080p. The only paid compute was
about $4 of GPU time on Hugging Face, spent on art experiments that the final cut didn't use.

## What's here

| Folder | What it is |
|---|---|
| `skills/` | Five Claude skills. Each SKILL.md holds the full method and the scripts it uses. |
| `tools/lipsync/` | Mouth-swap lip-sync for painted characters (timing from Rhubarb Lip Sync). |
| `tools/framing/` | Finds faces in every picture and re-aims camera moves so no head is cut off. |
| `tools/parallax/` | Multiplane parallax shot from background, character and foreground layers. |
| `tools/hf_jobs/` | Image generation on rented Hugging Face GPUs (FLUX.1-schnell, HiDream-O1). |
| `examples/blackfeather/` | The real project scripts from the Blackfeather ad, as used. |

### Skills

- **motion-comic-video**: a story or script with characters becomes a motion comic: a cut list in `plan.json`,
  Kokoro voices per character, word-timed cuts and effects, camera moves, captions. Contains `motion_comic.py`
  (the renderer) and its helper scripts.
- **narrated-explainer-video**: narrated slideshow / lesson videos; contains `narrate.py` (local Kokoro TTS with
  exact line timestamps) and `check_audio.py`.
- **cinematic-sound-design**: the sound bed: recorded effects anchored to words, score placed by its climax,
  ducking under speech, silence as a tool.
- **trailer-verify**: blind QA of a finished render: picture, loudness, speech clarity, flashes, captions.
  Writes a pass/warn/fail report.
- **image-request-pack**: packages requests for new images that a person makes in an outside image tool
  (start image, character references, prompts, fallbacks), so new shots match the approved art.

The scripts live inside the SKILL.md files as code blocks; extract the ones a skill names before running them.

## The pipeline, in the order that saves the most work

1. **Script to plan.** Cut the script into lines, one speaker each, with the shot under each line (`plan.json`).
2. **Voices first.** Narrate every line (`narrate.py`), tighten pauses (`voice_fx.py`), get word times
   (`word_times.py`). The real length is known before any art exists.
3. **Rough draft.** Render with placeholder cards and the real sound. Judge timing and jokes here, while changes
   are free.
4. **Art.** Make the pictures in your image tool, guided by `image-request-pack`; or on a rented GPU
   (`tools/hf_jobs`). Draw any on-screen text in code, never in the image model.
5. **Framing.** `tools/framing/face_audit.py` then `fix_faces.py`, so camera moves keep heads whole.
6. **Sound bed.** Recorded effects on word anchors, music ducked under speech (`cinematic-sound-design`).
7. **Lip-sync (optional).** Six mouth images per speaking picture from your image tool, then `tools/lipsync`.
8. **Render and check.** `motion_comic.py` (or `render_lipsync.py`), then `trailer_verify.py`, then look at frames.

## Lip-sync in short

For each picture where someone talks, ask your image tool for six edits of the same picture where only the mouth
changes: A closed (M/B/P), B teeth together (S/EE), C half open (EH), D wide (AH), E round (O), F pucker (OO). Name
them `<picture>__A.png` ... `__F.png`. Then:

```bash
# map.json: which picture shows which speaker, e.g. {"osric": "osric", "helena_box": "healer"}
RHUBARB=/path/to/rhubarb python3 tools/lipsync/lipsync_build.py plan.json map.json mouths/
LIPSYNC=lipsync.json python3 tools/lipsync/render_lipsync.py plan.json --out final.mp4
```

Mouths change only while that picture's own speaker is talking, and each shape is held at least two frames
("on twos", as in hand-drawn cartoons). The rest of the face stays still, so blinks or a small head move are the
next step if a long close-up feels stiff.

## Requirements

Python 3.10+, ffmpeg, numpy, pillow, scipy, onnxruntime, opencv-python-headless, sherpa-onnx (speech recognition for
timing and checks). Models: Kokoro-82M ONNX (voices), sherpa-onnx zipformer small-en (word timing), YuNet face
detector (framing; set `YUNET=` to its path), Rhubarb Lip Sync binary (lip-sync; set `RHUBARB=`). Hugging Face jobs
need a token with the Jobs permission and a billing method.

## Licences and what is not included

- No pictures, voices or sounds from the Blackfeather project are included. Sound libraries such as Pixabay allow
  use in your videos but not sharing the raw files.
- Model licences differ, and some don't allow commercial use. Check them before using the output commercially.
  FLUX.1-schnell is Apache 2.0, HiDream-O1-Image is MIT, and Kokoro-82M is Apache 2.0. Some newer image models are
  non-commercial or exclude whole countries.
