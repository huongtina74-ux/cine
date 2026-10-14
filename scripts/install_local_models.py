#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

PRESETS = {
    "wan22-5b": {
        "files": [
            ("diffusion_models/wan2.2_ti2v_5B_fp16.safetensors", "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_ti2v_5B_fp16.safetensors"),
            ("text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"),
            ("vae/wan2.2_vae.safetensors", "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan2.2_vae.safetensors"),
        ],
        "workflow": "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/refs/heads/main/templates/video_wan2_2_5B_ti2v.json",
    },
    "qwen-image-2512": {
        "files": [
            ("diffusion_models/qwen_image_2512_fp8_e4m3fn.safetensors", "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_2512_fp8_e4m3fn.safetensors"),
            ("text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors", "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors"),
            ("vae/qwen_image_vae.safetensors", "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors"),
        ],
        "workflow": "https://raw.githubusercontent.com/Comfy-Org/workflow_templates/refs/heads/main/templates/image_qwen_Image_2512.json",
    },
}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"SKIP {dest} (already exists)")
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"GET  {url}\n  -> {dest}")
    with urllib.request.urlopen(url) as r, tmp.open("wb") as f:
        total = int(r.headers.get("Content-Length", "0") or 0)
        done = 0
        while True:
            chunk = r.read(8 * 1024 * 1024)
            if not chunk:
                break
            f.write(chunk); done += len(chunk)
            if total:
                print(f"\r  {done/1024**3:.2f}/{total/1024**3:.2f} GiB ({done*100/total:.1f}%)", end="", flush=True)
    if total:
        print()
    tmp.replace(dest)


def main() -> int:
    ap = argparse.ArgumentParser(description="Install official local model files into an existing ComfyUI tree.")
    ap.add_argument("preset", choices=sorted(PRESETS))
    ap.add_argument("--comfy-root", type=Path, required=True)
    ap.add_argument("--reference-workflows", type=Path, default=Path("workflows/reference"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()

    comfy = args.comfy_root.resolve()
    models = comfy / "models"
    preset = PRESETS[args.preset]
    print(f"Preset: {args.preset}\nComfyUI: {comfy}")
    print("This downloads large open-weight files. Review the exact model/license terms before commercial production.")
    if not args.yes and not args.dry_run:
        answer = input("Continue? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            return 1

    for rel, url in preset["files"]:
        dest = models / rel
        if args.dry_run:
            print(f"DRY {url} -> {dest}")
        else:
            download(url, dest)

    workflow_dest = args.reference_workflows / f"{args.preset}.frontend.json"
    if args.dry_run:
        print(f"DRY {preset['workflow']} -> {workflow_dest}")
    else:
        download(preset["workflow"], workflow_dest)
        print(f"Reference frontend workflow saved to {workflow_dest}")
        print("Load it in ComfyUI, verify it, then export API-format JSON and import it with `cinefactory import-workflow`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
