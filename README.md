# Mobile A11y Agent Skills

Production-focused accessibility agents and skills for Android, iOS, and Kotlin Multiplatform.

The project helps AI coding agents implement and review accessible native mobile interfaces instead of applying web accessibility rules blindly. It covers Jetpack Compose, Android Views, SwiftUI, UIKit, Kotlin Multiplatform boundaries, TalkBack, VoiceOver, Voice Control, Switch Control, Dynamic Type, font scaling, reduced motion, contrast, autofill, focus, and device testing.

> Early release: APIs and instructions may evolve while the skills are validated against real projects.

## What makes this different

- Native mobile accessibility, not an ARIA checklist adapted to mobile.
- Shared product requirements with platform-native implementations.
- Clear separation between what automated tests can prove and what requires a real device.
- KMP guidance for deciding what belongs in common code and what must stay in Android or iOS code.
- Implementation, testing, architecture, and independent review agents.
- Privacy-aware guidance for OTP, passwords, payment fields, and other sensitive input.

## Included agents

| Agent | Use it for |
|---|---|
| `kmp-a11y-architect` | Shared contracts, source-set boundaries, dependencies, and Swift interop |
| `android-a11y-engineer` | Compose or Views implementation and TalkBack behavior |
| `ios-a11y-engineer` | SwiftUI or UIKit implementation and VoiceOver behavior |
| `accessibility-test-engineer` | Unit, semantics, UI, and device-test coverage |
| `accessibility-reviewer` | Independent review before a pull request or release |

## Included skills

| Skill | Focus |
|---|---|
| `mobile-a11y-review` | Cross-platform audit workflow and severity-based findings |
| `android-a11y` | TalkBack, Compose semantics, Views, focus, autofill, and Android testing |
| `ios-a11y` | VoiceOver, Voice Control, SwiftUI, UIKit, Dynamic Type, and XCUITest |
| `kmp-a11y` | Shared accessibility contracts with native UI and safe Swift interop |
| `mobile-a11y-testing` | Automated and manual verification across Android and iOS |

## Install with Claude Code

Add the repository as a plugin marketplace:

```text
/plugin marketplace add Vprogrammers/mobile-a11y-agent-skills
```

Then install the plugin from the marketplace UI. You can also copy the required folders into a project:

```text
.claude/
├── agents/
└── skills/
```

Copy this repository's `agents/*` into `.claude/agents/` and `skills/*` into `.claude/skills/`.

## Use with other agents

The skills use the open `SKILL.md` format. Copy an individual skill directory into the skill location used by Codex, Cursor, or another compatible coding agent. Agent markdown files are Claude Code-specific; the underlying skills are intentionally tool-agnostic.

## Recommended workflow

1. Use `kmp-a11y-architect` when public APIs, dependencies, or source-set boundaries change.
2. Use the Android and/or iOS implementation agent.
3. Use `accessibility-test-engineer` to close coverage gaps.
4. Use `accessibility-reviewer` for an independent final pass.
5. Report automated results separately from manual device verification.

## Non-goals

- Claiming WCAG or legal compliance from static code review alone.
- Simulating real TalkBack or VoiceOver speech without device verification.
- Replacing disabled-user testing.
- Forcing identical Android and iOS accessibility implementations.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Keep skills concise, sourced from platform behavior, and explicit about verification limits.

## License

MIT. See [LICENSE](LICENSE).
