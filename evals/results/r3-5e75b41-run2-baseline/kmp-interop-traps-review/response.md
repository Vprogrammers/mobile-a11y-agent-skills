I reviewed the excerpt inline in your message and did not edit anything or open the file on disk. I haven't built this, so the Compose and Kotlin API claims need confirming against your pinned versions.

## 1. API ownership

| Item | Problem | Recommendation |
|---|---|---|
| `expect fun isReduceMotionEnabled()` | It has no modifier, so it is public API in a published library. | Make it `internal`, or put it behind a `MotionPreferences` interface. |
| `lateinit var appContext` (androidMain) | It is a public, global, mutable var. Nothing says who sets it or when. If `motionSpec()` runs first, it throws `UninitializedPropertyAccessException`. If someone assigns an Activity, it leaks. | Remove it. Use an `androidx.startup` Initializer that stores `applicationContext` privately, or take a `Context` in an Android-only entry point. |
| `public data class MotionSpec` | `copy`, `componentN` and the constructor signature become permanent ABI, so adding a field breaks binary compatibility. | Use a final class with explicit `equals`/`hashCode`/`toString`, a private constructor and a factory, or an `@ConsistentCopyVisibility` data class. |
| `durationMillis: Int` | The unit is baked into the name and type. | Decide whether to expose `Duration` or keep `Int`. |
| `fun MainViewController()` | It has no visibility modifier and no explicit return type. The inferred type is `UIViewController`, so a UIKit type sits in the public API. | Add explicit `public` and an explicit return type, and turn on explicit API mode. |
| `sectionTitleTraits()` | It re-exports a UIKit constant. `UIAccessibilityTraits` is a `ULong` typealias, so it reaches Swift as a bare `uint64_t`. Swift already has `.header`. | Delete it. If it stays, document it. |

## 2. Android and iOS integration points

- **Android signal:** `ANIMATOR_DURATION_SCALE == 0f` is a developer-options/"Remove animations" proxy. It ignores transition and window scales. A user who turns animations off in developer options is reported as "reduce motion".
- **iOS signal:** `UIAccessibilityIsReduceMotionEnabled()` is the real system preference. The two platforms therefore mean different things.
- **No change observation on either platform:** `motionSpec()` is a one-shot read.
  - On Android you would need a `ContentObserver`.
  - On iOS you would need `UIAccessibilityReduceMotionStatusDidChangeNotification`.
  - Without them, the UI stays stale after the user toggles the setting.
  - The fix is to expose a `State`/`Flow`, or read it inside a composition-aware holder.
- **Semantics:** Reduce Motion usually means swapping large motion for a crossfade, not setting the duration to 0. Decide what `MotionSpec` should express.
- **Threading:** Document or verify that the iOS call is safe off the main thread.
- **`accessibilitySyncOptions = Always(...)`:**
  - It is hard-coded in a library entry point. It forces the full accessibility tree sync on every host app, with a performance cost, instead of syncing only when needed.
  - Check whether the API requires an experimental opt-in in 1.8.1.
  - Expose it as a parameter, defaulting to the Compose default.
- **`App(motion = motionSpec())`:** `App` isn't shown, so I can't see whether it reads the spec reactively.
- **Other targets:** Confirm that any other target (desktop, wasm/js) has an `actual`. Otherwise the build breaks.

## 3. Swift export

- **The CI check contradicts the code.**
  - The public `MainViewController()` returns `UIViewController`.
  - The Obj-C header would normally contain `UIViewController`, for example in `@class UIViewController`.
  - "CI passes" therefore means one of three things:
    - The check is a weak grep.
    - It runs against a different artifact.
    - The function isn't exported.
  - Treat the check as unverified until you inspect the real header.
- **The check gives false comfort in two ways.**
  - `UIAccessibilityTraits` collapses to `uint64_t`, so the header never names it. The API is still a UIKit leak.
  - The check says nothing about Swift export, which is a different pipeline.
- **Naming:**
  - The Obj-C names depend on file names, such as `MotionSpecKt`, `MotionSpec_iosKt` and `MainViewControllerKt`.
  - Renaming a file changes the name Swift sees.
  - Pin names with `@ObjCName` or `@file:JvmName`/`@ShouldRefineInSwift` as appropriate.
  - Use `@HiddenFromObjC` for anything that should not be visible.
- **Swift export differs from the Obj-C header.** Packages become namespaces, and a data class, `Int`, top-level functions and default arguments map differently. The module name `MotionKit` and the `example.motion` package may produce `MotionKit.example.motion...`. Verify this explicitly.
- **Static Kotlin runtime:** If the Swift team also links another Kotlin framework, the Kotlin runtime is duplicated. Plan an umbrella framework or a documented limitation.

## 4. Binary compatibility

- Add binary-compatibility-validator (or the Kotlin Gradle plugin's klib ABI validation) with `apiDump` committed. That covers both the JVM/Android surface and the klib surface.
- Turn on `explicitApi()`.
- Pin the Android JVM class names (`MotionSpecKt`, `MotionSpec_androidKt`) with `@file:JvmName`.
- Removing `appContext` is a breaking change if any version has shipped it. Deprecate it with `ERROR`, or document the break.
- Adding a property to the data class `MotionSpec` is a breaking change, as noted above.

## 5. Dependency risks

- **Compose Multiplatform 1.8.1 is pinned in the iOS source set.**
  - It ties consumers to a matching Kotlin and Compose compiler version.
  - Klib compatibility is strict between Kotlin versions.
  - The Compose runtime is bundled in the framework, which grows binary size and conflicts with a host app's own Compose.
  - Check that 1.8.1 is still the right pin today (October 2026).
- **`platform.UIKit.*` in public signatures** couples the klib to Apple SDK and Kotlin cinterop versions.
- **`android.provider.Settings`** needs an explicit `compileSdk`/`minSdk` statement.

## 6. Required tests

1. **Header and Swift export snapshot:**
   - Diff the generated `.h` and the Swift export module interface against a committed golden file.
   - Assert that no `UIViewController`, `UIAccessibility` or `uint64_t` traits appear unless intended.
2. **Swift consumer smoke test:** Build a small SwiftPM or Xcode app that imports `MotionKit`, calls the entry point and embeds the view controller.
3. **ABI dump check:** Run `apiCheck` for the JVM and klib surfaces in CI.
4. **Android unit tests (Robolectric):**
   - Scale `0f`, `1f` and the missing-setting case.
   - Calling before initialization.
   - The Application-context initializer.
   - A ContentObserver update, once added.
5. **iOS simulator test:**
   - Inject a fake preference provider to test `motionSpec()` for both values.
   - Test notification-driven updates.
   - Run the real API once on the simulator for each of the three iOS targets.
6. **Compose UI and accessibility tests:** Compare accessibility sync `Always` against the default (VoiceOver, XCUITest accessibility audit, a memory or performance benchmark).
7. **Behavior test:** Changing the setting while the UI is visible updates the animation.

## 7. Unresolved decisions

- Is `isReduceMotionEnabled` public API or internal? (I recommend internal.)
- How does Android obtain a `Context`: Startup initializer or explicit parameter?
- Is the signal a snapshot or an observable? What does "reduce motion" mean (zero duration or crossfade)?
- Is `MotionSpec` a data class? Should it hold `Duration`?
- Do you support Obj-C export, Swift export, or both? Which names are frozen?
- Should `sectionTitleTraits()` exist?
- Should the library hard-code `AccessibilitySyncOptions.Always`, or expose it?
- Is Compose Multiplatform part of the published contract, or an implementation detail? That determines whether it can move to a separate artifact.
- What is the CI header check actually scanning, and why does it pass? Run it against the real output before trusting it.
