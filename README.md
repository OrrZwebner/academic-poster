# academic-poster

A Claude skill that turns your research paper into a print-ready conference poster, and checks
any finished poster before you send it to print.

| You give | You get |
|---|---|
| Your paper (PDF or LaTeX) + its figures | A poster built in Canva, or an editable PowerPoint if you don't use Canva |
| A paragraph from the poster | 2–3 shorter, poster-readable versions that still say only what the paper says |
| Any finished poster (PDF, PowerPoint, image or Canva link) | `REVIEW.md`: a summary, then each problem with a crop of the poster and a suggested fix |

The pre-print review checks what people miss: text too small at print size, blurry figures, a QR
code that doesn't scan, the venue's size rules, unclear terms, and numbers that disagree.
Open `REVIEW.md` in a Markdown preview (VS Code: Cmd+Shift+V) to see the crops.

<details>
<summary>All modes</summary>

| Mode | Inputs | Output |
|---|---|---|
| **SETUP** | Your Claude app; a Canva account (optional) | Canva connected, or the PowerPoint route chosen |
| **PLAN** | The planning prompt (below) | `specs/<task>-PLAN.md`, with the decisions left to you |
| **BUILD** | A finished plan | A Canva copy or a `.pptx`, plus exports and checks |
| **TEXT-EDIT** | A text block + the paper | 2–3 checked rewrites |
| **FIGURES** | Figure PDFs/PNGs | Print-resolution images and a re-plot prompt for small text |
| **VERIFY/EXPORT** | Design or PDF | Wording, numbers and print checks |
| **REVIEW** | Any poster | `REVIEW.md` + crops |

</details>

## Installation

**There are three separate ways to install this. They are alternatives — pick the one that matches
how you use Claude, and ignore the other two.**

| How you use Claude | Use |
|---|---|
| In the browser at **claude.ai**, the Claude desktop app, or Cowork | **Option A** — upload one file, no terminal |
| In **Claude Code** (terminal) | **Option B** — install as a plugin |
| In **Claude Code**, and you want the skill without the plugin wrapper | **Option C** — copy the skill folder |

---

### Option A — claude.ai, the Claude app or Cowork · no terminal

This route needs no terminal. It requires a paid Claude plan.

1. Download **`academic-poster.zip`** from the [latest release](https://github.com/OrrZwebner/academic-poster/releases/latest)
   (direct link: <https://github.com/OrrZwebner/academic-poster/releases/latest/download/academic-poster.zip>). Don't unzip it.
2. Go to **claude.ai** → **Customize** in the left sidebar → **Skills**.
3. Click **Upload skill**, pick the file you just downloaded, and make sure the toggle next to
   **academic-poster** is **on**.

Then start a new chat, attach your paper (and figures), and ask — see [Usage](#usage). On this
route the review lenses run one after another rather than in parallel, and scripts whose Python
packages are unavailable report "skipped". When that happens, Claude does the check by inspection
instead.

> Use the release file, not the green **Code → Download ZIP** button. That button gives you the
> entire repository, which buries `SKILL.md` several folders deep and won't be recognized as a skill.
> The release archive is built for uploading as-is.
>
> The official docs do not state which archive extension the uploader accepts (`.zip` or `.skill`).
> If the upload rejects `academic-poster.zip`, rename it to `academic-poster.skill` and try again.

---

### Option B — Claude Code, as a plugin

```
/plugin marketplace add OrrZwebner/academic-poster
/plugin install academic-poster@academic-poster
```

Or from a shell: `claude plugin marketplace add OrrZwebner/academic-poster && claude plugin install academic-poster@academic-poster`.

This also installs the four agents: `poster-planner`, `poster-builder`, `poster-text-editor` and
`poster-review-visitor-lens`.

---

### Option C — Claude Code, as a standalone skill

Copy `skills/academic-poster/` into `~/.claude/skills/` (personal) or `.claude/skills/` (one project).
If you want the agents, also copy `agents/*.md` into `~/.claude/agents/` or `.claude/agents/`:

```bash
git clone https://github.com/OrrZwebner/academic-poster.git
mkdir -p ~/.claude/skills ~/.claude/agents
cp -R academic-poster/skills/academic-poster ~/.claude/skills/
cp academic-poster/agents/*.md ~/.claude/agents/      # optional
```

## Connect Canva (optional)

You can skip this. Without Canva the skill builds a `.pptx` instead (see
[Without Canva](#without-canva)).

Sources: Canva help, "MCP / agent setup" (https://www.canva.com/help/mcp-agent-setup/); Claude Code
MCP docs (https://code.claude.com/docs/en/mcp); Claude help, custom connectors
(https://support.claude.com/en/articles/11175166). These were checked on 2026-10-04, and menu labels
change, so re-check them if a button is missing.

**claude.ai, the Claude desktop app, or Cowork.** Canva calls this "the easiest and recommended way".
Canva's page says it needs a paid Claude plan.

1. In Claude, open **Connectors**. Canva's page calls it **Manage Connectors**; in the current Claude
   UI it is under **Customize** (or **Settings**).
2. Click **Browse Connectors**.
3. Find **Canva** and click **Connect**.
4. Sign in to Canva in the window that opens and allow access.
5. In a chat, make sure the Canva connector's toggle is **on**.

If Canva is not listed, add it as a custom connector:

1. Go to **Customize** → **Connectors**.
2. Click **+ Add** → **Add custom connector**.
3. Enter the name `Canva` and the URL `https://mcp.canva.com/mcp`.
4. Sign in.
5. Click **Add**.

**Claude Code.** If you log in to Claude Code with your claude.ai account, connectors you added on
claude.ai appear automatically; check with `/mcp`. To add Canva directly, use Claude Code's
documented `claude mcp add --transport http` syntax with Canva's documented server URL:

```
claude mcp add --transport http --scope user canva https://mcp.canva.com/mcp
```

Then restart or resume Claude Code, run `/mcp`, select **canva**, and finish the sign-in in your
browser.

**Do not install the Canva *Dev* MCP server** (`npx @canva/cli mcp`). It is for building Canva apps
and cannot edit designs.

**Canva plan.** The free plan works, with workarounds; Canva Pro is recommended for print. Two
limits were observed in 2026-10 and may change:

- The free plan's resize quota runs out quickly.
- Regular-quality exports downsampled images below print resolution.

On the free plan, start from a design that is already at the print size, and download **PDF Print**
from the Canva editor for the print file.

## Without Canva

The PPTX route uses the same PLAN:

1. The planner writes a plan-spec JSON.
2. `build_pptx.py` turns it into an editable `.pptx` at the exact print size. Text comes from your
   wording slots, and figures are placed at the right resolution.
3. The script reports any text below the size floor, any image below 150 PPI, and anything outside
   the page.

Open the result in PowerPoint, Keynote or LibreOffice, or upload it to Canva later. Planning, text
editing, figures, verification and review all work without Canva.

## How to handle PDFs and figures

- **Give the vector PDFs of your figures** (what LaTeX includes), not screenshots.
  `export_figs.py` renders them at 6000 px on the long side, which is ≥ 150 PPI up to about 1 m of
  placed width. It can also write SVG.
- **Paper as .tex is best.** A paper PDF also works: text is extracted, and locators become "page,
  extracted line".
- **Text inside figures** is checked at print scale. If it is below the floor (default 24 pt), the
  skill writes a re-plot prompt for whoever has your plotting scripts. That prompt keeps the same
  plots, makes the text bigger, and leaves the paper figures byte-identical.
- **For the print file**, export the best quality available: Canva "PDF Print" or pro quality. Then
  run `check_export.py`, which checks size, PPI, text size, fonts, QR and margins.

## What to put in your planning prompt

Copy this, fill it in, and paste it into the chat. Anything you leave blank becomes a question, not
a guess.

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

## Pre-print review of an existing poster

The poster does not need to have been made with this skill, and any format works. Give:

- the poster: a PDF, a Canva link (exported to PDF/PNG through the Canva MCP first), a PPTX/ODP/Keynote
  file (converted with LibreOffice, or Keynote on macOS), or a PNG/JPG;
- the paper;
- the venue's poster-rules page.

> Review my poster before printing: poster.pdf, paper paper.tex, venue rules https://… — is it ready
> for A0?

You get **one Markdown notes file**:

```
poster_review_<YYYY-MM-DD>/
├── REVIEW.md        summary at the top, then one section per finding with its crop
├── crops/           full.png + one PNG per finding (before/after pairs when a fix was applied)
└── 01_visitor.md …  optional lens appendices, linked from REVIEW.md
```

`REVIEW.md` starts with a **summary**: the verdict (ready to print / fix first), the number of
must-fix, should and nice findings, and the top fixes as a short ranked list. Each finding then gets
its own section with severity, location, evidence and fix, the poster crop it refers to, and
Accept / Reject checkboxes.

**Open `REVIEW.md` in a Markdown preview** — the crops only render there: in VS Code press
Cmd+Shift+V (Ctrl+Shift+V on Windows/Linux) or click "Open Preview"; Typora, Obsidian and GitHub also work.

The five lenses behind it:

- **visitor:** can an outsider follow it at 1–2 m?
- **print preflight:** size, PPI, text sizes, fonts, contrast, margins, QR decoding.
- **proofread + fidelity:** spelling, consistency, and every number traced to the paper.
- **venue rules:** quoted verbatim from the official page.
- **design critique:** eight criteria, with section crops.

Crops come from `scripts/render_crops.py`, which takes boxes as fractions of the page so the same box
works for a PDF, a PNG export or a converted PPTX. Nothing is edited during a review.

## Usage

- "Make an A0 poster from my paper; here is the filled planning prompt."
- "Connect Canva and build option B from the plan on a copy."
- "Turn the introduction paragraph into labelled rows — stick to the paper wording."
- "Are the figures big enough for A0? Re-export them."
- "Is my poster ready to print?"

The skill triggers on research poster, conference poster, academic poster, paper to poster, Canva
poster, poster review, pre-print check, poster preflight, and "is my poster ready to print".

## What it checks that people miss

- Figures exported by a "standard" PDF download land near 100 PPI even when the uploads were 5000 px.
- Tick labels that collide at poster scale (e.g. "1020" for adjacent ticks 10 and 20) and legends that print at 15 pt.
- A number that is true for one model or dataset, printed beside a plot that shows several.
- A headline number copied from a slide instead of re-derived from the paper.
- Light data colours used as text (3.1:1 contrast) and logos 5 mm from the trim.
- Venue size assumed from memory rather than quoted from the official page.
- Canva quirks: new text is 16 px black, fonts can't be set over MCP, element IDs change on every
  copy, and there is no delete-page operation.

## Repository layout

```
academic-poster/
├── .claude-plugin/{plugin.json, marketplace.json}
├── agents/            poster-planner · poster-builder · poster-text-editor · poster-review-visitor-lens
├── skills/academic-poster/
│   ├── SKILL.md
│   ├── references/    canva-mcp-setup · canva-mcp-recipe · canva-mcp-gotchas · pptx-route ·
│   │                  figures-and-pdf · planning-prompt · wording-fidelity · layout-and-typography ·
│   │                  pre-print-review
│   ├── scripts/       export_figs · verify_wording · check_claims · check_export ·
│   │                  render_script_text · build_pptx · render_crops
│   └── templates/     PLAN-template.md · plan-spec.example.json · wording.template.json ·
│                      media.template.json · poster-rules.template.md · REVIEW-template.md
├── README.md · LICENSE · CONTRIBUTING.md
```

## Scripts

Every script prints JSON and supports `--help`. Exit codes: 0 = pass, 1 = checks failed,
2 = skipped because a dependency is missing.

```bash
S=skills/academic-poster/scripts
python3 $S/export_figs.py figures/*.pdf --out assets/figs --svg --placed-cm 40
python3 $S/verify_wording.py wording.json --source paper.tex
python3 $S/check_claims.py --poster wording.json --source paper.tex --registered claims.json
python3 $S/check_export.py poster.pdf --size A0 --min-pt 24 --qr-url https://example.org --contrast
python3 $S/render_script_text.py rows.json --out sample.png --dpr 3
python3 $S/build_pptx.py plan-spec.json --wording wording.json --media media.json --out poster.pptx
python3 $S/render_crops.py --poster poster.pdf --out-dir poster_review_2026-10-04/crops --crops crops.json --grid 3x2
```

## Requirements

- Python ≥ 3.8. The wording and claims checks need only the standard library.
- Optional:
  - `pymupdf`: PDF figures, PDF papers and `check_export.py`.
  - `python-pptx`: the PPTX route.
  - `playwright` + `playwright install chromium`: non-Latin text rendering.
  - `opencv-python` or `pyzbar` + `pillow`: QR decoding.
  - `transformers`: tokenizing sample sentences.
  - `pillow` (or `pymupdf`): PNG/JPG posters in `render_crops.py`; LibreOffice (`soffice`) or, on
    macOS, Keynote: PPTX/ODP posters in a review.
- Canva MCP: optional. Behaviour notes were observed in 2026-10 and may change.

## Scope

This skill helps prepare a poster. It does not replace reading the venue's rules, your print shop's
requirements, or a phone scan of the QR on a printed proof. Font sizes, margin conventions and
viewing-distance models are rules of thumb, and the skill labels them as such. Canva's plans, menus
and MCP behaviour, and Claude's connector UI, change over time. Verify the setup steps against the
linked official pages.
