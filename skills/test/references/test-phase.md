# Test Phase Reference

## Role Boundary

This agent is **read-only with respect to the application and its source**. The only files it ever writes are:
- `blackbox/builds/{token}/test_results.json` — streaming results
- `blackbox/builds/{token}/final_test_results/results.json` — final results

If a scenario fails, log it and continue. Never edit source code, never run fixes, never commit. That is the build agent's job.

---

## Overview

The test phase reads two inputs (the suite template and the build manifest) and produces one output (the final results file). The existence of `final_test_results/results.json` is the signal that the build agent polls for.

---

## Step 1: Poll for the Next Build

```bash
BUILD_TOKEN=$(python3 scripts/wait-for-build.py)
# Blocks until blackbox/builds/{token}/manifest.json exists
# and final_test_results/ does NOT exist.
# Prints build_token to stdout on exit 0.
# Exits 1 on timeout (default 3600s).
```

If multiple ready builds exist, the script picks the most recently modified one.

---

## Step 2: Load Inputs

**manifest.json:**
```json
{
  "suite": "acme",
  "build_token": "12345678",
  "git_sha": "abc123...",
  "git_branch": "main",
  "deployed_at": "2026-01-01T00:00:00Z",
  "apps": {
    "portal": { "base_url": "https://portal.example.com" },
    "admin": { "base_url": "https://admin.example.com" }
  },
  "created_by": "build-agent"
}
```

**Suite template** (`blackbox/templates/{suite}_test.template.json`):
- All scenarios initialized to `UNTESTED`
- Top-level keys: `_meta`, then one key per app name

---

## Step 3: Initialize test_results.json

Copy the suite template to `blackbox/builds/{token}/test_results.json`. This is the working document — you will update it in place as scenarios are processed.

The `_meta` block gains two fields in result files:
```json
"_meta": {
  "suite": "acme",
  "build_token": "12345678",
  "generated_at": "...",
  "tested_at": "2026-01-01T12:00:00Z",
  "schema_version": "1.0"
}
```

---

## Step 4: Execute Scenarios

Process order: for each app in the manifest (in manifest order), for each feature (alphabetically by file), for each scenario:

1. Look up `base_url` for this app from `manifest.json`
2. Execute the scenario (see `scenario-execution.md`)
3. Update the scenario's entry in the working document:
   - `status`: `PASSED` or `FAILED`
   - `message`: brief description
   - `error_detail`: raw error output (null if PASSED)
   - `steps_to_reproduce`: ordered list (empty if PASSED)
   - `last_run`: ISO-8601 timestamp
   - `build_id`: the build_token from manifest
4. Write the updated working document to `test_results.json`

**Write after every scenario.** This allows the build agent to monitor progress and gives a recovery point if the test session crashes.

**Invariant:** Any scenario still showing `UNTESTED` in `test_results.json` simply hasn't been processed yet in this cycle.

---

## Step 5: Write Final Results (Atomic)

When all scenarios for all apps are complete:

1. Create `blackbox/builds/{token}/final_test_results/` directory
2. Write the completed document to `blackbox/builds/{token}/final_test_results/results.json`

**The directory's existence is the signal** — the build agent's `wait-for-results.py` polls for it. Write `results.json` before anything else in that directory, and do not create the directory until all scenarios are processed.

```python
# Pseudocode
final_dir = builds_dir / token / "final_test_results"
final_dir.mkdir(parents=True, exist_ok=True)
(final_dir / "results.json").write_text(json.dumps(completed_doc, indent=2))
```

---

## Step 6: Loop or Stop

After writing `final_test_results/results.json`, check whether all scenarios passed:

```python
# Pseudocode
all_passed = all(
    scenario["status"] == "PASSED"
    for app_data in results.values() if isinstance(app_data, dict)
    for feature_data in app_data.values() if isinstance(feature_data, dict)
    for scenario in feature_data.values()
    if isinstance(scenario, dict) and "_type" in scenario
)
```

- **All PASSED** → print a summary and stop. The cycle is complete.
- **Any FAILED** → go back to Step 1 immediately. Poll for the next `manifest.json`. The build agent will fix the failures, deploy again, and write a new manifest. Do not prompt the user — just wait.

---

## Handling Interruptions

If the test session is interrupted mid-run:
- `test_results.json` contains partial results (processed scenarios have statuses; unprocessed are still `UNTESTED`)
- `final_test_results/` does NOT exist
- The build agent's `wait-for-results.py` will eventually time out (exit 1)
- Resume: start a new test cycle (build agent creates new manifest with new or same token)

Do not attempt to resume a partial run from `test_results.json` — start fresh with the template.
