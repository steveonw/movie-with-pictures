# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["torch>=2.10", "torchvision", "transformers==4.57.1", "diffusers", "accelerate", "einops",
#                 "numpy", "pillow", "tqdm", "scipy", "huggingface_hub"]
# ///
"""HiDream-O1-Image-Dev on a Hugging Face GPU job. Reads a spec (list of {name, prompt, refs, w, h}) from the
dataset repo, generates TAKES images per entry with the given reference images, uploads PNGs back to the repo."""
import io, json, os, sys, time, urllib.request, zipfile
from pathlib import Path

REPO = os.environ['OUT_REPO']; SPEC = os.environ['SPEC']; SUBDIR = os.environ['SUBDIR']
TAKES = int(os.environ.get('TAKES', '2'))
t0 = time.time()

# HiDream's code from GitHub (no git in the image), flash-attn switched off
code = Path('hd'); zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(
    'https://github.com/HiDream-ai/HiDream-O1-Image/archive/refs/heads/main.zip').read())).extractall(code)
src = next(code.iterdir()); pl = src / 'models' / 'pipeline.py'
pl.write_text(pl.read_text().replace('"use_flash_attn": True', '"use_flash_attn": False'))
sys.path.insert(0, str(src))

import torch
from huggingface_hub import HfApi, hf_hub_download, snapshot_download
from transformers import AutoProcessor, PreTrainedTokenizerBase
from models.qwen3_vl_transformers import Qwen3VLForConditionalGeneration
from models.pipeline import generate_image, DEFAULT_TIMESTEPS

api = HfApi()
spec = json.loads(Path(hf_hub_download(REPO, SPEC, repo_type='dataset')).read_text())
refs_needed = sorted({r for e in spec for r in e.get('refs', [])})
ref_dir = Path(snapshot_download(REPO, repo_type='dataset', allow_patterns=refs_needed)) if refs_needed else None

mp = snapshot_download('HiDream-ai/HiDream-O1-Image-Dev')
processor = AutoProcessor.from_pretrained(mp)
model = Qwen3VLForConditionalGeneration.from_pretrained(mp, torch_dtype=torch.bfloat16, device_map='cuda').eval()
tok = processor if isinstance(processor, PreTrainedTokenizerBase) else processor.tokenizer
tok.boi_token, tok.bor_token, tok.eor_token, tok.bot_token, tok.tms_token = \
    '<|boi_token|>', '<|bor_token|>', '<|eor_token|>', '<|bot_token|>', '<|tms_token|>'
print(f'loaded in {time.time() - t0:.0f}s', flush=True)

out = Path('out'); out.mkdir()
for i, e in enumerate(spec):
    refs = [str(ref_dir / r) for r in e.get('refs', [])]
    for k in range(TAKES):
        img = generate_image(model=model, processor=processor, prompt=e['prompt'], ref_image_paths=refs,
                             height=e.get('h', 1440), width=e.get('w', 2560), num_inference_steps=28,
                             guidance_scale=0.0, shift=1.0, timesteps_list=DEFAULT_TIMESTEPS, scheduler_name='flash',
                             seed=1000 * (i + 1) + k, noise_scale_start=7.5, noise_scale_end=7.5, noise_clip_std=2.5)
        img.save(out / f"{e['name']}__{k}.png")
    print(f"{i + 1}/{len(spec)} {e['name']} refs={len(refs)} ({time.time() - t0:.0f}s)", flush=True)
    if (i + 1) % 6 == 0 or i + 1 == len(spec):
        api.upload_folder(folder_path=str(out), repo_id=REPO, repo_type='dataset', path_in_repo=SUBDIR)
print(f'done in {time.time() - t0:.0f}s', flush=True)
