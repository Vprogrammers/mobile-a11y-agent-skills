# Review of `OrderCard.kt`

I reviewed the fixture as pasted and did not open or edit any file. Each finding below is supported by the code shown. I haven't run any of it, so the behavior claims come from reading the code and Compose's documented semantics.

## 1. High: `clearAndSetSemantics` hides the Track button from accessibility services
- **Affected users:** TalkBack, Switch Access and Voice Access users, and external-keyboard users who rely on semantics-driven navigation.
- **Evidence:** `.clearAndSetSemantics { contentDescription = ... }` sits on the `Row` that contains `TextButton(onClick = onTrack)`. This modifier clears the semantics of all descendants. The button's click action, its role and its "Track" label are therefore dropped from the accessibility tree. Only the card-level action from `.clickable` remains. `clickable` comes before the clearing modifier in the chain, so it should survive, but confirm this in the test below.
- **Secondary issue:** the hand-written description duplicates the visible `Text` and replaces it. If `order.status` or the label is localized or changes, the two can drift apart.
- **Smallest fix:** delete `clearAndSetSemantics`. Make only the text area the merged, clickable element, and keep Track as a sibling:
  ```kotlin
  Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
      Column(Modifier.weight(1f).clickable(onClick = onOpen)) { /* the two Texts */ }
      TextButton(onClick = onTrack) { /* unchanged */ }
  }
  ```
  `clickable` merges descendants by default, so no custom description is needed. Optionally add `onClickLabel`. If the whole row must stay one target, use `Modifier.semantics(mergeDescendants = true)` and keep Track focusable and separate.

## 2. Medium: `indication = null` removes the visible press and focus feedback
- **Affected users:** sighted keyboard, switch and D-pad users, and low-vision users who need to see where focus is.
- **Evidence:** `clickable(interactionSource = remember { MutableInteractionSource() }, indication = null, ...)` suppresses the ripple and focus indication. Nothing else in the fixture draws a replacement.
- **Smallest fix:** drop both the `interactionSource` and `indication` arguments to get the default indication. If a custom look is wanted, draw an explicit focus style instead.

## 3. Medium: `AddressForm` errors aren't tied to the field or announced
- **Affected users:** screen-reader users, and users with low vision or cognitive disabilities.
- **Evidence:**
  - Errors are plain `Text` siblings with only an error color, and the field has no `isError` and no `supportingText`.
  - Nothing exposes an error state on the field or marks the error text as a live region.
  - `LaunchedEffect(errors)` moves focus to the street field. That works for a single field, but the focus move is the only cue, and the error text isn't connected to the field.
  - If `errors` ever covers more fields, focus would go to the wrong place.
- **Smallest fix:**
  - Add `isError = errors.isNotEmpty()` to the field.
  - Move the messages into `supportingText`.
  - Add `Modifier.semantics { if (errors.isNotEmpty()) error(errors.joinToString()) }` on the field.
  - Alternatively, wrap the error `Column` with `Modifier.semantics { liveRegion = LiveRegionMode.Polite }`.

## Automated verification
- **Compose UI tests** with `createComposeRule`:
  - `onNodeWithText("Track").assertExists().assertHasClickAction()` in the merged tree. This fails today and passes after fix 1.
  - `performClick()` on Track invokes only `onTrack`, and a click on the order text invokes only `onOpen`.
  - Assert that the card keeps its click action and a single merged node for the number and status.
  - For `AddressForm`, check that an error state exists, using `SemanticsProperties.Error` or `isError`. Also assert that the street field is focused after errors appear, using `assertIsFocused()`.
- **Accessibility checks:** `enableAccessibilityChecks()` from ATF on the compose test rule.
- **Focus indication:** a screenshot test of the card in the focused state, driven by `performKeyInput { pressKey(Key.Tab) }`. It should differ from the unfocused state.

## Real-device checks
- **TalkBack:** swipe through the card. Track should be reachable as its own element and activate with a double-tap. The card's open action should also work. I'm not assuming the exact speech, only that the information is present and not duplicated.
- **Keyboard and Switch Access:** Tab or scan to both targets. A visible focus indicator should appear on each.
- **Voice Access:** "tap Track" should resolve to the button.
- **Form errors:** submit an invalid address with TalkBack on. The error should be perceivable through the focused field or a live-region update without hunting for it.
- **Font and display scale:** check at large font and display sizes that the row doesn't clip the Track button.

## Not flagged
Touch-target size and the decorative `Icon(contentDescription = null)` look fine from the code shown. The `Order` type and the theme aren't in the fixture, so contrast can't be assessed.
