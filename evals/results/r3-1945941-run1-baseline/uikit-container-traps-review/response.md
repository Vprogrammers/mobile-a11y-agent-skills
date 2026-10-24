# Review: `ReceiptCell.swift`

I reviewed the fixture as pasted and didn't edit anything. I haven't run it on a device or simulator, so every finding comes from reading the code. The verification steps at the end are what would confirm each one.

## Findings

| # | Sev | Area | Problem |
|---|-----|------|---------|
| 1 | **P0** | VoiceOver, Voice Control | `ReceiptCell` sets `isAccessibilityElement = true`, which turns the cell into a single leaf element. UIKit then stops exposing its subviews, so the **Remove** button can't be reached by VoiceOver swipe or touch exploration. Voice Control also can't resolve "Tap Remove", and "Show numbers" won't label it. The row's only action becomes unavailable and there is no custom action as an alternative. |
| 2 | **P1** | AutoFill | The verification field has `.numberPad` but no `textContentType`. Without `.oneTimeCode`, iOS won't offer the SMS code in QuickType. Users must read the code, remember it, and type it by hand. That is hard for people with motor, cognitive, or memory-related barriers, and for people using Voice Control or Switch Control. |
| 3 | **P1** | Dynamic Type | `amount` keeps the default `numberOfLines = 1`. At accessibility sizes, or with long currency strings, it truncates. Truncating a money value is a real information loss. `title` already uses `numberOfLines = 0`, so this is inconsistent. |
| 4 | **P1** | Dynamic Type | The `.system` button's title uses the default fixed-size font and doesn't scale. At large text sizes, the row's text grows while its only action stays small. |
| 5 | **P1** | Dynamic Type, layout | `CodeEntryView` adds `field` with no frame, constraints, or `intrinsicContentSize`. Unless the host sets a frame, it has zero size, so it is invisible and can't be activated. Even with a manual frame, a fixed height won't follow text size. |
| 6 | **P2** | Voice Control, VoiceOver | Every row has an identical "Remove" button. Voice Control gets ambiguous "Tap Remove" targets (it falls back to numbers). VoiceOver users hear the same name with no indication of which receipt it removes. |
| 7 | **P2** | Dynamic Type, motor | The system button's default hit area is likely under 44×44 pt. The stack has no spacing, so the button sits flush against the amount. Both problems get worse as content grows. |
| 8 | **P2** | Resilience | `onRemove` isn't cleared in `prepareForReuse()`. A recycled cell can fire the previous row's closure and remove the wrong receipt. The fixture shows no state-tracking or guard against this. |
| 9 | **P2** | Labelling | The code field's only name is its placeholder. The visible label disappears once the user types, and placeholder text is low contrast. There is no persistent label to scale with Dynamic Type or to anchor Voice Control commands. |
| 10 | **P2** | Keyboard | `.numberPad` has no Return or Done key, and nothing replaces it (no `inputAccessoryView`, no auto-submit). VoiceOver, Voice Control, and Switch Control users have no obvious way to dismiss the keyboard or submit. |
| 11 | **P3** | Localization | "Remove" and the combined `"\(title), \(amount)"` label are hard-coded and not localizable. Once finding 1 is fixed, the custom label is also unnecessary. |

## Smallest native corrections

**1 and 6: expose the children and name the button per row.** Delete `isAccessibilityElement = true` and the custom `accessibilityLabel` in `configure`. UIKit then exposes `title`, `amount`, and the button separately. If you want one stop per row, keep the cell as a container instead and set `accessibilityElements = [combinedElement, remove]`. Don't collapse the button into the row.
```swift
// configure(title:amount:)
remove.accessibilityLabel = String(localized: "Remove \(title)")
```
This label begins with the visible text "Remove", so Voice Control's "Tap Remove" still matches it.

**3, 4, 7: scaling, wrapping, and hit area.** Use `UIButton.Configuration`, which scales and wraps by default and adds padding.
```swift
amount.numberOfLines = 0

var config = UIButton.Configuration.plain()
config.title = "Remove"
config.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer {
    var a = $0; a.font = .preferredFont(forTextStyle: .body); return a
}
remove.configuration = config
remove.contentHorizontalAlignment = .leading
stack.alignment = .leading
stack.spacing = 8
```
Also confirm that the table view sets `rowHeight = UITableView.automaticDimension` with an estimated height. That isn't visible in the fixture. At accessibility sizes, `.leading` alignment keeps the button's text wrapping inside the stack's width.

**8: prevent stale closures.**
```swift
override func prepareForReuse() {
    super.prepareForReuse()
    onRemove = nil
}
```

**2: AutoFill.**
```swift
field.textContentType = .oneTimeCode
```

**5 and 9: layout and a persistent label.** Add a visible `UILabel` with a text style and `adjustsFontForContentSizeCategory = true`. Put the label and field in a vertical `UIStackView` pinned to `layoutMarginsGuide`. Use `field.borderStyle = .roundedRect`, and keep the placeholder as an example only. Keep the label text and the field's accessible name consistent.

**10: Done key.** Add a `UIToolbar` as `inputAccessoryView` with a Done button, or submit automatically when the code reaches its expected length. If you auto-submit, announce the result (for example with a UIAccessibility announcement or a focus change) so VoiceOver users aren't left guessing.

## Verification

- **Static and automated:**
  - Run Xcode's Accessibility Inspector audit.
  - Add a UI test using `performAccessibilityAudit()`.
  - Add a unit test asserting `textContentType == .oneTimeCode`.
  - Add a unit test asserting the cell is not a leaf element and the button is reachable (`accessibilityElements`, or the button's `isAccessibilityElement`).
- **VoiceOver, on a device:** Swipe through a receipt row and confirm the Remove button is its own focus stop and double-tap activates it. Check that the name identifies the receipt. Don't assert exact spoken strings, since speech varies with settings and OS version.
- **Voice Control:** Say "Show names" and "Show numbers". Confirm each row's Remove is individually targetable, that "Tap Remove" is either unambiguous or falls back to numbers sensibly, and that you can reach the code field by name.
- **Dynamic Type:** Check at the default size and the largest accessibility size (AX5), including with Bold Text and in landscape. The amount should wrap rather than truncate, the button should scale and stay tappable, and the code field should stay visible and usable. Also check with the keyboard open.
- **AutoFill:** Test on a real device that receives an SMS. The simulator can't receive SMS, so it can't confirm the QuickType suggestion. Confirm the code suggestion appears and fills the field. Also confirm manual entry still works.
- **Reuse:** Scroll rapidly and delete rows. Confirm the correct receipt is removed each time.
