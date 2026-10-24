I applied the `kmp-a11y` skill and its `kmp-boundaries.md` reference directly. I didn't launch the `kmp-a11y-architect` subagent because I have no tool for it in this session. I didn't edit the fixture. Nothing was built or run, so every iOS Compose behavior below is unverified.

## 1. Recommended public API and ownership

**Architecture:** this is a hybrid. Shared logic is consumed by Compose Multiplatform shared UI on iOS (`ComposeUIViewController`), and the framework is also published to external Swift teams. The Compose-semantics rules apply to the shared screen. The native-boundary rules apply to the published framework surface.

**Problems in the fixture:**
- **`expect fun isReduceMotionEnabled()` is a public `expect` that reads global state.**
  - It cannot be faked in common tests.
  - It is a one-shot read, so it misses changes made while the app runs.
  - It is visibly public API on the common surface, which makes it hard to change later.
- **`lateinit var appContext` is a public mutable global.**
  - It crashes with `UninitializedPropertyAccessException` if the host forgets to set it.
  - It leaks a `Context`.
  - It makes initialization order part of the library contract.
- **`sectionTitleTraits(): UIAccessibilityTraits` is a public iOS function that exports a UIKit typealias.**
  - The Kotlin typealias exports to Swift as `uint64_t`, so the header check cannot see it.
  - It hands consumers a raw trait bitmask that they should set natively.
- **`motionSpec()` hard-codes 0 ms versus 300 ms.**
  - Product meaning (a "reduced" policy) is mixed with a platform read.
  - Reduce Motion on iOS does not mean "no animation". It usually means a cross-fade or a simpler transition.
- **The Android check is wrong.**
  - `ANIMATOR_DURATION_SCALE == 0` is a developer-option animation setting, not an accessibility "remove animations" preference.
  - Reading it from `Settings.Global` does not observe changes.

**Recommended shape:**
```kotlin
// commonMain
public interface AccessibilityPreferences {
    public val reduceMotion: Boolean              // primitive, Swift-friendly
    public fun observeReduceMotion(onChange: (Boolean) -> Unit): Cancellable
}
public enum class MotionPolicy { Standard, Reduced }
public fun motionSpec(prefs: AccessibilityPreferences): MotionSpec
```
- **Constructor injection:** the apps create `AndroidAccessibilityPreferences(context)` and `IosAccessibilityPreferences()` and pass them into shared code. A `StateFlow<Boolean>` is fine for Kotlin and Compose consumers. Offer a callback-based adapter for Swift, because `Flow` is an interop decision.
- **`MotionSpec`:** make it a final class, or a data class with `@ConsistentCopyVisibility` and an explicit API decision (see section 3). Prefer a `MotionPolicy` enum plus duration values the app can tune.
- **Compose usage:** the Compose UI reads the preference through a `CompositionLocal` or a `remember`ed observable, not a one-time call during composition.
- **Remove `sectionTitleTraits` from the public API.**
  - In Compose, headings are `Modifier.semantics { heading() }`.
  - Native Swift teams apply `.isHeader` themselves.
- **Ownership:**
  - Shared: motion policy semantics and durations, plus the `AccessibilityPreferences` contract.
  - Android: the settings read and its observer.
  - iOS: the `UIAccessibilityIsReduceMotionEnabled` read and its notification.
  - App: instantiation and lifecycle.
- Use `explicitApi()` so every public declaration is deliberate. `expect fun isReduceMotionEnabled()` and `actual` are currently implicitly public.

## 2. Android and iOS integration points

**Android:**
- Create `AndroidAccessibilityPreferences(context)` in the app's `Application` or DI graph. Use the application context only.
- **Which setting to read:**
  - Use `Settings.Global.ANIMATOR_DURATION_SCALE` for "animations disabled in developer options" if that's what you want.
  - **Decision needed:** whether to also honor the user-facing "Remove animations" setting. It is device-dependent and currently surfaces through `TRANSITION_ANIMATION_SCALE` and `ANIMATOR_DURATION_SCALE` on supported builds. Verify on the target API levels.
- Observe changes with a `ContentObserver` registered on the same settings URIs, and unregister it on cancel.

**iOS:**
- Read `UIAccessibilityIsReduceMotionEnabled()` and observe `UIAccessibilityReduceMotionStatusDidChangeNotification` in `IosAccessibilityPreferences`. Remove the observer on cancel.
- **`AccessibilitySyncOptions.Always(...)` is wrong for the version the fixture states.**
  - The reference notes that Compose Multiplatform 1.8.0 removed this setting, because the tree now syncs lazily.
  - The fixture claims 1.8.1, so this call likely does not compile, or the version label is wrong. Remove it, or confirm the actual version.
  - Also note that `AccessibilitySyncOptions` is an iOS-specific tree-synchronization setting from before 1.8.0. If it was kept for performance or testing reasons, record why.
- Verify on the Compose screen: headings, roles, `stateDescription`, traversal order, focus, and `testTag` to `accessibilityIdentifier`. Host iOS-only capabilities (rotors, Voice Control input labels, Large Content Viewer, modals) in native views if they fail.
- **Hybrid interop trap:** `MainViewController()` has no `public` modifier and no `@ObjCName`, so consumers get a default generated name. Treat that name as API.

## 3. Swift export, binary compatibility, and dependency risks

**Swift export and Objective-C header:**
- **The header check passing is false assurance.** The check can't see `UIAccessibilityTraits`, because it exports as `uint64_t`. Review source for `platform.UIKit` imports in public signatures, as well as the generated header.
- **`isReduceMotionEnabled()` and `appContext` also land on the Swift surface.** They appear as top-level functions and properties on a file facade class (`MotionSpec_androidKt` and similar). These names are ugly, and changing them later is a source break. Use `@file:ObjCName` or move the declarations into named objects and classes.
- **Swift export is Alpha.**
  - It requires direct Xcode integration.
  - It erases generics.
  - It ignores `List`/`Set`/`Map`-inheriting types.
  - It supports only final classes inheriting directly from `Any`.
  - Don't make the external contract depend on it. Keep the Objective-C framework as the supported baseline, and test Swift export as an opt-in path if offered.
- **SKIE:** keep it optional. If the contract uses `Flow`, `suspend`, or sealed types, decide whether consumers must configure SKIE. Test both paths if both are supported.

**Binary compatibility:**
- Public `data class MotionSpec(val durationMillis: Int)` generates `copy`, `componentN`, and a constructor. Adding a field breaks binary compatibility. Prefer a final class or a builder, or use `@ConsistentCopyVisibility` with a private constructor.
- Removing `isReduceMotionEnabled`, `appContext`, and `sectionTitleTraits` from the public API is a break if already published. Follow a deprecation cycle (`@Deprecated` with `ReplaceWith`) and track it with `binary-compatibility-validator`, or the Kotlin Gradle plugin's ABI validation. Run it for both JVM/Android and klib targets.
- Treat the framework name `MotionKit`, exported names, and XCFramework packaging as API. Changes need a major or minor version bump and a changelog entry.

**Dependency risks:**
- The core artifact should not depend on Compose UI if non-Compose consumers exist. `MainViewController.kt` depends on Compose Multiplatform and ships in the same iOS framework. That pulls the Compose runtime into every Swift consumer's binary, with its size and linker settings. Split into `motionkit-core` (logic only) and `motionkit-compose-ios` (UI).
- Verify the Compose Multiplatform and Kotlin version alignment across the published artifact and the consumers.
- Android `Settings`/`Context` use stays in `androidMain`. Check that the library doesn't pull in AndroidX or Play Services unnecessarily.

## 4. Automated and real-device tests

**Automated:**
- **Common tests:** `motionSpec(fakePrefs)` for reduced and standard, using a fake `AccessibilityPreferences`. This is only possible after the interface refactor.
- **Android:**
  - A Robolectric or instrumented test of `AndroidAccessibilityPreferences` for the initial read and for change notification via a `ContentObserver`.
  - A test that observers are unregistered.
  - Compose semantics tests (`onNodeWithTag`, `assertIsHeading` or an equivalent semantics-property assertion) for the shared UI.
- **iOS simulator tests:** `IosAccessibilityPreferences` returns a value and observes the notification. Toggling Reduce Motion in the simulator can be driven by `simctl`-based or UI-setting automation, so mark which cases need a device.
- **Header and ABI checks:**
  - Strip comments before scanning the generated header.
  - Also fail the build on `platform.UIKit`/`platform.*` imports and on Compose types in public signatures in the library module.
  - Run the ABI validator for both JVM and klib.
  - Add a check that `MainViewController`'s exported name is stable.
- **XCUITest with `performAccessibilityAudit()`** against the Compose screen, using `testTag` identifiers.
- **A real Swift consumer sample** that links the published XCFramework through the Objective-C path. Add one for SKIE and for Swift export if either is supported.

**Real-device:**
- **iOS:** VoiceOver on the Compose screen (headings, order, focus, state announcements). Reduce Motion toggled live, with the animation visibly changing without a restart. Dynamic Type and Increase Contrast, if those apply to the screen.
- **Android:** TalkBack on the same screen. The animation setting toggled live. Check at least one older API level and a device from a different OEM, because the settings behave differently across vendors.

## 5. Unresolved product or platform decisions

1. **What does reduced motion mean for the product?** Zero duration, cross-fade, or a static state? The fixture hard-codes `0` ms on both platforms. The right behavior may differ per platform and per component, and may differ from "disabled".
2. **Which Android signal counts?** The developer option `ANIMATOR_DURATION_SCALE`, a user-facing "Remove animations" setting, or both. The answer depends on the minimum API level and OEM behavior.
3. **Compose Multiplatform version.** Is it actually 1.8.1? If so, remove `AccessibilitySyncOptions`. If an older version, document why `Always` is needed and what regression it covers.
4. **Library split.** Is `MotionKit` a logic-only library for native UIs, or a shared-UI library? That determines whether Compose belongs in the Swift-facing framework.
5. **Swift-consumer contract.** Which interop paths are supported (Objective-C only, SKIE, Swift export), and who configures them?
6. **Migration policy.** Is the current API already published? If so, deprecate and keep `isReduceMotionEnabled` and `appContext` for a release, or accept a major version break.
7. **Observation API shape.** `StateFlow`, a callback, or both, and who owns the lifecycle and cancellation.
8. **iOS-only capabilities on the Compose screen.** Which are needed (rotors, Voice Control labels, Large Content Viewer, modals), and whether any must move to native interop views. These stay unverified until tested on a device.
