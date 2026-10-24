# Review: Release 4.2 accessibility evidence

The fixture's evidence doesn't support its conclusion. At best it shows the suites run. I judged this from the text you gave me and didn't open the file or any code.

## Claims, support and fixes

| Claim | Supported? | Why | Smallest fix or extra check |
|---|---|---|---|
| Android: 38 tests pass, so there are no touch-target, contrast or label problems | **No** | `tryPerformAccessibilityChecks()` is the non-throwing variant. It collects results and doesn't fail the test, so a green run is expected whatever the screens contain. Robolectric also doesn't do real layout or rendering, so size and contrast checks aren't reliable there. Each test probably covers only one default state per screen. | Switch to `performAccessibilityChecks()`, which throws. Run on an emulator or device (`androidTest`). Add a negative control, such as a deliberately bad composable that must fail the suite. Cover non-default states (error, empty, dialogs, expanded). Review contrast by hand or with a dedicated tool. |
| Paparazzi: identical 1.0 and 2.0 snapshots prove text scales without clipping | **No, it shows the opposite** | If scaling worked, the 2.0 render would differ. Identical images mean the font scale was never applied (a misconfigured `fontScale`, or text that ignores it). Snapshots only detect change from a baseline. They don't show correctness. | Assert that the 2.0 image differs from the 1.0 image. Fix the configuration. Then have a person review the 2.0 goldens for clipping, truncation and overlap. Add a test that checks text bounds. |
| iOS: zero audit failures on iOS 26 | **No** | The handler `{ _ in true }` tells XCTest every issue is handled, so every issue is ignored. Zero failures is guaranteed. | Drop the closure, or ignore only specific, documented issues. Add a negative control screen that must fail. Log the issue count. Also test Dynamic Type at the largest sizes, and the states reached by scrolling, not just the launch state. |
| Both suites are green, so TalkBack and VoiceOver work correctly | **No** | Neither suite runs a screen reader. Automated checks can't judge focus order, announcements, label quality, custom actions, state descriptions, focus traps or gesture alternatives. | See the manual pass below. |
| No device testing with assistive tech is needed | **No** | This follows only if the claims above hold, and they don't. | Do the manual pass below. |

## What the evidence does support

- The Android screens can be composed and tested under Robolectric without crashing.
- The iOS UI tests can reach every screen and invoke the audit.
- The Paparazzi font-scale setup is probably broken.

## Smallest credible package

1. Make both suites able to fail, and prove it with a known-bad negative control that turns each suite red.
2. Fix the font-scale configuration, and assert that the 2.0 images differ from the 1.0 images.
3. Run a short manual pass on a real device with TalkBack and VoiceOver, with large text. Cover the critical flows (launch, sign-in, the main task, checkout or equivalent, error recovery). Check reading and focus order, control names, roles and states, dialogs and focus return, and whether any content is clipped or unreachable.
4. Reword the release note to something like "automated checks (now enforcing) pass; manual screen-reader pass done on flows X, Y, Z". Don't claim that assistive technologies work correctly.
