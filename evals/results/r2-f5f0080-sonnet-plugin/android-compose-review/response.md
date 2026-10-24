# Review: `evals/android-compose-review/CheckoutScreen.kt`

**Scope:** Compose, Android only. The fixture is a single composable snippet with no line numbers, so locations below are symbols or the order of elements. I made no edits and ran no builds. The fixture has no tests, theme or caller, so I could not check anything outside the snippet.

## Findings

```text
P1 — CheckoutScreen / "Swipe left for help" Text (pointerInput + detectHorizontalDragGestures)
Affected users: TalkBack, Switch Access, Voice Access, keyboard, and users with limited dexterity who can't do a directional drag
Evidence: The only way to set showHelp = true is a horizontal drag handler on a non-clickable Text.
  The code exposes no click or custom action semantics, so help is gesture-only. (Proven by the code.)
  The "Swipe left" text also tells the user to use a gesture.
Criterion: WCAG 2.5.1 Pointer Gestures, 2.1.1 Keyboard
Fix: Add a single-pointer alternative. Use a Button or TextButton "Help" with onClick = { showHelp = true }.
  Keep the swipe only as an optional shortcut.
Verify: Compose test: onNodeWithText("Help").assertHasClickAction().performClick() shows the help content.
  Device: reach and open Help with TalkBack, Switch Access, Voice Access and a hardware keyboard.
```

```text
P1 — CheckoutScreen / `if (showHelp)` overlay Box
Affected users: TalkBack, Switch Access, Voice Access and keyboard users. Sighted users are also affected by the missing dismissal.
Evidence: Proven by the code:
  - The overlay is a plain Box with no dialog or modal semantics.
  - Nothing in the snippet ever sets showHelp back to false. There is no dismiss control, no back handling and no onDismissRequest.
  - A plain Box doesn't consume pointer input or hide the content underneath from the accessibility tree.
  Assumptions: no caller or parent resets showHelp, and the underlying nodes stay focusable.
  Also, the overlay Text color on a 50% black scrim over unknown content has unproven contrast.
Criterion: WCAG 2.4.3 Focus Order, 1.4.3 Contrast, 2.1.2 No Keyboard Trap (if the user can't leave)
Fix: Replace the Box with an AlertDialog or Dialog with a visible "Close" button and onDismissRequest = { showHelp = false }.
  This also keeps the dismissal reachable through system back. Use theme-based text colors.
Verify: Compose test: after opening, assert the Close button exists and that clicking it removes the help content.
  Device: check that TalkBack focus stays inside the help content and back dismisses it.
  Check contrast in light and dark themes.
```

```text
P1 — CheckoutScreen / Text("Checkout", Modifier.height(32.dp))
Affected users: Large font and display size users, low-vision users
Evidence: A fixed 32 dp height is applied to text, so it cannot grow with font scale.
  At a larger scale or with a wrapping title, the text is likely to be clipped. This is a code-proven risk, but the visible result needs confirmation.
Criterion: WCAG 1.4.4 Resize Text, 1.4.10 Reflow
Fix: Remove the fixed height. Use heightIn(min = 32.dp) or padding so the height can grow.
Verify: Screenshot or Compose test with a fontScale of 2.0 (LocalDensity override) and check the title isn't clipped.
  Device: test with the largest system font size and display size.
```

```text
P2 — CheckoutScreen / "Checkout" Text
Affected users: TalkBack users who navigate by headings
Evidence: The title has no semantics { heading() } and is styled only as plain Text. (Proven by the code.)
Criterion: WCAG 1.3.1 Info and Relationships, 2.4.6
Fix: Add Modifier.semantics { heading() }, and use a typography style that visually matches.
Verify: Compose test: onNodeWithText("Checkout").assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Heading)).
  Device: use TalkBack heading navigation.
```

```text
P2 — CheckoutScreen / item Row (Icon with clickable + Text "Delete ${item.name}")
Affected users: Motor-impaired users, TalkBack users, and Voice Access users
Evidence: Proven by the code:
  - The Icon has a bare clickable with no Role.Button and no 48 dp minimum interactive size. The default Icon is 24 dp, and foundation clickable does not enforce the minimum.
  - The adjacent Text repeats the same "Delete X" string but is not clickable. It looks like a control but does nothing.
  - It also adds a duplicate stop in the accessibility tree.
  Assumption: no parent applies a size.
Criterion: WCAG 2.5.8 Target Size (Minimum), 4.1.2 Name, Role, Value
Fix: Use IconButton(onClick = { onDelete(item) }) with Icon(contentDescription = "Delete ${item.name}"). It gives the button role and a 48 dp target.
  Show the item name as a separate Text, or make the whole Row the single action.
  Consider a confirmation or undo for the destructive action.
Verify: Compose test: onAllNodes(hasClickAction()) has one node per item, with a size of at least 48 dp.
  Enable accessibility checks as well.
  Device: step through the list with TalkBack and Voice Access ("click Delete <name>"), and check that focus is sensible after an item is removed.
```

## Blockers
- **P1:** Help is available only through a swipe gesture.
- **P1:** The Help overlay can't be dismissed and isn't modal.
- **P1:** The fixed-height "Checkout" title is likely clipped at large font scales.

## Device checks
- TalkBack: reach and dismiss Help, move focus through the list, and check focus after a delete.
- Switch Access, Voice Access and a hardware keyboard: open Help and delete an item.
- Font size and display size at maximum: check the title and the item rows.
- Light and dark themes: check the overlay text contrast.
- I did not assume any exact TalkBack speech. Confirm the spoken output on a device.

## Residual risk
- Only this snippet was reviewed. I can't see the Item type, the theme, the callers or the navigation, so I can't confirm that the list scrolls correctly in the Column.
- I did not verify that no other code resets showHelp.
- I did not check delete confirmation or undo behavior, or error handling after onDelete.
- Nothing was run, so all results come from static review only.
