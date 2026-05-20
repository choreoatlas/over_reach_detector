# 越权检测 v0.0.1 — Authority Boundary Detector

Detects when AI code changes exceed declared task scope. Compares declared files + categories vs. actual diff.

## Quick start

Run tests: `python -m pytest tests/test_smoke.py -v`

Run detector: `python detector.py --input fixtures/example_pr_1.json --format markdown`

## Input format

Provide a JSON file with two top-level keys:

- `task_spec`: contains `declared_files` (list of fnmatch globs) and `declared_categories` (list of category names: tests, docs, infra, config, code).
- `actual_diff`: contains `files` (list of file paths).

See `fixtures/example_pr_1.json` for a worked example.

## Output

- `status`: `in_scope` | `over_reach` | `empty`
- `file_overreach`: files modified but not matching any glob in `declared_files`
- `category_overreach`: categories inferred from actual files but not in `declared_categories`
- Exit code: 1 if `over_reach`, 0 otherwise

## Scope (v0.0.1)

In scope: file scope + category scope detection. Python only. CLI only. fnmatch-based globs.

Out of scope (forbidden): code quality review, security audit, completeness governance, languages other than Python, MCP server (that is v0.0.2).
