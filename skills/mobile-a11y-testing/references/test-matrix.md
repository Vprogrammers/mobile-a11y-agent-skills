# Accessibility test matrix

| Requirement | First automated layer | Device verification |
|---|---|---|
| Input normalization | Common unit test | No |
| Progress or masked description | Common unit test | Confirm spoken result |
| Compose semantics | Host or device semantics test | TalkBack navigation |
| Android focus and IME | Device test | TalkBack and keyboard |
| Android autofill | Device or integration test | Real SMS/autofill flow |
| SwiftUI/UIKit label and value | XCTest or XCUITest | VoiceOver navigation |
| iOS automated accessibility audit | XCUITest | Triage on target OS |
| Voice Control input labels | XCUITest presence check | Voice Control overlay |
| Dynamic Type or font scale | Snapshot/layout assertions | Largest supported size |
| Reduced motion | State or animation policy test | Visual device check |
| Contrast calculation | Unit test | Inspect dynamic/material backgrounds |
| Exact screen-reader speech | Not reliable as a unit assertion | Real device required |

Do not use accessibility identifiers as user-facing labels. Keep automation hooks separate from accessibility copy unless the platform API intentionally combines them.
