# Review: `ReceiptCell.swift`

I reviewed the fixture as pasted and didn't open or edit the file.

## Findings

| # | Sev | Area | Defect |
|---|-----|------|--------|
| 1 | **P0** | VoiceOver, Voice Control | `isAccessibilityElement = true` on the cell makes it a leaf element, so its subviews, including the Remove button, are hidden from the accessibility tree. |
| 2 | **P1** | AutoFill | `field` has no `textContentType = .oneTimeCode`, so iOS can't offer the SMS code as a QuickType suggestion. |
| 3 | **P1** | Dynamic Type | `amount` keeps the default `numberOfLines = 1`, so the amount truncates at large accessibility sizes. |
| 4 | **P1** | Dynamic Type | `CodeEntryView` adds `field` with no frame or constraints. It sits at zero size, and nothing lays it out or resizes it with the text size. |
| 5 | **P1** | VoiceOver, Voice Control | The field's only name is a placeholder, which disappears once the user types. There is no explicit `accessibilityLabel` and no visible label. |
| 6 | **P2** | Dynamic Type | The Remove button's title uses the fixed system button font, so it doesn't scale with the other text. |
| 7 | **P2** | Dynamic Type | The Remove button's height isn't guaranteed to reach 44 pt. |
| 8 | **P2** | Voice Control, VoiceOver | Every row's button is just "Remove", so rows are ambiguous. |
| 9 | **P2** | Reuse | `onRemove` isn't cleared in `prepareForReuse`, so a reused cell can run a stale closure for the wrong row. |
| 10 | **P2** | Keyboard | `.numberPad` has no Return key and nothing dismisses or submits it. |
| 11 | **P3** | Layout | The stack has no `spacing`. |

### Why the main ones matter

- **#1:** With the Remove button out of the tree, VoiceOver users can't reach it, and Voice Control can't show a name or number for it. Nothing replaces it, so a destructive action is unavailable to those users. That is why it's P0. The combined label `"\(title), \(amount)"` is fine on its own, but the container flag causes the problem.
- **#2:** Without the one-time-code content type, users have to leave the app, read the SMS, and retype the code. That is a real barrier for users with motor or cognitive disabilities. It is not a total block, because typing the code still works.
- **#4:** I'm treating this as a fixture omission. Please confirm whether the real code constrains the field elsewhere.

## Smallest native fixes

**Cell**
```swift
// remove: isAccessibilityElement = true   (cell stays a plain container)
amount.numberOfLines = 0

var cfg = UIButton.Configuration.plain()
cfg.title = "Remove"        // configuration titles scale with Dynamic Type and add padding
remove.configuration = cfg
remove.heightAnchor.constraint(greaterThanOrEqualToConstant: 44).isActive = true
stack.spacing = 8

func configure(title: String, amount: String) {
    self.title.text = title
    self.amount.text = amount
    remove.accessibilityLabel = "Remove \(title)"       // starts with the visible text
    remove.accessibilityUserInputLabels = ["Remove"]    // short spoken name for Voice Control
}

override func prepareForReuse() {
    super.prepareForReuse()
    onRemove = nil
}
```

- With the cell no longer an element, title and amount are read as separate elements and Remove is reachable.
- If you want one swipe stop per row, make a combined element instead. Set `isAccessibilityElement = false` on the cell, expose `accessibilityElements` as a combined text element plus `remove`, and keep the button separate. A single-element cell with an `accessibilityCustomActions` "Remove" action is an alternative. It does not reliably serve Voice Control, so I'd prefer the first option.
- If the button's visible text is also what Voice Control users say, keep the accessibility label starting with "Remove". The `accessibilityUserInputLabels` line keeps the short phrase working.

**Code entry**
```swift
field.textContentType = .oneTimeCode
field.accessibilityLabel = "Verification code"
field.borderStyle = .roundedRect
field.translatesAutoresizingMaskIntoConstraints = false
// pin to layoutMarginsGuide, with a minHeight of 44 and no fixed height
// add a visible UILabel above the field (not placeholder-only)
// add an inputAccessoryView toolbar with Done/Submit, since numberPad has no Return key
```

## Verification

I haven't run any of these. Check actual spoken output on a device rather than assuming it.

- **VoiceOver (device):**
  - Swipe through a row and confirm Remove is reachable and activates the right row.
  - Confirm title and amount are both announced, in whatever form the final design chooses.
  - Confirm the field's name is still exposed once it holds text.
- **Voice Control (device):**
  - Turn on "Show Names" and "Show Numbers" and confirm each Remove button gets a name or number.
  - Say "Tap Remove" and confirm the behavior is sensible with several rows.
  - Say the field's name and confirm it focuses.
- **Dynamic Type:**
  - Test at the default size, XXXL, and AX5, using the Xcode environment override or Accessibility settings.
  - Confirm no truncation of amount or title.
  - Confirm the button is at least 44 pt tall and its title scales.
  - Confirm rows self-size (`rowHeight = UITableView.automaticDimension` plus an estimate).
  - Confirm the code field is visible and unclipped.
- **AutoFill:** On a device, receive a real SMS code and confirm the QuickType suggestion appears and fills the field. The simulator isn't reliable for this.
- **Automated:**
  - An XCUITest asserting `cell.buttons["Remove"].exists` and is hittable would have caught #1.
  - Run `performAccessibilityAudit()` (iOS 17+) and the Accessibility Inspector audit for contrast, hit-region and text-clipping issues.
  - Add a snapshot test at an accessibility content size.
