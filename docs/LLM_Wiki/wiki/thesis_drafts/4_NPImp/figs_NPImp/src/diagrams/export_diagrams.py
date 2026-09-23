#!/usr/bin/env python3
"""
Standalone Draw.io diagram exporter for Chapter 4 Neurosymbolic Pipeline Implementation figures.
Exports all .drawio files in this directory (or a specific target) to ../../pdf/ and ../../png/.
Supports native Linux and WSL (calling Windows draw.io.exe seamlessly).
"""

import sys
import shutil
import argparse
import subprocess
from pathlib import Path


def find_drawio() -> tuple[str, bool]:
    """Finds drawio executable on Linux or WSL."""
    # 1. Native Linux
    for cmd in ["drawio", "draw.io"]:
        if shutil.which(cmd):
            return cmd, False

    # 2. WSL Windows paths
    candidates = [
        Path("/mnt/c/Users/felip/AppData/Local/Programs/draw.io/draw.io.exe"),
        Path("/mnt/c/Program Files/draw.io/draw.io.exe"),
        Path("/mnt/c/Program Files (x86)/draw.io/draw.io.exe"),
    ]
    for cand in candidates:
        if cand.is_file():
            return str(cand), True

    # 3. Query Windows cmd where
    try:
        where_out = subprocess.check_output(
            ["cmd.exe", "/c", "where draw.io"], stderr=subprocess.DEVNULL
        ).decode().strip().splitlines()
        if where_out:
            wsl_cand = subprocess.check_output(
                ["wslpath", "-u", where_out[0].strip()]
            ).decode().strip()
            if Path(wsl_cand).is_file():
                return wsl_cand, True
    except Exception:
        pass

    raise FileNotFoundError(
        "Draw.io desktop executable not found in PATH or standard WSL paths."
    )


def export_diagram(src_file: Path, drawio_exe: str, is_wsl: bool) -> None:
    """Exports a single .drawio file to PDF and PNG with bounding-box cropping."""
    figs_root = src_file.parents[2]  # from src/diagrams/ -> figs_NPImp/
    pdf_dir = figs_root / "pdf"
    png_dir = figs_root / "png"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)

    base_name = src_file.stem
    out_pdf = pdf_dir / f"{base_name}.pdf"
    out_png = png_dir / f"{base_name}.png"

    if is_wsl:
        win_in = subprocess.check_output(["wslpath", "-w", str(src_file)]).decode().strip()
        win_pdf = subprocess.check_output(["wslpath", "-w", str(out_pdf)]).decode().strip()
        win_png = subprocess.check_output(["wslpath", "-w", str(out_png)]).decode().strip()
    else:
        win_in = str(src_file)
        win_pdf = str(out_pdf)
        win_png = str(out_png)

    print(f"--> Exporting {src_file.name} to PDF ({out_pdf.name})...")
    subprocess.run([drawio_exe, "-x", "-f", "pdf", "--crop", "-o", win_pdf, win_in], check=True)

    print(f"--> Exporting {src_file.name} to PNG ({out_png.name})...")
    subprocess.run([drawio_exe, "-x", "-f", "png", "--crop", "-o", win_png, win_in], check=True)

    print(f"✓ Generated {out_pdf.name} and {out_png.name}")


def main():
    parser = argparse.ArgumentParser(description="Export Draw.io diagrams to PDF and PNG.")
    parser.add_argument("target", nargs="?", help="Specific diagram name or file to export (default: all .drawio in folder)")
    args = parser.parse_args()

    curr_dir = Path(__file__).resolve().parent
    drawio_exe, is_wsl = find_drawio()

    if args.target:
        target_path = Path(args.target)
        if not target_path.suffix:
            target_path = curr_dir / f"{args.target}.drawio"
        elif not target_path.is_absolute():
            target_path = curr_dir / target_path
        files = [target_path]
    else:
        files = [f for f in curr_dir.glob("*.drawio") if not f.name.startswith(".")]

    if not files:
        print("No .drawio files found to export.")
        return

    for f in sorted(files):
        export_diagram(f, drawio_exe, is_wsl)


if __name__ == "__main__":
    main()
