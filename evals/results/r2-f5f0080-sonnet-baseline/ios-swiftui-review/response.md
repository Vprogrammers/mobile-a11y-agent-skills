# Review of `AccountScreen.swift`

I reviewed the fixture as given. It is a snippet: `edit`, `delete`, `accountURL` and `WebView` aren't defined in it, so findings that depend on them are listed at the end as not reported.

## Findings

### 1. Edit and Delete merged into one accessibility element (High)
- **Affected users:** VoiceOver, Voice Control and Switch Control users.
- **Evidence:** `.accessibilityElement(children: .combine)` sits on the `HStack` holding two `Button`s. Combining makes the pair one element, so the two separate actions are no longer exposed as independent controls. Which one gets activated, if either, is left to the framework.
- **Smallest fix:** Remove the modifier. If grouping is wanted, use `.accessibilityElement(children: .contain)`.
- **Automated check:** An XCUITest asserts that `app.buttons["Edit"]` and `app.buttons["Delete"]` each exist and are hittable, and that tapping each calls the right action.
- **Device check:** With VoiceOver, confirm you can reach and activate each button separately. With Voice Control, say "Tap Edit" and "Tap Delete". With Switch Control, confirm each button is a separate target.

### 2. Status conveyed by color only (Medium–High)
- **Affected users:** Color-blind users, VoiceOver users, and anyone using grayscale or Increase Contrast.
- **Evidence:** The `Circle` is filled red or green depending on `message.isEmpty`. It has no text, shape difference or accessibility label or value. The fixture doesn't say what the states mean, so the intended text is unknown.
- **Smallest fix:** Pair the color with visible text or a distinct symbol, for example `Label("Ready", systemImage: "checkmark.circle")` versus an error symbol. Add `.accessibilityLabel` and `.accessibilityValue` if the dot stays.
- **Automated check:** A UI test asserts that an element carrying the status text or value exists for both the empty and non-empty `message` states. `performAccessibilityAudit()` may not flag this, so don't rely on it alone.
- **Device check:** Use VoiceOver, grayscale and Differentiate Without Color to confirm both states are distinguishable.

### 3. Dynamic Type capped at `.large` (High)
- **Affected users:** Low-vision users who set a text size above Large, including the accessibility sizes.
- **Evidence:** `.dynamicTypeSize(...DynamicTypeSize.large)` is applied to the whole screen. Text in it stops growing at Large, which is below the default size range's top end and well below the accessibility sizes.
- **Smallest fix:** Remove the cap. If layout breaks at large sizes, fix the layout instead, for example with `ViewThatFits` or a vertical `HStack` fallback.
- **Automated check:** Snapshot or UI tests at `.accessibility3` or higher, and `performAccessibilityAudit(for: .dynamicType)`.
- **Device check:** Set Settings > Accessibility > Display & Text Size > Larger Text to maximum and confirm nothing is clipped, truncated or unreachable.

### 4. Accessibility focus moved on every `message` change (Medium)
- **Affected users:** VoiceOver users.
- **Evidence:** `.onChange(of: message) { focused = true }` runs on every change. `.accessibilityFocused($focused)` is attached to the whole `VStack` rather than a specific element. A Bool that is never reset to `false` may not re-trigger after the first time. The fixture contains nothing that edits `message`, so the real trigger is unverified.
- **Smallest fix:** Move focus only for a deliberate event, such as an error or confirmation. Attach the focus state to that specific element, and reset it afterwards.
- **Automated check:** Unit or UI tests that the focus-changing path runs only for the intended state transition.
- **Device check:** With VoiceOver, confirm focus doesn't jump while the user is navigating. When it does move, check that it lands on a sensible element. Don't assume exact speech.

## Not reported (unsupported by the fixture)
- **`WebView(url: accountURL)`:** Accessibility depends on the page content and on what `WebView` is, and neither is shown.
- **Delete without confirmation:** The `delete` body isn't shown.
- **`onChange` signature:** The zero-parameter form needs iOS 17+, and the deployment target isn't in the fixture.
