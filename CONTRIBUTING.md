# Contributing

## Layout rules
- `skills/academic-poster/SKILL.md` is loaded on **every** invocation. Keep it a router plus hard
  rules, under ~500 lines (currently ~230). Long or volatile material (Canva quirks, checklists,
  templates) belongs in `references/`, which load only when needed.
- SKILL.md frontmatter may contain only `name`, `description`, `license`, `compatibility`,
  `metadata`, `allowed-tools`. Any other key makes claude.ai uploads and packaging fail.
- Components are declared once: `skills/` and `agents/` are auto-discovered. Do not list them in
  `plugin.json` or in the marketplace entry.
- Scripts: Python ≥ 3.8 syntax (no `list[int]`-style hints, no `match`), stdlib first, optional
  dependencies imported lazily, JSON on stdout, `--help` that documents every option, exit codes
  0 pass / 1 fail / 2 skipped (dependency missing).
- No personal material in examples: synthetic papers, numbers and IDs only.

## Tests
The test suite and CI live in `tests/` and `.github/workflows/test.yml` (Python 3.8 and 3.12).
Run locally before a pull request:

```bash
python3 tests/make_fixtures.py && python3 tests/run_tests.py
```

Fixtures are synthetic and generated (nothing binary is committed). Their expected values are derived
independently of the scripts, by hand arithmetic recorded in `tests/make_fixtures.py` and
`tests/README.md`. **Never update an expected value to match new output**: if a value moves, the code
is wrong until proven otherwise. Tests whose optional dependency is missing must SKIP, not fail.

## Releases
1. Bump `version` in `.claude-plugin/plugin.json` and in the SKILL.md `metadata`.
2. Tag `vX.Y.Z` and push the tag. The release workflow builds `academic-poster.zip` with `SKILL.md`
   one level deep (the archive for claude.ai uploads).
3. Download the zip and confirm `academic-poster/SKILL.md` sits at the top level.

## Volatile sources — re-check before each release
| Source | What to verify |
|---|---|
| https://www.canva.com/help/mcp-agent-setup/ | Server URL `https://mcp.canva.com/mcp`, connector button names, plan requirements |
| https://claude.com/connectors/canva | Canva is still in the connector directory; tool list |
| https://code.claude.com/docs/en/mcp | `claude mcp add --transport http` syntax, scopes, `/mcp` auth flow, claude.ai connector sync |
| https://support.claude.com/en/articles/11175166 | Custom connector steps and plan availability |
| https://www.canva.dev/docs/apps/dev-mcp-server/ | Still the app-development server (the one NOT to install) |
| Canva pricing/help pages | Resize quota and export-quality limits on the free plan |
| Canva MCP behaviour in `references/canva-mcp-*.md` | Marked "observed 2026-10, may change": re-test with a scratch design |
