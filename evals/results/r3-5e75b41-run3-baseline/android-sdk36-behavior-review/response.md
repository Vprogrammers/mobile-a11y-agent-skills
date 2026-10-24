# PinEntryActivity accessibility review (targetSdk 36)

I reviewed the fixture inline and didn't edit it. These are findings from reading the code, not from running it on a device.

## Findings

| # | Severity | Failure | Why it matters |
|---|---|---|---|
| 1 | **High** | **Back-only dismissal relies on the deprecated `onBackPressed()`.** The notice can only be hidden through `onBackPressed()`. | With `targetSdk 36`, predictive back is on by default and the legacy `onBackPressed()`/`KEYCODE_BACK` path isn't dispatched. The notice can then never be dismissed, and the Back behavior differs from what the code implies. Even where it works, the dismissal has no visible control. Keyboard and Switch Access users have to find a global Back action. Hiding the notice with `GONE` also gives no focus or state feedback. |
| 2 | **High** | **`announceForAccessibility` on every keystroke.** It's called inside `onTextChanged`. | The API is deprecated in API 36. It can interrupt or duplicate the field's own typing feedback, and it is not tied to a view's state, so it can be chatty or dropped. It also gives non-TalkBack users (such as Braille displays) an inconsistent experience. |
| 3 | **Medium** | **The only label is `hint`.** | The hint disappears once the user types. A screen-magnifier or cognitive-load user loses the field's purpose, and the accessible name may depend on the hint. There is no programmatic label association. |
| 4 | **Medium** | **Contradictory password configuration.** The field uses `TYPE_NUMBER_VARIATION_PASSWORD` but sets `transformationMethod = null`. | The digits are visible, but the node may still be flagged as a password. Assistive tech may then suppress echo of what's typed, so sighted and screen-reader users get different information. An OTP isn't a secret to hide from the user. It also blocks the SMS OTP autofill hint, which helps users with motor impairments. |
| 5 | **Medium** | **The counter is inaccurate or misleading.** It reads "N of 6", but no length limit is enforced. The counter is empty at launch, and "N of 6" has no unit. | A user can type 8 digits and be told "8 of 6". The initial state isn't conveyed. |
| 6 | **Low–Medium** | **No view IDs, so state isn't restored on recreation.** | On rotation, font-scale or display-size changes, the entered code and counter are lost. Users who rely on these settings are hit hardest. |
| 7 | **Low** | **Hard-coded strings, no IME action, and no submit control in the fixture.** | Hard-coded strings aren't localizable. With no `imeOptions` action or submit button, keyboard and Switch Access users have no obvious way to finish. The fixture may be partial, so confirm this against the real screen. |

## Minimal native fixes

```kotlin
val label = TextView(this).apply { text = getString(R.string.otp_label) }   // persistent visible label
pin = EditText(this).apply {
    id = R.id.otp_pin                                  // enables state restore
    inputType = InputType.TYPE_CLASS_NUMBER            // drop PASSWORD variation and transformationMethod = null
    filters = arrayOf(InputFilter.LengthFilter(6))
    setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)
    imeOptions = EditorInfo.IME_ACTION_DONE
    // keep hint only as a secondary example, not as the label
}
label.labelFor = R.id.otp_pin

counter.apply {
    id = R.id.otp_counter
    accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE   // replaces announceForAccessibility
    text = getString(R.string.otp_progress, 0, 6)                     // initial state, e.g. "%1$d of %2$d digits entered"
}
// onTextChanged: counter.text = getString(R.string.otp_progress, s?.length ?: 0, 6)
// no announceForAccessibility call
```

- **Back and the notice:** the notice is static information, so the simplest fix is to remove the `onBackPressed()` override and leave it visible. If it must be dismissible, add a real "Dismiss" `Button` and move focus to the field afterwards. If Back must also dismiss it, register an `OnBackInvokedCallback` (or `OnBackPressedCallback` via AndroidX) that is enabled only while the notice is visible.
- **Live-region chattiness:** a polite live region updating on every digit may still be too verbose. If device testing shows that, announce only at meaningful points (for example when complete or on error) by updating the counter conditionally.

## Verification split

### Automated
- **Espresso with `AccessibilityChecks.enable()` (ATF):** catches touch-target size, contrast and missing speakable text. It will **not** catch that a hint-only label disappears, or that Back behavior is wrong.
- **Instrumented tests on an API 36 emulator** (`ActivityScenario`):
  - Press Back, then assert the notice dismissal path works (or that the notice stays, if you remove dismissal).
  - Type 8 digits and assert the field holds at most 6.
  - Recreate the activity and assert the text and counter survive.
- **Property assertions:**
  - `labelFor` points at the field.
  - The counter's `accessibilityLiveRegion` is polite.
  - The field's input type has no password variation.
  - The autofill hint is set.
  - The field's `AccessibilityNodeInfo.isPassword` is false.
- **Lint and code search:** flag hard-coded `text` and any `announceForAccessibility` use.

### Device checks (cannot be proven automatically)
- **TalkBack:**
  - The field's purpose is conveyed when it is focused both empty and filled.
  - Typing feedback isn't duplicated or interrupted by the counter.
  - Counter changes reach the user without moving focus.
  - Verbosity of the live region is acceptable.
  - Don't assert exact speech strings. Check that the information is present and not redundant.
- **Keyboard (Tab/arrows/Enter):**
  - Focus order is label, field, counter, then any actions.
  - Focus is visibly indicated.
  - The IME action or Enter completes the flow.
  - Esc/Back behaves predictably.
- **Switch Access:**
  - Every actionable element, including the dismiss control, can be reached and activated.
  - There is no dependence on a hidden Back-only path.
- **Back on Android 16 hardware:** test the predictive-back gesture and 3-button navigation.
- **Display settings:** check at 200% font scale, large display size, and after rotation.
