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
5. Report device checks separately from automated results.

## Quality checks

| Check | What it covers | Command |
|---|---|---|
| Structure | Skill and agent frontmatter, skill names used by agents, reference review dates and sources, manifest versions, eval markers, links | `./scripts/validate.sh` |
| Android samples | Reference examples and eval fixtures compile; Robolectric semantics tests | `cd samples/android && ./gradlew assembleDebug testDebugUnitTest` |
| iOS samples | Reference examples and eval fixture compile; XCTest property tests | `./samples/ios/test.sh` |
| Evals | Agent finds seeded defects without invented evidence; one negative control | Manual, see [evals/README.md](evals/README.md) |

CI runs the first three on every pull request.

## Non-goals

- Claiming WCAG, EAA, ADA, Section 508, or EN 301 549 compliance from static review alone.
- Simulating exact TalkBack or VoiceOver speech without device verification.
- Replacing testing with disabled users.
- Forcing identical Android and iOS accessibility implementations.
- Flutter, React Native, and other non-Kotlin cross-platform UI frameworks.
- Providing legal advice.

## License

MIT. See [LICENSE](LICENSE).
