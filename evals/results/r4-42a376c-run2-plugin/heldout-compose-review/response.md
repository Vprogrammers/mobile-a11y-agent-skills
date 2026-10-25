# Review: `MessageThread.kt`

**Scope:** This is a single Jetpack Compose fixture. It is not a git repository, so there was no diff or history to inspect. The review is static only, with no build, test or device evidence. Line numbers count from `data class Message` as line 1.

## Findings

**P1 — MessageThread.kt:37-41 (`ClickableText`) and :26-35 (`policy`)**
Affected users: TalkBack, Voice Access and Switch Access users. Also low-vision and color-blind users.
Evidence:
- The two links are only an `AnnotatedString` read through `ClickableText`'s tap-offset callback.
- The fixture does not use `LinkAnnotation`, `customActions` or any semantics that would expose "terms" and "privacy policy" as separate operable links. Nothing here proves they are reachable without a touch at an exact character offset.
- Assumption: how TalkBack presents this node needs device confirmation.
- The links are marked only by `Color.Blue` (:29, :33), with no underline or other cue.
- The `Color.Blue` contrast depends on a background the fixture doesn't show.

Criterion: WCAG 2.1.1 Keyboard, 1.4.1 Use of Color, 2.5.8 Target Size.
Fix: Replace `ClickableText` with `Text(buildAnnotatedString { withLink(LinkAnnotation.Url(url, styles = TextLinkStyles(SpanStyle(textDecoration = TextDecoration.Underline)))) { append(...) } })`. This needs a Compose UI version that supports `LinkAnnotation` (1.7 or later). To keep `onOpenUrl`, use `LinkAnnotation.Clickable`. Take the link colors from the theme.
Verify: A Compose test that checks the semantics tree for link or click actions on the policy text. Then a TalkBack check with the links menu or the actions menu, a Voice Access check by saying the link text, and a hardware-keyboard Tab check.

**P1 — MessageThread.kt:58-80 (undo bar) and :59-62**
Affected users: TalkBack, Switch Access and Voice Access users. Also users with motor or cognitive disabilities who need more time.
Evidence:
- `onDelete` runs immediately (:51), and `Undo` exists only inside a bar that removes itself after `delay(3_000)`.
- The bar is a plain `Row`. It has no `liveRegion`, `paneTitle` or announcement semantics, so nothing in the fixture tells a screen-reader user that a deletion happened or that Undo is available.
- Accessibility focus is not moved to the bar. A user who is exploring or scanning can lose the only recovery path before reaching it.
- The fixture offers no alternative route to Undo.

Criterion: WCAG 2.2.1 Timing Adjustable, 4.1.3 Status Messages, 3.3.4 Error Prevention.
Fix: Use Material `SnackbarHost` and `SnackbarHostState.showSnackbar(message, actionLabel = "Undo", withDismissAction = true)`. This lets the platform extend the duration for accessibility timeouts and announce the snackbar. Alternatively, mark the message `Text` with `liveRegion = Polite` and keep the bar until the user dismisses it or chooses Undo. Whichever you pick, don't rely on a fixed 3 s limit.
Verify: A Compose test with the clock advanced past 3 s, asserting that Undo is still available or that the snackbar is shown. Then a TalkBack check with the system "Time to take action" setting raised, confirming the deletion is announced and Undo is reachable.

**P2 — MessageThread.kt:49-53 (per-row `Delete`)**
Affected users: Voice Access users (ambiguous "Delete" targets) and TalkBack users navigating by controls.
Evidence:
- Every row exposes an identical "Delete" button with no reference to its message.
- On a long list, "click Delete" is ambiguous. Voice Access would fall back to numbered overlays (assumption).
- The `key = { it.id }` on `items` is good for focus continuity.

Fix: Give each button a distinct accessible name that keeps the visible word "Delete", for example `Modifier.semantics { contentDescription = "Delete: ${message.body}" }`. Truncate long bodies. Alternatively, put a `customActions` entry on the row.
Verify: A Compose test asserting the per-row names are unique. Then a Voice Access check saying "Delete" and then the row's number.

**P2 — MessageThread.kt:15-24 (read-receipts toggle)**
Affected users: TalkBack, Switch Access and keyboard users.
Evidence:
- The row uses `clickable` and the `Switch` has its own `onCheckedChange`, so there are two toggle paths.
- `clickable` has no `Role.Switch` and no toggle state of its own. How the merged node exposes the label, role and state depends on the merge and needs inspection.
- Assumption: this may produce a duplicated or inconsistent node.

Fix: Use `Modifier.toggleable(value = readReceipts, role = Role.Switch, onValueChange = onReadReceiptsChange)` on the `Row`, and set `Switch(checked = readReceipts, onCheckedChange = null)`.
Verify: Print the merged and unmerged semantics trees and assert a single toggleable node with the label text. Then a TalkBack check that the control is announced once as a switch with its state.

## Blockers
- P1: policy links not exposed as operable links and marked by color only (:26-41).
- P1: time-limited, unannounced Undo for a destructive action (:58-80).

## Device checks
- TalkBack: delete a message and confirm that the deletion and Undo are announced and reachable. Repeat with the system accessibility timeout raised.
- TalkBack, Voice Access and a keyboard: open both policy links.
- Voice Access: say "Delete" in a list with several rows.
- Check the read-receipts row for a single, correctly stated switch.
- Check at 200% font scale, in dark theme and in landscape.

## Residual risk
- The Android API level and targetSdk are unknown. The `Column` applies no system-bar or IME insets (:14). If the app targets SDK 35 or later, the bottom undo bar could be obscured by the navigation bar. This is an assumption.
- `Color.Blue` and `inverseSurface` contrast depend on the theme and need a dark-theme check.
- `deleted` uses plain `remember` (:12). The Undo state is lost on configuration change, which is a resilience concern (P3).
- Tap targets for the links, and the exact TalkBack speech, can't be proven statically.
