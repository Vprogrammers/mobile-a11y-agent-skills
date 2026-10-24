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

## Plugin versus baseline, 2026-10-24

The agent and judge were both `claude -p --model sonnet` (Claude Code 2.1.310) with `--restricted`. Each variant got one run per eval. The baseline received the same task and fixture without the plugin or the agent name (`EVAL_VARIANT=baseline`). The rubrics, judge, and scorer were the same for both variants.

| Round | Commit | Plugin passed | Plugin points | Baseline passed | Baseline points |
|---|---|---|---|---|---|
| r1 | `225c5c3` | 9/13 | 74 (3 results rejected) | 13/13 | 104/104 |
| r2 | `f5f0080` | 13/13 | 98/104 | 11/13 | 92 (1 result rejected) |

What changed between the rounds, and why:

- **r1 plugin failures.** Three judge results were rejected for severity: the plugin rated P2 where the rubric expects P1, and the judge attached severity to non-defect criteria. The fourth failure was `clean-uikit-review`. There the plugin reported that `UIButton(type: .system)` keeps a fixed 15 pt title. That is true: the title measured 15 pt at AX5 on the iOS 26 simulator. The control was not clean, so the baseline's full score there was wrong. r2 fixes the fixture, adds severity calibration to `mobile-a11y-review`, and drops stray non-defect severities in the judge adapter.
- **r2 baseline failures.** On `clean-uikit-review` the baseline claimed exact VoiceOver speech. On `android-compose-review` the judge invented a P2 severity for a response that gave none.
- **r2 plugin misses (passed).** The plugin missed `unstable-lazy-list-identity`, `webview-needs-separate-audit`, and `custom-view-needs-accessibility-node-contract`.

Conclusions and limits:

- This is evidence, not a benchmark. Each variant ran once, and the baseline's pass count moved by two evals between identical-variant runs. Run at least three times per variant before claiming a difference.
- The suite is near its ceiling for Sonnet without the plugin. Most evals do not discriminate. Add harder fixtures, for example ones with subtle defects, mixed frameworks, or traps the base model gets wrong, before using pass counts to measure value.
- Severity scoring is asymmetric. A response without severities cannot have a mismatch, so it is never penalized for severity. Interpret severity-related rejections with that in mind.
- The clearest verified plugin advantage in these runs is the `UIButton` Dynamic Type defect. The skill-guided review found it, the baseline missed it, and a simulator test now proves it.
