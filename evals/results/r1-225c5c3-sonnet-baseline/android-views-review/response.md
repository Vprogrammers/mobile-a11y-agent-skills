# Accessibility review: `PaymentView.kt`

I reviewed the inline fixture only and made no edits. I didn't run anything, so none of this has been tested on a device.

## Failures

| # | Severity | Failure | Why it matters |
|---|---|---|---|
| 1 | **Critical** | The view has no accessibility semantics. It's a custom `View` that draws text and a circle on a canvas, so it exposes no text, no `contentDescription` and no role. | Screen readers can't read "Amount: N", and the circle is unlabeled. A TalkBack user gets no information about the amount or the control. |
| 2 | **Critical** | The only action is a raw `setOnTouchListener` that increments on `ACTION_UP`. It returns `true` and never calls `performClick()`. The view isn't declared clickable or focusable, and there is no `ACTION_CLICK` accessibility action. | TalkBack double-tap, Voice Access ("click …") and switch or keyboard activation all go through `performClick` or accessibility actions. None of them can increment the amount. Touch-only gestures exclude those users. |
| 3 | **High** | Keyboard and D-pad focus is missing: `isFocusable` is false, there is no key handling for Enter or Space, and there is no focus indicator. | Keyboard, switch and external-input users can't reach or operate the control. |
| 4 | **High** | The amount changes with no announcement and no state exposure, and `invalidate()` is never called. | The amount is drawn once, so the displayed text can go stale. A screen-reader user also never learns the value changed. |
| 5 | **Medium** | The touch target isn't sized. `onMeasure` isn't overridden, so the size comes from the parent. The circle has a 56px diameter, which is about 56dp only at mdpi (1x) density, and the code uses raw pixels. | The target may fall below the 48dp minimum, and the layout is density-dependent. |
| 6 | **Medium** | Drawing uses fixed pixel values, a text size left at the `Paint()` default, and hard-coded positions. | Text won't scale with the user's font-size setting, and it can clip at large font scales. The default paint color has unverified contrast against the background. |
| 7 | **Low** | `Paint()` objects are allocated on every `onDraw`. | This isn't an accessibility failure, but it's avoidable churn in a draw path. |
| 8 | **Low** | The circle's purpose is unclear. It looks like a button or indicator, but nothing says which. | It needs a name and role once it is exposed. |

## Minimal native fixes

Keep the custom view. Don't rewrite it as a `Button`.

1. **Make it a real, clickable control.** In `init`, set `isClickable = true` and `isFocusable = true`. Replace the touch listener with `setOnClickListener { amount++; update() }`. The click path then also handles TalkBack double-tap, Voice Access and keyboard Enter, and `performClick()` is called for you.
2. **Expose a name, role and state.**
   - Set `contentDescription` to something like "Amount, $amount" and refresh it whenever `amount` changes.
   - Use `ViewCompat.setAccessibilityDelegate` with `AccessibilityNodeInfoCompat` to set the role. `setRoleDescription` or `setClassName(Button::class.java.name)` works. Add `ACTION_CLICK` with a label such as "Increase amount".
3. **Announce changes.** Call `invalidate()` after the increment. Then call `announceForAccessibility`, or set `accessibilityLiveRegion = ACCESSIBILITY_LIVE_REGION_POLITE` on the view or a nearby label. Avoid duplicating the announcement if the live region already speaks.
4. **Fix the target size.** Override `onMeasure` with `resolveSize` and a minimum of `48.dp` converted to pixels. Alternatively, set `minimumWidth` and `minimumHeight`.
5. **Scale the drawing.** Use `TypedValue.applyDimension(COMPLEX_UNIT_SP, …)` for text size and dp for the circle geometry. Take colors from theme attributes and check contrast. Hoist the `Paint` objects into fields.
6. **Show focus.** Set a foreground or background selector, or draw a focus ring when `isFocused` is true.
7. **Decide the circle's role.** If it is decorative, set `importantForAccessibility` accordingly. If it is the tap target, make it part of the one labeled control instead of exposing it as a separate node.

## Test coverage

### Automated

These checks run without a device, or on an emulator:

- **Espresso with `AccessibilityChecks.enable()`** flags missing labels, small touch targets and, with an emulator or device, some contrast issues.
- **Instrumented tests** can assert these behaviors:
  - `performClick()` increments the amount.
  - `contentDescription` updates after each click.
  - `isClickable` and `isFocusable` are true.
  - The custom action is present on the `AccessibilityNodeInfo`.
  - The measured size is at least 48dp.
- **Lint** (`ContentDescription`, `ClickableViewAccessibility`) catches the touch-listener-without-`performClick` pattern.
- **Compose-style semantics tests** don't apply here, because this is the Views toolkit.

### Manual checks on a device

Automation can't judge the following:

- **TalkBack:**
  - The control is reachable by swipe navigation.
  - The name and role are understandable, and the state change is conveyed.
  - Double-tap activates it.
  - The live-region announcement is neither missing nor duplicated.
  - Don't assert exact speech strings. They vary by TalkBack version, locale and settings.
- **Voice Access:**
  - The control gets a usable on-screen label or number.
  - Saying "tap" with that label or number activates it.
  - A spoken name based on the label works.
- **Switch Access and keyboard:** Focus order, the visible focus indicator, and Enter or Space activation.
- **Display settings:** Large font scale, large display size, and high-contrast or dark themes, checking for clipping and contrast.
- **Touch exploration:** Make sure exploring by touch doesn't trigger the increment, which was a risk with the raw `ACTION_UP` listener.
