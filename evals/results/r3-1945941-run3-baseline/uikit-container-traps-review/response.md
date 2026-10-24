# Review of `ReceiptCell.swift`

I reviewed the pasted fixture and didn't edit it. The line references below point at the fixture's own constructs, since the file's line numbers weren't shown. I haven't run any of this, so each item needs the verification listed at the end.

## Findings

| # | Sev | Area | Problem |
|---|-----|------|---------|
| 1 | **P0** | VoiceOver, Voice Control, Switch Control | `ReceiptCell` sets `isAccessibilityElement = true` while it contains a button. The cell becomes a leaf, and its children are hidden from the accessibility tree. The Remove button can't be focused, activated, named by voice or numbered. If a trailing swipe action or another path to remove exists elsewhere, this drops to P1. |
| 2 | **P0** | All users (layout), and VoiceOver and Voice Control | In `CodeEntryView`, `field` is added with a zero frame and no constraints. `translatesAutoresizingMaskIntoConstraints` is still `true`, and nothing sizes it in `layoutSubviews`. The field is zero-size, so it is invisible and can't be tapped or focused. There is also no `borderStyle`, so it would have no visible bounds even when sized. |
| 3 | **P1** | Dynamic Type | `amount` keeps the default `numberOfLines = 1`. At accessibility sizes the money value truncates with an ellipsis, so users lose the key data. `title` already wraps correctly. |
| 4 | **P2** | Voice Control, VoiceOver | The Remove button's name is the same on every row. Once finding 1 is fixed, "Tap Remove" is ambiguous, and VoiceOver users hear "Remove" with no object. |
| 5 | **P2** | Dynamic Type | The `.system` button's title font isn't set from a text style and doesn't scale. Its title is also single-line by default, so it won't wrap at large sizes. |
| 6 | **P2** | AutoFill | `field` has no `textContentType = .oneTimeCode`, so the SMS code suggestion never appears above the keyboard. Manual typing still works, so this is a degradation. |
| 7 | **P2** | VoiceOver, Voice Control | The field's only name comes from the placeholder, which disappears once the user types. UIKit uses the placeholder as a fallback label, but it is not a stable name. |
| 8 | **P2** | Motor, keyboard | `.numberPad` has no Return or Done key, and nothing offers a way to dismiss it or submit. |
| 9 | **P3** | Maintainability | `onRemove` isn't cleared in `prepareForReuse`. This is only a hazard if a data source forgets to reassign it. |

## Smallest native corrections

**1 and 4. Stop hiding the button and give it a specific name.**
```swift
// in init: replace `isAccessibilityElement = true` with
isAccessibilityElement = false   // cell is a container; title, amount, button are separate elements

// in configure:
remove.accessibilityLabel = "Remove \(title)"
```
This gives title, amount and a named button as separate stops, and Voice Control can address each one.

If you want one stop per row, keep `isAccessibilityElement = true`, keep the combined label and add:
```swift
accessibilityCustomActions = [UIAccessibilityCustomAction(name: "Remove \(title)") { [weak self] _ in
    self?.onRemove?(); return true }]
```
Also set the button's `isHidden = true` or `accessibilityElementsHidden = true` so it isn't duplicated. Voice Control support for custom actions is weaker than for real controls, so verify it before choosing this. The first option is the safer default.

**3 and 5. Let content wrap and scale.**
```swift
amount.numberOfLines = 0
var config = UIButton.Configuration.plain()
config.title = "Remove"
config.titleTextAttributesTransformer = UIConfigurationTextAttributesTransformer {
    var a = $0; a.font = UIFont.preferredFont(forTextStyle: .body); return a }
remove.configuration = config
```
A configuration-based button wraps its title, grows its height and keeps a hit target of about 44pt. Also confirm the table view uses `rowHeight = UITableView.automaticDimension` with an `estimatedRowHeight`. That setting isn't in the fixture.

**2, 6, 7 and 8. Fix the field's layout, content type and name.**
```swift
field.translatesAutoresizingMaskIntoConstraints = false
field.borderStyle = .roundedRect
field.textContentType = .oneTimeCode
field.accessibilityLabel = "Verification code"   // or pair with a visible UILabel
NSLayoutConstraint.activate([
    field.leadingAnchor.constraint(equalTo: layoutMarginsGuide.leadingAnchor),
    field.trailingAnchor.constraint(equalTo: layoutMarginsGuide.trailingAnchor),
    field.topAnchor.constraint(equalTo: layoutMarginsGuide.topAnchor),
    field.bottomAnchor.constraint(equalTo: layoutMarginsGuide.bottomAnchor),
    field.heightAnchor.constraint(greaterThanOrEqualToConstant: 44),
])
```
For finding 8, add a `UIToolbar` with a Done button as `inputAccessoryView`, or switch to a keyboard type that has a Return key. A visible label above the field is better than a placeholder-only name.

**9.** Add `override func prepareForReuse() { super.prepareForReuse(); onRemove = nil }`.

## Verification

- **Accessibility tree:** Run Accessibility Inspector, and also test on a device with VoiceOver on. Confirm the Remove button is focusable, activates, and has a distinct name per row. Don't assert exact spoken wording, only that the name identifies the receipt.
- **Voice Control:** Turn on "Show Names" and "Show Numbers". Confirm each row's button is addressable and that "Tap Remove <item>" resolves to one target.
- **Dynamic Type:** Test at the largest accessibility size and at the smallest. Confirm `amount` and the button title wrap with no ellipsis, rows self-size, and nothing clips. Try landscape and Bold Text too.
- **Field layout:** Check the Xcode view debugger or Accessibility Inspector to confirm `field` has a non-zero frame of at least 44pt high.
- **AutoFill:** On a physical device with a real SMS code, confirm the code suggestion appears. The simulator doesn't reliably show it.
- **Regression:** Add a UI test that calls `performAccessibilityAudit()` on a screen with both views. The audit can flag small hit targets, clipped text at large sizes and missing labels. It won't prove the tree structure or AutoFill, so keep the manual checks above.
