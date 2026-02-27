# Step 19: Blackbox Test Template

## Tier
4 — Per-app (run after Step 9 BDD features exist; can run any time after Step 9)

## Purpose
Generate a machine-readable JSON template from the app's BDD feature files — the handoff artifact between the blueprint skill and the future build/test cycle skill. The template gives the build agent a stable, spec-derived inventory of every scenario it must exercise, with each entry initialized to `UNTESTED` so the agent can distinguish "never run" from "ran and failed".

## Prerequisites
- `./spec/apps/{app_name}/features/` (Step 9) — at least one `.feature.md` must exist

## Inputs
- `./spec/apps/{app_name}/features/*.feature.md` — all BDD feature files for the app

## App Selection Process
Before running the script, determine which app to generate for:
1. List any existing apps found in `./spec/apps/` subdirectories.
2. Ask: "Which app are you generating the blackbox test template for?"
3. Confirm that at least one `.feature.md` file exists in `./spec/apps/{app_name}/features/` before proceeding.

## Interrogation

This step is intentionally minimal — the feature files contain all the needed information.

Ask only:
1. "Confirm the app name: `{app_name}`?"
2. "Output directory for the template? (default: `./blackbox/templates/`)"
3. "Do you want me to run the script, or generate the template directly?"
   - If running the script: execute the command below
   - If generating directly: parse the feature files and write the JSON template manually following the schema in the Output section

## Execution

```bash
python3 scripts/generate-blackbox-template.py --app {app_name}
```

With a custom spec or output directory:

```bash
python3 scripts/generate-blackbox-template.py \
  --app {app_name} \
  --spec-dir ./spec \
  --output-dir ./blackbox/templates
```

The script always **overwrites** the output file — it always reflects the current feature files with fresh defaults. This is intentional: the template is a manifest artifact, not a result store.

## Output

### `./blackbox/templates/{app_name}_test.template.json`

```json
{
  "_meta": {
    "app": "{app_name}",
    "generated_at": "2026-01-01T00:00:00Z",
    "spec_dir": "spec/apps/{app_name}/features/",
    "schema_version": "1.0"
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
```

### Schema Reference

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `_type` | `"scenario"` \| `"scenario_outline"` | derived | Lets build agent know if parameterized |
| `status` | `"UNTESTED"` \| `"PASSED"` \| `"FAILED"` | `"UNTESTED"` | Pass/fail gate |
| `message` | string | `"Untested"` | Human/AI readable description of failure or note |
| `error_detail` | string \| null | `null` | Raw technical output — stack trace, assertion error, browser console error |
| `steps_to_reproduce` | string[] | `[]` | Ordered steps for build agent to replay the failure |
| `last_run` | ISO-8601 string \| null | `null` | Timestamp of last test execution |
| `build_id` | string \| null | `null` | Which build cycle this result belongs to |

### Status Values

| Status | Meaning to build agent |
|--------|----------------------|
| `UNTESTED` | Test has never run — agent must execute it for the first time |
| `FAILED` | Test ran and failed — agent should read `steps_to_reproduce` and `error_detail` to fix |
| `PASSED` | Test ran and passed — agent can skip |

### Scenario Outline Handling

Scenario Outlines are stored as a **single entry** with `_type: "scenario_outline"` rather than expanded per example row. The build/test cycle skill will expand outlines into individual run records when it executes them.

## Completion Checklist
- [ ] App selected and at least one `.feature.md` confirmed present
- [ ] Script executed (or template generated directly)
- [ ] `./blackbox/templates/{app_name}_test.template.json` exists
- [ ] Scenario count in the output matches the count in the feature files
- [ ] All scenario entries have `status: "UNTESTED"`, `message: "Untested"`, and null/empty fields
- [ ] Re-running the script after adding a scenario produces a fresh file with the new scenario present
