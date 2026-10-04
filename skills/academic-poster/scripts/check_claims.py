#!/usr/bin/env python3
"""Claim provenance check: every number printed on the poster must come from the paper.

Input : --poster  wording JSON (slot "text" / "short.text"), a poster PDF, or a .txt of poster text
        --source  the paper: .tex, .txt or .pdf (results CSVs may be passed as extra --source files)
        --registered  optional claims JSON for derived numbers:
                      {"claims": [{"value": "42%", "derivation": "(a-b)/a from results.csv"}]}
Method: extract numeric tokens (integers, decimals, percentages, k/M suffixes; ranges and ratios
        are split into their numbers), normalise them (thousands separators, LaTeX \\% and {,},
        unicode minus), and look each one up in the numbers of the source. A poster token with "%"
        needs a source number followed by "%". A token not in the source passes only if it is
        registered with a non-empty derivation.
Output: JSON on stdout. Exit 0 = all numbers traced, 1 = untraced numbers, 2 = a file could not be read.
Python >= 3.8, stdlib only (PyMuPDF optional for PDF inputs).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys

NUM = re.compile(r"(?<![A-Za-z\d.,])[+\-−]?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s?(%|[kKM](?![A-Za-z]))?")


def emit(obj, code):
    print(json.dumps(obj, ensure_ascii=False, indent=1))
    sys.exit(code)


def read_text(path):
    low = path.lower()
    if low.endswith(".pdf"):
        try:
            try:  # PyMuPDF >= 1.24.3 is 'pymupdf'; 'fitz' is the deprecated alias
                import pymupdf as fitz
            except ImportError:
                import fitz
            return "\n".join(p.get_text("text") for p in fitz.open(path))
        except ImportError:
            if shutil.which("pdftotext"):
                return subprocess.run(["pdftotext", path, "-"], stdout=subprocess.PIPE,
                                      check=True).stdout.decode("utf-8", "replace")
            raise RuntimeError("dependency missing: PyMuPDF (pip install pymupdf) or pdftotext")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def clean_latex(s):
    s = re.sub(r"(?<!\\)%.*", "", s)          # comments (keeps \%)
    return s.replace("{,}", ",").replace(r"\%", "%").replace("$", " ").replace("~", " ")


def numbers(text):
    """Return list of (raw, key) where key is the normalised number, e.g. '1250', '143.5%', '100k'."""
    out = []
    for m in NUM.finditer(text.replace("−", "-").replace(" ", " ")):
        integer, frac, suf = m.group(1), m.group(2) or "", (m.group(3) or "").lower()
        key = integer.replace(",", "") + frac + suf
        out.append((m.group(0).strip(), key))
    return out


def poster_texts(path):
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            slots = json.load(fh).get("slots", {})
        res = []
        for k, v in slots.items():
            t = v.get("text") or (v.get("short") or {}).get("text", "")
            res.append((k, t))
        return res
    return [("poster", read_text(path))]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--poster", required=True, help="wording JSON, poster PDF, or poster .txt")
    ap.add_argument("--source", required=True, action="append", help="paper .tex/.txt/.pdf (repeatable)")
    ap.add_argument("--registered", help="claims JSON for derived numbers")
    ap.add_argument("--ignore", default="", help="comma-separated tokens to skip, e.g. '2026,1,2,3'")
    a = ap.parse_args()

    try:
        src = " ".join(clean_latex(read_text(p)) for p in a.source)
        texts = poster_texts(a.poster)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
        emit({"ok": None, "status": "skipped", "reason": str(e)}, 2)

    have = set(k for _, k in numbers(src))
    registered = {}
    if a.registered:
        with open(a.registered, encoding="utf-8") as fh:
            for c in json.load(fh).get("claims", []):
                registered[numbers(c["value"])[0][1] if numbers(c["value"]) else c["value"]] = c
    ignore = set(x.strip() for x in a.ignore.split(",") if x.strip())

    checks, fails = [], 0
    for where, text in texts:
        for raw, key in numbers(text):
            if raw in ignore or key in ignore:
                continue
            if key in have:
                status, how = "PASS", "found in source"
            elif key in registered and registered[key].get("derivation"):
                status, how = "PASS", "registered: " + registered[key]["derivation"]
            else:
                status, how = "FAIL", "not in source and not registered"
                fails += 1
            checks.append({"where": where, "value": raw, "normalised": key, "status": status, "how": how})

    emit({"ok": fails == 0, "numbers_checked": len(checks), "failing": fails, "checks": checks},
         0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
