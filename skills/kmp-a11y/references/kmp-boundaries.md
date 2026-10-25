# KMP accessibility boundaries

Last reviewed: 2026-10-25. Swift export, SKIE, and Compose Multiplatform accessibility change quickly; verify against the Kotlin and Compose Multiplatform versions used by the project.
Review interval: 180 days.

Two architectures need different rules:

- **Shared logic, native UI**: Compose on Android, SwiftUI or UIKit on iOS. The rest of this file applies.
- **Shared UI with Compose Multiplatform**: see [Compose Multiplatform shared UI](#compose-multiplatform-shared-ui).

## Share

- immutable state and state transitions;
- normalization, validation, progress, and error models;
- privacy and redaction policy;
- domain-level actions and capabilities;
- contrast calculations using primitive color values when the algorithm is genuinely shared;
- localization keys, arguments, or provider interfaces when ownership is explicit;
- platform-neutral test fixtures and requirements.

## Keep native

- Compose `Modifier.semantics` and Android `AccessibilityNodeInfo`;
- SwiftUI accessibility modifiers and UIKit `UIAccessibility` APIs;
- TalkBack/VoiceOver focus and announcements;
- native views, typography, colors, touch targets, haptics, autofill, IME, rotors, and custom actions;
- platform test frameworks and real-device verification.

## Interface versus expect/actual

Prefer an interface when the app can inject a capability and tests benefit from a fake:

```kotlin
interface AccessibilityPreferences {
    val reduceMotion: StateFlow<Boolean>
}
```

`StateFlow` keeps the example short, but it reaches Swift as a generic Kotlin class without native observation. When Swift consumers observe the preference, decide the interop explicitly: add a callback-based listener, or use SKIE or Swift export, which map flows to `AsyncSequence`. See [Swift interop](#swift-interop).

Prefer `expect`/`actual` only when every target needs the same compile-time API and platform selection is intrinsic:

```kotlin
expect fun platformAccessibilityPreferences(): AccessibilityPreferences
```

Do not use `expect`/`actual` merely to hide poor ownership or to export native UI types through common code.

A no-argument Android `actual` needs a global `Context` to read settings. Prefer constructor injection, such as `AndroidAccessibilityPreferences(context)` and `IosAccessibilityPreferences()`, created by each app and passed to shared code.

## State contract example

Good shared API:

```kotlin
data class ValidationState(
    val messageKey: String?,
    val isBlocking: Boolean,
)
```

Android maps it to Compose `error()`/state semantics; iOS maps it to native label/value/error presentation. Common code does not decide TalkBack or VoiceOver speech.

## Swift interop

- Prefer explicit names, primitives, classes, enums, and small callbacks.
- Avoid leaking Compose, Android, UIKit, or SwiftUI types.
- Review default arguments, overloads, generic variance, nullable primitives, sealed classes, value classes, suspend functions, `Flow`, and Kotlin collections from Swift.
- Retain Kotlin objects that own native state for as long as Swift views use them.
- Verify generated headers/interfaces and a real Swift consumer sample. Automate a header check that fails when exported declarations mention UIKit or Compose types. Strip comments first, because KDoc is copied into the header.
- Header checks cannot catch typealiased platform types: `UIAccessibilityTraits` exports as `uint64_t`. Review common and iOS source for platform imports as well.
- Treat Objective-C export annotations and naming as public API.

## Swift export and SKIE

- Kotlin/Native framework export through Objective-C headers is the baseline and must remain understandable without optional tooling.
- Swift export is Alpha as of this review (kotlinlang.org, checked 2026-10-25): it works only with direct Xcode integration, erases generic type parameters, ignores types inheriting `List`/`Set`/`Map`, and supports only final classes that inherit directly from `Any`. Suspend functions become `async` and flows become `AsyncSequence`. Do not make a public library contract depend on it without accepting breaking changes.
- SKIE can improve coroutines, flows, sealed hierarchies, and Swift ergonomics, but adds a build dependency and configuration surface. Keep it optional unless the library contract requires it.
- Document which layer consumers must configure and test both direct and enhanced interop paths when both are supported.

## Compatibility and dependencies

- Keep Play Services, analytics, message retrieval, platform test frameworks, and optional interop plugins out of the core runtime artifact unless every consumer requires them.
- Review API/ABI compatibility when public state, enum values, constructors, exported names, or framework packaging changes.
- Verify Android publication, iOS framework/XCFramework export, linker settings, and sample-app consumption.

## Reference sample

The repository's `samples/kmp` project compiles this file's native-UI pattern:

- `commonMain`: `ValidationState`, the `AccessibilityPreferences` interface, a Swift-friendly `MotionPolicy` enum;
- `androidMain`: Compose `error()` mapping and animator-scale preferences;
- `iosMain`: `UIAccessibilityIsReduceMotionEnabled` with its change notification;
- tests: common tests with a fake, a Robolectric host test, iOS simulator tests, and an exported-header check.

It does not cover Compose Multiplatform shared UI.

## Compose Multiplatform shared UI

This section is draft guidance. The official documentation does not list iOS accessibility limitations exhaustively, so treat every iOS behavior as unverified until tested on a device.

- Compose semantics are mapped to native iOS accessibility objects, so `contentDescription`, `role`, `stateDescription`, `heading()`, and traversal properties are the shared implementation surface. This is the exception to keeping semantics native: the Compose UI itself is the iOS UI.
- Material components map automatically. Give custom components explicit semantics and verify them with VoiceOver on iOS, not only with Android tests.
- `testTag` maps to `accessibilityIdentifier`, so XCUITest and `performAccessibilityAudit()` can run against Compose screens.
- Material3 `ColorScheme` has no built-in high-contrast variant. Detect Increase Contrast on iOS (`UIAccessibilityDarkerSystemColorsEnabled` and its change notification) through a platform capability and supply your own palette.
- Before relying on an iOS-only capability (rotors, Voice Control input labels, Large Content Viewer, UIKit notifications, modal containment), verify that it works on the Compose screen. When it does not, host that part in a native SwiftUI/UIKit view through interop, or record the gap and its affected users.
- Keep platform preference reads (reduced motion, increased contrast, font scale) behind the same injected interfaces described above.
- Compose Multiplatform 1.8.0 removed the `AccessibilitySyncOptions` tree-synchronization setting; the tree now syncs lazily. Remove that configuration when upgrading.
- The official iOS page names VoiceOver, native gestures, AssistiveTouch, and Full Keyboard Access as supported. It does not mention Switch Control, Voice Control, or Dynamic Type, so test those on a device and record each result before claiming support.
- Shared `Canvas` drawings and charts need the same explicit semantics as on Android. Verify on iOS that VoiceOver reaches each exposed part; Android semantics tests do not establish it.

Official sources:

- Kotlin/Objective-C interop: https://kotlinlang.org/docs/native-objc-interop.html
- Swift export: https://kotlinlang.org/docs/native-swift-export.html
- SKIE: https://skie.touchlab.co/
- Compose Multiplatform accessibility: https://kotlinlang.org/docs/multiplatform/compose-accessibility.html
- Compose Multiplatform iOS accessibility: https://kotlinlang.org/docs/multiplatform/compose-ios-accessibility.html
