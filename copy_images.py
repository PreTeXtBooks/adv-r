#!/usr/bin/env python3
"""
Copy and convert images to PreTeXt assets/images directory.
This script prepares images from the diagrams/ and screenshots/ source
directories for the PreTeXt build process.
"""

import shutil
import subprocess
from pathlib import Path


def copy_tree(src_dir, dest_dir, convert_available, images_copied, images_converted):
    """Recursively copy PNG files and convert EPS files from src_dir to dest_dir."""
    for src_file in src_dir.rglob("*"):
        if not src_file.is_file():
            continue

        rel_path = src_file.relative_to(src_dir)
        target_file = dest_dir / rel_path

        if src_file.suffix.lower() == ".png":
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, target_file)
            images_copied += 1
            print(f"  Copied: {rel_path}")

        elif src_file.suffix.lower() == ".eps" and convert_available:
            png_target = target_file.with_suffix(".png")
            if png_target.exists():
                continue
            png_target.parent.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    [
                        "convert",
                        "-density", "300",
                        "-quality", "90",
                        str(src_file),
                        str(png_target),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                images_converted += 1
                print(f"  Converted: {rel_path} -> {png_target.name}")
            except subprocess.CalledProcessError as e:
                print(f"  Warning: Failed to convert {src_file.name}: {e}")
            except Exception as e:
                print(f"  Warning: Error processing {src_file.name}: {e}")

    return images_copied, images_converted


def main():
    script_dir = Path(__file__).parent
    # Source directories (diagrams and screenshots live at the repo root)
    diagrams_dir = script_dir / "diagrams"
    screenshots_dir = script_dir / "screenshots"
    # Target directory: pretext/assets/images/ (the "external" assets directory
    # for PreTeXt is pretext/assets/, so images must be inside images/ there)
    pretext_images = script_dir / "pretext" / "assets" / "images"

    print("Preparing images for PreTeXt book...")

    convert_available = shutil.which("convert") is not None
    if convert_available:
        print("ImageMagick found - will convert EPS to PNG")
    else:
        print("ImageMagick not found - will only copy existing PNG files")

    images_copied = 0
    images_converted = 0

    # Copy diagram images (preserving subdirectory structure)
    if diagrams_dir.exists():
        print(f"\nCopying diagrams: {diagrams_dir} -> {pretext_images}")
        images_copied, images_converted = copy_tree(
            diagrams_dir, pretext_images, convert_available, images_copied, images_converted
        )
    else:
        print(f"Warning: diagrams directory not found at {diagrams_dir}")

    # Copy screenshots (placed under images/screenshots/)
    if screenshots_dir.exists():
        screenshots_target = pretext_images / "screenshots"
        print(f"\nCopying screenshots: {screenshots_dir} -> {screenshots_target}")
        images_copied, images_converted = copy_tree(
            screenshots_dir, screenshots_target, convert_available, images_copied, images_converted
        )
    else:
        print(f"Warning: screenshots directory not found at {screenshots_dir}")

    total_images = sum(1 for _ in pretext_images.rglob("*.png"))
    print(f"\nComplete!")
    print(f"  Copied: {images_copied} PNG files")
    print(f"  Converted: {images_converted} EPS files")
    print(f"  Total images in assets/images: {total_images}")

    if total_images == 0:
        print("\nNote: No images were found.")

    return 0


if __name__ == "__main__":
    exit(main())
