"""
Generate placeholder canonical items and media.

This script writes:
- JSON canonical items to a target directory (default: data/canonical)
- Placeholder SVG media under media/items/<template_id>/figN.svg

Notes
- Output conforms to schemas/item_canonical_v1.json (required fields present)
- Content is filler text; useful for wiring storage, selection, and serve transforms
- Designed to be quiet by default and non-interactive

Example (PowerShell, run from repo root):
  python tools/generate_canonical_seed.py --count 10

Exit behavior
- Exit 0 with a single summary line on success
- Exit 1 with a brief error line on failure
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import string
import sys
from pathlib import Path
from typing import List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate placeholder canonical items and media", add_help=True)
    parser.add_argument("--count", type=int, default=10, help="Number of items to generate (default: 10)")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data") / "canonical",
        help="Directory to write canonical JSON files (default: data/canonical)",
    )
    parser.add_argument(
        "--media-root",
        type=Path,
        default=Path("media") / "items",
        help="Root directory for media (default: media/items)",
    )
    parser.add_argument("--steps", type=int, default=2, choices=[1, 2, 3], help="Steps per item (default: 2)")
    parser.add_argument(
        "--seed",
        type=str,
        default=None,
        help="Random seed for reproducible output (default: none)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing JSON files with the same id (default: false)",
    )
    return parser.parse_args()


HEX_ALPHABET = "abcdef" + string.digits


def generate_id(prefix: str, length: int = 8) -> str:
    token = "".join(random.choice(HEX_ALPHABET) for _ in range(length))
    return f"{prefix}_{token}"


def generate_svg(label: str) -> str:
    # Minimal placeholder SVG; label helps visual verification
    return (
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"320\" height=\"160\">"
        f"<rect width=\"100%\" height=\"100%\" fill=\"#eeeeee\"/>"
        f"<text x=\"16\" y=\"88\" font-size=\"14\" fill=\"#333333\">{label}</text>"
        f"</svg>"
    )


def build_steps(steps_count: int) -> List[dict]:
    steps: List[dict] = []
    for idx in range(1, steps_count + 1):
        step = {
            "step_id": f"s{idx}",
            "prompt": {"html": f"Step {idx}: filler prompt lorem \( x \) ipsum?"},
            "choices": [
                {"id": cid, "text": f"{cid}-option"} for cid in ["A", "B", "C", "D"]
            ],
            "hint": "n/a",
            "explanation": {"html": "Filler explanation."},
        }
        steps.append(step)
    return steps


def main() -> int:
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    out_dir: Path = args.out
    media_root: Path = args.media_root
    out_dir.mkdir(parents=True, exist_ok=True)
    media_root.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    written = 0
    items_count = max(0, int(args.count))
    if items_count == 0:
        print("You have to request at least one item via --count", file=sys.stderr)
        return 1

    for n in range(1, items_count + 1):
        template_id = f"tpl_lorem_{n:03d}"
        item_id = generate_id("i")
        variant_index = n

        # Media: write two placeholder svgs per template
        template_media_dir = media_root / template_id
        template_media_dir.mkdir(parents=True, exist_ok=True)
        (template_media_dir / "fig1.svg").write_text(generate_svg(f"{template_id}-fig1"), encoding="utf-8")
        (template_media_dir / "fig2.svg").write_text(generate_svg(f"{template_id}-fig2"), encoding="utf-8")

        item = {
            "id": item_id,
            "template_id": template_id,
            "content_version": 1,
            "type": "LOREM_TYPE",
            "title": f"Lorem Item {n}",
            "content": {"html": f"Filler prompt {n}: \\( x \\) zizzle."},
            "media": [
                {"id": "fig1", "object_key": f"items/{template_id}/fig1.svg", "alt": "Placeholder figure 1"},
                {"id": "fig2", "object_key": f"items/{template_id}/fig2.svg", "alt": "Placeholder figure 2"},
            ],
            "steps": build_steps(args.steps),
            "final": {"answer_text": "n/a", "explanation": {"html": "n/a"}},
            "tags": {"skill": f"skill_group_{(n % 3) + 1}", "difficulty": random.choice(["E", "M", "H"])},
            "generated_at": now,
            "generator_version": "seed_v1",
            "variant_index": variant_index,
        }

        target_path = out_dir / f"{item_id}.json"
        if target_path.exists() and not args.overwrite:
            # Skip existing unless overwrite requested
            continue

        target_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
        written += 1

    print(f"Done: wrote {written} canonical items to {out_dir.as_posix()} and media to {media_root.as_posix()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - top-level guard to keep output terse
        print(f"You have to fix error in generator ({type(exc).__name__}: {exc})", file=sys.stderr)
        raise


