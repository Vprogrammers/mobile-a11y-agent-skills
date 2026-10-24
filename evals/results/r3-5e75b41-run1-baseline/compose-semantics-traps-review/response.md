# Review of `OrderCard.kt`

I reviewed the inline fixture only and did not edit it. Each finding below is supported by the code shown.

## 1. High: `clearAndSetSemantics` removes the Track button from accessibility

**Affected users:** TalkBack, Switch Access, Voice Access and external-keyboard users. Anyone who navigates by the semantics tree is affected.

**Evidence:**
- `clearAndSetSemantics { contentDescription = ... }` sits on the `Row` that contains `TextButton(onClick = onTrack)`.
- That modifier clears the semantics of all descendants, so the button's click action, its text "Track" and its button role are dropped from the tree.
- Only the row's description and the row's `onOpen` click remain. Assistive tech users can open an order but have no route to `onTrack`.
- The description also duplicates the text the two `Text` children already expose, so the override adds nothing.

**Smallest fix:** Delete the `.clearAndSetSemantics { ... }` line. `clickable` already merges the two child `Text` nodes into one focusable item, and the `TextButton` stays a separate node. Optionally add `onClickLabel = "Open order"` to `clickable`.

## 2. Medium: `indication = null` hides press and focus feedback

**Affected users:** Keyboard, D-pad and Switch Access users, who can't see which row has focus. Low-vision and sighted touch users also get no pressed state.

**Evidence:** `clickable(interactionSource = remember { MutableInteractionSource() }, indication = null, ...)` suppresses the default ripple and focus indication on the whole row. Nothing else in the fixture draws a focus or pressed state.

**Smallest fix:** Drop `interactionSource` and `indication` so `clickable` uses the defaults. Or keep a custom `indication` that shows focus and press.

## 3. Medium: Error state in `AddressForm` is not tied to the field

**Affected users:** Screen reader users, and sighted users who rely on more than colour.

**Evidence:**
- The errors are standalone `Text` siblings coloured with `colorScheme.error`.
- The `OutlinedTextField` has no `isError` and no `supportingText`.
- Focus is moved to the field, but nothing in the field's semantics marks it invalid or links it to its messages.
- A screen reader user landing on the field may hear only the label and value, not the errors. Sighted users see the errors only as separate red text.

**Smallest fix:** Pass `isError = errors.isNotEmpty()` and `supportingText = { errors.forEach { Text(it) } }` to the field. Optionally set `Modifier.semantics { error(errors.joinToString()) }`.

## 4. Low: Focus request re-fires whenever the `errors` instance changes

**Affected users:** Keyboard and screen reader users.

**Evidence:**
- `LaunchedEffect(errors)` is keyed on the `List` object.
- If the caller rebuilds an equal list on each recomposition or validation pass, the effect re-runs and calls `requestFocus()` again. That can pull focus back to the field mid-interaction.
- Whether this happens depends on the caller, which the fixture doesn't show.

**Smallest fix:** Key the effect on a stable value, such as a submit-attempt counter or `errors.isNotEmpty()`. Or `remember` the list by content.

## 5. Low: Repeated "Track" label has no order context

**Affected users:** Screen reader and Voice Access users in a list of many orders.

**Evidence:** Each card's button is labelled only by `Text("Track")`. The icon has `contentDescription = null`, which is correct, but each list item gets an identical button name.

**Smallest fix:** Add `Modifier.semantics { contentDescription = "Track order ${order.number}" }` to the button. This only matters once finding 1 is fixed. Voice Access users may need the visible text "Track" to stay in the label, so keep it at the start.

## Automated verification

Compose UI tests:
- **Finding 1:** Assert `onNodeWithText("Track").assertHasClickAction()` and `onNodeWithText("Track").performClick()` calls `onTrack`. This fails today. Also assert the row still exposes `onOpen`.
- **Finding 2:** Run `enableAccessibilityChecks()` for touch-target and clickable checks. Add a focus-state check that `performSemanticsAction(RequestFocus)` produces a visible focused state, via screenshot or semantics.
- **Finding 3:** Assert `onNodeWithText("Street")` has `SemanticsProperties.Error`. Assert the error text is displayed.
- **Finding 4:** Recompose with an equal but new list, and count focus requests via `onFocusChanged` or a test-injected `FocusRequester`. Assert focus is stable.
- **Finding 5:** Check that `onAllNodesWithText("Track")` nodes have distinct merged labels.

## Real-device checks

Check the results by behaviour, not exact speech:
- **TalkBack:** Swipe through a card. Confirm the Track button is reachable as a separate item and double-tap activates it. Confirm the row opens the order. After a failed submit, confirm the field's error is discoverable without hunting for sibling text.
- **Switch Access / Voice Access:** Confirm "Track" is selectable and "tap Track" works.
- **External keyboard:** Press Tab through the card and confirm a visible focus indicator on the row and the button. Press Enter or Space to activate each.
- **Font scale 200% and display size:** Confirm the row and button don't clip.
- **Focus behaviour:** Confirm repeated validation doesn't steal focus mid-typing.
