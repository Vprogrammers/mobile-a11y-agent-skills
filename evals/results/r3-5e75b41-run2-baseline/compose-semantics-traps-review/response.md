## Findings for `OrderCard.kt`

### 1. High: `clearAndSetSemantics` hides the "Track" button from accessibility services
- **Affected users:** TalkBack, Switch Access and voice-control users. Voice Access matches on-screen labels and actions, so it is likely affected too.
- **Evidence:**
  - `.clearAndSetSemantics { contentDescription = ... }` sits on the `Row` that contains `TextButton(onClick = onTrack)`.
  - That modifier discards the semantics of all descendants, so the button's label ("Track") and its click action are removed from the semantics tree.
  - The row's `clickable` comes earlier in the modifier chain, so the open action probably survives. Only the nested button is lost.
- **Smallest fix:** Remove `clearAndSetSemantics`. Use `Modifier.semantics(mergeDescendants = true) { }` after `clickable`, or let `clickable` merge descendants by default. The merged text ("Order N", status) is then read naturally, and the Track button stays a separate focusable node. Keep a custom `contentDescription` only if the merged text proves inadequate, and never on a container holding interactive children.
- **Automated verification:**
  - Compose UI test: `onNodeWithText("Track").assertHasClickAction()` and `.performClick()`, asserting `onTrack` was invoked.
  - Test the row with `onNode(hasClickAction() and hasText("Order 123", substring = true))`.
  - Run with the Accessibility Test Framework enabled (`enableAccessibilityChecks()`).
- **Real-device checks:**
  - With TalkBack, swipe through the card and confirm "Track" is a separate stop that can be activated.
  - With Switch Access or Voice Access, confirm "Track" can be targeted.
  - Don't assert exact speech.

### 2. Medium: `indication = null` removes the row's focus and pressed feedback
- **Affected users:** Keyboard, D-pad and switch users who need a visible focus indicator. Low-vision and sighted touch users also lose press feedback.
- **Evidence:** `clickable(interactionSource = remember { MutableInteractionSource() }, indication = null, ...)`. The interaction source is also created locally and never used for anything else, so nothing replaces the indication.
- **Smallest fix:** Drop `indication = null` and use the default indication. If a custom look is needed, collect focus and press state from the interaction source and draw an equivalent visible indicator.
- **Automated verification:** A UI test that sends keyboard focus to the row (`performKeyInput` / `requestFocus`) and compares screenshots, or a screenshot test of the focused state.
- **Real-device checks:** Tab or D-pad through the list with a hardware keyboard and confirm the focused card is clearly visible.

### 3. Medium: Validation errors are not tied to the field and are conveyed by color alone
- **Affected users:** Screen-reader users, who may not hear the error in context. Color-blind and low-vision users are also affected.
- **Evidence:**
  - `OutlinedTextField` has no `isError = true` and no `supportingText`.
  - The errors are loose `Text(it, color = error)` siblings with no live region, so there is no programmatic link to the field.
  - Focus moves to the field via `LaunchedEffect(errors)`, but the errors are separate nodes.
- **Smallest fix:** Pass `isError = errors.isNotEmpty()` and put the messages in `supportingText = { errors.forEach { Text(it) } }`. This adds error semantics and associates the text with the field. Optionally add `Modifier.semantics { liveRegion = LiveRegionMode.Polite }` on the error container if a separate announcement is wanted.
- **Automated verification:** Assert the `SemanticsProperties.Error` property is present when errors are non-empty (or use `assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Error))`). Also assert the error text exists and the field is focused (`assertIsFocused()`).
- **Real-device checks:**
  - Submit invalid input with TalkBack on and confirm the error is reachable and tied to the field when it takes focus.
  - Confirm the error is understandable without color.

### 4. Low: The focus effect is unconditional and fits only a single-field form
- **Affected users:** Keyboard and screen-reader users, if this form grows.
- **Evidence:** `LaunchedEffect(errors) { if (errors.isNotEmpty()) focusRequester.requestFocus() }` always targets the Street field, whatever the error is about. If the `errors` list changes content later, for example while the user edits another field, focus is pulled back to Street.
- **Smallest fix:** Move focus to the first field that actually has an error. Trigger it on a submit-attempt event, not on every change of the error list.
- **Automated verification:** A test where an error appears for a different field, asserting that focus doesn't move to Street.
- **Real-device checks:** Edit a later field while an error exists and confirm focus isn't stolen.

### Not flagged
- The `Icon` with `contentDescription = null` next to the "Track" text is appropriate, because it's decorative.
- I did not assume exact TalkBack speech anywhere, and I did not edit the fixture.
- The row lacks an explicit `Role` (e.g. `Role.Button`). That is a minor optional improvement, not a defect the fixture proves.
