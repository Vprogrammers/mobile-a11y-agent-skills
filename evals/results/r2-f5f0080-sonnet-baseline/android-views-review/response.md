# Review of `PaymentView.kt`

I reviewed the inline fixture only and didn't edit it. Findings are ordered by severity.

## Failures

| # | Severity | Failure | Minimal native fix |
|---|---|---|---|
| 1 | **Critical** | **Touch-only activation.** The only input is `setOnTouchListener`, which returns `true` and never calls `performClick()`. TalkBack's double-tap, Switch Access, keyboard Enter and Voice Access "tap" send `ACTION_CLICK` or key events, not raw touches. The view is also not `isClickable` or `isFocusable`. Assistive-tech users can't increment the amount at all. | Replace the touch listener with `setOnClickListener { amount++; invalidate(); … }`, and set `isClickable = true` and `isFocusable = true`. Or use a real `Button`/`MaterialButton` plus a `TextView`. |
| 2 | **Critical** | **No accessible name, role or value.** `onDraw` renders "Amount: N" and the circle as pixels. The view has no `contentDescription`, `stateDescription` or `AccessibilityNodeInfo` override, so assistive tech gets an unlabeled node, or none. Voice Access has no label to show or speak. | Prefer native widgets. If the custom view stays, set a `contentDescription` for the action, such as "Increase amount". Expose the value through `stateDescription`, or use `ViewCompat.setAccessibilityDelegate` to set `className = Button::class.java.name`. Add a label for the click action with `ViewCompat.replaceAccessibilityAction(...)`. |
| 3 | **High** | **Value changes aren't communicated, and the view never redraws.** `amount++` doesn't call `invalidate()`, so even the visual text goes stale. There is no live-region or state update, so screen reader users get no feedback. | Call `invalidate()`. Update `stateDescription` on each change, or set `ViewCompat.setAccessibilityLiveRegion(this, ACCESSIBILITY_LIVE_REGION_POLITE)`. Avoid `announceForAccessibility`. |
| 4 | **High** | **Text doesn't scale.** `drawText` uses a default `Paint` (about 12px) with hard-coded pixel coordinates. It ignores sp and font scale, and the text can clip at large font or display sizes. The view also has no `onMeasure`. | Set `textSize` from `TypedValue.applyDimension(COMPLEX_UNIT_SP, …)`. Implement `onMeasure` from the text bounds (`paint.fontMetrics`) and the minimum target size. Better still, use a `TextView`. |
| 5 | **Medium** | **Touch target may be too small.** The circle is 56px in diameter (28px radius), which is under 48dp on most devices. Nothing in the view guarantees a hit area. | Enforce `minimumWidth` and `minimumHeight` of 48dp in `onMeasure`. Use dp-based dimensions, or `TouchDelegate`. |
| 6 | **Medium** | **Color and state.** `Paint()` defaults to black with no theme or dark-mode awareness, which can be unreadable on a dark background. There is no pressed or focus visual, so keyboard and switch users can't see where focus is. | Resolve colors from theme attributes. Give the view a `foreground` or background ripple/selector (`?attr/selectableItemBackground`) so it draws focus and pressed states. |
| 7 | **Medium** | **Payment error prevention.** The amount changes on `ACTION_UP`, with no `ACTION_CANCEL` handling and no way to decrement or correct. | Moving to click handling fixes the cancel case. Add an explicit decrement or edit control, plus a review/confirm step before payment. |
| 8 | **Low** | **The circle's purpose is undefined.** If it is the tap affordance, it needs the name and role from #2. If it is decorative, mark it so. | Set `importantForAccessibility` deliberately. |

`Paint()` is also allocated on every `onDraw`. That isn't an accessibility issue, but you should hoist it to a field.

## Coverage

**Automated (catches the structure, not the experience):**
- Android Lint `ClickableViewAccessibility` flags the touch listener without `performClick`. Lint also flags a missing `contentDescription`.
- Espresso `AccessibilityChecks.enable()` (Accessibility Test Framework) covers missing speakable text, touch target size and, to a degree, contrast.
- A Robolectric or instrumented unit test can check four things:
  - `performClick()` increments `amount`.
  - The node info's `className`, text/description/state and `ACTION_CLICK` are present.
  - `isClickable` and `isFocusable` are true.
  - The state description updates after a click.

**Manual on device (needed, and I'm not predicting exact speech):**
- **TalkBack:** Swipe focus reaches the control. Check that a name, role and current value are conveyed, and that they make sense. Double-tap increments, and the new value is conveyed without re-navigating.
- **Voice Access:** The control gets a visible label or number, and "tap <label>" works.
- **Switch Access and keyboard:** Focus is reachable, a visible focus indicator shows, and Enter/Space activates.
- **Display:** Test at the largest font and display size, in dark mode, and at small screen widths. Check for clipping and for target size.
- **Behavior:** Cancelling a touch by dragging off doesn't change the amount, and the payment flow offers a way to correct a mistake.
