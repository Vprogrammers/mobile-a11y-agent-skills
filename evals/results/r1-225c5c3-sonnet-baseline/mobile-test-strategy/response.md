# Checkout accessibility test strategy

I worked from the fixture text you pasted and didn't open or edit the file.

## Assignment by layer

| # | Requirement | Narrowest reliable layer | Assertion |
|---|---|---|---|
| 1 | KMP validation rejects empty cardholder name | **Shared `commonTest` unit test** (no UI, no device) | Empty, whitespace-only and valid names return the expected error code or type. Assert on a stable error key, not on display text. |
| 2 | Compose and SwiftUI expose the validation error | **Per-platform component tests**: Compose UI test with semantics matchers, and XCTest/ViewInspector or an XCUITest on a simulator | Given the invalid state, the field's accessibility tree has an error state or description (Compose `error()` semantics, SwiftUI `accessibilityValue`/`accessibilityHint`, or a linked label). The error node is present, not hidden, and associated with the field. Also check that it is not conveyed by color alone. |
| 3 | Slider supports equivalent increment/decrement | **Per-platform component tests** | Compose: assert `SemanticsActions.SetProgress` or custom actions exist, then invoke them and check the value changes by the expected step, clamped at min and max. SwiftUI: `accessibilityAdjustableAction` increments and decrements by the same step, and `accessibilityValue` updates. Shared step logic, if it exists, gets a `commonTest`. |
| 4 | Overlay traps focus and restores it on dismiss | **Split.** Component tests cover structure. A real device covers behavior. | Component tests: the overlay is marked modal (Compose `isTraversalGroup` plus `Modifier.semantics { }` hiding the background, SwiftUI `.accessibilityAddTraits(.isModal)`), background nodes are not reachable, and the state or focus target is set on dismiss. Real focus movement can't be trusted in simulators. See the device section. |
| 5 | Payment details never in screenshots, logs or artifacts | **Static and CI-hygiene checks, plus a negative test** | Use synthetic test card data only, with a recognizable sentinel PAN. Add a CI step that greps logs, test reports and screenshot or video artifacts' metadata and text for the sentinel and for PAN-shaped strings. Mark the payment fields as secure so screenshots are blocked or masked (`FLAG_SECURE`, secure text entry). Disable screenshot and video capture for the payment screens in the test runner. Lint for logging calls near payment models. |
| 6 | CI proves the exact TalkBack and VoiceOver announcement text | **Not provable in CI as stated.** Push back on the requirement. | Replace it with two things. CI asserts the strings handed to the accessibility API: the label, value, hint and error text in the semantic tree, which is what the screen reader reads. Manual device QA confirms what is actually spoken. |

## Why requirement 6 can't be met as written

Neither screen reader exposes its spoken output to automated tests. Actual speech depends on:
- OS version
- screen reader version
- user verbosity settings
- language
- how the reader composes label, role, state and hint

A CI assertion on "exact announcement text" would therefore be either a restatement of the semantic properties, which is the layer-2 check, or flaky. I'd propose to Product: "CI verifies the semantic content supplied to TalkBack and VoiceOver. A release checklist verifies spoken output on devices."

## What still needs a real device with assistive technology

Run these with TalkBack on at least one physical Android device, and VoiceOver on at least one physical iPhone:

1. **Spoken output for the validation error** (req. 2, 6). Check that it is announced when it appears, either through focus or a live region or announcement, and that the wording is sensible. Don't gate on exact text.
2. **Slider adjustment** (req. 3). Swipe up and down (VoiceOver) or use volume keys or actions (TalkBack). Confirm the spoken value and step feel right, and that the increment and decrement actions are discoverable.
3. **Overlay focus** (req. 4). Check that:
   - Focus moves into the overlay when it opens.
   - Swipe navigation can't escape to the background.
   - The escape or dismiss gesture works (VoiceOver two-finger scrub, TalkBack back).
   - Focus returns to the triggering control after dismissal.
4. **Payment privacy in a real session** (req. 5). Confirm that no card data appears in the screen reader's output history, the system screenshot or recents preview, or any captured logs. Use test cards only.
5. **Other checks:** large font and display scaling, and external keyboard or switch access if those are in scope.

## Minimal execution plan

- **Every PR:** `commonTest` (req. 1), Compose and SwiftUI semantic tests (reqs. 2–4 structure), and the artifact-leak scan (req. 5).
- **Nightly or pre-release:** simulator-based UI smoke tests, if they exist, run with accessibility audit tooling (for example Android's Accessibility Test Framework checks and Xcode's `performAccessibilityAudit`).
- **Release gate:** a short manual TalkBack and VoiceOver script covering the five device items above, with results recorded without any real payment data.

Items 1–3 are cheap, deterministic and give most of the coverage. The device checklist is small because it only covers what automation can't observe.
