---
name: academic-poster
description: >
  Plans, builds, edits and pre-print-checks academic research posters from a paper (LaTeX or PDF
  plus its figures). Builds natively in Canva through the Canva MCP when connected, or as an editable
  .pptx without Canva; keeps every poster sentence and number traceable to the paper; exports figures
  at print resolution; renders non-Latin scripts correctly; writes a build plan with open decisions
  before editing; works only on copies; and runs a five-lens pre-print review (visitor clarity, print
  preflight, proofread and fidelity, venue rules, design) on any existing poster in any format (PDF,
  Canva, PPTX, PNG/JPG), delivered as one Markdown notes file with a summary and a crop per finding.
  Use when the user asks for a research poster, conference poster, academic poster, paper to poster,
  "make a poster from my paper", a Canva poster, connecting the Canva MCP, an A0 or 36x48 in poster,
  re-plotting figures for print, restructuring or shortening poster text, a poster review, a pre-print
  check or preflight, or "is my poster ready to print".
license: MIT
compatibility: >
  Claude Code, claude.ai and Cowork. The Canva MCP server is optional (Canva build route only).
  Scripts need Python 3.8+; PyMuPDF, python-pptx, Playwright and OpenCV or pyzbar are optional and
  each script reports "skipped: dependency missing" without them.
metadata:
  version: "0.1.0"
  author: "Orr Zwebner"
allowed-tools: Read Grep Glob
---

# Academic poster: paper → print-ready poster, and pre-print review

You turn a research paper into a conference poster and check posters before printing. The paper is
the authority for every word and number. You plan before you build, build only on copies, and
surface every real decision to the author as a self-contained question with your recommendation.

Scripts live in `${CLAUDE_PLUGIN_ROOT}/skills/academic-poster/scripts/` (standalone skill: the
`scripts/` folder next to this file). Every script prints JSON and supports `--help`.

## 1. Start of chat: intake (do this first, once)

1. **Detect Canva.** Look for Canva design tools in your tool list (names ending in `read-design`,
   `edit-design`, `search-designs`, `export-design`). Present → note "Canva route available" and verify
   with one read-only call before the first build. Absent → note "PPTX route" and tell the user Canva is
   optional (`references/canva-mcp-setup.md` explains how to connect it).
2. **Find or create the poster rules file** (`poster-rules.md` in the poster folder, from
   `templates/poster-rules.template.md`). If it exists, read it and the decisions log; do not re-ask
   what it already answers.
3. **Ask the approval style** (unless stored), as a multiple-choice question:
   - **Ask once at PLAN (default, recommended):** the author approves each PLAN once; the builder then
     builds on a copy and commits without asking again.
   - **Live in Canva:** the author reviews in Canva; commit after the content choice is approved and
     report "Canva updated" (no preview images to approve).
   - **Approve/reject Markdown:** a file with before/after crops and an Approve/Reject box per change.
   Store the answer in the poster rules file.
4. **Collect the planning-prompt fields** (`references/planning-prompt.md`): paper, figures, venue +
   print size + rules URL, audience, sections, must-include figures, wording mode, allowed
   abbreviations, minimum text size (default 24 pt at print size for ALL text, including inside
   figures), branding, QR target, build route and Canva plan, number of options, design jams (off
   unless asked). Missing fields become OPEN DECISIONS; never guess a venue size.
5. **Pick the mode** (table below) and say which one you are in.

For REVIEW only (an existing poster), intake is just: the poster (any format: PDF, Canva link, PPTX,
PNG/JPG), the paper, the venue rules. Skip steps 3–4.

## 2. Modes

| Mode | Use when | Inputs | Output | Read |
|---|---|---|---|---|
| **SETUP** | Canva tools missing or failing | Claude surface; Canva account | Canva connected + verified, plan recorded — or PPTX route chosen | `references/canva-mcp-setup.md` |
| **PLAN** | New poster, new section, layout change, revision, resize | Planning prompt; current design/file; rules file | `specs/<task>-PLAN.md` with OPEN DECISIONS (+ plan-spec JSON for PPTX) | `references/planning-prompt.md`, `references/layout-and-typography.md` |
| **BUILD — Canva route** | A PLAN with every decision resolved; Canva connected | PLAN, wording file, media map | Committed Canva copy, exports in a new folder, check results, deviations | `references/canva-mcp-recipe.md`, `references/canva-mcp-gotchas.md` |
| **BUILD — PPTX route** | Resolved PLAN; no Canva (or .pptx requested) | PLAN → plan-spec JSON, wording, figures | Editable .pptx at print size + problem report | `references/pptx-route.md` |
| **TEXT-EDIT** | Re-word, shorten, bulletize, "make it more visual", fix unclear terms | Block + constraints + paper | 2–3 verified + audited options, then one page/file per option | `references/wording-fidelity.md` |
| **FIGURES** | Export/re-plot figures, PPI questions, non-Latin sample text | Figure files, placed sizes, print size | Print-resolution PNG/SVG, PPI table, re-plot prompt, media IDs | `references/figures-and-pdf.md` |
| **VERIFY/EXPORT** | Before sharing or printing a poster this skill built | Design or PDF, wording file, venue size | Wording + claims checks, print PDF, `check_export.py` report | `references/figures-and-pdf.md` |
| **REVIEW** | "Review my poster", "is it ready to print", any existing poster | Poster in any format (PDF, Canva, PPTX, PNG/JPG); paper; venue rules | `poster_review_<date>/REVIEW.md` (summary + one crop per finding) + `crops/`; lens files as optional appendices | `references/pre-print-review.md`, `templates/REVIEW-template.md` |

PLAN, TEXT-EDIT, FIGURES, VERIFY and REVIEW all work without Canva. A request that spans modes runs
them in order: PLAN → (approval) → FIGURES → BUILD → VERIFY; REVIEW findings hand off to TEXT-EDIT,
PLAN or FIGURES.

## 3. Hard rules (all modes)

- **The paper is authoritative.** Never edit the paper. Every number traces to the paper or to a
  registered derived claim; re-derive any headline number from source before printing (a slide or an
  older poster is not a source).
- **Wording mode.** Paper-only by default: poster text comes from wording-file slots that cite source
  lines; light edits in the paper's terms, no new claims, no stronger causality. Free wording only when
  the author says so (recorded in the rules file); the numbers check stays on in both modes.
- **No unrequested rhetoric.** No slogans, rhetorical questions, invented headings, big-number callouts
  or insight captions; captions say what is plotted.
- **Readable for a passer-by.** No unexplained abbreviations or notation beyond the rules-file whitelist.
- **Never invent figures.** Use the paper's plots; never add a derived plot the paper does not contain.
- **Copy first.** Build every revision on a copy or on new pages/files. Never overwrite earlier
  designs, pages or exports; exports go to a new dated folder. Never touch designs owned by others.
- **Plan before build.** BUILD runs only from a PLAN whose OPEN DECISIONS are resolved. If reality
  differs from the PLAN (element missing, content does not fit), stop and return the question.
- **Approval.** Commit/merge only under the stored approval style. Structural Canva changes
  (`merge-designs`, new pages) need explicit approval.
- **Print floor.** Text ≥ the rules-file floor (default 24 pt at print size, all text including inside
  figures); images ≥ 150 PPI at placed size; ink ≥ 10 mm from the edge. Exceptions are logged per item.
- **Questions.** Every question is self-contained: name the design/file, page, section, the exact
  wording and sizes; no internal shorthand; one decision per question; give your opinion and a
  recommended option first. Never re-propose items the rules file lists as rejected.
- **Log decisions** in the decisions log: `## <date> — <title>` · Decided · Why · Touches.
- **Automate, don't delegate to the user.** Do via MCP or scripts whatever can be done; involve the
  user for decisions, plan upgrades, page deletion and font application only.

## 4. Procedures

### SETUP
1. Run the detection in section 1. If missing, give the two connection routes from
   `references/canva-mcp-setup.md` (claude.ai/desktop connector; or `claude mcp add` in Claude Code),
   warn that the **Canva Dev MCP** (`@canva/cli`) is the wrong server, and offer the PPTX route.
2. After connecting: restart/resume if in Claude Code, authenticate via `/mcp`, verify with one
   read-only call.
3. Record route and Canva plan in the rules file. Free plan → no `resize-design`; print via pro
   export or the editor's **PDF Print** download; Pro recommended for print.

### PLAN
1. Read decisions log → rules file → last review → wording file + media map → latest exports (view
   them) → the paper.
2. Restate input → method → output in three lines.
3. Measure the real state (Canva `read-design` + PNG export; or open/render the file). Label values
   REAL or LAYOUT.
4. Write each change as an exact operation with px geometry, style, wording slot, media key; show the
   space-budget arithmetic; check every minimum.
5. Turn forks into OPEN DECISIONS (2–4 options, recommendation first, ASCII mockup).
6. Write `specs/<task>-PLAN.md` from `templates/PLAN-template.md` (Canva ops batched ≤ 15, Z-order
   panels → images → text, `format_text` after every `add_text`). PPTX route: also the plan-spec JSON.
7. Return path + ≤ 10-line summary + OPEN DECISIONS; ask them; append RESOLVED DECISIONS.
8. N whole-poster options: vary named axes in one matrix. Design jams only if opted in.

### BUILD — Canva route
1. Confirm all OPEN DECISIONS are resolved. 2. `copy-design` (name per PLAN). 3. `read-design` with
`open_transaction: true`, filtered fields. 4. `edit-design` batches ≤ 15 ops, `keep_open`. 5. After
every batch: read returned geometry, re-position below auto-height text, check `top + height ≤
bottom`, aspect ratios, overlaps; take element IDs from the returned document. 6. Commit under the
approval style. 7. Upload new media and record IDs + px. 8. VERIFY. 9. Report: copy ID, pages, export
paths, pass/fail per check, deviations, draft log entry.
Gotchas (16 px black default text, integer sizes, no fonts, no delete-page, resize quota, export
downsampling, stale thumbnails): `references/canva-mcp-gotchas.md`.

### BUILD — PPTX route
Translate the PLAN into `<task>.plan-spec.json` (`templates/plan-spec.example.json`), then
`build_pptx.py <spec> --wording wording.json --media media.json --out out/<task>/<name>.pptx`. Fix every
reported problem, export to PDF, run VERIFY. Details and the optional import into Canva:
`references/pptx-route.md`.

### TEXT-EDIT
1. Read the block and its free area; settle story, placement and wording freedom.
2. Draft 2–3 options (two-lane flow, numbered chain, labelled rows) as new wording slots with word caps.
3. `verify_wording.py` → 0 failing; `check_claims.py`; then a read-only fidelity audit (subagent in
   Claude Code; separate pass in Cowork) rating each phrase SUPPORTED / OVERSTATED / UNDERSTATED /
   UNSUPPORTED; apply minimal fixes the author accepts.
4. After approval: one page (Canva, `merge-designs` one op per call) or file (PPTX) per option; build;
   commit; export to a new folder; crop and view the block. Log; record rejected variants in the slot note.

### FIGURES
1. Map poster figure → source file (vector preferred) → plotting script.
2. `export_figs.py <pdfs> --out assets/figs [--svg] [--placed-cm W]` (long side 6000 px).
3. PPI at placed size (≥ 150; venue "ideal" reported separately); in-figure text at print scale.
4. Too-small in-figure text → poster-mode re-plot prompt (same plots, bigger text only; paper outputs
   byte-identical). No scripts → report and log the exception.
5. Non-Latin sample text → `render_script_text.py` (browser shaping; count assertions).
6. Upload (Canva) or reference (PPTX); record media IDs and px.

### VERIFY/EXPORT
1. `verify_wording.py wording.json --source paper.tex` and
   `check_claims.py --poster wording.json --source paper.tex [--registered claims.json]`.
2. Export PNG (view) into a new folder; crop risky regions; look at them.
3. Print PDF: Canva pro-quality export or the editor's **PDF Print**; PPTX: export to PDF.
4. `check_export.py poster.pdf --size <A0|WxHcm> --min-pt <floor> --qr-url <URL> --safe-mm 10 --contrast`.
5. Remind: phone-scan the QR on the printed proof; ask the print shop about bleed.

### REVIEW (any existing poster, any format; read-only)
Default deliverable: ONE Markdown notes file, `poster_review_<YYYY-MM-DD>/REVIEW.md`, with crops in
`poster_review_<date>/crops/` (template `templates/REVIEW-template.md`).
1. Get a renderable file: PDF/PNG/JPG as given; **Canva** → export with the Canva MCP `export-design`
   (PDF, pro quality if available, else full-size PNG) and save it; PPTX/ODP/KEY → `render_crops.py`
   converts it (LibreOffice, else Keynote on macOS; else ask for a PDF export). Compute the print scale.
2. Render once: `render_crops.py --poster <file> --out-dir poster_review_<date>/crops --grid 3x2`
   → `full.png` + section tiles for the lenses.
3. Fan out the five lenses — Claude Code: five parallel `poster-review-visitor-lens` agents with
   `lens` = visitor | preflight | proofread | venue | design; Cowork/claude.ai: run them in sequence.
   Each returns findings with severity, effort and a fractional crop box `[x0, y0, x1, y1]`.
4. Merge: de-duplicate, rank must-fix → should → nice, number N1…; write the boxes to `crops.json`
   and run `render_crops.py --crops crops.json` (before/after pairs: `--suffix _before` / `_after`).
5. Write `REVIEW.md`: preview tip line first ("open in a Markdown preview — VS Code Cmd+Shift+V /
   'Open Preview', Typora, GitHub — crops only render there"), then the **Summary** (verdict READY TO
   PRINT / FIX FIRST, counts, top fixes ranked), the full poster, one `## Nn.` section per finding
   (bold-labelled bullets, crop image, Accept/Reject checkboxes), open decisions, author to-do, links
   to the `NN_<lens>.md` appendices. Tell the user the preview tip when you hand it over.
6. Hand fixes to TEXT-EDIT, PLAN → BUILD, or FIGURES. Never edit during REVIEW.

## 5. Scripts

| Script | Does | Key options | Optional deps |
|---|---|---|---|
| `export_figs.py` | Vector PDF → PNG (long side N px), optional SVG; px + PPI report | `--out --long-side --svg --placed-cm` | PyMuPDF (PDF inputs) |
| `verify_wording.py` | Fragment traceability (ordered subsequence of cited line ± 1) + word caps | `--source --limits --default-limit --window --free-wording` | PyMuPDF/pdftotext (PDF paper) |
| `check_claims.py` | Every poster number found in the paper or registered with a derivation | `--poster --source --registered --ignore` | PyMuPDF/pdftotext |
| `check_export.py` | Print preflight: size, PPI, min pt, fonts, QR, margins, contrast | `--size --min-ppi --ideal-ppi --min-pt --qr-url --safe-mm --contrast --crops` | PyMuPDF (required), OpenCV or pyzbar (QR) |
| `render_script_text.py` | Token chips / lines in any script via headless Chromium | `--out --dpr --width --tokenizer --html-only` | Playwright, transformers |
| `build_pptx.py` | PPTX route: plan-spec JSON → editable .pptx with checks | `--out --wording --media --assets --check-only` | python-pptx (required) |
| `render_crops.py` | REVIEW: any poster file → `full.png` + named crops from fractional boxes; px + PPI | `--poster --out-dir --dpi --full-width --crops --grid --suffix --print-width-cm` | PyMuPDF (PDF/office), Pillow or PyMuPDF (raster), LibreOffice/Keynote (office) |

Exit codes: 0 pass, 1 checks failed, 2 skipped (dependency missing; JSON says which). On claude.ai,
where packages may be unavailable, say which check was skipped and do it by inspection instead.

## 6. Agents (Claude Code plugin)

| Agent | Role | Writes |
|---|---|---|
| `poster-planner` | PLAN mode; read-only on designs | `specs/<task>-PLAN.md`, plan-spec JSON |
| `poster-builder` | BUILD from one resolved PLAN (Canva or PPTX route) | the copy / .pptx, exports, report |
| `poster-text-editor` | TEXT-EDIT with a fidelity-audit subagent | wording slots, option pages/files |
| `poster-review-visitor-lens` | One REVIEW lens (`lens` argument); read-only | findings JSON with crop boxes; appendix `NN_<lens>.md` |

You (the main agent) relay: you ask the user, render the crops and write `REVIEW.md`, and log decisions. Subagents
cannot ask the user; they return questions. Run independent tasks as parallel subagents. In Cowork
or claude.ai, play these roles inline, in the same order.

## 7. Reference files (load on demand)

| File | Load when |
|---|---|
| `references/canva-mcp-setup.md` | SETUP; Canva tools missing; auth problems; Canva plan questions |
| `references/canva-mcp-recipe.md` | Before any Canva edit, copy, merge or export |
| `references/canva-mcp-gotchas.md` | A Canva call fails or surprises you; before a large build |
| `references/pptx-route.md` | BUILD without Canva; .pptx requested |
| `references/figures-and-pdf.md` | FIGURES; PPI/size math; paper given as PDF; non-Latin text; re-plot prompt |
| `references/planning-prompt.md` | New poster; "what should I put in the prompt"; writing any PLAN |
| `references/wording-fidelity.md` | Any new or changed poster text; TEXT-EDIT |
| `references/layout-and-typography.md` | Layout, type scale, canvas sizes, colour, second print size |
| `references/pre-print-review.md` | REVIEW; each review lens; report templates |

Templates: `templates/PLAN-template.md`, `templates/plan-spec.example.json`,
`templates/wording.template.json`, `templates/media.template.json`,
`templates/poster-rules.template.md`, `templates/REVIEW-template.md`.

Canva MCP behaviour described in these files was **observed in 2026-10 and may change**; when the
tool's own schema or messages disagree, follow the tool and note the difference.
