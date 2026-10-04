# Tests

```bash
python3 tests/make_fixtures.py   # writes tests/fixtures/ (generated, git-ignored)
python3 tests/run_tests.py       # stdlib unittest; missing optional deps -> SKIP
```

All fixtures are synthetic. Expected values are derived by hand, never copied from script output;
if a script stops matching them, the script is wrong until proven otherwise.

| Fixture | Script | Expected | Derivation |
|---|---|---|---|
| `wording_fail.json` vs `paper.tex` | verify_wording | fragments_failing 1, short_failing 2, exit 1 | "We train the corpus models": nothing named "models" follows "corpus" in lines 2–4; short of 7 words > limit 5; short cites line 99 of a 10-line file |
| same, `--free-wording` | verify_wording | 0 / 1 | fragments skipped; 7 > 5 remains |
| `poster_text.txt` vs `paper.tex` | check_claims | 6 numbers, 1 FAIL (42%) | 0.64, 143.5%, 1,250, 25, 2,500 are in lines 5–6; 42% exists only in a LaTeX comment |
| `fig_4x3.pdf` (288×216 pt) | export_figs | 6000×4500 px; 600 PPI at 25.4 cm | 6000·216/288 = 4500; 6000 px / 10 in |
| `clean.pdf` (A0) | check_export | all PASS; 300 PPI; left margin 20 mm | 1200 px / 4 in; rect drawn at x = 20 mm |
| `a1_scaled.pdf` as A0 | check_export | size WARN, scale 1.41582, text 28.3 pt | 841/594; 20 pt × 1.41582 |
| `defects.pdf` as A0 | check_export | size, images, text, fonts, qr, margins FAIL; contrast WARN | page 2400 pt = 846.67 mm (Δ +5.67); s = 841/846.67 = 0.99331; 300 px / (4 in · s) = 75.5 PPI; 12 pt · s = 11.9 pt; Base-14 Helvetica not embedded; QR encodes a different URL; rect at 5 mm · s = 4.97 mm; #cccccc on white: L = 0.6038, ratio 1.05/0.6538 = 1.61 |
| `plan-spec.example.json` + `pptx_assets` | build_pptx | 0 problems, 14 shapes | image 2760 px over 1380/96 in = 192 PPI ≥ 150; 34 px × 0.75 = 25.5 pt ≥ 24 |
| `pptx_bad_spec.json` | build_pptx | 4 problems | 12 pt < 24; 300 px / (10/2.54 in) = 76.2 PPI; x 15 + w 10 > 20 cm; slot "nope" absent |
| `render_ok.json` / `render_bad.json` | render_script_text | counts 3, 3 / exit 1 | len(tokens); expected 4 ≠ 3 |
| `review_poster.pdf` (720×1008 pt) | render_crops | raster 1500×2100; full 2000×2800; box (0.1,0.1,0.6,0.4) 750×630; 2×2 tiles 750×1050; 75.0 PPI at 50.8 cm | 720·150/72; 2000·1008/720; round(frac·W/H); 1500 px / 20 in |
| same, `--dpi 72` | render_crops | box 360×302 | px box (72, 101, 432, 403) = round(0.1·720, 0.1·1008, 0.6·720, 0.4·1008) |
| `review_poster.png` (1000×1400 px) | render_crops (Pillow, and PyMuPDF with Pillow blocked) | full 500×700 at `--full-width 500`; box 500×420; tiles 500×700; 100 PPI at 25.4 cm | (100,140,600,560); 1000 px / 10 in |
| `review_poster.pptx` (placeholder) | render_crops `--no-keynote` | exit 2 "skipped" when LibreOffice is absent | no converter |
| `templates/REVIEW-template.md` | — | preview tip → `## Summary` → first `## Nn.` | required order of the notes file |

Tolerances: PPI 0.1, printed pt 0.1, margins 0.6 mm (50-dpi render pixel 0.51 mm plus
anti-aliasing), contrast ratio 0.01.
