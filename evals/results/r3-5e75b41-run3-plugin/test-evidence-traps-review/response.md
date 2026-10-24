# Release 4.2 evidence review

I reviewed the fixture text from your prompt. `evals/test-evidence-traps-review/ReleaseEvidence.md` doesn't exist in the working directory, and a glob for it found nothing. I created and edited no files, and I ran no tests. This is a review of the written claims only. I didn't inspect the real test code, so I haven't confirmed the suites are configured as the fixture describes.

## Verdict

The evidence doesn't support the conclusion that TalkBack and VoiceOver work correctly or that device testing can be skipped. Each claim fails for a different reason.

| Claim | Supported? | Why |
|---|---|---|
| All 38 Android tests pass, so there are no touch-target, contrast, or missing-label problems | **No** | The checks run in `app/src/test` on Robolectric. `enableAccessibilityChecks()` is documented as not working on Robolectric. In practice it passes silently there, even for an unlabeled 16 dp target. The 38 green results are probably meaningless. Even on a device, these checks are heuristics, and "all pass" wouldn't prove "no problems". |
| Paparazzi 2.0 snapshots are pixel-identical to 1.0, which proves text scales without clipping | **No, and it points to a defect** | Identical pixels most likely mean the font scale never applied. Scaled text should change the layout. A passing record/verify run would also only compare each image against its own baseline. It would not compare 2.0 against 1.0, so it can't show anything about clipping. |
| `performAccessibilityAudit { _ in true }` with zero failures on iOS 26 proves the iOS screens pass | **No** | The handler returns `true` for every issue, so every issue is ignored. The suite can't fail, and zero failures says nothing. |
| Both suites are green, so TalkBack and VoiceOver work correctly | **No** | Neither suite exercises a screen reader. Semantics tests, snapshots, simulator runs, and audits don't prove exact TalkBack or VoiceOver speech, focus order, or navigation. |
| No device testing with assistive technologies is needed | **No** | Nothing in the fixture supports this. It contradicts the evidence boundaries. |

## What the tests do support

Very little as written:

- Each of the 38 Android screens can be composed and queried under Robolectric without crashing.
- The 38 screens run in Paparazzi at both font scales. The identical output suggests the 2.0 run may be misconfigured.
- Each iOS screen can be launched by XCUITest, and the audit call completes without throwing. The audit itself is effectively disabled.

## Smallest changes and checks that give credible evidence

**Android**
1. Move the `enableAccessibilityChecks()` tests to `androidTest` or another device-backed source set. Run them on an API 34+ emulator or device with the existing connected-check task. Find the task through discovery; don't guess its name.
2. Add one known-bad canary: an unlabeled 16 dp clickable that must fail. If it passes, the harness is invalid. Put it in the same environment as the real tests.
3. Triage each real finding, and suppress only specific false positives, as narrowly as possible. Report the result as heuristic supplemental evidence.
4. For font scale, first confirm the 2.0 scale is applied. Assert that the 2.0 render differs from the 1.0 one. Then check that text isn't truncated, either with layout assertions on a few high-risk screens or by manually reviewing the largest scale. Don't use pixel identity as a pass condition.
5. Add a few Compose semantics assertions on critical flows. These cover role, state, error, and merged-versus-unmerged nodes. Don't assert spoken text.

**iOS**
1. Replace the handler with `performAccessibilityAudit(for: [.dynamicType, .contrast, .hitRegion, .sufficientElementDescription])`. Return `true` only for triaged false positives, matched by audit type and element identifier, and note why each one is suppressed.
2. Run it on a pinned simulator destination, chosen from `-showdestinations` or `simctl`. Confirm that the audit actually reports a deliberately bad canary element.
3. Add XCUITest assertions on labels, values, and state for the key flows.

**Both platforms**
- Add a short device-evidence record for each platform, using the real-device template. Record the device and OS, app build, assistive technology and settings, steps, and expected versus actual results.

## Required device checks

- **TalkBack on a real Android device:**
  - Reading order and focus.
  - Names, roles, and states of controls.
  - Error and live announcements.
  - Dialogs and sheets.
  - Custom actions.
  - Navigation.
  - Voice Access and Switch Access on the main flows.
- **VoiceOver on a real iPhone:**
  - Reading order, rotor, and adjustable controls.
  - Modal and navigation focus.
  - Announcements.
  - Voice Control labels.
  - Switch Control or Full Keyboard Access.
- **Display settings on both platforms:**
  - Largest font or Dynamic Type size, plus display size.
  - Dark mode.
  - Increase Contrast.
  - Reduced motion.

## Coverage gaps

- Real touch-target, contrast, and label coverage on Android is unknown.
- Android font scaling is unverified, and the Paparazzi configuration needs investigation.
- iOS audit coverage is effectively zero until the suppress-everything handler is removed.
- Screen-reader behavior is unverified on both platforms.
- There is no evidence for Voice Access, Switch Access, Voice Control, keyboard, RTL, or reduced-motion behavior.

## Recommended release wording

"Automated checks are being corrected. The current Android host checks and the iOS audit aren't valid evidence. TalkBack and VoiceOver verification is pending on real devices."
