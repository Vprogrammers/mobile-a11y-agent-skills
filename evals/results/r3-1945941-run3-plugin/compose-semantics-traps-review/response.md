**Scope:** Android Jetpack Compose, reviewing `OrderCard` and `AddressForm`. `OrderCard.kt` is not on disk here (Glob found nothing) and the directory is not a git repo, so I reviewed only the inline fixture text. I ran no builds, tests or devices. I invoked the review and android-a11y skills directly because only the Skill tool was available, not the named agent.

```text
P1 — OrderCard.kt:OrderCard, Row modifier chain (clearAndSetSemantics)
Affected users: TalkBack, Voice Access and Switch Access users. Also any UI test or service that finds "Track" through semantics.
Evidence: The Row applies clearAndSetSemantics, which removes the semantics of all descendants. The TextButton("Track") is a descendant. Its button role, click action and "Track" text are therefore dropped from the accessibility tree. Tracking is a separate action with no other path in this composable. The Row keeps only one description, "Order N, status", plus the click that sits earlier in the modifier chain. Whether the outer click survives is expected from Compose behavior but not proven here. Check it in the semantics tree.
Criterion: WCAG 4.1.2 Name, Role, Value; 2.1.1 Keyboard. Useful here.
Fix: Replace clearAndSetSemantics with a merge that leaves the button independent. Move the clickable and semantics(mergeDescendants = true) onto the info Column, or onto a Box around it. Keep TextButton as a sibling. Add a Button role and onClickLabel to the card click. Optionally give Track an order-specific name, such as "Track order N", through semantics, so repeated "Track" buttons in a list are distinguishable.
Verify: Automated: compose test with printToString(useUnmergedTree = true), then assert onNodeWithText("Track") and hasClickAction(). Assert the card node has a click action. Device: with TalkBack, Voice Access and a switch or keyboard, reach and activate both Open and Track.

P2 — OrderCard.kt:OrderCard, clickable(indication = null)
Affected users: Hardware-keyboard and Switch Access users with sight. Also anyone who needs pressed-state feedback.
Evidence: The card's clickable removes the indication. Unless another focus style is added, the focused or pressed state has no visible cue. The card stays operable, so the task can still be done with more effort. Whether any other focus cue exists is an assumption. None appears in the fixture.
Criterion: WCAG 2.4.7 Focus Visible; 2.4.11.
Fix: Remove indication = null and the throwaway interactionSource. Use the default Material indication, or supply a visible focus border and pressed style.
Verify: Automated: no reliable semantics check. Use a screenshot test with focus forced if you have one. Device: Tab or arrow through the list with a keyboard and confirm a visible focus indicator on the card.

P2 — OrderCard.kt:AddressForm, errors list and LaunchedEffect(errors)
Affected users: TalkBack users, Voice Access users, and low-vision users who rely on association rather than color.
Evidence: Errors are plain Text in error color. They are not tied to the field through isError, supportingText or semantics error(). The field is not marked invalid. Color is the only cue linking the messages to the problem, apart from the text itself. LaunchedEffect calls requestFocus on the Street field for any non-empty errors, even if the errors concern other fields. It fires on each new errors list. This moves input focus, not TalkBack focus. Whether TalkBack follows it is device-dependent, and I make no claim about it. The messages are reachable by swiping, so the task is still completable.
Criterion: WCAG 3.3.1 Error Identification; 3.3.3; 1.4.1.
Fix: Pass isError = errors.isNotEmpty() and put the message in supportingText, or add semantics { error(msg) }. Only move focus to the first invalid field and only after a submit attempt. Don't re-request on every recomposition. Consider a polite liveRegion or an error summary for the submit result.
Verify: Automated: assert the field has the error semantics, for example SemanticsProperties.Error. Device: with TalkBack, submit invalid data and check that the error is discoverable at the field. Also confirm focus does not jump unexpectedly and the IME does not hide the error.
```

**Not flagged (checked, no defect shown):**
- `Icon(contentDescription = null)` inside `TextButton` is correct, because the button text names it.
- The `TextButton` has default Material target sizing, assumed to meet 48 dp. Confirm this on a device.
- `OutlinedTextField` has a label.

**Blockers**
- One P1: the nested "Track" action is hidden by `clearAndSetSemantics` on the card. No P0 found.

**Device checks**
- TalkBack: the card and Track are separate stops, and the order is logical. Don't assert exact speech.
- Voice Access: "Track" can be targeted. Several cards in a list may make the name ambiguous.
- Switch Access or hardware keyboard: both actions are reachable and a focus indicator is visible.
- Address form: submit with errors at 1.0x and 2.0x font scale, with the IME open.

**Residual risk**
- This is a static review of a fragment, with no semantics tree, tests or device evidence. The order and click behavior of the outer `clickable` relative to `clearAndSetSemantics` should be confirmed in the unmerged tree.
- The `Order` model, themes and callers are not visible. Error-to-field mapping and list keys are unknown.
