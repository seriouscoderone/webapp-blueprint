---
name: webapp-blueprint-test
description: Blackbox BDD test execution for webapp-blueprint suites. READ-ONLY role — executes scenarios via browser automation and logs results. NEVER modifies source code, configuration, or any project files. Writes only to blackbox/builds/{token}/. Run in a completely separate Claude Code session from the build agent.
---

# Webapp Blueprint Test — BDD Scenario Executor

## CRITICAL: Read-Only Role

**This agent observes and reports. It does not fix.**

| Allowed | Prohibited |
|---------|-----------|
| Navigate the running app via browser | Modify source code |
| Execute BDD scenarios | Edit config files |
| Write to `blackbox/builds/{token}/` | Run build commands |
| Record PASSED / FAILED / error details | Commit or push changes |
| Read spec files and seed-data.md | Suggest or apply fixes |

If a scenario fails, record the failure with full detail and move on to the next scenario. **Stop. Do not fix. Do not touch code.** The build agent reads the results and decides what to fix.

---

## Overview

This skill runs a **continuous polling loop** until all scenarios pass:

```
┌─────────────────────────────────────────────────────┐
│  loop until all scenarios PASSED                     │
│                                                       │
│  1. Poll blackbox/builds/ for new manifest.json      │
│  2. Run all BDD scenarios via Playwright             │
│  3. Write final_test_results/results.json  ← signal  │
│  4. If all PASSED: stop                              │
│  5. If any FAILED: go back to 1, wait for next build │
└─────────────────────────────────────────────────────┘
```

**Do not stop after writing results.** After writing `final_test_results/results.json`, check if all scenarios passed. If not, go straight back to polling for the next `manifest.json` from the build agent. Only stop when every scenario in the results is `PASSED`.

**This must run in a completely separate Claude Code session** from the build agent — it needs its own browser automation tool permissions and must have zero shared state with the build agent.

---

## Prerequisites

- **Playwright** installed: `npx playwright install` (use the `example-skills:webapp-testing` skill for Playwright integration)
- Network access to the app's `base_url` (from `manifest.json`)
- Read/write access to `blackbox/builds/` and `blackbox/templates/`

---

## Folder Protocol

```
blackbox/
├── templates/
│   └── {suite}_test.template.json     <- READ: spec snapshot (all UNTESTED)
└── builds/
    └── {build_token}/
        ├── manifest.json               <- READ: suite name, per-app base_url
        ├── test_results.json           <- WRITE: streaming results during run
        └── final_test_results/
            └── results.json            <- WRITE: final results (existence = done signal)
```

---

## Detecting a New Build

Use `scripts/wait-for-build.py` to poll for the next build. It blocks until a ready build appears and prints the `build_token`:

```bash
BUILD_TOKEN=$(python3 {SKILL_DIR}/scripts/wait-for-build.py)
# exits 0 and prints build_token when ready
# exits 1 on timeout (default 3600s)
```

A build is "ready to test" when `blackbox/builds/{token}/manifest.json` exists and `final_test_results/` does not.

---

## Execution Flow

See `references/test-phase.md` for the full execution protocol.

1. Run `BUILD_TOKEN=$(python3 {SKILL_DIR}/scripts/wait-for-build.py)` — blocks until a build is ready
2. Read `manifest.json` → get `suite` name and per-app `base_url`s
3. Read `blackbox/templates/{suite}_test.template.json` → scenario inventory
4. For each app in the manifest, for each feature, for each scenario:
   - Execute the scenario against `base_url` (see `references/scenario-execution.md`)
   - Write result to `test_results.json` after each scenario
5. Write `blackbox/builds/{token}/final_test_results/results.json`
6. **Check results:** if all PASSED → stop. If any FAILED → go back to step 1 and wait for the next build.

---

## Result Schema

Each scenario result:
```json
{
  "_type": "scenario",
  "status": "PASSED",
  "message": "All steps completed successfully",
  "error_detail": null,
  "steps_to_reproduce": [],
  "last_run": "2026-01-01T12:00:00Z",
  "build_id": "{build_token}"
}
```

Status values: `PASSED`, `FAILED`, `UNTESTED` (unprocessed)

---

## Reference Files

| File | Contents |
|------|----------|
| `references/test-phase.md` | Full execution protocol, streaming writes, atomic final write |
| `references/scenario-execution.md` | Translating Given/When/Then into browser actions, error capture |
