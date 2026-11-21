# /// script
# requires-python = ">=3.10"
# dependencies = ["torch", "diffusers>=0.32", "transformers", "accelerate", "sentencepiece", "protobuf", "huggingface_hub", "pillow"]
# ///
"""FLUX.1-schnell on a Hugging Face GPU job. Reads a spec (list of {name, prompt, w?, h?}) from your dataset repo,
makes TAKES images per entry and uploads them back. FLUX.1-schnell is Apache 2.0 but gated: accept its terms on the
model page first.

  hf jobs uv run --flavor a100-large --timeout 1h --secrets HF_TOKEN \
      -e OUT_REPO=you/my-art -e SPEC=spec.json -e SUBDIR=takes -e TAKES=3 -d gen_flux.py
"""
import json, os, time
from pathlib import Path
import torch
from diffusers import FluxPipeline
from huggingface_hub import HfApi, hf_hub_download

REPO, SPEC, SUBDIR = os.environ['OUT_REPO'], os.environ['SPEC'], os.environ.get('SUBDIR', 'takes')
TAKES = int(os.environ.get('TAKES', '3'))
t0 = time.time(); api = HfApi()
spec = json.loads(Path(hf_hub_download(REPO, SPEC, repo_type='dataset')).read_text())
pipe = FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-schnell', torch_dtype=torch.bfloat16).to('cuda')
print(f'loaded in {time.time() - t0:.0f}s', flush=True)
out = Path('out'); out.mkdir()
for i, e in enumerate(spec):
    for k in range(TAKES):
        im = pipe(e['prompt'], width=e.get('w', 1344), height=e.get('h', 768), num_inference_steps=4, guidance_scale=0.0,
                  max_sequence_length=256, generator=torch.Generator('cuda').manual_seed(1000 * (i + 1) + k)).images[0]
        im.save(out / f"{e['name']}__{k}.png")
    print(f"{i + 1}/{len(spec)} {e['name']} ({time.time() - t0:.0f}s)", flush=True)
    if (i + 1) % 10 == 0 or i + 1 == len(spec):
        api.upload_folder(folder_path=str(out), repo_id=REPO, repo_type='dataset', path_in_repo=SUBDIR)
print(f'done in {time.time() - t0:.0f}s', flush=True)
