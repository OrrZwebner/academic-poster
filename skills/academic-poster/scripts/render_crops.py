#!/usr/bin/env python3
"""Render a poster (any format) to a full-page PNG plus named crops for the REVIEW notes file.

Input : --poster  PDF | PNG/JPG/TIFF/WebP | PPTX/PPT/ODP/ODG/DOCX/KEY (converted to PDF first).
        A Canva design cannot be read directly: export it first with the Canva MCP `export-design`
        (PDF, pro quality if available, or PNG) and pass the exported file.
Method:
  1 convert   office formats -> PDF with `soffice --headless --convert-to pdf` (LibreOffice; path from
              $SOFFICE, PATH or /Applications/LibreOffice.app); else on macOS Keynote via osascript
              (PPTX/PPT/KEY only; --no-keynote disables); else exit 2 "skipped".
  2 raster    PDF page -> pixmap at --dpi (W = page_pt_w * dpi / 72). Raster images are used as is.
  3 full      full.png, --full-width px wide (PDF: rendered at that width; raster: downscaled only,
              never upscaled), height keeps the aspect ratio.
  4 crops     boxes in FRACTIONAL page coordinates {name, x0, y0, x1, y1}, 0 <= x0 < x1 <= 1, so the
              same box works for a PDF, a PNG export or a converted PPTX of any size.
              Pixel box = (round(x0 W), round(y0 H), round(x1 W), round(y1 H)) on the --dpi raster.
              --grid RxC adds R*C equal section tiles named r<i>c<j>.
  5 PPI       PDF: --dpi px per inch of the page as stored in the file. With --print-width-cm the
              effective PPI at print size is W / (print_width_cm / 2.54) for both PDF and raster.
Output: JSON on stdout {"ok", "status", "input", "dpi", "effective_ppi", "full", "crops", "problems"}.
  Each crop: {"name", "box", "px": [w, h], "path", "rel", "md"}; "rel" is relative to the parent of
  --out-dir, so with --out-dir poster_review_<date>/crops a REVIEW.md in poster_review_<date>/ can
  embed it as written in "md".
  Exit 0 = ok, 1 = a crop box was invalid (valid ones still written), 2 = skipped (dependency or
  converter missing, or a Canva URL given; JSON says what to do).
Python >= 3.8. PyMuPDF needed for PDF and office inputs; raster inputs use Pillow, else PyMuPDF.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

RASTER = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".bmp"}
OFFICE = {".pptx", ".ppt", ".odp", ".odg", ".docx", ".doc", ".odt", ".key"}
KEYNOTE_OK = {".pptx", ".ppt", ".key"}


def emit(obj, code):
    print(json.dumps(obj, indent=2))
    sys.exit(code)


def skipped(reason, **extra):
    d = {"ok": None, "status": "skipped", "reason": reason}
    d.update(extra)
    emit(d, 2)


def import_fitz():
    try:
        try:  # PyMuPDF >= 1.24.3 is 'pymupdf'; 'fitz' is the deprecated alias
            import pymupdf as fitz
        except ImportError:
            import fitz
        return fitz
    except ImportError:
        return None


def import_pil():
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None          # posters are legitimately huge
        return Image
    except ImportError:
        return None


def find_soffice():
    cands = [os.environ.get("SOFFICE"), shutil.which("soffice"), shutil.which("libreoffice"),
             "/Applications/LibreOffice.app/Contents/MacOS/soffice"]
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def to_pdf(path, workdir, allow_keynote):
    """Convert an office file to PDF. Return (pdf path, converter) or call skipped()."""
    ext = os.path.splitext(path)[1].lower()
    os.makedirs(workdir, exist_ok=True)
    out = os.path.join(workdir, os.path.splitext(os.path.basename(path))[0] + ".pdf")
    so = find_soffice()
    if so:
        p = subprocess.run([so, "--headless", "--convert-to", "pdf", "--outdir", workdir, path],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
        if p.returncode == 0 and os.path.exists(out):
            return out, "soffice"
    if allow_keynote and sys.platform == "darwin" and ext in KEYNOTE_OK and os.path.isdir("/Applications/Keynote.app"):
        script = ('tell application "Keynote"\n set d to open POSIX file "%s"\n'
                  ' export d to POSIX file "%s" as PDF\n close d saving no\nend tell'
                  % (os.path.abspath(path).replace('"', '\\"'), os.path.abspath(out).replace('"', '\\"')))
        p = subprocess.run(["osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=600)
        if p.returncode == 0 and os.path.exists(out):
            return out, "keynote"
    skipped("no converter for %s: LibreOffice (soffice) not found%s" %
            (ext, "" if ext not in KEYNOTE_OK else " and Keynote unavailable or disabled"),
            todo="Export the poster to PDF from its editor (PowerPoint/Keynote/Impress: File > Export > "
                 "PDF, best quality) and re-run with --poster <file>.pdf; or install LibreOffice.")


def safe_name(s):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("._") or "crop"


def load_boxes(a):
    boxes = []
    if a.crops:
        with open(a.crops, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            data = data.get("crops", [])
        boxes.extend(data)
    if a.grid:
        m = re.match(r"^(\d+)\s*[xX×]\s*(\d+)$", a.grid.strip())
        if not m or int(m.group(1)) < 1 or int(m.group(2)) < 1:
            raise SystemExit("bad --grid %r (use RxC, e.g. 3x2)" % a.grid)
        r, c = int(m.group(1)), int(m.group(2))
        for i in range(r):
            for j in range(c):
                boxes.append({"name": "r%dc%d" % (i + 1, j + 1), "x0": j / float(c), "y0": i / float(r),
                              "x1": (j + 1) / float(c), "y1": (i + 1) / float(r)})
    return boxes


def check_box(b):
    try:
        x0, y0, x1, y1 = (float(b[k]) for k in ("x0", "y0", "x1", "y1"))
    except (KeyError, TypeError, ValueError):
        return None, "box needs numeric x0, y0, x1, y1"
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        return None, "fractions must satisfy 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1"
    return (x0, y0, x1, y1), None


def px_box(f, w, h):
    x0, y0, x1, y1 = f
    return int(round(x0 * w)), int(round(y0 * h)), int(round(x1 * w)), int(round(y1 * h))


class PilImage(object):
    def __init__(self, Image, path):
        self.Image = Image
        im = Image.open(path)
        self.im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        self.w, self.h = self.im.size

    def save_full(self, width, path):
        if width < self.w:
            out = self.im.resize((width, int(round(self.h * width / float(self.w)))), self.Image.LANCZOS)
        else:
            out = self.im
        out.save(path)
        return list(out.size)

    def save_crop(self, box, path):
        c = self.im.crop(box)
        c.save(path)
        return list(c.size)


class FitzImage(object):
    def __init__(self, fitz, pix):
        self.fitz, self.pix = fitz, pix
        self.w, self.h = pix.width, pix.height

    def save_full(self, width, path):
        if width < self.w:
            out = self.fitz.Pixmap(self.pix, width, int(round(self.h * width / float(self.w))), None)
        else:
            out = self.pix
        out.save(path)
        return [out.width, out.height]

    def save_crop(self, box, path):
        r = self.fitz.IRect(*box)
        c = self.fitz.Pixmap(self.pix.colorspace, r, self.pix.alpha)
        c.copy(self.pix, r)
        c.save(path)
        return [c.width, c.height]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--poster", required=True, help="poster file (PDF, PNG/JPG, PPTX/ODP/DOCX/KEY)")
    ap.add_argument("--out-dir", required=True, help="folder for full.png and crops (e.g. poster_review_<date>/crops)")
    ap.add_argument("--page", type=int, default=1, help="PDF page, 1-based")
    ap.add_argument("--dpi", type=float, default=150.0, help="PDF render dpi for crops (default 150)")
    ap.add_argument("--full-width", type=int, default=2000, help="full.png width in px (default 2000)")
    ap.add_argument("--crops", help="JSON list (or {'crops': [...]}) of {name, x0, y0, x1, y1} fractions")
    ap.add_argument("--grid", help="RxC: add R*C equal section tiles r1c1 .. rRcC")
    ap.add_argument("--suffix", default="", help="appended to every crop name, e.g. _before / _after")
    ap.add_argument("--print-width-cm", type=float, help="printed poster width; reports effective PPI at print size")
    ap.add_argument("--no-full", action="store_true", help="do not write full.png")
    ap.add_argument("--no-keynote", action="store_true", help="never fall back to Keynote for PPTX conversion")
    a = ap.parse_args()

    if re.match(r"^https?://", a.poster) or re.match(r"^D[A-Za-z0-9_-]{10}$", a.poster):
        skipped("a Canva design cannot be rendered directly",
                todo="Export it first with the Canva MCP export-design (PDF, pro quality if available, or "
                     "PNG at full size), save the file, and pass it as --poster.")
    if not os.path.isfile(a.poster):
        emit({"ok": False, "status": "error", "reason": "file not found: %s" % a.poster}, 1)

    boxes = load_boxes(a)
    os.makedirs(a.out_dir, exist_ok=True)
    ext = os.path.splitext(a.poster)[1].lower()
    info = {"path": a.poster, "format": ext.lstrip(".")}
    src = a.poster
    if ext in OFFICE:
        if import_fitz() is None:
            skipped("dependency missing: PyMuPDF (pip install pymupdf) needed to render the converted PDF")
        src, conv = to_pdf(a.poster, os.path.join(a.out_dir, "_converted"), not a.no_keynote)
        info.update({"converted_pdf": src, "converter": conv})
        ext = ".pdf"

    full_path = os.path.join(a.out_dir, "full%s.png" % a.suffix)
    res = {"ok": True, "status": "ok", "input": info, "dpi": None, "effective_ppi": None,
           "full": None, "crops": [], "problems": []}

    if ext == ".pdf":
        fitz = import_fitz()
        if fitz is None:
            skipped("dependency missing: PyMuPDF (pip install pymupdf)")
        doc = fitz.open(src)
        page = doc[a.page - 1]
        pw, ph = page.rect.width, page.rect.height
        info.update({"page": a.page, "pages_in_file": len(doc), "page_pt": [round(pw, 3), round(ph, 3)]})
        res["dpi"] = a.dpi
        z = a.dpi / 72.0
        # render the page once at --dpi and cut every crop from that raster, so a crop's px box is
        # exactly round(fraction * W/H), the same rule as for raster inputs
        img = FitzImage(fitz, page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False))
        W, H = img.w, img.h
        res["raster_px"] = [W, H]
        res["effective_ppi"] = {"at_file_size": a.dpi}
        if not a.no_full:
            fz = a.full_width / pw
            pm = page.get_pixmap(matrix=fitz.Matrix(fz, fz), alpha=False)
            pm.save(full_path)
            res["full"] = {"path": full_path, "px": [pm.width, pm.height]}

        def save_crop(box_f, path):
            return img.save_crop(px_box(box_f, W, H), path)
    elif ext in RASTER:
        Image = import_pil()
        if Image is not None:
            img = PilImage(Image, src)
            info["backend"] = "pillow"
        else:
            fitz = import_fitz()
            if fitz is None:
                skipped("dependency missing: Pillow or PyMuPDF (pip install pillow)")
            pix = fitz.Pixmap(src)
            if pix.colorspace and pix.colorspace.n not in (1, 3):
                pix = fitz.Pixmap(fitz.csRGB, pix)
            img = FitzImage(fitz, pix)
            info["backend"] = "pymupdf"
        W, H = img.w, img.h
        info["px"] = [W, H]
        res["raster_px"] = [W, H]
        if not a.no_full:
            res["full"] = {"path": full_path, "px": img.save_full(a.full_width, full_path)}

        def save_crop(box_f, path):
            return img.save_crop(px_box(box_f, W, H), path)
    else:
        emit({"ok": False, "status": "error", "reason": "unsupported format %r" % ext,
              "todo": "export the poster as PDF or PNG and pass that file"}, 1)

    if a.print_width_cm:
        res["effective_ppi"] = dict(res["effective_ppi"] or {})
        res["effective_ppi"]["at_print_size"] = round(W / (a.print_width_cm / 2.54), 1)
        res["effective_ppi"]["print_width_cm"] = a.print_width_cm

    parent = os.path.dirname(os.path.abspath(a.out_dir))
    if res["full"]:
        res["full"]["rel"] = os.path.relpath(os.path.abspath(full_path), parent).replace(os.sep, "/")
    seen = set()
    for b in boxes:
        name = safe_name(str(b.get("name", "crop"))) + a.suffix
        f, err = check_box(b)
        if err or name in seen:
            res["problems"].append({"name": name, "problem": err or "duplicate crop name"})
            continue
        seen.add(name)
        path = os.path.join(a.out_dir, name + ".png")
        px = save_crop(f, path)
        rel = os.path.relpath(os.path.abspath(path), parent).replace(os.sep, "/")
        res["crops"].append({"name": name, "box": [round(v, 6) for v in f], "px": px, "path": path,
                             "rel": rel, "md": "![%s](%s)" % (name, rel)})
    if res["problems"]:
        res["ok"] = False
    emit(res, 1 if res["problems"] else 0)


if __name__ == "__main__":
    main()
