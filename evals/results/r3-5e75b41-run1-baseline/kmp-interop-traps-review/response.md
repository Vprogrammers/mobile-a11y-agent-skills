# MotionKit review (`MotionKit.kt`, read from the inline excerpt)

The fixture was not edited. I judged it as written and did not build it. Points that depend on a toolchain version are marked **verify**.

## 1. API ownership

| Symbol | Current state | Problem and recommendation |
|---|---|---|
| `expect fun isReduceMotionEnabled()` | Public by default, no `public` modifier | It's an implementation seam that becomes permanent API. Make it `internal expect`, or expose a deliberate `MotionPreferences` API. |
| `MotionSpec` (data class) | Public, one `Int` field | A data class publishes `copy`, `componentN`, `equals` and the constructor signature. Adding a field later breaks binary compatibility. Use a plain class with a private constructor and a factory, or apply `@ConsistentCopyVisibility`. Nothing validates negative durations. |
| `motionSpec()` | Non-reactive, reads platform state once | The policy "reduce motion means 0 ms" lives in common code. The result can't say *why* the duration is 0, so consumers can't swap motion for a cross-fade. Decide whether the library or the app owns that policy. |
| `appContext` | Public mutable top-level `lateinit var` | This is a global setter exposed in the public ABI. If nothing sets it, `motionSpec()` throws `UninitializedPropertyAccessException`. A caller can also store an Activity there and leak it. Make it `internal` and initialize it through an `androidx.startup` initializer, or take an explicit `Context` and call `applicationContext`. |
| `sectionTitleTraits()` | Public, returns a UIKit constant | It only wraps `UIAccessibilityTraitHeader`. Swift callers can use `UIAccessibilityTraits.header` directly. Remove it, or make it internal and use it only in Compose semantics. |
| `MainViewController()` | No visibility modifier, so public | This is the real iOS entry point and it exposes `UIViewController`. Own it deliberately and name it explicitly. `App` isn't shown, so its visibility and its use of `MotionSpec` are unknown. |

If explicit API mode were on, most of these would fail to compile. Turn it on.

## 2. Android integration

- **Wrong signal, possibly.** `ANIMATOR_DURATION_SCALE == 0f` is the "animations off" setting. It also appears in Developer options, and Android 12+ "Remove animations" may set it. Android has no dedicated reduce-motion API, so document the semantics. **Verify** on API 26 through the current release. `TRANSITION_ANIMATION_SCALE` and `WINDOW_ANIMATION_SCALE` aren't checked.
- **Snapshot only.** Nothing observes the setting, for example with a `ContentObserver` on `Settings.Global`. Toggling it while the app runs has no effect until `motionSpec()` is called again.
- **Context lifecycle.** The initialization contract is undefined (see §1). Compose Multiplatform can use `LocalContext` instead of a global.
- **Naming.** The file facade is `MotionSpec_androidKt`. Renaming the file breaks the ABI, so pin it with `@file:JvmName`.

## 3. iOS integration

- **Snapshot only.** `UIAccessibilityIsReduceMotionEnabled()` is read once, when `MainViewController()` builds `App(motion = motionSpec())`. The value is then frozen. Observe `UIAccessibilityReduceMotionStatusDidChangeNotification` (`reduceMotionStatusDidChangeNotification`) and expose it as state, such as a `Flow` or Compose `State`.
- **Threading.** UIKit accessibility calls belong on the main thread. State this in the contract.
- **`AccessibilitySyncOptions.Always(...)`.** As I recall, `Always` is meant for testing and debugging. It forces the accessibility tree to sync even with no assistive technology running, which costs performance, and the type is probably experimental. The excerpt has no `@OptIn(ExperimentalComposeUiApi::class)`. **Verify** against CMP 1.8.1 whether it should be `WhenRequiredByAccessibilityServices` in production.
- **Shipped debug option.** `debugLogger = null` in a published library suggests a leftover debug setting.

## 4. Swift export and ObjC header

- **The CI check is not trustworthy.**
  - `UIAccessibilityTraits` is a typealias for `ULong`, so the header shows `uint64_t`. That's why the check passes while the Kotlin signature still carries a UIKit semantic.
  - `MainViewController()` returns `UIViewController`. I'd expect the header to contain at least `@class UIViewController`. If the check still passes, it probably greps for the wrong pattern, or the function isn't exported. **Verify** by reading the generated header.
- **Swift consumers get an unhelpful shape.** `sectionTitleTraits` appears as `UInt64`. The top-level functions land under `MainViewControllerKt` and `MotionSpecKt` in ObjC, or in package-based namespaces in Swift export.
- **Swift export is experimental and version-dependent.** **Verify** which Kotlin version you use, which of these constructs it handles, and what it does with the data class.
- **Decide which bridge you support.** If both ObjC and Swift export ship, test both. Swift teams would also see name changes on migration, which is another compatibility break.
- **Framework linking.** Compose and Skiko are linked into the `MotionKit` framework. External teams that embed a second Kotlin framework will have duplicate runtimes. Document whether it's static or dynamic.

## 5. Binary compatibility

- **JVM and Android.**
  - `MotionSpec` data-class members, file-facade class names, and the `getAppContext`/`setAppContext` accessors are all public ABI.
  - Run `binary-compatibility-validator` (`apiCheck`).
  - Make all additions append-only, using a builder or `@JvmOverloads`-style constructors.
- **klib and iOS.**
  - Use Kotlin Gradle plugin klib ABI validation.
  - Moving `appContext`, adding or renaming `expect` declarations, and changing `MotionSpec` all change the klib signature.
  - `actual fun` signatures must match the `expect` exactly.
- **Missing targets.** If the project declares any other target, such as jvm, desktop, or wasm, it has no `actual` and the build fails. The excerpt shows only Android and iOS.

## 6. Dependency risks

- **Compose Multiplatform 1.8.1** is pinned. Today is 2026-10-24, so check that it is still the version you want. Compose needs a matching Kotlin version, and consumers inherit the Compose runtime, Skiko, and a larger binary.
- **Android.** `Context` and `Settings` have no API-level guard. `minSdk` and the Compose runtime must stay aligned with the consuming apps.
- **iOS.** `platform.UIKit` binds to the Xcode SDK used at build time. Header and cinterop differences between Xcode versions are a risk.
- **Publishing.** Confirm that all three iOS targets are published (`iosArm64`, `iosSimulatorArm64`, `iosX64`) and that external teams have a supported minimum Xcode version.

## 7. Required tests

1. **Android:** reduce-motion on gives `0`, off gives `300`. Cover an uninitialized context and an Application context, and test that a change at runtime updates the result.
2. **iOS:** unit tests with an injectable provider. Device or simulator UI test that toggles Reduce Motion and checks the Compose UI updates.
3. **Common:** `MotionSpec` equality and validation, including a negative duration, and `motionSpec()` with a fake provider.
4. **ABI:** `apiCheck` and klib ABI dump checked in, and failing on `MotionSpec` signature changes.
5. **Header and Swift export:**
   - Generate the ObjC header and the Swift export module.
   - Compile a small Swift consumer that calls `MainViewController()` and the other public symbols.
   - Make the CI check assert on symbols and types, not on the string "UIKit".
6. **Accessibility:** VoiceOver and TalkBack smoke tests with the chosen `AccessibilitySyncOptions`, plus a performance check showing that `Always` costs frames with no assistive technology running.
7. **Packaging:** consume the published artifact from a clean Android app and a clean Xcode project.

## 8. Unresolved decisions

1. Which symbols are public API, and is explicit API mode enabled?
2. Does the library or the app own the reduce-motion policy, and is the value reactive?
3. Is the Android semantic "animations off", or something else, and how is it documented?
4. How does Android get its `Context`: a startup initializer or an explicit parameter?
5. Do you ship ObjC export, Swift export, or both, and which Kotlin version is the baseline?
6. Does `MainViewController` belong in the library or in the app, and what should its Swift name be?
7. Should `AccessibilitySyncOptions.Always` ship at all, and is the experimental opt-in intentional?
8. Do you keep `MotionSpec` as a data class, or replace it with a ABI-stable shape?
9. How should the CI header check change so it can fail on the cases in §4?
10. Which Compose Multiplatform version, Kotlin version, and minimum Xcode and Android versions do you guarantee?
