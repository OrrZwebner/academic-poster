# <task>-PLAN — <one-line task name> (<YYYY-MM-DD>)

## Context
- **Input:** <what the author asked, the design/file it applies to, the sources read>
- **Method:** <how the change will be made: Canva route | PPTX route; which copy>
- **Output:** <the new design copy / .pptx, exports folder, reports>

## Target
- Route: <Canva | PPTX>
- Canva: source design <ID or URL>, page <n>; copy to make: "<copy name>" | PPTX: plan-spec `<path>.json` → `<out>.pptx`
- Print size: <e.g. A0 portrait 84.1 × 118.9 cm = 3178 × 4494 px at 96 px/in>
- Reserved areas (do not touch): <none | area + owner>
- Approval style: <from the poster rules file>

## Current state (REAL — measured)
| Element | left | top | width | height | text / media | Source |
|---|---|---|---|---|---|---|
| <heading "Results"> | <px> | <px> | <px> | <px> | <slot or media key> | read-design / export, <date> |

## Changes per section
### <Section name>
| # | Element | Action | left | top | width | height | Style (size px / pt, colour, weight) | Wording slot / media | REAL or LAYOUT |
|---|---|---|---|---|---|---|---|---|---|
| 1 | <caption under results plot> | add_text + format_text | <px> | <px> | <px> | auto | 34 px (25.5 pt) #646c78 centred | `results_caption` | LAYOUT |

**Space budget** (must sum exactly):
```
frame height                      = <H>
heading <h1> + gap <g1> + figure <h2> + gap <g2> + caption <h3> + padding <p>
= <h1> + <g1> + <h2> + <g2> + <h3> + <p> = <sum>  ✓ (≤ H, spare <H − sum>)
```
Minimums checked: text ≥ <floor> pt at print size; figure widths ≥ <min per role>; aspect h = w × px_h / px_w.

## Op list (Canva route; batches of ≤ 15, Z-order panels → images → text)
**Batch 1** (page_index <n>)
1. insert_shape <panel> …
2. insert_fill media <media key> left … top … width … height …
3. add_text slot `<key>` → 4. format_text font_size … color … font_weight … text_align … line_height 1.25

(PPTX route: the same elements, in the same order, as `elements` of the plan-spec JSON.)

## Verification checklist
- [ ] `verify_wording.py` → 0 failing (or free-wording mode recorded)
- [ ] `check_claims.py` → every number traced
- [ ] after every batch: `top + height ≤ container bottom` for every text; no overlaps
- [ ] export PNG into a NEW folder; view it; crop the changed region
- [ ] `check_export.py` on the print PDF (size, PPI, min pt, fonts, QR, margins)
- [ ] QR decodes to <URL>; remind the author to phone-scan the printed proof

## OPEN DECISIONS
<Each one self-contained: design + page + section named, exact wording and sizes, no internal shorthand, one decision per question, 2–4 options, recommendation first with an ASCII mockup.>

**OD-1.** <question>
- Option A (recommended): <…>
  ```
  +---------------------------+
  | heading                   |
  | [ figure ]   text rows    |
  +---------------------------+
  ```
- Option B: <…>

## Draft decisions-log entry
## <YYYY-MM-DD> — <title>
- **Decided:** <…>
- **Why:** <…>
- **Touches:** <design copy / pages / wording slots / files>

## RESOLVED DECISIONS
<appended after the author answers; these override the sections above>
