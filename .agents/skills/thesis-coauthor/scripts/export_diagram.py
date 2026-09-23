#!/usr/bin/env python3
"""
Draw.io diagram exporter for thesis figures (Pathway A).
Exports native .drawio files to vector PDF and raster PNG (with bounding box crop).
Works seamlessly on Linux and WSL (calling Windows draw.io.exe via wslpath).
"""

import sys
import shutil
import argparse
import subprocess
from pathlib import Path

DEFAULT_CHAPTER = "3_SystemModel"
DEFAULT_WORKSPACE = Path("/home/felipeab/MultiAgentON")


def find_drawio_executable() -> tuple[str, bool]:
    """
    Locates the draw.io executable.
    Returns (executable_path, is_windows_binary_in_wsl).
    """
    # 1. Check native Linux PATH
    for cmd in ["drawio", "draw.io"]:
        if shutil.which(cmd):
            return cmd, False

    # 2. Check known WSL paths to Windows draw.io.exe
    wsl_candidates = [
        Path("/mnt/c/Users/felip/AppData/Local/Programs/draw.io/draw.io.exe"),
        Path("/mnt/c/Program Files/draw.io/draw.io.exe"),
        Path("/mnt/c/Program Files (x86)/draw.io/draw.io.exe"),
    ]
    for cand in wsl_candidates:
        if cand.is_file():
            return str(cand), True

    # Check via cmd.exe where draw.io if on WSL
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
        "Could not find draw.io or draw.io.exe in PATH or standard WSL paths. "
        "Please ensure Draw.io Desktop is installed."
    )


def export_single_diagram(src_file: Path, drawio_exe: str, is_wsl_win: bool) -> None:
    """Exports a single .drawio file to its corresponding pdf/ and png/ folders."""
    if not src_file.is_file():
        raise FileNotFoundError(f"Diagram source not found: {src_file}")

    # Determine figs_<Chapter> root from file hierarchy
    # Expected: .../figs_<Chapter>/src/diagrams/<name>.drawio
    if "src" in src_file.parts and "diagrams" in src_file.parts:
        figs_root = src_file.parents[2]
    else:
        figs_root = src_file.parent

    pdf_dir = figs_root / "pdf"
    png_dir = figs_root / "png"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)

    base_name = src_file.stem
    out_pdf = pdf_dir / f"{base_name}.pdf"
    out_png = png_dir / f"{base_name}.png"

    if is_wsl_win:
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

    print(f"✓ Successfully generated {out_pdf.name} and {out_png.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Export .drawio diagram(s) to publication-ready PDF and PNG."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Diagram semantic name (e.g., 'conceptual_framework') or path to .drawio file.",
    )
    parser.add_argument(
        "--chapter",
        "-c",
        default=DEFAULT_CHAPTER,
        help=f"Chapter folder name under thesis_drafts (default: '{DEFAULT_CHAPTER}').",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all diagrams in the chapter's src/diagrams directory.",
    )

    args = parser.parse_args()

    drawio_exe, is_wsl_win = find_drawio_executable()

    figs_dir = (
        DEFAULT_WORKSPACE
        / "docs"
        / "LLM_Wiki"
        / "wiki"
        / "thesis_drafts"
        / args.chapter
        / f"figs_{args.chapter.split('_', 1)[-1] if '_' in args.chapter else args.chapter}"
    )

    diagrams_dir = figs_dir / "src" / "diagrams"

    if args.all:
        drawio_files = sorted(diagrams_dir.glob("*.drawio"))
        if not drawio_files:
            print(f"No .drawio files found in {diagrams_dir}")
            sys.exit(1)
        for f in drawio_files:
            export_single_diagram(f, drawio_exe, is_wsl_win)
        return

    if not args.target:
        print("Error: Specify a diagram name, a file path, or use --all.")
        parser.print_help()
        sys.exit(1)

    target_path = Path(args.target)
    if target_path.is_file():
        export_single_diagram(target_path, drawio_exe, is_wsl_win)
    else:
        # Treat as semantic name
        name = target_path.stem
        src_file = diagrams_dir / f"{name}.drawio"
        if not src_file.is_file():
            # Fallback: search anywhere under thesis_drafts
            matches = list(
                (DEFAULT_WORKSPACE / "docs" / "LLM_Wiki" / "wiki" / "thesis_drafts").glob(
                    f"**/{name}.drawio"
                )
            )
            if matches:
                src_file = matches[0]
            else:
                print(f"Error: Diagram '{name}.drawio' not found in {diagrams_dir}")
                sys.exit(1)
        export_single_diagram(src_file, drawio_exe, is_wsl_win)


if __name__ == "__main__":
    main()
