#!/usr/bin/env python3
"""Convert annotated waveform SVGs directly to high-fidelity vector PDFs via rsvg-convert.

Renders raw oscilloscope background photos and vector annotations natively
using rsvg-convert, bypassing OpenCV/Matplotlib parsing.
"""

import base64
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = PROJECT_ROOT / "report" / "fig_work_A"
SVG_DIR = FIG_DIR / "svg"
RAW_DIR = FIG_DIR / "raw"
RSVG_BIN = Path("/opt/homebrew/bin/rsvg-convert")


def render_svg_to_pdf(svg_path: Path, out_pdf_path: Path) -> bool:
    if not svg_path.exists():
        print(f"Skipping {svg_path.name}: file not found")
        return False

    svg_text = svg_path.read_text(encoding="utf-8")

    # Inlining background raw image as Base64 Data URI to bypass local file access restrictions
    stem = svg_path.stem
    raw_path = RAW_DIR / f"{stem}.JPG"
    if raw_path.exists():
        b64_data = base64.b64encode(raw_path.read_bytes()).decode("ascii")
        svg_text = svg_text.replace(f"../raw/{stem}.JPG", f"data:image/jpeg;base64,{b64_data}")

    # Invoke rsvg-convert via stdin
    cmd = [str(RSVG_BIN), "-f", "pdf", "-o", str(out_pdf_path), "-"]
    res = subprocess.run(cmd, input=svg_text.encode("utf-8"), capture_output=True)

    if res.returncode != 0:
        print(f"Error rendering {svg_path.name}: {res.stderr.decode('utf-8')}")
        return False

    size_kb = out_pdf_path.stat().st_size / 1024
    print(f"Rendered: {out_pdf_path.name} ({size_kb:.1f} KB)")
    return True


def main() -> None:
    print(f"Using {RSVG_BIN} for native SVG->PDF vector rendering...")
    svg_files = sorted(SVG_DIR.glob("*.svg"))
    success_count = 0

    for svg_file in svg_files:
        out_pdf = FIG_DIR / f"{svg_file.stem}.pdf"
        if render_svg_to_pdf(svg_file, out_pdf):
            success_count += 1

    print(f"Successfully rendered {success_count}/{len(svg_files)} PDFs.")


if __name__ == "__main__":
    main()
