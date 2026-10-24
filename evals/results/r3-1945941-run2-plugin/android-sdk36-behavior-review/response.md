# Review: `PinEntryActivity.kt` (targetSdk 36, Android 16)

This is a static review of the fixture only. I did not edit any files, run tests, or use a device. The manifest, theme and resources weren't provided, so I flag them where they matter.

## Findings

**P2 — `onBackPressed()` override**
- **Affected users:** Everyone who uses back, including keyboard (Esc/Back), Switch Access and TalkBack back gesture users.
- **Evidence:** With `targetSdk = 36`, predictive back is on by default. The framework no longer calls `onBackPressed()` unless the manifest sets `android:enableOnBackInvokedCallback="false"`. I couldn't see the manifest. If it doesn't opt out, the "hide notice first" branch is dead on Android 16 but still runs on older OS versions. Back then behaves differently across the supported range. Where the override does run, back hides the notice instead of leaving the screen. The notice is plain static text, not a dismissible pane. The notice is also removed (`GONE`) with no focus handling, so accessibility focus can be lost if it was on the notice.
- **Criterion:** WCAG 3.2.3 and 3.2.4 (consistent behavior), loosely.
- **Fix:** Delete the override, so back always leaves the screen. If the dismissal is a real requirement, register an `OnBackInvokedCallback` through `onBackInvokedDispatcher` (API 33+), enable it only while the notice is visible, and fall back to `onBackPressed` below API 33. Do not add a library for this unless the project already uses `androidx.activity`.
- **Verify:**
  - Automated: an instrumented `ActivityScenario` test on an API 36 emulator that presses back and asserts the expected finish or hide behavior. Run the same test on an API 32 or 34 emulator to confirm the two match.
  - Device: Back through gesture, three-button navigation, keyboard Esc and Switch Access, with TalkBack on. Confirm where focus lands.

**P2 — Edge-to-edge insets (assumption: the theme doesn't handle them)**
- **Affected users:** Low-vision and magnification users, and anyone whose device has a cutout or an on-screen keyboard.
- **Evidence:** At targetSdk 35 and above, edge-to-edge is enforced, and the opt-out is not honored at 36. The root `LinearLayout` has no inset handling and no scroll container. The notice at the top can sit under the status bar or cutout. The IME can cover the field and counter, and large font or landscape adds to this. If the overlap is confirmed on a device, raise this to P1, because text would be unreadable.
- **Fix:** Apply `setOnApplyWindowInsetsListener` on the root and pad by `systemBars() | displayCutout() | ime()`. Wrap the content in a `ScrollView`.
- **Verify:**
  - Automated: an inset-padding assertion in an instrumented test.
  - Device: a cutout device, IME open, 200% font and landscape.

**P2 — `announceForAccessibility` on every keystroke**
- **Affected users:** TalkBack and braille display users.
- **Evidence:**
  - `announceForAccessibility` is called inside `onTextChanged`, so it fires on every character. TalkBack already echoes typed characters, so the announcements are redundant and can interrupt the echo.
  - The API is deprecated as of API 36.
  - The counter has no initial text until the first edit.
  - "3 of 6" has no unit.
  - The strings are hardcoded and can't be localized.
- **Fix:**
  - Drop the announcement.
  - Set `counter.accessibilityLiveRegion = ACCESSIBILITY_LIVE_REGION_POLITE` only if the count is worth announcing. Otherwise make it passive text.
  - Set the initial text.
  - Move the strings to a plurals resource, such as "%1$d of 6 digits".
- **Verify:**
  - Automated: assert the counter's initial text, its live-region mode, and that no announcement is sent (for example, check that no `TYPE_ANNOUNCEMENT` event is emitted).
  - Device: type quickly with TalkBack and with a braille display. Check for cut-off or duplicated speech without asserting the exact wording.

**P2 — Contradictory input type and masking (`NUMBER_VARIATION_PASSWORD` with `transformationMethod = null`)**
- **Affected users:** Users who need to see the code to verify it (low vision, cognitive disability). Also anyone exposed to shoulder-surfing, and TalkBack users.
- **Evidence:** The field is flagged as a password, but masking is removed, so the code shows in clear text. The flag also changes what accessibility services and keyboards do with the field, such as suppressing suggestions and possibly muting spoken characters. The result is unpredictable and not a deliberate choice. I have not confirmed how TalkBack treats this combination on a device.
- **Fix:** This needs a product decision. A one-time code usually uses `TYPE_CLASS_NUMBER` with no password variation, so it is visible and verifiable. If it must be masked, keep the default masking and add a native show/hide toggle. Also set `setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)`.
- **Verify:**
  - Automated: assert the `inputType`, autofill hints and `isPassword` in an instrumented test.
  - Device: TalkBack with "speak passwords" on and off, SMS-code autofill, and a clipboard paste.

**P2 — Hint-only label and an unenforced length**
- **Affected users:** Screen reader and low-vision users, and users with cognitive or memory disabilities.
- **Evidence:** The field's only label is `hint`. It disappears once text is entered, so there is no persistent visible label. The counter says "of 6" but there is no `InputFilter.LengthFilter(6)`, so the screen can show "8 of 6". There is also no `imeOptions` or action to submit the code, and no error state.
- **Fix:** Add a persistent visible `TextView` label and link it with `labelFor`. Add `filters = arrayOf(InputFilter.LengthFilter(6))`. Set `imeOptions` to `IME_ACTION_DONE`.
- **Verify:**
  - Automated: Espresso `AccessibilityChecks` or ATF for the label, and a test that input stops at 6 characters.
  - Device: TalkBack focus on the field with text entered, and Voice Access "tap one-time code".

**P3 — Hardcoded user strings and no layout params**
- **Affected users:** Localized and large-font users.
- **Evidence:** The strings are literals, and the views have no padding or margins.
- **Fix:** Move the strings to resources and add spacing.
- **Verify:** Pseudo-locale and 200% font on a device.

## Blockers
No blocking finding found (no P0 or P1 proven from the code). Edge-to-edge could become P1 if the device check shows the notice is covered.

## Device checks
- TalkBack: typing echo, focus order (notice → label → field → counter), and focus after back.
- Keyboard: Tab order, Esc/back, and a visible focus indicator.
- Switch Access: reaching the field and the IME action.
- Voice Access: target the field by its label.
- Android 16 (API 36) and one older release (such as API 33 or 34), to compare back behavior.
- 200% font, landscape, a cutout device, IME open, and SMS-code autofill.

## Residual risk
- The manifest and theme weren't provided, so back opt-out and inset handling are inferred.
- Actual TalkBack speech for the password-variation field is unconfirmed.
- Whether the code should be masked is a product decision.
- Automated checks catch labels, target size and contrast. They do not catch focus loss or speech quality.

**Changed files:** none. **Commands run:** none.
