# Review: `AccessibilityContract.kt` as a `commonMain` public API

**Verdict: not shippable as written.** The file is in `commonMain` but imports from three platform or toolkit layers. `platform.UIKit` won't compile for the Android target. `SemanticsPropertyReceiver` ties the contract to Compose. `enableSmsRetriever` is Android-only behavior with no relation to accessibility.

## 1. API ownership

| Member | Problem | Owner |
|---|---|---|
| `SharedAccessibilityError` / `InvalidInput(reason: String)` | Acceptable shape. `reason` is a free-form string, so callers can't branch on it, and it risks being user-facing and unlocalized. | `commonMain` (keep). Replace `reason` with a typed code, or add a stable `code` and keep the message for diagnostics only. |
| `events: Flow<SharedAccessibilityError>` | Named `events` but carries only errors. Hot or cold, replay, and buffering are unspecified. | `commonMain`, but rename it (e.g. `errors`) or widen the event type. Document the semantics. |
| `iosTraits: UIAccessibilityTraits` | `platform.UIKit` is unavailable on Android, so `commonMain` fails to compile. It is also a platform-typed property on a "shared" contract. | `iosMain`. In common, model a platform-neutral enum or set such as `Role`, `State`, `Trait`, and map it in each platform. |
| `applyComposeSemantics(SemanticsPropertyReceiver)` | Hard-couples the contract to Compose UI. It is a UI-layer concern, not a service contract. It is also only usable from a Compose scope. | Compose-specific module (`ui-compose`), as an extension function such as `Modifier.a11y(model)`. Keep the contract UI-agnostic. |
| `enableSmsRetriever()` | Google Play Services SMS Retriever is Android-only. It has no connection to accessibility, and it has a privacy and permission surface. | `androidMain`, in a separate feature API. Remove it from this contract. |
| `kotlinx.cinterop.BetaInteropApi` | The import is unused. It is native-only and a beta opt-in, and it fails in common or Android code. | Delete it. |

Suggested split:
- **`:accessibility-api` (commonMain):** plain data types (`A11yRole`, `A11yState`, `A11yLabel`), error types, and the service interface.
- **`:accessibility-compose`:** semantics mapping, depending on Compose.
- **`androidMain` / `iosMain`:** actual implementations that map to `AccessibilityNodeInfo` or `contentDescription` on Android, and to `UIAccessibilityTraits` on iOS.
- **Separate Android-only module:** the SMS retriever.

## 2. Android and iOS integration points

**Android**
- Map the common model to Compose semantics (`role`, `contentDescription`, `stateDescription`, `liveRegion`) and to View-system `AccessibilityNodeInfoCompat` where Views are still used.
- Detect TalkBack and accessibility services with `AccessibilityManager`. Announce through `View.announceForAccessibility` or live regions.
- If the SMS retriever is kept, it needs a `BroadcastReceiver` and a Play Services dependency. It belongs behind its own interface, with lifecycle and consent handled there.

**iOS**
- Map the common model to `UIAccessibilityTraits`, `accessibilityLabel`, `accessibilityValue` and `accessibilityHint`. Post `UIAccessibility.post(notification:argument:)` for announcements and layout changes.
- For Compose Multiplatform on iOS, check how Compose semantics bridge to UIKit accessibility elements. Don't assume `iosTraits` and Compose semantics stay in sync.
- Observe VoiceOver status via `UIAccessibility.isVoiceOverRunning` and its change notification.

**Threading:** `UIAccessibility` calls must run on the main thread. Decide whether the contract guarantees main-thread delivery, or whether the implementation hops to it.

## 3. Swift export and dependency risks

- **Swift export / ObjC header:**
  - `Flow<T>` is not usable from Swift. It needs a wrapper, a SKIE-style bridge, or an `AsyncSequence` adapter. Check which one the project uses and whether it is supported with Swift export.
  - A `sealed interface` with a nested `data class` exports poorly. Generics and sealed hierarchies lose exhaustiveness in Swift. Expect awkward names like `SharedAccessibilityErrorInvalidInput`.
  - Properties typed `UIAccessibilityTraits` and `SemanticsPropertyReceiver` can't be meaningfully exposed. The Compose type would leak into the iOS framework header and pull in Compose internals.
- **`public` explicit API mode:** every symbol is committed API. Enable explicit API mode and binary-compatibility validation (`binary-compatibility-validator`) so these members don't ship by accident.
- **Dependency leakage:**
  - `compose.ui` becomes an `api` dependency of a nominally shared module. This forces Compose on every consumer, including non-UI ones.
  - `kotlinx.coroutines` is an unavoidable `api` dependency if `Flow` is public. Pin the version policy.
  - `platform.*` is available only on Apple targets. Expect failures on Android, JVM and any other target, and on the metadata compilation.
- **Naming:** the `Shared*` prefix adds noise and carries no meaning. Prefer `Accessibility*`.
- **Hierarchical source sets:** `platform.UIKit` would be reachable from `appleMain` or `iosMain`, never from `commonMain`.

## 4. Required tests

1. **Compile matrix:** build metadata, `androidTarget`, `iosArm64`, `iosSimulatorArm64` and the JVM target, if any. The current file must fail, and the fix must pass. This is a CI gate.
2. **API dump:** `apiCheck` (BCV) baselines for Android and the klib. Verify no platform or Compose types appear in the common dump.
3. **Dependency guard:** a Gradle test that `commonMain` has no `compose.ui` or `platform.*` imports. A lint or `konsist` rule can enforce it.
4. **Contract tests in `commonTest`:** a fake implementation checking that `events` emits `InvalidInput`, that collection and cancellation behave, and what happens with no collectors.
5. **Android instrumented tests:** Compose UI semantics assertions (`assertContentDescriptionEquals`, `SemanticsProperties.Role`), plus the Accessibility Test Framework (ATF) checks via `AccessibilityChecks.enable()`.
6. **iOS tests:** XCUITest or unit tests asserting that traits and labels map as expected. Include a VoiceOver-on/off toggle path if testable.
7. **Swift consumption test:** a small Swift package or XCTest that builds against the exported framework. It should collect the error stream and switch over the error type.
8. **Mapping tests:** table-driven tests for common role/state to Android semantics and to iOS traits, including unmapped values.
9. **SMS retriever (if retained elsewhere):** permission, timeout (5 minutes), and registration/unregistration lifecycle tests.

## 5. Unresolved decisions

1. Is this a service contract or a UI-semantics model? The answer decides whether Compose appears at all.
2. What is the common vocabulary of roles, states and traits, and who owns it? Mirror the existing Compose `Role` values, or define a smaller set?
3. How are errors surfaced: a `Flow`, `Result`, or exceptions? Is `InvalidInput.reason` localized or a code? Should the error type be extensible, and is a `sealed` hierarchy a binary-compatibility risk when subtypes are added later?
4. Why is `enableSmsRetriever` in this contract? Move it, or justify it. It also needs a privacy review.
5. Which Swift interop route does the project support (Swift export, ObjC export, SKIE, or a manual wrapper), and what is the minimum Kotlin version?
6. Is `Flow` an acceptable public type for iOS consumers, or should the API expose callbacks or a `suspend` function plus a wrapper?
7. Are the interfaces open for consumer implementation, or sealed or `@SubclassOptInRequired`, so methods can be added without breaking implementers?
8. Which threads and dispatchers does `events` emit on?
9. Stability policy: should the API be marked `@ExperimentalAccessibilityApi` until it settles?

I didn't edit the fixture, and everything above comes from the inline source. I didn't see any build files, so I couldn't check the actual source-set layout or dependency declarations.
