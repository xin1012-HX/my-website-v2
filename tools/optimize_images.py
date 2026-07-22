#!/usr/bin/env python3
"""Create web-ready image assets from the original portfolio repository."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUTPUT = ROOT / "assets" / "images"
MEDIA = ROOT / "assets" / "media"


def load_required_images() -> set[str]:
    projects = json.loads((CONTENT / "projects.json").read_text(encoding="utf-8"))
    artworks = json.loads((CONTENT / "artworks.json").read_text(encoding="utf-8"))
    names = {"logo.png", "profile.jpg", "favicon.png"}
    for project in projects:
        names.add(project["cover"])
        names.update(image["src"] for image in project["images"])
    names.update(artwork["src"] for artwork in artworks)
    return names


def output_name(source_name: str) -> str:
    if source_name == "favicon.png":
        return source_name
    return f"{Path(source_name).stem}.webp"


def max_width_for(name: str) -> int:
    if name.startswith("art-"):
        return 1600
    if any(token in name for token in ("plan", "section", "analysis", "diagram", "location")):
        return 2400
    return 2200


def convert(source: Path, destination: Path) -> tuple[int, int]:
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        maximum = max_width_for(source.name)
        if image.width > maximum:
            height = round(image.height * maximum / image.width)
            image = image.resize((maximum, height), Image.Resampling.LANCZOS)

        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.suffix.lower() == ".png":
            image.save(destination, format="PNG", optimize=True)
        else:
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            image.save(destination, format="WEBP", quality=82, method=6)
        return image.width, image.height


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Path to the original my-website checkout")
    args = parser.parse_args()
    source_root = args.source.resolve()
    if not source_root.is_dir():
        raise SystemExit(f"Source directory not found: {source_root}")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict[str, int | str]] = {}

    for name in sorted(load_required_images()):
        source = source_root / name
        if not source.is_file():
            raise SystemExit(f"Required image not found: {source}")
        generated_name = output_name(name)
        destination = OUTPUT / generated_name
        width, height = convert(source, destination)
        manifest[name] = {
            "file": generated_name,
            "width": width,
            "height": height,
            "bytes": destination.stat().st_size,
        }
        print(f"{name} -> {generated_name} ({width}x{height})")

    for media_name in ("Xin_Louis_He_CV.pdf", "z-day-video.mp4"):
        source = source_root / media_name
        if source.is_file():
            shutil.copy2(source, MEDIA / media_name)

    (CONTENT / "image-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
