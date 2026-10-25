# Review of `MessageThread.kt`

I reviewed the fixture as given and did not edit it. I did not assume any exact TalkBack speech.

## Findings

### 1. P1: The Undo prompt disappears after 3 seconds and isn't announced
- **Affected users:** TalkBack users, Switch Access users, and people with motor, cognitive, or low-vision needs who act slowly. Users who set Android's "Time to take action" preference are also affected.
- **Evidence:**
  - `LaunchedEffect(message.id) { delay(3_000); deleted = null }` removes the Undo prompt on a fixed timer.
  - The row has no live-region or announcement semantics.
  - The row is composed after the `LazyColumn`, so it's last in traversal order, far from the Delete button that triggered it.
  - `onDelete` has already run, so a missed Undo means the deletion is permanent.
- **Smallest fix:**
  - Replace the hand-rolled row with a Material3 `SnackbarHost`/`SnackbarHostState.showSnackbar(message, actionLabel = "Undo", withDismissAction = true, duration = SnackbarDuration.Long)`.
  - Alternatively, keep the custom row, add `Modifier.semantics { liveRegion = LiveRegionMode.Polite }`, and use a much longer or user-dismissable timeout.
- **Automated verification:**
  - Compose UI test: click Delete, advance `mainClock` by 3.5 s, and assert the Undo node still exists.
  - Assert that the live-region semantics or snackbar are present.
- **Real-device checks:**
  - With TalkBack, delete an item and confirm the state change is perceivable and Undo can be reached.
  - Repeat with Switch Access and with a raised "Time to take action" setting.

### 2. P1: The Terms and Privacy links are probably not operable without touch
- **Affected users:** TalkBack, Switch Access, and keyboard users. Users with low vision or color-vision deficiency are also affected.
- **Evidence:**
  - `ClickableText` with an offset-based `getStringAnnotations` handler uses a tap position. That gives non-touch input no obvious way to activate an individual link.
  - Only the `Color.Blue` span styling distinguishes the links from the surrounding text, and there is no underline. That is color alone.
  - The hard-coded color's contrast against the actual background and in dark theme isn't verified by the fixture.
  - `ClickableText` is also a legacy API.
- **Smallest fix:**
  - Use `Text` with `LinkAnnotation.Url` (or `LinkAnnotation.Clickable`) and a `TextLinkStyles` that adds an underline.
  - Take the color from the theme, for example `MaterialTheme.colorScheme.primary`, and route clicks to `onOpenUrl` via the `LinkInteractionListener`.
- **Automated verification:**
  - Compose test: assert the link semantics or custom actions exist and that invoking them calls `onOpenUrl` with the correct URL.
  - Contrast check of the link color in light and dark themes.
- **Real-device checks:**
  - With TalkBack, confirm each link can be discovered and activated, for example via the links/actions menu.
  - Confirm each link can be reached and activated with Switch Access and a hardware keyboard.
  - Test at large font scale.

### 3. P2: The read-receipts row has duplicated, ambiguous toggle semantics
- **Affected users:** TalkBack, Switch Access, and keyboard users.
- **Evidence:**
  - The `Row` is `clickable`, and the `Switch` also has its own `onCheckedChange`.
  - That gives two competing actions and click targets for one control.
  - The row has no `Role.Switch`, and the label isn't explicitly tied to the switch.
  - How the merged node is exposed to assistive tech depends on the merge behavior, so the fixture doesn't prove it's wrong. The duplication is still a maintainability and consistency risk.
- **Smallest fix:** Put `Modifier.toggleable(value = readReceipts, role = Role.Switch, onValueChange = onReadReceiptsChange)` on the row, and set `Switch(checked = readReceipts, onCheckedChange = null)`.
- **Automated verification:**
  - Compose test: `onNode(isToggleable())` finds exactly one node.
  - Assert the node has `Role.Switch`, includes the label text, and toggles when clicked.
- **Real-device checks:**
  - With TalkBack, confirm one focus stop with the label, state, and an action that toggles it.
  - Check Switch Access and keyboard toggling.

### 4. P2: Every Delete button has the same label and no message context
- **Affected users:** Screen reader users and voice-control users.
- **Evidence:**
  - Each row renders `TextButton { Text("Delete") }` with identical text.
  - The message `Text` and its button are separate, unassociated nodes.
  - Out of context, a screen reader user can't tell which message a button deletes. Voice Access "click Delete" is ambiguous.
- **Smallest fix:**
  - Give each button a unique accessible name that includes the message, for example with `semantics { contentDescription = ... }` built from a string resource.
  - Alternatively, expose Delete as a custom accessibility action on the row.
  - Keep the visible text "Delete" as the start of the accessible name so voice control still works.
- **Automated verification:** Compose test with two messages that asserts the Delete nodes have distinct names and each one calls `onDelete` with its own message.
- **Real-device checks:**
  - With TalkBack, navigate the list and confirm each Delete is distinguishable.
  - With Voice Access, confirm commands target the intended item.

### 5. P2: Focus isn't managed after delete or undo
- **Affected users:** TalkBack, Switch Access, and keyboard users.
- **Evidence:**
  - After `onDelete` the focused button's item is presumably removed. The code never moves focus to a sensible target.
  - `deleted` uses `remember`, not `rememberSaveable`. The Undo prompt is lost on configuration change, and so is the chance to undo.
- **Smallest fix:**
  - Move focus to the next item or to the Undo control.
  - Hold the pending-delete state somewhere that survives rotation, such as a ViewModel or `rememberSaveable` with the id.
- **Automated verification:** Compose test that deletes an item, recreates the activity, and checks the Undo state.
- **Real-device checks:** With TalkBack and a keyboard, delete the first, a middle, and the last item and watch where focus lands. Rotate during the Undo window.

### Not reported
- **Empty list:** An empty-list state isn't shown, and the fixture doesn't demonstrate a barrier from it.
- **Touch target size:** `TextButton` defaults to the Material minimum touch target.
