# Mobile A11y Agent Skills

Production-focused accessibility agents and skills for Android, iOS, and Kotlin Multiplatform.

The project helps coding agents implement and review accessible native mobile interfaces instead of applying a web checklist blindly. It covers Compose, Android Views, SwiftUI, UIKit, KMP boundaries, TalkBack, VoiceOver, Voice Access/Control, Switch Access/Control, Dynamic Type, font scaling, reduced motion, contrast, autofill, focus, testing, and standards-aware reporting.

> Early release: verify version-sensitive APIs and real assistive-technology behavior in the target project and on supported devices.

## Why use it

- Native mobile guidance with concrete platform APIs and failure modes.
- Shared product requirements with platform-native implementation boundaries.
- Explicit separation of static, automated, simulator, and real-device evidence.
- WCAG 2.2, EN 301 549, EAA, ADA Title II, and Section 508 context without false compliance claims.
- Privacy-aware guidance for credentials, payments, identity, health, and other sensitive data.

## Agents

| Agent | Use it for |
|---|---|
| `kmp-a11y-architect` | Shared contracts, source-set boundaries, dependencies, Swift export/SKIE, and interop |
| `android-a11y-engineer` | Compose or Views implementation and TalkBack/Voice Access behavior |
| `ios-a11y-engineer` | SwiftUI or UIKit implementation and VoiceOver/Voice Control behavior |
| `accessibility-test-engineer` | Unit, semantics, UI, audit, and device-test coverage |
| `accessibility-reviewer` | Independent, severity-based review before a pull request or release |

## Skills

| Skill | Focus |
|---|---|
| `mobile-a11y-review` | Cross-platform audit, evidence, severity, and regulatory mapping |
| `android-a11y` | Compose/Views semantics, focus, actions, scaling, input, WebView, and testing |
| `ios-a11y` | SwiftUI/UIKit structure, focus, actions, Dynamic Type, audits, and device checks |
| `kmp-a11y` | Shared state with native UI, Compose Multiplatform shared UI (draft), expect/actual decisions, export, SKIE, and dependency boundaries |
| `mobile-a11y-testing` | Test-layer selection, concrete tools, commands, and evidence limits |

## Install with Claude Code

```text
/plugin marketplace add Vprogrammers/mobile-a11y-agent-skills
/plugin install mobile-a11y-agent-skills@vprogrammers-mobile-a11y
```

Or copy `agents/*` to `.claude/agents/` and `skills/*` to `.claude/skills/`.

The agents invoke skills by name, so they work from plugin installation or copied project directories without repository-relative paths.

For a minimal copy-ready package, use [`mobile-a11y-agent-skills-lite`](https://github.com/Vprogrammers/mobile-a11y-agent-skills-lite). It is generated from this repository and contains only consumer instructions, agents, skills, references, and license files.

## Example prompts

Plugin agents are namespaced. When the plugin is installed, invoke them as `<plugin>:<agent>` or with Claude Code's explicit `@agent-...` form. Agents copied directly into `.claude/agents/` keep their unprefixed names.

```text
Use @agent-mobile-a11y-agent-skills:accessibility-reviewer to review this PR. Separate proven findings from device checks.
```

```text
Use @agent-mobile-a11y-agent-skills:android-a11y-engineer to fix the TalkBack order in this Compose screen without changing the shared API.
```

```text
Use @agent-mobile-a11y-agent-skills:kmp-a11y-architect to decide whether reduced-motion state belongs behind an interface or expect/actual.
```

Example reviewer finding:

```text
P1 — CheckoutDialog.kt:84
Affected users: TalkBack and keyboard users.
Evidence: the custom overlay does not expose a modal boundary, so focus reaches content behind it.
Fix: use a platform dialog or add the correct modal/window semantics and restore focus on dismissal.
Verify: Compose device test for reachable nodes, then TalkBack navigation on a supported device.
```

## Workflow

1. Use `kmp-a11y-architect` when public APIs, exports, dependencies, or source-set ownership change.
2. Use the Android and/or iOS implementation agent.
3. Use `accessibility-test-engineer` to close evidence gaps.
4. Use `accessibility-reviewer` for an independent final pass.
5. Run `./scripts/validate.sh` and report device checks separately using [the real-device evidence template](skills/mobile-a11y-testing/references/real-device-evidence-template.md).

## Validation and evals

```bash
./scripts/validate.sh
```

`validate.sh` runs the repository validator, compiles the scripts, runs the installation smoke test, and runs the unit tests. The validator checks skill and agent metadata, explicitly named invoked skills, duplicate names, local links, plugin version consistency, required review dates, executable permissions, and typed eval manifests/rubrics. It warns 30 days before each reference's declared review interval expires and fails when it is stale. Dynamic platform references use 180 days, regulatory guidance uses 90 days, and references without an override use 365 days. External links are intentionally optional to keep pull-request CI deterministic; a scheduled workflow checks them monthly:

CI also installs the pinned Claude Code version and runs its authoritative manifest check:

```bash
claude plugin validate --strict .
```

```bash
CHECK_EXTERNAL_LINKS=1 ./scripts/validate.sh
```

Evaluation scenarios live in `evals/`. Each manifest entry points to a prompt, raw code fixture, scoring rubric, minimum score, and forbidden claims. Give only the prompt and fixture to the agent; score the result afterward with the rubric to avoid leaking expected findings.

Rubrics keep finding `kind` separate from severity. Each finding has explicit acceptance `criteria`. Severity uses the `P0`–`P3` definitions in `mobile-a11y-review`, applies only to defects, and is `null` for architecture, interop, testing, verification, compliance, dependency, or recommendation criteria.

Record the assessment using rubric finding IDs, with the P0–P3 severity the response assigned to each defect. A defect whose severity does not match the rubric earns no points; the rest of the result still counts. Evals whose prompts ask for severity set `"severity_required": true` in the manifest. The suite then appends the P0–P3 definitions from `mobile-a11y-review` to the prompt for both the plugin and the baseline, and a matched defect without a P0–P3 severity earns no points, so omitting severity never scores better than a mismatch. Elsewhere, severity stays optional. When the judge's output is rejected, `judge_eval.py` keeps it in `<result>.rejected.txt`:

```json
{
  "matched_findings": [
    {"id": "gesture-only-help", "severity": "P1"},
    {"id": "non-modal-overlay", "severity": "P1"}
  ],
  "forbidden_claims": []
}
```

Then calculate deterministic pass/fail:

```bash
./scripts/score_eval.py android-compose-review result.json
```

`clean-compose-review` intentionally requires both of its criteria (4 of 4): a clean control passes only when the agent both declines to manufacture a blocker and asks for device verification.

Most evals test defects that the skills describe, so they show whether the plugin delivers its own guidance. The `heldout-*` evals instead use defects whose patterns and fix APIs appear nowhere in `skills/`, which measures review on defects the plugin was not taught. General principles, such as exposing state or giving users enough time, may still apply. Their manifest entries list `held_out_terms`, and the validator fails when any of those terms appears in a skill file. If guidance must later cover one of them, drop the eval's held-out status instead of the guidance.

The scorer is deterministic, but classification is intentionally separate: a human or independent evaluator must map the raw agent response to finding IDs and forbidden claims. This avoids pretending that substring matching can judge review quality.

For an optional end-to-end run, configure any judge CLI that reads the blind judging prompt from standard input and returns the documented JSON result:

```bash
EVAL_JUDGE_COMMAND='claude -p --model opus --restricted --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 2 --max-budget-usd 0.25' \
  ./scripts/judge_eval.py android-compose-review response.md result.json
```

The judge may wrap its JSON in a fenced block or short prose; the adapter extracts it and validates it against the rubric before writing the result file. The judge is deliberately excluded from pull-request CI because model evaluation is nondeterministic, costs money, and requires user-managed credentials.

Run every custom domain eval with separate trusted agent and judge commands and retain a dated result bundle. The agent command must include `{agent}`; `{plugin_dir}` is optional and resolves to the repository root. This example runs each manifest-selected, namespaced agent in a restricted temporary workspace. `--restricted` confines file tools to that workspace, so `--add-dir "{plugin_dir}/skills"` lets agents read skill references. Add only `skills/`: the repository root also holds the rubrics.

```bash
EVAL_AGENT_COMMAND='claude -p --model sonnet --plugin-dir "{plugin_dir}" --agent mobile-a11y-agent-skills:{agent} --restricted --add-dir "{plugin_dir}/skills" --allowedTools Read Glob Grep Skill --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 8 --max-budget-usd 0.75' \
EVAL_JUDGE_COMMAND='claude -p --model opus --restricted --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 2 --max-budget-usd 0.25' \
EVAL_MODEL='agent=sonnet,judge=opus' \
./scripts/run_eval_suite.py "evals/results/$(date -u +%Y-%m-%dT%H%M%SZ)-sonnet-opus"
```

Set `EVAL_VARIANT=baseline` to send the same tasks and fixtures without the plugin. The prompt drops the agent name, and `{agent}` is not required. Score both runs with the same judge and rubrics. `summary.json` records the variant and per-eval points, so the runs compare directly. Set `EVAL_SECOND_JUDGE_COMMAND` to score every response with a second judge as well. A run then passes only when both judges pass it. The second judge writes `result-2.json` and `score-2.txt`, and `summary.json` records both scores and whether the judges agree. Reviewed bundles are kept in `evals/results/`; see [the baseline summary](evals/results/README.md).

```bash
EVAL_VARIANT=baseline \
EVAL_AGENT_COMMAND='claude -p --model sonnet --restricted --allowedTools Read Glob Grep --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 8 --max-budget-usd 0.75' \
EVAL_JUDGE_COMMAND='…same Opus judge…' EVAL_MODEL='agent=sonnet,judge=opus' \
./scripts/run_eval_suite.py "evals/results/$(date -u +%Y-%m-%dT%H%M%SZ)-sonnet-opus-baseline"
```

The repository also includes a small official Claude plugin eval under `plugin-evals/`. It verifies real namespaced agent routing and evaluates output quality in Claude Code's isolated eval runner:

```bash
claude plugin eval . --runs 1 --ablation with-without --max-cost-usd 3.00 --no-publish
```

Use the official runner for plugin loading, routing, trace, and baseline evidence. Use the custom suite for the repository's 18 detailed accessibility rubrics and deterministic scoring contract.

The manually triggered `Agent eval regression` workflow performs both runs only when the repository owner configures `CLAUDE_CODE_OAUTH_TOKEN`. It has no schedule. The custom suite uses Sonnet for the agent and Opus as an independent judge to reduce correlated evaluation bias. Without the secret, a run records an explicit skipped summary. Pull-request CI never invokes a paid model. Workflow results are retained as artifacts rather than committed automatically.

## Compiled samples

`samples/` compiles the reference examples and platform code eval fixtures, and runs semantics and property tests. Guard tests fail when a fixture loses a defect its rubric expects. The KMP and SwiftUI fixtures have static guards in `tests/test_eval_fixtures.py`. `samples/kmp` compiles the recommended KMP boundary for native UI: a shared contract, native Android and iOS adapters, and a check that the exported Objective-C header leaks no platform UI types. CI runs all three projects on every pull request:

```bash
(cd samples/android && ./gradlew assembleDebug testDebugUnitTest)
./samples/ios/test.sh
(cd samples/kmp && ./gradlew check)
```

See [samples/README.md](samples/README.md) for requirements and limits.

When the iOS job fails, CI uploads its `.xcresult` bundle for diagnosis. Successful runs do not retain the bundle.

The eval set includes defect-bearing Android, iOS, KMP, test-strategy, and regulatory cases; clean Compose, Android Views, SwiftUI, and UIKit cases that penalize invented findings; and an EN 301 549 scenario that tests technology self-scoping.

## Non-goals

- Claiming WCAG, EAA, ADA, Section 508, or EN 301 549 compliance from static review alone.
- Simulating exact TalkBack or VoiceOver speech without device verification.
- Replacing testing with disabled users.
- Forcing identical Android and iOS accessibility implementations.
- Flutter, React Native, and other non-Kotlin cross-platform UI frameworks.
- Providing legal advice.

## Security

Review [SECURITY.md](SECURITY.md) before running agents with shell access or using an external eval judge. Projects can optionally start from the [deny-only Claude Code settings template](templates/claude/README.md).

## Distribution

Use the repository directly as a Claude Code plugin or copy `agents/` and `skills/` into a project. GitHub Releases are intentionally not generated; tags may still identify reviewed snapshots if versioned distribution is needed later.

## License

MIT. See [LICENSE](LICENSE).
