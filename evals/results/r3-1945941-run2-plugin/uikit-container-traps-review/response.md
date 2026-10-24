**Review of `ReceiptCell.swift`** (static review only. I did not edit the fixture, run anything, or use a device. Exact VoiceOver speech is not assumed.)

**P1 — `ReceiptCell.init`, `isAccessibilityElement = true`, and `configure`**
Affected users: VoiceOver, Voice Control, Switch Control, and Full Keyboard Access users.
Evidence: The cell is made a single accessibility element, so its children (the `remove` button and the labels) are hidden from the accessibility tree. `accessibilityLabel` is set, but no custom action, activation path, or `accessibilityElements` is defined. The Remove button therefore cannot be focused or activated through assistive technology. Voice Control's "Tap Remove" has no target, and "Show numbers" cannot number the button. The visible button is still reachable by touch, so the function is lost for these users with no reasonable alternative. If this is a destructive action in a core flow, treat it as the top blocker. Whatever the cell's own activation does (for example, selecting the row) is the only action left.
Criterion: WCAG 4.1.2 Name, Role, Value; 2.1.1 Keyboard. Cite these only if useful.
Fix: Remove `isAccessibilityElement = true` and keep the native button as a separate element. Alternatively, keep the row as one element and add a named custom action:
```swift
accessibilityCustomActions = [
    UIAccessibilityCustomAction(name: "Remove \(title)") { [weak self] _ in
        self?.onRemove?(); return true }
]
```
The smallest option that keeps native behavior is to use a container: `isAccessibilityElement = false`, with `title` and `amount` left as elements or combined into one, and the real `remove` button left as its own element.
Verify: First an XCUITest that finds the Remove button (or the custom action) inside the cell and asserts that `onRemove` fires. Then on a device, check that VoiceOver can reach and activate Remove, that Voice Control "Tap Remove" works, and that Switch Control can reach it.

**P1 — `remove` button label is the same in every row**
Affected users: Voice Control users and VoiceOver users using the rotor or an element list.
Evidence: Every row's button is titled only "Remove". Once it is reachable (see the first finding), the rows cannot be told apart by name. Voice Control then shows disambiguation numbers, and VoiceOver users hear no row context. Without it, VoiceOver users can't tell which receipt a button will delete. Voice Control users can still select by number, so I'm rating this P2 on its own. It becomes part of the P1 fix if you choose the separate-button design.
Severity: P2.
Fix: Keep the visible title "Remove" so the spoken and visible names match. Set `remove.accessibilityLabel = "Remove \(title)"` in `configure`, but only if the label still starts with the visible text. Do not rely on a bare label that drops the visible word, or Voice Control by visible name will break. A custom action named "Remove \(title)" is the alternative.
Verify: Voice Control "Show names" and "Tap Remove" with several rows, then a VoiceOver check that the target row is identifiable.

**P1 — Dynamic Type: `amount`, `remove`, and the stack layout**
Affected users: Users at accessibility text sizes, and low-vision users.
Evidence: `amount.numberOfLines` is left at its default of 1, so large text truncates the amount, which is the key information in a receipt row. The `remove` button uses `UIButton(type: .system)` with `setTitle` and no `titleLabel.font` or `adjustsFontForContentSizeCategory`, so its text may not scale with the user's setting. `title.numberOfLines = 0` is correct. The vertical stack at least avoids horizontal clipping. The table's row height must be self-sizing (`UITableView.automaticDimension`). That setting is not in this file, so it is an assumption to check.
Criterion: WCAG 1.4.4 Resize Text, 1.4.10 Reflow.
Fix: Set `amount.numberOfLines = 0`. Give the button a scalable font with `remove.titleLabel?.font = .preferredFont(forTextStyle: .body)` and `remove.titleLabel?.adjustsFontForContentSizeCategory = true`. Better is `UIButton.Configuration.plain()` with a title text transform that uses a preferred font, and `titleLabel.numberOfLines = 0` or `lineBreakMode = .byWordWrapping`. Confirm the table uses automatic row height.
Verify: An XCUITest or snapshot test at `UIContentSizeCategory.accessibilityExtraExtraExtraLarge` showing the amount and the button fully visible, then a device check at the largest accessibility size.

**P2 — Button touch target and row height**
Affected users: Motor-impaired users.
Evidence: A system button with only a title has a hit area that follows its text, with no minimum size guaranteed by the code. This is lower risk at large text sizes and higher at default size. This is an assumption: the code does not set a size.
Fix: Use `UIButton.Configuration` with content insets, or a `heightAnchor` of at least 44 pt (`greaterThanOrEqualToConstant: 44`).
Verify: Accessibility Inspector element frame, then a manual tap check.

**P2 — `configure` label construction and reuse**
Affected users: VoiceOver users.
Evidence: `accessibilityLabel = "\(title), \(amount)"` builds the full label by hand. This duplicates the text already shown and bypasses localization of the amount formatting. The value is not set for reuse: it relies on `configure` being called every time, and a dequeued cell otherwise keeps stale text and labels. The label, with the amount as a comma-joined suffix, also loses the structure (the amount could be a value).
Fix: If the combined single element is kept, leave this and set `accessibilityValue` for the amount only if that matches your design. Reset state in `prepareForReuse` (clear `onRemove`, text). Clearing `onRemove` is also a correctness point, since a reused cell's closure could target an old row.
Verify: Unit test of `configure` after reuse. VoiceOver check that reading is concise.

**P2 — `CodeEntryView.field`: AutoFill and one-time code**
Affected users: AutoFill users, VoiceOver users, and people with cognitive or motor disabilities who cannot easily retype a code.
Evidence: The field has `keyboardType = .numberPad` but no `textContentType = .oneTimeCode`, so iOS does not offer the SMS/Mail code suggestion in the QuickType bar. Users must remember and type the code. This is a barrier to accessible authentication, but manual entry is still possible, hence P2.
Criterion: WCAG 3.3.8 Accessible Authentication (Minimum), where applicable.
Fix: Add `field.textContentType = .oneTimeCode`. Do not block paste. Do not log or announce the code.
Verify: Unit test asserting `textContentType == .oneTimeCode`. On a device, check that the SMS code suggestion appears and that paste works.

**P1 — `CodeEntryView`: the field has no frame, no constraints, and no label**
Affected users: All VoiceOver, Voice Control, and low-vision users.
Evidence: `field` is added with `addSubview` and no frame or Auto Layout constraints. Unless the parent sets them (not shown), it has a zero-size frame, which makes it effectively invisible and not hittable, and it provides no usable accessibility frame. The only name is `placeholder`. A placeholder disappears when typing and is not a durable label. `accessibilityIdentifier` is for tests only and is not spoken. Voice Control users can't reliably target a field with no label. Whether it is P0 or P1 depends on whether this is the only way to enter the code. I rate P1 because the layout may be done outside the fixture; confirm this.
Fix: Add constraints (leading/trailing/top/bottom, minimum height 44 pt) and `field.accessibilityLabel = "Verification code"`, kept equal to the visible label. Add a visible label above the field rather than relying on the placeholder. Use `UILabel` with Dynamic Type, or `UIListContentConfiguration`.
Verify: XCUITest that finds the field by label and types a code, an audit run with `performAccessibilityAudit()`, then VoiceOver and Voice Control ("Tap Verification code") on a device.

**P2 — `CodeEntryView` font scaling and multi-line behavior**
Affected users: Large-text users.
Evidence: `UITextField` is single-line. The font scales, but a field with no height constraint or `borderStyle` may clip at large sizes. This depends on the missing layout above.
Verify: Check the field at accessibility sizes with its real constraints.

**Blockers**
- P1: the whole cell is one accessibility element and hides the Remove button.
- P1: `amount` is truncated and `remove` may not scale at accessibility text sizes.
- P1: `field` has no layout or durable label (confirm against the parent's layout).

**Device checks**
- VoiceOver: row reading, access to Remove, and the code field's name and entry.
- Voice Control: "Show names/numbers", "Tap Remove" with several rows, "Tap Verification code".
- Switch Control and Full Keyboard Access: Remove is reachable.
- Largest accessibility Dynamic Type size, with the amount and button visible.
- SMS one-time code AutoFill on a real device, and paste.

**Residual risk**
- This is a static review, so I did not test any of the above.
- Table row-height configuration, the parent layout of `CodeEntryView`, and what the cell's selection does are outside the fixture.
- Whether the Remove action needs confirmation or undo is a product decision I did not assess.
- Automated audits cover only part of these barriers.
