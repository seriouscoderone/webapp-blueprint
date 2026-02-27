---
name: webapp-blueprint-test
description: Blackbox BDD test execution for webapp-blueprint suites. Reads the suite test template and manifest, runs every scenario against the deployed app, and writes results for the build agent to consume. Run this in a completely separate Claude Code session from the build agent — it requires browser automation tools and must not share context with the build agent.
---

# Webapp Blueprint Test — BDD Scenario Executor

## Overview

This skill is a **single-purpose test executor**. It:

1. Watches `blackbox/builds/` for a new `manifest.json` (the build agent's signal)
2. Loads the suite test template (`blackbox/templates/{suite}_test.template.json`)
3. Executes every BDD scenario against the running app using browser automation
4. Streams results to `test_results.json` after each scenario
5. Writes `final_test_results/results.json` when all scenarios are complete (the signal back to the build agent)

**This must run in a completely separate Claude Code session** from the build agent — it needs its own browser automation tool permissions and must have zero shared state with the build agent.

---

## Prerequisites

- Browser automation tool available: **Playwright** (`npx playwright test`) or **claude-in-chrome MCP**
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

Watch `blackbox/builds/` for a new subdirectory containing `manifest.json`:

```bash
ls blackbox/builds/
# Look for a directory that does NOT yet have a final_test_results/ subdirectory
```

A build is "ready to test" when:
- `blackbox/builds/{token}/manifest.json` exists
- `blackbox/builds/{token}/final_test_results/` does NOT yet exist

Pick the most recently created such directory.

---

## Execution Flow

See `references/test-phase.md` for the full execution protocol.

1. Read `manifest.json` -> get `suite` name and per-app `base_url`s
2. Read `blackbox/templates/{suite}_test.template.json` -> scenario inventory
3. For each app in the manifest, for each feature, for each scenario:
   - Execute the scenario against `base_url` (see `references/scenario-execution.md`)
   - Write result to `test_results.json` after each scenario
4. When all scenarios complete: write `blackbox/builds/{token}/final_test_results/results.json`

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
