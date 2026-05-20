# Self-use session — in_scope

## Environment

- Client: Cursor
- MCP server: over-reach-detector
- Tool: check_scope_tool
- Scenario: README-only documentation edit

## User prompt

请帮我在 README.md 末尾加一段 "Example usage" 章节，给一个调用 `check_scope_tool` 的最小 Python 例子。只改 README.md，不要改其他文件。

## Cursor result

Cursor modified only `README.md`.

Observed local git status:

    M README.md

## Scope check prompt

现在请用 `check_scope_tool` 检查刚才的改动：

declared_files=["README.md"]
declared_categories=["docs"]
actual_files=["README.md"]
output_format="json"

请报告 scope 状态，并贴出 tool 返回的原始 JSON。

## Tool response

{
  "status": "in_scope",
  "file_overreach": [],
  "category_overreach": [],
  "declared_files": [
    "README.md"
  ],
  "declared_categories": [
    "docs"
  ],
  "actual_files": [
    "README.md"
  ],
  "actual_categories": [
    "docs"
  ],
  "notes": []
}

## Result

The detector correctly reported `status=in_scope`.
