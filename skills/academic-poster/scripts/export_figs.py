#!/usr/bin/env python3
"""Export paper figures at print resolution for a poster.

Input : one or more figure files or folders (vector PDF preferred; PNG/JPEG accepted).
Method: vector PDF -> PNG whose long side is exactly --long-side px (default 6000, which gives
        >= 150 PPI up to ~101 cm placed width); optionally also SVG with text as paths (--svg).
        Raster inputs are copied unchanged and their pixel size is reported.
        With --placed-cm W, each figure's effective PPI at W cm placed width is reported:
        PPI = px_w / (W / 2.54).
Output: JSON on stdout: {"ok", "figures": [{"src", "png", "px": [w, h], "aspect", "svg"?, "ppi_at_placed"?}],
        "skipped": [...]}. Exit 0 = ok, 1 = a file failed, 2 = PDFs given but PyMuPDF missing.
Python >= 3.8. PyMuPDF (pip install pymupdf) is needed only for PDF inputs.
"""
import argparse
import json
import os
import shutil
import struct
import sys

RASTER = (".png", ".jpg", ".jpeg")


def raster_size(path):
    """(w, h) of a PNG or JPEG using only the stdlib."""
    with open(path, "rb") as fh:
        head = fh.read(26)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            return struct.unpack(">II", head[16:24])
        fh.seek(0)
        if fh.read(2) != b"\xff\xd8":
            raise ValueError("not a PNG or JPEG")
        while True:
            marker = fh.read(2)
            if len(marker) < 2 or marker[0] != 0xFF:
                raise ValueError("bad JPEG")
            if marker[1] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                fh.read(3)
                h, w = struct.unpack(">HH", fh.read(4))
                return w, h
            seg = struct.unpack(">H", fh.read(2))[0]
            fh.seek(seg - 2, 1)


def collect(srcs):
    files = []
    for s in srcs:
        if os.path.isdir(s):
            for name in sorted(os.listdir(s)):
                if name.lower().endswith((".pdf",) + RASTER):
                    files.append(os.path.join(s, name))
        else:
            files.append(s)
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="+", help="figure files (PDF/PNG/JPEG) or folders")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--long-side", type=int, default=6000, help="PNG long side in px (default 6000)")
    ap.add_argument("--page", type=int, default=1, help="PDF page to render, 1-based (default 1)")
    ap.add_argument("--svg", action="store_true", help="also write SVG with text as paths (PDF inputs)")
    ap.add_argument("--placed-cm", type=float, help="placed width in cm, to report effective PPI")
    a = ap.parse_args()

    files = collect(a.src)
    os.makedirs(a.out, exist_ok=True)
    fitz = None
    if any(f.lower().endswith(".pdf") for f in files):
        try:
            try:  # PyMuPDF >= 1.24.3 is 'pymupdf'; 'fitz' is the deprecated alias
                import pymupdf as fitz
            except ImportError:
                import fitz
        except ImportError:
            print(json.dumps({"ok": None, "status": "skipped",
                              "reason": "dependency missing: PyMuPDF (pip install pymupdf) needed for PDF inputs"}))
            sys.exit(2)

    figs, errors = [], []
    for f in files:
        stem = os.path.splitext(os.path.basename(f))[0]
        try:
            rec = {"src": f}
            if f.lower().endswith(".pdf"):
                page = fitz.open(f)[a.page - 1]
                zoom = a.long_side / max(page.rect.width, page.rect.height)
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
                dst = os.path.join(a.out, stem + ".png")
                pix.save(dst)
                w, h = pix.width, pix.height
                if a.svg:
                    svg = os.path.join(a.out, stem + ".svg")
                    with open(svg, "w", encoding="utf-8") as fh:
                        fh.write(page.get_svg_image(text_as_path=True))
                    rec["svg"] = svg
            else:
                dst = os.path.join(a.out, os.path.basename(f))
                if os.path.abspath(dst) != os.path.abspath(f):
                    shutil.copyfile(f, dst)
                w, h = raster_size(f)
            rec.update({"png": dst, "px": [w, h], "aspect_h_over_w": round(h / float(w), 5)})
            if a.placed_cm:
                rec["ppi_at_placed"] = round(w / (a.placed_cm / 2.54), 1)
            figs.append(rec)
        except Exception as e:  # report and continue
            errors.append({"src": f, "error": str(e)})

    print(json.dumps({"ok": not errors, "figures": figs, "errors": errors}, indent=1))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
