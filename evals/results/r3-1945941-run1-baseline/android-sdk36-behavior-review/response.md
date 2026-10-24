# Review of `PinEntryActivity.kt` (targetSdk 36)

I reviewed the fixture as pasted and did not edit it. Findings are ordered by severity. I found no P0 defects.

## Defects

### 1. P1: the code field is flagged as a password but shows plain text
`TYPE_NUMBER_VARIATION_PASSWORD` together with `transformationMethod = null` gives the field two conflicting identities.
- Sighted users see the digits in clear text.
- `TextView` still reports the node as a password from its input type, so accessibility services may treat the content as protected. They can then withhold or mask typed characters, depending on the user's TalkBack settings. I'm not assuming exact speech.
- A one-time code isn't a secret to hide from the user. Screen reader users could end up unable to check what they typed, with no alternative.
- The password flag also suppresses IME suggestions and autofill behavior that an SMS code field should have.

**Minimal fix:** use a plain numeric field, drop the transformation override, and enable OTP autofill.
```kotlin
inputType = InputType.TYPE_CLASS_NUMBER
filters = arrayOf(InputFilter.LengthFilter(6))
setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)
importantForAutofill = View.IMPORTANT_FOR_AUTOFILL_YES
```
If the code must be masked, keep the password type and the default transformation. Then provide a visible show/hide control that is labeled and keyboard-operable.

### 2. P2: the counter is announced with a deprecated API on every keystroke
- `announceForAccessibility` is deprecated in API 36. Announcements are not tied to the view, so they can't be localized or prioritized properly.
- Firing one on every character can collide with the typing feedback from the IME and TalkBack.
- "N of 6" doesn't say what is being counted.
- The counter starts as an empty `TextView`.

**Minimal fix:** remove `announceForAccessibility`. Make the counter a polite live region, set its initial text, and name the unit.
```kotlin
counter.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
counter.text = getString(R.string.digits_entered, 0, 6)   // e.g. "0 of 6 digits"
```
Consider whether the counter is needed at all. A visible "6 digits" label plus `LengthFilter(6)` may be enough.

### 3. P2: Back is the only way to dismiss the notice, and it won't run on Android 16
- With targetSdk 36, predictive back is always on. `onBackPressed()` is not called, so the dismiss branch is dead code on Android 16 devices. Back just finishes the activity.
- On older OS versions, the first Back press hides informational text with no visible control. Users then need a second press to leave. Keyboard and Switch Access users have no in-UI equivalent, and the behavior differs by OS version.

**Minimal fix:** delete the `onBackPressed` override, so Back always means "leave" and the notice stays put. If dismissal is a real requirement, add a visible, labeled Dismiss button. Optionally register an `OnBackInvokedCallback` only while the notice is visible.

### 4. P2: no edge-to-edge insets handling
With targetSdk 36, edge-to-edge is enforced and the opt-out is gone. The root `LinearLayout` applies no insets. The notice can sit under the status bar or a cutout, and the field or counter can sit under the navigation bar or IME. This is a visibility and reachability risk for all users, and it gets worse with large font scale or landscape.

**Minimal fix:**
```kotlin
root.setOnApplyWindowInsetsListener { v, insets ->
    val b = insets.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.ime() or WindowInsets.Type.displayCutout())
    v.setPadding(b.left, b.top, b.right, b.bottom)
    WindowInsets.CONSUMED
}
```
Setting `fitsSystemWindows` on the root is an alternative, but test its IME behavior.

### 5. P2: the label exists only as a hint
`hint` becomes the accessible name, but it disappears once text is entered. It's also less reliable for voice access and for users with cognitive or memory needs.

**Minimal fix:** add a visible `TextView` label with `labelFor = pin.id` (give the field an id). Keep the hint only as an example or format.

### 6. P3: other observations
- There's no submit control or IME action in the fixture. This may just be truncation. If it isn't, add `imeOptions = EditorInfo.IME_ACTION_DONE` and a real button.
- The 6-digit limit is only a counter today. `LengthFilter` in fix 1 enforces it.

## Coverage

### Automated
- **Lint and static checks:** flag the deprecated `announceForAccessibility` and `onBackPressed`, a missing `labelFor`, and a missing `autofillHints`.
- **Espresso with `AccessibilityChecks.enable()`:** catches touch target size, contrast, and missing names. It does not catch the password/plain-text conflict.
- **Instrumented test on an API 36 emulator:**
  - `createAccessibilityNodeInfo().isPassword` is false.
  - The input type has no password flag.
  - A `LengthFilter` of 6 is present.
  - The autofill hint is set.
  - The counter has a polite live-region mode.
  - `pressBack()` with the notice visible finishes the activity (or runs your intended handler).
  - Field and notice bounds don't intersect the system bar and IME insets. Run this at font scale 2.0, in landscape, and with the IME open.

### Device checks (not automatable)
- **TalkBack:**
  - What is spoken while typing, and whether the counter update interrupts it.
  - The field's name before and after text is entered.
  - Whether typed digits can be verified in the default and "speak passwords" settings.
  - The Back gesture and the notice.
- **Keyboard:** Tab order (notice, field, any button), a visible focus indicator, no keyboard trap, and a way to dismiss or ignore the notice.
- **Switch Access:** reach the field, enter digits through the IME, and reach submit. Confirm system Back works and that nothing depends on a hidden Back-only action.
- **Autofill:** SMS OTP suggestion and fill behavior.
- **Layout:** gesture and 3-button navigation, and large display size.
