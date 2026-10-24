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

## Example prompts

```text
Use accessibility-reviewer to review this PR. Separate proven findings from device checks.
```

```text
Use android-a11y-engineer to fix the TalkBack order in this Compose screen without changing the shared API.
```

```text
Use kmp-a11y-architect to decide whether reduced-motion state belongs behind an interface or expect/actual.
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
5. Run `./scripts/validate.sh` and report device checks separately.

## Validation and evals

```bash
./scripts/validate.sh
```

The validator checks skill and agent metadata, invoked skill names, duplicate names, local links, plugin version consistency, required review dates, executable permissions, and typed eval manifests/rubrics. External links are intentionally optional to keep pull-request CI deterministic; a scheduled workflow checks them monthly:

```bash
CHECK_EXTERNAL_LINKS=1 ./scripts/validate.sh
```

Evaluation scenarios live in `evals/`. Each manifest entry points to a prompt, raw code fixture, scoring rubric, minimum score, and forbidden claims. Give only the prompt and fixture to the agent; score the result afterward with the rubric to avoid leaking expected findings.

Rubrics keep finding `kind` separate from severity. Each finding has explicit acceptance `criteria`. Severity uses the `P0`–`P3` scale defined in `mobile-a11y-review` for defects and is `null` for architecture, interop, testing, verification, compliance, dependency, or recommendation criteria.

Record the assessment using rubric finding IDs. Severity is optional for backward compatibility; when supplied for a defect, it must match the rubric:

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

The scorer is deterministic, but classification is intentionally separate: a human or independent evaluator must map the raw agent response to finding IDs and forbidden claims. This avoids pretending that substring matching can judge review quality.

For an optional end-to-end run, configure any judge CLI that reads the blind judging prompt from standard input and returns the documented JSON result:

```bash
EVAL_JUDGE_COMMAND='claude -p' \
  ./scripts/judge_eval.py android-compose-review response.md result.json
```

The judge is deliberately excluded from CI: model evaluation is nondeterministic, costs money, and requires user-managed credentials. The deterministic scorer still validates its output.

Run repository tests with:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/install_smoke.py .
```

## Compiled samples

`samples/` compiles the reference examples and the Android and iOS eval fixtures, and runs semantics and property tests. Guard tests fail when a fixture loses a defect its rubric expects. CI runs both projects on every pull request:

```bash
(cd samples/android && ./gradlew assembleDebug testDebugUnitTest)
./samples/ios/test.sh
```

See [samples/README.md](samples/README.md) for requirements and limits.

The eval set includes positive Android, iOS, KMP, test-strategy, and regulatory cases plus a clean-screen case that penalizes invented findings.

## Non-goals

- Claiming WCAG, EAA, ADA, Section 508, or EN 301 549 compliance from static review alone.
- Simulating exact TalkBack or VoiceOver speech without device verification.
- Replacing testing with disabled users.
- Forcing identical Android and iOS accessibility implementations.
- Flutter, React Native, and other non-Kotlin cross-platform UI frameworks.
- Providing legal advice.

## License

MIT. See [LICENSE](LICENSE).
