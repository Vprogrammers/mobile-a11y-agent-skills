# Accessibility test matrix

Last reviewed: 2026-10-23. Verify test API availability against the Compose, Robolectric, Xcode, and iOS versions used by the project.
Review interval: 180 days.

## Discover before writing tests

Android/KMP examples:

```bash
./gradlew projects
./gradlew tasks --all
./gradlew test
./gradlew connectedCheck
```

Run the narrowest existing task after discovery; do not invent module task names. Determine whether Compose host tests use Robolectric and whether an emulator/device is available. Robolectric runs against one SDK per sandbox; recent SDK sandboxes can require a newer JDK than the build uses, so pin the sandbox SDK explicitly (for example in `robolectric.properties`) when the JDK is fixed.

iOS examples:

```bash
xcodebuild -list -project App.xcodeproj
xcodebuild -showdestinations -scheme App
xcodebuild test -scheme App -destination 'id=<simulator-udid>'
```

Adapt workspace/project, scheme, configuration, and destination to the repository. Choose the destination from `xcrun simctl list devices available` or `-showdestinations`; a device name alone can match several installed runtimes. Do not change signing merely to make a test run.

## Layer selection

| Requirement | First automated layer | Device verification |
|---|---|---|
| Shared validation/state/privacy | `commonTest` or common unit test | Usually no |
| Compose semantics | Compose host test if supported; otherwise instrumentation | TalkBack navigation |
| Views accessibility node/actions | Robolectric where faithful; otherwise instrumentation | TalkBack/Voice Access |
| Android focus, IME, autofill, WebView | Instrumentation/integration | Real service and assistive technology |
| SwiftUI/UIKit label, value, action | XCTest/XCUITest | VoiceOver navigation |
| iOS accessibility audit | XCUITest on supported OS | Triage and manual verification |
| Voice Control input labels | XCUITest presence/flow | Voice Control overlay |
| Dynamic Type/font scale | Layout/snapshot assertions | Largest supported size |
| Reduced motion | Policy/state test | Visual device check |
| Contrast algorithm | Unit test | Inspect rendered dynamic backgrounds |
| Exact screen-reader speech | Not a reliable unit assertion | Real device required |

## Android APIs

- Use Compose semantics matchers and assertions against merged and unmerged trees intentionally: roles, text, state, actions, errors, and traversal metadata.
- Use `enableAccessibilityChecks()` on the Compose test rule from Compose 1.8 with the `ui-test-junit4-accessibility` dependency. Treat results as heuristics and suppress false positives narrowly.
- Use `AccessibilityChecks.enable()` for Espresso/View tests.
- Use Android Accessibility Scanner for exploratory device evidence.
- Use instrumentation or device tests for IME, autofill, framework focus, WebView, insets, back handling, and window behavior.
- Test node role/state/actions/errors rather than hard-coding a full spoken sentence.

## Apple APIs

- Use accessibility identifiers for automation, not as user-facing labels.
- Assert labels, values, enabled/selected state, actions, and flow completion in XCUITest.
- Use `performAccessibilityAudit(for:)` on supported Xcode/iOS versions and document issue types or exclusions.
- Use Accessibility Inspector for hierarchy, hit regions, contrast, and manual auditing.
- Use XCTest for view-model and UIKit adapter properties (traits, values, custom actions, `accessibilityViewIsModal`); SwiftUI accessibility structure needs XCUITest or Accessibility Inspector.

## Manual device checks

- Android: TalkBack, Voice Access, Switch Access, hardware keyboard, font scale and display size, RTL, dark theme, removed animations, three-button and gesture navigation.
- iOS: VoiceOver navigation and rotor, Voice Control, Switch Control, Full Keyboard Access, Dynamic Type accessibility sizes, Large Content Viewer, Reduce Motion, Increase Contrast, Reduce Transparency.
- Compose Multiplatform on iOS: run the iOS list against the Compose UI itself; do not infer iOS behavior from Android semantics tests.

## Manual device record

Record:

- device and OS build;
- app build/configuration;
- assistive technology and relevant settings;
- locale, font size, display size, appearance, and orientation;
- start state and exact steps;
- expected and actual results;
- screenshots/video only when they do not expose sensitive data.

Do not report “accessibility passed” from a green automated suite. Report which observable requirements passed and which assistive-technology behaviors remain unverified.

Official sources:

- Compose accessibility testing: https://developer.android.com/develop/ui/compose/accessibility/testing
- Espresso accessibility checks: https://developer.android.com/training/testing/espresso/accessibility-checking
- Robolectric configuration: https://robolectric.org/configuring/
- XCUITest audits: https://developer.apple.com/documentation/xctest/xcuiapplication/performaccessibilityaudit(for:)
- Compose Multiplatform iOS accessibility: https://kotlinlang.org/docs/multiplatform/compose-ios-accessibility.html
