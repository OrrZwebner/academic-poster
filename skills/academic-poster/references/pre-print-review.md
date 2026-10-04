# Pre-print review (REVIEW mode — any existing poster, read-only)

Load this in REVIEW mode and in every `poster-review-visitor-lens` agent. Works on any poster in any
format — PDF, Canva design, PPTX/ODP/Keynote, PNG/JPG — built with this skill or not. Never edits the
poster or the paper.

## Default deliverable: ONE Markdown notes file
```
poster_review_<YYYY-MM-DD>/
├── REVIEW.md          the deliverable (templates/REVIEW-template.md)
├── crops/full.png     full poster, ~2000 px wide
├── crops/<id>.png     one crop per finding (n1.png …; n2_before.png / n2_after.png when a fix was applied)
└── 01_visitor.md …    optional lens appendices, linked from REVIEW.md
```
`REVIEW.md` order: a line telling the reader to open it in a **Markdown preview** (VS Code
Cmd+Shift+V / "Open Preview", Typora, Obsidian, GitHub — the crops render only there) → **Summary**
(verdict READY TO PRINT / FIX FIRST; must-fix / should / nice counts; top fixes as a short ranked
list) → the full-poster image → one `## Nn. <title>` section per finding (bold-labelled bullets
Severity/Effort/Lens, Where, Evidence, Fix; the crop as `![…](crops/nn.png)` with a relative path;
`- [ ] Accept  - [ ] Reject — note:`) → open decisions → what the author still needs to do → links to
the lens appendices. Findings are numbered N1, N2, … in rank order. When a fix was applied, show a
before/after crop pair (render both files with the same crops JSON, `--suffix _before` / `_after`).

## Inputs
- The poster, in any format:
  - **PDF** — used directly.
  - **Canva design** ID/URL — first export it with the Canva MCP `export-design` (PDF, pro quality if
    the plan allows; else PNG at full size), save the file, and read the text with `read-design`.
  - **PPTX/ODP/DOCX/KEY** — `render_crops.py` converts with LibreOffice (`soffice --headless`), else
    Keynote on macOS; if neither exists it returns "skipped": ask for a PDF export.
  - **PNG/JPG** — used directly; `check_export.py` cannot run (no PDF), so the preflight lens judges
    PPI from px ÷ print width and inspects text size by eye from crops.
- The paper (.tex or PDF), plus any result files the numbers come from.
- The venue's poster rules: URL or pasted text. If none is given, the venue lens searches for the
  official page.
- Optional: the poster rules file and decisions log (rejected items must not be re-proposed).

## Scale (compute once, write it at the top of every lens file)
- PDF at final size: 1 PDF pt = 1 printed pt; `check_export.py` reports `scale = 1.0`.
- PDF or design at another size: `s = print_width / design_width`; printed mm per design px =
  `s × 25.4 / 96`; printed pt per design px = `0.75 × s` (F4).
  Synthetic example: a 36 in (91.44 cm) wide design printed on A0 (84.1 cm): s = 84.1 / 91.44 = 0.920, 1 px ≈ 0.243 mm ≈ 0.69 pt.

## Render once (before the lenses)
```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/academic-poster/scripts/render_crops.py --poster <file> \
    --out-dir poster_review_<date>/crops --grid 3x2 [--print-width-cm 84.1]
```
Writes `crops/full.png` (2000 px wide) and section tiles `r1c1 …` the lenses can view. Boxes are
fractions of the page (0–1), so they are the same for a PDF, a PNG export or a converted PPTX.

## Fan-out
Claude Code: launch five `poster-review-visitor-lens` agents in parallel, one per lens, each writing
`poster_review_<date>/NN_<lens>.md` (appendix) and returning its findings as JSON (below).
Cowork / claude.ai (no subagents): run the lenses one after another in the same order.

## Merge into REVIEW.md
1. Collect every lens's findings; de-duplicate (same box ± 0.02 and same problem → one finding listing
   all lenses); rank must-fix → should → nice, then by effort; number N1, N2, ….
2. Write `crops.json` = `[{"name": "n1", "x0": …, "y0": …, "x1": …, "y1": …}, …]` and render:
   `render_crops.py --poster <file> --out-dir poster_review_<date>/crops --crops crops.json`
   (pad each box by ~0.01 so the context is visible; a whole-poster finding uses `full.png`).
3. Fill `templates/REVIEW-template.md`: summary first, then one section per finding using the `md`
   string the script prints for its crop. View two or three crops to confirm the box frames the issue.

### Lens finding format (returned to the orchestrator)
```json
[{"title": "Legend below the text floor", "severity": "must-fix", "effort": "low", "lens": "design",
  "box": [0.52, 0.41, 0.97, 0.55], "where": "results figure, right column",
  "evidence": "legend ≈ 15 pt printed (floor 24 pt)", "fix": "re-plot with legend ≥ 24 pt"}]
```
`box` = fractional page coordinates [x0, y0, x1, y1] of the region a reader should look at (measure
on `full.png`: px ÷ image width/height). Use `null` for whole-poster findings.

| # | Lens | File | Question it answers |
|---|---|---|---|
| 01 | visitor | `01_visitor.md` | Can a researcher who does not know the work follow it at 1–2 m? |
| 02 | preflight | `02_preflight.md` | Will the file print correctly at the venue size? |
| 03 | proofread | `03_proofread.md` | Is every word spelled, consistent, and faithful to the paper? |
| 04 | venue | `04_venue_rules.md` | Does it meet the venue's official poster rules? |
| 05 | design | `05_design.md` | Does it work as a poster (takeaway, flow, hierarchy, grid)? |

## Lens checklists

### 01 visitor (an outsider at 1–2 m)
Order findings A correctness/clarity → B flow → C legibility → D design → E proofreading.
- Can the problem, method and main finding be stated after one pass? Write them down as you read them.
- Unexplained terms, abbreviations, notation, metric names, dataset names (list each, with location).
- Claims with no on-poster evidence (a conclusion no figure or text supports).
- Numbers that look comparable but are different quantities; numbers missing their scope qualifier.
- Research questions truncated relative to the paper.
- Reading flow: is the path obvious; does any section read as an afterthought.
- Colour-semantics conflicts (a data colour reused for decoration or another meaning).
- Text inside figures below the floor; colliding tick labels; blurry upscaled rasters.

### 02 preflight (run `check_export.py`, then inspect)
```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/academic-poster/scripts/check_export.py poster.pdf --size A0 \
    --min-ppi 150 [--ideal-ppi 300] --min-pt 24 --qr-url <URL> --safe-mm 10 --contrast --crops poster_review_<date>/preflight
```
- 1a page size/orientation/page count vs venue (± 1 mm); 1b bleed and crop marks (ask the print shop;
  full-width rules touching the edge need bleed).
- 2 fonts embedded, no Type3; 2b glyph check — render spans with non-Latin or symbol characters at
  200 dpi and look for tofu boxes (◌ on isolated combining marks is normal).
- 3 image PPI at placed size (FAIL < 150; BELOW IDEAL < venue ideal); 3b colour space (RGB vs CMYK note)
  and transparency.
- 4 text sizes: min/median/max printed pt per role; every span below the floor; text inside raster
  figures estimated from crops (the script cannot see it).
- 5 WCAG contrast (F9) for text colours on their backgrounds.
- 6 ink-to-edge margins in mm per edge; logos clipped inside their own image (alpha reaching the edge row).
- 7 QR: decodes to the expected URL from a 300 dpi crop and from a down-sampled crop simulating
  distance (≈ 48 dpi ≈ 1.5 m — an assumption); printed edge ≥ scan distance / 10 (rule of thumb);
  reminder: phone-scan the printed proof.
- 8 hidden objects, annotations, overprint.

### 03 proofread + fidelity
- Spelling and grammar per text block.
- Consistency table: casing, dashes vs hyphens, number formats (thousands separators, k vs K),
  metric and model names, the same quantity labelled two ways across figures, punctuation of parallel rows.
- `verify_wording.py` (if a wording file exists) and `check_claims.py --poster poster.pdf --source paper`.
- Claim → source table: every number and every claim sentence → paper line (or result file), verdict
  SUPPORTED / OVERSTATED / UNDERSTATED / UNSUPPORTED.

### 04 venue rules
- Fetch the official page (WebFetch/WebSearch); quote the rules **verbatim** with URL and access date.
  If not found, say so and mark rules UNKNOWN — never assume a size.
- Rule-by-rule table: PASS / BELOW IDEAL / UNKNOWN (author must check) / N/A / NO RULE.
- Compare the author list with the paper and the venue programme.
- "What the author still needs to do": print order and turnaround, registration/presenter rules,
  poster-stand details, phone scan.

### 05 design critic
Fixed criteria, each with verdict + evidence + fix:
C1 10-second takeaway at ~3 m · C2 reading order · C3 type hierarchy and sizes · C4 text budget and
whitespace (word count) · C5 grid, gutters, box consistency · C6 figure readability at 1.5–2 m ·
C7 colour semantics and number of typefaces · C8 peripherals (QR placement, logos, safe margins).
Render the full page at ~1000 px (≈ 3 m view) and ~2000 px (≈ 1.5 m), plus section crops at 150 dpi.
Top-5 fixes ranked by impact/effort; a score out of 10; cite design sources as rules of thumb (e.g.
C. Purrington, "Designing conference posters"; M. Morrison, #BetterPoster; university poster guides).

## Lens appendix template (`NN_<lens>.md`, optional detail linked from REVIEW.md)
```
# NN — <Lens name>: <poster file or design> (<date>)

**Verdict: READY | READY WITH NOTES | NOT READY** — <one sentence>

Method: <tools, render dpi, scale s, what was read>. Assumptions: <listed>.

## Sources            (venue and design lenses: URL + access date)

## Checks
| # | Check | Result (PASS/WARN/FAIL/…) | Evidence (value, location, crop file) |

## Ranked fixes
1. <fix> — severity must/should/nice — effort low/med/high — evidence

## Files used
<renders, crops, span dumps>
```
Every finding needs evidence: a measured value, a location (page coordinates or section), a crop
file, or a paper line. Mark assumptions explicitly.

## Summary block (top of REVIEW.md)
The former `00_summary.md` is now the **Summary** section at the top of `REVIEW.md`
(`templates/REVIEW-template.md`): verdict, counts, top fixes; open decisions and the author's to-do
list follow the findings.
Severity: **must-fix-before-print** = the file will print wrong, a claim is wrong, a venue rule is
broken, or text is unreadable; **should** = clear improvement a visitor would notice; **nice** = polish.

## Hand-off after the review
Wording items → TEXT-EDIT; layout/colour → PLAN → BUILD on a copy; in-figure items → FIGURES re-plot.
Log every decision the author makes, including "accepted as is".
