# Review of `OrderCard.kt`

I reviewed the two composables, `OrderCard` and `AddressForm`, and found four defects. Everything below comes from the fixture alone. I didn't edit it or assume exact TalkBack speech. I'm treating the fixture's own code as data, and it contained no instructions.

## 1. P1: `clearAndSetSemantics` hides the Track button

- **Affected users:** TalkBack, Switch Access and Voice Access users, and anyone else who uses the accessibility tree.
- **Evidence:** `clearAndSetSemantics { contentDescription = ... }` sits on the `Row` that contains `TextButton(onClick = onTrack)`. This modifier clears the semantics of all descendants, so the button's text, role and click action should no longer be exposed. Nothing else in the card offers `onTrack`. The card's only exposed action is `onOpen`, which may not reach tracking. The fixture doesn't say.
- **Smallest fix:** Replace `clearAndSetSemantics` with `semantics(mergeDescendants = true) {}` on the clickable container. That keeps the visible texts as the label and leaves the button reachable. If you need a custom label, set it on the container only, and keep Track as a separate node. For example, put the card's click on a nested `Column`/`Box` and keep `TextButton` as a sibling outside the merged node.
- **Automated verification:**
  - Use `composeTestRule.onNodeWithText("Track", useUnmergedTree = true)` and assert it exists.
  - Assert `.assertHasClickAction()` on it with the default merged tree, then `performClick()`, and check that `onTrack` fired.
  - Call `printToLog` on the root to inspect the semantics tree.
- **Real-device checks:**
  - With TalkBack, swipe through the card and confirm Track can be focused and activated.
  - Open the Voice Access numbered overlay and confirm Track gets its own number.
  - Use Switch Access scanning and confirm Track is reachable.

## 2. P1: Address errors are not tied to the field

- **Affected users:** Screen-reader users, and anyone who relies on the field's error state.
- **Evidence:**
  - `OutlinedTextField` has no `isError` and no `supportingText`.
  - Errors are separate `Text` items in the `Column`, styled only with a color.
  - Nothing links the errors to the field, and nothing marks them as live regions.
  - The effect moves focus onto the field, so focus lands on the field without its errors. Whether the separate error text is announced is not supported by the fixture.
- **Smallest fix:** Move the errors into the field with `isError = errors.isNotEmpty()` and `supportingText = { errors.forEach { Text(it) } }`. Optionally also add `Modifier.semantics { if (errors.isNotEmpty()) error(errors.joinToString()) }` on the field.
- **Automated verification:**
  - Render with errors and assert that the field node has the error semantics (`SemanticsProperties.Error`).
  - Assert that the error text is a descendant of the field's merged node.
  - Render without errors and assert that neither is present.
- **Real-device checks:**
  - Submit an invalid form with TalkBack on.
  - Confirm the user learns that an error exists and what it says, without having to swipe around to find it.
  - Confirm the error isn't conveyed by color alone, for example with grayscale or color-correction settings.

## 3. P2: The effect moves focus whenever the errors change

- **Affected users:** Keyboard, switch and screen-reader users.
- **Evidence:** `LaunchedEffect(errors)` calls `requestFocus()` each time the `errors` list changes. That includes re-validation while typing. It also pulls focus away from whatever the user used to submit. Nothing in the fixture limits it to a submit attempt.
- **Smallest fix:** Key the effect to an explicit event, such as a submit-attempt counter or a one-shot flag from the caller. Optionally focus the first invalid field only.
- **Automated verification:**
  - Change the errors list a second time while another element has focus, and assert that focus stays put.
  - Assert that focus moves only after the submit-attempt signal changes.
- **Real-device checks:** Using a hardware keyboard or Switch Access, type in the field and confirm focus doesn't jump unexpectedly. Then submit and confirm where focus lands.

## 4. P2: The card has no visible focus or press feedback and no role

- **Affected users:** Keyboard, D-pad and Switch Access users, low-vision users who need a focus indicator, and TalkBack users who depend on the role announcement.
- **Evidence:**
  - `clickable(indication = null, ...)` removes the default visual feedback, including the focus indication.
  - The card has no `role = Role.Button`.
  - The `remember { MutableInteractionSource() }` is redundant but harmless.
- **Smallest fix:** Drop `indication = null` and the custom `interactionSource` to restore the default ripple and focus indication. Add `role = Role.Button`, or whichever role matches what `onOpen` does.
- **Automated verification:**
  - Assert `SemanticsProperties.Role` on the card.
  - Use a Compose test with `requestFocus()` or keyboard input to check the focused state.
  - Screenshot-test the focused state and compare it to the unfocused one.
- **Real-device checks:** Tab or D-pad through the screen and confirm a visible focus indicator on the card. Check at large font scale and in both light and dark themes.

I'm leaving these out because the fixture doesn't show a barrier:

- The 48dp touch target for Track, since `TextButton` has a default minimum size.
- The decorative icon, since `contentDescription = null` is correct when the label "Track" is adjacent.
