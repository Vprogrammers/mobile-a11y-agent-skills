# Android SDK 36 review: `PinEntryActivity.kt`

**Scope and limits.** The fixture file isn't on disk, so I reviewed the inline copy. Line numbers count from `class PinEntryActivity` as line 1 and are approximate. This is static evidence only. I ran no commands and edited no files. I also couldn't launch the `android-a11y-engineer` agent from here, so I applied the `android-a11y` and `mobile-a11y-review` skills directly. Nothing below is an observed TalkBack announcement.

## Findings

```text
P1 — PinEntryActivity.kt:onCreate / setContentView (~L28-35), root LinearLayout
Affected users: Everyone on Android 15+ with targetSdk 36. Low-vision, magnification and TalkBack users are hit hardest, and so are keyboard users whose focused field can be covered.
Evidence: The root layout applies no window insets. With targetSdk 36 on Android 16, the opt-out from edge-to-edge enforcement is not available. The first view (`notice`) can sit under the status bar or display cutout. The `EditText` and `counter` can be covered by the IME or navigation bar. This is proven by the missing inset handling. The exact overlap depends on the device.
Criterion: WCAG 2.2 SC 2.4.11 Focus Not Obscured (Minimum), SC 1.3.1.
Fix: Set `setOnApplyWindowInsetsListener` on the root. Pad it with `getInsets(systemBars() | displayCutout() | ime())` and return `CONSUMED`. Use `WindowInsetsCompat` only if androidx is already a dependency. Keep the root scrollable if the IME leaves little room at large font size.
Verify: Automated: an instrumented `ActivityScenario` test asserts the root padding is at least the system bar inset, and `AccessibilityChecks` runs on the screen. Device: API 36 with a cutout, 3-button and gesture navigation, IME open, font scale 200%, landscape.
```

```text
P2 — PinEntryActivity.kt:onBackPressed (~L38-44)
Affected users: TalkBack, Switch Access, keyboard and Voice Access users who use system Back. This includes users who dismiss the notice that way.
Evidence: `onBackPressed()` is deprecated. With targetSdk 36, predictive back is on by default and the legacy callback is no longer invoked. Back therefore skips the "dismiss the notice first" branch and finishes the activity, which drops the user out of the code-entry flow. Dismissing the notice is also reachable only through Back, because there is no visible dismiss control. Whether Back can reach the legacy callback depends on opt-out and platform details I haven't confirmed.
Criterion: WCAG 2.2 SC 2.1.1 Keyboard, SC 3.2.2 On Input.
Fix: Register an `OnBackInvokedCallback` on `onBackInvokedDispatcher` at `PRIORITY_DEFAULT`, and unregister it when the notice is hidden. This is the platform API on API 33+. Keep the `onBackPressed` branch for lower minSdk. A plain `Activity` has no `OnBackPressedDispatcher`. Moving to `ComponentActivity` would be a new dependency or product decision, so I'm flagging it rather than recommending it. Also decide whether the notice needs a visible dismiss control or should just be non-modal static text.
Verify: Automated: an `ActivityScenario` test calls `pressBack()` once and asserts the notice is `GONE` and the activity is not finishing. A second `pressBack()` asserts the activity finishes. Run it on an API 36 emulator. Device: Back through the 3-button, gesture and keyboard Esc routes, then check where TalkBack focus lands.
```

```text
P2 — PinEntryActivity.kt:onTextChanged (~L16-19)
Affected users: TalkBack users, and Braille display users if the announcement reaches them.
Evidence: `announceForAccessibility` fires on every keystroke, and the visible `counter` has no live region. Platform guidance discourages `announceForAccessibility` and recent API levels mark it deprecated. I haven't confirmed the exact API-level status. Each keystroke can interrupt or duplicate the system's character echo.
Criterion: WCAG 2.2 SC 4.1.3 Status Messages.
Fix: Remove the announce call. Set `counter.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE` so status changes reach TalkBack without a manual announcement. Consider a live region only for the "6 of 6" complete state. Use a string resource such as "%1$d of %2$d digits".
Verify: Automated: Robolectric or instrumented test asserts no `TYPE_ANNOUNCEMENT` event is sent and the live-region mode is set. Device: TalkBack typing six digits. Confirm the speech isn't excessive, doesn't interrupt echo, and doesn't repeat.
```

```text
P2 — PinEntryActivity.kt:pin (~L9-13)
Affected users: TalkBack users, password manager and SMS autofill users, and people who find transcription hard.
Evidence: `TYPE_NUMBER_VARIATION_PASSWORD` marks the node as a password for accessibility and the IME. `transformationMethod = null` shows the digits visually. Visual and accessibility masking therefore disagree, and TalkBack may suppress digit echo depending on the user's "speak passwords" setting. No autofill hint, no `maxLength`, and no `importantForAutofill` are set. The one-time code can't be filled from SMS, which the accessible-authentication rule asks for.
Criterion: WCAG 2.2 SC 3.3.8 Accessible Authentication (Minimum), SC 1.3.1.
Fix: Use `TYPE_CLASS_NUMBER` without the password variation. Add `setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)` where the API level allows it, plus `InputFilter.LengthFilter(6)`. Keep paste enabled. If the code is genuinely secret, choose masking deliberately and apply it both visually and to the accessibility node. That is a product decision.
Verify: Automated: unit test asserts input type, autofill hints, filters, and `AccessibilityNodeInfo.isPassword`. Device: TalkBack with and without "speak passwords", SMS autofill suggestion, and paste.
```

```text
P2 — PinEntryActivity.kt:pin.hint (~L10)
Affected users: Low-vision, cognitive and screen-reader users.
Evidence: The only field name is `hint = "One-time code"`. It disappears on input and has weak visible contrast by default. The separate `notice` text isn't programmatically associated with the field. Nothing links `counter` to the field either.
Criterion: WCAG 2.2 SC 1.3.1, SC 3.3.2.
Fix: Add a persistent visible label `TextView` with a view ID, and set `labelFor` to the field. Keep the hint for the format example only. Move the literal strings into resources.
Verify: Automated: `AccessibilityChecks` (ATF) and an assertion on the label relationship. Device: TalkBack focus on the field both empty and filled.
```

## Blockers
**P1:** Edge-to-edge insets are missing at targetSdk 36. The P2 items above should be fixed in the same change, since the Back change and the OTP input type are also SDK 36 / Android 16 behavior concerns.

## Device checks
- **TalkBack, API 36:** Check the order notice → field → counter. Check the typing echo and the counter updates. Check where focus goes after the notice is hidden.
- **Keyboard and Switch Access:** Check Esc and Back handling, and check that the field's focus is visible and not obscured by the IME.
- **Voice Access:** Check that the field can be targeted by name once there is a visible label.
- **Display settings:** Test font scale 200% and display size, landscape, a cutout device, and dark theme.
- **Autofill and paste:** Test the OTP SMS suggestion and pasting a code.

## Residual risk
- I haven't confirmed the API-level deprecation status of `announceForAccessibility`, or whether any opt-out keeps the legacy `onBackPressed` callback alive.
- Moving to `ComponentActivity` or Material `TextInputLayout` would add a runtime dependency, so I didn't recommend either.
- Standards references are for mapping only. This isn't a legal conformance claim.

**Changed files:** none.
**Commands run:** none.
