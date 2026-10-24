---
name: mobile-a11y-testing
description: Plan, implement, or review accessibility tests for Android, iOS, and Kotlin Multiplatform. Use for Compose semantics tests, enableAccessibilityChecks, Espresso AccessibilityChecks, Android device tests, XCTest, XCUITest, performAccessibilityAudit, Accessibility Inspector, TalkBack or VoiceOver test plans, regression coverage, and CI commands.
---

# Test mobile accessibility

1. Define the observable requirement and affected user before selecting a test layer.
2. Discover existing modules, source sets, Gradle tasks, Xcode schemes, destinations, dependencies, and CI environment.
3. Use common tests for domain state, validation, formatting, privacy, and platform-neutral decisions.
4. Use Android host tests only when Robolectric or the configured environment supports the required behavior; use instrumentation for framework integration.
5. Use XCTest for native logic and XCUITest for user-visible accessibility structure and flows.
6. Run automated scanners/audits as supplemental evidence, triage each result, and suppress narrowly.
7. Reserve exact TalkBack, VoiceOver, Voice Control, Switch Control/Access, keyboard, and system-service behavior for device verification.
8. Report passed, failed, skipped, unavailable, and manual checks separately.

Read [references/test-matrix.md](references/test-matrix.md) for APIs, discovery commands, and evidence boundaries. Use [the real-device evidence template](references/real-device-evidence-template.md) when recording manual results.
