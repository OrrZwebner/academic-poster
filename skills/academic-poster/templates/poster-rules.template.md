# Poster rules — <poster short name>

Standing rules for this poster. Every planner, builder, text editor and reviewer reads this file
first. Later entries in the decisions log override this file; update this file when they do.

## Live state (re-verify with read-design or by opening the file before planning)
- **Main design / file:** <Canva design ID or URL | path to .pptx/.pdf> — the only one to edit
- **Print size:** <A0 portrait 84.1 × 118.9 cm | 36 × 48 in | …> — source: <venue rules URL, access date>
- **Design canvas:** <W × H px at 96 px/in>; scale to print s = <print width / design width>
- **Archived / superseded designs:** <IDs or files> — do not edit
- **Others' designs (read-only reference, never edit):** <IDs or "none">
- **QR target:** <URL> — decode-checked on <date>; phone scan of the printed proof: <pending | done>

## Intake answers (asked once at the start)
- **Approval style:** <live in Canva — commit after approval, report "Canva updated" | approve/reject Markdown with before/after crops | ask once per PLAN> (default: asked once at PLAN, stored here)
- **Build route:** <Canva MCP | PPTX>
- **Canva plan:** <free | Pro/Teams> — free: no resize, use "PDF Print" from the editor
- **Wording mode:** <paper-only (default) | free wording> — the numbers check stays on in both
- **Minimum text size:** <24> pt at print size, for ALL text including text inside figures
- **Design jams (themed variants):** <off (default) | on>

## Hard rules
- **Copy first.** Every revision is built on a copy or on new pages; never overwrite earlier designs,
  pages or exports. New exports go to a new dated folder.
- **Text:** <paper wording only: each text is a wording-file slot citing its source lines; light edits
  in the paper's terminology, no new claims | free wording>. No slogans, rhetorical questions,
  invented headings or big-number callouts unless the author asks.
- **Non-paper text allowed:** <"QR", venue tag, section markers, …> — each exception recorded in the
  wording file `meta.non_paper_exceptions` with date and approver.
- **Abbreviations allowed unexplained:** <list, e.g. one method acronym>; spell out everything else.
- **Numbers:** every number traces to the paper or a registered derived claim (`claims.json`).
- **Figures:** at most <n> dense figures (heatmaps); minimum widths per role: <role: px>; never
  distort aspect ratios; never invent a plot that is not in the paper.
- **Style:** body <size px> <colour>; captions one line, under the plot, centred, <colour>;
  header <…>; footer <logos only | …>; data colours <colour: meaning> are reserved for data.
- **Fonts:** <heading font / body font> (set by the author in Canva; the MCP cannot set fonts).

## Rejected before (do not re-propose without a new reason)
- <idea> — rejected <date>, because <reason>

## Logged exceptions
- <item below the text floor, or other accepted deviation> — accepted by <author> on <date>

## Coordination
- Parallel sessions announce which design, pages and wording keys they own, and release them when done.
- Log every resolved decision in `<decisions log path>`: date, what, why, what it touches.
