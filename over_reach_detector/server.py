"""MCP server wrapper for over-reach-detector v0.0.2.

Exposes the v0.0.1 scope check as a single MCP tool that AI coding agents
(Cursor, Claude Code, etc.) can call before / after applying code changes.

Run (stdio transport):
    python server.py

Local AI agent config example (Cursor at ~/.cursor/mcp.json):
    {
      "mcpServers": {
        "over-reach-detector": {
          "command": "python",
          "args": ["/absolute/path/to/server.py"]
        }
      }
    }
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .detector import check_scope, report_to_json, report_to_markdown

mcp = FastMCP("over-reach-detector")


@mcp.tool()
def check_scope_tool(
    declared_files: list[str],
    declared_categories: list[str],
    actual_files: list[str],
    output_format: str = "json",
) -> str:
    """Check whether an AI's actual code diff exceeds the declared task scope.

    Call this BEFORE committing AI-generated changes to detect over-reach.

    Args:
        declared_files: fnmatch globs allowed for this task (e.g. ["docs/*.md", "tests/*.py"]).
        declared_categories: allowed category labels. One or more of: tests, docs, infra, config, code.
        actual_files: file paths actually modified by the AI.
        output_format: "json" (default, machine-parseable) or "markdown" (human-readable).

    Returns:
        Formatted scope report. The 'status' field is one of:
          - "in_scope" (safe to commit)
          - "over_reach" (BLOCK; review needed)
          - "empty" (no files changed)
    """
    task_spec = {
        "declared_files": declared_files,
        "declared_categories": declared_categories,
    }
    actual_diff = {"files": actual_files}
    report = check_scope(task_spec, actual_diff)
    if output_format == "markdown":
        return report_to_markdown(report)
    return report_to_json(report)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
