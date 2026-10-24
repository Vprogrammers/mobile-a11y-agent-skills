# KMP interop review: MotionKit

I reviewed the fixture text only. I haven't built it or run it on a device. The iOS behavior below is unverified until it's tested on hardware.

**Architecture.** There are two surfaces in one artifact. `commonMain` is the logic library and is published to Swift teams. `MainViewController` is Compose Multiplatform 1.8.1 shared UI on iOS. These need different rules, so I'd split them.

## 1. Recommended public API and ownership

**Findings in the fixture**
- **Wrong reduce-motion signal on Android.** `ANIMATOR_DURATION_SCALE == 0f` is the developer-options animation scale. It is not an accessibility "reduce motion" setting. Users who turn off animations through Remove animations or Reduce Motion in accessibility settings get the same scale of 0, but the check is fragile. Document the exact signal you chose.
- **Non-reactive.** `motionSpec()` reads the setting once and can't observe changes. iOS has `UIAccessibilityReduceMotionStatusDidChangeNotification`. Android has a `ContentObserver`.
- **Global mutable `lateinit var appContext`.** It is public, unset by default, and throws `UninitializedPropertyAccessException` if the consumer forgets to set it. It also leaks a Context.
- **`expect fun isReduceMotionEnabled()` is declared in common, and `public` is not applied to it.** The `public` modifier is applied inconsistently across the fixture, so the API surface is implicit. Turn on explicit API mode.
- **`sectionTitleTraits()` is public and returns `UIAccessibilityTraits`.** That is native UI semantics leaking through a shared module.
- **`MotionSpec` is a public `data class`.** `copy` and `componentN` become binary API.

**Recommended API**
```kotlin
// commonMain
public interface AccessibilityPreferences { public val reduceMotion: StateFlow<Boolean> }
public enum class MotionPolicy { Full, Reduced }
public class MotionSpec private constructor(public val durationMillis: Int) { /* equals/hashCode, no copy */ }
public fun motionSpec(prefs: AccessibilityPreferences): MotionSpec
```
- Shared code owns the policy, which is reduced motion mapped to a duration. It also owns the tests.
- Each app owns platform reads, created and injected per platform:
  - `AndroidAccessibilityPreferences(context)` takes the Context through its constructor.
  - `IosAccessibilityPreferences()` has no arguments.
- Delete `appContext`, and delete the top-level `expect fun isReduceMotionEnabled()`.
- **Remove `sectionTitleTraits()` from the public library.** Heading semantics belong to the UI layer, which is native `.isHeader` or `.accessibilityAddTraits(.isHeader)` on iOS, and Compose `heading()`. If Swift teams need the trait, they set it themselves.
- Mark the platform implementations `internal`, or make them public classes with explicit constructors.

## 2. Android and iOS integration points

**Android**
- Inject the Context from `Application`. For example, `AndroidAccessibilityPreferences(applicationContext)`.
- Decide what "reduce motion" means:
  - Read `ANIMATOR_DURATION_SCALE`, `TRANSITION_ANIMATION_SCALE` and `WINDOW_ANIMATION_SCALE`.
  - On API 34+, check whether newer system settings or `AccessibilityManager` give a better signal.
- Observe changes with a `ContentObserver` exposed as a `StateFlow`.
- In Compose, collect the flow with `collectAsState` and gate animations on it.

**iOS, native UI path (SwiftUI/UIKit consumers)**
- `IosAccessibilityPreferences` wraps `UIAccessibility.isReduceMotionEnabled` plus the status-change notification, and retains the observer token.
- Swift consumers can also read `@Environment(\.accessibilityReduceMotion)` themselves.

**iOS, Compose Multiplatform path (`MainViewController`)**
- **`AccessibilitySyncOptions` was removed in CMP 1.8.0.** `accessibilitySyncOptions = AccessibilitySyncOptions.Always(...)` should not compile against 1.8.1. If it does, the fixture's version note or dependency is wrong. Delete the configuration. The tree now syncs lazily.
- Compose semantics are the iOS accessibility surface. Custom components need explicit `role`, `contentDescription`, `stateDescription` and `heading()`.
- Pass an injected `AccessibilityPreferences` into `App`. Don't call `motionSpec()` once at construction, because that value stays stale.
- Verify any iOS-only features on the Compose screen: rotors, Voice Control labels, modal containment, Large Content Viewer.
- `MainViewController()` is a top-level function with no `public` or visibility modifier, and it exports a `UIViewController`. That is fine for a Compose host, but decide whether it belongs in the same published framework as the logic library. I'd put it in a separate artifact.

## 3. Swift export, binary compatibility, and dependency risks

- **The header check passing is a false assurance.** `UIAccessibilityTraits` is a typealias and exports as `uint64_t`, so `sectionTitleTraits()` evades the check for UIKit type names. Grep the `commonMain` and `iosMain` sources for `platform.UIKit` imports in public signatures as well. Strip KDoc from the header before the text check.
- **Top-level functions in `MotionSpec.ios.kt`** export under an Objective-C file-facade class name (`MotionSpec_iosKt`). Treat that name as public API. Set `@file:ObjCName` or move the functions into explicit objects or classes.
- **`MotionSpec` data class:**
  - It exports a `copy`, `component1` and similar members.
  - Adding a field later is a breaking change in the JVM ABI and in the Objective-C header.
  - Prefer a final class with a private constructor. Run `binary-compatibility-validator` for the klib/JVM API dump.
- **Direct Objective-C export** is the baseline. It must work without optional tooling.
- **Swift export** is Alpha:
  - It needs direct Xcode integration.
  - It erases generics.
  - It ignores types inheriting `List`/`Set`/`Map`.
  - It supports only final classes inheriting directly from `Any`.
  - It turns `StateFlow` into `AsyncSequence`.
  - Don't make the contract depend on it. If you support it, test the Objective-C and Swift export paths separately.
- **SKIE** is optional. It improves `Flow` and enum ergonomics for Swift teams but adds a build dependency. Document which path consumers should use.
- **Dependency boundaries:**
  - `android.content.Context` and `Settings` stay in `androidMain`.
  - Keep Compose Multiplatform (UI) out of the core logic artifact, so that logic-only Swift consumers don't pull in the Compose runtime and Skiko. Split `motionkit-core` from `motionkit-compose-ui`.
  - Check the Kotlin, CMP and Xcode toolchain versions published with the XCFramework.
- **Removing public symbols** such as `appContext`, `isReduceMotionEnabled` and `sectionTitleTraits` is a source- and binary-breaking change. Plan a deprecation cycle and a major version, or mark them `@Deprecated(level = ERROR)` first. Since the library is already published, I'd deprecate rather than delete in the first release.

## 4. Tests

**Automated**
- Common tests with a `FakeAccessibilityPreferences`:
  - Reduced mode gives 0 ms, and full mode gives 300 ms.
  - Flow transitions update `motionSpec`.
- Android:
  - A Robolectric or instrumented test for `AndroidAccessibilityPreferences`, covering scale 0, scale 1 and observer updates.
  - A test that an uninitialized setup can't crash. Constructor injection removes this case.
  - Compose semantics tests that animation is skipped under reduced motion.
- iOS simulator tests:
  - The preference wrapper reads reduce motion.
  - The notification updates the flow.
  - The observer is released on deinit.
- Header and API checks:
  - A header check on comment-stripped text.
  - A source scan for `platform.UIKit`, `androidx.compose` and `android.*` in public signatures.
  - `apiCheck` against the API dump.
- A compile check against CMP 1.8.1, which catches the `AccessibilitySyncOptions` removal.
- A sample Swift consumer, built against both the Objective-C path and the Swift export or SKIE path, if supported.
- XCUITest with `performAccessibilityAudit()` on the Compose screen. `testTag` maps to `accessibilityIdentifier`.

**Real devices**
- TalkBack on Android: toggle Remove animations and the animation scale mid-session, and check the UI responds.
- VoiceOver on iOS:
  - Check the CMP screen's reading order, headings, roles, focus and custom components.
  - Check the Swift consumer's header.
- Toggle Settings > Accessibility > Motion > Reduce Motion while the app is running, and confirm the animation changes live.
- Also try Switch Control and Voice Control on the CMP screen, since CMP gaps are undocumented.

## 5. Unresolved product or platform decisions

1. What does "reduce motion" mean on Android? Is the animator scale (the developer-level setting) acceptable, or do you want a documented broader rule? What about API levels below the newer settings?
2. Should the library ship Compose UI at all, or only the policy? If both, are they separate artifacts?
3. Which CMP version is the real target? The fixture says 1.8.1 but uses an API that 1.8.0 removed.
4. Is a breaking change allowed now? If not, what is the deprecation timeline for `appContext`, `isReduceMotionEnabled` and `sectionTitleTraits`?
5. Which interop paths will you support: Objective-C only, SKIE, or Swift export? Who documents consumer setup?
6. Should the reduced-motion duration be 0 ms, or should it substitute a non-motion alternative (such as a fade or an instant state change)? This is a product and WCAG 2.3.3 question, not only a duration.
7. How do you handle Increase Contrast and font scaling in the CMP screen, which has no built-in high-contrast variant?
8. Who owns localization of accessibility strings: the library, or the host apps through a provider interface?
9. Which CMP iOS accessibility gaps are acceptable, and which require native SwiftUI/UIKit hosting?
