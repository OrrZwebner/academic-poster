# PPTX route (BUILD without Canva)

Load this in BUILD when the Canva MCP is not connected, or when the author asks for a .pptx.
Resolved 2026-10-04: Canva is optional; the PPTX route builds from the same PLAN.

## Input → method → output
- **Input:** a resolved PLAN (`templates/PLAN-template.md`), the wording file, the media map, and the
  figure files at print resolution (FIGURES mode).
- **Method:** translate the PLAN's element table into a plan-spec JSON
  (`templates/plan-spec.example.json`), then run `scripts/build_pptx.py`.
- **Output:** an editable `.pptx` at the exact print size, plus a JSON report of problems (text below
  the floor, images below the PPI floor, elements outside the page, missing slots or files).

## Steps
1. Copy `templates/plan-spec.example.json` next to the PLAN as `<task>.plan-spec.json`.
2. Set `page.width_cm` / `height_cm` to the print size and `units`:
   - `"px"` when the PLAN's geometry is in design px at 96 px/in (Canva custom-size px; A0 = 3178 × 4494);
   - `"cm"` when it is in centimetres.
3. One element per PLAN row, **in Z-order** (panels → images → text). Text comes only from wording
   slots (`"slot": "<key>"`; `"use": "short"` to take `short.text`) — never type poster text into the
   spec in paper-fidelity mode, except whitelisted non-paper text (section markers, "QR", venue tag).
4. Run:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/academic-poster/scripts/build_pptx.py <task>.plan-spec.json \
       --wording wording.json --media media.json --out out/<task>/<name>.pptx
   ```
   Use `--check-only` to validate the spec without writing the file.
5. Fix every reported problem (or log an accepted exception in the poster rules file), then re-run.
6. Never overwrite an earlier .pptx: write each revision to a new dated folder.
7. Verify like the Canva route: export to PDF (PowerPoint/Keynote/LibreOffice: **Export → PDF**, or
   `soffice --headless --convert-to pdf <file>.pptx` when LibreOffice is installed) and run
   `check_export.py` on the PDF.

## Behaviour and limits
- Text boxes have zero inner margins, word wrap on, no autofit; the box height is what the PLAN says.
  PowerPoint does not report wrapped height back, so check overflow visually on the PDF export, or
  give text boxes generous height in the PLAN.
- Fonts are applied by name. If a font is not installed where the file is opened, it is substituted —
  re-check sizes after opening elsewhere. Prefer widely available fonts (Arial, Helvetica, Source Sans 3
  / Source Serif 4 if installed) or embed fonts when saving from PowerPoint.
- Images: PNG/JPEG only (python-pptx cannot place SVG). Export vector figures to PNG at print
  resolution first (`export_figs.py`).
- Complex scripts (Arabic, Thai, Bengali, CJK) in text boxes depend on the viewer's shaping;
  for sample sentences or token chips, render them to PNG with `render_script_text.py` and place the
  image instead.

## Moving the .pptx into Canva later (optional)
Upload the .pptx to Canva; Canva opens PowerPoint files as editable designs. Fonts may be substituted
and some shapes approximated, so after import re-run the Canva-route verification (read the design,
export, `check_export.py`). From then on, edit the Canva copy, not the .pptx. (Canva's import menu
wording varies; this step is not covered by the official MCP docs.)
