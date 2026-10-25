# Review: `PhotoFeedView.swift`

I reviewed the inline fixture text only. I didn't edit anything or run anything. Every finding below comes from the code shown, and anything that depends on runtime behavior is marked as unconfirmed.

## Findings

### 1. P1: Featured photos 2…n can't be reached except by waiting
- **Affected users:** VoiceOver users, Switch Control and Voice Control users, keyboard users, and anyone who can't wait for the timer. This also covers users with motor or cognitive disabilities who need control over timing.
- **Evidence:** `featuredIndex` changes only inside the `.task` loop. The featured `Image` has no gesture, button, paging control or accessibility adjustable action. For VoiceOver users, `autoAdvance` is set to `false` in `onAppear`, so they only ever see `featured[0]`.
- **Smallest fix:** Add Previous and Next buttons with labels, or a `TabView(.page)` or an `accessibilityAdjustableAction`. Include a position hint such as "2 of 5".
- **Automated verification:**
  - Add a UI test that taps Next and asserts the featured element's label changes.
  - Add a unit test for the index wrap logic once it is extracted from the view.
- **Real-device checks:**
  - With VoiceOver on, confirm every featured item can be reached and the change is announced.
  - Repeat with Switch Control and Voice Control.

### 2. P1: Auto-advancing content has no pause or stop control
- **Affected users:**
  - People with attention, cognitive or reading disabilities.
  - Low-vision users who need time to inspect an image.
  - Motor-impaired users.
  - Users of assistive tech other than VoiceOver, such as Switch Control and Voice Control.
- **Evidence:**
  - The `.task` loop swaps the featured image every 4 seconds.
  - The only opt-out is `autoAdvance = !UIAccessibility.isVoiceOverRunning`, read once in `onAppear`.
  - There is no user control and no `accessibilityReduceMotion` check.
  - Turning VoiceOver on or off while the view is on screen isn't picked up.
  - This is a WCAG 2.2.2 (Pause, Stop, Hide) concern.
- **Smallest fix:**
  - Add a visible Pause/Play toggle, default auto-advance to off or stop it after one cycle, and honor `@Environment(\.accessibilityReduceMotion)`.
  - Remove the VoiceOver sniffing, since a user control makes it unnecessary.
  - The loop can also skip ticks (or stop) while paused.
- **Automated verification:**
  - Add a UI test that the pause control exists and that the featured label stays unchanged after more than 4 seconds once it's activated.
  - Make the interval injectable, or use a clock abstraction, so the tests don't need real sleeps.
- **Real-device checks:**
  - Test with Reduce Motion on, and with VoiceOver toggled on and off while the screen is visible.
  - Check Switch Control scanning with the carousel running.

### 3. P2: The filter selection is shown by color only and has no selected state for assistive tech
- **Affected users:** VoiceOver users, and color-blind or low-vision users.
- **Evidence:**
  - The selected state is a background of `accentColor` or `clear` plus a foreground color change.
  - There is no `.accessibilityAddTraits(.isSelected)`, no icon or checkmark, and no group label.
- **Smallest fix:**
  - Add `.accessibilityAddTraits(filter == option ? .isSelected : [])`.
  - Add a non-color cue such as a checkmark or border, and wrap the row with `.accessibilityElement(children: .contain)` and a label.
  - Alternatively, use a `Picker` with `.segmented`.
- **Automated verification:** Add a UI test asserting `isSelected` on the active filter button, and run `performAccessibilityAudit()`.
- **Real-device checks:**
  - Confirm VoiceOver exposes which filter is active.
  - Check with Differentiate Without Color on.

### 4. P2: The filter control doesn't filter anything
- **Affected users:** All users. VoiceOver users are most affected, because an unchanged result reads as a silent failure.
- **Evidence:**
  - `filter` is written by the buttons but never read when building the grid.
  - `ForEach(photos)` always shows all photos.
  - `Photo` also has no favorite or shared field, so the model can't support the filters as written.
- **Smallest fix:**
  - Add the missing model fields and filter `photos` by `filter`.
  - Post an accessibility announcement or update the grid's state when the result changes.
  - If the filters are placeholders, remove them or mark them as unavailable.
- **Automated verification:** Add a unit test for the filtering logic and a UI test that the grid count changes per filter.
- **Real-device checks:** Confirm with VoiceOver that the result of changing the filter is perceivable, such as through an announcement or a count.

### 5. P2: The filter row may break at large Dynamic Type sizes, and its touch targets are small (needs device confirmation)
- **Affected users:** Low-vision users with large text sizes, and motor-impaired users.
- **Evidence:**
  - The three buttons sit in one non-wrapping `HStack` with fixed `.padding(.vertical, 8)`.
  - There is no `ViewThatFits`, `dynamicTypeSize` handling, `minHeight` or `contentShape`.
  - At default sizes the target height is roughly the line height plus 16 pt, so it may be under 44 pt. This is an estimate and isn't confirmed by the fixture.
- **Smallest fix:**
  - Use `.frame(minHeight: 44)` plus `.contentShape(Capsule())`.
  - Use `ViewThatFits` or an `AnyLayout` fallback to a vertical or wrapped layout at accessibility sizes.
- **Automated verification:**
  - Run `performAccessibilityAudit()`, which covers hit region and Dynamic Type clipping.
  - Take snapshot tests at `.accessibility3` and `.accessibility5`.
- **Real-device checks:** Check the row at the largest accessibility text size for truncation, overflow and tap accuracy.

### 6. P3: No heading or grouping semantics on the screen sections
- **Affected users:** VoiceOver users navigating by headings or containers.
- **Evidence:** The featured area, filters and grid have no headings, container labels or `.accessibilityAddTraits(.isHeader)`. This is an optional improvement, not a demonstrated barrier.
- **Smallest fix:** Add a section label for the filters and the grid, and a header if visible titles are added.
- **Automated verification:** Assert the labels exist in a UI test.
- **Real-device checks:** Try rotor navigation by headings and containers.

## Not flagged
- **Image labels:** The image labels use `photo.caption`. Whether the captions are good descriptions can't be judged from the fixture.
- **Contrast:** White text on `accentColor` has no supported finding, because the accent value isn't in the fixture.
- **Modulo indexing:** The `featured[featuredIndex % featured.count]` modulo access is safe for empty and shrinking arrays given the `isEmpty` guard.
- **VoiceOver speech:** I don't assume exact VoiceOver speech anywhere above.
