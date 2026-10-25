# Review: `MessageThread.kt`

I reviewed the inline fixture only. I did not edit it. I did not assume any exact TalkBack speech, so the real-device checks list behaviors to observe.

## Findings

### 1. P1: The undo affordance is transient and not announced
**Affected users:** TalkBack and Switch Access users, keyboard users, and people with motor, cognitive or reading differences.

**Evidence:**
- The "Message deleted / Undo" row is a plain `Row` with no `liveRegion` or other semantics.
- `LaunchedEffect(message.id) { delay(3_000); deleted = null }` removes it after a fixed 3 seconds.
- The row appears at the end of the `Column`, after the list. A screen-reader user would have to find it and reach it within 3 seconds.

**Smallest fix:**
- Use `SnackbarHost` and `SnackbarHostState.showSnackbar(message, actionLabel = "Undo", withDismissAction = true, duration = SnackbarDuration.Long)`, or `Indefinite` plus a dismiss action. Material snackbars already carry accessibility semantics.
- If you keep the custom row, add `Modifier.semantics { liveRegion = LiveRegionMode.Polite }` and lengthen the timeout.
- Pause or extend the timeout while accessibility services are active.

### 2. P1: Policy links use `ClickableText`, so they are not exposed as links
**Affected users:** TalkBack, Switch Access and keyboard users. Low-vision users are also affected by points 2b and 2c below.

**Evidence:**
- `ClickableText` handles taps by character offset, so it is not exposed as separate, focusable links. Navigating to "terms" or "privacy policy" individually by keyboard, Switch Access or a TalkBack links rotor looks unsupported. This needs device confirmation.
- The only link styling is `SpanStyle(color = Color.Blue)`. There is no underline, so color is the only cue (2b).
- `Color.Blue` is hardcoded rather than taken from the theme, so contrast is unverified against dark or dynamic color schemes (2c). Pure blue on a dark surface is a likely failure.
- No `style` is passed to `ClickableText`, so it may not pick up the theme's text color. Confirm this on a device in dark theme.

**Smallest fix:**
- Replace `ClickableText` with `Text` and `LinkAnnotation.Url`. Pass `TextLinkStyles(SpanStyle(color = MaterialTheme.colorScheme.primary, textDecoration = TextDecoration.Underline))`.
- Route opening through `onOpenUrl` using a `LinkInteractionListener`, or the default URI handler.

### 3. P1: The read-receipts row has a duplicate, unlabeled control
**Affected users:** TalkBack and Switch Access users, and keyboard users.

**Evidence:**
- The `Row` is `clickable` and toggles the setting. The inner `Switch` also has its own `onCheckedChange`.
- That creates two separate actions for one setting.
- The label `Text` is not associated with the `Switch`, so the switch likely has no accessible name.
- The row has no `Role`, so the row and the switch each convey only part of the information (name versus state).

**Smallest fix:**
- Put `Modifier.toggleable(value = readReceipts, role = Role.Switch, onValueChange = onReadReceiptsChange)` on the `Row`.
- Set `Switch(checked = readReceipts, onCheckedChange = null)` so the row merges into one labeled control.

### 4. P2: Every "Delete" button has the same name and no row context
**Affected users:** Screen-reader, voice-control and switch users.

**Evidence:**
- Each row has a `TextButton { Text("Delete") }`, so every button has an identical name.
- Nothing ties a button to its message. Voice Access cannot tell the buttons apart ("click Delete" is ambiguous).
- After deletion the focused node disappears, and the fixture does nothing to manage focus.

**Smallest fix:**
- Give the button a distinguishing semantic description that includes the message body, for example `Modifier.semantics { contentDescription = "Delete: ${message.body}" }`. Keep the visible text "Delete" included in the description so Voice Access still works.
- Alternatively, expose a custom action on the row.
- After deletion, move focus deliberately, for example to the snackbar or the next item.

### 5. P2: The undo state is fragile
**Affected users:** Everyone, with the largest impact on assistive-technology users who need more time.

**Evidence:**
- `deleted` is only `remember`ed, so rotation or process recreation drops the pending undo even though `onDelete` has already fired.
- `deleted` holds a single message. Deleting a second message while the first undo is pending overwrites it, and the first one can no longer be undone.

**Smallest fix:**
- Use `rememberSaveable` with the message id, or hoist the pending-delete state.
- Better, defer the actual delete until the undo window closes.
- Queue undo events if multiple deletes should be supported.

### 6. P2: The "Undo" button colors against the inverse surface are unverified
**Affected users:** Low-vision users.

**Evidence:**
- The row background is `inverseSurface` and the message text uses `inverseOnSurface`.
- The `TextButton` keeps its default content color (`primary`), which is designed for normal surfaces, not the inverse surface.
- Contrast of "Undo" against the background is likely low and is not verified.

**Smallest fix:**
- Set `ButtonDefaults.textButtonColors(contentColor = MaterialTheme.colorScheme.inversePrimary)`. Using the Material `Snackbar` handles this automatically.

### 7. P3: The snackbar row shifts layout
- It is inserted into the `Column` below the list, so the list height changes when it appears and disappears. This is an optional improvement and no barrier is demonstrated. Overlaying it in a `Box` or `Scaffold` avoids the shift.

## Automated verification

Use Compose UI tests with `createComposeRule()`:
- **Undo timing:** Set `mainClock.autoAdvance = false`. Click Delete, then assert "Undo" exists and `onNodeWithText("Undo")` is still present after advancing 3,000 ms (or whatever policy you pick). Assert the live-region or snackbar semantics with `SemanticsMatcher.expectValue(SemanticsProperties.LiveRegion, LiveRegionMode.Polite)`.
- **Two quick deletes:** Delete A, then B, and assert both remain undoable (or that the policy is explicit).
- **Rotation or recreation:** Use `StateRestorationTester` and assert the pending-undo state survives.
- **Switch:** Assert exactly one node matches `isToggleable()`, that it has `Role.Switch`, and that its merged node includes "Send read receipts". Assert that a click toggles once.
- **Links:** Assert the link nodes expose link or click semantics, for example via `SemanticsProperties.LinkAnnotation`-based nodes or `performTextInput`-free `performClick` on the node. Check `onClick` is invoked with the expected URL.
- **Delete buttons:** Assert `onAllNodes(hasText("Delete"))` all have unique merged descriptions.
- **Accessibility Test Framework:** Call `enableAccessibilityChecks()` for touch targets, contrast and missing labels.
- **Themes and font scale:** Run with light, dark and large font scale, and check contrast on the link and Undo colors.

## Real-device checks

- **TalkBack:** Check whether the deletion and Undo are announced without moving focus. Check whether Undo is reachable by swipe navigation before it disappears. Check where focus lands after deletion. Check how the switch row is traversed (one stop or two). Check whether each link is individually reachable, for example via the links rotor.
- **Switch Access and keyboard (Tab, Enter and Space):** Activate each link, the toggle and Undo.
- **Voice Access:** Say "Delete" with several messages on screen, and check that the buttons can be told apart.
- **Display settings:** Test dark theme, dynamic color, 200% font scale and a narrow width. Check link visibility without color perception, for example grayscale.
- **Lifecycle:** Rotate the device with the Undo row visible.
- **System timing:** Check the system "time to take action" accessibility setting against the 3 second timeout.
