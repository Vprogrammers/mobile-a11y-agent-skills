---
name: kmp-a11y
description: Design or review Kotlin Multiplatform accessibility architecture. Use for shared accessibility state, expect/actual decisions, native Android and iOS UI ownership, Compose and SwiftUI integration, Kotlin/Native export, Swift interop, SKIE, Swift export, binary compatibility, or platform dependency boundaries.
---

# Design KMP accessibility

1. Share product meaning, state, validation, formatting, privacy rules, and localizable text contracts.
2. Keep platform semantics objects, views, focus handles, announcements, colors, fonts, and assistive-technology APIs native.
3. Prefer interfaces and dependency injection when common behavior needs a platform capability; use `expect`/`actual` when the platform distinction is inherent and stable.
4. Expose Swift-friendly primitives, classes, enums, and callbacks; treat coroutines, generics, sealed hierarchies, and collections as explicit interop decisions.
5. Evaluate direct Kotlin/Native export, Swift export, and SKIE against project maturity, toolchain, binary surface, and consumer requirements rather than selecting one by default.
6. Keep optional platform services and heavy dependencies outside the core artifact.
7. Test shared behavior in common tests and native adapters in platform test targets.
8. Document consumer configuration, localization ownership, export setup, and device verification.

Read [references/kmp-boundaries.md](references/kmp-boundaries.md) before changing a public API.
