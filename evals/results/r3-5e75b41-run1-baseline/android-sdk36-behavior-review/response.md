# Review of `PinEntryActivity.kt` (targetSdk 36)

I reviewed the fixture as inline text. I didn't edit it or run it, so every finding below comes from reading the code and not from device testing.

## Findings

| # | Severity | Failure |
|---|---|---|
| 1 | **High** | Per-keystroke `announceForAccessibility` |
| 2 | **High** | Back handler is dead code on targetSdk 36, and the notice has no operable dismiss control |
| 3 | **Medium** | The field's only label is a `hint` |
| 4 | **Medium** | `PASSWORD` variation combined with `transformationMethod = null` |
| 5 | **Medium** | No window-inset handling (edge-to-edge is enforced) |
| 6 | **Low** | Counter text has no context and no initial state |
| 7 | **Low** | No scrolling for large font or display sizes |

### 1. Per-keystroke `announceForAccessibility` (High)
`announceForAccessibility` fires on every `onTextChanged`. It is deprecated as of API 36 and unreliable across services. It also competes with the screen reader's own echo of the typed digit, so the user can have the digit or the count cut off. The announcement is also tied to text edits, so it fires on programmatic changes (paste, autofill) too.

**Fix:** Delete the call and make the counter a polite live region. Alternatively, drop per-keystroke feedback and announce only on completion or error.
```kotlin
counter.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
counter.text = getString(R.string.digits_entered, len, 6) // "3 of 6 digits"
```
A polite live region can still be chatty. Consider updating it only at meaningful points, such as at 6 digits.

### 2. Back handling and the notice (High)
- With `targetSdk = 36`, predictive back is on by default (`enableOnBackInvokedCallback` defaults to true). `Activity.onBackPressed()` is no longer called, so `notice` is never hidden. Back simply finishes the activity.
- Even if it worked, the only way to dismiss the notice is a hidden Back gesture. There is no visible control, so keyboard and Switch Access users can't operate it. The `GONE` change is also silent.
- Back doubles as "dismiss" and "leave", which is an unexpected navigation side effect.

**Fix (minimal):** Remove the override and keep the notice as persistent text. If it must be dismissible, add a native `Button` ("Dismiss") that sets `GONE` and moves focus to `pin`. If Back handling is still wanted, register an `OnBackInvokedCallback` on `onBackInvokedDispatcher`. Enable it only while the notice is visible, and keep the visible button as well.

### 3. Hint-only label (Medium)
Once text is entered the hint disappears, so there is no persistent visible name. Hint-based names are also less robust for voice control and magnification users.

**Fix:** Add a visible `TextView` "One-time code" before the field. Give both views ids (`View.generateViewId()`) and set `label.labelFor = pin.id`. The hint can stay as an example format.

### 4. Conflicting input type and masking (Medium)
`NUMBER_VARIATION_PASSWORD` marks the node as a password, which affects whether services read or echo its text. `transformationMethod = null` then shows the digits in clear. The two settings contradict each other, so behavior depends on the user's "speak passwords" setting and on the service. If the code is secret, visible digits are also a shoulder-surfing problem.

**Fix:** Pick one.
- **Not secret (typical OTP):** use `TYPE_CLASS_NUMBER` only, plus `setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)`. Add `filters = arrayOf(InputFilter.LengthFilter(6))`.
- **Secret:** keep the default masking and add a "Show code" toggle with an accessible name and state.

### 5. No inset handling (Medium)
Edge-to-edge is enforced at target 35+, and the opt-out is gone at 36. The root `LinearLayout` has no padding for system bars or the IME, so the notice and field can sit under the status bar, and the counter can sit under the keyboard or nav bar.

**Fix:** Use `setOnApplyWindowInsetsListener` on the root. Apply `systemBars() | ime()` insets as padding (via `WindowInsets.getInsets`, which is native on API 30+).

### 6. Counter text (Low)
The counter is empty until the first edit, and "3 of 6" doesn't say what is being counted. Set the initial text to "0 of 6 digits".

### 7. No scroll container (Low)
There is no `ScrollView`, so content can clip at 200% font or at large display size with the keyboard open. Wrap the layout in a `ScrollView`.

## Test coverage

### Automated
- **Lint:** flags the deprecated `onBackPressed` and missing autofill/`labelFor` issues. It does not prove the back behavior is correct.
- **Instrumented test (Espresso with `AccessibilityChecks.enable()`):** catches touch-target size, contrast, and missing names on controls. It will pass the hint-only field, so also assert:
  - `labeledBy` is set on the field's node info.
  - `counter.accessibilityLiveRegion == POLITE`.
  - No `announceForAccessibility` call is made (a code review item or a wrapper spy).
- **Back test:** `pressBack` on an API 36 emulator, asserting the intended behavior (the activity finishes, or the notice dismisses via the button).
- **Insets test:** apply synthetic insets and assert padding on the root.
- **Input type test:** assert `isPassword` and masking are consistent with the chosen design.

### Manual device checks
- **TalkBack:**
  - The field's name is still discoverable after typing.
  - Typed digits are not cut off or doubled by count updates.
  - The counter updates are useful and not excessive.
  - Reading order is notice, then label and field, then counter.
  - Masked vs. clear behavior with "speak passwords" on and off.
  - Do not assert exact speech strings, since they vary by version and settings.
- **Keyboard:** Tab and arrow focus order, and visible focus. The dismiss button (if added) is reachable and activates with Enter or Space. Focus moves sensibly after dismissal.
- **Switch Access:** every control is reachable by scanning, with no action available only through the Back gesture.
- **Android 16 system checks:**
  - Back gesture and 3-button navigation behave consistently, with the predictive back animation.
  - Edge-to-edge looks right in both nav modes with the IME open.
  - 200% font scale and largest display size, with no clipping.
