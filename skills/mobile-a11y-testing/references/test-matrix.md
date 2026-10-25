# Accessibility test matrix

Last reviewed: 2026-10-25. Verify test API availability against the Compose, Robolectric, Xcode, and iOS versions used by the project.
Review interval: 180 days.

## Discover before writing tests

Android/KMP examples:

```bash
./gradlew projects
./gradlew :app:tasks --all
./gradlew :app:testDebugUnitTest --tests '*CheckoutScreenTest*'
```

List tasks first, then run the narrowest existing one, filtered to the affected tests; do not invent module task names. Avoid the aggregate `test` and `connectedCheck` tasks unless the change needs them: they run every module, and `connectedCheck` also needs an attached device or emulator. Determine whether Compose host tests use Robolectric and whether an emulator/device is available. Robolectric runs against one SDK per sandbox; recent SDK sandboxes can require a newer JDK than the build uses, so pin the sandbox SDK explicitly (for example in `robolectric.properties`) when the JDK is fixed.

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
| iOS accessibility audit | XCUITest on iOS 17 or later | Triage and manual verification |
| Voice Control input labels | XCUITest presence/flow | Voice Control overlay |
| Dynamic Type/font scale | Layout/snapshot assertions | Largest supported size |
| Reduced motion | Policy/state test | Visual device check |
| Contrast algorithm | Unit test | Inspect rendered dynamic backgrounds |
| Touch target size | Compose `assertHeightIsAtLeast`/`assertWidthIsAtLeast`; XCUITest `.hitRegion` audit | Switch Access/Control scanning |
| Right-to-left layout | Compose `DeviceConfigurationOverride.LayoutDirection`; XCUITest with `-AppleLanguages` | RTL locale on a device |
| Exact screen-reader speech | Not a reliable unit assertion | Real device required |

## Android APIs

- Use Compose semantics matchers and assertions against merged and unmerged trees intentionally: roles, text, state, actions, errors, and traversal metadata.
- Use `enableAccessibilityChecks()` (package `androidx.compose.ui.test.junit4.accessibility`, dependency `ui-test-junit4-accessibility`, Compose 1.8+) in instrumented tests on API 34+ devices or emulators. Its documentation states that it does not work on Robolectric, and in practice it passes silently there even for an unlabeled 16 dp target. Never report a green host-test accessibility check as evidence. Treat device results as heuristics and suppress false positives narrowly.
- Use `AccessibilityChecks.enable()` (`androidx.test.espresso.accessibility`, dependency `espresso-accessibility`) in instrumented Espresso/View tests.
- Use Android Accessibility Scanner for exploratory device evidence.
- Use instrumentation or device tests for IME, autofill, framework focus, WebView, insets, back handling, and window behavior.
- Test node role/state/actions/errors rather than hard-coding a full spoken sentence.
- Override device settings inside a Compose test with `DeviceConfigurationOverride`, for example `DeviceConfigurationOverride(DeviceConfigurationOverride.FontScale(2f)) { Screen() }` or `DeviceConfigurationOverride.LayoutDirection(LayoutDirection.Rtl)`.
- Check minimum sizes with `assertHeightIsAtLeast(48.dp)` and `assertWidthIsAtLeast(48.dp)`, and the expanded touch bounds with `assertTouchHeightIsEqualTo`/`assertTouchWidthIsEqualTo` when `minimumInteractiveComponentSize()` extends them.
- Read an action's label through `SemanticsActions.OnClick`, for example to assert an `onClickLabel`.

## Apple APIs

- Use accessibility identifiers for automation, not as user-facing labels.
- Assert labels, values, enabled/selected state, actions, and flow completion in XCUITest.
- Use `performAccessibilityAudit(for:)` (Xcode 15 and iOS 17 or later) and document issue types or exclusions.
- Launch the app at a Dynamic Type size with `app.launchArguments += ["-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"]`, and in a right-to-left language with `["-AppleLanguages", "(ar)"]`.
- Use Accessibility Inspector for hierarchy, hit regions, contrast, and manual auditing.
- Use XCTest for view-model and UIKit adapter properties (traits, values, custom actions, `accessibilityViewIsModal`); SwiftUI accessibility structure needs XCUITest or Accessibility Inspector.

## Examples

The repository samples compile these examples. The accessibility-checks example uses the same API with a placeholder screen. Adapt names to the project.

### Shared rule with a fake platform capability (`commonTest`)

```kotlin
private class FakeAccessibilityPreferences(reduceMotion: Boolean) : AccessibilityPreferences {
    override val reduceMotion = MutableStateFlow(reduceMotion)
}

@Test
fun reduceMotion_followsCurrentPreference() {
    val preferences = FakeAccessibilityPreferences(reduceMotion = false)
    assertEquals(MotionPolicy.Animated, motionPolicy(preferences))

    preferences.reduceMotion.value = true
    assertEquals(MotionPolicy.Reduced, motionPolicy(preferences))
}
```

### Compose semantics: assert properties, not speech

```kotlin
@Test
fun passwordField_exposesErrorAndPasswordSemantics() {
    rule.setContent { PasswordField(value = "", onValueChange = {}, errorMessage = "Enter your password") }

    rule.onNode(SemanticsMatcher.keyIsDefined(SemanticsProperties.EditableText))
        .assert(SemanticsMatcher.expectValue(SemanticsProperties.Error, "Enter your password"))
        .assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Password))
}
```

Use `useUnmergedTree = true` when the assertion concerns a descendant, such as a decorative icon that must stay hidden.

### Compose accessibility checks (instrumented, API 34+)

```kotlin
@Test
fun checkout_passesAccessibilityChecks() {
    rule.enableAccessibilityChecks()
    rule.setContent { CheckoutScreen() }
    rule.onRoot().tryPerformAccessibilityChecks()
}
```

Put this in `androidTest` or another device-backed source set, not in a Robolectric host test.

### XCUITest audit with narrow triage

```swift
try app.performAccessibilityAudit(for: [.dynamicType, .contrast, .hitRegion, .sufficientElementDescription]) { issue in
    // Return true only for a triaged false positive, matched as narrowly as possible.
    issue.auditType == .contrast && issue.element?.identifier == "decorative-watermark"
}
```

Bad: `try app.performAccessibilityAudit { _ in true }`. That suppresses every issue and turns the audit into a false pass.

### UIKit properties (XCTest)

```swift
func testModalCardIsModalWithHeaderTitle() {
    let card = ModalCardView()

    XCTAssertTrue(card.accessibilityViewIsModal)
    XCTAssertTrue(card.titleLabel.accessibilityTraits.contains(.header))
}
```

### Settings-dependent adapters

Test that native adapters read the platform setting. On Android, set `Settings.Global.ANIMATOR_DURATION_SCALE` in a Robolectric test. On iOS, compare with `UIAccessibilityIsReduceMotionEnabled()` on the simulator. These tests prove the mapping only. Verify the visual result with the real setting on a device.

## Manual device checks

- Android: TalkBack, Voice Access, Switch Access, hardware keyboard, font scale and display size, RTL, dark theme, removed animations, three-button and gesture navigation.
- iOS: VoiceOver navigation and rotor, Voice Control, Switch Control, Full Keyboard Access, Dynamic Type accessibility sizes, Large Content Viewer, Reduce Motion, Increase Contrast, Reduce Transparency.
- Compose Multiplatform on iOS: run the iOS list against the Compose UI itself; do not infer iOS behavior from Android semantics tests.

## Manual device record

Record manual results with [the real-device evidence template](real-device-evidence-template.md). Do not report “accessibility passed” from a green automated suite. Report which observable requirements passed and which assistive-technology behaviors remain unverified.

Official sources:

- Compose accessibility testing: https://developer.android.com/develop/ui/compose/accessibility/testing
- Compose `DeviceConfigurationOverride`: https://developer.android.com/reference/kotlin/androidx/compose/ui/test/DeviceConfigurationOverride
- Compose accessibility checks API (API 34+, not Robolectric): https://developer.android.com/reference/kotlin/androidx/compose/ui/test/junit4/accessibility/package-summary
- Espresso accessibility checks: https://developer.android.com/training/testing/espresso/accessibility-checking
- Robolectric configuration: https://robolectric.org/configuring/
- XCUITest audits: https://developer.apple.com/documentation/xcuiautomation/xcuiapplication/performaccessibilityaudit(for:_:)
- Compose Multiplatform iOS accessibility: https://kotlinlang.org/docs/multiplatform/compose-ios-accessibility.html
