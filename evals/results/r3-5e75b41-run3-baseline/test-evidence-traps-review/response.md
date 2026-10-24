# Review of Release 4.2 accessibility evidence

I worked from the fixture text in your prompt and didn't open the file. Nothing was edited or created.

## Android

**Claim: all 38 screens pass, so there are no touch-target, contrast, or missing-label problems.**
- **Supported:** For the 38 screens as rendered in the test, the checks found nothing they are able to flag.
- **Not supported:**
  - **`tryPerformAccessibilityChecks()`:** In Compose test, `tryPerformAccessibilityChecks()` does not fail the test. It is the non-throwing variant, so a violation wouldn't fail it. Only `performAccessibilityChecks()` throws. Green results are therefore close to meaningless until this is confirmed. If a violation is reported through a listener or log, the fixture doesn't say.
  - **Robolectric:** It has no real rendering, so color contrast is effectively unchecked. It also doesn't give real density or window metrics, and it lacks real fonts, so touch-target sizing is weak evidence.
  - **Coverage:** Checks run on a single initial state of each screen. Dialogs, error states, loaded data, and bottom sheets aren't covered.
  - **Scope:** Automated checks such as Accessibility Test Framework (ATF) catch only a subset of issues. "No problems" is an overclaim even if the checks ran properly.
- **Smallest fix:**
  - Switch to `performAccessibilityChecks()`.
  - Prove the suite can fail: add one deliberately bad composable (a 20dp clickable with no label), and confirm the test goes red.
  - Run on an emulator or device as `androidTest`, so contrast and size checks are meaningful.
  - Narrow the claim to "ATF found no violations in the default state of 38 screens."

**Claim: the 2.0 snapshots are pixel-identical to 1.0, which proves text scales without clipping.**
- **Not supported, and it points the other way.** Identical images mean the font scale was most likely not applied. If text had scaled, the pixels would differ. This is a broken test setup, or the app ignores the system font scale (hardcoded `sp` or `dp`, or a fixed-size container). Neither case proves anything about clipping.
- **Smallest fix:**
  - Check that Paparazzi's `fontScale` config is actually reaching the composition, for example via `LocalDensity`.
  - Assert that the 2.0 images differ from the 1.0 images.
  - Review the 2.0 images by eye, or add layout assertions for truncation and overflow, such as `onNodeWithText().assertIsDisplayed()` plus bounds checks.
  - Consider adding 1.3x and the largest system scale.

## iOS

**Claim: zero failures on iOS 26 means the audit passes.**
- **Not supported.** `performAccessibilityAudit { _ in true }` is a trap. The closure is the issue handler, and returning `true` means "this issue is handled or ignored" for every issue. Every issue is therefore suppressed, and the suite can never fail.
- **Smallest fix:**
  - Remove the closure, or filter only specific, documented, justified exceptions, for example `{ issue in issue.auditType == .X && knownIssueID }`.
  - Confirm it can fail by injecting a known violation, such as an unlabeled button.
  - Record the audit types included (the default is all).
  - Check that each screen is actually navigated to and reached, not just launched.
  - Then re-run, and report real findings.

## Conclusion

**Claim: both suites are green, so TalkBack and VoiceOver work correctly and device testing isn't needed.**
- **Not supported.**
  - Even valid automated checks don't test screen reader behavior. They don't cover focus order, reading order, announcement quality, custom actions, gesture alternatives, live-region behavior, or whether labels make sense (as opposed to merely being present).
  - On top of that, the evidence here is invalid: the Android check is non-throwing and untested for failure, the font-scale comparison shows scaling probably didn't happen, and the iOS audit suppresses everything.
- **Smallest credible evidence:**
  - Fix and prove the automated checks as above.
  - Run a manual TalkBack and VoiceOver pass over the critical user flows, such as launch, sign-in, the core task, and error recovery, on at least one real device each.
  - Run the same pass at the largest font size.
  - Record the devices, OS versions, and findings.
  - Until then, say only "automated checks were run, with the known limitations above." Don't say "works correctly" and don't waive device testing.

## Summary

| Claim | Supported? |
|---|---|
| 38 Android tests pass | Yes (but they may not be able to fail) |
| No touch-target, contrast, or label problems | No |
| Text scales without clipping | No (the evidence suggests scaling wasn't applied) |
| iOS audit has zero failures | Only trivially (the audit can't fail) |
| TalkBack and VoiceOver work, no device testing needed | No |
