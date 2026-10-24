# Review: `ProfileViewController.swift`

I reviewed the snippet as given. It never adds views to a hierarchy and has no layout code, so layout behavior is unverified.

## Findings

| # | Severity | Area | Problem |
|---|---|---|---|
| 1 | **High** | VoiceOver, Voice Control | `save` is a plain `UIView` with only a tap gesture. It isn't an accessibility element, and it has no label and no button trait. VoiceOver users likely can't find or activate it. Voice Control users have no name to say, and the control has no visible text. |
| 2 | **High** | Dynamic Type | `status.font = .systemFont(ofSize: 14)` is a fixed size. It ignores the user's text size. `adjustsFontForContentSizeCategory` isn't set, and `numberOfLines` is left at 1, so larger text would truncate. |
| 3 | **Medium** | VoiceOver | `avatar.accessibilityLabel = "Image"` says nothing about the content, and the element type is already conveyed by the image trait. It adds a stop that carries no information. |
| 4 | **Medium** | Visual accessibility | `.green` (pure green) on a light background very likely has low contrast. It also ignores dark mode and Increase Contrast. The text "Verified" carries the meaning, so color isn't the only cue, but the contrast should be measured. |
| 5 | **Low** | Dynamic Type, touch target | `save` has no visible size or title. Nothing guarantees a 44×44 pt minimum target or room to grow with text. |

## Smallest native fixes

1. **Save control.** Replace the `UIView` and gesture with a `UIButton`:
   ```swift
   private let save = UIButton(configuration: .filled())
   // viewDidLoad:
   save.configuration?.title = "Save"
   save.addTarget(self, action: #selector(saveProfile), for: .touchUpInside)
   ```
   This gives the button trait, a label, a Voice Control name, focus and keyboard activation, and a standard hit area. The configuration title scales with Dynamic Type. If it has to stay a `UIView`, the fallback is `isAccessibilityElement = true`, `accessibilityLabel = "Save"`, `accessibilityTraits = .button`, and a 44 pt minimum size. That is more code and easier to get wrong.
2. **Status label.**
   ```swift
   status.font = .preferredFont(forTextStyle: .footnote)
   status.adjustsFontForContentSizeCategory = true
   status.numberOfLines = 0
   ```
   If you use a custom font, wrap it with `UIFontMetrics`.
3. **Avatar.** Choose one of two options:
   - If the image is decorative, set `isAccessibilityElement = false`. This is the default for `UIImageView`, so you can delete the lines.
   - If it carries information, use a specific label such as `"Profile photo of \(name)"`, without the word "image".
4. **Status color.** Use a semantic color that meets contrast in light, dark, and Increase Contrast, such as `.label` or a custom asset color. If you want green, use an asset color with light and dark variants and measure it. Aim for at least 4.5:1 for text.
5. **Layout.** Make sure the constraints don't fix heights, so the label and button can grow with text size.

## Verification

- **Automated:** run Xcode's Accessibility Inspector audit on a device or simulator. Add `performAccessibilityAudit()` in a UI test (Xcode 15+) to catch contrast, small hit regions, Dynamic Type clipping, and missing labels.
- **VoiceOver (on device):** swipe through the screen. Confirm that:
  - Save is reachable and identifies as a button.
  - Double-tap activates it.
  - The avatar either is skipped or has a meaningful label.
  
  Judge the content and role of what is announced, not exact wording, which varies by OS version and settings.
- **Voice Control:** enable "Show Names" and say "Tap Save". Check that the name appears and activation works. Also try "Show Numbers".
- **Dynamic Type:** step through the sizes in Settings, including the Accessibility sizes up to AX5, or use Xcode's Environment Overrides. Confirm the status text and button title grow, wrap, and don't clip or overlap.
- **Display settings:** check dark mode and Increase Contrast, and measure the status color contrast.
