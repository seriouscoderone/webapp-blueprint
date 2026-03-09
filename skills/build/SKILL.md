---
name: webapp-blueprint-build
description: Build, test, fix, and spec-sync cycle for webapp-blueprint suites. Guides the build agent through deploying from generation briefs, coordinating the test agent, fixing BDD failures sequentially, and syncing spec gaps back to the blueprint. Use when you have a completed spec (from webapp-blueprint) and want to implement and validate the application.
---

# Webapp Blueprint Build — Build, Test & Fix Cycle

## Overview

This skill guides the **build agent** through a continuous loop that runs until all BDD scenarios pass:

```
┌─────────────────────────────────────────────────────┐
│  loop until summarize-results.py exits 0             │
│                                                       │
│  1. Build & deploy                                    │
│  2. Write manifest.json  ← signals test agent        │
│  3. wait-for-results.py  ← blocks until test done    │
│  4. summarize-results.py ← check pass/fail           │
│     ↓ all PASSED                ↓ failures           │
│  5. Spec Sync (final)     5. Fix each failure        │
│  6. STOP                  6. Spec Sync ← HERE        │
│                           7. Redeploy → go to 1      │
│                                                       │
│  Exit only when: all PASSED or 3× same failure       │
└─────────────────────────────────────────────────────┘
```

**Spec Sync runs after every fix cycle** — once you've discovered and written the fixes, you know exactly what the spec was missing or wrong about. Update the spec to reflect that before redeploying, so each new cycle starts from an honest spec. If BDD features change, regenerate the suite template before the next build.

**Do not stop between cycles.** Only stop when `summarize-results.py` exits 0 (all PASSED) or the stopping condition is hit.

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
python3 {SKILL_DIR}/scripts/wait-for-results.py --build-token $BUILD_TOKEN
```

---

## Fix Phase

See `references/fix-cycle.md` for full details.

**Quick start:**
```bash
# Read results
python3 {SKILL_DIR}/scripts/summarize-results.py --build-token $BUILD_TOKEN
# exits 0 = all passed → run Spec Sync (final cleanup) then STOP
# exits 1 = failures exist → fix them, then Spec Sync, then redeploy

# For each FAILED scenario:
# 1. Read steps_to_reproduce + error_detail
# 2. Write a failing unit/integration test
# 3. Fix code until test passes
# 4. git commit -m "fix: {scenario title} — {description}"

# After all fixes committed: run Spec Sync, then redeploy → new BUILD_TOKEN
```

---

## Spec Sync

See `references/spec-sync.md` for full details.

**Run after every fix cycle** — before redeploying. The fixes reveal what the spec was wrong or incomplete about; update it while that understanding is fresh.

```bash
git log {pre_build_sha}..HEAD --oneline
# Review: do any fix commits contradict or extend the spec?
# Write: blackbox/builds/{token}/spec-gaps.md
# Apply spec updates, then if BDD features changed, regenerate the template:
python3 {SKILL_DIR}/scripts/generate-blackbox-template.py --suite {suite_name}
# Now redeploy
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
