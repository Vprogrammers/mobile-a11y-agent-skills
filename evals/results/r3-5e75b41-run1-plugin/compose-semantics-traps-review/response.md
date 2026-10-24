# Review: `OrderCard.kt` (`OrderCard`, `AddressForm`)

**Scope:** Android Jetpack Compose, static review of the inline fixture. I treated it as data. I ran no builds or tests, and the `evals/...` path was not read from disk. Nothing was edited. The KMP and iOS skills don't apply because no shared or iOS code is present.

## Findings

**P1 — OrderCard.kt:`OrderCard` (`clearAndSetSemantics` on the Row)**
Affected users: TalkBack, Voice Access and Switch Access users. Anyone using an accessibility service that depends on the semantics tree.
Evidence (proven by code):
- `clearAndSetSemantics` drops the semantics of all descendants.
- The `Track` `TextButton` is a descendant, so its click action and "Track" label are removed from the tree.
- Only the Row's merged description, "Order N, status", remains.
- That leaves "Track" without an accessible node, and Voice Access can't target "Track".
- Assumption: whether the Row's own `onOpen` click survives depends on the order in which same-node modifiers are processed. Confirm this with a semantics test.

Criterion: WCAG 4.1.2 Name, Role, Value; 2.1.1 Keyboard.
Fix:
- Remove `clearAndSetSemantics`.
- Put `Modifier.semantics(mergeDescendants = true)` on the text `Column`, or use `clickable` with `onClickLabel`.
- Keep `TextButton` as its own sibling node outside the clickable area.
- Preferably make only the `Column` clickable, so "open" and "track" are two separate nodes.

Verify:
- **Automated:** a Compose test with `onNodeWithText("Track").assertHasClickAction()` and a check that the open action exists.
- **Device:** TalkBack swipe traversal reaches both actions, and Voice Access "click Track" works.

**P2 — OrderCard.kt:`OrderCard` (row `clickable`)**
Affected users: keyboard, D-pad and Switch Access users, and low-vision users who need to see focus. TalkBack users also lose the role.
Evidence:
- `indication = null` removes the press and focus indication from a custom interactive row.
- There is no `role = Role.Button` and no `onClickLabel`.
- The row's visible text is overridden by a hand-written `contentDescription`. This is redundant once merging is used, and it doesn't localize or follow the visible text.

Criterion: WCAG 2.4.7 Focus Visible; 1.4.11 Non-text Contrast, if a focus indicator is added.
Fix: Restore the default indication, or supply a visible focus style. Add `role = Role.Button` and a meaningful `onClickLabel`. Let the merged visible text provide the name.
Verify:
- **Automated:** a semantics test asserting the role.
- **Device:** with a hardware keyboard, Tab onto the row and confirm the focus indicator is visible.

**P2 — OrderCard.kt:`AddressForm` (`LaunchedEffect(errors)` + `requestFocus`)**
Affected users: TalkBack and keyboard users, and users with motor or cognitive disabilities.
Evidence:
- `requestFocus()` moves input focus, not TalkBack accessibility focus. It does not announce the error.
- It re-runs whenever the `errors` list instance changes.
- If a new list is created on each validation pass, focus and the IME are repeatedly pulled back to Street while the user is elsewhere or typing. That repeat depends on how the caller builds `errors`, which the fixture doesn't show.

Criterion: WCAG 3.3.1 Error Identification; 3.2.2 On Input.
Fix:
- Key the effect on a one-shot "submit failed" event, not the list identity.
- Focus the first invalid field only after a submit attempt.
- Don't steal focus on live validation.

Verify:
- **Automated:** a Compose test that recomposes with an equal-content new list and asserts focus is not re-requested.
- **Device:** TalkBack with IME active, confirming what is announced after a failed submit.

**P2 — OrderCard.kt:`AddressForm` (error `Text` rows)**
Affected users: TalkBack users and screen magnifier users.
Evidence:
- The errors are plain `Text` below the field.
- The text field has no `isError = true` and no `supportingText`.
- Nothing links the errors to the field, and nothing exposes them as an asynchronous update.
- The errors are not color-only, because they have text.
- Assumption: the errors are not announced when they appear. Confirm this on a device.

Criterion: WCAG 3.3.1; 4.1.3 Status Messages.
Fix:
- Set `isError = errors.isNotEmpty()`.
- Pass the message through `supportingText`.
- Optionally add `Modifier.semantics { error(errors.first()) }` on the field.
- Use `liveRegion = LiveRegionMode.Polite` on the error container if no field-level semantics are used.

Verify:
- **Automated:** a test asserting the error semantics are on the field.
- **Device:** TalkBack reads the error when the field gets focus or when validation fails.

## Blockers
- P1: `clearAndSetSemantics` removes the accessible `Track` action.

## Device checks
- TalkBack: swipe order and available actions on an order card. Check that "Track" and the open action can each be activated.
- Voice Access: "click Track" and "click order".
- Switch Access and keyboard: focus visibility and reachability of both actions.
- TalkBack with large font (200%): the card layout and error text.
- The form: failed submit, with IME and TalkBack, checking focus placement and error reading.
- I made no assumptions about exact TalkBack speech.

## Residual risk
- The `clickable` and `clearAndSetSemantics` interaction on the same node needs a semantics-tree dump to confirm.
- How `errors` is created is outside this fixture, so the repeated-focus severity may differ.
- Touch targets, contrast and font scaling are not evidenced in this code. `TextButton` normally meets the 48 dp minimum.
