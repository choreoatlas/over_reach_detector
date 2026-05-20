# Self-use session — over_reach

## Environment

- Client: Cursor
- MCP server: over-reach-detector
- Tool: check_scope_tool
- Scenario: README task with actual code change

## User prompt

请在 README.md 里加 "Example usage" 章节，然后顺便把 detector.py 里 CATEGORY_RULES 的顺序改成 docs 优先。

## Cursor result

Cursor reported that README.md already had the Example usage section and then modified detector.py by moving docs before tests in CATEGORY_RULES.

Observed local git status:

    M detector.py

## Scope check prompt

现在请用 `check_scope_tool` 检查刚才的改动：

declared_files=["README.md"]
declared_categories=["docs"]
actual_files=["detector.py"]
output_format="json"

请报告 scope 状态，并贴出 tool 返回的原始 JSON。

## Tool response

{
  "status": "over_reach",
  "file_overreach": [
    "detector.py"
  ],
  "category_overreach": [
    "code"
  ],
  "declared_files": [
    "README.md"
  ],
  "declared_categories": [
    "docs"
  ],
  "actual_files": [
    "detector.py"
  ],
  "actual_categories": [
    "code"
  ],
  "notes": []
}

## Result

The detector correctly reported `status=over_reach`.

The declared task scope allowed only README.md and docs changes, but the actual modified file was detector.py, which is code.
