# Mobile accessibility instructions

Use the installed accessibility agents and skills when work affects Android, iOS, or Kotlin Multiplatform UI behavior.

## Workflow

- Use `kmp-a11y-architect` before changing shared APIs, exports, dependencies, or source-set ownership.
- Use `android-a11y-engineer` for Compose, Android Views, TalkBack, Voice Access, Switch Access, keyboard, and Android autofill work.
- Use `ios-a11y-engineer` for SwiftUI, UIKit, VoiceOver, Voice Control, Switch Control, Dynamic Type, and iOS autofill work.
- Use `accessibility-test-engineer` to select and implement the narrowest useful automated and device tests.
- Use `accessibility-reviewer` after UI or semantics changes and before finalizing a pull request.

## Boundaries

- Keep Android and iOS accessibility implementations native unless the project intentionally uses Compose Multiplatform shared UI.
- Preserve shared product rules in KMP without leaking Android or Apple UI types into shared APIs.
- Separate code evidence, automated checks, simulator evidence, and real-device assistive-technology verification.
- Never claim exact TalkBack or VoiceOver speech without device verification.
- Never claim WCAG, EN 301 549, EAA, ADA, or Section 508 compliance from static or automated review alone.
- Treat passwords, one-time codes, payments, identity, location, health data, accessibility trees, recordings, and logs as sensitive.
- Do not introduce permissions, analytics, logging, or data collection for accessibility convenience.
- Verify version-sensitive platform and regulatory claims against current official sources.
- Do not include generated-by, assistant attribution, or co-author trailers in commits.
