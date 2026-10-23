# Samples

Minimal projects that compile the “Better” examples from the skill references and the eval fixtures. They exist to catch API drift, not to demonstrate a full app.

| Project | Contents | Command |
|---|---|---|
| `android/` | Compose and Views patterns, Robolectric semantics tests, `android-compose-review` and `compose-clean-control` fixtures | `./gradlew assembleDebug testDebugUnitTest` |
| `ios/` | SwiftUI and UIKit patterns, XCTest property tests, `ios-swiftui-review` fixture (`Sources/EvalFixtures` is a symlink) | `./test.sh` |

Android requires JDK 17 and an Android SDK with platform 37 (set `ANDROID_HOME` or `local.properties`). Robolectric runs with SDK 34 so it stays compatible with JDK 17. iOS requires Xcode with an iPhone simulator runtime.

These tests assert exposed semantics and accessibility properties. They do not prove TalkBack or VoiceOver speech or navigation; report device verification separately.

When you change a code example in a reference file, change the matching sample in the same pull request.
