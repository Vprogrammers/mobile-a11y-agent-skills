# Android SDK 36 review: `PinEntryActivity.kt`

I reviewed the fixture as supplied, by static reading only. I didn't edit it, build it, or run it on a device. I used the `android-a11y` and `mobile-a11y-review` skills directly, because this session has no tool for delegating to the `android-a11y-engineer` agent. The fixture has no submit control, layout XML, manifest or theme, so anything depending on those is a device check.

## Findings

**P2 — `PinEntryActivity.onBackPressed` (`notice` visibility)**
- Affected users: TalkBack, Switch Access and keyboard users, and anyone using the system back gesture or button.
- Evidence:
  - For apps targeting SDK 36, predictive back is always on and the opt-out is ignored. `Activity.onBackPressed()` is not called.
  - So the "first Back hides the notice" branch never runs, and Back leaves the screen immediately. I'm confident of this from the platform behavior change, but the effect needs a check on an API 36 device.
  - Even where the override does run, it is a hidden, back-only way to dismiss content. The notice has no visible control. Setting it to `GONE` also moves the layout and can drop accessibility focus.
- Fix:
  - The smallest fix is to delete the override and keep the notice as static text.
  - If dismissal is a real product requirement, that is a product decision. Add a visible, labelled dismiss button. Register an `OnBackInvokedCallback` with `onBackInvokedDispatcher` (or `OnBackPressedCallback` on AndroidX), enabled only while the notice is visible.
- Verify:
  - Automated: an Activity test on API 36 that sends Back and asserts the expected finish or dismiss behavior.
  - Device: the back gesture and 3-button navigation, with TalkBack on and off.

**P2 — `onTextChanged`: `counter.announceForAccessibility`**
- Affected users: TalkBack users, and Braille display users.
- Evidence:
  - A spoken announcement fires on every keystroke. It can interrupt or duplicate the editing feedback the platform already gives.
  - `announceForAccessibility` is deprecated, and its delivery isn't guaranteed.
  - The `counter` text ("3 of 6") is also ambiguous and empty until the first edit.
- Fix:
  - Remove the call.
  - Either set `counter.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE`, or drop the live behavior and expose the count as visible helper text.
  - Make the text self-describing, for example a string resource like "%1$d of 6 digits", and set it in `onCreate`.
- Verify:
  - Automated: assert that the live-region mode is set and that no announce event is sent per keystroke.
  - Device: TalkBack typing flow, to check the speech isn't noisy or duplicated. I don't assume exact speech.

**P2 — `pin`: password input type with `transformationMethod = null`**
- Affected users: all users, including anyone who relies on masking, plus TalkBack users.
- Evidence:
  - `TYPE_NUMBER_VARIATION_PASSWORD` says the field is secret, but removing the transformation shows the one-time code in plain text. There is no show/hide control.
  - How TalkBack treats typed characters for this combination is not provable from code.
- Fix:
  - Pick one behavior. For an OTP that the user must read back, use `TYPE_CLASS_NUMBER` without the password variation, so the field is not marked as a password.
  - If masking is wanted, drop `transformationMethod = null` and add a labelled show/hide toggle.
- Verify:
  - Automated: assert `inputType` and `transformationMethod`.
  - Device: whether TalkBack echoes the characters, with and without headphones.

**P2 — `pin`: label, autofill and length**
- Affected users: screen reader, Voice Access and low-vision users, and users who rely on SMS autofill.
- Evidence:
  - The field has only `hint`, which disappears once the user types. Voice Access and screen magnifier users lose the visible name.
  - There is no `setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)`.
  - There is no length filter, though the counter assumes 6 digits.
- Fix:
  - Add a visible `TextView` label and link it with `labelFor`, or use a `TextInputLayout`.
  - Set the autofill hint.
  - Add `InputFilter.LengthFilter(6)` and an appropriate `imeOptions`.
- Verify:
  - Automated: assert the autofill hint, the `labelFor` target, and the filter.
  - Device: Voice Access ("tap one-time code"), and SMS autofill from the keyboard suggestion.

**P2 — `setContentView(LinearLayout…)`: no inset handling**
- Affected users: low-vision, magnifier and large-font users, and anyone on a device with a cutout or gesture bar.
- Evidence:
  - Targeting SDK 36 means edge-to-edge is enforced and there is no opt-out.
  - The root `LinearLayout` applies no system-bar, cutout or IME insets. The notice can draw under the status bar or cutout, and the field can sit under the keyboard at large font or in landscape.
  - The exact overlap depends on the theme and device, which aren't in the fixture.
- Fix: use `ViewCompat.setOnApplyWindowInsetsListener` on the root. Pad it with `systemBars() | displayCutout() | ime()`.
- Verify:
  - Automated: an instrumented test on an API 36 emulator that checks the root padding is non-zero with insets applied.
  - Device: portrait and landscape, 200% font size, and the IME open.

## Automated coverage vs device checks

**Automated** (JVM or Robolectric where the behavior is supported; instrumented on API 36 for framework behavior):
- `inputType`, `transformationMethod`, autofill hints and the length filter on `pin`.
- The live-region mode on `counter`, and no per-keystroke announce.
- The Back result on API 36.
- Root insets padding.
- Espresso `AccessibilityChecks` or ATF for missing labels and touch-target size.

**Device checks:**
- TalkBack: reading order, typing feedback, the counter, and focus after Back.
- Keyboard: Tab into the field, a visible focus indicator, and an IME action.
- Switch Access and Voice Access: reaching and naming the field.
- Large font (200%), landscape, and the keyboard open with edge-to-edge on API 36.
- On large screens, Android 16 ignores orientation and resizability restrictions for apps targeting 36. The fixture sets none, so I found no issue, but check the manifest.

## Blockers
No blocking finding found. I rated nothing P0 or P1: the OTP can still be entered and the task completed in every case.

## Residual risk
- Without the manifest, theme and the rest of the flow (submit, error and resend), I can't judge error handling, the Activity title, or `windowSoftInputMode`.
- Real TalkBack, Voice Access and Switch Access behavior is unverified until it's tested on a device.

**Changed files:** none.
**Commands run:** none (static review only; the two skills were loaded).
