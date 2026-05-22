# Over-Reach Detector (MCP server)

<!-- mcp-name: io.github.choreoatlas/over-reach-detector -->

Detect and report when AI coding agents change files outside their declared task scope. Designed to plug into Cursor, Claude Code, and other MCP-compatible AI coding agents via the standard stdio transport.

Compares two things:

1. **Declared scope** — the files (as fnmatch globs) and categories (tests, docs, infra, config, code) the task is allowed to touch.
2. **Actual diff** — the files the AI actually modified.

If the actual diff exceeds the declared scope, the tool returns `status=over_reach` and lists the offending files and categories.

## What this tool does and does not do

`over-reach-detector` is an audit/disclosure tool, not a sandbox and not a blocker.

It compares a declared task scope with the actual files/categories changed by an AI coding agent. If the actual changes exceed the declared scope, it reports that mismatch.

It does not prevent file writes by itself. It does not decide whether to revert, approve, or block a change. The caller remains responsible for enforcement, rollback, or human review.

## Install

From PyPI:
```bash
pip install over-reach-detector
```

From source:
```bash
git clone https://github.com/choreoatlas/over_reach_detector
cd over_reach_detector
pip install -e .
```

## Quick start

Run all tests: `python -m pytest -v`

Try the CLI directly: `python -m over_reach_detector.detector --input fixtures/example_pr_1.json --format markdown`

## Use as MCP server

Start the server (stdio transport): `over-reach-detector` (or `python -m over_reach_detector.server` from source)

Register with your AI agent:

- **Cursor**: in `~/.cursor/mcp.json`, add (after `pip install over-reach-detector`):

```json
{
  "mcpServers": {
    "over-reach-detector": {
      "command": "over-reach-detector"
    }
  }
}
```

  Dev / from source: use `"command": "python", "args": ["-m", "over_reach_detector.server"]` (run from repo root).

- **Claude Code**: after `pip install over-reach-detector`, run `claude mcp add over-reach-detector over-reach-detector` (writes to `~/.claude.json`). Dev / from source: `claude mcp add over-reach-detector /absolute/path/to/python -m over_reach_detector.server`.

## The tool

`check_scope_tool` takes:

- `declared_files`: list of fnmatch globs (e.g. `["docs/*.md", "tests/*.py"]`)
- `declared_categories`: subset of `["tests", "docs", "infra", "config", "code"]`
- `actual_files`: list of file paths the AI modified
- `output_format`: `"json"` (default) or `"markdown"`

Returns a report with:

- `status`: `in_scope` (within declared scope) | `over_reach` (reported mismatch) | `empty`
- `file_overreach`: files not matching any declared glob
- `category_overreach`: inferred categories outside the declared set

## Scope discipline

**Current scope**: CLI + MCP stdio server + 1 tool. Python only. fnmatch-based globs.

**Out of scope (forbidden)**: code quality review, security audit, completeness governance, languages other than Python, multi-tool MCP servers, HTTP/SSE transport, GitHub Actions integration. These are deliberately deferred to later versions or never.

## Example usage

Call `check_scope_tool` directly from Python (same logic the MCP server exposes):

```python
import json
from over_reach_detector import server

result = server.check_scope_tool(
    declared_files=["docs/*.md"],
    declared_categories=["docs"],
    actual_files=["docs/a.md", "scripts/extra.py"],
    output_format="json",
)

report = json.loads(result)
print(report["status"])          # "over_reach"
print(report["file_overreach"])  # ["scripts/extra.py"]
```

## License

MIT — see [LICENSE](LICENSE).
