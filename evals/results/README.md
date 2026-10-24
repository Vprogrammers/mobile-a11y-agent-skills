# Evaluation run artifacts

Do not commit credentials or raw project data here. Store only synthetic eval responses, judge results, score output, and the generated `summary.json` when a reviewed baseline is intentionally retained.

Run the full suite with trusted local commands:

```bash
EVAL_AGENT_COMMAND='claude -p' \
EVAL_JUDGE_COMMAND='claude -p' \
EVAL_MODEL='model-id' \
./scripts/run_eval_suite.py "evals/results/$(date -u +%Y-%m-%dT%H%M%SZ)-model-id"
```

The scheduled GitHub workflow uses user-managed Claude credentials when configured and uploads results as workflow artifacts. Pull-request validation never invokes a paid model.
