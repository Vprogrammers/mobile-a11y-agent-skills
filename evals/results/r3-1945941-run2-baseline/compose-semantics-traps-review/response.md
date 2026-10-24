# Review of `OrderCard.kt`

I reviewed the inline fixture only. I didn't edit anything or run any code. I found four defects, listed below.

## 1. P1: `clearAndSetSemantics` hides the Track button from accessibility services
- **Affected users:** TalkBack, Switch Access and Voice Access users, and anyone using accessibility-service-driven navigation.
- **Evidence:** `clearAndSetSemantics { contentDescription = ... }` sits on the `Row`, and the `TextButton(onClick = onTrack)` is a descendant of it. That modifier clears the semantics of all descendants. The "Track" button's click action, role and label are therefore removed from the accessibility tree. The card exposes only one `contentDescription` and the `clickable` action, which calls `onOpen`.
- **Severity note:** I rate this P1 because the fixture doesn't show whether tracking is reachable another way, such as from the order detail screen. If `OrderCard` is the only entry point to tracking, this becomes P0.
- **Smallest fix:** Replace `clearAndSetSemantics` with `Modifier.semantics(mergeDescendants = true) {}`. Keep the Track button as its own node, either by dropping the merge or by exposing Track as a `customActions` entry. The existing `Text` children already supply the order number and status, so the override isn't needed.
- **Automated verification:** In a Compose UI test, use `onNodeWithText("Track", useUnmergedTree = true)` and assert `assertHasClickAction()`. Then call `performClick()` and assert `onTrack` fired. Separately, assert that clicking the card fires `onOpen`.
- **Real-device checks:**
  - With TalkBack on, confirm you can reach and activate Track and the card separately.
  - Try Switch Access scanning and Voice Access on the same card.

## 2. P1: Address errors aren't tied to the field
- **Affected users:** Screen-reader users, and users who rely on the field's error state.
- **Evidence:** Errors render as loose `Text` siblings, colored with `colorScheme.error`. The `OutlinedTextField` has no `isError` or `supportingText`, and there's no error semantics or live region. The field itself doesn't expose an error state. Moving focus to the field doesn't make the error text part of the field's semantics.
- **Smallest fix:** Set `isError = errors.isNotEmpty()` and move the messages into `supportingText = { errors.forEach { Text(it) } }`. If custom layout is needed, use `Modifier.semantics { error(errors.joinToString()) }` on the field.
- **Automated verification:**
  - Assert `SemanticsProperties.Error` is present on the field when `errors` is non-empty and absent when it's empty.
  - Assert the error text is found inside the field's merged node.
- **Real-device checks:**
  - Submit an invalid form with TalkBack on and confirm the error is conveyed on the field.
  - Check that it is also conveyed when focus is elsewhere.
  - Don't depend on exact speech wording.

## 3. P2: Focus is requested on every `errors` change
- **Affected users:** Keyboard, switch and screen-reader users, and anyone typing.
- **Evidence:** `LaunchedEffect(errors)` calls `requestFocus()` whenever the list changes. If validation reruns as the user types, the list changes and focus is pulled back to the field. It also fires on first composition if errors already exist. Focus always goes to the street field, which is the only field in this fixture.
- **Smallest fix:** Trigger focus only on a submit or validation-failed event, such as a counter or one-shot event key. Don't key it on the list contents.
- **Automated verification:** Recompose with a new non-empty list and assert focus isn't re-requested. Assert focus moves once on a submit event.
- **Real-device checks:**
  - Type in the field with live validation and confirm the IME and focus don't jump.
  - Use external-keyboard Tab navigation.

## 4. P2: No visible pressed or focus feedback on the card
- **Affected users:** Keyboard, D-pad and switch users, and sighted users generally.
- **Evidence:** `clickable(indication = null, ...)` removes the ripple and the focus and press indication. The `Row` is a focusable, clickable target with no replacement visual state.
- **Smallest fix:** Remove `indication = null` and the custom `interactionSource`, or supply a visible indication. Add `role = Role.Button` or an `onClickLabel` such as "Open order".
- **Automated verification:** A test can assert the click action and role. Visible focus needs a screenshot test with the node focused.
- **Real-device checks:**
  - With a hardware keyboard or D-pad, confirm the focused card has a visible indicator.
  - Check contrast in light and dark themes.

## Minor note (not rated)
Several cards each show a "Track" button with the same label. Once finding 1 is fixed, a screen-reader user may hear identical names across a list. If that turns out to be a problem, consider a per-order label. The fixture doesn't demonstrate it, so I'd treat it as optional and P3 at most.
