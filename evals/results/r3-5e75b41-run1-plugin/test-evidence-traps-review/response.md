# Release 4.2 evidence review

I assessed the fixture text you supplied inline. A glob for `ReleaseEvidence.md` found no file in the working directory, so I could not check it against the file on disk. I did not edit anything, create test files, or run any tests. I also could not delegate to the `accessibility-test-engineer` agent, because I have no agent-launch tool in this session. I applied the `mobile-a11y-testing`, `android-a11y` and `ios-a11y` skills directly.

## Claims the described tests support

| Claim | What it supports |
|---|---|
| The suites run and pass | 38 Robolectric tests pass on the host. `AuditUITests` reports no failures on iOS 26. These are weak smoke signals, and only for the iOS audit's reach (see below). |
| Paparazzi runs at font scale 1.0 and 2.0 | The snapshot pipeline works. The two sets of recordings are identical, which is a warning sign (see below). |

## Claims the tests do not support

**1. Android: "no touch-target, contrast, or missing-label problems."**
- `enableAccessibilityChecks()` documents that it does not work on Robolectric. In practice it passes silently there, even for an unlabeled 16 dp target.
- Its supported environment is instrumented tests on API 34+ devices or emulators. `ScreensAccessibilityTest` lives in `app/src/test`, so all 38 passes are meaningless as evidence.
- Even on a device, these checks are heuristics. They are not proof that no problems exist.
- Separately, `tryPerformAccessibilityChecks()` is called without any visible assertion or triage. I'd confirm it fails the test when it finds a violation.

**2. Android: "pixel-identical 2.0 and 1.0 snapshots prove text scales without clipping."**
- This conclusion is backwards. Identical images mean the font scale probably never took effect. Text at 2.0 should render larger.
- The likely cause is that the scale was not applied to the composition's `LocalDensity` or configuration. Fonts that don't use `sp` or that ignore scaling would also cause it.
- The snapshots show that scaling is not being exercised. They show nothing about clipping.
- Even if the scale did apply, snapshots only show clipping on the screens and states captured. They don't cover long strings, localized text or dynamic content.

**3. iOS: "zero audit failures."**
- `performAccessibilityAudit { _ in true }` suppresses every issue, so it cannot fail. This is the false-pass pattern.
- Without `for:`, it audits whatever the Xcode default covers. Nothing is documented about which audit types ran.
- It only audits what is on screen when it runs. "Launches every screen" doesn't mean every state, such as errors, modals, large text or dark mode.
- Contrast, Dynamic Type and similar results are not checked against real settings.

**4. Both platforms: "TalkBack and VoiceOver work correctly, so device testing isn't needed."**
- No automated layer here proves exact screen-reader speech, focus order, gestures or actions. That covers host semantics tests, Paparazzi, XCUITest audits and Accessibility Inspector.
- Neither suite exercises TalkBack or VoiceOver at all. Real-device verification is required.
- The conclusion is unsupported and should be withdrawn.

## Smallest changes that produce credible evidence

**Android**
1. Move the accessibility-check tests to `androidTest`, or another device-backed source set, and run them on an API 34+ emulator or device. The `ui-test-junit4-accessibility` dependency and Compose 1.8+ are required. Run the narrowest existing connected task after discovering it with `./gradlew tasks --all`.
2. Treat results as heuristics. Triage each finding and suppress only narrowly.
3. Keep the Robolectric tests only for semantics assertions that Robolectric supports. Assert roles, state, actions and errors on key controls, not speech strings.
4. Fix the font-scale snapshots. Set the scale explicitly, for example through the `LocalDensity` `fontScale` or the device configuration. Add a guard that the 2.0 render differs from the 1.0 render.
5. Add layout assertions for clipping on text-heavy screens. For example, check that nodes are displayed and that bounds fit within the parent.

**iOS**
1. Replace the catch-all closure with an explicit audit, as in the matrix example: `performAccessibilityAudit(for: [.dynamicType, .contrast, .hitRegion, .sufficientElementDescription]) { issue in … }`.
2. The handler may return `true` only for a triaged false positive, matched by audit type and element identifier. Record the reason for each.
3. Run it at least at default and at an accessibility Dynamic Type size, on a pinned simulator destination. Choose the destination from `-showdestinations`.
4. Add XCUITest assertions of label, value and traits for critical controls.

**Release conclusion**
Replace it with a statement of which observable requirements passed. Add a completed real-device record for the critical flows.

## Required device checks

- **Android:** TalkBack on a real device for the critical flows. Cover traversal order, labels, state and role announcements, error messages and custom actions. Add Voice Access and Switch Access. Check the largest font and display size, RTL and dark theme.
- **iOS:** VoiceOver navigation and rotor, Voice Control labels, Switch Control and Full Keyboard Access. Check Dynamic Type at accessibility sizes, Reduce Motion, Increase Contrast and Reduce Transparency.
- **Record:** device and OS build, app build, assistive technology and settings, steps, and expected versus actual results.

## Summary for the release record

| Item | Result |
|---|---|
| Changed test files | None |
| Commands run | None. I only read the skill reference and searched for the fixture. |
| Pass/fail/skip | Not applicable. The reported 38 Android passes and the iOS zero failures were not re-run, and neither is valid evidence of accessibility. |
| Coverage gaps | Android checks run in a host environment where they can't work. The font-scale snapshots show no scaling. The iOS audit suppresses every issue. No state coverage beyond the default state. No Dynamic Type or large-font checks on iOS. |
| Required device checks | TalkBack, Voice Access and Switch Access on Android. VoiceOver, Voice Control and Switch Control on iOS. |
