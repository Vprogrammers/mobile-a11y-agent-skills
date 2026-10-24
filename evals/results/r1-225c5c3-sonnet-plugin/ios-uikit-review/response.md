# Review: `ProfileViewController.swift`

This is a static review of the inline fixture. `evals/ios-uikit-review/ProfileViewController.swift` doesn't exist in the working directory, so line numbers count from `final class` as line 1. I made no edits and ran no commands. Nothing was run on a simulator or device, and I haven't assumed exact VoiceOver speech.

```text
P1 — ProfileViewController.swift:4, 11–12 (`save`)
Affected users: VoiceOver, Voice Control, Switch Control, and Full Keyboard Access users.
Evidence: `save` is a plain `UIView` with a tap gesture recognizer.
  - It has no `isAccessibilityElement`, label, or button trait, so it is likely not exposed as an actionable element.
  - A bare `UIView` has no title for Voice Control to match, and no focus or keyboard activation.
  - It has no visible text, so the primary action may be invisible to sighted users too (the fixture sets no subviews).
  - The fixture sets no size, so I can't judge the touch target.
Criterion: WCAG 4.1.2 Name, Role, Value; 2.5.8 Target Size (if the size is small).
Fix: Replace it with a `UIButton` (`UIButton.Configuration.filled()`, title "Save"). Remove the gesture recognizer and use `addTarget(_:action:for: .touchUpInside)`. The title then provides the label, the button trait, and the Voice Control name. If it must stay a custom view, set `isAccessibilityElement = true`, `accessibilityLabel = "Save"`, `accessibilityTraits = .button`, and implement `accessibilityActivate()`. That is more work and weaker than a native button.
Verify: An XCUITest asserts `app.buttons["Save"]` exists and is hittable, and `performAccessibilityAudit()` runs on the screen. Then on a device, check that VoiceOver finds it and double-tap activates it, Voice Control "Tap Save" works, and Full Keyboard Access can focus and activate it.

P1 — ProfileViewController.swift:10 (`status` font)
Affected users: Low-vision users who rely on Dynamic Type.
Evidence: `.systemFont(ofSize: 14)` is a fixed size and doesn't scale. Line 3 also never sets `adjustsFontForContentSizeCategory` or `numberOfLines = 0`, so even a scaling font would not update live or wrap.
Criterion: WCAG 1.4.4 Resize Text.
Fix: Use `status.font = .preferredFont(forTextStyle: .footnote)` (or `.subheadline`). Set `status.adjustsFontForContentSizeCategory = true` and `status.numberOfLines = 0`. If the text needs a custom font, wrap it in `UIFontMetrics`.
Verify: A UI test launches with `-UIPreferredContentSizeCategoryName UICTContentSizeCategoryAccessibilityXXXL` and checks the label isn't truncated. Then on a device, set the largest accessibility sizes and confirm the text grows and wraps without clipping.

P2 — ProfileViewController.swift:9 (`status` color and meaning)
Affected users: Low-vision users, colorblind users, and Increase Contrast users.
Evidence: `.green` text is the only visual cue beyond the word "Verified". The fixture sets no background, so I can't compute the contrast ratio. Pure `.green` on a light background is likely below 4.5:1 for 14pt regular text (assumption, needs measuring). The word "Verified" carries the meaning, so color isn't the sole cue. The issue is contrast.
Criterion: WCAG 1.4.3 Contrast (Minimum); 1.4.1 Use of Color (only if an icon or color is added later).
Fix: Use a semantic or adaptive color such as `.label` or `.secondaryLabel`, or a custom asset with light, dark, and high-contrast variants. Keep the text "Verified".
Verify: Measure contrast in Accessibility Inspector or the audit in light, dark, and Increase Contrast modes.

P2 — ProfileViewController.swift:2, 13–14 (`avatar`)
Affected users: VoiceOver users.
Evidence: The label "Image" is generic and says nothing about the content. The avatar is exposed as an element, so VoiceOver users hit a stop that gives no information. I can't tell from the fixture whether it is decorative or identifies the user, or whether the "Verified" status relates to it.
Criterion: WCAG 1.1.1 Non-text Content.
Fix: If the avatar is decorative, set `isAccessibilityElement = false` (the `UIImageView` default) and drop the label. If it carries meaning, use a specific label such as "Profile photo of <name>". Don't include the word "image" in the label, because VoiceOver adds the trait. Add `.image` or `.button` traits only if that matches the behavior; if it is tappable it should be a button.
Verify: Accessibility Inspector audit for the label, then a VoiceOver swipe-through on a device to confirm the order and that no stop is redundant.

P3 — ProfileViewController.swift:3, 8, and the missing layout
Affected users: VoiceOver and Dynamic Type users.
Evidence: No views are added to the hierarchy and no constraints or `accessibilityElements` order are shown, so focus order and layout under large text can't be judged. Whether "Verified" should be read together with the avatar or name is a product decision.
Fix: When wiring the layout, use Auto Layout with flexible heights and a stack that can go vertical at accessibility content sizes (check `traitCollection.preferredContentSizeCategory.isAccessibilityCategory`). Leave the traversal order to the natural layout order if it matches the visual order.
Verify: Check order with VoiceOver and layout at AX5.
```

## Blockers
- The `save` control (P1) is not a real button. Voice Control, Switch Control, and keyboard access are the main concerns, and VoiceOver exposure is likely affected too.
- The `status` font is fixed at 14pt and won't scale (P1).

## Device checks
- **VoiceOver:** the `Save` button is found and activates, `Verified` reads once, and the avatar is either skipped or has a meaningful name.
- **Voice Control:** "Tap Save" works, and "Show names" displays the name.
- **Dynamic Type:** test the largest accessibility size with the layout wrapping.
- **Display settings:** check Increase Contrast and Dark Mode for the status color.
- **Full Keyboard Access / Switch Control:** focus and activate the Save button.

## Residual risk
- The review is static, based on a partial fixture. There is no layout, no real contrast measurement, and no knowledge of the avatar's purpose.
- Behavior of the real `ProfileViewController.swift` could differ from the inline copy.
- The fixes need a unit or UI test added to the existing XCTest/XCUITest target, which I haven't written because this was review-only.
