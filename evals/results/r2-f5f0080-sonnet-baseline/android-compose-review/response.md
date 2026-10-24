# Review of `CheckoutScreen.kt`

I reviewed the inline fixture only. I didn't edit it, and I didn't run anything.

## Findings

### 1. High: Help is reachable only by a horizontal swipe
- **Affected users:** TalkBack, Switch Access, keyboard and Voice Access users, and anyone with limited dexterity or motor control.
- **Evidence:** `Text("Swipe left for help", Modifier.pointerInput…detectHorizontalDragGestures)` is the only place `showHelp = true` is set. The text has no click action, no custom accessibility action, and no role. Touch exploration, which uses a different gesture model, may not deliver this drag. Assistive input methods can't perform it at all.
- **Smallest fix:** Make it a real control, such as `TextButton(onClick = { showHelp = true }) { Text("Help") }`. Keep the swipe as an optional shortcut only. Change the visible text so it no longer tells users to swipe.

### 2. High: The help overlay can't be dismissed and isn't modal
- **Affected users:** Everyone, and especially screen reader, keyboard and switch users.
- **Evidence:**
  - Nothing ever sets `showHelp = false`, and the overlay has no close control or back handling. Once opened, it covers the screen for the rest of the composition.
  - The overlay is a plain `Box` with a scrim. It has no dialog semantics and no focus management.
  - Nothing here hides the checkout content underneath from accessibility services. A screen reader can likely still reach the delete controls behind the scrim.
  - The `Box` has no pointer handling, so touches may also pass through to the content below. I can't confirm that from this snippet alone.
- **Smallest fix:** Replace the `Box` with `AlertDialog` or `Dialog(onDismissRequest = { showHelp = false })`. Include a visible "Close" button. A dialog gives you modal behavior, back dismissal and focus handling.

### 3. High: The delete control is a small, redundant, split target
- **Affected users:** TalkBack, Switch Access and Voice Access users, plus anyone with motor impairments or low vision.
- **Evidence:**
  - `Icon(...Modifier.clickable)` has no explicit size or minimum touch target. An `Icon` defaults to 24dp, which is under the usual 48dp guideline. A plain `clickable` on a non-interactive-component `Icon` doesn't enlarge it.
  - The `Icon` has `contentDescription = "Delete ${item.name}"`, and the adjacent `Text("Delete ${item.name}")` repeats it. Each row therefore has two separate accessibility nodes with the same label. Only the icon is actionable.
  - The visible "Delete …" text does nothing when tapped. Voice Access users who say that visible label may hit an ambiguity, because two nodes share it.
  - The click has no `Role.Button`.
- **Smallest fix:** Replace the icon and text with one control:
  ```kotlin
  TextButton(onClick = { onDelete(item) }) {
      Icon(Icons.Default.Delete, contentDescription = null)
      Text("Delete ${item.name}")
  }
  ```
  If you keep the icon-only design, use `IconButton` (48dp minimum) with the description and drop the duplicate text. Don't leave the description on both.

### 4. Medium: The "Checkout" title isn't a heading, and its height is fixed
- **Affected users:** Screen reader users who navigate by headings, and users with large font or display scaling.
- **Evidence:**
  - `Text("Checkout", Modifier.height(32.dp))` has no `heading()` semantics.
  - A fixed 32dp height can clip the text at large font scale. That depends on the style and scale, and I haven't measured it.
- **Smallest fix:** `Modifier.semantics { heading() }`, and replace `height(32.dp)` with `heightIn(min = 32.dp)` or remove it.

## Not reported
Colors and contrast: the text color is unspecified, and the scrim sits over an unknown background, so the fixture doesn't support a finding. The same goes for the exact TalkBack speech, which I haven't assumed.

## Automated verification
- Use a Compose UI test with `createComposeRule().enableAccessibilityChecks()`. The Accessibility Test Framework checks should flag the small touch target, and duplicate or overlapping click bounds, if they remain.
- For the delete control, assert that each item has exactly one node with a click action: `onAllNodesWithText("Delete …").assertCountEquals(1)` with `assertHasClickAction()`. Also assert `Role.Button` and a minimum size of 48dp with `assertWidthIsAtLeast` and `assertHeightIsAtLeast`.
- For the title, assert that `SemanticsProperties.Heading` is defined, with `SemanticsMatcher.keyIsDefined`.
- For font scaling, run with `LocalDensity` set to `fontScale = 2f` and assert the title is fully displayed with `assertIsDisplayed()`. Also compare its measured height against its text height.
- For help, assert that a node with a click action opens it without any gesture. Then click "Close" and assert that the help content no longer exists. Assert that the checkout content is not reachable while the dialog is open.

## Real-device checks
- **TalkBack:** Swipe through the list and confirm each row has one delete stop with a sensible label and that it activates. Confirm that Help can be opened and closed, and that focus moves into the help and returns afterward. Move through headings with the headings navigation setting.
- **Switch Access and keyboard:** Reach and activate Delete and Help using Tab/arrow keys and switch scanning. Confirm focus can't land behind the open help.
- **Voice Access:** Say the visible "Delete <name>" label and confirm it resolves to one target.
- **Display scaling:** Check font scale at the maximum and display size at the largest, and confirm the title isn't clipped.
- **Back gesture:** Confirm it dismisses help.
- **Touch targets:** With a finger on a physical device, check that delete is easy to hit and doesn't trigger a neighbor.
