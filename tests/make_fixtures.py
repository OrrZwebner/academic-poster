#!/usr/bin/env python3
"""Generate the synthetic test fixtures into tests/fixtures/ (nothing binary is committed).

Every value here is invented. The expected results that tests/run_tests.py asserts are derived by
hand in the comments below and in tests/README.md, NOT by running the scripts. If a script's output
stops matching, the script is wrong until proven otherwise.

Text fixtures (.tex/.json/.txt) need only the stdlib. PDF fixtures need PyMuPDF; QR images need
OpenCV (cv2.QRCodeEncoder). Whatever cannot be generated is recorded in fixtures/manifest.json and the
dependent tests SKIP.
Python >= 3.8.
"""
import json
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.join(HERE, "fixtures")
MM = 72 / 25.4                      # pt per mm
QR_GOOD = "https://example.org/poster"
QR_WRONG = "https://example.org/wrong"


def w(name, text):
    path = os.path.join(FX, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def wj(name, obj):
    return w(name, json.dumps(obj, ensure_ascii=False, indent=1))


def png(path, width, height, row_fn):
    """Minimal RGB PNG writer (stdlib). row_fn(y) -> bytes of length 3*width."""
    raw = b"".join(b"\x00" + row_fn(y) for y in range(height))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    return path


def solid(width, rgb):
    row = bytes(rgb) * width
    return lambda y: row


def gradient(width):
    # horizontal grey ramp: never a QR code, and not uniform
    row = b"".join(bytes([int(200 * x / max(1, width - 1))] * 3) for x in range(width))
    return lambda y: row


# ---------------------------------------------------------------- text fixtures (stdlib)
def text_fixtures():
    # toy paper, 10 lines; line numbers are 1-based
    tex = [
        r"\section{Introduction}",                                                   # 1
        r"Our setup is simple.",                                                     # 2
        r"We train small models on the cleaned corpus.",                             # 3
        r"Results follow in a later section.",                                       # 4
        r"Accuracy rises to 0.64 (+143.5\%) on 1{,}250 sentences~\citep{doe2020}.",  # 5
        r"We sweep the batch size from 25--2{,}500 samples.",                         # 6
        r"% a comment with 42\% that must be ignored",                               # 7
        r"\section{Conclusion}",                                                     # 8
        r"Smaller is often enough.",                                                 # 9
        r"\end{document}",                                                           # 10
    ]
    w("paper.tex", "\n".join(tex) + "\n")

    # verify_wording PASS case. Hand check:
    #  "We train models on the corpus" is an ordered subsequence of line 3
    #     (we, train, [small], models, on, the, [cleaned], corpus)                    -> pass
    #  "Accuracy rises to 0.64 on 1,250 sentences" vs line 5 after LaTeX normalisation
    #     (\% -> %, {,} -> ",", ~ -> space, \citep{..} dropped)                       -> pass
    #  short: 3 words <= limit 5, cites line 3 (exists, 1..10)                       -> pass
    wj("wording_pass.json", {"meta": {"source_path": "paper.tex"}, "slots": {
        "intro": {"text": "We train models on the corpus",
                  "fragments": [{"text": "We train models on the corpus", "tex_line": 3}]},
        "result": {"text": "Accuracy rises to 0.64 on 1,250 sentences",
                   "fragments": [{"text": "Accuracy rises to 0.64 on 1,250 sentences", "tex_line": 5}]},
        "caption": {"text": "Cleaned corpus models", "fragments": [],
                    "short": {"text": "Cleaned corpus models", "tex_lines": [3]}, "limit": 5}}})

    # verify_wording FAIL case: exactly 1 passing fragment, 1 failing fragment, 1 over-limit short,
    # 1 bad-line short. Hand check:
    #  "We train the corpus models" on line 3 (+/-1: lines 2..4): after "corpus" (last word of line 3)
    #     no "models" follows in lines 3..4 -> FAIL, missing_word = "models"
    #  short "one two three four five six seven" = 7 words > limit 5 -> FAIL
    #  short cites line 99 on a 10-line file -> FAIL, bad_lines = [99]
    #  => fragments_failing = 1, short_failing = 2, exit 1
    #  with --free-wording: fragments skipped; 7 > 5 still fails, the bad line is not checked
    #  => fragments_failing = 0, short_failing = 1, exit 1
    wj("wording_fail.json", {"meta": {"source_path": "paper.tex"}, "slots": {
        "ok_slot": {"text": "We train models on the corpus",
                    "fragments": [{"text": "We train models on the corpus", "tex_line": 3}]},
        "order_slot": {"text": "We train the corpus models",
                       "fragments": [{"text": "We train the corpus models", "tex_line": 3}]},
        "long_short": {"text": "x", "fragments": [],
                       "short": {"text": "one two three four five six seven", "tex_lines": [3]}, "limit": 5},
        "badline_short": {"text": "x", "fragments": [],
                          "short": {"text": "three short words", "tex_lines": [99]}}}})

    # check_claims. Poster numbers: 0.64, 143.5%, 1,250, 42%, 25, 2,500 (6 numbers).
    #  in paper (line 5, 6): 0.64, 143.5%, 1250, 25, 2500 -> 5 PASS
    #  42% appears only in a LaTeX comment (line 7, stripped)              -> 1 FAIL
    #  with claims_registered.json (42% + derivation)                      -> 6 PASS, exit 0
    #  with claims_noderiv.json   (42% without derivation)                 -> still 1 FAIL
    w("poster_text.txt", "Accuracy 0.64 (+143.5%) on 1,250 sentences.\n"
                         "Batch size 25–2,500 samples; 42% fewer tokens.\n")
    wj("claims_registered.json", {"claims": [{"value": "42%", "derivation": "(a-b)/a from a synthetic table"}]})
    wj("claims_noderiv.json", {"claims": [{"value": "42%", "derivation": ""}]})
    # wording-JSON route of check_claims: 2 slots, numbers 0.64 and 1,250 -> 2 PASS
    wj("claims_wording.json", {"slots": {"a": {"text": "rises to 0.64"},
                                         "b": {"short": {"text": "on 1,250 sentences"}}}})

    # render_script_text: two 3-token rows (Latin, Thai) -> counts 3 and 3, ok
    wj("render_ok.json", {"width": 400, "rows": [
        {"label": "Latin", "tokens": ["a", "b", "c"], "expected_count": 3},
        {"label": "Thai", "tokens": ["สวัส", "ดี", "ครับ"], "expected_count": 3}]})
    # a 3-token row asserted to have 4 -> exit 1
    wj("render_bad.json", {"width": 400, "rows": [{"label": "Latin", "tokens": ["a", "b", "c"], "expected_count": 4}]})

    # build_pptx failing spec, page 20 x 10 cm, units cm. Hand check of the 4 problems:
    #  tiny: 12 pt < min_pt 24                                     -> problem 1
    #  low_img: 300 px placed 10 cm wide -> 300 / (10/2.54) = 76.2 PPI < 150 -> problem 2
    #  wide_rect: x 15 + w 10 = 25 cm > page width 20 cm           -> problem 3 (outside the page)
    #  ghost: slot "nope" not in the wording file                  -> problem 4
    wj("pptx_bad_spec.json", {"page": {"width_cm": 20, "height_cm": 10}, "units": "cm",
                              "min_pt": 24, "min_ppi": 150, "elements": [
        {"id": "tiny", "type": "text", "x": 1, "y": 1, "w": 5, "h": 1, "text": "tiny", "size_pt": 12},
        {"id": "low_img", "type": "image", "path": "low_300x150.png", "x": 1, "y": 3, "w": 10, "fit": "width"},
        {"id": "wide_rect", "type": "rect", "x": 15, "y": 1, "w": 10, "h": 1, "fill": "#000000"},
        {"id": "ghost", "type": "text", "x": 1, "y": 8, "w": 5, "h": 1, "slot": "nope"}]})


# ---------------------------------------------------------------- raster fixtures (stdlib)
def raster_fixtures():
    png(os.path.join(FX, "fig_raster.png"), 300, 200, solid(300, (18, 122, 138)))          # 300 x 200
    png(os.path.join(FX, "low_300x150.png"), 300, 150, solid(300, (200, 0, 0)))
    # plan-spec.example.json image: w = 1380 design px = 1380/96 in = 14.375 in.
    # 2760 px wide -> 2760 / 14.375 = 192.0 PPI (>= 150, PASS); fit width -> h = 1380*1380/2760 = 690 px
    png(os.path.join(FX, "pptx_assets", "figs", "example_results.png"), 2760, 1380, solid(2760, (18, 122, 138)))
    png(os.path.join(FX, "img_300.png"), 300, 300, gradient(300))      # 75 PPI in a 4 in box
    png(os.path.join(FX, "img_1200.png"), 1200, 1200, gradient(1200))  # 300 PPI in a 4 in box
    # render_crops: a 1000 x 1400 px raster poster. Crop (0.1, 0.1, 0.6, 0.4) -> px box
    # (100, 140, 600, 560) -> 500 x 420; grid 2x2 -> 500 x 700 tiles; --full-width 500 -> 500 x 700.
    png(os.path.join(FX, "review_poster.png"), 1000, 1400, gradient(1000))
    # an office file that is never opened: only reaches the converter lookup (no soffice -> skipped)
    with open(os.path.join(FX, "review_poster.pptx"), "wb") as fh:
        fh.write(b"PK\x03\x04 placeholder, not a real pptx")


def qr_png(path, text):
    """QR code -> PNG scaled x20 (29 modules incl. quiet zone -> 580 px). Returns False without OpenCV."""
    try:
        import cv2
        q = cv2.QRCodeEncoder.create().encode(text)
    except Exception:
        return False
    n = q.shape[0]
    k = 20

    def row(y):
        return b"".join(bytes([int(q[y // k, x])] * 3) * k for x in range(n))
    png(path, n * k, n * k, row)
    return True


# ---------------------------------------------------------------- PDF fixtures (PyMuPDF)
def pdf_fixtures(manifest):
    try:
        try:  # PyMuPDF >= 1.24.3 is 'pymupdf'; 'fitz' is the deprecated alias
            import pymupdf as fitz
        except ImportError:
            import fitz
    except ImportError:
        manifest["pdf"] = False
        return
    manifest["pdf"] = True
    font = fitz.Font("helv").buffer            # bundled with MuPDF -> embeddable on any OS

    # export_figs: a 4 x 3 in vector figure (288 x 216 pt). Long side 6000 px ->
    # 6000 x round(6000 * 216/288) = 6000 x 4500; aspect 0.75. --placed-cm 25.4 (10 in) -> 600 PPI
    d = fitz.open()
    p = d.new_page(width=288, height=216)
    p.draw_rect(fitz.Rect(20, 20, 268, 196), color=(0, 0, 0), fill=(0.45, 0.35, 0.6), width=2)
    p.insert_text((40, 120), "fig", fontsize=40)
    d.save(os.path.join(FX, "fig_4x3.pdf"))

    qr_ok = qr_png(os.path.join(FX, "qr_good.png"), QR_GOOD)
    qr_png(os.path.join(FX, "qr_wrong.png"), QR_WRONG)
    manifest["qr_generated"] = qr_ok

    # clean.pdf: exact A0 portrait (841 x 1189 mm = 2383.937 x 3370.394 pt), scale s = 1.
    #  image 1200 px in 288 pt (4 in)       -> 300 PPI          PASS
    #  QR 580 px in 144 pt (2 in)           -> 290 PPI, decodes to QR_GOOD   PASS (if decoder present)
    #  text 30 pt / 60 pt, embedded font    -> min 30 pt        PASS; fonts PASS
    #  nearest ink: black rect at x = 20 mm -> left margin 20 mm (+/- 0.6 = 50-dpi pixel + AA) PASS
    d = fitz.open()
    p = d.new_page(width=841 * MM, height=1189 * MM)
    p.insert_font(fontname="F0", fontbuffer=font)
    p.draw_rect(fitz.Rect(20 * MM, 1000, 20 * MM + 100, 1100), color=None, fill=(0, 0, 0))
    p.insert_image(fitz.Rect(600, 400, 888, 688), filename=os.path.join(FX, "img_1200.png"))
    if qr_ok:
        p.insert_image(fitz.Rect(1500, 400, 1644, 544), filename=os.path.join(FX, "qr_good.png"))
    p.insert_text((600, 1500), "Clean poster title", fontsize=60, fontname="F0")
    p.insert_text((600, 1700), "Body text at thirty points", fontsize=30, fontname="F0")
    d.save(os.path.join(FX, "clean.pdf"))

    # defects.pdf: the planted-defect poster for the REVIEW dry run, checked as --size A0.
    #  page 2400 x 3370.394 pt = 846.667 x 1189.0 mm -> size FAIL, delta_w = +5.67 mm, delta_h = 0
    #     (aspect 1.40433 vs 1.41380 differs by 0.0095 > 0.002, so FAIL, not the same-aspect WARN)
    #  scale s = 841 / 846.667 = 0.993307
    #  img_300 in 288 pt (4 in): 300 / (4 * 0.993307) = 75.51 PPI          -> images FAIL (1 below min)
    #  img_1200 in 288 pt:       1200 / (4 * 0.993307) = 302.02 PPI        -> PASS
    #  QR encoding QR_WRONG, expected QR_GOOD                               -> qr FAIL
    #  12 pt text, Base-14 Helvetica (NOT embedded): 12 * 0.993307 = 11.92 pt -> text FAIL, fonts FAIL
    #  30 pt text, embedded: 29.80 pt                                       -> above floor
    #  grey #cccccc text on white: WCAG L = ((0.8+0.055)/1.055)^2.4 = 0.6038,
    #     ratio = 1.05 / (0.6038 + 0.05) = 1.606 < 3.0 (large text)        -> contrast WARN, ratio 1.61
    #  black rect at x = 5 mm (pdf) -> 5 * 0.993307 = 4.97 printed mm      -> margins FAIL on "left" only
    d = fitz.open()
    p = d.new_page(width=2400, height=1189 * MM)
    p.insert_font(fontname="F0", fontbuffer=font)
    p.draw_rect(fitz.Rect(5 * MM, 1000, 5 * MM + 100, 1100), color=None, fill=(0, 0, 0))
    p.insert_image(fitz.Rect(600, 400, 888, 688), filename=os.path.join(FX, "img_300.png"))
    p.insert_image(fitz.Rect(1000, 400, 1288, 688), filename=os.path.join(FX, "img_1200.png"))
    if qr_ok:
        p.insert_image(fitz.Rect(1500, 400, 1644, 544), filename=os.path.join(FX, "qr_wrong.png"))
    p.insert_text((600, 1500), "Tiny footnote text", fontsize=12, fontname="helv")
    p.insert_text((600, 1700), "Body text at thirty points", fontsize=30, fontname="F0")
    p.insert_text((600, 1900), "Pale grey text", fontsize=40, fontname="F0", color=(0.8, 0.8, 0.8))
    d.save(os.path.join(FX, "defects.pdf"))

    # a1_scaled.pdf: A1 portrait (594 x 841 mm) checked as A0. scale = 841/594 = 1.415825; scaled
    # height 841 * 1.415825 = 1190.71 mm, 1.71 mm off 1189 <= max(2*1, 0.0025*1189 = 2.97) -> size WARN.
    # 20 pt text -> 20 * 1.415825 = 28.32 printed pt >= 24 -> text PASS; ok = true (WARN is not FAIL)
    d = fitz.open()
    p = d.new_page(width=594 * MM, height=841 * MM)
    p.insert_font(fontname="F0", fontbuffer=font)
    p.insert_text((400, 1000), "Scaled up for print", fontsize=20, fontname="F0")
    d.save(os.path.join(FX, "a1_scaled.pdf"))

    # review_poster.pdf for render_crops: 720 x 1008 pt (10 x 14 in).
    #  --dpi 150 raster: 720*150/72 x 1008*150/72 = 1500 x 2100 px
    #  full.png at --full-width 2000: 2000 x 2000*1008/720 = 2000 x 2800
    #  crop (0.1, 0.1, 0.6, 0.4): 360 x 302.4 pt -> 750 x 630 px; grid 2x2 tile 360 x 504 pt -> 750 x 1050
    #  --print-width-cm 50.8 (20 in): 1500 / 20 = 75.0 PPI
    d = fitz.open()
    p = d.new_page(width=720, height=1008)
    p.draw_rect(fitz.Rect(72, 100.8, 432, 403.2), color=(0, 0, 0), fill=(0.45, 0.35, 0.6), width=2)
    p.insert_text((100, 700), "Review fixture", fontsize=40)
    d.save(os.path.join(FX, "review_poster.pdf"))


def main():
    os.makedirs(FX, exist_ok=True)
    manifest = {"qr_generated": False}
    text_fixtures()
    raster_fixtures()
    pdf_fixtures(manifest)
    wj("manifest.json", manifest)
    print(json.dumps({"ok": True, "fixtures": FX, "manifest": manifest}))


if __name__ == "__main__":
    main()
