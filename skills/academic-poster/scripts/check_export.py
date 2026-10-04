#!/usr/bin/env python3
"""Print preflight for a poster PDF.

Input : the exported poster PDF and the target print size.
Method: scale s = target width / page width (1.0 when the PDF is already at print size).
  1 size      page mm = pt / 72 * 25.4, compared with the target (+/- --tol-mm), orientation-aware
  2 images    effective PPI = image px / (placed pt / 72 * s); FAIL < --min-ppi, WARN < --ideal-ppi
  3 text      printed pt = span size * s; FAIL < --min-pt (text inside raster figures is NOT seen)
  4 fonts     embedded (not "n/a") and no Type3
  5 qr        decode embedded images and a page render; compare with --qr-url
              (needs OpenCV or pyzbar+Pillow; otherwise SKIPPED)
  6 margins   render at 50 dpi; first non-white pixel (sum |RGB-255| > 30) from each edge, in
              printed mm; FAIL < --safe-mm
  7 contrast  (--contrast) WCAG 2.x ratio of each span colour vs the modal background pixel in its
              bbox; WARN < 4.5 (normal) or < 3.0 (large: >= 18 pt, or >= 14 pt bold)
Output: JSON on stdout {"ok", "file", "scale", "checks": [{"id","status","detail",...}]}.
  status per check: PASS | WARN | FAIL | SKIPPED. Exit 0 = no FAIL, 1 = any FAIL,
  2 = PyMuPDF missing (pip install pymupdf).
Sizes: A0..A4, "70x100cm", "841x1189mm", "36x48in".
Python >= 3.8; PyMuPDF required; OpenCV (opencv-python) or pyzbar+Pillow optional for the QR check.
"""
import argparse
import collections
import json
import os
import re
import sys

ISO = {"A0": (841, 1189), "A1": (594, 841), "A2": (420, 594), "A3": (297, 420), "A4": (210, 297)}


def parse_size(s):
    s = s.strip()
    if s.upper() in ISO:
        return ISO[s.upper()]
    m = re.match(r"^([\d.]+)\s*[x×]\s*([\d.]+)\s*(mm|cm|in)$", s, re.I)
    if not m:
        raise SystemExit("bad --size %r (use A0..A4, 70x100cm, 841x1189mm, 36x48in)" % s)
    f = {"mm": 1.0, "cm": 10.0, "in": 25.4}[m.group(3).lower()]
    return float(m.group(1)) * f, float(m.group(2)) * f


def luminance(rgb):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def decode_qr(samples, w, h, n):
    """Return (decoded strings, backend) or (None, reason)."""
    try:
        import numpy as np
        import cv2
        arr = np.frombuffer(samples, dtype=np.uint8).reshape(h, w, n)[:, :, :3]
        det = cv2.QRCodeDetector()
        try:
            ok, texts, _, _ = det.detectAndDecodeMulti(arr)
            texts = [t for t in (texts if ok else []) if t]
        except Exception:
            t, _, _ = det.detectAndDecode(arr)
            texts = [t] if t else []
        return texts, "opencv"
    except ImportError:
        pass
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
        img = Image.frombytes("RGB" if n == 3 else "RGBA", (w, h), samples)
        return [d.data.decode("utf-8", "replace") for d in decode(img)], "pyzbar"
    except ImportError:
        return None, "dependency missing: opencv-python or pyzbar+Pillow"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--size", required=True, help="target print size: A0..A4, 70x100cm, WxHmm, WxHin")
    ap.add_argument("--orientation", choices=["portrait", "landscape"], default="portrait")
    ap.add_argument("--page", type=int, default=1, help="page to check, 1-based")
    ap.add_argument("--tol-mm", type=float, default=1.0)
    ap.add_argument("--min-ppi", type=float, default=150.0)
    ap.add_argument("--ideal-ppi", type=float, default=0.0, help="WARN below this (e.g. a venue's 300); 0 = off")
    ap.add_argument("--min-pt", type=float, default=24.0, help="text floor in printed pt (default 24)")
    ap.add_argument("--qr-url", help="expected QR content; enables the QR check")
    ap.add_argument("--qr-dpi", type=float, default=100.0, help="page render dpi for QR decoding")
    ap.add_argument("--safe-mm", type=float, default=10.0, help="ink-to-edge safe margin (default 10)")
    ap.add_argument("--contrast", action="store_true", help="run the WCAG contrast check")
    ap.add_argument("--crops", help="folder for crops of failing images and spans (150 dpi printed)")
    a = ap.parse_args()

    try:
        try:  # PyMuPDF >= 1.24.3 is 'pymupdf'; 'fitz' is the deprecated alias
            import pymupdf as fitz
        except ImportError:
            import fitz
    except ImportError:
        print(json.dumps({"ok": None, "status": "skipped",
                          "reason": "dependency missing: PyMuPDF (pip install pymupdf)"}))
        sys.exit(2)

    doc = fitz.open(a.pdf)
    page = doc[a.page - 1]
    tw, th = parse_size(a.size)
    tw, th = (min(tw, th), max(tw, th)) if a.orientation == "portrait" else (max(tw, th), min(tw, th))
    pw_mm, ph_mm = page.rect.width / 72 * 25.4, page.rect.height / 72 * 25.4
    s = tw / pw_mm
    checks = []
    if a.crops:
        os.makedirs(a.crops, exist_ok=True)

    def crop(rect, name):
        if not a.crops:
            return None
        z = 150.0 / 72 * s
        path = os.path.join(a.crops, name + ".png")
        page.get_pixmap(matrix=fitz.Matrix(z, z), clip=rect + (-20, -20, 20, 20), alpha=False).save(path)
        return path

    # 1 size
    dw, dh = pw_mm - tw, ph_mm - th
    st = "PASS" if abs(dw) <= a.tol_mm and abs(dh) <= a.tol_mm else "FAIL"
    detail = {"page_mm": [round(pw_mm, 2), round(ph_mm, 2)], "target_mm": [tw, th],
              "delta_mm": [round(dw, 2), round(dh, 2)], "pages_in_file": len(doc)}
    # Same aspect ratio -> WARN (scaled to print). ISO A sizes are rounded to whole mm, so A1 scaled to
    # A0 lands 1.7 mm off in height (841/594*841 = 1190.7 vs 1189): allow max(2*tol, 0.25% of height).
    if st == "FAIL" and abs(ph_mm * s - th) <= max(2 * a.tol_mm, 0.0025 * th):
        st, detail["note"] = ("WARN", "same aspect ratio; PDF will be scaled by %.4f to print "
                              "(scaled height off by %.1f mm)" % (s, ph_mm * s - th))
    checks.append({"id": "size", "status": st, "detail": detail})

    # 2 images
    imgs, bad, low = [], 0, 0
    for i, info in enumerate(page.get_image_info(xrefs=True)):
        x0, y0, x1, y1 = info["bbox"]
        if x1 - x0 <= 0 or y1 - y0 <= 0:
            continue
        ppi = min(info["width"] / ((x1 - x0) / 72 * s), info["height"] / ((y1 - y0) / 72 * s))
        stt = "FAIL" if ppi < a.min_ppi else ("WARN" if a.ideal_ppi and ppi < a.ideal_ppi else "PASS")
        rec = {"index": i, "px": [info["width"], info["height"]],
               "placed_mm": [round((x1 - x0) / 72 * 25.4 * s, 1), round((y1 - y0) / 72 * 25.4 * s, 1)],
               "ppi": round(ppi, 1), "status": stt}
        if stt == "FAIL":
            bad += 1
            rec["crop"] = crop(fitz.Rect(info["bbox"]), "img_%02d_%dppi" % (i, round(ppi)))
        low += stt == "WARN"
        imgs.append(rec)
    checks.append({"id": "images", "status": "FAIL" if bad else ("WARN" if low else "PASS"),
                   "detail": {"count": len(imgs), "below_min": bad, "below_ideal": low,
                              "min_ppi": min([r["ppi"] for r in imgs]) if imgs else None, "images": imgs}})

    # 3 text sizes (+ collect spans for contrast)
    spans, small = [], []
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for sp in line["spans"]:
                if not sp["text"].strip():
                    continue
                pt = sp["size"] * s
                spans.append(sp)
                if pt < a.min_pt - 0.05:
                    small.append({"text": sp["text"][:60], "printed_pt": round(pt, 1), "font": sp["font"],
                                  "crop": crop(fitz.Rect(sp["bbox"]), "span_%02d_%dpt" % (len(small), round(pt)))})
    sizes = sorted(round(sp["size"] * s, 1) for sp in spans)
    checks.append({"id": "text", "status": "FAIL" if small else "PASS",
                   "detail": {"spans": len(spans), "min_pt": sizes[0] if sizes else None,
                              "median_pt": sizes[len(sizes) // 2] if sizes else None,
                              "max_pt": sizes[-1] if sizes else None, "below_floor": small,
                              "note": "text inside raster images is not measured; check it visually"}})

    # 4 fonts
    fonts, fbad = [], []
    for xref, ext, ftype, base, name, enc in [f[:6] for f in page.get_fonts(full=False)]:
        rec = {"font": base, "type": ftype, "embedded": ext != "n/a"}
        fonts.append(rec)
        if ext == "n/a" or ftype == "Type3":
            fbad.append(rec)
    checks.append({"id": "fonts", "status": "FAIL" if fbad else "PASS",
                   "detail": {"fonts": fonts, "problems": fbad}})

    # 5 QR
    if a.qr_url:
        found, backend = [], None
        for info in page.get_image_info(xrefs=True):
            if info.get("xref") and abs(info["width"] - info["height"]) <= 0.05 * info["width"]:
                pix = fitz.Pixmap(doc, info["xref"])
                if pix.n - pix.alpha != 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                if pix.alpha:
                    pix = fitz.Pixmap(pix, 0)
                texts, backend = decode_qr(pix.samples, pix.width, pix.height, pix.n)
                if texts is None:
                    break
                found += texts
        if backend is None or (found == [] and not str(backend).startswith("dependency")):
            z = a.qr_dpi / 72
            pix = page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
            texts, backend = decode_qr(pix.samples, pix.width, pix.height, pix.n)
            if texts:
                found += texts
        if texts is None and not found:
            checks.append({"id": "qr", "status": "SKIPPED", "detail": {"reason": backend}})
        else:
            st = "PASS" if a.qr_url in found else "FAIL"
            checks.append({"id": "qr", "status": st, "detail": {"decoded": sorted(set(found)),
                                                                 "expected": a.qr_url, "backend": backend,
                                                                 "reminder": "phone-scan the printed proof"}})

    # 6 safe margins (ink-to-edge)
    dpi = 50.0
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    w, h, n, smp = pix.width, pix.height, pix.n, pix.samples
    stride = w * n

    def ink(px):
        return (765 - px[0] - px[1] - px[2]) > 30

    def row_has_ink(y):
        row = smp[y * stride:(y + 1) * stride]
        if min(row) >= 245:
            return False
        return any(ink(row[i:i + 3]) for i in range(0, len(row), n))

    def col_has_ink(x):
        chans = [smp[x * n + c::stride] for c in range(3)]
        if min(min(c) for c in chans) >= 245:
            return False
        return any((765 - chans[0][y] - chans[1][y] - chans[2][y]) > 30 for y in range(h))

    def first(rng, test):
        for k, v in enumerate(rng):
            if test(v):
                return k
        return None

    mm_per_px = 25.4 / dpi * s
    edges = {"top": first(range(h), row_has_ink), "bottom": first(range(h - 1, -1, -1), row_has_ink),
             "left": first(range(w), col_has_ink), "right": first(range(w - 1, -1, -1), col_has_ink)}
    edges_mm = {k: (round(v * mm_per_px, 1) if v is not None else None) for k, v in edges.items()}
    close = {k: v for k, v in edges_mm.items() if v is not None and v < a.safe_mm}
    checks.append({"id": "margins", "status": "FAIL" if close else "PASS",
                   "detail": {"ink_to_edge_mm": edges_mm, "safe_mm": a.safe_mm, "too_close": close,
                              "resolution_mm": round(mm_per_px, 2),
                              "note": "full-width rules/backgrounds touching the edge need bleed; ask the print shop"}})

    # 7 contrast
    if a.contrast:
        rows = []
        cz = 72 / 72.0
        cpix = page.get_pixmap(matrix=fitz.Matrix(cz, cz), alpha=False)
        cw, chh, cn, cs = cpix.width, cpix.height, cpix.n, cpix.samples
        for sp in spans:
            x0, y0, x1, y1 = [int(round(v * cz)) for v in sp["bbox"]]
            cnt = collections.Counter()
            for y in range(max(0, y0), min(chh, y1)):
                for x in range(max(0, x0), min(cw, x1)):
                    o = (y * cw + x) * cn
                    cnt[(cs[o], cs[o + 1], cs[o + 2])] += 1
            if not cnt:
                continue
            bg = cnt.most_common(1)[0][0]
            c = sp["color"]
            fg = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
            r = contrast(fg, bg)
            pt = sp["size"] * s
            bold = "bold" in sp["font"].lower() or bool(sp["flags"] & 16)
            need = 3.0 if (pt >= 18 or (bold and pt >= 14)) else 4.5
            if r < need:
                rows.append({"text": sp["text"][:60], "fg": "#%02x%02x%02x" % fg, "bg": "#%02x%02x%02x" % bg,
                             "ratio": round(r, 2), "needs": need})
        checks.append({"id": "contrast", "status": "WARN" if rows else "PASS",
                       "detail": {"low_contrast": rows,
                                  "method": "WCAG 2.x; background = modal pixel in span bbox"}})

    ok = not any(c["status"] == "FAIL" for c in checks)
    print(json.dumps({"ok": ok, "file": a.pdf, "scale": round(s, 5), "checks": checks},
                     ensure_ascii=False, indent=1))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
