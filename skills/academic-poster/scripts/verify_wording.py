#!/usr/bin/env python3
"""Wording traceability check: every poster text slot must come from the paper.

Input : a wording JSON file (see templates/wording.template.json) and the paper source
        (.tex, .txt, or .pdf).
Method: pass 1 - every fragment's words, after normalisation (LaTeX -> Unicode, \\cite/\\ref/
        \\footnote dropped, "..." gaps, case folded), must form an ORDERED SUBSEQUENCE of the words
        of the cited source line +/- WINDOW lines (deletion-only edits).
        pass 2 - every slot's "short" text cites existing source lines and respects its word cap
        (slot "limit", then --limits file, then --default-limit).
Output: JSON on stdout. Exit 0 = all pass, 1 = failures, 2 = source could not be read
        (e.g. a PDF without PyMuPDF and without pdftotext on PATH).

Free-wording mode (--free-wording) skips pass 1 and keeps the word caps.
Python >= 3.8, stdlib only (PyMuPDF optional for PDF sources).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "theta": "θ",
    "lambda": "λ", "mu": "μ", "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "phi": "φ",
    "omega": "ω", "Delta": "Δ", "Gamma": "Γ", "Theta": "Θ", "Lambda": "Λ", "Sigma": "Σ",
    "Phi": "Φ", "Omega": "Ω",
}
SUP = str.maketrans("0123456789,", "⁰¹²³⁴⁵⁶⁷⁸⁹,")


def emit(obj, code):
    print(json.dumps(obj, ensure_ascii=False, indent=1))
    sys.exit(code)


def norm(s):
    """Normalise a LaTeX or plain-text line to lower-case Unicode words."""
    s = re.sub(r"(?<!\\)%.*", "", s)                       # LaTeX comments
    s = re.sub(r"\\textsuperscript\{([^}]*)\}", lambda m: m.group(1).translate(SUP), s)
    s = re.sub(r"\\(citep|citet|citealp|cite|ref|eqref|autoref|cref|Cref|footnote|label|url)\{[^}]*\}", "", s)
    s = re.sub(r"\((Figure|Fig\.|Table|Section|Appendix)~?\s*\)", "", s)
    for name, ch in GREEK.items():
        s = re.sub(r"\\" + name + r"(?![A-Za-z])", ch, s)
    cmds = {"dots": "…", "ldots": "…", "rightarrow": "→", "to": "→", "times": "×", "in": "∈",
            "approx": "≈", "leq": "≤", "geq": "≥", "pm": "±"}
    for name, ch in cmds.items():
        s = re.sub(r"\\" + name + r"(?![A-Za-z])", ch, s)
    reps = [("{,}", ","), (r"\%", "%"), ("~", " "), ("---", "—"), ("--", "–"),
            ("``", "“"), ("''", "”"), ("$", "")]
    for a, b in reps:
        s = s.replace(a, b)
    s = re.sub(r"\\(texttt|textbf|textit|textsc|emph|mathrm|mathbf|text)\{([^}]*)\}", r" \2 ", s)
    s = s.replace("{", " ").replace("}", " ").replace("\\", " ")
    s = re.sub(r"[“”\"‘’]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def words(s):
    return re.findall(r"[\w%|∈→×≈≤≥±+.\-⁰¹²³⁴⁵⁶⁷⁸⁹]+", s)


def read_source(path):
    """Return the source as a list of lines, or raise RuntimeError."""
    low = path.lower()
    if low.endswith(".pdf"):
        try:
            try:  # PyMuPDF >= 1.24.3 is 'pymupdf'; 'fitz' is the deprecated alias
                import pymupdf as fitz
            except ImportError:
                import fitz
            doc = fitz.open(path)
            lines = []
            for page in doc:
                lines.extend(page.get_text("text").splitlines())
            return lines
        except ImportError:
            if shutil.which("pdftotext"):
                out = subprocess.run(["pdftotext", "-layout", path, "-"], stdout=subprocess.PIPE,
                                     check=True).stdout.decode("utf-8", "replace")
                return out.splitlines()
            raise RuntimeError("dependency missing: PyMuPDF (pip install pymupdf) or pdftotext; "
                               "or pass a .txt export of the paper")
    with open(path, encoding="utf-8") as fh:
        return fh.read().splitlines()


def found(frag, line, src, window):
    """Ordered-subsequence test of frag against source lines line-window .. line+window (1-based)."""
    lo, hi = max(0, line - 1 - window), min(len(src), line + window)
    hay = [w.strip(".") for w in words(norm(" ".join(src[lo:hi])))]
    need = [w.strip(".") for w in words(norm(frag).replace("…", " ")) if w.strip(".")]
    i = 0
    for w in need:
        while i < len(hay) and hay[i] != w:
            i += 1
        if i == len(hay):
            return False, w
        i += 1
    return True, ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("wording", help="wording JSON (meta + slots)")
    ap.add_argument("--source", required=True, help="paper source: .tex, .txt or .pdf")
    ap.add_argument("--limits", help="JSON object {slot_key: max_words} (overridden by a slot's own 'limit')")
    ap.add_argument("--default-limit", type=int, default=20, help="word cap when a slot has none (default 20)")
    ap.add_argument("--window", type=int, default=1, help="search the cited line +/- N lines (default 1)")
    ap.add_argument("--free-wording", action="store_true", help="skip traceability, keep word caps")
    a = ap.parse_args()

    try:
        src = read_source(a.source)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as e:
        emit({"ok": None, "status": "skipped", "reason": str(e)}, 2)
    with open(a.wording, encoding="utf-8") as fh:
        slots = json.load(fh).get("slots", {})
    limits = {}
    if a.limits:
        with open(a.limits, encoding="utf-8") as fh:
            limits = json.load(fh)

    results, frag_fail, short_fail = [], 0, 0
    for key, v in slots.items():
        r = {"slot": key, "fragments_ok": True, "missing": []}
        if not a.free_wording:
            for fr in v.get("fragments", []):
                ok, miss = found(fr["text"], int(fr.get("tex_line", fr.get("line", 0))), src, a.window)
                if not ok:
                    frag_fail += 1
                    r["fragments_ok"] = False
                    r["missing"].append({"fragment": fr["text"], "line": fr.get("tex_line", fr.get("line")),
                                         "missing_word": miss})
        sh = v.get("short")
        if sh:
            lim = v.get("limit", limits.get(key, a.default_limit))
            n = len(sh.get("text", "").split())
            cited = sh.get("tex_lines", sh.get("lines", []))
            bad = [ln for ln in cited if not (0 < int(ln) <= len(src))]
            short_ok = n <= lim and (a.free_wording or (bool(cited) and not bad))
            r.update({"short_words": n, "limit": lim, "bad_lines": bad, "short_ok": short_ok})
            if not cited and not a.free_wording:
                r["short_problem"] = "no source lines cited"
            if not short_ok:
                short_fail += 1
        results.append(r)

    ok = frag_fail == 0 and short_fail == 0
    emit({"ok": ok, "mode": "free-wording" if a.free_wording else "paper-fidelity",
          "source_lines": len(src), "slots": len(slots), "fragments_failing": frag_fail,
          "short_failing": short_fail, "results": results}, 0 if ok else 1)


if __name__ == "__main__":
    main()
