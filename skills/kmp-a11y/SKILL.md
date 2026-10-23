---
name: kmp-a11y
description: Design or review Kotlin Multiplatform accessibility architecture, shared state and text contracts, source-set boundaries, Android and iOS native UI ownership, Kotlin/Native export, and Swift interop without leaking platform APIs across targets.
---

# Design KMP accessibility

1. Share product meaning, state, validation, formatting, privacy rules, and localizable text contracts.
2. Keep TalkBack, VoiceOver, Compose semantics, SwiftUI modifiers, UIKit traits, focus objects, colors, fonts, and views in platform source sets.
3. Expose primitive or stable data to Swift where possible.
4. Avoid platform framework types in `commonMain`.
5. Keep optional platform integrations in separate modules when they add heavy dependencies.
6. Do not force identical platform APIs when native conventions differ.
7. Test shared behavior in common tests and platform adapters in platform test targets.
8. Document what consumers must configure, export, localize, and verify on devices.

Read [references/kmp-boundaries.md](references/kmp-boundaries.md) before changing a public API.
