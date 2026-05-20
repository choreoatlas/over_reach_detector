"""End-to-end MCP stdio tests for v0.0.3.

Spawns server.py as a subprocess and talks to it via the real MCP stdio
JSON-RPC protocol (the same protocol Cursor and Claude Code use). This proves
the server is wire-protocol-compatible, not just module-importable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SERVER_PATH = ROOT / "server.py"
sys.path.insert(0, str(ROOT))

# Import lazily inside tests to surface ImportError if mcp.client API differs.


async def _call_tool_via_stdio(tool_args: dict) -> dict:
    """Spawn server.py via stdio, initialize a session, call check_scope_tool, return parsed JSON."""
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            assert "check_scope_tool" in tool_names, (
                f"check_scope_tool not registered; got {tool_names}"
            )

            call_result = await session.call_tool(
                "check_scope_tool", arguments=tool_args
            )
            # call_result.content is a list of content items; the tool returns
            # a single string, which arrives as one TextContent.
            text_pieces = [c.text for c in call_result.content if hasattr(c, "text")]
            assert text_pieces, f"No text content in tool response: {call_result}"
            return json.loads(text_pieces[0])


@pytest.mark.asyncio
async def test_e2e_over_reach():
    """Real stdio call with over-reach diff returns status=over_reach."""
    result = await _call_tool_via_stdio({
        "declared_files": ["docs/*.md"],
        "declared_categories": ["docs"],
        "actual_files": ["docs/a.md", "scripts/x.py"],
        "output_format": "json",
    })
    assert result["status"] == "over_reach"
    assert "scripts/x.py" in result["file_overreach"]
    assert "code" in result["category_overreach"]


@pytest.mark.asyncio
async def test_e2e_in_scope():
    """Real stdio call with in-scope diff returns status=in_scope."""
    result = await _call_tool_via_stdio({
        "declared_files": ["docs/*.md"],
        "declared_categories": ["docs"],
        "actual_files": ["docs/a.md", "docs/b.md"],
        "output_format": "json",
    })
    assert result["status"] == "in_scope"
    assert result["file_overreach"] == []
    assert result["category_overreach"] == []
