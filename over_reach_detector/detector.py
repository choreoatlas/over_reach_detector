"""
越权检测 v0.0.1 — Authority Boundary Detector for AI code changes.

Compares a declared task scope (file globs + category labels) to the actual
diff of files changed, and reports any over-reach.

Categories are inferred from file paths using simple glob rules.

Usage:
    python detector.py --input fixtures/example_pr_1.json --format markdown
    python detector.py --input fixtures/example_pr_1.json --format json
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

DOCS_META_FILENAMES: frozenset[str] = frozenset(
    {
        "LICENSE",
        "LICENSE.md",
        "LICENSE.txt",
        "COPYING",
        "NOTICE",
        "AUTHORS",
        "CONTRIBUTORS",
        "CHANGELOG",
        "CHANGELOG.md",
    }
)


def _docs_meta_path_patterns() -> tuple[str, ...]:
    patterns: list[str] = []
    for name in sorted(DOCS_META_FILENAMES):
        patterns.append(name)
        patterns.append(f"*/{name}")
    return tuple(patterns)


CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("tests", ("test_*.py", "*_test.py", "tests/*")),
    ("docs", (*_docs_meta_path_patterns(), "*.md", "docs/*", "README*")),
    ("infra", (".github/*", "Dockerfile", "*.dockerfile")),
    ("config", ("*.yml", "*.yaml", "*.toml", "*.json", "*.ini", "*.cfg")),
]
DEFAULT_CATEGORY = "code"


def infer_category(path: str) -> str:
    for cat, patterns in CATEGORY_RULES:
        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern):
                return cat
    return DEFAULT_CATEGORY


def match_any_glob(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


@dataclass
class ScopeReport:
    status: str  # "in_scope" | "over_reach" | "empty"
    file_overreach: list[str] = field(default_factory=list)
    category_overreach: list[str] = field(default_factory=list)
    declared_files: list[str] = field(default_factory=list)
    declared_categories: list[str] = field(default_factory=list)
    actual_files: list[str] = field(default_factory=list)
    actual_categories: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def check_scope(task_spec: dict, actual_diff: dict) -> ScopeReport:
    declared_files: list[str] = list(task_spec.get("declared_files", []))
    declared_categories: set[str] = set(task_spec.get("declared_categories", []))
    actual_files: list[str] = list(actual_diff.get("files", []))
    actual_categories: set[str] = {infer_category(f) for f in actual_files}

    file_overreach: list[str] = []
    if declared_files:
        file_overreach = [f for f in actual_files if not match_any_glob(f, declared_files)]

    category_overreach: list[str] = []
    if declared_categories:
        category_overreach = sorted(actual_categories - declared_categories)

    if not actual_files:
        status = "empty"
    elif file_overreach or category_overreach:
        status = "over_reach"
    else:
        status = "in_scope"

    notes: list[str] = []
    if not declared_files:
        notes.append("declared_files empty — file scope check skipped")
    if not declared_categories:
        notes.append("declared_categories empty — category scope check skipped")

    return ScopeReport(
        status=status,
        file_overreach=sorted(file_overreach),
        category_overreach=sorted(category_overreach),
        declared_files=sorted(declared_files),
        declared_categories=sorted(declared_categories),
        actual_files=sorted(actual_files),
        actual_categories=sorted(actual_categories),
        notes=notes,
    )


def report_to_json(report: ScopeReport) -> str:
    return json.dumps(asdict(report), indent=2, ensure_ascii=False)


def report_to_markdown(report: ScopeReport) -> str:
    lines = [f"# Scope check: **{report.status}**", ""]
    lines.append(f"- Declared files: `{report.declared_files or '(none)'}`")
    lines.append(f"- Declared categories: `{report.declared_categories or '(none)'}`")
    lines.append(f"- Actual files ({len(report.actual_files)}): `{report.actual_files}`")
    lines.append(f"- Actual categories: `{report.actual_categories}`")
    if report.file_overreach:
        lines.append("")
        lines.append("## File over-reach")
        for f in report.file_overreach:
            lines.append(f"- `{f}`")
    if report.category_overreach:
        lines.append("")
        lines.append("## Category over-reach")
        for c in report.category_overreach:
            lines.append(f"- `{c}`")
    if report.notes:
        lines.append("")
        lines.append("## Notes")
        for n in report.notes:
            lines.append(f"- {n}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="越权检测 v0.0.1")
    parser.add_argument("--input", required=True, help="Path to JSON with task_spec and actual_diff")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = check_scope(payload["task_spec"], payload["actual_diff"])
    print(report_to_json(report) if args.format == "json" else report_to_markdown(report))
    return 1 if report.status == "over_reach" else 0


if __name__ == "__main__":
    sys.exit(main())
