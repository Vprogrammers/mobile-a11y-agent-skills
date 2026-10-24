# Review: `PinEntryActivity.kt` (targetSdk 36, Android 16 supported)

I reviewed the file statically and did not edit it. I did not run it on a device or emulator, and I make no claims about exact TalkBack speech.

**P1 — `PinEntryActivity.onBackPressed`**
Affected users: TalkBack, Switch Access, keyboard and Voice Access users on Android 16. This is the same code path every user takes.
- Evidence: the app targets SDK 36, and Android 16 no longer calls `onBackPressed` or delivers `KEYCODE_BACK` to apps that target it. The notice-dismiss branch and the `super` fallback therefore never run on those devices. The notice stays on screen, and back may finish the Activity instead. Behavior differs between devices that do and don't honor the legacy callback.
- Criterion: WCAG 2.1.1 Keyboard and 2.5.1 Pointer Gestures, only as supporting references.
- Fix: register `onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) { override fun handleOnBackPressed() { … } })`. Use a ComponentActivity or AppCompatActivity base; plain `Activity` has no dispatcher. A cleaner version keeps the callback's `isEnabled` equal to "notice is visible". The callback hides the notice and disables itself, so the next back goes to the system. Set `android:enableOnBackInvokedCallback="true"` in the manifest. Remove the `@Deprecated` override.
- Verify:
  - Automated: Robolectric or an instrumented test that calls `onBackPressedDispatcher.onBackPressed()` and asserts the notice is `GONE`, then that a second call finishes the Activity.
  - Device: Android 16 with three-button and gesture navigation, a keyboard Esc/back key, and Switch Access back.

**P1 — `pin` field: `TYPE_NUMBER_VARIATION_PASSWORD` plus `transformationMethod = null`**
Affected users: TalkBack users, and users of autofill, password managers and SMS code suggestions.
- Evidence: the field is declared as a password input but its digits are shown on screen. Visual and accessibility masking are therefore inconsistent. A password-class field may be treated as sensitive by TalkBack, autofill and the IME. Depending on settings and version, that can mean bullets, character counts only, or suppressed echo. A user who relies on speech may not be able to verify the code they typed. Password semantics were also chosen only to get a numeric keyboard.
- Criterion: WCAG 3.3.8 Accessible Authentication (Minimum) and 1.3.1, as supporting references.
- Fix:
  - Use `InputType.TYPE_CLASS_NUMBER` only, so the field is a plain number field.
  - Add `setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)`.
  - Add `importantForAutofill = IMPORTANT_FOR_AUTOFILL_YES`.
  - Add `imeOptions = IME_ACTION_DONE`.
  - Add `filters = arrayOf(InputFilter.LengthFilter(6))`.
  - If the code must be hidden, keep the password type and the default masking, and do not set `transformationMethod = null`. Don't mix the two.
- Verify:
  - Automated: assert `inputType` and the autofill hints. Run Espresso `AccessibilityChecks`.
  - Device: TalkBack typing, the SMS OTP autofill suggestion, and paste.

**P1 — `pin` field: no accessible name (`hint` only)**
Affected users: TalkBack and Voice Access users.
- Evidence: the only label is `hint = "One-time code"`, and the hint disappears once text is entered. There is no visible persistent label, and no association between `notice` and the field. A hard-coded English string is also used instead of a resource.
- Fix: add a visible `TextView` label and call `labelFor = pin.id` (the field needs an id). Alternatively, wrap the field in a `TextInputLayout`. Keep the hint as a secondary prompt. Move the strings to `strings.xml`.
- Verify:
  - Automated: Espresso `AccessibilityChecks`.
  - Device: TalkBack focus on the field with the field empty and filled, and Voice Access "tap one-time code".

**P2 — `counter` with `announceForAccessibility` on every keystroke**
Affected users: TalkBack users while typing.
- Evidence: `announceForAccessibility` is deprecated on newer Android versions. It fires on every `onTextChanged` call, including programmatic and autofilled changes. The announcement can interrupt or duplicate typing echo, and the string is built from the same text just written to `counter`. "N of 6" is also not localizable as written.
- Fix: remove the announcement call. Either drop the counter, or keep it as a plain `TextView` with `accessibilityLiveRegion = ACCESSIBILITY_LIVE_REGION_POLITE`. Only announce when it matters, for example when the code is complete or invalid. Use a plurals or formatted string resource.
- Verify:
  - Automated: assert the live-region mode and that no announcement is posted per keystroke.
  - Device: TalkBack typing speed, with and without autofill.

**P2 — `counter` initial state and traversal order**
- Evidence: `counter` has no initial text, so it is an empty focusable-by-TalkBack node until the first keystroke. It sits after the field, so the count is not read together with the field.
- Fix: set the initial "0 of 6" in `onCreate`, or hide it with `importantForAccessibility = NO` until needed.
- Verify: use accessibility tree inspection, then a TalkBack linear swipe.

**P2 — `notice` has no dismiss control**
Affected users: any user whose only way to dismiss it is system back, especially Switch Access and Voice Access users.
- Evidence: the only dismissal path is back. No visible close affordance exists. Together with the back issue above, the notice may be undismissable on Android 16.
- Fix: this is a product decision. If the notice must be dismissible, add a native `Button` with a label and a 48 dp target. If it is informational, it needs no dismissal, and the back handling can be removed.
- Verify: Switch Access and Voice Access reach the control.

**P3 — Layout and insets**
- Evidence: there are no explicit padding or inset handling in the layout. At targetSdk 35 and above, edge-to-edge is enforced, so the fields can sit under the system bars or the keyboard.
- Fix: apply `ViewCompat.setOnApplyWindowInsetsListener` with `systemBars()` and `ime()` insets on the root.
- Verify: three-button and gesture navigation, IME open, 200% font scale.

## Coverage

| Layer | What it covers |
|---|---|
| Automated | Back-dispatch behavior, `inputType`, autofill hints and `labelFor` assertions, live-region mode, `AccessibilityChecks` for names and target size |
| TalkBack on device | Field name and state when empty and filled, typing feedback, traversal order, count behavior, notice reading |
| Keyboard | Back/Esc key dismissal, focus visibility, IME action, tab order |
| Switch Access / Voice Access | Reaching and dismissing the notice, back, focusing the field by name |
| Other device checks | Gesture and three-button back on Android 16, SMS OTP autofill and paste, 200% font scale, IME and insets |

## Blockers
- Three P1 findings: back handling on Android 16, password-type input with visible digits, and no persistent field name.

## Device checks
Run these on an Android 16 device (and one older API level for comparison) with TalkBack, a keyboard, and Switch Access. Record device, build, settings, steps and results.

## Residual risk
- I did not read the manifest or the theme, so edge-to-edge and `enableOnBackInvokedCallback` are unconfirmed.
- Whether the code should be masked is a product and security decision.
- Whether the notice should be dismissible is a product decision.
- The base class is a plain `Activity`. Switching to `ComponentActivity` or `AppCompatActivity` for the back dispatcher may need a dependency check, so I'd confirm what the project already uses before changing it.

Changed files: none. Commands run: none beyond reading the skill references.
