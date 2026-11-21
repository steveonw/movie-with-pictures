---
name: "image-request-pack"
description: "Package requests for new or sharper images that a person will make with an outside image AI: start image per shot, prompts, face references, a master prompt, return naming, fallbacks."
---

# Image request pack

Use when a project (usually a video built from stills) needs new or sharper images that the person
will generate in another tool, starting from the existing art so faces, costumes and style stay
consistent. Distilled from a trailer where 12 returned images fixed more than any effect did.

## Decide what to ask for
Look at a contact sheet of every shot and count:
- **Repeats:** a face used 6 times, or two stills that ping-pong through a conversation.
- **Soft or dark shots:** small upscaled crops, frames with a mean luma near 10.
- **What the script names but the picture never shows:** geography, two-shots, the people at stake,
  hands and props, the threat up close.

Ask for new coverage first (about 6), remasters of the softest shots second (about 4), nice-to-haves
third. Number them by tier: P1-01, P2-07, P3-11. Don't spend a request on yet another portrait of the
most-used face.

## One folder per request (`P1-01_short_name/`)
- `start.png`: the clean starting picture, cropped clear of painted text, timecodes and panel gutters.
- `start_16x9.png`: the same picture on a 16:9 canvas with dark blurred edges, for tools that keep
  the input's shape (they paint over the edges).
- `prompt.txt`: id and title; which lines or shots it is for; how much to change; which face
  references to attach; then the prompt = shot description + character sentences + style block +
  world block + avoid block, ready to paste.

Plus `character_refs/` (a clean close-up and a costume crop per main character), `PROMPTS.md` (all
requests in one file), `requests_overview.png` (numbered sheet of the start images) and
`MASTER_PROMPT.txt`.

```python
from PIL import Image, ImageFilter
def to169(im):
    w, h = im.size
    if abs(w / h - 16 / 9) < .02: return im
    W = max(w, round(h * 16 / 9)); H = round(W * 9 / 16)
    if H < h: H = h; W = round(H * 16 / 9)
    bg = im.resize((W, H)).filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * .55))
    bg.paste(im, ((W - w) // 2, (H - h) // 2)); return bg
```

## How much to change (tools name this differently: strength, denoise, image weight)
- **Little, about 30-40%:** a remaster. Keep the composition, faces and light; add detail; extend to 16:9.
- **Moderate, about 50-60%:** same faces and costume, new pose or framing.
- **A lot, about 65-75% or the tool's reference mode:** style, palette and costume only; new composition.

## Prompt blocks
- **Style:** the existing look in words (medium, palette, light, depth of field), plus
  "16:9, 1920x1080 or larger".
- **World:** costumes, weapons, the enemy and the setting in one or two sentences.
- **Characters:** one sentence each: age, hair, wounds or marks, costume.
- **Avoid:** no text, letters, captions, subtitles, timecodes, numbers, watermarks, logos or borders;
  no modern clothing; no extra limbs or fingers; don't change named faces.

Look at every start image before writing its prompt, and describe what is actually there (a
handheld radio stays a handheld radio; "in profile" only if it is a profile).

## Master prompt (adapt the names)
```
I'm attaching a zip of image requests for <project>. Make one new image per request, starting
from the picture I give you for it.

In the zip: one folder per request (start.png, start_16x9.png, prompt.txt), character_refs/ with
clean pictures of the main characters (keep their faces, hair, marks and costume consistent),
and PROMPTS.md with all prompts.

Work in order: P1 first, then P2, then P3 (optional). Follow each prompt.txt exactly, including
how much to change the start image (little = re-render sharper; moderate = new pose, same faces;
a lot = new composition, same style). Every image 16:9, 1920x1080 or larger, in the same look as
the start images. Never put text, letters, captions, timecodes, numbers, watermarks, logos or
borders in an image. Don't change the named characters' faces.

Return: name each image by its number only (P1-01.png ...). After each, say in one line if
anything didn't match (face, hands, framing). If you can't do one, skip it, say why, move on.

<short list: one or two lines per request>

If you can't open zip files, tell me and I'll upload one request at a time.
```

## When images come back
- Expect filter rejections on anything that sounds violent (a crying young soldier was refused as
  violent). Keep a fallback shot for every request, and don't re-ask with grimmer wording.
- Check each: size and 16:9, faces against the references, stray text, hands. Measure mean luma and
  lift very dark images with a gamma of about 0.6-0.75 before use.
- Returned images may be upscaled from about 1672x941: cap zoom at about 1.5x on them.
- Re-run the contact sheet and the repeated-framing check with the new images in place.