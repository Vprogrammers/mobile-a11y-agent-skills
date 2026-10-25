# Mobile accessibility instructions

Use the installed accessibility agents and skills when work affects Android, iOS, or Kotlin Multiplatform UI behavior.

Invoke the `mobile-a11y-workflow` skill before planning or delegating accessibility work. It defines which agent runs when, the repair/re-review loop, scope limits, source policy, safety rules, and the completion report every agent follows.

| Work | Agent |
|---|---|
| Shared public APIs, exports, dependencies, source-set ownership, native UI boundaries, Compose Multiplatform UI | `kmp-a11y-architect` |
| Compose, Android Views, TalkBack, Voice Access, Switch Access | `android-a11y-engineer` |
| SwiftUI, UIKit, VoiceOver, Voice Control, Switch Control, Dynamic Type | `ios-a11y-engineer` |
| Automated and device test coverage | `accessibility-test-engineer` |
| Independent final review | `accessibility-reviewer` |
