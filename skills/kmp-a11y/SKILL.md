---
name: kmp-a11y
description: Design or review Kotlin Multiplatform accessibility architecture. Use for shared accessibility state, expect/actual decisions, native Android and iOS UI ownership, Compose and SwiftUI integration, Compose Multiplatform shared UI on iOS, Kotlin/Native export, Swift interop, SKIE, Swift export, binary compatibility, or platform dependency boundaries.
---

# Design KMP accessibility

1. Determine whether iOS uses native SwiftUI/UIKit or Compose Multiplatform shared UI; the boundary rules differ.
2. Share product meaning, state, validation, formatting, privacy rules, and localizable text contracts.
3. With native UI, keep platform semantics objects, views, focus handles, announcements, colors, fonts, and assistive-technology APIs native.
4. Prefer interfaces and dependency injection when common behavior needs a platform capability; use `expect`/`actual` when the platform distinction is inherent and stable.
5. Expose Swift-friendly primitives, classes, enums, and callbacks; treat coroutines, generics, sealed hierarchies, and collections as explicit interop decisions.
6. Evaluate direct Kotlin/Native export, Swift export, and SKIE against project maturity, toolchain, binary surface, and consumer requirements rather than selecting one by default.
7. Keep optional platform services and heavy dependencies outside the core artifact.
8. Test shared behavior in common tests and native adapters in platform test targets.
9. With Compose Multiplatform shared UI, use Compose semantics as the iOS implementation surface, verify iOS-only capabilities on the Compose screen, and host gaps in native views when needed.
10. Document consumer configuration, localization ownership, export setup, and device verification.

Read [references/kmp-boundaries.md](references/kmp-boundaries.md) before changing a public API.
