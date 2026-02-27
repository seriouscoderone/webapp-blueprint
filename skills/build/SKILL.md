---
name: webapp-blueprint-build
description: Build, test, fix, and spec-sync cycle for webapp-blueprint suites. Guides the build agent through deploying from generation briefs, coordinating the test agent, fixing BDD failures sequentially, and syncing spec gaps back to the blueprint. Use when you have a completed spec (from webapp-blueprint) and want to implement and validate the application.
---

# Webapp Blueprint Build — Build, Test & Fix Cycle

## Overview

This skill guides the **build agent** through the full implementation and validation cycle for a webapp-blueprint suite:

1. **Build Phase** — implement the app from generation briefs and seed data, deploy it, signal the test agent
2. **Poll** — wait for the test agent to finish (`scripts/wait-for-results.py`)
3. **Fix Phase** — read failures from `final_test_results/results.json`, fix each sequentially
4. **Spec Sync** — update the spec to reflect what was actually built
5. **Repeat** — new deployment → new build_token → new test cycle → until all green

**Critical:** The test agent is a **completely separate Claude Code session**. The build agent never runs tests itself — it only writes the `manifest.json` signal and waits.

---

## Prerequisites

Before starting:
- `./spec/` — complete blueprint spec (all 19 steps, or at minimum Steps 9, 17, 18)
- `./blackbox/templates/{suite}_test.template.json` — suite test template (Step 19)
- A separate Claude Code session ready to run `webapp-blueprint-test`

---

## Folder Protocol

```
blackbox/
├── templates/
│   └── {suite}_test.template.json     ← blueprint output (Step 19)
└── builds/
    └── {build_token}/
        ├── manifest.json               ← BUILD writes this (signals test agent)
        ├── test_results.json           ← TEST writes streaming results
        └── final_test_results/
            └── results.json            ← TEST writes when done (signals build agent)
```

---

## Build Phase

See `references/build-phase.md` for full details.

**Quick start:**
```bash
# 1. Read generation briefs and seed data
ls spec/apps/*/generation-briefs/
cat spec/apps/{app}/seed-data.md

# 2. Implement and deploy (per Step 17 build tiers)

# 3. Generate build_token
BUILD_TOKEN=$(git rev-parse --short HEAD)   # local dev
# or use ${{ github.run_id }} in CI

# 4. Write manifest
mkdir -p blackbox/builds/$BUILD_TOKEN
# Write blackbox/builds/$BUILD_TOKEN/manifest.json

# 5. Wait for test results
python3 scripts/wait-for-results.py --build-token $BUILD_TOKEN
```

---

## Fix Phase

See `references/fix-cycle.md` for full details.

**Quick start:**
```bash
# Read results
python3 scripts/summarize-results.py --build-token $BUILD_TOKEN

# For each FAILED scenario:
# 1. Read steps_to_reproduce + error_detail
# 2. Write a failing unit/integration test
# 3. Fix code until test passes
# 4. git commit -m "fix: {scenario title} — {description}"
```

---

## Spec Sync

See `references/spec-sync.md` for full details.

After all tests pass (or after any cycle with fix commits):
```bash
git log {pre_build_sha}..HEAD --oneline
# Review: does any fix commit contradict or extend the spec?
# Write: blackbox/builds/{token}/spec-gaps.md
# Apply spec updates if needed, then re-run Step 19:
python3 scripts/generate-blackbox-template.py --suite {suite_name}
```

---

## Stopping Condition

If the same BDD scenario fails **3 consecutive build cycles**, stop looping and surface it as a blocking issue requiring human review. Do not continue iterating on a scenario that resists automated fixing.

---

## Reference Files

| File | Contents |
|------|----------|
| `references/build-phase.md` | Build token strategy, manifest schema, deployment patterns, team structure |
| `references/fix-cycle.md` | Sequential fix protocol, unit-test-first approach, commit conventions |
| `references/spec-sync.md` | Feedback loop, gap detection, spec update process |
