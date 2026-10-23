# Accessibility test matrix

Last reviewed: 2026-10-23

## Discover before writing tests

Android/KMP examples:

```bash
./gradlew projects
./gradlew tasks --all
./gradlew test
./gradlew connectedCheck
```

Run the narrowest existing task after discovery; do not invent module task names. Determine whether Compose host tests use Robolectric and whether an emulator/device is available.

iOS examples:

```bash
xcodebuild -list -project App.xcodeproj
xcodebuild -showdestinations -scheme App
xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'
```

Adapt workspace/project, scheme, configuration, and destination to the repository. Do not change signing merely to make a test run.

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

- Use Compose semantics matchers and assertions against merged and unmerged trees intentionally.
- Use `enableAccessibilityChecks()` when supported by the Compose testing dependency.
- Use `AccessibilityChecks.enable()` for Espresso/View tests.
- Use Android Accessibility Scanner for exploratory device evidence.
- Test node role/state/actions/errors rather than hard-coding a full spoken sentence.

## Apple APIs

- Use accessibility identifiers for automation, not as user-facing labels.
- Assert labels, values, enabled/selected state, actions, and flow completion in XCUITest.
- Use `performAccessibilityAudit(for:)` on supported Xcode/iOS versions and document issue types or exclusions.
- Use Accessibility Inspector for hierarchy, hit regions, contrast, and manual auditing.

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
