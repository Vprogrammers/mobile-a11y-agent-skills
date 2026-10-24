# Review of `ReceiptCell.swift`

I reviewed the fixture as pasted and didn't edit it. These are static findings. I didn't build or run anything, so none of them has been confirmed on a device.

## Findings

| # | Sev | Area | Problem |
|---|---|---|---|
| 1 | **High** | VoiceOver, Voice Control | `isAccessibilityElement = true` on the cell makes it a leaf element. That hides the Remove button from the accessibility tree. VoiceOver users can't focus it separately. Voice Control can't reliably name or number it ("Tap Remove"). The cell is a container, so it should not be an element. |
| 2 | **High** | All (if used as written) | `CodeEntryView` adds `field` with no constraints, no frame and no `translatesAutoresizingMaskIntoConstraints = false`. The field is zero-sized or mispositioned, so it is effectively unreachable and untappable. That affects every assistive technology and AutoFill. |
| 3 | **Medium** | AutoFill | The code field has no `textContentType = .oneTimeCode`. The system can't offer the SMS code as a suggestion. |
| 4 | **Medium** | Dynamic Type | `amount` leaves `numberOfLines` at the default of 1. At accessibility sizes it truncates, so the money value can be clipped. |
| 5 | **Medium** | Dynamic Type, Voice Control | The Remove button uses the system button title font, which doesn't scale with Dynamic Type. Its tap target is also tied to a small intrinsic title. |
| 6 | **Medium** | VoiceOver, Voice Control | Every row has an identical "Remove" button. Without row context a user can't tell which receipt it affects. Voice Control will show numbered disambiguation, which is workable but slower. |
| 7 | **Low** | VoiceOver | The only label is a placeholder, "Verification code". It disappears once the user types, and there is no persistent visible label. Placeholder-as-label is a fallback, not a design. |
| 8 | **Low** | Keyboard | `.numberPad` has no Return or Done key. Add a way to dismiss it. |
| 9 | **Low** | Reuse | `onRemove` isn't cleared in `prepareForReuse`. A recycled cell can fire a stale closure for the wrong row if `configure` or the handler isn't reset. |

Item 1 also makes the manual `accessibilityLabel` in `configure` redundant. It only exists to feed the cell-as-element, and it duplicates what the two labels already provide.

## Smallest native corrections

**ReceiptCell**
```swift
// init: don't make the container an element
isAccessibilityElement = false          // remove the `= true`
amount.numberOfLines = 0

var config = UIButton.Configuration.plain()
config.title = "Remove"                 // UIButton.Configuration text scales automatically
remove.configuration = config
remove.titleLabel?.numberOfLines = 0
remove.contentHorizontalAlignment = .leading

// configure(title:amount:): delete the cell-level accessibilityLabel and add
remove.accessibilityLabel = "Remove \(title)"   // visible text "Remove" stays at the start of the label

override func prepareForReuse() {
    super.prepareForReuse()
    onRemove = nil
}
```
- The title and amount stay separate elements. To get a single swipe stop for them, put them in one container with a combined label. Leave the button outside it.
- If a one-stop row is preferred, keep the cell as the element and expose Remove through `accessibilityCustomActions`. Then verify Voice Control behavior separately, because named actions are less discoverable than a real button.
- The table must self-size (`rowHeight = UITableView.automaticDimension` plus an estimate). The fixture doesn't show this, so check it where the table is configured.

**CodeEntryView**
```swift
field.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    field.leadingAnchor.constraint(equalTo: layoutMarginsGuide.leadingAnchor),
    field.trailingAnchor.constraint(equalTo: layoutMarginsGuide.trailingAnchor),
    field.topAnchor.constraint(equalTo: layoutMarginsGuide.topAnchor),
    field.bottomAnchor.constraint(equalTo: layoutMarginsGuide.bottomAnchor),
])
field.borderStyle = .roundedRect
field.textContentType = .oneTimeCode
field.accessibilityLabel = "Verification code"  // or a visible UILabel above the field
// optional: an inputAccessoryView toolbar with a Done button for the number pad
```
No fixed heights anywhere, so the field grows with Dynamic Type.

## Verification
- **Static:** run the Accessibility Inspector audit on both views. It should flag the missing Remove element and any clipped text.
- **VoiceOver (device):** swipe through a row and confirm Remove is separately focusable, and that its label identifies the receipt. Check the field's label and hint after typing, when the placeholder is gone. Don't assert exact speech, only that the information is present and the order is logical.
- **Voice Control:** use "Show names" and "Show numbers". Say "Tap Remove" and confirm it either activates or disambiguates. Check that the field can be focused by its name.
- **Dynamic Type:** test at the largest accessibility size (AX5) and with Bold Text. Nothing should truncate, and the button should stay at least 44×44 pt. Use a snapshot or UI test with `preferredContentSizeCategory` overrides.
- **XCUITest:** `app.buttons["Remove …"]` should exist inside a cell. Then run `try app.performAccessibilityAudit(for: [.dynamicType, .textClipped, .hitRegion, .sufficientElementDescription])`.
- **AutoFill:** this needs a physical device. The simulator can't receive SMS, so send a code to the device and confirm the QuickType suggestion appears and fills the field.
