# Review: `MessageThread.kt`

I read the fixture only and ran nothing. Findings are ordered by severity, and I found no P0 defects.

## P1-1: Policy links are unreachable without touch (`ClickableText`)

- **Affected users:** TalkBack, Switch Access, keyboard/D-pad and Voice Access users. Low-vision users are also affected, because the links are marked by color only.
- **Evidence:**
  - `ClickableText` activates links from a tap offset, using `getStringAnnotations(offset)`. That exposes no per-link semantics, so assistive tech has no link nodes to focus or activate.
  - The only visual cue is `SpanStyle(color = Color.Blue)`, with no underline. That is color-only (WCAG 1.4.1). The hard-coded color also ignores the theme, so contrast in dark mode is unverified.
  - `ClickableText` is a legacy API.
- **Smallest fix:**
  - Build the text with `LinkAnnotation.Url`/`withLink`, or `LinkAnnotation.Clickable` if the callback must stay `onOpenUrl`.
  - Pass `TextLinkStyles` with an underline and theme colors.
- **Automated verification:**
  - Compose UI test that finds each link node, performs a click, and asserts `onOpenUrl` receives the expected URL.
  - Accessibility Test Framework checks via `enableAccessibilityChecks()`.
  - Screenshot test in light and dark themes that asserts the underline.
- **Real-device checks:**
  - TalkBack: confirm both links can be found and activated, for example through the links rotor or actions menu.
  - Switch Access and keyboard: confirm both links are reachable and activatable.
  - Check contrast in dark theme and at 200% font scale.

## P1-2: The undo bar is transient, unannounced and unreachable in time

- **Affected users:** TalkBack, Switch Access and keyboard users, and users with motor or cognitive impairments who need more than 3 seconds.
- **Evidence:**
  - `onDelete` fires immediately, and `LaunchedEffect` + `delay(3_000)` removes the bar. Undo is the only recovery.
  - The bar is a plain `Row` with no `liveRegion` or other announcement, so non-visual users may never learn it appeared.
  - Focus does not move to it, and it is appended after the list. Reaching it by swipe or scan traversal within 3 seconds is unlikely.
  - The delay ignores the user's accessibility timeout preference.
- **Smallest fix:**
  - Use Material `SnackbarHost`/`SnackbarResult` with an action and `SnackbarDuration.Long` or `Indefinite`. It announces itself and respects the recommended accessibility timeout.
  - Alternatively, keep the custom bar, add `Modifier.semantics { liveRegion = LiveRegionMode.Polite }`, and lengthen or remove the auto-dismiss.
- **Automated verification:**
  - Compose test with `mainClock.autoAdvance = false`. Advance past 3000 ms and assert the Undo node still exists (or follows the chosen policy).
  - Assert the live-region semantics or the snackbar message.
  - Assert the click calls `onUndoDelete`.
- **Real-device checks:**
  - With TalkBack, delete an item and confirm the deletion is announced and Undo can be reached and activated.
  - Repeat with Switch Access scanning.
  - Set "Time to take action" to its longest value and confirm the timing follows it.

## P2-1: Every "Delete" button has the same name

- **Affected users:** TalkBack and Voice Access users, and anyone navigating buttons out of context.
- **Evidence:** Each row renders `TextButton { Text("Delete") }` with no reference to `message.body`. In a list, N identical controls are indistinguishable, and a voice command like "tap Delete" is ambiguous.
- **Smallest fix:**
  - Give the button a per-item `contentDescription` or `semantics`. A stringResource with the message text is better than a fixed string for localization.
  - Alternatively, put a custom accessibility action on the row.
  - Truncate long bodies in the description.
- **Automated verification:**
  - Compose test with two messages. Assert the delete nodes have distinct names or actions.
  - Assert each click calls `onDelete` with the right message.
- **Real-device checks:**
  - TalkBack: swipe through several rows and confirm each Delete is distinguishable.
  - Voice Access: confirm numbered or labeled targets resolve to the correct row.

## P2-2: The read-receipts row duplicates click handlers and lacks Switch semantics

- **Affected users:** TalkBack, Switch Access and Voice Access users.
- **Evidence:**
  - The row has `clickable { onReadReceiptsChange(!readReceipts) }`, and the nested `Switch` also has `onCheckedChange`. That is two independent toggle paths.
  - The row has no `Role.Switch`.
  - How the merged node's label, state and role resolve depends on semantics merging. Verify this on a device and don't assume it.
- **Smallest fix:**
  - Use `Modifier.toggleable(value = readReceipts, role = Role.Switch, onValueChange = onReadReceiptsChange)` on the row.
  - Set the `Switch`'s `onCheckedChange = null`.
- **Automated verification:**
  - Compose test: `onNode(isToggleable())` asserts exactly one toggleable node, `assertIsOff()` / `assertIsOn()`, and a click toggles once and calls the callback once.
  - Assert the Switch role.
- **Real-device checks:**
  - TalkBack: confirm one focus stop with label, state and role.
  - Confirm the whole row is a touch target of at least 48dp.
  - Toggle with Switch Access.

## P2-3: Undo state is fragile

- **Affected users:** All users, most visibly those who rotate the device or delete quickly.
- **Evidence:**
  - `deleted` is held in `remember`, so rotation or process recreation clears it. The message is already gone via `onDelete`, so undo is lost.
  - A single slot holds one `Message`, so a second delete within 3 seconds replaces the first and its undo is lost permanently.
- **Smallest fix:**
  - Hoist pending-delete state into the ViewModel or caller, or store the ID with `rememberSaveable`.
  - Queue the pending deletions, or defer the real deletion until the undo window ends.
- **Automated verification:**
  - Compose test with `StateRestorationTester`: delete, restore state, and assert Undo is still offered.
  - Test deleting A then B and assert A remains recoverable, or that the chosen policy is documented.
- **Real-device checks:** Rotate during the undo window and delete two rows in quick succession.

## Not reported

I didn't report empty state, list performance or `key` usage. The fixture shows no demonstrated barrier there. I also made no claims about exact TalkBack speech.
