---
name: mobile-a11y-testing
description: Plan, implement, or review accessibility tests for Android, iOS, and Kotlin Multiplatform, including shared unit tests, Compose semantics, Android device tests, XCTest, XCUITest, automated audits, and manual TalkBack or VoiceOver verification.
---

# Test mobile accessibility

1. Define the observable requirement before selecting a test layer.
2. Use common tests for normalization, state, masking, descriptions, and layout decisions.
3. Use platform unit or host tests for adapters and semantics construction.
4. Use Android device tests for framework behavior, Compose UI, autofill, focus, and IME integration.
5. Use XCTest or Kotlin/Native tests for iOS adapter logic.
6. Use XCUITest for accessible labels, values, identifiers, actions, flow state, and automated audits.
7. Reserve actual TalkBack, VoiceOver, Voice Control, Switch Control, keyboard, and autofill behavior for device verification.
8. Report passed, failed, and skipped checks honestly.

Read [references/test-matrix.md](references/test-matrix.md) to choose the narrowest useful layer.
