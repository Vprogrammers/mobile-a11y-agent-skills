# KMP interop traps review: `MotionKit.kt`

I reviewed the excerpts only and ran no builds. Claims about CMP 1.8.1 and Swift export are from memory, so verify them against a real build.

## 1. API ownership

| Item | Problem | Recommendation |
|---|---|---|
| `expect fun isReduceMotionEnabled()` | It has no `public` or `internal`, so it is public. A platform probe becomes permanent ABI on every target. | Make it `internal`, or expose it deliberately as a documented API. Turn on explicit API mode so this fails the build. |
| `lateinit var appContext` (Android) | It is a public, mutable, process-global `Context` that the host app must set. If the host forgets, `motionSpec()` throws `UninitializedPropertyAccessException`. If the host passes an `Activity`, it leaks. The library owns the dependency but the host owns the lifecycle. | Make it `internal`. Obtain the context through an `androidx.startup` Initializer, or take an explicit `applicationContext` parameter. Store only `applicationContext`. |
| `data class MotionSpec` | The public `data class` exposes `copy`, `componentN`, and the constructor. Adding a field later breaks binary compatibility. | Use a final class with a private constructor, a factory, and hand-written `equals`/`hashCode`/`toString`. Alternatively, accept the freeze and document it. |
| `motionSpec()` | It policy-bakes `0` or `300` ms. It is a one-shot snapshot of the setting, not an observable value. | Decide whether the library owns motion policy or only reports the preference. Prefer a `State`/`Flow`-based API. |
| `sectionTitleTraits()` (iOS) | It exposes a platform type, `UIAccessibilityTraits`, from a library API. That is an Apple concern, not motion. | Remove it. Swift consumers can use `.isHeader` directly. |
| `MainViewController()` | It has implicit public visibility and an inferred return type (`UIViewController`). It hard-wires `App(...)`, which isn't shown, so ownership of `App` is unclear. | Declare the type explicitly. Decide whether a motion library should ship a UI entry point at all. |
| `accessibilitySyncOptions = Always(...)` | The library forces an app-wide accessibility policy. | The host app should own this setting, not the library. |

## 2. Android integration

- **Wrong signal.** `ANIMATOR_DURATION_SCALE == 0f` only detects "animations fully off". That is the developer option, and the "Remove animations" accessibility toggle sets it too. A scale of 0.5 or 2 is not treated as reduced motion, and the setting can be missing or vary by OEM.
- **No change observation.** A `ContentObserver` or lifecycle-aware listener is needed. Without it, toggling the setting leaves the UI stale.
- **Zero duration.** `durationMillis = 0` may break animations that rely on completion callbacks, or that divide by the duration.
- **File-facade names.** The generated class `MotionSpec_androidKt` carries the public `appContext` accessors. Renaming the file changes the JVM ABI. Pin the name with `@file:JvmName`.
- **Setup and testing.** Check `minSdk` and the Robolectric/instrumentation setup, because `Settings.Global` needs a real or faked `ContentResolver`.

## 3. iOS integration

- `UIAccessibilityIsReduceMotionEnabled()` is read once. The library should observe `UIAccessibilityReduceMotionStatusDidChangeNotification`, and the main-thread contract should be documented.
- Hosting is unclear. `ComposeUIViewController` returns a `UIViewController`, so the Swift host has to embed it and own its lifecycle.
- **`AccessibilitySyncOptions.Always`.** In CMP 1.8.x this API is, as I recall, experimental and needs an opt-in annotation, which the excerpt doesn't show. `Always` also builds the accessibility tree even when no assistive technology is running, which costs performance. The default, "when required by accessibility services", is usually the right choice for a library. `debugLogger = null` is fine.
- The `motionSpec()` call inside the content lambda reads no state, so it will not recompose when the setting changes.

## 4. Swift export and ObjC header

- **The CI check proves little.** `UIAccessibilityTraits` is a typealias for `ULong`. The generated header therefore shows `uint64_t`/`UInt64`, and "no UIKit types mentioned" passes without telling you whether the API is sensible. Swift callers get an untyped bitmask with no `UIAccessibilityTraits` type.
- **Possible contradiction.** `MainViewController()` returns `UIViewController`, which should appear in the header (as `@class UIViewController` or an import). If the check really passes, either it is a naive string grep or it doesn't cover this file. Inspect the actual header.
- **Swift export.** It is still experimental. It has limited support for platform (cinterop) types, so declarations that use UIKit types may be skipped. Don't treat the ObjC header as proof of Swift behavior. Generate the Swift module and read it.
- **Naming.** Top-level functions land in file-named facades such as `MotionSpecKt`/`MainViewControllerKt`, and `Int` becomes `Int32`. Add `@ObjCName`/`@ShouldRefineInSwift` where the names matter, or move the entry points into an `object`.

## 5. Binary compatibility

- Add the Binary Compatibility Validator, including klib validation. Today there is no baseline, so the first release freezes the accidental API.
- Items that would be frozen: the public `expect fun`, `appContext`, the `MotionSpec` data-class members, `sectionTitleTraits`, and the file-facade class names.
- `expect`/`actual` functions are stable. If this later becomes an `expect class`, that is a different compatibility story.

## 6. Dependency risks

- **Compose Multiplatform 1.8.1 is in the public surface.** It is tied to a specific Kotlin version and a specific Skiko/Compose klib ABI. Consumers on a different CMP or Kotlin version can hit klib mismatches. Use `implementation` unless the types are intentionally exposed, and document the minimum and maximum supported versions.
- `platform.UIKit` in `iosMain` means all Kotlin-side consumers need the Apple platform libraries. The commonizer and target set (`iosArm64`, `iosSimulatorArm64`, and so on) must be consistent.
- `androidx.startup`, if adopted, is another transitive dependency.
- No actuals are shown for other targets. If JVM/desktop/wasm exist, the build breaks. If they don't, document that.

## 7. Required tests

1. API-dump check (BCV, JVM and klib) that fails on any unreviewed public change.
2. Explicit-API-mode compile of every source set.
3. Generate the Swift export and ObjC header, and assert on exact signatures (diff against a golden file), not string greps for "UIKit".
4. A Swift consumer test that links `MotionKit.framework` and calls `MainViewController` and the motion API.
5. Android unit test: `appContext` uninitialized (a clear error or safe default), scale values 0, 0.5, 1, and missing, plus a settings change at runtime.
6. iOS test: reduce motion on and off, and a change notification updating the UI.
7. Compose UI test that `motionSpec` updates on recomposition when the setting changes.
8. Accessibility test: VoiceOver/TalkBack traversal with each `accessibilitySyncOptions` value, and a performance baseline for `Always` against the default.
9. Dependency matrix: build consumers with the supported CMP and Kotlin range.

## 8. Unresolved decisions

1. Is `isReduceMotionEnabled` public API or an implementation detail?
2. Context provisioning on Android: Initializer, explicit parameter, or host-supplied?
3. Should `MotionSpec` stay a `data class`, accepting the ABI freeze?
4. Should motion be reactive (a `Flow` or Compose `State`) rather than a snapshot?
5. Is the Android semantic of "animator scale == 0" acceptable, or should other values count?
6. Does `MainViewController`/`App` belong in this library at all?
7. Who sets `AccessibilitySyncOptions`: the library or the host app?
8. Which Swift surface is supported (ObjC header only, or Swift export too)? What is the support policy while Swift export is experimental?
9. Which CMP and Kotlin versions are guaranteed?
10. What is the fate of `sectionTitleTraits()`? I recommend removing it.
