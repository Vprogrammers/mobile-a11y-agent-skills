# Samples

Minimal projects that compile the “Better” examples from the skill references and the eval fixtures. They catch API drift and keep fixtures valid code; they do not demonstrate a full app.

| Project | Contents | Command |
|---|---|---|
| `android/` | Compose and Views patterns; Robolectric semantics tests; compiled copies of the Compose and Android Views fixtures, including both defect-bearing and clean cases | `./gradlew assembleDebug testDebugUnitTest` |
| `ios/` | SwiftUI and UIKit patterns; XCTest property tests; compiled copies of the SwiftUI and UIKit fixtures, including both defect-bearing and clean cases | `./test.sh` |
| `kmp/` | Shared `ValidationState`, `AccessibilityPreferences`, and `MotionPolicy` in `commonMain`; Compose `error()` and animator-scale adapters in `androidMain`; the UIKit Reduce Motion adapter in `iosMain`; common, Robolectric, and iOS simulator tests; an exported-header check | `./gradlew check` |

Eval fixtures are given to agents without package or import lines, so the samples compile generated copies with a header (`android/eval-fixture-header.kt.txt`, `ios/test.sh`) and stubs for undeclared helpers. Do not add imports to the fixtures themselves. `kmp-boundary-review` is not compiled because it intentionally places platform types in common code.

`EvalFixturesTest` (Android), `ProfileViewControllerFixtureTests`, and `ReceiptCellFixtureTests` (iOS) fail when a fixture no longer contains a defect its rubric expects, or when the clean fixture gains one. Test names end with the rubric finding id. The `kmp-boundary-review`, SwiftUI modifier findings, and prose regulatory fixtures are also guarded statically by `tests/test_eval_fixtures.py` when compilation cannot prove the rubric criterion. Static guards keep fixture evidence aligned with finding IDs; they do not prove runtime accessibility behavior.

Android requires JDK 17 and an Android SDK with platform 37 (set `ANDROID_HOME` or `local.properties`). Robolectric runs with SDK 34 so it stays compatible with JDK 17. iOS requires Xcode with an iPhone simulator runtime. KMP requires both and runs on macOS. Its `checkExportedHeader` task links the debug framework for the host simulator architecture. The header must contain the shared contract and no UIKit or Compose types.

`AccessibilityChecksTest` documents an evidence limit: Compose accessibility checks pass silently on Robolectric, so they must run in instrumented tests on API 34+.

These tests assert exposed semantics and accessibility properties. They do not prove TalkBack or VoiceOver speech or navigation; report device verification separately.

When you change a code example in a reference file or an eval fixture, update the matching sample or guard test in the same pull request.
