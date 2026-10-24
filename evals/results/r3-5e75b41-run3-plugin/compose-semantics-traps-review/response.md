Review of `evals/compose-semantics-traps-review/OrderCard.kt`. The scope is the pasted fixture only: Android Compose, with no git context and no builds run. I did not read or edit the file on disk. All findings come from static reading.

**P1 — OrderCard: `clearAndSetSemantics` on the card Row**
Affected users: TalkBack, Voice Access and Switch Access users. Keyboard-only users may also be affected.
Evidence:
- `.clearAndSetSemantics { contentDescription = ... }` sits inside `.clickable(...)`. Per the Android reference, it replaces all descendant semantics and hides them from accessibility services and tests.
- The "Track" `TextButton` is a descendant of that Row. That puts its role, label and `onTrack` action at risk of being removed from the accessibility tree. This is the Row-level "grouping that removes independently operable actions" pattern.
- The replacement description repeats the visible "Order N" and status text, so it adds nothing.
- The card also has no `Role`, so it is exposed as a generic clickable node rather than a button.
- Assumption: the exact merged tree depends on the Compose version. That is why it needs the `printToLog` check under Verify.

Criterion: WCAG 4.1.2 Name, Role, Value; 2.1.1 Keyboard (if the action is unreachable).
Fix:
- Remove `clearAndSetSemantics`.
- Keep the visible `Text` nodes as the card's name.
- If you want explicit grouping, use `semantics(mergeDescendants = true)` with `onClick(role = Role.Button)`. Then confirm "Track" stays a separate actionable node. If it doesn't, expose it as a `customActions` entry.

Verify:
- Automated: a Compose test comparing `printToLog` for the merged and unmerged trees. It should assert `onNodeWithText("Track").assertHasClickAction()` in the merged tree and that the card has a click action.
- Device: with TalkBack, swipe through one card and confirm "Track" is reachable and activates `onTrack`. Confirm the card still opens. Check Voice Access with "click Track".

**P2 — OrderCard: `indication = null` on `clickable`**
Affected users: Hardware keyboard and Switch Access users, and low-vision users who rely on focus or press feedback.
Evidence: `indication = null` with a fresh `MutableInteractionSource` removes the default focus and press highlight. Nothing else in the fixture draws a focus state. This matches the checklist signal for keyboard focus visibility.
Criterion: WCAG 2.4.7 Focus Visible; 1.4.11 Non-text Contrast.
Fix: Remove both the `interactionSource` and the `indication` arguments to get the default indication. If a custom style is needed, add a visible focus border driven by `collectAsState` on `isFocused`.
Verify:
- Automated: this is hard to assert in a semantics test, so use a screenshot test with the card focused.
- Device: Tab through the screen with a hardware keyboard and check that focus on the card is visible.

**P2 — OrderCard: ambiguous "Track" button across list items**
Affected users: TalkBack and Voice Access users who explore a list of orders.
Evidence:
- Each card has a "Track" button with identical text. Once the P1 is fixed, nothing in the button ties it to its order.
- Assumption: the card is used in a list. The fixture doesn't show that.

Fix: Add a `customActions` entry on the card, or use a label that keeps the visible word first, such as "Track order 123". Don't replace the label with unrelated text, because that breaks Voice Access matching.
Verify:
- Automated: a semantics test of the labels or actions across two cards.
- Device: with TalkBack, check that the actions are distinguishable. With Voice Access, check that "click Track" behaves sensibly when several orders are on screen.

**P2 — AddressForm: errors are not associated with the field or exposed as errors**
Affected users: TalkBack users, and low-vision users who may miss the errors.
Evidence:
- `OutlinedTextField` has no `isError` or `supportingText`.
- The errors are plain `Text` siblings with no `error()` semantics and no `liveRegion`.
- `LaunchedEffect` moves input focus to the Street field. That is not TalkBack accessibility focus and does not announce the errors.
- The only visual error cue is the red text color. The field itself shows no error state.

Criterion: WCAG 3.3.1 Error Identification; 1.4.1 Use of Color; 4.1.3 Status Messages.
Fix:
- Set `isError = errors.isNotEmpty()`.
- Put the message in `supportingText`, which carries error semantics.
- Add a concise `liveRegion` only if the errors arrive asynchronously.

Verify:
- Automated: a semantics test that asserts the error text and error state on the field node.
- Device: submit invalid data with TalkBack on. Check that the user can tell what failed and which field it belongs to. Don't assume what TalkBack says.

**P2 — AddressForm: `requestFocus()` keyed on `errors`**
Affected users: TalkBack, Switch Access and keyboard users. Anyone with a screen reader or switch device may lose their place.
Evidence:
- `LaunchedEffect(errors)` calls `requestFocus()` on every change to the list contents.
- It always targets Street, even though the fixture shows only one field.
- If validation runs while typing, which the fixture doesn't show, focus would be re-requested during editing.
- The checklist says to move focus only for meaningful context changes.

Fix:
- Trigger the focus move from a submit-attempt event rather than the error list.
- Target the first invalid field.
- Skip the focus request when the field is already focused.

Verify:
- Automated: a Compose test that submits invalid data and asserts focus lands once on the first invalid field. A second test should type into the field and assert that focus isn't re-requested.
- Device: TalkBack plus a hardware keyboard or Switch Access. Check for no focus jumps and no repeated keyboard pop-ups.

### Blockers
- The P1 above: the `clearAndSetSemantics` on `OrderCard` risks hiding the "Track" action from assistive technologies. The code proves the clearing, but the final merged tree needs confirmation.

### Device checks
- TalkBack on a real device: card traversal, "Track" reachability, and the form error flow after submit.
- Voice Access: "click Track" and the card's open action.
- Hardware keyboard or Switch Access: focus visibility on the card and focus behavior in the form.
- Font scale at 200%: check that the Row and the Track button reflow without clipping. The fixture shows no fixed heights, but this wasn't verified.

### Residual risk
- All findings are static. I did not confirm merged-tree behavior, Compose version differences, or actual TalkBack speech.
- The fixture is partial. I couldn't see how `OrderCard` is used in lists, how `AddressForm` validates, or whether there are other fields.
- Contrast of the error color and the touch target size of the default `TextButton` weren't evaluated. Both need a check in context.
