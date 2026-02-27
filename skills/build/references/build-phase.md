# Build Phase Reference

## Overview

The build phase takes the blueprint spec as input and produces a running application plus a `manifest.json` that signals the test agent to begin.

---

## Step 1: Read the Spec

**Generation briefs** (Step 17) define the build order and page-level briefs:
```
spec/apps/{app}/generation-briefs/
├── 00-build-order.md        ← which pages/features to build first
├── 01-{page-name}.md        ← per-page brief with components, API endpoints, state
└── ...
```

**Seed data** (Step 18) defines the database records needed for tests to pass:
```
spec/apps/{app}/seed-data.md
```

Read both before writing any code.

---

## Step 2: Organize a Build Team

Use subagents organized by the build tiers from Step 17's build order:

| Tier | Typical Contents | Suggested Subagent |
|------|-----------------|-------------------|
| Foundation | DB schema, auth, shared components | `infra-agent` |
| Core features | Primary CRUD pages, main user flows | `feature-agent` |
| Secondary features | Dashboards, reports, settings | `feature-agent` |
| Integration | Third-party APIs, webhooks | `integration-agent` |

Spawn one subagent per tier. Each subagent reads its generation briefs and implements the pages/components described. Briefs reference Step 14 (API Contracts) and Step 12 (Component Inventory) for exact shapes.

---

## Step 3: Deploy or Start Dev Server

**Local dev:**
```bash
npm run dev   # or equivalent
# Note the base URL: typically http://localhost:3000
```

**CDK / Cloud:**
```bash
cdk deploy --all
# Wait for stack outputs — extract base URLs per app
```

After CDK deploys, wait **60 seconds** for the deployment to settle before writing the manifest.

---

## Step 4: Generate build_token

The build_token is suite-scoped — one deployment = one token.

| Context | Token Source | Example |
|---------|-------------|---------|
| GitHub Actions | `${{ github.run_id }}` | `12345678` |
| AWS CodePipeline | execution ID | `a1b2c3d4-...` |
| Local dev | `git rev-parse --short HEAD` | `a1b2c3d` |

```bash
# Local dev
BUILD_TOKEN=$(git rev-parse --short HEAD)

# CI (GitHub Actions)
BUILD_TOKEN=${{ github.run_id }}
```

**Why CI run ID (not SHA) in production:** A pipeline run is naturally suite-scoped (one CDK stack = one deploy). The same SHA may be re-deployed without a new commit (e.g., hotfix rollback) — run IDs are always unique.

The git SHA is still recorded in `manifest.json` for code traceability.

---

## Step 5: Write manifest.json

```
blackbox/builds/{build_token}/manifest.json
```

### Schema

```json
{
  "suite": "{suite_name}",
  "build_token": "{pipeline_run_id}",
  "git_sha": "{full_git_sha}",
  "git_branch": "{branch_name}",
  "deployed_at": "2026-01-01T00:00:00Z",
  "apps": {
    "{app_name}": { "base_url": "https://app.example.com" }
  },
  "created_by": "build-agent"
}
```

**Creating the file is the signal** — the test agent watches `blackbox/builds/` for new subdirectories containing a `manifest.json`. Write it only after the app is fully deployed and ready to receive requests.

---

## Step 6: Wait for Results

```bash
python3 scripts/wait-for-results.py --build-token $BUILD_TOKEN
```

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| `0` | `final_test_results/` found — test agent finished | Read results, proceed to Fix Phase |
| `1` | Timeout (default 600s) | Treat as test infrastructure failure; check test agent session |

Default options:
- `--timeout 600` — seconds before giving up (10 minutes)
- `--interval 30` — seconds between status prints

---

## Multi-App CDK Stacks

If your CDK stack deploys multiple apps (the typical case), `manifest.json` lists all apps with their respective `base_url`s. The test agent iterates them in order.

If you ever split into per-app stacks, create one `manifest-{app}.json` per app under the same `builds/{token}/` folder. The test agent processes them in sequence. But assume one stack = one manifest unless the spec says otherwise.
