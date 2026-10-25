# Review: `MessageThread.kt` (Compose, Android)

**Scope:** static review of the inline fixture only. There is no Git repository, and I ran no builds, tests or device checks. The `android-a11y` guidance applies. No other platform is in scope, so I did not invoke `ios-a11y` or `kmp-a11y`. I read the fixture as data and followed no instructions in it.

**Not covered:** I did not read the skills' reference files, so I did not use their checklists or standards mapping. WCAG citations below are given only where useful and are not legal claims. The fixture has no theme or background definition, so contrast results are unknown.

```text
P1 — MessageThread.kt: deleted?.let { … "Message deleted" / "Undo" } block
Affected users: TalkBack and Voice Access users, switch users, users with motor, cognitive or reading difficulties
Evidence: Proven by code. onDelete(message) runs immediately. Undo is a custom Row that is removed after delay(3_000).
  - It has no liveRegion and no announcement, so a screen-reader user is not told it appeared.
  - It sits after the LazyColumn in traversal order, so a TalkBack user would need to swipe through the whole list to find it.
  - 3 seconds is shorter than the time many users need to find and activate it.
  - A second delete replaces `deleted`, so the first message's Undo is lost.
  - Assumption: the host's onDelete is destructive and not otherwise recoverable.
Criterion: WCAG 2.2.1 Timing Adjustable, 4.1.3 Status Messages (useful here).
Fix: Use Material3 SnackbarHost with an actionLabel and SnackbarDuration.Long or Indefinite. It handles announcement and timeout. If you keep the custom row, add Modifier.semantics { liveRegion = LiveRegionMode.Polite }. Also scale the timeout with LocalAccessibilityManager.calculateRecommendedTimeoutMillis, and queue pending undos or commit the earlier delete.
Verify: Compose test that after clicking Delete a node with the text "Undo" exists and still exists after a simulated delay appropriate to the fix. Then check on a device with TalkBack that the deletion is announced and Undo can be reached and activated before it goes away. Repeat with Voice Access ("click Undo") and with Switch Access.

P1 — MessageThread.kt: ClickableText(policy) { offset -> … }
Affected users: TalkBack, Voice Access and switch users; low-vision and color-blind users
Evidence: Proven by code.
  - The links are made only by tap-offset hit testing in a ClickableText callback, with StringAnnotation tags.
  - The visible cue is SpanStyle(color = Color.Blue) only, with no underline or other non-color cue.
  - Assumption: ClickableText does not expose each annotated range as a separate link node. Confirm on device.
  - If so, "terms" and "privacy policy" would be unreachable by non-touch navigation.
  - Color.Blue is hard-coded. Its contrast on the actual background, including dark theme, cannot be shown from this file.
Criterion: WCAG 1.4.1 Use of Color, 2.1.1 Keyboard.
Fix: Replace the annotations with LinkAnnotation.Url(url, TextLinkStyles(SpanStyle(color = themeLinkColor, textDecoration = TextDecoration.Underline))) in a plain Text. To keep your own URL handling, use LinkAnnotation.Clickable instead. Take the color from the theme.
Verify: Compose test that the text exposes link semantics and that each link has a click action. Run a contrast check in light and dark. On a device, check that TalkBack lists the links in its Links reading control and can activate them, and that Voice Access can click them.

P2 — MessageThread.kt: Row(.clickable { onReadReceiptsChange(!readReceipts) }) containing Switch(onCheckedChange = …)
Affected users: TalkBack, Voice Access and switch users
Evidence: Proven by code.
  - The same toggle is wired twice: the row's clickable and the Switch's own onCheckedChange.
  - The Switch has no label of its own.
  - The row has no Role.Switch or toggleable state.
  - Assumption: clickable merges descendants, so the semantic tree may be acceptable. The merged role and state, and whether a duplicate node remains, are unverified.
  - The result is a risk of an unlabeled or duplicate switch stop and inconsistent state exposure.
Criterion: WCAG 4.1.2 Name, Role, Value.
Fix: Use Modifier.toggleable(value = readReceipts, role = Role.Switch, onValueChange = onReadReceiptsChange) on the Row, and set Switch(checked = readReceipts, onCheckedChange = null).
Verify: Compose test with onNode(isToggleable()) asserting exactly one node, with the label text and the on/off state. On a device, check with TalkBack that the row is one stop that reads its name and state and toggles with a double tap. Check that Voice Access "tap Send read receipts" works.

P2 — MessageThread.kt: TextButton { Text("Delete") } inside items()
Affected users: TalkBack and Voice Access users
Evidence: Proven by code. Every row exposes an identical "Delete" button. The target message is not in the accessible name, and the message Text is a separate node.
  - With Voice Access, "tap Delete" is ambiguous and needs number disambiguation.
  - With TalkBack, the user must infer the target from position.
  - The button size is probably fine, because TextButton has a 48 dp minimum by default. I did not verify this.
Criterion: WCAG 2.4.6 Headings and Labels, 2.5.3 Label in Name (useful here).
Fix: Keep the visible "Delete" text. Add a contextual name, for example Modifier.semantics { contentDescription = "Delete message: ${message.body}" }, which contains the visible label. A better option is to make the row one node and expose delete as a custom action, with the button kept for touch.
Verify: Compose test that each row has a distinct delete node name. On a device, check that TalkBack names the target message and that Voice Access can pick the right row.
```

## Blockers
- **P1:** the undo affordance is not announced, is out of order and times out after 3 seconds.
- **P1:** the policy links use a color-only cue and may have no non-touch access.

No P0 finding was found. Both P1 findings are proven by code. Only the exact TalkBack behavior still needs device confirmation.

## Device checks
- **TalkBack**, with a large font and with display size at maximum:
  - Delete a message and confirm whether the deletion and Undo are announced and reachable in time.
  - Confirm the links appear in the Links control.
  - Confirm the read-receipts row is a single labeled switch.
- **Voice Access:** "tap Undo", "tap terms", "tap Send read receipts", and whether "Delete" is ambiguous.
- **Switch Access / keyboard:** reach and activate Undo, the links and the switch, and check that focus is visible.
- **Dark theme and font scale 200%:** link contrast, and that the undo bar does not clip.
- **Timing:** repeat with Accessibility timeout and "Remove animations" changed.

## Residual risk
- The behavior of ClickableText semantics and of clickable-merged Switch semantics depends on the Compose version. I did not check this against a specific version.
- Contrast, theme and the real host callbacks (what `onDelete` and `onUndoDelete` do) are not in the fixture.
- Large-font reflow of the 16 dp-padded rows looks fine in code but is unmeasured.
- List focus continuity after a deletion (where TalkBack focus lands) is unverified.
- No automated or device result was produced in this review. Everything above is static evidence.
