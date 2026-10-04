# Wording fidelity (TEXT-EDIT mode; also PLAN and VERIFY)

Load this before writing or changing any poster text, and in TEXT-EDIT mode.

## Policy

- **Paper-only (default).** Every poster sentence comes from the paper: captions, body, research
  questions, conclusions. Light edits and summaries are allowed **in the paper's terminology**; no new
  claims, no stronger causality than the paper states, exact numbers.
- **Free wording (on request).** The author may switch it off; record that in the poster rules file.
  The numbers check (`check_claims.py`) stays on in both modes; only fragment traceability is relaxed.
- **No slogans**, rhetorical questions, invented headings, big-number callouts, or "insight captions"
  unless the author asks. Captions say what is plotted, sit under the plot, one line where possible.
- **Readable for a passer-by.** No unexplained abbreviations or notation. Keep at most an explicit
  whitelist (often one method acronym, spelled out at first use); spell out field terms; turn symbols
  into plain words (e.g. "θ′ = θ − η∇L" → "the weights after one update step").
- **Non-paper text** only from a short whitelist ("QR", venue tag, section markers, a QR header,
  navigation like "(see right)"), each exception recorded in `meta.non_paper_exceptions` with the
  approver and date.

## The wording file (`templates/wording.template.json`)

```
slots.<key>.text            the exact poster text ("\n" = line break)
slots.<key>.fragments[]     {text, tex_line}: deletion-only extracts; text = fragments joined
slots.<key>.short           {text, tex_lines[]}: a light edit/summary citing its source lines
slots.<key>.limit           word cap for short.text
slots.<key>.note            where it is used, what was rejected and why, the chosen variant
```
Keep the file's JSON indentation when editing (`json.dump(..., ensure_ascii=False, indent=1)` if it
uses one-space indent) so diffs show only the new slots. New variants get new keys (`intro_v2a`);
never overwrite a slot the poster already uses.

## Checks

1. `verify_wording.py wording.json --source paper.tex` → `fragments_failing = 0`, `short_failing = 0`.
   Pass 1: each fragment's words are an ordered subsequence of the cited line ± 1 (after LaTeX →
   Unicode, dropped cites/refs, case folding). Pass 2: `short` cites existing lines and respects its cap.
2. `check_claims.py --poster wording.json --source paper.tex [--registered claims.json]` → every number
   traced. Derived numbers (a percentage computed from a table) go in `claims.json` with the derivation.
3. **Fidelity audit** (read-only subagent, or a separate pass in Cowork) on every new or edited
   sentence: rate each phrase SUPPORTED / OVERSTATED / UNDERSTATED / UNSUPPORTED against the paper,
   with the line it relies on and a minimal fix. Apply fixes only if the author agrees; log accepted
   overstatements. Neither script checks meaning — the audit does.

## Fidelity-trap patterns to audit for

- **Terminology drift:** a near-synonym that names a different quantity in the field (e.g. calling a
  raw count a rate or ratio the paper never computed).
- **Scope loss:** a number true for one model, dataset or setting printed without its qualifier next
  to a plot that shows several. The auditor always flags it; the author decides; record overrides.
- **Two quantities, one look:** a single-example count beside a dataset mean — label which is which.
- **Causal upgrade:** "causes", "because", "fixes" where the paper says "is associated with",
  "suggests", "helps".
- **Adjective upgrade:** "the standard method" where the paper says "a common approach".
- **Truncated research questions:** dropping a clause that the figure's axis depends on.
- **Wrong locator:** citing the abstract's paraphrase instead of the line that states the claim.

## TEXT-EDIT procedure (paragraph → poster-readable structure)

1. **Plan.** Read the block's current text and free area (Canva `read-design`, or the PPTX/PDF).
   Settle story, placement and wording freedom with the author (self-contained questions).
2. **Draft 2–3 options** from the structure menu, one wording slot each, word cap set:
   - **Two-lane flow:** setting line → one row per problem `[gap] → [fix]` → a "But…" callout → a
     full-width question bar.
   - **Numbered chain:** lead-in line → 3–4 numbered boxes left→right joined by arrows → question bar.
   - **Labelled rows:** bold label (Problem / Common fix / Catch) + one-line text per row → question bar.
3. **Verify** (checks 1–3 above); fix `tex_lines`.
4. **Pages** (Canva, after explicit approval): one new page per option via `merge-designs`, one
   operation per call. PPTX route: one file per option.
5. **Build** per `canva-mcp-recipe.md` (take element IDs from the returned document; `format_text` after
   every `add_text`; `top + height ≤ box bottom`).
6. **Commit** under the stored approval style; export into a new folder; crop the block and view it.
7. **Log** the decision; record the chosen slot and rejected variants in the slot `note`.

Typography for text structures (defaults, design px at print size): body 36–40 px, labels bold
40–42 px, question bar bold 44–46 px white on a dark fill, nothing below the floor (32 px = 24 pt).
Use semantic colours consistently (one meaning per colour) and never reuse a data colour for decoration.
