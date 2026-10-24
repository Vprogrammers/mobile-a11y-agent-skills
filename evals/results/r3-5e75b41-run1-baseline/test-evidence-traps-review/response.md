**Verdict:** the evidence supports almost none of the stated conclusions. The one exception is that the iOS suite runs without crashing, and it proves little else.

## Android

**Accessibility checks (38 passing tests)**
- **What it supports:** the tests ran and nothing threw. That is all.
- **What it does not support:** "no touch-target, contrast, or missing-label problems." There are three reasons.
  - **The check may be a no-op.** `tryPerformAccessibilityChecks()` is the lenient variant, and I'd verify whether it can fail a test at all. Compose accessibility checks are also designed for instrumented runs. Robolectric has no real rendering, so contrast and pixel-size checks are unreliable there. A green result can't be told apart from checks that never ran.
  - **The scope is narrow.** The tests cover one default state per screen. Error, empty, loading, dialog, and bottom-sheet states are not covered. The automated checks also flag only detectable issues. They can't tell whether a label is meaningful, so "no missing-label problems" overreaches.
- **Smallest fix:**
  - Add a deliberately broken fixture screen, such as a 20dp clickable with no label and low contrast. Confirm the suite fails on it.
  - Move or duplicate the suite as instrumented tests on a real emulator or device, using `performAccessibilityChecks()` so failures throw.
  - Report any suppressed checks and states explicitly.

**Paparazzi snapshots at font scale 1.0 and 2.0**
- **What it supports:** nothing positive. Identical output at 2.0 and 1.0 is a red flag, not proof. It most likely means the font scale was never applied, or the text uses fixed sizes that ignore scaling. That would be a real defect.
- **What it does not support:** "text scales without clipping." Even with different images, snapshot equality checks that output hasn't changed. It doesn't check that the layout is correct.
- **Smallest fix:**
  - Assert that the 2.0 images differ from the 1.0 images, and confirm the config sets `fontScale`.
  - Review the 2.0 images by eye, or add overflow and ellipsis assertions.
  - Use long strings and also test the largest OS scale (about 2.0) plus display size.
  - Spot-check on a device.

## iOS

**`performAccessibilityAudit { _ in true }`**
- **What it does not support:** "zero failures." The issue handler returns `true` for every issue, which means "this issue is handled, ignore it." Every finding is suppressed, so the suite cannot fail. The result is vacuous.
- **What it supports:** that the app launched and the audit API ran.
- **Other gaps:**
  - "Launches every screen" doesn't mean each screen was audited in its meaningful states.
  - Only iOS 26 is covered.
- **Smallest fix:**
  - Remove the closure, or make it return `true` only for specific, documented exceptions, each with a tracked issue.
  - Log all issues, then confirm the suite fails against a seeded violation, such as a small unlabeled button.
  - Run the audit on the navigated and populated states, and also at a large Dynamic Type size.

## Conclusion

- **Not supported:** "TalkBack and VoiceOver work correctly" and "no device testing needed."
  - Neither suite drives a screen reader.
  - Neither suite checks focus order, reading order, announcements, custom actions, or whether the experience is usable.
- **Needed instead:**
  - A short manual pass with TalkBack and VoiceOver on real devices covering the critical user journeys.
  - Keyboard and switch access checks if those are in scope.
- **Until the fixes above land:** describe the automated suites as "smoke checks of unknown sensitivity" and don't use them as release evidence. The manual pass is the only way to support the assistive-technology claim.
