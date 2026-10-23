---
name: android-a11y
description: Implement or review Android accessibility in Jetpack Compose or Views, including TalkBack semantics, focus, touch targets, font scaling, autofill, errors, live regions, motion, contrast, and Android host or device testing.
---

# Implement Android accessibility

1. Prefer native controls and their built-in semantics.
2. Model one logical control as one accessibility node; hide decorative children.
3. Expose changing value and state through semantics before adding announcements.
4. Use live regions only for important asynchronous changes.
5. Use `FocusRequester` for input focus and accessibility focus APIs only when context changes.
6. Preserve platform keyboard, paste, selection, and autofill behavior.
7. Support font scale, RTL, dark theme, remove animations, and 48 dp targets.
8. Add JVM tests for platform-neutral behavior and device tests for Compose semantics or Android framework behavior.
9. Verify TalkBack interaction on a real device before claiming speech behavior.

Read [references/android-patterns.md](references/android-patterns.md) for API-level guidance.
