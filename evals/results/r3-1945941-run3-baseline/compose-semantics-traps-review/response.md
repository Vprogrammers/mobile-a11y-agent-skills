## Findings

### 1. P1: `clearAndSetSemantics` hides the "Track" button from assistive tech
- **Where:** `OrderCard`, the `.clearAndSetSemantics { contentDescription = ... }` on the `Row`, which also contains the `TextButton(onClick = onTrack)`.
- **Affected users:** TalkBack, Switch Access and Voice Access users. UI tests that query by semantics are affected too.
- **Evidence:** `clearAndSetSemantics` discards the semantics of all descendants. The `TextButton`, its "Track" text and its click action are all descendants, so none of them reach the accessibility tree. The fixture shows no other way to trigger `onTrack`.
- **Smallest fix:**
  - Replace `clearAndSetSemantics` with `semantics(mergeDescendants = false)`, or drop it.
  - Keep the label from the existing text ("Order N" and the status), which is already visible.
  - Keep `Track` as its own focusable button, so the card and the button are separate targets.
- **Automated verification:**
  - Compose UI test: `onNodeWithText("Track", useUnmergedTree = true).assertExists().assertHasClickAction()`, then `performClick()` and assert that `onTrack` was invoked.
  - Assert the card node still has a click action.
  - Run Accessibility Test Framework checks (`enableAccessibilityChecks()`).
- **Real-device checks:**
  - With TalkBack, swipe through a card and confirm both the card and Track are reachable and activatable.
  - Repeat with Switch Access and Voice Access ("click Track").

### 2. P1: Address errors aren't tied to the field and aren't announced
- **Where:** `AddressForm`, `errors.forEach { Text(...) }` next to an `OutlinedTextField` with no `isError` or `supportingText`.
- **Affected users:** Screen reader users, who get no error state on the field and no announcement of the messages.
- **Evidence:**
  - The field has no `isError` and no error semantics.
  - The messages are separate `Text` nodes with no live region.
  - The `LaunchedEffect` only moves focus to the field. The messages are siblings, so focus on the field doesn't convey them.
  - The fixture shows no other error announcement.
- **Smallest fix:**
  - Set `isError = errors.isNotEmpty()`.
  - Move the messages into `supportingText`.
  - Optionally add `Modifier.semantics { error(errors.joinToString()) }` on the field.
- **Automated verification:**
  - Compose UI test: with errors, assert the field has `SemanticsProperties.Error` (for example `SemanticsMatcher.keyIsDefined(SemanticsProperties.Error)`).
  - Assert the message text exists and the field is focused.
  - Assert there's no error semantics when `errors` is empty.
- **Real-device checks:**
  - Submit an invalid form with TalkBack on. Confirm the error state and message are discoverable and that you get an audible cue, without assuming exact wording.
  - Check at large font scale and with an external keyboard.

### 3. P2: `indication = null` removes press and focus feedback on the clickable card
- **Where:** `OrderCard`, `clickable(indication = null, interactionSource = remember { MutableInteractionSource() })`.
- **Affected users:** Keyboard, D-pad and Switch Access users, and low-vision users. They get no visible focus or pressed state on the card.
- **Evidence:** Indication is explicitly disabled, and no replacement focus or pressed styling appears in the fixture.
- **Smallest fix:** Remove both the `indication = null` and the custom `interactionSource` arguments to use the default ripple. Alternatively, supply a visible focus and press indication.
- **Automated verification:** Compose test that sends a focus request and asserts a focused state. The visual indicator itself needs a screenshot test.
- **Real-device checks:** Tab or D-pad to the card with a hardware keyboard and confirm a clearly visible focus indicator. Check contrast in light and dark themes.

### 4. P2: Focus is requested on every change to `errors`
- **Where:** `AddressForm`, `LaunchedEffect(errors) { ... requestFocus() }`.
- **Affected users:** Screen reader and keyboard users. This is conditional, because the fixture has only one field.
- **Evidence:**
  - The effect re-fires whenever the list content changes. With per-keystroke validation, this could re-pull focus.
  - In a form with more fields, it would pull focus away from the field the user is on.
  - It runs again on any recomposition that supplies a changed list.
- **Smallest fix:** Request focus only on a submit-triggered validation event, not on every list change.
- **Automated verification:** Test that changing `errors` while another element is focused doesn't move focus. Test that focus does move on submit.
- **Real-device checks:** With TalkBack, type in the field and confirm focus doesn't jump unexpectedly.

### 5. P3: Optional polish
- **Repeated "Track" label:** When several cards appear in a list, each "Track" button has the same visible text. This is not a demonstrated barrier. Any added `contentDescription` should include the visible word "Track" so Voice Access still matches it.
- **Missing role on the clickable card:** It sets no `Role` (for example `Role.Button`). Whether this matters depends on the intended announcement, so check it on a device rather than assuming.

## Notes
I didn't edit the fixture. I haven't run any of the tests above.
