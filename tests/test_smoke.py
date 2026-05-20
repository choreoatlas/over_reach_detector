"""Smoke tests for v0.0.1 detector."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from over_reach_detector.detector import check_scope, infer_category  # noqa: E402

FIXTURES_DIR = ROOT / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def test_example_pr_1_over_reach():
    fx = load("example_pr_1.json")
    report = check_scope(fx["task_spec"], fx["actual_diff"])
    expected = fx["expected"]
    assert report.status == expected["status"], (
        f"status mismatch: {report.status} != {expected['status']}"
    )
    assert sorted(report.file_overreach) == sorted(expected["file_overreach"]), (
        f"file_overreach: {report.file_overreach} != {expected['file_overreach']}"
    )
    assert sorted(report.category_overreach) == sorted(expected["category_overreach"]), (
        f"category_overreach: {report.category_overreach} != {expected['category_overreach']}"
    )


def test_in_scope_when_all_files_declared():
    task_spec = {"declared_files": ["docs/*.md"], "declared_categories": ["docs"]}
    actual_diff = {"files": ["docs/a.md", "docs/b.md"]}
    report = check_scope(task_spec, actual_diff)
    assert report.status == "in_scope"
    assert report.file_overreach == []
    assert report.category_overreach == []


def test_empty_when_no_actual_files():
    report = check_scope(
        {"declared_files": ["*"], "declared_categories": ["code"]},
        {"files": []},
    )
    assert report.status == "empty"


def test_license_infer_category_is_docs():
    assert infer_category("LICENSE") == "docs"
    assert infer_category("subdir/LICENSE") == "docs"
    assert infer_category("COPYING") == "docs"
    assert infer_category("vendor/COPYING") == "docs"
    assert infer_category("CHANGELOG.md") == "docs"
