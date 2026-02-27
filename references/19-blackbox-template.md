# Step 19: Blackbox Test Template

## Tier
4 — Suite-level (run after Step 9 BDD features exist for all apps; can run any time after Step 9)

## Purpose
Generate a machine-readable JSON template from all BDD feature files in the suite — the handoff artifact between the blueprint skill and the `webapp-blueprint-build`/`webapp-blueprint-test` skills. The template gives the test agent a stable, spec-derived inventory of every scenario across every app, with each entry initialized to `UNTESTED`.

## Prerequisites
- `./spec/apps/` — at least one app directory with at least one `.feature.md` in its `features/` subdirectory (Step 9)

## Inputs
- `./spec/apps/*/features/*.feature.md` — all BDD feature files for all apps in the suite

## Suite Name
The suite name is a short identifier for the project (e.g. `acme`, `my-platform`). It becomes part of the output filename: `{suite}_test.template.json`. Ask the user for this if not obvious from context.

## Interrogation

This step is intentionally minimal — the feature files contain all the needed information.

Ask only:
1. "What is the suite name? (e.g. `acme`, `my-platform`)"
2. "Output directory for the template? (default: `./blackbox/templates/`)"
3. "Do you want me to run the script, or generate the template directly?"
   - If running the script: execute the command below
   - If generating directly: parse the feature files and write the JSON template manually following the schema in the Output section

## Execution

```bash
python3 scripts/generate-blackbox-template.py --suite {suite_name}
```

With a custom spec or output directory:

```bash
python3 scripts/generate-blackbox-template.py \
  --suite {suite_name} \
  --spec-dir ./spec \
  --output-dir ./blackbox/templates
```

The script always **overwrites** the output file — it always reflects the current feature files with fresh defaults. This is intentional: the template is a manifest artifact, not a result store.

## Output

### `./blackbox/templates/{suite_name}_test.template.json`

```json
{
  "_meta": {
    "suite": "{suite_name}",
    "generated_at": "2026-01-01T00:00:00Z",
    "schema_version": "1.0"
  },
  "{app_name}": {
    "_meta": {
      "spec_dir": "spec/apps/{app_name}/features/",
      "feature_count": 3
    },
    "{Feature Name}": {
      "_meta": {
        "file": "{feature-name}.feature.md",
        "scenario_count": 3
      },
      "{Scenario Title}": {
        "_type": "scenario",
        "status": "UNTESTED",
        "message": "Untested",
        "error_detail": null,
        "steps_to_reproduce": [],
        "last_run": null,
        "build_id": null
      },
      "{Scenario Outline Title}": {
        "_type": "scenario_outline",
        "status": "UNTESTED",
        "message": "Untested",
        "error_detail": null,
        "steps_to_reproduce": [],
        "last_run": null,
        "build_id": null
      }
    }
  }
}
```

### Schema Reference

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `_type` | `"scenario"` \| `"scenario_outline"` | derived | Lets test agent know if parameterized |
| `status` | `"UNTESTED"` \| `"PASSED"` \| `"FAILED"` | `"UNTESTED"` | Pass/fail gate |
| `message` | string | `"Untested"` | Human/AI readable description of failure or note |
| `error_detail` | string \| null | `null` | Raw technical output — stack trace, assertion error, browser console error |
| `steps_to_reproduce` | string[] | `[]` | Ordered steps for build agent to replay the failure |
| `last_run` | ISO-8601 string \| null | `null` | Timestamp of last test execution |
| `build_id` | string \| null | `null` | Which build cycle this result belongs to |

### Status Values

| Status | Meaning |
|--------|---------|
| `UNTESTED` | Test has never run — agent must execute it for the first time |
| `FAILED` | Test ran and failed — build agent reads `steps_to_reproduce` and `error_detail` to fix |
| `PASSED` | Test ran and passed — agent can skip |

### Scenario Outline Handling

Scenario Outlines are stored as a **single entry** with `_type: "scenario_outline"` rather than expanded per example row. The `webapp-blueprint-test` skill expands outlines into individual runs; if any example row fails, the entry is marked `FAILED` with combined error details.

## Companion Skills

This template is consumed by:
- **`webapp-blueprint-build`** — reads the template to track fix-cycle progress
- **`webapp-blueprint-test`** — copies the template, fills in results as scenarios execute, writes `final_test_results/results.json` when complete

See `skills/build/SKILL.md` and `skills/test/SKILL.md`.

## Migration Note

Prior to this suite-scoped format, the script accepted `--app {app_name}` and produced a per-app template. If you have existing per-app templates, re-run with `--suite` to generate the new suite-scoped file.

## Completion Checklist
- [ ] Suite name confirmed
- [ ] At least one `.feature.md` confirmed present across apps
- [ ] Script executed (or template generated directly)
- [ ] `./blackbox/templates/{suite_name}_test.template.json` exists
- [ ] All apps in `spec/apps/` are represented as top-level keys
- [ ] Scenario count in the output matches the feature files
- [ ] All scenario entries have `status: "UNTESTED"`, `message: "Untested"`, and null/empty fields
- [ ] Re-running the script after adding a scenario produces a fresh file with the new scenario present
