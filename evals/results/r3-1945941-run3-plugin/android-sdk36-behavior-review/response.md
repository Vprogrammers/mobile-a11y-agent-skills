# Review: `PinEntryActivity.kt` (targetSdk 36, Android 16)

This is a static review of the inline fixture. I didn't edit any files, run any commands, or test on a device. I didn't see the manifest or theme, so I mark where a finding depends on them.

## Findings

**P1 — `PinEntryActivity.onCreate` (root `LinearLayout`, no inset handling)**
- **Affected users:** Low-vision and magnification users, and anyone on a cutout or gesture-bar device. This also affects keyboard users when the IME opens.
- **Evidence:** Apps targeting 36 get enforced edge-to-edge. The layout has no `fitsSystemWindows`, no `OnApplyWindowInsetsListener`, and no IME handling. The notice at the top can sit under the status bar or cutout, and the field can sit under the IME. Assumption: the theme doesn't add its own insets.
- **Criterion:** WCAG 1.4.4 and 2.4.11 (content obscured).
- **Fix:** Add an `OnApplyWindowInsetsListener` on the root that pads it with `systemBars() | displayCutout() | ime()`. Don't opt out of edge-to-edge.
- **Verify:**
  - Automated: an instrumented test that dispatches insets and asserts the root padding.
  - Device: check with a cutout, 3-button and gesture navigation, the IME open, and 200% font.

**P2 — `onBackPressed` override (`notice.visibility = GONE`)**
- **Affected users:** Everyone who uses Back, including TalkBack, Switch Access and keyboard users.
- **Evidence:** For apps targeting 36, predictive back is always on, so `onBackPressed()` isn't called and the opt-out is ignored. The notice never dismisses, and Back leaves the screen and discards the half-entered code. Even where it did run, the notice has no visible dismiss control, and hiding a static notice with Back is a hidden, gesture-only behavior.
- **Fix:** Delete the override, because the notice doesn't need dismissing. If dismissal is a real product need, add a visible close button. Then use `onBackPressedDispatcher.addCallback` with `isEnabled` tied to the notice's visibility, or `OnBackInvokedCallback`.
- **Verify:**
  - Automated: `ActivityScenario` plus `pressBack()` on an API 36 emulator, asserting the intended outcome.
  - Device: Back gesture, 3-button Back and keyboard Esc, with TalkBack on.

**P2 — `pin` (`TYPE_NUMBER_VARIATION_PASSWORD` combined with `transformationMethod = null`)**
- **Affected users:** TalkBack users and anyone who needs to check their entry.
- **Evidence:** The field has contradictory semantics. It is visually plain text, but the password variation marks the node as a password. Accessibility services can then withhold or suppress character echo. The code is also a one-time code, not a secret to mask.
- **Fix:** Use `TYPE_CLASS_NUMBER` only, and drop the `transformationMethod` line. If masking is required, keep the password type and add a visible show/hide toggle.
- **Verify:**
  - Automated: assert the input type and that the node's `isPassword` is false.
  - Device: TalkBack typing echo, with and without the "speak passwords" setting.

**P2 — `pin` (`hint` as the only label, no `autofillHints`, no length limit)**
- **Affected users:** Screen reader, cognitive and motor-impaired users, and SMS autofill users.
- **Evidence:** The hint disappears once the user types, and nothing else is a persistent label. There are no `autofillHints` (`AUTOFILL_HINT_SMS_OTP` is a candidate) and no `InputFilter.LengthFilter(6)`. The "of 6" text implies a limit that isn't enforced.
- **Criterion:** WCAG 1.3.1, 3.3.2 and 1.3.5.
- **Fix:**
  - Add a visible label `TextView` with `labelFor` pointing at the field.
  - Set `setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)`.
  - Add `filters = arrayOf(InputFilter.LengthFilter(6))`.
- **Verify:**
  - Automated: Espresso `AccessibilityChecks` plus assertions on the hints and filters.
  - Device: TalkBack label readout and autofill suggestion.

**P2 — `onTextChanged` (`announceForAccessibility` per keystroke)**
- **Affected users:** TalkBack and braille users.
- **Evidence:**
  - The announcement fires on every character, which competes with typing echo.
  - `announceForAccessibility` is deprecated at API 36.
  - The `counter` text ("3 of 6") has no context.
- **Fix:**
  - Remove the call.
  - Give `counter` `accessibilityLiveRegion = ACCESSIBILITY_LIVE_REGION_POLITE` only if progress updates are wanted.
  - Better, drop the live region and rely on the field's own echo.
  - Make the text self-describing, for example "3 of 6 digits entered".
- **Verify:**
  - Automated: assert the live-region mode and no `announceForAccessibility` call.
  - Device: TalkBack, to check that it isn't verbose or interrupting.

## Blockers
P1: the missing inset handling under enforced edge-to-edge. It depends on the unseen theme, so confirm it on a device.

## Automated vs. device checks

| Layer | Coverage |
|---|---|
| **Automated** | Espresso `AccessibilityChecks.enable()`; assertions on input type, `isPassword`, hints, filters, live-region mode and label association; inset-padding test; `pressBack` behavior on API 36. |
| **TalkBack** | Label and value readout, typing echo and verbosity, focus after the notice change, no stolen focus. |
| **Keyboard** | Tab order, visible focus, Esc and Back, IME action. |
| **Switch Access** | Reach and operate the field and any added dismiss or toggle control. |
| **Display settings** | 200% font, cutout, gesture and 3-button navigation. |

## Residual risk
- I don't know the exact TalkBack speech, which varies by version and settings.
- The manifest, theme and the surrounding flow (resend, errors, submit) weren't provided.
- The deprecated-API and predictive-back conclusions rest on the documented Android 16 behavior. They still need confirmation on an API 36 device.
