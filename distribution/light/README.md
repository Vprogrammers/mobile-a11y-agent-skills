# Mobile A11y Agent Skills Lite

Accessibility agents and skills for Claude Code that help implement, test, and review native Android, iOS, and Kotlin Multiplatform UI: Compose, Views, SwiftUI, UIKit, TalkBack, VoiceOver, Voice Access and Voice Control, Dynamic Type and font scaling, focus, autofill, and privacy.

This is an early release and a work in progress. Suggestions, corrections, and real-device results are all welcome; see [Contributing](#contributing).

This repository is a copy-ready mirror generated from [`Vprogrammers/mobile-a11y-agent-skills`](https://github.com/Vprogrammers/mobile-a11y-agent-skills), where the documentation, compiled samples, evals, and verification status live.

## What you get

| Agent | Use it for |
|---|---|
| `kmp-a11y-architect` | Shared contracts, source-set boundaries, Swift export and SKIE interop |
| `android-a11y-engineer` | Compose or Views fixes, TalkBack and Voice Access behavior, and a focused regression test |
| `ios-a11y-engineer` | SwiftUI or UIKit fixes, VoiceOver and Voice Control behavior, and a focused regression test |
| `accessibility-test-engineer` | Test strategy, new test layers, audits, and device-verification plans |
| `accessibility-reviewer` | Independent, severity-based review before a pull request or release |

Six skills hold the platform guidance, review checklist, test matrix, and the shared workflow every agent follows. The agents separate what code and automated tests prove from what still needs a real device, and they never claim legal compliance.

## Install

As a Claude Code plugin:

```text
/plugin marketplace add Vprogrammers/mobile-a11y-agent-skills
/plugin install mobile-a11y-agent-skills@vprogrammers-mobile-a11y
```

Or copy the agents and skills into the `.claude/` directory at the root of your project:

```bash
mkdir -p /path/to/your-project/.claude
cp -R .claude/agents .claude/skills /path/to/your-project/.claude/
```

Then add the short instructions from `.claude/CLAUDE.md`. If your project has no `.claude/CLAUDE.md`, copy the file; otherwise, merge its sections into your existing file.

## Contents

```text
.claude/
├── CLAUDE.md
├── agents/
└── skills/
```

The generated `.source.json` records the source repository and commit.

## Status

Guidance is checked against official platform documentation and compiled in the main repository's samples. A first pass on real devices covered TalkBack on Android 17 and VoiceOver on iOS 26; see the [verification status](https://github.com/Vprogrammers/mobile-a11y-agent-skills#verification-status). Always verify behavior on your own supported devices.

## Contributing

Every suggestion is welcome, from a typo to a new pattern. Please open issues, discussions, and pull requests in the [main repository](https://github.com/Vprogrammers/mobile-a11y-agent-skills):

- [Report wrong or outdated guidance](https://github.com/Vprogrammers/mobile-a11y-agent-skills/issues/new?template=guidance-correction.yml)
- [Share a real-device result](https://github.com/Vprogrammers/mobile-a11y-agent-skills/issues/new?template=device-result.yml)
- [Suggest an improvement](https://github.com/Vprogrammers/mobile-a11y-agent-skills/issues/new?template=suggestion.yml)
- [Ask a question or discuss an idea](https://github.com/Vprogrammers/mobile-a11y-agent-skills/discussions)

This mirror is regenerated from the main repository, so changes made here would be overwritten. See the [contributing guide](https://github.com/Vprogrammers/mobile-a11y-agent-skills/blob/main/CONTRIBUTING.md).
