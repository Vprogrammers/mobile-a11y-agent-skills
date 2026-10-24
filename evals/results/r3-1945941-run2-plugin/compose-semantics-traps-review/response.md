**Scope:** `evals/compose-semantics-traps-review/OrderCard.kt` is not on disk in this working directory (Glob found nothing), so I reviewed the fixture text supplied in the prompt. I did not edit anything and ran no builds. Android Compose is the only platform in scope, so I used `mobile-a11y-review` and `android-a11y`. Everything below is static evidence. Nothing was run on a device.

## Findings

**P1 — `OrderCard`, `Row` modifier chain (`clearAndSetSemantics`)**
- **Affected users:** TalkBack, Voice Access, and Switch Access users. They cannot reach the "Track" action.
- **Evidence:**
  - `clearAndSetSemantics` clears the semantics of all descendants. The `TextButton(onClick = onTrack)` is a descendant of that `Row`.
  - The button's click action, its "Track" text, and its button role are therefore removed from the accessibility tree.
  - The Row's `contentDescription` only names the order and status, so no other node exposes tracking.
  - The visible button is still tappable by touch, so sighted touch users are unaffected.
  - Assumption: that the Row's own `clickable` survives. It is declared before `clearAndSetSemantics` in the chain, so it should, but this needs a tree check.
- **Criterion:** WCAG 4.1.2 Name, Role, Value, and 2.1.1 Keyboard (useful here).
- **Fix:**
  - Remove `clearAndSetSemantics`.
  - `clickable` already merges the card's text into one node, and the `Button` stays a separate node.
  - Optionally add `onClickLabel = "Open order"`.
  - If you keep a custom description, use `semantics(mergeDescendants = true)` and add `customActions` for Track. Do not clear the semantics.
- **Verify:**
  - **Automated:** a Compose test that compares `onRoot(useUnmergedTree = true).printToString()` with the merged tree. It should assert `onNodeWithText("Track").assertHasClickAction()` and that the card exposes an open action.
  - **Device:** with TalkBack, swipe through the card and confirm "Track" is reachable and activates. With Voice Access, say "tap Track".

**P2 — `OrderCard`, `clickable(indication = null)`**
- **Affected users:** Hardware-keyboard and Switch Access users, and low-vision users who rely on focus or press feedback.
- **Evidence:**
  - `indication = null` with a custom `MutableInteractionSource` removes the visual focus and press indication from the card.
  - The Row has no role, so it is not a recognizable button.
  - Whether the card is focusable depends on the Compose version. Confirm that on a device.
- **Criterion:** WCAG 2.4.7 Focus Visible, 2.4.11 Focus Not Obscured.
- **Fix:**
  - Drop `interactionSource` and `indication = null` so the default ripple and focus indication apply.
  - Add `role = Role.Button`, or use `Card(onClick = …)`.
- **Verify:**
  - **Automated:** a test asserting the `Role` and click action.
  - **Device:** Tab through the card with an external keyboard and confirm a visible focus state. Repeat with Switch Access.

**P2 — `OrderCard`, "Track" button name**
- **Affected users:** TalkBack and Voice Access users in a list of several orders.
- **Evidence:**
  - Every card exposes an identical "Track" button, with a decorative icon (`contentDescription = null`, which is correct).
  - Nothing says which order it applies to. Voice Access has several identical "Track" targets to choose from.
- **Fix:**
  - Add `Modifier.semantics { contentDescription = "Track order ${order.number}" }` to the button. The name begins with the visible label, so voice commands still match.
  - Alternatively, rely on traversal context. That is weaker.
- **Verify:**
  - **Automated:** a semantics test per item.
  - **Device:** in a multi-order list, check that Voice Access disambiguates the buttons and that TalkBack gives enough context.

**P2 — `AddressForm`, `LaunchedEffect(errors)` with `requestFocus()`**
- **Affected users:** Screen-reader, keyboard, and switch users, plus anyone typing.
- **Evidence:**
  - Focus is requested whenever `errors` changes and is non-empty, regardless of which field the errors belong to. The effect is not tied to a submit event.
  - It also fires on first composition if errors already exist.
  - It requests input focus, not TalkBack accessibility focus. The two are separate systems, so this does not reliably lead a TalkBack user to the errors.
  - Assumption: if the caller revalidates on each keystroke, the changing error list pulls focus back repeatedly. That would be P1 by this skill's calibration. It is not provable from the fixture.
- **Fix:**
  - Trigger focus from an explicit submit-failure event, such as an incrementing counter or a one-shot flow.
  - Target the first invalid field only.
  - Do not refocus on routine error text changes.
- **Verify:**
  - **Automated:** a Compose test that updates `errors` and asserts focus moves only after submit.
  - **Device:** with TalkBack, type and submit with an invalid street. Confirm focus is not stolen while typing.

**P2 — `AddressForm`, error association and announcement**
- **Affected users:** TalkBack users, and users with low vision or color-vision differences.
- **Evidence:**
  - `OutlinedTextField` has no `isError` and no `supportingText`.
  - The errors are loose `Text` nodes below the field, so the error is not tied to the field.
  - The errors are not announced as a live region.
  - The error text itself is not color-only, but the field's error state has no non-color indicator.
- **Criterion:** WCAG 3.3.1 Error Identification, 4.1.3 Status Messages.
- **Fix:**
  - Set `isError = errors.isNotEmpty()`.
  - Move the text into `supportingText = { Text(errors.first()) }`.
  - Add `Modifier.semantics { error(errors.first()) }`, because Material's default error semantics message is generic.
  - Add `liveRegion = LiveRegionMode.Polite` only if the errors appear asynchronously.
- **Verify:**
  - **Automated:** a semantics test with `SemanticsProperties.Error` on the field.
  - **Device:** with TalkBack, focus the field after a failed submit and confirm the error is conveyed. Do not assume the exact speech.

## Blockers
- **P1:** the `clearAndSetSemantics` on the `OrderCard` Row removes the "Track" action from the accessibility tree.

## Device checks
- **TalkBack:**
  - Check that the card and Track are separate stops.
  - Check the error flow on a failed submit.
  - Check that focus is not stolen during typing.
- **Voice Access:** say "tap Track" in a multi-order list.
- **Keyboard and Switch Access:** check focus visibility on the card.
- **Settings:** repeat at 200% font scale with the IME open, to check the error text stays visible.

## Residual risk
- The fixture is an excerpt: I cannot see the caller's validation timing, the `Order` data, or the theme.
- I did not check contrast of `colorScheme.error` or the touch-target size in context.
- The exact Compose version affects the default focusability of `clickable` and the error semantics defaults.
- No device results exist, so the assistive-technology behavior above is proven from code only.
