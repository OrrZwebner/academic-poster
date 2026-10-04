# Canva MCP setup (SETUP mode)

Load this in SETUP mode, or when the Canva tools are missing or failing to authenticate. Canva is
optional: without it, BUILD uses the PPTX route (`pptx-route.md`).

Sources (all fetched 2026-10-04; these pages change, so re-check them before relying on a step):
- Canva help, "MCP / agent setup": https://www.canva.com/help/mcp-agent-setup/ (redirect target of
  canva.dev/docs/connect/canva-mcp-server-setup). It could only be read through search snippets
  (the page returned a bot challenge), so the button names below are as quoted in those snippets.
- Anthropic connector directory, Canva: https://claude.com/connectors/canva
- Claude Code MCP docs: https://code.claude.com/docs/en/mcp
- Claude help, custom connectors via remote MCP: https://support.claude.com/en/articles/11175166
- Canva **Dev** MCP server (the wrong server for posters): https://www.canva.dev/docs/apps/dev-mcp-server/

## 1. Detect whether Canva is already connected

Look at the tool list for Canva design tools: names ending in `read-design`, `edit-design`,
`search-designs`, `export-design` (for example `mcp__canva__read-design` when the server was added as
`canva` in Claude Code, or a `claude_ai_Canva`-style prefix when it comes from a claude.ai connector).
- Present → verify with one read-only call (`search-designs` with a short query, or `read-design` on a
  design the user names). Success = SETUP done. Record the route as "Canva" in the poster rules file.
- Absent → offer the two routes below, or the PPTX route. Never block PLAN, TEXT-EDIT, FIGURES, VERIFY
  or REVIEW on Canva.

## 2. Route A — claude.ai, the Claude desktop app, or Cowork (recommended by Canva)

Canva's help page calls Claude connectors "the easiest and recommended way" and says they work on
web and desktop and are "only available to users on Claude paid plans" (snippet, 2026-10-04).

Steps (button names as quoted from Canva's help page; Claude's current UI may label the first menu
**Customize** or **Settings**):
1. In Claude, open **Connectors** (Canva's page: **Manage Connectors**).
2. Click **Browse Connectors**.
3. Find **Canva** and click **Connect**.
4. Sign in to Canva in the window that opens and allow access.
5. Back in Claude, make sure the Canva connector's toggle is **on** for the chat.

If Canva is not in the directory, add it as a custom connector (Claude help article 11175166):
**Customize > Connectors** → **+ Add** → **Add custom connector** → name `Canva`, URL
`https://mcp.canva.com/mcp` → authenticate → **Add**. That article lists custom connectors on Free,
Pro, Max, Team and Enterprise plans (Free: one custom connector). On Team/Enterprise an owner adds
connectors under **Organization settings > Connectors** first.

Claude Code picks these up too: per the Claude Code MCP docs, "If you've logged into Claude Code with
a claude.ai account, MCP servers you've added in claude.ai … are automatically available in Claude
Code". Check with `/mcp`.

## 3. Route B — Claude Code, added directly

The Claude Code docs give the generic syntax `claude mcp add --transport http <name> <url>`, and Canva
documents the remote server URL `https://mcp.canva.com/mcp`. Combining them (an inference, not a
command printed on Canva's page):

```
claude mcp add --transport http canva https://mcp.canva.com/mcp
```

- Add `--scope user` to make it available in every project (default scope `local` = this project only;
  `project` writes `.mcp.json` for the team).
- The server is read at session start: restart or resume Claude Code, then run `/mcp`, select
  **canva**, and complete the browser sign-in (OAuth). `claude mcp login canva` is the CLI equivalent
  per the docs.
- Verify with one read-only call (section 1).
- Naming the server `canva` makes the tool names `mcp__canva__*`, which is what the agent files mention.

## 4. Do NOT install the Canva Dev MCP server

`claude mcp add canva-dev -- npx -y @canva/cli@latest mcp` (canva.dev/docs/apps/dev-mcp-server) is for
**building Canva apps**. It cannot read or edit designs. If the user has it, it is not a substitute.

## 5. Canva plan (record in the poster rules file)

Observed 2026-10, may change; verify on Canva's pricing/help pages:
- Free plan: `resize-design` quota ran out after 2 resizes ("Free resize quota has been exceeded").
- Regular-quality export downsampled embedded images (≤ 800 px wide observed) and a "PDF Standard"
  download held figures well below 150 PPI at A0. Pro-quality export was refused on the free account and
  worked after upgrading.
- A snippet says the MCP is "available with Canva Pro, Teams, Business, Nonprofit" — **unverified**;
  the source project used it on a free account for editing.

Policy (resolved 2026-10-04): support the free plan with workarounds, recommend Pro for print.
Free-plan workarounds: never call resize — start from a design already at the print size (create it
with the custom size from `layout-and-typography.md`) or copy an already-sized page; upload figures
at final size; for the print file, ask the author to download **PDF Print** from the Canva editor
(Share → Download) and run `check_export.py` on it.

## 6. Rate limits and errors seen

- `generate-image`: about 10 calls per minute (observed).
- "Not allowed to access design/asset/folder item": the design belongs to someone else. Treat it as a
  read-only reference; copy it into the user's own account only if they own the right to.
- An auto-mode or permission classifier refusing an edit call is a harness event, not Canva: retry
  once, then ask the user.
