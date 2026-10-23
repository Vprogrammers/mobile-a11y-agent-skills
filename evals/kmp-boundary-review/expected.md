# Expected: KMP boundary review

Severity does not apply to architecture output; the row must appear as a risk or required change.

## Must find

| ID | Location | Min severity | Evidence the finding must contain |
|---|---|---|---|
| `compose-type-in-common` | `AccessibleField.applySemantics` | Required | `SemanticsPropertyReceiver` belongs in the Android adapter. |
| `uikit-type-in-common` | `AccessibleField.iosTraits` | Required | UIKit traits belong in the iOS adapter. |
| `shared-speech-string` | `spokenDescription()` | Required | Share state and localizable content, not the spoken sentence. |
| `raw-flow-export` | `FieldValidator.errors`, `FieldError` | Required | Flow and sealed class need an explicit Swift interop decision (direct export, Swift export, or SKIE). |
| `play-services-in-core` | `OtpAutofill` | Required | Play Services must stay out of the core artifact; inject an optional capability. |
| `expect-actual-hides-ownership` | `PlatformFocusHandle` | Required | Screen-reader focus stays native; do not expose it through `expect`/`actual`. |

## Must not

- Recommend `expect`/`actual` for `AccessibleField` as a whole.
- Edit files.

## Expected output shape

The five sections defined by `kmp-a11y-architect`: API and ownership, integration points, export and dependency risks, tests, open decisions.
