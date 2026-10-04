# Canva MCP gotchas and workarounds

Load this when a Canva call fails or returns something unexpected, and skim it before a large BUILD.
Every row was **observed 2026-10 and may change** — if the MCP behaves differently now, trust what it
does and note the difference.

| Symptom | Cause | Workaround |
|---|---|---|
| Server added but not in the session's tool list | MCP config is read at session start | Restart or resume the session, authenticate via `/mcp`, verify with one read-only call |
| `Free resize quota has been exceeded` | Free Canva plan | Never call `resize-design` on a free plan. Start from a design already at print size, or copy an already-sized page. Pro removes the limit |
| Print PDF holds figures well below 150 PPI although sources are high-resolution | Regular/"PDF Standard" export downsamples (≤ 800 px observed) | Export at pro quality, or the author downloads **PDF Print** from the editor; re-run `check_export.py` |
| `Only a single operation per merge request is supported` | `merge-designs` limit | One operation per call |
| `Not allowed to access design / asset / folder item` | The item belongs to someone else | Read-only reference; never edit; `move-item-to-folder` also fails on such items — ask the owner |
| `media bundle not found` on `insert_fill` | Some media inside a design cannot be re-inserted | Export the element on white and on black backgrounds, recover alpha by difference matting, re-upload, record the new media ID |
| `read-design` result exceeds the output limit | Whole `design_content` of a dense poster | Filter fields and pages; if saved to a file, read it by character ranges |
| Headings read as "ntroduction", "ethodology" | Drop-cap first letter is a separate element (often an image) | Match elements by geometry + remaining text, not by the full heading |
| Element IDs not found on a copied page | IDs differ per copy and per page | Take IDs from the document returned by the latest edit call |
| New text is 16 px black in the heading font | `add_text` defaults; fonts cannot be set via MCP | `format_text` after every `add_text`; author applies fonts with **Copy style** |
| Font size rejected or rounded | Integer sizes only | Round, then re-check the text floor |
| Image zoomed 1.2–4× after a swap | `update_fill` (+ `crop_media`) | Delete + `insert_fill` (cover-fits), or verify the crop visually and reset it |
| Colour adjustments lost after re-inserting an image | Image adjustments are not exposed by `read-design` | Export the adjusted render and upload that as new media |
| Thumbnail shows old content / "No stored thumbnail" | Stale thumbnails | Verify with `design_content` or a fresh export |
| No way to delete a page | No delete-page operation | Ask the user to delete it by hand; do not work around it |
| Layout scrambled after `resize-design` | Resize shifts blocks (≈ +130 px vertical observed), displaces header items, moves texts into wrong rows | Re-place every element at source × s, restore minimums (`layout-and-typography.md`, dual-size resize) |
| `edits_unverified` status | Large edits | Normal; verify from the returned document |
| Edit refused by an auto-mode/permission classifier | Harness, not Canva | Retry once; continue other work; ask the user if it persists |
| Text overflows its box after a batch | Auto height and wrapping | Check `top + height ≤ bottom` after every batch |
| `generate-image` errors after many calls | Rate limit (~10 per minute) | Wait a minute; batch requests |

## Things that cost time in the source project

- Two parallel builds of the same target: when a better route succeeds, stop the superseded agent and
  record which design is main in the poster rules file.
- Falling back to "please do these steps by hand": automate through the MCP; involve the user only for
  real decisions, plan upgrades, page deletion, or font application.
- Notes naming the wrong "main" design: re-verify the live state with `read-design` before planning.
- An element-by-element MCP rebuild of a whole poster (to change size without resize) loses fonts and
  some media: use it only when resize is unavailable and copying an already-sized page is impossible.
