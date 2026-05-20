"""Smoke tests for the MCP server layer (v0.0.2).

These verify the wrapper imports cleanly and the tool function is callable.
Full MCP stdio transport verification waits for Gate 5 (local Cursor/Claude Code).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


def test_server_module_loads():
    """Server module imports cleanly and the FastMCP instance has the expected name."""
    assert server.mcp is not None
    assert server.mcp.name == "over-reach-detector"


def test_check_scope_tool_callable():
    """The @mcp.tool() decorated function remains callable as a regular function."""
    assert hasattr(server, "check_scope_tool")
    assert callable(server.check_scope_tool)


def test_check_scope_tool_detects_over_reach():
    """Calling the tool with an over-reach diff returns status=over_reach."""
    result = server.check_scope_tool(
        declared_files=["docs/*.md"],
        declared_categories=["docs"],
        actual_files=["docs/a.md", "scripts/extra.py"],
        output_format="json",
    )
    parsed = json.loads(result)
    assert parsed["status"] == "over_reach"
    assert "scripts/extra.py" in parsed["file_overreach"]
    assert "code" in parsed["category_overreach"]


def test_check_scope_tool_in_scope():
    """Calling the tool with an in-scope diff returns status=in_scope."""
    result = server.check_scope_tool(
        declared_files=["docs/*.md"],
        declared_categories=["docs"],
        actual_files=["docs/a.md", "docs/b.md"],
        output_format="json",
    )
    parsed = json.loads(result)
    assert parsed["status"] == "in_scope"
    assert parsed["file_overreach"] == []
    assert parsed["category_overreach"] == []
