# Layout and typography defaults

Load this in PLAN (new layout, new section, resize) and in REVIEW (design lens). Values are defaults;
the poster rules file overrides them.

## Canvas sizes (F1: px = cm / 2.54 × 96)

| Print size | mm | Design px at 96 px/in | Aspect h/w |
|---|---|---|---|
| A0 | 841 × 1189 | 3178 × 4494 | 1.414 |
| A1 | 594 × 841 | 2245 × 3178 | 1.416 |
| 36 × 48 in | 914 × 1219 | 3456 × 4608 | 1.333 |

A0 was observed in Canva as 3178 × 4494 px; a ±1 px rounding difference is harmless.
Always take the size from the venue's official rules (quote them, with URL and access date) — not
from memory or from last year.

## Type scale (design px at print size; 1 pt = 1.333 px)

| Role | Default px | ≈ pt | Rule-of-thumb range (poster guides) |
|---|---|---|---|
| Title | 110–120 bold | 83–90 | 72–92 pt |
| Subtitle | 64–68 | 48–51 | — |
| Authors | 44–52 | 33–39 | — |
| Section heading | 64–70 bold | 48–53 | 36–54 pt |
| Sub-heading / research question | 48–60 bold | 36–45 | — |
| Body | 36–42 | 27–32 | 24–36 pt |
| Captions | 34 | 25.5 | ≥ 18 pt in guides; this skill's floor applies |
| **Floor (all text, incl. inside figures)** | **32** | **24** | configurable; exceptions logged |

## Layout rules

- **Safe margin:** ink ≥ 10 mm from every edge (≈ 38 px) — a print-shop convention, not a venue rule;
  confirm bleed needs with the print shop (if needed: 3 mm bleed + crop marks, extend full-width rules).
- **Grid:** equal gutters (≈ 32–76 px), equal box widths per column, one box style per role.
- **Reading order:** one obvious path (columns or Z-flow); numbered section markers must equal RQ
  numbers; do not duplicate a symbol and a word ("RQ" badge + "RQ1:").
- **Text budget:** about 300–800 words (poster guides); state the count in reviews.
- **Figures:** minimum width per role (decide in the rules file; dense heatmaps need the most); cap
  dense figures (e.g. ≤ 2 heatmaps); plot pairs centred with an equal gap; never distort (F7); never add
  a derived plot that is not in the paper.
- **Captions:** one line, directly under the plot, plot width, centred, muted grey.
- **Header:** title, subtitle, authors (affiliations optional); a light header reads better than a dark
  band in most venues — ask.
- **Footer:** logos only, same width as content; use official logo files and any lockup a funder
  requires; acknowledgement text when the funder requires it.
- **Colour semantics:** colours that encode data (e.g. one per language or method) are reserved for
  that meaning; decorative borders go neutral grey; text in a light data colour needs a darker variant
  for contrast (WCAG ≥ 4.5:1 normal text, ≥ 3:1 large text ≥ 18 pt or ≥ 14 pt bold).
- **10-second path:** the opening question and the main answer should be visually linked (same fill
  or style), so a passer-by sees question → answer.
- **Space reclaim order** when content does not fit: shrink non-key figures (never below minimum) →
  tighten gaps → never drop required content → report the compromise as an OPEN DECISION.

## Second print size (dual venue)

1. Compare aspect ratios (3:4 vs 1:√2). One file serves both only if the larger board fits.
2. Canva `resize-design` needs quota (Pro) and was observed to shift blocks: after any resize, re-place
   every element at source × s (F6), restore text and key figure widths to their minimums, and allocate
   the spare height in a table that sums exactly.
3. Free plan: start from a design already at the target size or copy an already-sized page.
4. Element-by-element rebuild is the last resort (it loses fonts and some media).
5. Verify the new PDF with `check_export.py --size <new size>`.
