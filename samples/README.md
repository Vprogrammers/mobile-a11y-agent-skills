# Samples

Minimal projects that compile the “Better” examples from the skill references and the eval fixtures. They catch API drift and keep fixtures valid code; they do not demonstrate a full app.

| Project | Contents | Command |
|---|---|---|
| `android/` | Compose and Views patterns; Robolectric semantics tests; compiled copies of the `android-compose-review`, `android-views-review`, and `clean-compose-review` fixtures | `./gradlew assembleDebug testDebugUnitTest` |
| `ios/` | SwiftUI and UIKit patterns; XCTest property tests; compiled copies of the `ios-swiftui-review` and `ios-uikit-review` fixtures | `./test.sh` |

Eval fixtures are given to agents without package or import lines, so the samples compile generated copies with a header (`android/eval-fixture-header.kt.txt`, `ios/test.sh`) and stubs for undeclared helpers. Do not add imports to the fixtures themselves. `kmp-boundary-review` is not compiled because it intentionally places platform types in common code.

`EvalFixturesTest` (Android) and `ProfileViewControllerFixtureTests` (iOS) fail when a fixture no longer contains a defect its rubric expects, or when the clean fixture gains one. Test names end with the rubric finding id. The `kmp-boundary-review` and `ios-swiftui-review` fixtures are guarded statically by `tests/test_eval_fixtures.py`, because the first cannot compile and SwiftUI modifiers cannot be inspected from XCTest without a third-party dependency.

Android requires JDK 17 and an Android SDK with platform 37 (set `ANDROID_HOME` or `local.properties`). Robolectric runs with SDK 34 so it stays compatible with JDK 17. iOS requires Xcode with an iPhone simulator runtime.

These tests assert exposed semantics and accessibility properties. They do not prove TalkBack or VoiceOver speech or navigation; report device verification separately.

When you change a code example in a reference file or an eval fixture, update the matching sample or guard test in the same pull request.
