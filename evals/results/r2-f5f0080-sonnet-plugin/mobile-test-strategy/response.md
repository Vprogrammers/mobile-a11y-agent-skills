# Checkout accessibility test strategy

**Discovery status:** The working directory is empty, and `CheckoutRequirements.md` isn't on disk. I used the fixture text you pasted and treated it as data. I found no Gradle modules, source sets, Xcode schemes, simulators or CI config. I wrote no files, ran no commands and made no test runs. Before any test is written, someone must run these discovery commands:
- `./gradlew projects` and `./gradlew tasks --all`
- `xcodebuild -list` and `xcodebuild -showdestinations`

Tests go only into targets that already exist. If a layer has no target, that's a gap to report, not a reason to create one.

## Assertion-to-layer assignment

| # | Requirement | Narrowest reliable layer | Assertion (observable behavior) | Still needs a device and assistive technology |
|---|---|---|---|---|
| 1 | Shared KMP validation rejects an empty cardholder name | `commonTest` (plain unit test) | An empty name gives an invalid result with the "name required" error code. Also test a whitespace-only name and a valid name. Use a stable error code or key, not localized prose. | None. |
| 2a | Compose exposes the validation error | Compose semantics test. Use a host test only if Robolectric is already configured. Otherwise use instrumentation. | The text field node has `SemanticsProperties.Error` equal to the expected message. | TalkBack reads the error when the field is focused or the error appears. |
| 2b | SwiftUI exposes the validation error | XCUITest on a simulator | After submitting an empty name, the error element exists. The field's accessibility value or the error element carries the message. | VoiceOver reads the error. Check that focus or an announcement surfaces it. |
| 2c | Shared-to-native wiring | Thin native adapter tests, if the adapters exist | Each platform maps the shared error code to its own localized string. | Localization review on device. |
| 3 | Custom slider has equivalent increment and decrement actions | Android: Compose semantics test. iOS: XCUITest. | Android: assert `ProgressBarRangeInfo` and the `SetProgress` action. Perform it and check the value changes. Assert any custom increment and decrement actions, if present. iOS: assert an adjustable element. Call `adjust(toNormalizedSliderPosition:)` or the increment/decrement API and check the value changes. Test the shared step and clamp logic in `commonTest`: min, max, step and the increment/decrement symmetry. | TalkBack swipe-up/down or its adjust gesture. VoiceOver swipe-up/down. Confirm the spoken value is sensible and the action is discoverable. Test with Switch Access, Voice Control and Voice Access. |
| 4 | Confirmation overlay traps focus and restores it on dismiss | Android: instrumentation. iOS: XCUITest plus XCTest for any UIKit `accessibilityViewIsModal` adapter. | Android: assert background nodes aren't reachable while the overlay is up, and that dismiss and back work. Use a semantics test for the dialog or pane role and for hiding background content. Use instrumentation to check the input-focus target after dismiss. iOS: while the overlay is up, background elements are not hittable or not present in the accessibility tree. After dismiss, the triggering element exists. Don't assert accessibility focus position from XCUITest, because it can't observe it reliably. | **This is the biggest device gap.** The tests above prove input focus, node reachability and tree structure. They can't prove TalkBack or VoiceOver accessibility focus. On a device, check the swipe order inside the overlay, that the background can't be reached, and that focus returns to the trigger on dismiss. Also check keyboard focus and Switch Access. |
| 5 | Payment details must not leak into screenshots, logs or test artifacts | Unit and static layers, plus review of test configuration | Use synthetic fake card data only, such as a clearly fake test number. Add a `commonTest` for any redaction or masking function. Add a test that `toString()` and logging of the payment model are masked, if such a model exists. Grep the CI artifacts and logs for the fake values as a gate. Disable screenshot, video and `xcresult` attachment capture for payment screens. Don't dump the full semantics tree or UI hierarchy for those screens. | Check on a device that the app screen is hidden in the recents switcher, and that screen recording or screenshots are handled per policy. Manually review artifacts from the first real run. Automation can't prove a negative across everything. |
| 6 | CI proves the exact TalkBack and VoiceOver announcement text | **Not achievable at any automated layer.** | Reframe it. Assert the inputs to speech instead: role, state, value, error, label and custom actions. Don't hard-code full spoken sentences. | A real device with TalkBack or VoiceOver is required. Record device, OS build, settings and steps with the real-device evidence template. A person (or a vetted device farm with the real screen reader) records the observed speech. |

## Requirement 6

CI cannot prove exact TalkBack or VoiceOver announcement text, and no unit, semantics, simulator, snapshot, Accessibility Inspector or XCUITest output can. Speech depends on the OS version, the screen-reader version, the user's verbosity settings, the language, the voice and the rotor or reading settings. Push back on this requirement to Product. The strategy replaces it with two parts:
1. CI proves the properties that feed speech: label, role, value, state, error and actions.
2. A scripted manual device pass records the observed speech per release.

## Supplemental automated checks

These add evidence but don't prove assistive-technology behavior.
- **Android:** `enableAccessibilityChecks()` in instrumented tests on API 34 or later. It silently passes on Robolectric, so never count a host-test result. Treat findings as heuristics and suppress false positives narrowly.
- **iOS:** `performAccessibilityAudit(for:)` with explicit audit types. Never use `{ _ in true }`. Triage each issue and suppress by audit type and element identifier.
- **Both:** Check large font and Dynamic Type layout. Check touch target size (48 dp on Android, 44 pt on iOS).

## Required device checks

Record each one using the real-device evidence template. Use synthetic card data and don't capture the payment fields in screenshots or video.
1. TalkBack and VoiceOver on the empty-name error: confirm it's perceivable and that focus or an announcement handles it.
2. Slider adjustment with TalkBack and VoiceOver. Add Switch Access, Voice Control, Voice Access and the keyboard where relevant.
3. Overlay focus trap and restore with both screen readers. Cover back and dismiss gestures, and check that nothing in the background can be reached.
4. The exact announcement text, recorded as observation only.
5. Large font, Dynamic Type accessibility sizes and RTL on the checkout screens.
6. Recents and screenshot privacy for the payment screens.

## Coverage gaps and open items

- The source sets, test targets, Robolectric setup, emulator or simulator availability and CI constraints are all unknown until discovery.
- I don't know whether iOS uses native SwiftUI or Compose Multiplatform. The fixture mentions SwiftUI, so I assumed native UI. If any iOS screen is Compose Multiplatform, test that screen on iOS itself. Don't infer its behavior from Android semantics tests.
- Automation can't verify accessibility focus placement, so requirement 4 stays only partly verified until a device check is done.
- The privacy requirement (5) can only be partly verified by automation.
- Nothing was run, so there are no pass, fail or skip results.

I could not delegate to the `accessibility-test-engineer` agent from this session, so I applied the skills directly. The strategy is the same either way.

**Changed test files:** none.
**Commands run:** none. Only the skill reference and the file search were used.
