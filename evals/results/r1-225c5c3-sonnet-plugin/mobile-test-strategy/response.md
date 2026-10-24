# Checkout accessibility test strategy

**Discovery status:** The working directory is empty, and `CheckoutRequirements.md` isn't on disk. I used the requirements as you pasted them. I found no Gradle modules, Xcode schemes, source sets, simulators or CI config, so I ran no commands. I created and edited no files. The layers below are a plan, and every target name still has to be confirmed. Run `./gradlew projects` and `tasks --all`, `xcodebuild -list` and `-showdestinations`, and check the CI config first. Add tests only to targets that already exist.

## Assertions by layer

| # | Requirement | Narrowest reliable layer | Assertion (observable behavior) |
|---|---|---|---|
| 1 | Shared KMP validation rejects an empty cardholder name | `commonTest` | Empty and whitespace-only names return the invalid result with the "name required" error code. A valid name passes. Assert a typed error or message key, not rendered text. |
| 2a | Compose exposes the validation error | Compose semantics test. Use a host test only if Robolectric is already configured. Otherwise use `androidTest`. | The name field's node has `SemanticsProperties.Error` set to the expected message. The error is on the field node, not only in a separate text node. |
| 2b | SwiftUI exposes the validation error | XCUITest, because SwiftUI structure can't be checked in plain XCTest | After submitting an empty name, the field's `accessibilityValue` or label includes the error. Or the error element exists in the hierarchy and is associated with the field. |
| 3a | Slider supports equivalent increment and decrement | Android: Compose semantics test | The node has `SetProgress` or `ProgressBarRangeInfo`, plus custom actions if the control uses them. Invoking increase and then decrease through semantics actions returns the value to its start. Check that the step size matches on both directions. |
| 3b | Same slider on iOS | XCUITest | The element has the adjustable trait. `adjust(toNormalizedSliderPosition:)`, or increment and decrement on the element, changes `value` by the same step in each direction. If the control is UIKit, XCTest can check the traits and `accessibilityIncrement` and `accessibilityDecrement` directly. |
| 3c | Shared step logic, if any | `commonTest` | Increment followed by decrement is symmetric, and values clamp at the minimum and maximum. |
| 4a | Overlay traps focus | Android: `androidTest` for the dialog or window behavior. iOS: XCTest for `accessibilityViewIsModal` if the overlay is UIKit, otherwise XCUITest. | Content behind the overlay is not reachable. On iOS, behind-overlay elements are not hittable or not in the hierarchy. On Android, the underlying content is hidden from semantics or the dialog is a separate window. |
| 4b | Overlay restores focus on dismissal | Instrumentation (Android) and XCUITest (iOS) | After dismissal, the opener control is present and enabled, and the overlay is gone. Android needs instrumentation because focus is framework-level. The tests can check input focus, not TalkBack or VoiceOver focus. |
| 5 | No payment details in screenshots, logs or artifacts | `commonTest` for redaction. Test-data review for artifacts. | Redaction or masking functions never emit the card number, CVV or expiry. Tests use obvious dummy values such as a test PAN. Screenshot and snapshot tests are not used on payment screens, or they mask the fields. Review CI artifact upload paths. A log-capture test can assert that dummy values don't appear in captured output. |
| 6 | CI proves exact TalkBack and VoiceOver announcement text | **Not achievable in CI.** See below. | |

## Requirement 6 can't be met as written
No unit, Compose semantics, simulator, snapshot, Accessibility Inspector or XCUITest result proves what TalkBack or VoiceOver says aloud. Speech depends on the screen-reader version, its settings, the locale and the order of announcements. CI can only check the inputs to speech:

- the label, value, state and error properties
- the role and traits
- the available actions

Recommend rewording to: "CI asserts that the semantic properties behind announcements are correct. Spoken output is verified manually on real devices at each release." Product should accept this change before the strategy is signed off.

## Cross-cutting constraints
- **Privacy:** Use fake payment data only. Don't capture screenshots, video or full view-hierarchy dumps from the card entry screens. Make sure test failure reports don't print field contents.
- **Android scanner checks:** If the project uses `enableAccessibilityChecks()`, run it in `androidTest` on API 34 or higher only. It passes silently under Robolectric, so a green host-test result there is not evidence.
- **iOS audit:** Run `performAccessibilityAudit(for:)` as supplemental evidence with narrow suppressions. Never use a blanket `{ _ in true }` handler.
- **Test the properties, not spoken sentences:** Assert the error property, value, role and actions, not a full spoken sentence.

## Needs a real device and assistive technology
These cannot be settled by any automated layer:
1. **TalkBack and VoiceOver announcement text and order.** Check that the validation error is announced when it appears, and read in context with the field.
2. **Slider:** Swipe up and down in TalkBack, and use VoiceOver adjustable swipes. Confirm the spoken value is meaningful and that increment and decrement feel equivalent.
3. **Overlay:** Confirm the screen reader cannot reach content behind it. Confirm focus lands on the overlay when it opens and returns to the opening control when it closes. This includes TalkBack accessibility focus, which Compose can't request through a stable public API.
4. **Voice Control, Voice Access, Switch Access and Switch Control, and keyboard** for the error, slider and overlay flows.
5. **Large font and Dynamic Type** at the largest size, to confirm the error text and overlay still fit.
6. **Privacy spot-check:** Inspect the artifacts of a real CI run and a device session for leaked payment data.

Record each manual check with device, OS build, app build, assistive technology and settings, locale and font size, exact steps, and expected versus actual results. Keep any screenshots free of payment data.

## Results report

- **Changed test files:** none. This was a planning task with no files created or modified.
- **Commands run:** none. Nothing was discovered to run against.
- **Pass, fail, skip:** none. No tests were run.
- **Coverage gaps:**
  - Nothing is implemented or verified yet.
  - The test targets and source sets are unconfirmed.
  - The simulator and device requirements are unknown.
  - The CI constraints are unknown.
  - Requirement 6 can't be met in CI.
- **Required device checks:** items 1–6 above.

**Next step:** Share the repository, or confirm that the fixture file should exist at that path. Then I can run discovery and map each row to a real target.
