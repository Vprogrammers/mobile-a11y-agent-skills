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
| `mobile-a11y-workflow` | Agent routing, repair/re-review loop, source policy, safety rules, and the completion report every agent follows |
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

The agents preload their skills by name, so they work from plugin installation or copied project directories without repository-relative paths. Claude Code does not load a `CLAUDE.md` from a plugin, so the shared rules live in the `mobile-a11y-workflow` skill, which ships with the agents. For copied installs, optionally add the short pointer in [`distribution/light/CLAUDE.md`](distribution/light/CLAUDE.md) to the project's `CLAUDE.md`.

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

The `mobile-a11y-workflow` skill defines the order: `kmp-a11y-architect` when shared APIs or boundaries change, then the Android and/or iOS engineer, then `accessibility-test-engineer`, an optional read-only architecture check, and `accessibility-reviewer` for an independent final review. P0/P1 findings go back to the engineer for at most two repair/re-review cycles. Report device checks separately using [the real-device evidence template](skills/mobile-a11y-testing/references/real-device-evidence-template.md).

## Validation and evals

```bash
./scripts/validate.sh
```

The validation command checks plugin metadata, skill and agent structure, source freshness, local links, eval manifests, scripts, installation, and unit tests. Pull-request CI also runs the compiled Android, iOS, and KMP samples and repair-eval self-checks.

See [Evaluation guide](docs/evals.md) for blind evaluation, deterministic scoring, baseline comparison, independent judges, official plugin evals, repair evals, and paid workflow setup.

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
