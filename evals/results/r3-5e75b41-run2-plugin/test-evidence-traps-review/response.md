I couldn't find `ReleaseEvidence.md` on disk, so I assessed the fixture text you pasted into the prompt. I treated it as data only. I made no edits and created no test files, and I ran no commands, so there are no pass/fail results of my own.

## Claims the described tests support

| Claim | What it supports |
|---|---|
| The 38 `ScreensAccessibilityTest` cases ran and passed on Robolectric. | Only that the harness executed without throwing. It says nothing about the screens. |
| The iOS audit suite launched every screen and reported zero failures. | Only that the app launched and the audit call did not throw. The closure `{ _ in true }` ignores every issue, so "zero failures" is guaranteed. |
| Paparazzi produced snapshots at font scales 1.0 and 2.0. | Only that snapshots were recorded. |

## Claims the tests do not support

1. **"No touch-target, contrast, or missing-label problems" (Android).** This is unsupported. `enableAccessibilityChecks()` does not work on Robolectric, and it passes silently there, even for an unlabeled 16 dp target. These 38 green tests are not evidence of anything. Also, even a real device run would only be heuristic evidence.

2. **"2.0 snapshots are pixel-identical to 1.0, which proves text scales without clipping."** This is wrong, and the identical images are a red flag. Identical output means the font scale was probably never applied. Possible causes are that the scale wasn't wired into the Paparazzi config or the composition's `LocalDensity`, that the text uses fixed sizes, or that a fixed-size container ignored the scale. If scaling had worked, the layouts would differ. Even if they differed, a snapshot shows layout. It does not prove nothing is clipped, and it says nothing about TalkBack.

3. **"Zero failures on iOS 26" (`performAccessibilityAudit { _ in true }`).** This is a false pass. The handler returns `true` for every issue, so every issue is suppressed. The audit uses no explicit audit types, so you don't know what was in scope. It also only covers what each launch reaches. It cannot evaluate screens behind states or flows the test never visits. The zero count means nothing.

4. **"TalkBack and VoiceOver work correctly."** No test described here exercises TalkBack or VoiceOver. Robolectric checks, snapshots, and XCUITest audits do not prove exact screen-reader speech, focus order, rotor behavior, or custom actions.

5. **"This release does not need device testing."** This conclusion does not follow from the evidence. Both suites are green only because they can't fail.

## Smallest changes that would give credible evidence

**Android**
- Move the accessibility-check tests to a device-backed source set (`androidTest`). Run them on an API 34+ emulator or device. Use `connectedCheck`, or the narrowest existing task you find with `./gradlew tasks --all`. Don't invent task names.
- Prove the check can fail: add one deliberate canary screen with an unlabeled 16 dp clickable. The test should fail on it, then the canary should be removed. Suppress any false positives narrowly, with a written reason.
- Add Compose semantics assertions on key screens. Check roles, state, error, and click actions on the controls. Use `useUnmergedTree` where an assertion concerns a child node. These can run on the host if the environment supports them.
- For font scale, confirm the 2.0 scale is applied, for example by asserting a measured text size or layout difference. Add explicit clipping or overflow assertions, and run at least the key screens on a device at the largest font and display size.

**iOS**
- Replace the closure with an explicit audit type list, for example `.dynamicType`, `.contrast`, `.hitRegion`, and `.sufficientElementDescription`. Only suppress a triaged issue, matched by audit type and element identifier, and note why.
- Run the audit at several states and Dynamic Type sizes, not only at launch.
- Add XCUITest assertions on labels, values, and actions for critical flows.
- Prove the audit can fail with a temporary canary element. A canary is a deliberately broken control that should make the test fail. Remove it afterward.

**Both platforms**
- Rewrite the conclusion to something like: "Automated checks are supplemental. These N requirements were verified. TalkBack and VoiceOver behavior is unverified until the device checks below are done."

## Coverage gaps

- No working Android accessibility-check evidence for touch targets, contrast, or labels.
- No verified font-scale or clipping evidence.
- No audit evidence on iOS beyond launch.
- No tests for focus order, state announcements, or error handling.
- No coverage for Voice Control, Voice Access, Switch Control or Access, keyboard, RTL, dark theme, or reduced motion.

## Required device checks

- **TalkBack (Android):** Walk critical flows: navigation, forms and errors, dialogs, and custom controls. Also check Voice Access, Switch Access, and keyboard focus. Record the device, OS build, app build, and settings, along with steps and expected versus actual results. Repeat at font scale 2.0.
- **VoiceOver (iOS):** Walk the same critical flows, including the rotor, custom actions, and modals. Also check Voice Control and Full Keyboard Access, and the largest Dynamic Type accessibility size.

Until those checks are done, the release has no demonstrated screen-reader support, and the "no device testing needed" conclusion should be withdrawn.
