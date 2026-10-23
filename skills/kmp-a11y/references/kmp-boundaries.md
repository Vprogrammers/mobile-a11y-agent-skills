# KMP accessibility boundaries

Last reviewed: 2026-10-23

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

Prefer `expect`/`actual` only when every target needs the same compile-time API and platform selection is intrinsic:

```kotlin
expect fun platformAccessibilityPreferences(): AccessibilityPreferences
```

Do not use `expect`/`actual` merely to hide poor ownership or to export native UI types through common code.

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
- Verify generated headers/interfaces and a real Swift consumer sample.
- Treat Objective-C export annotations and naming as public API.

## Swift export and SKIE

- Kotlin/Native framework export is the baseline and must remain understandable without optional tooling.
- Swift export may improve native Swift API shape but can be experimental or toolchain-constrained; verify current Kotlin support and limitations before adoption.
- SKIE can improve coroutines, flows, sealed hierarchies, and Swift ergonomics, but adds a build dependency and configuration surface. Keep it optional unless the library contract requires it.
- Document which layer consumers must configure and test both direct and enhanced interop paths when both are supported.

## Compatibility and dependencies

- Keep Play Services, analytics, message retrieval, platform test frameworks, and optional interop plugins out of the core runtime artifact unless every consumer requires them.
- Review API/ABI compatibility when public state, enum values, constructors, exported names, or framework packaging changes.
- Verify Android publication, iOS framework/XCFramework export, linker settings, and sample-app consumption.
