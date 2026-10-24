I invoked `kmp-a11y` and read its boundaries reference. I couldn't launch the `kmp-a11y-architect` subagent because this session has no tool for that, so this review is my own. It is based on the fixture text and the reference, and I haven't compiled or run anything. I didn't edit any files.

## 1. Recommended public API and ownership

**Findings**

- **Motion preference is hidden.** `isReduceMotionEnabled()` is a public top-level `expect` function. The app can't inject or fake it, and common tests can't control it.
- **The Android check is wrong.** `ANIMATOR_DURATION_SCALE == 0f` is the developer-option animation scale. It is not a user reduce-motion preference. Many TalkBack users never change it, and some people set it to 0 for unrelated reasons. Android has no single equivalent of iOS Reduce Motion, so the product has to decide what "reduce motion" means there (see section 5).
- **`appContext` is an unsafe global.** `lateinit var appContext: Context` is public and mutable. It crashes if the app hasn't set it, and it leaks the `Context`.
- **The policy is frozen into one value.** `motionSpec()` reads the setting once and returns a bare duration. The value can't react to a setting change while the app runs.
- **A platform type is public.** `sectionTitleTraits(): UIAccessibilityTraits` exposes a UIKit type from a published library. It is also native-UI concern (heading trait) living in shared iOS code.

**Recommended shape**

```kotlin
// commonMain
public interface AccessibilityPreferences {
    public val reduceMotion: StateFlow<Boolean>   // see Swift export risks below
}
public enum class MotionPolicy { Full, Reduced }
public class MotionSpec(public val durationMillis: Int)   // see binary compatibility below
public fun motionSpec(prefs: AccessibilityPreferences): MotionSpec
```

- **Ownership.** The shared library owns the meaning: the policy, the duration mapping, and the `AccessibilityPreferences` interface. Each app owns creating and injecting the platform implementation.
- **Implementations.** `AndroidAccessibilityPreferences(context)` and `IosAccessibilityPreferences()` are constructor-injected. The iOS one observes `UIAccessibilityReduceMotionStatusDidChangeNotification`.
- **Remove or demote the `expect` function.** Only keep `expect`/`actual` if a platform factory is truly intrinsic.
- **Delete `appContext`.**
- **Remove `sectionTitleTraits()` from the shared module.** The heading trait belongs in native Swift or UIKit code. In Compose it is `heading()` semantics.
- **Localization.** None is shown. If text is added later, share keys and arguments and keep the strings with the platform that owns the UI.

## 2. Android and iOS integration points

**Android**
- Inject the `Context` through the constructor.
- Pick a source for the preference and document it. Candidates are `ANIMATOR_DURATION_SCALE`, a Compose or app-level setting, or a combination.
- Observe changes with a `ContentObserver` so the `StateFlow` updates.
- Compose UI reads the injected preference as state.

**iOS**
- `UIAccessibilityIsReduceMotionEnabled()` is the correct system signal, but it is a one-time read in the fixture. Add the change notification.
- Compose Multiplatform shared UI is in use (`ComposeUIViewController`), so Compose semantics are the iOS accessibility surface.
- `AccessibilitySyncOptions.Always(debugLogger = null)` is stale. Compose Multiplatform 1.8.0 removed `AccessibilitySyncOptions`, and the tree now syncs lazily. Per the reference, remove the `configure` block. As written it probably won't compile against 1.8.1, or it signals a mismatched dependency version. Check this against the project's actual build.
- `MainViewController()` is public with no explicit visibility or return type, which is a public-API-hygiene issue. Decide whether it is the intended Swift entry point.
- `App(motion = motionSpec())` bakes the preference in once at creation. Pass the injected preferences or a state holder instead.
- Anything iOS-only that a screen relies on needs checking on the Compose screen. That includes rotors, Voice Control input labels, modal containment, and announcements. If it doesn't work there, host that part in a native view.

## 3. Swift export, binary compatibility, and dependency risks

**The header check is a false assurance.**
- `UIAccessibilityTraits` is a typealias, and it exports as `uint64_t`. So `sectionTitleTraits()` leaks a platform concept, and the "no UIKit in header" CI check passes anyway.
- Add a source-level check for platform imports in common and exported iOS source.
- Strip comments before the header check, because KDoc is copied into the header.

**Swift export (Alpha)**
- It requires direct Xcode integration, erases generics, and supports only final classes inheriting directly from `Any`.
- `StateFlow` becomes an `AsyncSequence`, and `expect`/top-level functions have naming consequences.
- The framework "MotionKit" goes to external Swift teams, so the Objective-C framework must stay the baseline.
- Don't make the contract depend on Swift export or SKIE. If either is offered, treat it as optional and test both paths.
- Top-level functions in Kotlin/Native export land on a generated `…Kt` class. Treat the names as public API and consider `@ObjCName`.

**Binary compatibility**
- `public data class MotionSpec(val durationMillis: Int)` publishes `copy`, `componentN`, and `equals`. Adding a field later breaks the ABI. Prefer a regular class or enum, or accept and document the constraint.
- Run the Binary Compatibility Validator (`apiCheck`) and dump the iOS klib API.
- Removing `appContext`, `sectionTitleTraits`, and the `expect` function is itself a breaking change for existing consumers. Plan deprecation or a major version.
- Adding an `expect` function and `actual` implementations changes the klib API per target.

**Dependency risks**
- Public `lateinit var` plus an `android.content.Context` in the shared artifact ties the core to Android.
- The iOS source set pulls in `platform.UIKit`. That is fine in `iosMain`, but not as exported API.
- The Compose Multiplatform version (1.8.1) must match the API used. A mismatched or removed API will fail at build time.
- Keep Compose Multiplatform itself out of the core artifact if native-UI consumers exist. They would otherwise inherit the Compose dependency.

## 4. Automated and real-device tests

**Automated**
- Common tests for `motionSpec(prefs)` using a fake `AccessibilityPreferences`. Cover both values and a change from one to the other.
- An Android host or Robolectric test for the Android implementation and its `ContentObserver` update.
- iOS simulator tests for the notification-driven update.
- A Compose semantics test of the screen.
- An exported-header check with comments stripped, plus a source-import check.
- API dump checks (`apiCheck` and the iOS klib dump).
- A real Swift consumer sample that builds against the published XCFramework, with and without SKIE or Swift export if supported.
- XCUITest with `performAccessibilityAudit()` on the Compose screen, using `testTag` to find elements.

**Real device**
- iOS: toggle Reduce Motion in Settings and confirm the running app updates. Run VoiceOver across the Compose screen and check traversal, headings, and roles.
- Android: TalkBack on the screen. Verify whatever setting is chosen as the reduce-motion source on real hardware and OS versions, including the case where the animation scale is 0.
- Also test Dynamic Type and font scale, and Increase Contrast, if the screen uses them.

## 5. Unresolved product or platform decisions

- **Android signal.** What counts as "reduce motion" on Android: animator scale, a custom in-app setting, or `Settings.Global.TRANSITION_ANIMATION_SCALE`? The current signal is probably not what users expect.
- **Native or shared UI.** Is shared Compose UI on iOS the long-term direction? Do external Swift teams get only logic or also the Compose entry point? If they only call logic, the Compose Multiplatform dependency should move out of the published core.
- **Reduced-motion duration.** Should it be zero, or a shorter, non-motion transition? Zero can remove helpful feedback.
- **Live or one-time.** Whether changes apply to a running screen or only on the next launch.
- **Public API.** Whether `MotionSpec` stays a `data class`, and the migration or deprecation path for removing public items.
- **Interop commitment.** Whether Swift export or SKIE is supported or only tolerated, and whether the minimum Kotlin and Xcode versions are documented.
- **Compose Multiplatform version.** The exact version in use, and whether the iOS accessibility gaps (rotors, Voice Control labels, modal behavior) matter for this screen. The reference says to treat them as unverified until tested on a device.
- **Heading trait.** If `sectionTitleTraits` was meant for Swift consumers, decide who owns heading semantics and how the Swift team gets them without a UIKit type crossing the boundary.
