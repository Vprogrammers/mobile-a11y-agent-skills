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

## r3: harder evals, three runs per variant, 2026-10-24

The agent was `claude -p --model sonnet` and the judge `claude -p --model opus` (Claude Code 2.1.310), both with `--restricted`, using the commands in the eval workflow. The five `*-traps-review` evals ran three times per variant. Bundles are named `r3-<commit>-run<n>-<variant>`.

- `kmp-interop-traps-review` and `test-evidence-traps-review` come from commit `5e75b41`.
- The three severity-required evals come from commit `1945941`. In the `5e75b41` bundles, 17 of their 18 judge results were rejected, so those runs have no score. The baseline used High/Medium/Low because the prompt did not define P0–P3, and one plugin severity mismatch rejected each whole result. `1945941` (#28) gives both variants the scale and scores a mismatch per finding. The prompts of the other two evals did not change.

Points per run, as scored at the time:

| Eval | Plugin | Baseline |
|---|---|---|
| `kmp-interop-traps-review` | 8, 8, 8 | 6, 4, 4 |
| `test-evidence-traps-review` | 8, 8, 8 | 6, 6, 6 (two runs fail on forbidden claims) |
| `compose-semantics-traps-review` | 6, 6, 6 | 2, 2, 2 |
| `android-sdk36-behavior-review` | 6, 6, 6 | 2, 8, 6 |
| `uikit-container-traps-review` | 8, 8, 8 | 4, 2, 4 |
| **Total** | **15/15 passed, 108/120** | **4/15 passed, 64/120** |

After these runs, `on-back-pressed-not-called-on-sdk36` changed from P1 to P2. In the fixture, the lost `onBackPressed` callback only stops back from hiding an informational notice: the code can still be entered, and the change affects every user rather than a specific assistive-technology group. That is P2 under the skill's own calibration. The plugin rated it P2 in all three runs. Re-scoring the stored results with `score_eval.py` gives plugin 8, 8, 8 and baseline 4, 6, 8 on that eval, for totals of 114/120 and 66/120. The summaries keep the original scores.

Findings:

- **Detection is close; calibration and claims differ.** Ignoring severity, the baseline found almost every defect the plugin found. Its consistent detection gaps were `input-focus-is-not-accessibility-focus` (missed in 3 of 3 Compose runs; the plugin missed it once) and the KMP interop criteria. Most of its lost points came from inconsistent severity, such as P0 for a P1 defect in all three UIKit runs, and from unsupported claims about automated evidence.
- **The plugin is stable.** It scored the same on every run of each eval. Baseline scores varied by up to 6 points between identical runs.
- **The remaining plugin miss was `indication-null-hides-focus`,** rated P2 instead of P1 in two of three runs. `mobile-a11y-review` now lists a removed visible focus indicator as a P1 example. Because that example was added after this result, a later pass on this eval is not independent evidence.

Limits:

- These evals measure whether the plugin delivers knowledge it contains. The traps were added to the references when the evals were written, and the review checklist's code signals name several of them, so the plugin has an advantage by construction. They do not measure general review ability on unseen defects.
- One judge model scored every run, and three runs per variant is a minimum, not a benchmark.

## r4: held-out evals, three runs per variant, two judges, 2026-10-25

The two `heldout-*` evals use defects whose patterns and fix APIs appear nowhere in `skills/`. The agent was `claude -p --model sonnet`. Every response was scored by Opus and by Sonnet as a second judge (`EVAL_SECOND_JUDGE_COMMAND`), all at commit `42a376c`. A usage limit stopped three agent runs in the third repetition (`run3-*`, status `agent-failed`). They were repeated in `run3b-*` with the same commands. No other run was repeated.

Points per run, Opus judge first, with the Sonnet score where it differs:

| Eval | Plugin | Baseline |
|---|---|---|
| `heldout-compose-review` | 8, 6 (Sonnet 8), 8 | 8, 8, 6 |
| `heldout-swiftui-review` | 4, 4 (Sonnet 6), 4 | 2, 2, 4 (Sonnet 6) |
| **Total (Opus)** | **3/6 passed, 34/48** | **3/6 passed, 30/48** |

Findings:

- **No clear plugin advantage on untaught defects.** Both variants passed the same evals. The 4-point gap comes from severity calibration: the plugin rated the color-only filter selection P1 in every run, and the baseline rated it P2 in two of three. The plugin delivers the knowledge it contains (r3: 15/15 against 4/15). It does not make general review better.
- **The Compose traps are already known.** Both variants found the `ClickableText` links, the fixed-timeout Undo banner, and the toggle row in every run. The baseline once rated the toggle row P1 instead of P2.
- **Nobody found the Smart Invert defect.** None of the six SwiftUI responses mentions invert at all. This is a real gap in both variants. The held-out terms keep it out of the skills, so a later fix there would end this eval's held-out status.
- **The judges agreed on 9 of 12 runs.** All three disagreements were on the verification criterion, and Opus was the stricter judge each time.

After these runs, the SwiftUI verification criterion stopped requiring Smart Invert, because a missed Smart Invert defect also failed verification. The scores above use the original criterion, so they are stricter than later runs. The finding id changed from `verification-covers-voiceover-switch-control-and-smart-invert` to `verification-covers-voiceover-and-switch-control`.

## r5: repair eval, three runs per variant, 2026-10-25

`run_repair_eval.py` ran `compose-order-card` at commit `f54f6ad`. The agent was `claude -p --model sonnet` with Read, Glob, Grep, Edit, Write, and Bash, plus the plugin, `android-a11y-engineer`, and Skill for the plugin variant. Hidden tests scored every fix, with no judge. Each bundle keeps the agent's report (`response.md`), the fix (`fix.diff`), and the scored checks (`result.json`). The Gradle logs are not kept because they contain local paths.

| Variant | Runs | Score |
|---|---|---|
| Plugin | 8, 8, 8 | **3/3 passed, 24/24** |
| Baseline | 8, 8, 8 | **3/3 passed, 24/24** |

Findings:

- **The eval does not separate the variants.** Every fix exposed Track as its own action, tied the errors to the field with `isError`, `supportingText`, and error semantics, removed `indication = null`, and kept the existing behavior. The prompt names the users and the actions that must work, and that is enough for the baseline to find all three defects.
- **Small differences outside the checks.** The plugin added a 48 dp minimum height to the open target in two of three runs. The baseline did not add one, but one baseline run listed the touch target as a device check. One baseline run added a polite live region to the error text.
- **Every report is honest about evidence.** All six built with `assembleDebug`, and none claims TalkBack, Switch Access, or keyboard results. Each lists what still needs a real-device check. The engineer rule from #33 to build before reporting held in every plugin run, and the baseline followed the prompt's build instruction.

Limits:

- One repair eval with three defects is too easy to measure the engineer agent. A useful next eval needs defects the baseline misses in review, such as `input-focus-is-not-accessibility-focus` from r3, or a held-out defect.
- Three runs per variant is a minimum, not a benchmark.
