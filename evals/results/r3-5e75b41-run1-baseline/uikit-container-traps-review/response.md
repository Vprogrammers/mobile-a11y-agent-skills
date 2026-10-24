# Review: `ReceiptCell.swift`

I reviewed the pasted fixture and didn't edit anything. I haven't run any of this, so each finding comes from reading the code. Where behavior depends on code outside the fixture, I say so.

## Findings

| # | Sev | Area | Problem |
|---|---|---|---|
| 1 | **High** | VoiceOver, Voice Control | `isAccessibilityElement = true` on the cell makes it a single leaf element. The Remove button inside is no longer exposed as its own element. VoiceOver users can't focus or activate it as a button. Voice Control users can't say "Tap Remove" or pick it from numbers or names. The cell's merged label also says nothing about the action. |
| 2 | **High** | All | `CodeEntryView` adds `field` with no frame and no constraints. It keeps a zero frame, so it is invisible and can't be tapped. This only holds if the parent never lays it out. The fixture doesn't show a parent, so confirm that. |
| 3 | **Medium** | AutoFill | The field has no `textContentType = .oneTimeCode`. iOS won't offer the SMS code in the QuickType bar, so users must switch apps and retype it. This is hardest for users with motor or memory difficulties. |
| 4 | **Medium** | Dynamic Type | The Remove button uses `setTitle` on a `.system` button with no configuration. Its title font is a fixed size and doesn't scale. It also may not wrap, and its height may fall below 44 pt. |
| 5 | **Medium** | Dynamic Type | `amount` has the default `numberOfLines = 1`. At accessibility sizes, long currency strings truncate, while `title` correctly uses 0. |
| 6 | **Medium** | VoiceOver, Voice Control | The field's only name is its placeholder. The placeholder disappears once the user types, and it is low contrast. There is no explicit `accessibilityLabel` or visible label. |
| 7 | **Low** | Dynamic Type | The text field has no `borderStyle` or background, so no visible boundary shows. Any fixed height added later would clip at large sizes. |
| 8 | **Low** | Keyboard, Voice Control | The number pad has no Return key, so there's no obvious way to dismiss or submit it. |
| 9 | **Low** | Correctness | `onRemove` isn't cleared on reuse. A stale closure could act on the wrong row if a later `configure` or assignment is missed. |

`accessibilityIdentifier = "verification-code"` is fine. It is for tests and isn't spoken, so it can't stand in for a label.

## Smallest native fixes

**Cell** (findings 1, 4, 5, 9). Stop merging the container, so the labels and the button are separate elements. Give the button a contextual label. Keep "Remove" at the start of that label so it matches the visible text for Voice Control. Let the button scale.

```swift
// init: delete `isAccessibilityElement = true`
amount.numberOfLines = 0

var cfg = UIButton.Configuration.plain()
cfg.title = "Remove"              // body-style, scales and wraps by default
remove.configuration = cfg
remove.heightAnchor.constraint(greaterThanOrEqualToConstant: 44).isActive = true

func configure(title: String, amount: String) {
    self.title.text = title
    self.amount.text = amount
    remove.accessibilityLabel = "Remove \(title)"
    remove.accessibilityUserInputLabels = ["Remove"]
    // delete the cell-level accessibilityLabel
}

override func prepareForReuse() {
    super.prepareForReuse()
    onRemove = nil
}
```

If you want one swipe stop for title and amount, set `accessibilityElements` to a single element built from the two labels, plus `remove`. Don't make the cell the element. A custom action alone is a weaker fix, because Voice Control support for it is less dependable.

Also confirm the table uses `rowHeight = UITableView.automaticDimension`. This is outside the fixture.

**Code entry** (findings 2, 3, 6, 7, 8)

```swift
field.textContentType = .oneTimeCode
field.accessibilityLabel = "Verification code"
field.borderStyle = .roundedRect
field.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    field.topAnchor.constraint(equalTo: layoutMarginsGuide.topAnchor),
    field.bottomAnchor.constraint(equalTo: layoutMarginsGuide.bottomAnchor),
    field.leadingAnchor.constraint(equalTo: layoutMarginsGuide.leadingAnchor),
    field.trailingAnchor.constraint(equalTo: layoutMarginsGuide.trailingAnchor),
    field.heightAnchor.constraint(greaterThanOrEqualToConstant: 44),
])
```

- Better still, add a visible `UILabel` above the field using a text style, so the name stays on screen after typing starts.
- For finding 8, either submit automatically when the code reaches its expected length, or add a `UIToolbar` accessory with a Done button.

## Verification

- **VoiceOver, on device:**
  - Swipe through a row and confirm that Remove is reachable as a button and that activating it fires `onRemove`.
  - Confirm the label includes the row's title.
  - Compare the order and wording on your own device. Don't assert exact speech.
- **Voice Control:** Use "Show names" and "Show numbers" and confirm that "Tap Remove" works. With several rows visible, check that it disambiguates or offers numbers.
- **Dynamic Type:**
  - Set the size to AX5 using Xcode environment overrides or the Accessibility Inspector.
  - Check that the title, amount and button text all wrap or scale with no truncation or clipping.
  - Check that the button stays at least 44 pt tall and that row heights update.
- **Automated:**
  - Run `try app.performAccessibilityAudit()` (iOS 17+) on a screen containing both views. It covers element description, hit region, text clipping and Dynamic Type.
  - Add a unit assertion that `textContentType == .oneTimeCode`.
  - Add a UI test that finds the Remove button inside a cell.
- **AutoFill:** Test on a real device. Send an SMS containing a code to that device, open the screen, and confirm the code is offered above the keyboard. The simulator is unreliable for this.
- **Layout:** Check that the field is visible and tappable on screen in the real parent.
