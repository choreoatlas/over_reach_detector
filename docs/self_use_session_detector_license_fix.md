# Self-use session 4: detector LICENSE false positive

## Context

While preparing the repo for MCP registry submission (Gate 7), Task A was to add a standard `LICENSE` file and a `## License` section in `README.md`. Both were declared as `docs`.

The detector flagged this as `over_reach`: `LICENSE` was classified as `code` because the default category catches anything not matched by the `tests/*`, `*.md`, `docs/*`, `README*`, infra, or config patterns.

Human review judged this a detector false positive — `LICENSE` is standard legal/project metadata present in virtually every repo, semantically `docs`. Rather than relax the Task A scope declaration to `["docs", "code"]` (which would pollute the scope signal for every future LICENSE-touching commit), the fix was lifted out as a separate task A.5: fix the detector's classification rule.

## Task A.5 — fix detector classification

### Declared

- `declared_files`: `["detector.py", "tests/test_smoke.py"]`
- `declared_categories`: `["code"]`

### Actions

- `detector.py`: added basename-precise patterns for `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `COPYING`, `NOTICE`, `AUTHORS`, `CONTRIBUTORS`, `CHANGELOG`, `CHANGELOG.md` into the docs rule, with `*/NAME` variants so subdirectory copies also match.
- `tests/test_smoke.py`: added `test_license_infer_category_is_docs`.
- Full test suite: 10/10 green.

### Tool response

```json
{
  "status": "over_reach",
  "file_overreach": [],
  "category_overreach": ["tests"],
  "declared_files": ["detector.py", "tests/test_smoke.py"],
  "declared_categories": ["code"],
  "actual_files": ["detector.py", "tests/test_smoke.py"],
  "actual_categories": ["code", "tests"],
  "notes": []
}
```

### Verdict

**True positive.** The over-reach is in the *declaration*, not the action. The session-author's Cursor prompt declared `["code"]` but the task explicitly required a test file, which the detector correctly classified as `tests`. Re-checking with `declared_categories=["code", "tests"]` returned `in_scope`.

This is meta-evidence: the detector caught an under-declared scope authored by the same agent that designed the task — exactly the failure mode the tool exists to surface. Files and changes were correct; only the declaration was wrong.

Commit: `d925db7` — `detector: classify LICENSE/COPYING/NOTICE as docs`

## Task A — rerun after detector fix

### Declared

- `declared_files`: `["LICENSE", "README.md"]`
- `declared_categories`: `["docs"]`

### Tool response (MCP, pre-reload)

`over_reach` — the MCP stdio server held the pre-fix `detector.py` in memory; `LICENSE` was still classified as `code`.

### Tool response (local Python, post-reload)

```json
{
  "status": "in_scope",
  "file_overreach": [],
  "category_overreach": [],
  "declared_files": ["LICENSE", "README.md"],
  "declared_categories": ["docs"],
  "actual_files": ["LICENSE", "README.md"],
  "actual_categories": ["docs"],
  "notes": []
}
```

### Verdict

`in_scope` after detector reload. Commit: `12f0944` — `Add MIT LICENSE`.

## Observations

1. **The detector's value scales with classifier coverage.** Default-to-`code` was a deliberate v0.0.1 choice to keep rules small, but it produces false positives on standard project metadata. The fix pattern — basename matches with `*/NAME` variants for path-insensitive matching — is the template for future classifier expansions (e.g. `Dockerfile.*`, `Makefile`, `.editorconfig`).

2. **MCP stdio servers cache loaded modules.** After modifying `detector.py`, the running `over-reach-detector` MCP process must be restarted for changes to take effect. This is operational friction for the self-use loop where the detector itself is the artifact under iteration. Candidate follow-ups: document the restart requirement in `README.md`, or add a reload hook. *(Out of scope for this session.)*

3. **AI-authored scope declarations are themselves over-reach candidates.** The A.5 prompt declared `["code"]` but the task required adding a test file. The detector caught this. Generalization: any time the agent designing a task also writes the scope declaration, the declaration is subject to the same over-reach pressure as the code. Two-author separation (one declares, one executes) is the structural mitigation; the detector provides the runtime audit signal.
