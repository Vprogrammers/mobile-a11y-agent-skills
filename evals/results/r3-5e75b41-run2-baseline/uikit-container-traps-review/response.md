I reviewed the inline fixture only and didn't edit anything or run any tooling. Nothing here assumes exact VoiceOver speech.

## Findings

| # | Sev | Area | Problem |
|---|-----|------|---------|
| 1 | **High** | VoiceOver, Voice Control | `isAccessibilityElement = true` on the cell makes it a leaf element. That hides the `remove` button from the accessibility tree. VoiceOver users can't focus or activate Remove, except through the default cell activation, which does nothing here. Voice Control can't target "Tap Remove" or show a number for it either. |
| 2 | **High** | AutoFill | `field` has no `textContentType = .oneTimeCode`, so iOS won't offer the SMS code on the keyboard. |
| 3 | **High** | Dynamic Type, all | `CodeEntryView` adds `field` with no constraints and no intrinsic layout, so its frame is `.zero`. The field is invisible and untappable unless a parent sets its frame. It also can't grow with text size. |
| 4 | **Medium** | Dynamic Type | `amount` keeps the default `numberOfLines = 1`, so it truncates at accessibility sizes. |
| 5 | **Medium** | Dynamic Type | The `.system` button's title uses a fixed system font, so "Remove" doesn't scale with the other labels. The button also has no content insets, so its tap target is probably under 44 pt tall. |
| 6 | **Medium** | VoiceOver, Voice Control | If several rows each have a button named just "Remove", VoiceOver users hear identical buttons with no item context. Voice Control users get ambiguous "Tap Remove" targets. |
| 7 | **Low-Med** | VoiceOver, Voice Control | The text field relies on its placeholder as its only name. The placeholder disappears once the user types, and it's low contrast. There's no explicit `accessibilityLabel` and no visible label. |
| 8 | **Low** | Robustness | `onRemove` survives cell reuse because there's no `prepareForReuse`. A stale closure could remove the wrong row. |
| 9 | **Low** | Keyboard | `.numberPad` has no Return or Done key, so the keyboard can be hard to dismiss. This matters most for Voice Control and Switch Control users. |

## Smallest native fixes

**ReceiptCell**
```swift
// delete: isAccessibilityElement = true
amount.numberOfLines = 0

var config = UIButton.Configuration.plain()   // scales with Dynamic Type and adds padding
config.title = "Remove"
remove.configuration = config
remove.contentHorizontalAlignment = .leading
remove.accessibilityUserInputLabels = ["Remove"]   // short Voice Control name
```
```swift
func configure(title: String, amount: String) {
    self.title.text = title
    self.amount.text = amount
    remove.accessibilityLabel = String(localized: "Remove \(title)")  // visible word "Remove" comes first
}
override func prepareForReuse() { super.prepareForReuse(); onRemove = nil }
```
- Dropping the cell-level element keeps the title, amount and button individually reachable.
- If you want one swipe stop for title and amount, expose a combined element through `accessibilityElements`, and keep the button as its own element. Don't collapse the whole cell again.
- The table view must use `rowHeight = UITableView.automaticDimension` with an estimated height. I can't see that from this file, so confirm it.

**CodeEntryView**
```swift
field.textContentType = .oneTimeCode
field.accessibilityLabel = String(localized: "Verification code")  // or a visible UILabel above the field
field.borderStyle = .roundedRect
field.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    field.leadingAnchor.constraint(equalTo: layoutMarginsGuide.leadingAnchor),
    field.trailingAnchor.constraint(equalTo: layoutMarginsGuide.trailingAnchor),
    field.topAnchor.constraint(equalTo: layoutMarginsGuide.topAnchor),
    field.bottomAnchor.constraint(equalTo: layoutMarginsGuide.bottomAnchor),
    field.heightAnchor.constraint(greaterThanOrEqualToConstant: 44),
])
```
- For finding 9, add a Done button on an `inputAccessoryView`, or switch to `.asciiCapableNumberPad`.
- Keep `.numberPad` only if codes are always numeric.
- A visible label is the better fix for finding 7, because it stays on screen after typing.

## Verification

- **Static checks:** run Accessibility Inspector's audit, or `try app.performAccessibilityAudit()` in XCUITest. Add a UI test that `cell.buttons.firstMatch` exists and is hittable. This catches the regression from #1.
- **VoiceOver, on device:** swipe through a row and confirm the title, amount and Remove button are each reachable and the button activates. Check that two rows' Remove buttons can be told apart. Judge this by what the user can distinguish, not by exact speech. Also check that the text field is named after text is entered.
- **Voice Control:**
  - Turn on "Show Names" and confirm the button is labeled "Remove".
  - Say "Tap Remove" and confirm it works. With several rows, confirm "Show Numbers" disambiguates.
  - Confirm the field is targetable by its name.
- **Dynamic Type:** run at the largest accessibility size, using Xcode's environment overrides or snapshot tests with `.accessibilityExtraExtraExtraLarge`. Confirm nothing truncates, the button title scales, rows grow, and the code field is visible and at least 44 pt tall.
- **AutoFill:** this needs a real device receiving an actual SMS with a code. Confirm the code appears in the QuickType bar and that tapping it fills the field. The simulator can't verify this.
