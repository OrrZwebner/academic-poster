# Planning prompt and PLAN spec (PLAN mode)

Load this at the start of a new poster, when the user asks what to put in a planning prompt, or
before writing any `<task>-PLAN.md`.

## The fill-in planning prompt

Give this to the user to fill in (anything left blank becomes an OPEN DECISION, not a guess):

```
POSTER PLANNING PROMPT
Paper:            <path to .tex and/or PDF>              (authoritative source of every claim)
Figures folder:   <path; vector PDFs preferred>          Plot scripts (optional): <path or "none">
Venue:            <name, year>   Print size: <e.g. A0 841×1189 mm | 36×48 in>   Orientation: <portrait|landscape>
Venue rules:      <URL or pasted text>                   Second venue/size (if any): <…>
Audience:         <e.g. researchers passing at 1–2 m; specialists vs. generalists>
Sections:         <e.g. Introduction · Method · RQ1..RQn · Conclusion>  (section numbers must match RQ numbers)
Must-include figures: <fig ids + where>   Candidates: <ids + leaning>   Excluded: <ids>
Max dense figures (heatmaps etc.): <n>    Hero/teaser visual: <which, or none>
Text policy:      fidelity = <paper-only (default) | free wording>;  allowed non-paper text: <"QR", venue tag, section markers, …>
Abbreviations allowed unexplained: <list, e.g. one method acronym>
Minimum text size: <24 pt at print size for all text (default) | other>
Branding:         logos <files>, placement <footer only?>, funding acknowledgement <required text or none>
Authors/affiliations: <show affiliations? email?>
QR target:        <URL>   QR header text: <e.g. "Paper & code" or none>
Style examples:   <links/files of posters to emulate>; colours <palette or "derive from figures">
Build route:      <Canva (design ID/URL to copy, or "new custom size") | PPTX>;  Canva plan: <free | Pro>
Deliverable:      <number of whole-poster options>; approval style <live in Canva | approve/reject Markdown | ask once at PLAN>
Themed design variants ("design jams"): <no (default) | yes, N>
Print deadline:   <date>, print shop <bleed needed? crop marks?>
Rejected before:  <ideas not to re-propose>
```

## Method (planner)

1. **Read, in order** (later overrides earlier): decisions log → poster rules file → last review or
   audit → wording file + media map → latest exports (VIEW them) → the paper (authoritative).
2. **Restate** the task as input → method → output in three lines.
3. **Inspect the real state.** Canva: `read-design` (page metadata + element geometry) and export a PNG
   of the target page into the task folder; VIEW it. PPTX/PDF: open/render it. Measure lefts, tops,
   widths, heights before proposing geometry. Label every number **REAL** (measured/sourced) or
   **LAYOUT** (a design choice).
4. **Plan each change as an exact operation:** element (by current text/position), action, px geometry,
   size/colour/weight, media key, wording slot.
5. **Arithmetic is shown.** Space budget per frame: heights + gaps + paddings = frame height, with the
   sum written out (F8). For a uniform rescale (F6): `s = W_target / W_source`,
   `spare_h = H_target − H_source × s`, restore every size with `size × s < floor` to the floor, and
   allocate `spare_h` in a table whose rows sum to `spare_h`.
6. **Check every rule:** text floor at print size, figure minimum widths per role, aspect lock, dense-
   figure cap, colour semantics, safe margin.
7. **Forks become OPEN DECISIONS** (format below). Give your own opinion first.
8. **Write `specs/<task>-PLAN.md`** from `templates/PLAN-template.md`: target + copy name + page +
   reserved areas; op list batched ≤ 15 with Z-order (panels → images → text) and a `format_text`
   after every `add_text`; verification checklist; OPEN DECISIONS; draft decisions-log entry.
   For the PPTX route also write the plan-spec JSON (`pptx-route.md`).
9. **Return** the path, a ≤ 10-line summary, and the OPEN DECISIONS verbatim.

### First-round variant (N whole-poster options)
When the author asks for several whole-poster options, make them differ on named axes (e.g. layout
family × motivation block × figure choice) and show them as one matrix, so the author can mix
(“layout of B with the figures of C”). Themed "design jams" (a visual pun on the paper's topic) only if
the author opted in; they must use real data, never decorative fake numbers.

## OPEN DECISION format

Each question must stand alone:
- Name the design (ID/URL or file), page, section and element.
- Quote the exact wording involved and give sizes in px and printed pt/cm.
- No internal shorthand (option codes, revision tags, notation) without spelling it out.
- One decision per question; 2–4 concrete options; the recommended option first, marked, with one
  sentence of reasoning; an ASCII mockup when layout is involved.
- Never re-propose an item listed as rejected unless there is a new reason, stated.

Example (synthetic):
> **In the Canva design "Poster – rev 3 (copy)", page 1, Results section: the caption under the
> accuracy plot ("Accuracy per model size (mean of 3 seeds)", 34 px = 25.5 pt at A0) wraps to two
> lines at the current plot width of 1380 px. Which fix?**
> A (recommended): widen the plot and caption to 1460 px (the full panel width) — keeps one line, the
> plot grows 6%. B: shorten the caption to "Accuracy per model size" (new wording slot, paper-faithful).
> C: allow two lines.

## Logging
After the author answers, append RESOLVED DECISIONS to the PLAN and a dated entry to the decisions log:
`## <date> — <title>` · Decided · Why · Touches.
