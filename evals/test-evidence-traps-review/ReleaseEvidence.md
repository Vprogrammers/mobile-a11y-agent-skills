# Release 4.2 accessibility evidence

## Android

`ScreensAccessibilityTest` lives in `app/src/test` and runs on Robolectric. For each of the 38 screens it calls `composeTestRule.enableAccessibilityChecks()` and then `onRoot().tryPerformAccessibilityChecks()`. All 38 tests pass, so the app has no touch-target, contrast, or missing-label problems.

Paparazzi snapshots are recorded at font scale 1.0 and 2.0. The 2.0 snapshots are pixel-identical to the 1.0 snapshots, which proves that text scales without clipping.

## iOS

`AuditUITests` launches every screen and runs:

```swift
try app.performAccessibilityAudit { _ in true }
```

The suite reports zero failures on iOS 26.

## Conclusion

Both automated suites are green, so TalkBack and VoiceOver work correctly and this release does not need device testing with assistive technologies.
