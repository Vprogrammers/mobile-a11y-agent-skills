**Scope:** Android Jetpack Compose only, one fixture (`OrderCard.kt`). The directory isn't a git repo, so there is no diff or history. I reviewed the code statically. I ran no builds, tests or devices, so nothing here is observed TalkBack, Voice Access or keyboard behavior. Line numbers count from the first line of the fixture.

**P1 — OrderCard.kt:11 (`clearAndSetSemantics` on the card Row)**
Affected users: TalkBack, Voice Access and Switch Access users. These users cannot reach or target "Track".
Evidence:
- `clearAndSetSemantics` replaces all descendant semantics (Android patterns reference).
- The "Track" `TextButton` (line 19) is a descendant of the Row, so its label and click action are hidden from the accessibility tree. The card exposes only a description string.
- A second independently operable action is therefore lost. Touch users can still tap it.
- Assumption: whether the outer `clickable` `onClick` survives on the card node depends on the Compose version. Confirm with `printToLog` on the merged and unmerged trees.
- Smaller issues: the description is hard-coded English that duplicates the visible text, and the card has no `Role`.

Criterion: WCAG 4.1.2 Name, Role, Value.
Fix:
- Drop `clearAndSetSemantics`.
- Keep Track as a real control. Either use `mergeDescendants = true` on the card and add `customActions` for Track, or split the card so Track is a sibling node.
- Give the action context, such as `onClickLabel` or a custom-action label "Track order ${order.number}", so several "Track" buttons are distinguishable.
- Move the strings to resources.

Verify:
- Automated: a Compose test asserting a node with a click action and the Track label or custom action exists, using `onNodeWithText(..., useUnmergedTree = true)` and `assertHasClickAction()`.
- Device: with TalkBack, check the Track action can be found and activated. With Voice Access, check "Track" can be spoken and the labels are unambiguous across cards.

**P1 — OrderCard.kt:8 (`indication = null`)**
Affected users: hardware-keyboard and Switch Access users with vision. Possibly low-vision touch users who rely on press feedback.
Evidence:
- `clickable(indication = null)` removes the default focus and press highlight on the card's primary action.
- Nothing else in the fixture draws a focus indicator, so this is proven by the code.
- The `remember`ed `MutableInteractionSource` adds nothing.
- Assumption: no theme-level or parent indication is applied elsewhere.

Criterion: WCAG 2.4.7 Focus Visible.
Fix: remove the `indication = null` and `interactionSource` arguments to use the default indication. If a custom look is wanted, supply an indication that draws a visible focused state.
Verify:
- Automated: a Compose test that requests focus on the card and asserts `isFocused()`. This does not prove the indicator is visible.
- Device: Tab through the screen with an external keyboard and with Switch Access. Confirm the focus position on the card is visible at 200% font and in dark theme.

**P2 — OrderCard.kt:~39 (`AddressForm` errors)**
Affected users: TalkBack, Switch Access and Voice Access users, plus users with cognitive disabilities.
Evidence:
- Errors are plain `Text` nodes beside the field.
- The field has no `isError` and no `supportingText`, and no `error()` semantics ties a message to it.
- There is no live region either, so nothing says an error appeared or which field it belongs to.
- Error identification relies on the text and its colour. The text is still readable, so the user can find it with extra navigation.

Criterion: WCAG 3.3.1 Error Identification.
Fix: pass `isError = errors.isNotEmpty()` and `supportingText = { errors.forEach { Text(it) } }`. Add `Modifier.semantics { error(errors.joinToString()) }` if the field doesn't expose the message. Use a debounced `liveRegion` only if errors appear asynchronously.
Verify:
- Automated: a test asserting the `Error` semantics property on the field.
- Device: submit an invalid form with TalkBack and check the user learns an error exists and where, without hunting through the screen.

**P2 — OrderCard.kt:~29 (`LaunchedEffect(errors)` + `requestFocus`)**
Affected users: keyboard and Switch Access users, and screen-reader users when the input focus change affects accessibility focus.
Evidence:
- Input focus is requested whenever the `errors` list content changes. That includes live validation while typing.
- This can pull focus away from the user's current position.
- The focus target is always the Street field, regardless of which field is in error.
- `requestFocus` controls input focus, not TalkBack accessibility focus. I do not claim TalkBack will follow it.
- Severity stays at P2 because the fixture has one field, so repeated focus loss isn't proven here. It would be P1 if a multi-field form re-triggers it.

Fix: request focus only on a submit-attempt event, and only for the first invalid field. Don't key it to the list identity or content.
Verify:
- Automated: a UI test that edits the field and checks focus doesn't change unexpectedly.
- Device: with TalkBack and a keyboard, submit with errors and then correct them. Confirm focus moves once, and only on submit.

**Blockers:** two P1 findings.
- `clearAndSetSemantics` hides the Track action.
- `indication = null` removes the visible keyboard and Switch Access focus.

**Device checks:**
- TalkBack on a real device with several order cards. Reach and activate Track, and confirm the card's own action still works.
- Voice Access: say "Track" and check the labels are unambiguous.
- External keyboard and Switch Access: confirm visible focus on the card and the Track button.
- Submit `AddressForm` with errors under TalkBack. Check error discoverability and focus behavior, at 200% font.

**Residual risk:**
- I did not run semantics trees or devices.
- The effect of `clearAndSetSemantics` on the outer `clickable` depends on the Compose version.
- The fixture omits the `Order` type and the screen host, so insets, headings, list keys and target sizes (`TextButton` is normally 48 dp) are unverified.
- I did not review locale, RTL or large-font layout, since the fixture sets no fixed heights or line limits.
