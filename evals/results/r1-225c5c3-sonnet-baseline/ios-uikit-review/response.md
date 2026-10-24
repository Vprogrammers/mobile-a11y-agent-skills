# Review of `ProfileViewController.swift`

I reviewed the fixture as pasted and didn't open the file on disk. Nothing was edited or run, so every finding below comes from reading the code, not from testing on a device.

## Findings

| # | Sev | Area | Problem |
|---|-----|------|---------|
| 1 | **High** | VoiceOver, Voice Control | `save` is a plain `UIView` with a tap gesture. It has no `isAccessibilityElement`, label, or button trait, so VoiceOver users probably can't find or activate it. Voice Control has no name to target. It also has no text or image content, so nothing tells a sighted user what it does. |
| 2 | **High** | Dynamic Type | `status.font = .systemFont(ofSize: 14)` is a fixed size and ignores the user's text size. `adjustsFontForContentSizeCategory` isn't set, and `numberOfLines` is left at the default of 1. At large sizes the text won't scale, and once it does it will truncate. |
| 3 | **Medium** | VoiceOver | `avatar.accessibilityLabel = "Image"` is generic and says nothing about the content. It's also redundant, because the role is already conveyed by the image trait. If the avatar is decorative, it shouldn't be an element at all. |
| 4 | **Medium** | Color and contrast (also affects low-vision users) | `.green` text on an unknown background likely has weak contrast, especially on white. "Verified" is conveyed only by the word and color, with no icon, so it's low-risk for color-blind users, but the contrast is a real concern. |
| 5 | **Medium** | Voice Control, Dynamic Type | The `save` view has no size constraints or frame, so it has no guaranteed 44×44 pt hit target. This can't be confirmed from the fixture because the layout isn't shown. |
| 6 | **Low** | VoiceOver | `status` is a label, so it's accessible by default. If it's meant to describe the profile or avatar, it could be read as a separate element with no context. That depends on the layout. |

## Smallest native corrections

**1. Save control.** Replace the view and gesture with a `UIButton`. It's natively an element with a button trait, and it gets Voice Control and Switch Control support, focus, and `accessibilityActivate`.

```swift
private let save = UIButton(type: .system)
// viewDidLoad
var config = UIButton.Configuration.filled()
config.title = "Save"   // localized
save.configuration = config
save.addTarget(self, action: #selector(saveProfile), for: .touchUpInside)
```

The title becomes the accessibility label and the Voice Control name, so no custom label is needed. `UIButton.Configuration` also wraps text and grows with Dynamic Type. If the control must stay a `UIView`, set `isAccessibilityElement = true`, `accessibilityLabel = "Save"`, and `accessibilityTraits = .button`. This is a worse option because it doesn't get keyboard or Switch Control behavior for free.

**2. Status font.**
```swift
status.font = .preferredFont(forTextStyle: .footnote)
status.adjustsFontForContentSizeCategory = true
status.numberOfLines = 0
```
`.footnote` is about 13 pt by default. Use `.subheadline` if you want to stay close to the current 14 pt.

**3. Avatar.** Choose one of two options.
- If it's decorative, set `isAccessibilityElement = false`.
- If it conveys identity, label it with the person's name, for example `"Profile photo of \(name)"`, localized. Don't use "Image".

**4. Color.** Use a semantic color such as `.label`, or a dynamic color pair whose contrast meets WCAG AA (4.5:1 for small text) in light, dark, and Increase Contrast modes. If the green meaning matters, add an SF Symbol like `checkmark.seal`. The word "Verified" already carries the meaning.

**5. Hit target.** Constrain the button to at least 44×44 pt. A `UIButton.Configuration` with default insets usually gets there. Verify this in the layout rather than assuming it.

## Verification

- **Accessibility Inspector (Xcode):** run the audit for contrast, hit-region size, clipped text, and missing labels. Check the element list for the save control's role, label, and traits.
- **VoiceOver on a device:** swipe through and confirm that the save control is reachable and reads as a button, that the avatar is either skipped or has a meaningful label, and that the status reads sensibly. Judge by whether the information is present and in a sensible order, not by exact speech.
- **Voice Control:** say "Show names" and confirm that Save has a visible name. Then say "Tap Save".
- **Dynamic Type:** step through the sizes in Settings or the Xcode environment overrides, up to the largest Accessibility sizes. Confirm that the status text scales and wraps without truncation and that the button stays usable.
- **Contrast:** check the status color in light mode, dark mode, and Increase Contrast.
- **Automated test:** add an XCUITest that finds `app.buttons["Save"]` and taps it. This guards against regressions in role and label.

## Limits of this review

The fixture doesn't show the layout, localization, or how the views are added to the hierarchy. The hit-target and contrast findings (4 and 5) are therefore unconfirmed and need checking in the running app. The save action is an empty stub, so there's no state or feedback to review. After a save succeeds, you may want to post an accessibility announcement.
