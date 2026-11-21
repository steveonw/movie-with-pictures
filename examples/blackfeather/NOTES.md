# Blackfeather Academy in a Box: project scripts

These are the scripts as they were used to make the ad, kept for reference. They expect the project's folders
(`user_art/`, `user_inserts/`, `sfx/`, models, voices) and the skill scripts next to them, so read them as worked
examples rather than ready tools; the general versions are in `tools/`.

| Script | Role |
|---|---|
| `make_plan.py` | The whole edit as code: every line, speaker, shot, camera move, effect and sound cue. Writes `plan.json`, plus `plan_hd.json` (`ART=art_hd`) and `plan_user.json` (`ART=art_user`) variants. |
| `build_bed.py` | Sound bed: designed layers (owlbear = monster roar + tiger + pitched hawk), music cues that start and stop on words, ducking under speech. |
| `art_prompts.py` | Shot prompts for the first art pass (FLUX.1-schnell). |
| `hd_specs.py`, `hd_action.py` | Character references and shot specs for the HiDream-O1 pass (with and without reference images). |
| `compose_art.py`, `compose_hd.py`, `compose_user.py` | Turn each art source into the plan's pictures: picks, crops, colour pass, on-screen text drawn in code. |
| `build_pack.py` | The image request pack for in-between shots in the painted style. |
| `lipsync_build.py` | Project version of `tools/lipsync/lipsync_build.py` (maps cropped pictures back to their mouth sources). |

## What we learned

- **Voice and rough draft first.** The placeholder draft caught effects landing on top of words and a creaking
  chest drowning out a line before any art existed.
- **Your own art won.** Three art sources were tried: FLUX.1-schnell, HiDream-O1 with and without references,
  and paintings from the user's image tool. The paintings were the most consistent and the most expressive.
- **References are a trade-off.** HiDream with reference images kept the characters identical but copied the
  reference's calm pose and face. Action and emotion shots worked better without references.
- **Re-aim the camera for every new art set.** Moves written for one set of pictures cut off 44 heads in the
  next. A face detector plus an automatic re-aim fixed them all.
- **Text in code, never in the image model.** Warning labels, banners and end cards were drawn in code, so they
  were always spelled right.
- **Lip-sync by mouth swaps suits painted art.** 90 mouth images (15 speakers × 6 shapes) plus Rhubarb timing.
  No video model was needed.
