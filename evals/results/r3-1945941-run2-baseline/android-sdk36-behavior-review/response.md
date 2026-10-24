I reviewed the inline fixture only and didn't edit anything. I haven't run any of this on a device, and I make no claims about exact TalkBack speech.

## Findings

| # | Sev | Defect |
|---|-----|--------|
| 1 | **P1** | `onBackPressed()` is dead code on targetSdk 36. |
| 2 | **P2** | The code field has no persistent label. |
| 3 | **P2** | The field mixes a password input type with no masking. |
| 4 | **P2** | Per-keystroke `announceForAccessibility` on a deprecated API. |
| 5 | **P2** | The "x of 6" counter isn't enforced and isn't localizable. |
| 6 | **P2** | No edge-to-edge insets handling and no scrolling. |
| 7 | **P2** | Programmatic views have no IDs, so state isn't restored. |
| 8 | **P3** | No autofill hint and no IME action. |

### 1. Back handler never runs (P1)
- **Cause:** Apps targeting 36 get predictive back by default, and `Activity.onBackPressed()` isn't called. Back skips the override and finishes the activity.
- **Impact:** The only way the notice can be dismissed never fires. Keyboard and Switch Access users have no other route. If hiding the notice was ever needed, that function is unavailable with no alternative. Even where the override ran, hiding the focused view with `GONE` drops accessibility focus with no managed destination.
- **Minimal fix:** Prefer deleting the interception and leaving the notice as static text. If it must be dismissible, add a visible, focusable "Dismiss" button. A back callback can be a secondary route, not the only one:
  ```kotlin
  private val backCb = OnBackInvokedCallback { notice.visibility = View.GONE; pin.requestFocus(); backCb.isEnabled... }
  ```
  A simpler form is to register the callback with `onBackInvokedDispatcher.registerOnBackInvokedCallback(PRIORITY_DEFAULT, cb)` while the notice is visible. Unregister it when the notice is hidden, so Back works normally afterwards.

### 2. Hint-only label (P2)
- **Cause:** `hint = "One-time code"` is the only label for the field.
- **Impact:** The visible label vanishes once text is entered, which hurts low-vision and cognitive-load users. Assistive technology exposes hint text inconsistently.
- **Minimal fix:** Add a visible `TextView` label and link it with `label.labelFor = pin.id`. Keep the hint only as an example format.

### 3. Password input type without masking (P2)
- **Cause:** `TYPE_NUMBER_VARIATION_PASSWORD` combined with `transformationMethod = null`.
- **Impact:** Digits show on screen, but the node is still flagged as a password. Screen readers may then suppress character echo depending on user settings. That is probably why the author added the announcement in #4. Sighted and non-visual users get different feedback.
- **Severity note:** I rated this P2 because the hint says "one-time code". If this is a persistent PIN, as the class name suggests, showing it in clear text is a sensitive-data exposure and should be P0/P1.
- **Minimal fix:** Pick one behavior. Either use `TYPE_NUMBER_VARIATION_NORMAL` for an OTP, or keep it masked and add a labeled "Show code" toggle.

### 4. Announcements on every keystroke (P2)
- **Cause:** `announceForAccessibility` is called on every text change, including paste, autofill, and clears.
- **Impact:** The API is deprecated as of API 36 and unreliable. Announcements can interrupt the user's own typing feedback. The counter also isn't a live region.
- **Minimal fix:** Remove the call. If progress feedback is still wanted, set `counter.accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE` and update the text only when it changes meaningfully. Better still, fix #3 so normal text echo works.

### 5. Counter not enforced or localizable (P2)
- **Cause:** There's no `InputFilter.LengthFilter(6)`, and the strings are hard-coded.
- **Impact:** The counter can read "8 of 6". The wording "x of 6" doesn't say what is being counted. It also can't be localized, and the counter is blank until the first keystroke.
- **Minimal fix:** Add `filters = arrayOf(InputFilter.LengthFilter(6))`. Move the strings to resources, for example `"%1$d of %2$d digits entered"`. Set the initial state in `onCreate`.

### 6. Edge-to-edge and scrolling (P2)
- **Cause:** Targeting 36 means edge-to-edge is enforced, but the layout has no inset handling, no padding, and no `ScrollView`.
- **Impact:** The notice can sit under the status bar or cutout. The field can be covered by the keyboard. At large font scale or in split-screen, content clips.
- **Minimal fix:** Apply `setOnApplyWindowInsetsListener` padding for system bars and IME, and wrap the content in a `ScrollView`.
- **Severity note:** This rating is unverified. It becomes P1 if the field is actually occluded.

### 7. No view IDs (P2)
- **Cause:** The `EditText` and `TextView` are created in code without IDs.
- **Impact:** View state isn't saved, so rotation or a font-size change wipes the entry. The counter then disagrees with the field.
- **Minimal fix:** Call `View.generateViewId()` or use fixed resource IDs, and update the counter after restore.

### 8. No autofill hint or IME action (P3)
- **Cause:** There's no `setAutofillHints("smsOTPCode")` and no `imeOptions`.
- **Impact:** This is not a demonstrated barrier. The fixture has no submit or resend control, so I can't judge that flow.
- **Minimal fix:** Add `setAutofillHints(View.AUTOFILL_HINT_SMS_OTP)`, `imeOptions = EditorInfo.IME_ACTION_DONE`, and a submit path.

## Coverage split

**Automated**
- **Lint:** Check for `HardcodedText`, `LabelFor`, and deprecated-API use (`onBackPressed`, `announceForAccessibility`).
- **Espresso:** Enable `AccessibilityChecks.enable()` to flag missing labels and touch-target size.
- **Unit or instrumented assertions:**
  - The input type and transformation are consistent.
  - A 6-character length filter is present.
  - The counter's live-region mode is set.
  - No `announceForAccessibility` call is made (shadow `AccessibilityManager`).
  - The state is restored after `recreate()`.
- **Back on an API 36 emulator:** Run `pressBack` and assert the intended outcome, either activity finishing or notice dismissal. Cover the callback register and unregister paths.
- **Screenshots:** Capture at fontScale 2.0, with system-bar and IME insets, and in split-screen.

**Device checks (TalkBack, keyboard, Switch Access)**
- **TalkBack:**
  - Focus order is notice, then field, then counter.
  - The field's name is understandable both empty and filled.
  - Typed digits are acknowledged in some way, and which way depends on the #3 decision.
  - Progress updates are neither missing nor interrupting.
  - Focus lands somewhere sensible after the notice is hidden.
  - Paste and autofill behave sensibly.
- **Keyboard (hardware or ADB):** Tab and arrow traversal reach the field, the IME action works, and nothing is trapped.
- **Switch Access:** The field and any dismiss or submit control are reachable and operable, and the system Back action behaves as expected on Android 16.
- **Back gesture:** Check the predictive-back animation and where it leads.
