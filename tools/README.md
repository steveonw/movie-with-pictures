# Tools

- `lipsync/`: `lipsync_build.py` (mouth timing per frame from Rhubarb) and `render_lipsync.py` (motion_comic with mouth swaps). See the main README.
- `framing/`: `face_audit.py plan.json` finds heads in every plan picture and lists shots that cut one off (writes faces.json); `fix_faces.py plan.json` re-aims those shots in place. Needs the YuNet ONNX model (`YUNET=path`).
- `parallax/`: `parallax.py` builds a 12 s multiplane shot from bg.png, a character PNG with transparency, a foreground PNG with transparency and the combined picture (used to match the character's size, position and light). Edit the constants at the top for a new scene.
- `hf_jobs/`: `gen_flux.py` and `gen_hidream.py` run on Hugging Face GPU jobs (`hf jobs uv run ...`), read a JSON spec from your dataset repo and upload the images back. HiDream takes `refs` (reference image paths in the same repo) per entry.
