# 越权检测 — Authority Boundary Detector (MCP server)

Detects when AI code changes exceed declared task scope. Designed to plug into Cursor, Claude Code, and other MCP-compatible AI coding agents via the standard stdio transport.

Compares two things:

1. **Declared scope** — the files (as fnmatch globs) and categories (tests, docs, infra, config, code) the task is allowed to touch.
2. **Actual diff** — the files the AI actually modified.

If the actual diff exceeds the declared scope, the tool returns `status=over_reach` and lists the offending files and categories.

## Quick start

Install: `pip install -r requirements.txt`

Run all tests: `python -m pytest -v`

Try the CLI directly: `python detector.py --input fixtures/example_pr_1.json --format markdown`

## Use as MCP server

Start the server (stdio transport): `python server.py`

Register with your AI agent:

- **Cursor**: edit `~/.cursor/mcp.json` and add an entry under `mcpServers` keyed `over-reach-detector` with `command: "python"` and `args: ["/absolute/path/to/server.py"]`.
- **Claude Code**: run `claude mcp add over-reach-detector /absolute/path/to/python /absolute/path/to/server.py` (writes to `~/.claude.json`).

## The tool

`check_scope_tool` takes:

- `declared_files`: list of fnmatch globs (e.g. `["docs/*.md", "tests/*.py"]`)
- `declared_categories`: subset of `["tests", "docs", "infra", "config", "code"]`
- `actual_files`: list of file paths the AI modified
- `output_format`: `"json"` (default) or `"markdown"`

Returns a report with:

- `status`: `in_scope` (safe) | `over_reach` (block) | `empty`
- `file_overreach`: files not matching any declared glob
- `category_overreach`: inferred categories outside the declared set

## Scope discipline

**Current scope**: CLI + MCP stdio server + 1 tool. Python only. fnmatch-based globs.

**Out of scope (forbidden)**: code quality review, security audit, completeness governance, languages other than Python, multi-tool MCP servers, HTTP/SSE transport, GitHub Actions integration. These are deliberately deferred to later versions or never.

## Example usage

Call `check_scope_tool` directly from Python (same logic the MCP server exposes):

```python
import json
import server

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
