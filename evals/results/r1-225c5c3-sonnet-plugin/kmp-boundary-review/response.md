# KMP boundary review: `AccessibilityContract.kt` as a `commonMain` public API

**Verdict: don't ship it as written.** The contract puts Compose, Android and UIKit types into common code, and it names an optional Android service in the core API.

Three limits on this review:
- I could not use the `kmp-a11y-architect` agent. No agent-launching tool was available, so I applied the `kmp-a11y` skill and its `kmp-boundaries.md` reference directly.
- The fixture file isn't on disk at `evals/kmp-boundary-review/AccessibilityContract.kt`. I reviewed the copy pasted in your prompt, and I edited nothing.
- The fixture does not say whether iOS uses native SwiftUI/UIKit or Compose Multiplatform shared UI. I assumed native UI and flag this below as decision 1.

## 1. Recommended public API and ownership

**Findings on the fixture**

| Member | Problem |
|---|---|
| `applyComposeSemantics(SemanticsPropertyReceiver)` | Puts a Compose type in common code. Semantics objects are native-owned, and the shared layer should not decide TalkBack or VoiceOver output. |
| `iosTraits: UIAccessibilityTraits` | `platform.UIKit` doesn't belong in `commonMain`, and it would not compile for Android targets. The typealias also exports to Swift as `uint64_t`, so a header check would miss it. |
| `enableSmsRetriever()` | An Android Play Services capability with no accessibility meaning. It pulls a heavy optional dependency into the core API. |
| `events: Flow<SharedAccessibilityError>` | `Flow` and a sealed hierarchy are not Swift-friendly by default. It also mixes error state with one-shot events. |
| `SharedAccessibilityError` | `reason: String` is free text. It has no localization ownership and no privacy rule, so it risks carrying user input. |
| `BetaInteropApi` import | It is unused, and it suggests a dependency on an unstable API. |

**Recommended shape**

- **Shared in `commonMain`:**
  - An immutable state model, for example `ValidationState(messageKey: String?, isBlocking: Boolean)`, with a stable error code or enum instead of `reason: String`.
  - Validation and privacy/redaction rules.
  - Domain-level actions.
  - A small `AccessibilityPreferences` interface for injected capabilities.
  - A Swift-friendly enum such as `MotionPolicy`.
- **Native-owned:**
  - Android maps the state to Compose `error()` and `stateDescription` in its own module.
  - iOS maps it to UIKit/SwiftUI label, value and traits in its own module.
  - Focus, announcements, traits and the SMS Retriever flow stay native.
- **Optional services:** move SMS Retriever, or any similar service, to a separate opt-in Android artifact or an app-injected interface.
- **Localization:** decide who owns text, and expose keys plus arguments or a provider interface to match.
- **Pattern for platform capabilities:** use an interface with constructor injection, for example `AndroidAccessibilityPreferences(context)` and `IosAccessibilityPreferences()`. Use `expect`/`actual` only where the platform split is inherent and stable. Don't use a no-argument Android `actual` that needs a global `Context`.

## 2. Android and iOS integration points

**Android**
- `androidMain` or the app maps the shared state to Compose `error()` and state semantics.
- Preferences such as animator scale come from an injected `AndroidAccessibilityPreferences(context)`.
- SMS Retriever, if wanted, goes in a separate optional module. Keep Play Services out of the core runtime artifact.

**iOS**
- `iosMain` or the app implements `IosAccessibilityPreferences`, using `UIAccessibilityIsReduceMotionEnabled` and its change notification. That keeps UIKit inside `iosMain`.
- SwiftUI/UIKit code applies label, value, error and traits from the shared state. VoiceOver speech remains a native decision.
- Swift code must retain any Kotlin object that owns native state for as long as its views use it.

**If iOS uses Compose Multiplatform shared UI instead:** Compose semantics become the iOS implementation surface, so a Compose type would be less wrong in that setup. Even so, keep it out of the public cross-module contract. Verify iOS behavior on a real device, and host any gaps (rotors, Voice Control labels, Large Content Viewer) in native views.

## 3. Swift export, binary compatibility, and dependency risks

**Swift interop**
- **Objective-C export baseline:** it must work without optional tooling. `Flow` and sealed types become awkward types there, so decide the Swift shape explicitly. Options are a callback or listener with a cancel handle, a final class, or an enum.
- **Swift export (Alpha as of the 2026-10-24 review):**
  - It works only with direct Xcode integration.
  - It erases generics.
  - It ignores types that inherit `List`, `Set` or `Map`.
  - It supports only final classes that inherit directly from `Any`.
  - Don't make the public contract depend on it without accepting breaking changes.
- **SKIE:** it can improve `Flow` and sealed ergonomics, but it adds a build dependency and configuration surface. Keep it optional, document which layer consumers configure, and test both the direct and the SKIE paths if both are supported.
- **Header check:** automate a check that fails when the exported header mentions UIKit or Compose types. Strip comments first, because KDoc is copied into the header. It cannot catch typealiased platform types, so also scan common and iOS sources for platform imports.
- **Annotations and naming:** treat Objective-C export annotations and names as public API.

**Binary compatibility**
- Run an API/ABI validator (binary-compatibility-validator or the Kotlin ABI tooling, whichever the project uses) over the public surface.
- Removing the Compose, UIKit and Play Services members before the first release is much cheaper than a later breaking change.
- Treat these as ABI-sensitive: sealed subtypes, data class `copy`/`componentN`, enum entries, constructors and exported names.
- Prefer a non-data class or explicit factories for evolving types.
- Note that `InvalidInput` as a data class locks in its property set.

**Dependency risks**
- `commonMain` currently needs Compose UI and `platform.UIKit`, and the latter breaks the Android and common compilation.
- `kotlinx.coroutines` becomes a transitive API dependency if `Flow` stays public.
- Play Services must stay out of the core artifact.
- Optional interop plugins (SKIE) must not be required.

## 4. Automated and real-device tests

**Automated**
- Common tests on a fake `AccessibilityPreferences`: validation state transitions, redaction and privacy rules, and stable error codes.
- Android host or Robolectric tests: shared state maps to Compose `error()`/`stateDescription` (check with `SemanticsMatcher`), and the preferences adapter reads animator scale. Android accessibility checks run through Compose test `enableAccessibilityChecks`.
- iOS simulator tests for `IosAccessibilityPreferences` and the change notification. XCTest or XCUITest with `performAccessibilityAudit()` on the native screens.
- An exported-header check for UIKit and Compose type names, with comments stripped. Also a source check for platform imports in `commonMain`.
- An API/ABI dump check in CI, plus publishing checks: the Android artifact, the iOS XCFramework, linker settings and sample-app consumption.
- A real Swift consumer sample that compiles against both the direct Objective-C export and the SKIE path, if SKIE is supported.

**Real device**
- TalkBack on Android and VoiceOver on iOS: error announcement and focus after invalid input, and state and value readout.
- Reduce Motion toggled live on both platforms.
- Voice Access and Voice Control on the forms.
- Font scale and Dynamic Type at large sizes.
- If SMS Retriever is offered: verify it on a device with Play Services, and check that the screen-reader flow still works when the code autofills.

## 5. Unresolved product and platform decisions

1. **UI architecture on iOS:** native SwiftUI/UIKit, or Compose Multiplatform shared UI? This sets the whole boundary.
2. **Contract purpose:** is this a state/validation contract, or a platform-capabilities contract? The fixture mixes both.
3. **SMS Retriever:** is it in scope at all, and in which optional artifact or app-injected interface? It isn't an accessibility concern.
4. **Event delivery to Swift:** callback, `Flow` with SKIE, or Swift export `AsyncSequence`? This depends on the minimum supported toolchain.
5. **Swift export:** supported, experimental, or unsupported as a consumer path? It is Alpha as of 2026-10-24.
6. **Localization ownership:** are keys with arguments, a provider interface, or resolved strings in the contract?
7. **Error taxonomy:** which stable codes replace `reason: String`, and what can never be included, since it could carry user input?
8. **Compatibility policy:** which Kotlin and Compose Multiplatform versions are supported, and does the library promise ABI stability, or will it stay `@ExperimentalApi` until 1.0?
9. **Increase Contrast and other preferences:** which preferences does the shared layer expose?
