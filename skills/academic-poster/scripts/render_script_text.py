#!/usr/bin/env python3
"""Render text in any script (Arabic, Thai, Bengali, CJK, ...) as token chips or plain lines.

Why: matplotlib and most image tools do not shape complex scripts (Arabic joining, Thai
vowel and tone marks, Bengali conjuncts). A browser does. This script writes an HTML page and screenshots it with
headless Chromium (Playwright) at a high device scale factor.

Input : a spec JSON:
  {"width": 2000, "background": "#ffffff", "chip_px": 32, "label_px": 34,
   "rows": [{"label": "English", "color": "#222831", "tint": "#e8ecee",
             "font_stack": "'Noto Sans', Arial",
             "tokens": ["The", " cat"],          # token chips, OR
             "text": "a plain line",             # one plain text line
             "expected_count": 2}]}             # optional assertion on len(tokens)
  With --tokenizer NAME, rows that have "text" but no "tokens" are tokenized with Hugging Face
  transformers (optional dependency) and drawn as chips.
Output: PNG (and the HTML next to it). JSON on stdout: {"ok", "png", "html", "px", "rows": [...]}.
  Exit 0 = ok, 1 = a count assertion failed, 2 = a dependency is missing (the HTML is still written,
  so you can open it in a browser and screenshot it by hand).
Python >= 3.8. Optional: playwright (+ `playwright install chromium`), transformers.
"""
import argparse
import html
import json
import os
import sys


def build_html(spec, rows):
    chip, lab = spec.get("chip_px", 32), spec.get("label_px", 34)
    parts = []
    for r in rows:
        c, tint = r.get("color", "#222831"), r.get("tint", "#f2f2f2")
        font = r.get("font_stack", "'Noto Sans', Arial, sans-serif")
        count = " <span class='n'>(%d)</span>" % len(r["tokens"]) if r.get("tokens") is not None and r.get("show_count", True) else ""
        if r.get("tokens") is not None:
            body = "".join("<span class='chip' style='background:%s;border-color:%s'>%s</span>"
                           % (tint, c, html.escape(t if t.strip() else "␣")) for t in r["tokens"])
        else:
            body = "<span class='line'>%s</span>" % html.escape(r.get("text", ""))
        parts.append("<div class='row' style='border-left-color:%s'><div class='lab' style='color:%s'>%s%s</div>"
                     "<div class='chips' style=\"font-family:%s\">%s</div></div>"
                     % (c, c, html.escape(r.get("label", "")), count, font, body))
    return ("<html><head><meta charset='utf-8'><style>"
            "body{margin:0;background:%s;width:%dpx;font-family:Arial,sans-serif}"
            ".wrap{padding:10px 16px}"
            ".row{border-left:14px solid;padding:14px 18px;margin:12px 0;background:#fafafa;border-radius:8px}"
            ".lab{font-weight:700;font-size:%dpx;margin-bottom:10px}.lab .n{font-weight:500;color:#646c78}"
            ".chips{display:flex;flex-wrap:wrap;gap:7px;line-height:1.6}"
            ".chip{border:2px solid;border-radius:8px;padding:6px 9px;font-size:%dpx}"
            ".line{font-size:%dpx}"
            "</style></head><body><div class='wrap'>%s</div></body></html>"
            % (spec.get("background", "#ffffff"), spec.get("width", 2000), lab, chip, chip, "".join(parts)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="spec JSON")
    ap.add_argument("--out", required=True, help="output PNG path")
    ap.add_argument("--width", type=int, help="page width in CSS px (overrides spec)")
    ap.add_argument("--dpr", type=float, default=3.0, help="device scale factor (default 3)")
    ap.add_argument("--tokenizer", help="Hugging Face tokenizer name for rows given as text")
    ap.add_argument("--html-only", action="store_true", help="write the HTML, skip the screenshot")
    a = ap.parse_args()

    with open(a.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    if a.width:
        spec["width"] = a.width
    rows = spec.get("rows", [])

    if a.tokenizer and any(r.get("tokens") is None and r.get("text") for r in rows):
        try:
            from transformers import AutoTokenizer
        except ImportError:
            print(json.dumps({"ok": None, "status": "skipped",
                              "reason": "dependency missing: transformers (pip install transformers)"}))
            sys.exit(2)
        tok = AutoTokenizer.from_pretrained(a.tokenizer)
        for r in rows:
            if r.get("tokens") is None and r.get("text"):
                ids = tok(r["text"], add_special_tokens=False).input_ids
                r["tokens"] = [p.replace("▁", " ").replace("Ġ", " ") for p in tok.convert_ids_to_tokens(ids)]

    report, bad = [], 0
    for r in rows:
        n = len(r["tokens"]) if r.get("tokens") is not None else None
        exp = r.get("expected_count")
        ok = exp is None or n == exp
        bad += not ok
        report.append({"label": r.get("label"), "count": n, "expected": exp, "ok": ok})

    out_html = os.path.splitext(a.out)[0] + ".html"
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as fh:
        fh.write(build_html(spec, rows))
    res = {"ok": bad == 0, "html": out_html, "png": None, "px": None, "rows": report}

    if not a.html_only:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            res.update({"ok": False if bad else None, "status": "skipped",
                        "reason": "dependency missing: playwright (pip install playwright && "
                                  "playwright install chromium); open the HTML and screenshot it by hand"})
            print(json.dumps(res, ensure_ascii=False, indent=1))
            sys.exit(1 if bad else 2)
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(device_scale_factor=a.dpr)
            pg.set_content(open(out_html, encoding="utf-8").read())
            pg.wait_for_timeout(300)
            pg.locator(".wrap").screenshot(path=a.out, omit_background=spec.get("background") == "transparent")
            box = pg.locator(".wrap").bounding_box()
            b.close()
        res["png"] = a.out
        res["px"] = [int(round(box["width"] * a.dpr)), int(round(box["height"] * a.dpr))]

    print(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
