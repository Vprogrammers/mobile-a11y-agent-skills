# Review of `PinEntryActivity.kt` (targetSdk 36, Android 16)

I reviewed the fixture as pasted. I did not edit it or run anything.

## Findings

| # | Severity | Failure |
|---|---|---|
| 1 | **High** | The Back-to-dismiss logic is dead code on targetSdk 36. |
| 2 | **High** | The counter is announced with `announceForAccessibility` on every keystroke. |
| 3 | **Medium** | The field's only label is a `hint`. |
| 4 | **Medium** | Nothing caps the code at 6 digits, so the counter can show "8 of 6". |
| 5 | **Medium** | The notice can only be dismissed through Back. |
| 6 | **Low–Medium** | `TYPE_NUMBER_VARIATION_PASSWORD` is combined with `transformationMethod = null`. |
| 7 | **Low** | The counter text is vague, and the strings are hard-coded. |

**1. Back handling (High).**
- Apps targeting API 36 get predictive back by default. `onBackPressed()` and `KEYCODE_BACK` are no longer dispatched to the activity.
- The `notice.visibility = GONE` branch never runs. Back finishes the activity and discards the partly typed code.
- This affects every Back path: gesture, 3-button nav, keyboard Esc/Back, and TalkBack's Back action.

**2. Announcements (High).**
- `announceForAccessibility` is deprecated in API 36.
- It fires per keystroke and competes with TalkBack's own typed-character feedback, so speech gets interrupted or doubled.
- It is invisible to braille and other services that rely on node events.
- The counter is also not a live region, so the structural route isn't available.

**3. Label (Medium).**
- A `hint` disappears once text is entered, and it is not a durable label.
- Whether the name is still exposed after typing varies by service and version, so verify it on a device.
- There is no visible label or `labelFor` relationship.

**4. No length limit (Medium).**
- There is no `InputFilter.LengthFilter(6)`.
- The counter can read "8 of 6", which is confusing and implies a hidden error.

**5. Notice dismissal (Medium).**
- The notice has no on-screen control, so touch, Switch Access, and keyboard users can only dismiss it through the Back path.
- Once finding 1 is fixed, that path is still a surprising place for dismissal to live.
- The notice also vanishes silently.

**6. Password variation (Low–Medium).**
- `TYPE_NUMBER_VARIATION_PASSWORD` marks the node as a password field, which can suppress echo in screen readers.
- `transformationMethod = null` then shows the digits on screen anyway.
- The semantics and the visuals disagree. Pick one: plain `TYPE_CLASS_NUMBER` for a visible one-time code, or keep the masking.

**7. Counter text and strings (Low).**
- "3 of 6" doesn't say what is being counted.
- The strings are hard-coded and not localizable.
- Both views use `wrap_content` with no padding. Check them at 200% font scale.

## Minimal native fixes

```kotlin
// Visible label tied to the field (replaces reliance on hint)
val label = TextView(this).apply { text = getString(R.string.otp_label); labelFor = pin.id }
pin.id = View.generateViewId()   // before labelFor is read
pin.filters = arrayOf(InputFilter.LengthFilter(6))
pin.inputType = InputType.TYPE_CLASS_NUMBER      // or keep masking and drop transformationMethod = null
pin.setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)

// Counter: live region instead of announceForAccessibility
counter.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
counter.text = getString(R.string.otp_count, len, 6)  // e.g. "%1$d of %2$d digits"
// delete counter.announceForAccessibility(...)
```

```kotlin
// Back: use the predictive-back API, enabled only while the notice is showing
private val backCallback = OnBackInvokedCallback { notice.visibility = View.GONE; isEnabled = false }
// onCreate:
onBackInvokedDispatcher.registerOnBackInvokedCallback(OnBackInvokedDispatcher.PRIORITY_DEFAULT, backCallback)
// unregister it when the notice is hidden, so the system Back animation and finish() work again
// delete the onBackPressed override
```

Better still, drop Back-to-dismiss and add a visible "Dismiss" `Button`, or leave the notice in place. That fixes the Switch Access and keyboard gap in finding 5.

If a live region still proves chatty on a device, announce only when the count crosses a meaningful threshold, such as complete or invalid.

## Verification split

**Automated**
- Lint should flag the deprecated `onBackPressed` and `announceForAccessibility`. Add a check for `android:enableOnBackInvokedCallback`.
- Espresso with `AccessibilityChecks.enable()` (ATF) covers touch-target size, contrast, and missing speakable text. It likely won't flag the hint-only label, because ATF accepts hints.
- Instrumented or Robolectric assertions can check:
  - `pin.labelFor`, or the label view's `labelFor` pointing at the field;
  - `counter.accessibilityLiveRegion == POLITE`;
  - the filter length of 6 (type 8 digits and assert 6);
  - the `inputType`;
  - `pressBack()` dismissing the notice and not finishing the activity (use `ActivityScenario` and a `targetSdk 36` emulator);
  - that no `announceForAccessibility` call remains.

**Manual device checks**
- **TalkBack:**
  - The field name is still conveyed after text is entered.
  - Typing doesn't produce doubled or interrupting speech from the counter.
  - Digits are echoed or not as intended for the chosen input type.
  - The notice is reachable and its dismissal is understandable.
  - Don't assert exact speech strings. Check that the information is present and not repeated.
- **Keyboard (hardware):**
  - Tab and arrow focus order is label, field, counter, and any dismiss button.
  - The focus indicator is visible.
  - Esc/Back dismisses the notice first, then leaves.
  - The IME action works.
- **Switch Access:** The dismiss control (or Back) can be reached and activated. The field is scannable, and focus doesn't get lost when the notice disappears.
- **Android 16 specifics:** The predictive back gesture animation behaves correctly, and entered text isn't lost unexpectedly. Also test at 200% font and display size, and with SMS-OTP autofill.
