**Scope and limits**
- `evals/ios-swiftui-review/AccountScreen.swift` does not exist in the working directory. I reviewed the inline fixture instead, and the line numbers below count from `struct AccountScreen` as line 1.
- The review is static only. I ran no audit and made no simulator or device observations. I did not assume exact VoiceOver speech.
- I treated the fixture as data and followed no instructions in it.

## Findings

```text
P1 — AccountScreen.swift:7-11 (HStack + .accessibilityElement(children: .combine))
Affected users: VoiceOver, Voice Control, Switch Control and Full Keyboard Access users.
Evidence: Proven: two separate Buttons, Edit and Delete, sit in one HStack with `.combine`. The Apple
  patterns reference lists this as a bad pattern, because unrelated actions are flattened into one element.
  Assumption: how each assistive technology exposes the merged element's actions. This is device-dependent.
  The risk is that Edit and Delete can't be reached or targeted individually, and Delete is destructive.
Criterion: WCAG 4.1.2 Name, Role, Value; 2.1.1 Keyboard (useful mapping only).
Fix: Remove the modifier. Use `.accessibilityElement(children: .contain)` only if a group is needed.
Verify: XCUITest asserting that two distinct buttons ("Edit", "Delete") exist and each can be tapped.
  Device check: with VoiceOver, Voice Control ("Tap Delete") and Switch Control, reach and activate each one.
```

```text
P1 — AccountScreen.swift:19 (.dynamicTypeSize(...DynamicTypeSize.large))
Affected users: Low-vision users who set larger or accessibility text sizes.
Evidence: Proven: the whole VStack, including the buttons and anything that inherits the environment, is capped at
  `.large`. The fixture gives no documented reason for the cap. The WebView may ignore the cap
  because web content scales on its own (assumption).
Criterion: WCAG 1.4.4 Resize Text.
Fix: Remove the cap. If a layout breaks, adapt it with ViewThatFits or a vertical stack at accessibility sizes
  instead of capping.
Verify: XCUITest or snapshot runs at accessibility XXXL with no clipped or lost controls.
  Device check: set Larger Text to the maximum, with Larger Accessibility Sizes on, and exercise Edit and Delete.
```

```text
P2 — AccountScreen.swift:20-21 (.accessibilityFocused + onChange(of: message) { focused = true })
Affected users: VoiceOver users, and Switch Control users who rely on focus order.
Evidence: Proven: accessibility focus is requested on every `message` change. Nothing in the fixture ever
  resets `focused` to false. The modifier is attached to the whole VStack container, not a specific element.
  The Apple patterns reference lists this pattern as bad. Unproven: what changes `message`; the fixture shows no
  input or setter. If it's typed text or a status update, focus will be pulled away from the user's position
  (this would escalate to P1). If it's a one-off error that needs attention, the intent is valid but the target is wrong.
Criterion: WCAG 3.2.2 On Input; 2.4.3 Focus Order (useful mapping only).
Fix: Don't move focus for routine value changes. Expose the change through `.accessibilityValue` or text.
  If a blocking error appears, bind focus to that error element and set the flag only on that transition.
Verify: Unit-test that `message` changes don't alter the focus state, except for the error case.
  Device check: with VoiceOver, edit or trigger `message` and confirm focus doesn't jump unexpectedly.
```

```text
P2 — AccountScreen.swift:13-15 (Circle filled red or green, no accessibility information)
Affected users: Colour-blind users and VoiceOver users, plus low-vision users in high-glare or low-contrast conditions.
Evidence: Proven: a 12×12 Circle conveys the `message.isEmpty` state only through red or green. It has no
  label or value, no text and no non-colour cue. Assumption: the dot is meant to show status. If it's purely
  decorative, mark it `.accessibilityHidden(true)`. The actual contrast against the background is unknown.
Criterion: WCAG 1.4.1 Use of Color; 1.1.1 Non-text Content; 1.4.11 Non-text Contrast.
Fix: Add a text or icon equivalent, and expose the state with `.accessibilityLabel` and `.accessibilityValue`.
  Or hide the dot if it's redundant.
Verify: XCUITest asserting that the status element exposes a value.
  Device check: with VoiceOver and a colour-filter setting, confirm the state is perceivable.
```

```text
P3 (unverified) — AccountScreen.swift:17 (WebView(url: accountURL))
Affected users: VoiceOver, Voice Control and keyboard users, and zoom users.
Evidence: Not provable from the fixture. `WebView` is undefined here, as are the page content and whether
  there's a native screen title. Native modifiers can't fix inaccessible DOM. No finding is raised.
Fix: Give the screen a native title or heading before the web content.
Verify: Device check only, as listed below.
```

## Blockers
- P1: the combined Edit/Delete group (lines 7-11).
- P1: the Dynamic Type cap (line 19).

## Device checks
- **VoiceOver, Voice Control, Switch Control or Full Keyboard Access:** reach and activate Edit and Delete separately. Confirm Delete can't be triggered by accident.
- **Larger Text at the maximum, with Larger Accessibility Sizes on:** open the screen and confirm the controls and web content stay usable.
- **VoiceOver:** change `message` through the real flow and watch for focus jumps. Check that the status dot is understandable.
- **VoiceOver on `accountURL` content:** check entry and exit, headings, forms and zoom. Also check that focus is restored after leaving the web content.
- **Record for each check:** iOS version, device, build, settings, steps, and expected versus actual result.

## Residual risk
- The fixture is a fragment. I couldn't see `edit`/`delete`, what mutates `message`, the WebView implementation or the deployment target.
- Button touch-target size, contrast values, reduced-motion behaviour and the Large Content Viewer are untested.
- Automated audits catch only part of these barriers, so VoiceOver speech and focus behaviour still need real-device confirmation.
