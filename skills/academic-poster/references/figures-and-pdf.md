# Figures, PDFs and print resolution (FIGURES mode; also used by VERIFY and REVIEW)

Load this when exporting, re-plotting, uploading or checking figures, when the paper arrives as a PDF,
or when sample text uses a non-Latin script.

## Formulas

| ID | Formula | Check |
|---|---|---|
| F1 px ↔ cm | Canva custom sizes are 96 px/in: `px = cm / 2.54 × 96` (1 cm = 37.795 px). A0 841 × 1189 mm → 3178 × 4494 px; 36 × 48 in → 3456 × 4608 px | PDF page `cm = pt / 72 × 2.54`; tolerance ± 1 mm |
| F2 effective PPI | `PPI = image_px / (placed_cm / 2.54)`; with a design at print size `PPI = image_px_w / (placed_w_px / 96)`. Required source px = `placed_cm / 2.54 × PPI` | `check_export.py` images check |
| F3 pt ↔ px | `px = pt × 96 / 72 = pt × 1.333`; 24 pt = 32 px | PDF span sizes |
| F4 print-scale text | `s = print_width / design_width`; `printed_pt = design_px × 0.75 × s` | `check_export.py` text check (uses s automatically) |
| F5 re-plot font size | at `dpi = 200`, `figsize = frame_px / 100` in → PNG = 2 × frame px; poster text px = `size_pt × 100/72 × s`; choose `size_pt ≥ (floor_px + margin_px) / (1.3889 × s)` | PNG h/w within ± 0.2% of the frame h/w |
| F7 aspect lock | `h = w × px_h / px_w` | returned geometry |

Worked example (synthetic): a figure placed 40 cm wide needs `40 / 2.54 × 150 = 2362 px` for 150 PPI
and 4724 px for 300 PPI. A 6000 px export gives 150 PPI up to `6000 / 150 × 2.54 = 101.6 cm`.

## Procedure

1. **Inventory.** Build a map `poster figure → source file (vector PDF preferred) → generating script`
   and add each to the media map.
2. **Export.** Vector PDF → PNG with long side 6000 px:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/academic-poster/scripts/export_figs.py figures/*.pdf --out assets/figs [--svg] [--placed-cm 40]
   ```
   `--svg` also writes SVG with text as paths (sharp in Canva if the account accepts SVG uploads).
   For raster-only sources use the largest original; a newer, sharper raster beats an older PDF.
3. **PPI table.** For every figure compute PPI at its placed size (F2). Floor 150 PPI; some venues
   state 300 dpi as "ideal" — report it as BELOW IDEAL, not FAIL, unless the venue requires it.
4. **Text inside figures.** Estimate printed size (F4): measure a capital letter in a crop of the
   placed figure. If it is below the floor (default 24 pt for ALL text, configurable), prefer a
   poster-mode re-plot (below) over upscaling. Without the plotting scripts, report it and log it as an
   accepted exception if the author agrees.
5. **Non-Latin scripts.** Never render Arabic, Thai, Bengali or CJK sample text with matplotlib
   (no shaping of stacks, conjuncts or joining). Use the browser renderer:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/academic-poster/scripts/render_script_text.py rows.json --out assets/figs/sample.png --dpr 3
   ```
   Give `expected_count` per row when the poster states a count (e.g. tokens per sentence) — the
   script fails if the rendered chips disagree. Re-derive any such number from the paper or by
   re-running the tokenizer; a slide or older poster is not a source. Dotted circles (◌) on isolated
   combining marks are the standard U+25CC rendering, not missing glyphs.
6. **Upload** (Canva route): `create-upload-url` or `upload-asset-from-url`; record `media_id` + px.
   PPTX route: reference the PNG path in the plan spec.
7. **Export quality decides the printed PPI.** In Canva, export pro quality or "PDF Print"; then run
   `check_export.py`.

## Poster-mode re-plot prompt (for whoever has the plotting scripts)

Use when in-figure text is below the floor or tick labels collide. Default scope (from experience):
**same plots, bigger text only** — changing axes, labels or legends away from the paper's figures was
rejected. Hand this block to the machine/session that has the scripts, filled in:

```
Goal: poster versions of <N> paper figures; the paper figures must not change.
Hard rules:
- Record md5 of every paper output first; re-check at the end — they must be identical.
- Back up each script; add a --poster flag (or X_poster.py copy). A run without the flag is byte-identical.
- Presentation only: figsize, font sizes, tick density, legend placement, output names.
  Never change data, filtering, computation, palette, colormap, vmin/vmax.
- figsize = frame_px / 100 in, dpi 200, no bbox_inches="tight"; h/w within ±0.2% of the frame;
  save vector PDF (pdf.fonttype 42) + PNG to <new folder>, names ending _poster.
- Font size for all text = <size_pt from F5> pt; heatmap cell text: largest size that fits 90% of the
  cell width, measured with get_window_extent after canvas.draw().
- After drawing, check tick-label and legend overlaps; apply fallbacks in this order: <…>; report which.
- If anything cannot be done as written, stop and report. No substitute design choices.
Per figure: <ID · paper output · script · frame w×h px · scale s · size_pt>.
Numbers to assert: <values copied from the result files that must appear in the plot>.
Report: md5 before/after, outputs, PNG sizes and h/w, overlap results, fallbacks used.
```

## Papers given as PDF (no .tex)

`verify_wording.py` and `check_claims.py` accept a PDF source: text is extracted with PyMuPDF (or
`pdftotext`), and line numbers refer to the extraction order — cite them as "page p, extracted line n".
Hyphenation and two-column extraction can split words: if a fragment fails only because of a
line-break hyphen, cite both lines (raise `--window`) rather than editing the wording. (PDF-mode
traceability was not exercised in the source project; treat failures with care.)
