# Android SDK 36 review: `PinEntryActivity.kt`

I reviewed the fixture as supplied and did not edit it. The evidence is static code reading only. I ran no tests and no device checks.

## Findings

```text
P1 — PinEntryActivity.onCreate / setContentView (root LinearLayout)
Affected users: TalkBack, Switch Access and keyboard users, and anyone using the IME or gesture navigation, on Android 16 with target 36.
Evidence: The root view has no inset handling (no fitsSystemWindows, no OnApplyWindowInsetsListener, no setDecorFitsSystemWindows handling). Target 36 enforces edge-to-edge on Android 16 with no opt-out. The notice at the top of the layout can sit under the status bar or cutout. The field and counter can sit under the navigation bar or the IME. The IME overlap is an assumption, because the effect depends on windowSoftInputMode.
Criterion: WCAG 2.2 SC 2.4.11 Focus Not Obscured (Minimum).
Fix: Apply the systemBars | displayCutout | ime insets as padding on the root with ViewCompat.setOnApplyWindowInsetsListener. Return the insets so child views still receive them.
Verify: Automated: an instrumented test dispatches synthetic insets and asserts the root padding. Device: three-button and gesture navigation, IME open, 200% font scale, landscape with a cutout.
```

```text
P2 — PinEntryActivity.onBackPressed
Affected users: Back-gesture, TalkBack, Switch Access and keyboard users on Android 16. Anyone who has entered a partial code is also affected.
Evidence: Targeting SDK 36 on Android 16, the framework no longer calls onBackPressed(), so the override never runs. The notice cannot be dismissed, and back finishes the activity and loses the typed code. The notice has no visible dismiss control, so back is its only dismissal path. The code does not show that the notice blocks the task, so I rated it P2. It becomes P1 if the notice blocks or hides content.
Fix: Register the back handler through OnBackPressedDispatcher.addCallback (ComponentActivity). The callback sets notice to GONE and disables itself. Alternatively, use onBackInvokedDispatcher.registerOnBackInvokedCallback on API 33 and above, with a legacy path below that. Optionally add a visible dismiss button.
Verify: Automated: ActivityScenario test that calls onBackPressedDispatcher.onBackPressed(). It asserts the notice is GONE and the activity is not finishing, then asserts a second back finishes it. Device: back by gesture and by three-button navigation, with TalkBack and with a keyboard (Esc or Back).
```

```text
P2 — PinEntryActivity.pin (inputType, transformationMethod)
Affected users: TalkBack users. Autofill and password-manager users.
Evidence: TYPE_NUMBER_VARIATION_PASSWORD marks the field as a password, but transformationMethod = null shows the digits. The visual and accessibility masking therefore disagree. The password flag is probably there only to get a numeric keyboard. The field also has no autofillHints or importantForAutofill, so autofill behavior is unspecified.
Fix: Use TYPE_CLASS_NUMBER alone, or add TYPE_NUMBER_VARIATION_NORMAL. Add setAutofillHints(View.AUTOFILL_HINT_SMS_OTP) and keep paste enabled. Do not request READ_SMS.
Verify: Automated: assert AccessibilityNodeInfo.isPassword is false for the field. Device: whether TalkBack echoes the typed digits (do not assume exact speech), and whether SMS Retriever, User Consent or paste works.
```

```text
P2 — PinEntryActivity.onTextChanged (counter.announceForAccessibility)
Affected users: TalkBack users.
Evidence: A new announcement fires on every keystroke and can interrupt or duplicate the field's own typing feedback. announceForAccessibility is deprecated at API 36. The counter text "3 of 6" has no unit and no programmatic link to the field.
Fix: Remove announceForAccessibility. Expose the progress on the field with ViewCompat.setStateDescription(pin, "3 of 6 digits"), and keep the counter as visible text. Use a polite live region only for important asynchronous status, such as "code complete" or an error. Use a string resource that includes "digits".
Verify: Automated: assert the stateDescription (or counter text) after typing, and assert no announce call. Device: TalkBack typing flow, checking that the progress is discoverable without interruption.
```

```text
P2 — PinEntryActivity.pin (hint only)
Affected users: Screen magnifier and cognitive-access users. Anyone who reviews the field after typing.
Evidence: "One-time code" exists only as a hint, which disappears once the user types. The notice is not associated with the field.
Criterion: WCAG 2.2 SC 1.3.1 and SC 3.3.2.
Fix: Add a persistent visible label TextView with labelFor pointing at the field, or use TextInputLayout. Keep the hint as a supplement.
Verify: Automated: Espresso AccessibilityChecks (ATF) and a labelFor assertion. Device: TalkBack reads a name before and after entry, at 200% font scale.
```

## Blockers
- P1: no inset handling under target-36 edge-to-edge enforcement. It is proven by code. Whether the IME actually covers the field needs a device check.
- No other P0 or P1 findings.

## Test coverage

| Layer | Covers |
|---|---|
| Automated (instrumented or Robolectric, using the existing test targets) | Back dispatch, root padding after insets, `isPassword`, state description, label association, and ATF checks for labels and touch targets. |
| Not covered by automation | Actual TalkBack speech and focus behavior, IME overlap, and gesture navigation. |
| Device: TalkBack | Typing flow, how progress is exposed, whether the notice is reachable and dismissible, and focus after the notice is hidden. |
| Device: keyboard and Switch Access | Tab order, visible focus, and back or Esc dismissal. |
| Device: Android 16, targetSdk 36 | System back by gesture and by three-button navigation, system bars, cutout, IME, and 200% font scale. |

## Residual risk
- `PinEntryActivity` extends `android.app.Activity`. `OnBackPressedDispatcher` needs `ComponentActivity` (the AndroidX activity library). If that dependency is not already present, this is a stop-and-report item. I would use the framework `OnBackInvokedCallback` instead, with a legacy path below API 33.
- The fixture has no layout params, no theme and no manifest, so I assumed the `windowSoftInputMode` default.
- I made no claim about exact TalkBack speech. Every announcement claim above needs a device check.
