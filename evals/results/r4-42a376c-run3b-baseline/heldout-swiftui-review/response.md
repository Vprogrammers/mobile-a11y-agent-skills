# Review of `PhotoFeedView.swift`

I reviewed the inline fixture text only. I didn't edit anything or run anything.

## Findings

### 1. P1: Auto-advancing featured image has no pause control, and VoiceOver users can't reach slides 2 and up

**Affected users:** People who need more time to read or look, including low-vision, cognitive, and motor-impaired users. Switch Control users and VoiceOver users are also affected.

**Evidence:**
- The `.task` loop changes `featuredIndex` every 4 seconds while `autoAdvance` is true.
- The view has no pause or stop control, and no next or previous control.
- `autoAdvance` is only set to `false` once, in `.onAppear`, and only when `UIAccessibility.isVoiceOverRunning` is true.
- Everyone else gets content that changes on its own with no way to stop it. That includes Switch Control, Voice Control, Full Keyboard Access and sighted users.
- The `onAppear` check never re-runs. If VoiceOver is turned on while the screen is showing, rotation continues.
- When VoiceOver is on, `featuredIndex` has no other writer, so it stays at 0. The other `featured` items can't be reached through this view.

**Smallest fix:**
- Add a visible Pause/Play button that toggles `autoAdvance`.
- Add Previous and Next buttons, or `accessibilityAdjustableAction`, so every slide is reachable.
- Replace the one-time `onAppear` check by observing `UIAccessibility.voiceOverStatusDidChangeNotification` and `\.accessibilityReduceMotion`.
- Treat the VoiceOver check as a convenience, not as the only pause mechanism.

**Automated verification:**
- Inject the clock or interval so the timer is testable.
- Unit-test that `featuredIndex` doesn't change after the interval when paused.
- Unit-test that manual next and previous wrap correctly.
- XCUITest: assert the Pause control exists and that tapping it stops advancement.

**Real-device checks:**
- Turn VoiceOver on while the screen is already open, and confirm rotation stops and each slide is reachable.
- Check Switch Control and Voice Control ("Tap Pause").
- Check with Reduce Motion enabled.

### 2. P1: Selected filter is shown by color only, with no selected state exposed to assistive tech

**Affected users:** VoiceOver users, who can't tell which filter is active. Color-blind users and users of Differentiate Without Color or Increase Contrast are also affected.

**Evidence:**
- The only selected-state signal is the `.background` and `.foregroundStyle` change (`filter == option`).
- There is no `.accessibilityAddTraits(.isSelected)`.
- There is no non-color cue such as a checkmark or a border.

**Smallest fix:**
- Add `.accessibilityAddTraits(filter == option ? .isSelected : [])`.
- Add a non-color indicator for the selected state.
- Optionally use a `Picker` with `.segmented` style, which provides these semantics.

**Automated verification:**
- XCUITest: after tapping "Favorites", assert `isSelected` on that button and not on the others.
- Run `performAccessibilityAudit`.

**Real-device checks:**
- Use VoiceOver to confirm the active filter is distinguishable.
- Turn on Differentiate Without Color.

### 3. P2: Filter buttons have a small hit area and may not fit at large Dynamic Type sizes

**Affected users:** Users with motor impairments or tremor, Voice Control users, and users at large text sizes.

**Evidence:**
- `.padding` and `.background` are applied outside the `Button`, so the capsule is decoration and the tappable region is likely just the label text.
- Vertical padding of 8 around single-line text gives a visual height well under 44 pt at default size.
- Three buttons sit in a fixed `HStack` with no wrapping fallback, and no `ViewThatFits` or `minimumScaleFactor`. At accessibility text sizes they will likely truncate or overflow horizontally.

**Smallest fix:**
- Move the padding and background into a `ButtonStyle` or the button's label, add `.contentShape(Capsule())` and `.frame(minHeight: 44)`.
- Wrap the row with `ViewThatFits` or a flexible layout, or use a `Picker`.

**Automated verification:**
- The hit-region and Dynamic Type checks in `performAccessibilityAudit`.
- Snapshot tests at default and AX5 sizes.

**Real-device checks:**
- Tap the capsule edges at default size.
- Set text size to the largest accessibility setting and confirm all three filters are visible and operable.

### 4. P2: The filter has no effect on the content

**Affected users:** Everyone. This is a functional defect that also misleads assistive tech users, because the control announces a choice that changes nothing.

**Evidence:**
- `filter` is written by the buttons and read only for styling.
- The grid always iterates `photos`.
- `Photo` has no favorite or shared property, so filtering can't be done with this model.

**Smallest fix:**
- Add the needed fields to `Photo`, or filter data upstream.
- Drive the grid from a `filteredPhotos` computed property.

**Automated verification:** A unit test that each `FeedFilter` returns the expected subset.

**Real-device check:** Switch filters and confirm the grid content changes. Check how an empty result is communicated.

### 5. P3: The timer loop keeps running while auto-advance is off

**Evidence:** The `while` loop wakes every 4 seconds even when `autoAdvance` is false.

**Smallest fix:** Make the task conditional on `autoAdvance`, for example `.task(id: autoAdvance)` with an early return.

**Automated verification:** Unit-test the injected-clock logic.

## Checked and not flagged

- **Image labels:** Both the featured image and the grid images use `accessibilityLabel(photo.caption)`, which is reasonable for informative images. The fixture can't show whether captions are good labels, and I'm not assuming exact VoiceOver speech.
- **Accent color contrast:** White text on `Color.accentColor` depends on the app's accent color, which the fixture doesn't define. Check it with the Accessibility Inspector.
- **`featured[featuredIndex % featured.count]`:** The modulo keeps this safe if the array shrinks.
