# Review of `AccountScreen.swift`

I reviewed only the inline fixture and did not edit anything. The findings are ordered by severity.

## 1. Edit and Delete are merged into one accessibility element
- **Severity:** High. Delete is destructive, and Edit may be unreachable.
- **Affected users:** VoiceOver, Switch Control, and Voice Control users.
- **Evidence:** `.accessibilityElement(children: .combine)` sits on the `HStack` that holds both buttons. This folds the children into a single element, so the two controls may no longer be separately focusable or activatable.
- **Smallest fix:** Remove the modifier. If you want grouping, use `.accessibilityElement(children: .contain)`, which keeps each button individually reachable.
- **Automated verification:** Write an XCUITest that asserts `app.buttons["Edit"]` and `app.buttons["Delete"]` both exist and are `isHittable`. Run `performAccessibilityAudit()` as well.
- **Real-device checks:**
  - Swipe through the screen with VoiceOver and confirm you can reach and activate each button on its own.
  - Check Switch Control navigation.
  - Say "Tap Edit" and "Tap Delete" with Voice Control.

## 2. Status is conveyed by color only
- **Severity:** High. This fails WCAG 1.4.1 (use of color) and 1.1.1 (non-text content).
- **Affected users:** Color-blind users, low-vision users, and VoiceOver users.
- **Evidence:** The `Circle` is filled red or green based on `message.isEmpty`. It has no text, shape difference, or `accessibilityLabel` or `accessibilityValue`. Nothing in the fixture tells assistive tech what it means, and I can't tell what red and green stand for from the code.
- **Smallest fix:** Add a visible text or icon state, such as a label with a checkmark or warning symbol. Give the indicator an `accessibilityLabel` and `accessibilityValue`. If the state is already shown as text, mark the circle `.accessibilityHidden(true)`.
- **Automated verification:** Add a UI test that asserts the status text or element exists in both states. A unit test can check that the state-to-label mapping differs between the two. The accessibility audit won't reliably catch color-only meaning.
- **Real-device checks:**
  - Use color-filter or grayscale settings.
  - Turn on Differentiate Without Color.
  - Confirm with VoiceOver that the state is discoverable.

## 3. Dynamic Type is capped at `.large`
- **Severity:** Medium to High. This fails WCAG 1.4.4 (resize text).
- **Affected users:** Low-vision users who rely on larger text sizes.
- **Evidence:** `.dynamicTypeSize(...DynamicTypeSize.large)` prevents text from growing past the default size.
- **Smallest fix:** Remove the cap. If a layout breaks at larger sizes, fix the layout, for example with `ViewThatFits` or a vertical stack. If a cap is truly needed, raise it into the accessibility range.
- **Automated verification:**
  - Render previews or snapshots at `.accessibility3` and above.
  - Run the UI test with a launch argument for an accessibility content size category.
  - Run the audit's Dynamic Type check.
- **Real-device checks:** Set Larger Text to its maximum with Larger Accessibility Sizes on. Confirm that nothing is clipped, that buttons stay reachable, and that the screen scrolls if needed. The `VStack` isn't in a `ScrollView`, so overflow is a risk.

## 4. Focus handling is likely to be ineffective or disruptive
- **Severity:** Medium.
- **Affected users:** VoiceOver and Switch Control users.
- **Evidence:**
  - `.accessibilityFocused($focused)` is applied to the container `VStack`, not to a specific element.
  - `.onChange(of: message) { focused = true }` sets focus on every change. It never resets to `false`, so once `focused` is `true`, later sets are no-ops.
  - Nothing in the fixture ever modifies `message`, so I can't see what triggers this.
- **Smallest fix:** Don't move focus on a value change. To announce a status update, post an `AccessibilityNotification.Announcement`. If focus must move, bind it to the specific element that changed, and reset the flag afterward.
- **Automated verification:** A UI test can change `message` and assert that focus does not jump unexpectedly. Automated coverage of focus is limited.
- **Real-device checks:** Trigger the change while VoiceOver focus is on Edit or Delete. Confirm that focus isn't stolen mid-interaction and that the update is perceivable.

## Not assessable from the fixture
- `WebView(url: accountURL)`, `accountURL`, `edit`, and `delete` are undefined here, so I can't judge the web content's accessibility, its reading order, or any title or label for it. Check the web content on a device with VoiceOver and with text scaling.

I made no claims about the exact VoiceOver speech.
