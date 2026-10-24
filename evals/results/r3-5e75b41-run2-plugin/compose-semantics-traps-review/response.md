**Scope:** I reviewed the inline fixture text, because `evals/compose-semantics-traps-review/OrderCard.kt` is not on disk in this working directory. There is no git repository, so I ran no git commands. The platform is Android Jetpack Compose. I did not edit anything or run any build. I also could not delegate to the `accessibility-reviewer` agent, because no agent tool is available here. This review follows the `mobile-a11y-review` and `android-a11y` skills instead.

## Findings

```text
P1 — OrderCard.kt: OrderCard, Row modifier chain (.clearAndSetSemantics)
Affected users: TalkBack, Voice Access and Switch Access users, and anyone using keyboard or other accessibility-service navigation.
Evidence: The Row applies `clearAndSetSemantics { contentDescription = ... }`.
  That API discards the semantics of all descendants.
  The `TextButton(onClick = onTrack)` is a descendant, so its button role, "Track" label and click action are removed from the accessibility tree (proven by code).
  The Track action then has no accessible path, and there is no alternative custom action.
  Unproven assumption: whether the row's own `onOpen` click action survives depends on the modifier order of `clickable` and `clearAndSetSemantics`.
  I have not confirmed the merged tree.
Criterion: WCAG 4.1.2 Name, Role, Value; 2.1.1 Keyboard.
Fix: Delete `clearAndSetSemantics`.
  `clickable` already merges the row's text into one node.
  The Track button should stay a separate, independently operable node.
  Add `role = Role.Button` and an `onClickLabel` such as "Open order" to the `clickable`.
  If a custom summary is still needed, set it with `semantics(mergeDescendants = true)` and without clearing children.
Verify: Compose semantics test.
  Use `onNodeWithText("Track").assertHasClickAction()`.
  Assert that the order row has a click action.
  Print `onRoot(useUnmergedTree = false).printToLog` to inspect the merged tree.
  Then check with TalkBack and Voice Access ("click Track") on a device that both the row and Track are reachable and activate the correct callbacks.
```

```text
P2 — OrderCard.kt: OrderCard, clickable(indication = null)
Affected users: Keyboard, D-pad and Switch Access users, and sighted users who need a visible press or focus cue.
Evidence: `indication = null` with a fresh `MutableInteractionSource` removes the default ripple and focus indication from a clickable row (proven by code).
  Whether a replacement focus cue exists elsewhere is not shown in the fixture.
Criterion: WCAG 2.4.7 Focus Visible; 1.4.11 Non-text Contrast.
Fix: Remove both arguments to use the default indication.
  If a custom style is required, draw an explicit focused/pressed state from a shared `InteractionSource`.
Verify: Test on a device or emulator with a hardware keyboard.
  Tab to the row and confirm a visible focus indicator.
  A screenshot test with forced focus can cover regressions.
```

```text
P2 — OrderCard.kt: AddressForm, error rendering
Affected users: TalkBack, Voice Access and low-vision users.
Evidence: The errors are plain `Text` nodes placed after the field.
  The field sets no `isError` and no `supportingText`.
  No live region or other announcement is tied to the field (proven by code).
  The error is therefore not programmatically associated with the Street field.
  The only visual error cue is red text color.
  The message itself is text, so meaning is not color-only.
  Whether TalkBack announces anything when the errors appear is device-dependent.
Criterion: WCAG 3.3.1 Error Identification; 4.1.3 Status Messages.
Fix: Pass `isError = errors.isNotEmpty()` to `OutlinedTextField`.
  Move the message into `supportingText`.
  Add `Modifier.semantics { liveRegion = LiveRegionMode.Polite }` only on the error container if it appears after submit.
Verify: Semantics test that the field has an error state and the message is in the merged node.
  Then use TalkBack on a device to submit invalid input and check that the error is discoverable and not announced twice.
```

```text
P2 — OrderCard.kt: AddressForm, LaunchedEffect(errors) { requestFocus() }
Affected users: TalkBack, keyboard and switch users; also anyone with a motor or cognitive disability.
Evidence: Each change to `errors` forces input focus to the Street field (proven by code).
  The fixture contains only that field, so it is the right target today.
  The effect would send focus to the wrong place once more fields are added, and it can re-steal focus when the error content changes.
  This is Compose input focus, not TalkBack accessibility focus.
  Compose has no stable public API to move TalkBack focus, and `requestFocus` does not guarantee it moves.
  It may also open the IME unexpectedly.
Fix: Focus only the first invalid field, and only after a submit attempt.
  Keep error text reachable through the field semantics from the previous finding.
Verify: Compose test that focus lands on the first invalid field after submit and does not move while typing.
  Device check with TalkBack and the IME to see what the user hears and where focus goes.
```

## Blockers
**P1:** `clearAndSetSemantics` hides the Track button from assistive technologies.

## Device checks
- **TalkBack:** swipe through an order card.
  Confirm one row node and a separate Track button, with correct activation of each.
- **Voice Access:** say "click Track" and "click order". Check that the labels and numbers appear.
- **Keyboard or Switch Access:** tab to the row and Track and check that focus is visible.
- **Address form on a device:** submit invalid input with TalkBack.
  Check the focus target, whether the error is discoverable, and the IME behavior.
- **Display settings:** check large font, dark theme and RTL.

## Residual risk
- The fixture is partial, so I could not check the unseen parts of `Order` and the surrounding screens.
- The effect of modifier order on the row's click semantics is unconfirmed.
- Exact TalkBack speech is not assumed anywhere in this review.
- I did not evaluate touch target size, contrast values or font scaling, because the fixture does not show them.
