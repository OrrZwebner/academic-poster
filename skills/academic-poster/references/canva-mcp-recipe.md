# Canva MCP build recipe (BUILD, Canva route)

Load this before any `edit-design`, `copy-design` or `merge-designs` call. Tool and operation names are
as seen in 2026-10 sessions; behaviour is **observed 2026-10, may change**. If a call's schema differs,
follow the schema the tool reports and note the difference in the build report.

## Transaction flow

1. **Copy first.** `copy-design` the source and give it the name the PLAN specifies (unless the PLAN
   names an existing working page). Never edit an original, an archived design, or anyone else's design.
2. **Open.** `read-design` with `open_transaction: true` and `filter.fields: ["page_metadata"]` →
   page IDs and a `transaction_id`. For content ask for `design_content` (and `thumbnails`) only on
   the pages you need: a whole dense poster overflows the tool output. If a result is saved to a file
   because it is too large, read it by character ranges.
3. **Edit.** `edit-design` with `transaction_id`, `page_index`, `operations` (≤ 15 per call) and
   `finalize: "keep_open"`.
4. **Verify after every batch** (section "Verification loop").
5. **Commit.** `edit-design` with `finalize: "commit"` — only on the authorised copy/pages and only
   under the approval style stored in the poster rules file. A read-only transaction with no edits:
   cancel/close it rather than committing.

## Operations used

| Operation | Use | Notes |
|---|---|---|
| `insert_shape` | panels, bands, rules, circles, arrows | `path` + viewBox; `color`, `stroke_color`, `stroke_weight`; `corner_rounding` for rounded boxes |
| `insert_fill` | place an uploaded image | `page_id`, `asset_type: "image"`, `asset_id` = media ID, `left`, `top`, `width`, `height` = width × px_h / px_w, `alt_text`; cover-fits |
| `add_text` | new text box | creates 16 px black text in the heading font — always follow with `format_text` |
| `format_text` | size, colour, weight, alignment, line height | `font_size` (integers only), `color`, `font_weight`, `text_align`, `line_height` 1.2–1.3; take the locator from the returned document |
| `find_and_replace` | fix wording inside an existing box | keeps the box's style |
| `update_fill` / `crop_media` | swap an image | observed to zoom the image (1.2–4×); prefer delete + `insert_fill` |
| `update_stroke_properties` | border colour/width | |
| `layer_element` | move to back/front | Z-order is otherwise insertion order |
| delete element | remove an element | there is **no delete-page** operation: ask the user to delete pages by hand |
| `add_page`, `reorder_page` | pages | never reorder or delete the author's pages unless the PLAN says so |

Other tools: `merge-designs` (one operation per call; needs approval), `resize-design` (quota/Pro;
see gotchas), `get-export-formats` + `export-design` (PNG width; PDF quality regular/pro),
`create-upload-url` / `upload-asset-from-url` (new media), `get-assets`, `search-designs`,
`list-folder-items`, `search-folders`, `create-folder`, `move-item-to-folder` (fails on items you do not
own), `list-comments`.

## Path library (insert_shape)

| Shape | path | viewBox |
|---|---|---|
| rectangle / rounded box | `M0 0H100V100H0z` (+ `corner_rounding`) | 100 × 100 |
| right arrow | `M0 15H38V2L60 20L38 38V25H0Z` | 60 × 40 |
| circle | `M50 0A50 50 0 1 1 50 100A50 50 0 1 1 50 0Z` | 100 × 100 |

## Z-order

Insertion order = stacking order. Insert in this order within a batch: background panels and bands →
images → text. To push an element back afterwards use `layer_element` "back".

## Text rules

- One text role per box (label vs body vs caption): the MCP formats whole boxes, and the author sets
  fonts in Canva by hand (select a body text → **Copy style** → paint onto the new box).
- Integer font sizes only: round, then re-check the floor (24 pt at print = 32 px when the design is
  at print size; F3 in `figures-and-pdf.md`).
- Native list formatting can break hyphenation; a manual bullet column (one box per bullet glyph, one
  per text, hanging indent) is more robust.
- Unbreakable ranges and compounds: U+2060 word joiners around an en dash ("25⁠–⁠2,500"), U+2011
  non-breaking hyphen in headings. Keep the plain characters in the wording file.

## Verification loop (after every batch)

1. Read the returned `document`: every element's `left`, `top`, `width`, `height`. Text height is
   computed by Canva, so re-position whatever sits below a text box from its **real** height.
2. For every text: `top + height ≤ container bottom` (F8). Wrapped lines are the usual overflow — widen
   the box, move it, or shorten the text (shortening = a new wording slot + verification).
3. Images: `height / width` within 0.1% of `px_h / px_w`.
4. Look at the returned thumbnail, but trust `design_content` or a fresh export over thumbnails (they
   can be stale or missing).
5. `edits_unverified` status is normal for large batches: verify from the returned document instead.
6. Element IDs differ on every copied page and change after copies: always take IDs from the latest
   returned document, never from another page or an earlier session.

## Media

- Upload with `create-upload-url` (local file) or `upload-asset-from-url`; record `media_id` and
  source px in the media map (`templates/media.template.json`).
- Upload figures at print resolution (`figures-and-pdf.md`); prefer SVG for vector plots where the
  account accepts it.

## Exports

- `get-export-formats` first. For viewing: PNG at width 1700. For crops: PNG at full design width.
- For print: PDF at pro quality (or the author downloads **PDF Print** in the editor). Regular quality
  downsampled images in 2026-10.
- Download every export into a **new** dated folder; never overwrite earlier exports. View the PNG.

## Approval styles (stored in the poster rules file)

- **Live in Canva:** after the author approves the content choice, keep a backup page or copy,
  commit, and report "Canva updated" — no PNG/PDF previews to approve.
- **Approve/reject Markdown:** write `REVIEW_modifications_<date>.md` with before/after crops per change
  and `[ ] Approve  [ ] Reject — note` per item; commit only approved items.
- **Ask once at PLAN (default):** the author approves the PLAN once (its OPEN DECISIONS answered);
  the builder then builds on the copy and commits without asking again, and reports what changed.
