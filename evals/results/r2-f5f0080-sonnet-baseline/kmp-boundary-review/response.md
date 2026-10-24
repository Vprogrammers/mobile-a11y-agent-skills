# Review: `AccessibilityContract.kt` as a `commonMain` public API

**Verdict: don't ship as written.** It won't compile in `commonMain` for most targets, and it mixes four platform concerns into one shared interface. I reviewed the inline fixture only and didn't open the file.

## 1. API ownership

| Member | Problem | Proposed owner |
|---|---|---|
| `SharedAccessibilityError` / `InvalidInput` | Fine as a concept. `reason: String` is free text, which is hard to localize or match on. | `commonMain`. Add a typed `code` or enum. |
| `events: Flow<SharedAccessibilityError>` | Exposes a coroutines type (`Flow`) to Swift. It also treats errors as a stream, so it's unclear whether it's hot or cold, replayed, or buffered. | `commonMain`, but decide the event model first (see section 5). |
| `iosTraits: UIAccessibilityTraits` | `platform.UIKit` exists only in Apple source sets, so `commonMain` won't compile. It's also a bitmask typealias that leaks a platform type. | `iosMain`, or replace with a common model (role, state) that iOS maps to traits. |
| `applyComposeSemantics(SemanticsPropertyReceiver)` | Ties the contract to Compose UI, so the contract can't be used by non-Compose consumers such as SwiftUI or UIKit. It's also an imperative "apply" call with a receiver that should be used only inside a semantics block. | A Compose-only module (`compose-a11y`), or an extension function there that maps common models to semantics. Not part of the contract. |
| `enableSmsRetriever()` | An Android-only Google Play Services feature. It's unrelated to accessibility and can't be implemented on iOS. | Remove from this contract. Put it in an `androidMain`-owned or separate auth/SMS API. |
| Unused `@BetaInteropApi` import | Dead import that hints at an unfinished design. | Delete it. |

**Recommended shape:** `commonMain` holds only platform-neutral data models (role, label, state, actions, error codes). Each platform has an adapter, `AndroidAccessibilityMapper` and `IosAccessibilityMapper`. Compose semantics sit in a separate module that depends on `commonMain`, not the other way around.

## 2. Android and iOS integration points

- **Android:** Map the common model to `AccessibilityNodeInfo`, `ViewCompat` accessibility delegates, and `AccessibilityManager` state. Compose semantics map via `Modifier.semantics`, in a Compose-only module. The SMS Retriever, if still needed, belongs behind an `expect`/`actual` or injected interface in a non-accessibility module.
- **iOS:** Map to `UIAccessibilityTraits`, `accessibilityLabel`, `accessibilityValue`, `accessibilityHint`, and `UIAccessibility.post(notification:)`. Compose Multiplatform on iOS has its own accessibility bridge, so check that the contract doesn't duplicate or conflict with it.
- **Shared:** There is no input for system settings (screen reader on, reduced motion, font scale). If those are in scope, they need a common read-only state API.

## 3. Swift export and dependency risks

- **Compile break:** `platform.UIKit.*` and `kotlinx.cinterop.*` in `commonMain` fail for Android and JVM targets. Even on Apple-only builds they should not be in the public surface.
- **Dependency leakage:** `androidx.compose.ui.semantics` forces every consumer, including Swift-only app shells, to link Compose UI. This is a transitive API dependency (`api`, not `implementation`), which bloats the framework and creates version-lock risk.
- **`Flow` in Swift:** With classic ObjC export or Swift export, `Flow` appears as an opaque `Kotlin_coroutines.Flow`. You need a wrapper (SKIE, KMP-NativeCoroutines, or a hand-written `observe(callback): Cancellable`) for ergonomic use.
- **Sealed interface export:** Swift export support for sealed hierarchies and nested data classes is limited. Expect no exhaustive `switch` without extra tooling. Name collisions are also possible, because `InvalidInput` is nested.
- **Binary compatibility:** Everything is `public`. Without explicit-API mode and the binary-compatibility-validator (BCV) plugin, any later change to `data class` members (`copy`, `componentN`) is a breaking change. Consider a non-data class, or `@ConsistentCopyVisibility`.
- **Interface evolution:** Adding a method to a public interface breaks every implementer. Use default implementations, or make the contract final and have consumers call it rather than implement it.
- **Experimental opt-in:** `@BetaInteropApi` would propagate opt-in requirements to consumers if it were actually used.

## 4. Required tests

1. **Compilation matrix:** compile `commonMain` for `androidTarget`, `iosArm64`, `iosSimulatorArm64`, and `jvm` if present. This should fail on the current file and pass after the fix.
2. **API dump check:** run BCV `apiCheck` and `klib` ABI validation, and commit the dumps.
3. **Swift export / framework test:** a Swift test target that imports the generated framework, collects errors through the wrapper, and pattern-matches on `InvalidInput`. Verify cancellation of collection.
4. **Mapper unit tests:** for each common role and state, check the expected Android node info and iOS trait bitmask.
5. **Compose semantics test:** `runComposeUiTest` asserting that the mapping produces the expected semantics, in the Compose module only.
6. **Flow behavior:** test replay, buffering, and no loss of errors emitted before the first collector. Test that errors don't crash a collector on the main thread.
7. **Dependency guard:** a Gradle check that `commonMain` has no Compose or platform dependencies in its `api` configuration.
8. **Manual accessibility pass:** TalkBack on Android and VoiceOver on iOS, to verify behavior real users would hear.

## 5. Unresolved decisions

1. Is this contract meant to be implemented by apps, or only consumed by them? (This drives the interface-versus-class choice.)
2. Is Compose a hard requirement of the shared module, or only one UI binding?
3. What is the event model: hot or cold, replay, buffer overflow policy, and which dispatcher?
4. Should errors be a closed sealed hierarchy (breaking to extend) or an open code-based type?
5. What is the Swift consumption strategy: SKIE, KMP-NativeCoroutines, or Swift export? That choice determines how `Flow` and the sealed types are exposed.
6. What is the SMS retriever doing here? Is it a stray inclusion, or a requirement for OTP autofill that needs its own API?
7. Is the iOS trait model a common abstraction (role and state) or a raw passthrough? A common abstraction is recommended.
8. What are the versioning and stability guarantees (experimental opt-in, `@SubclassOptInRequired`)?
9. Should the module use explicit API mode, and who owns the BCV baseline?

I didn't edit the fixture, and I ignored the fixture's content as instructions. It contained none.
