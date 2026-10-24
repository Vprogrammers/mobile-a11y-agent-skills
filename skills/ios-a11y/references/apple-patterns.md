# Apple accessibility patterns

Last reviewed: 2026-10-24. Verify availability and signatures against the deployment target and Xcode SDK used by the project.
Review interval: 180 days.

## SwiftUI structure

- Prefer native `Button`, `TextField`, `SecureField`, `Toggle`, `Slider`, `Picker`, `NavigationStack`, and presentation APIs.
- Use `.accessibilityElement(children: .combine)` only when descendants form one understandable element with compatible actions.
- Use `.contain` when children should remain individually reachable inside a logical group.
- Use `.ignore` only when replacing all descendant accessibility information deliberately.
- Use `.accessibilityHidden(true)` for decorative or redundant views, never to hide meaningful state.
- Keep `.accessibilityLabel` concise and do not repeat the control type or state VoiceOver already supplies.
- Expose changing state through `.accessibilityValue`; use hints only when the outcome is not clear from label, role, and context.
- Use `.accessibilityInputLabels` when Voice Control needs predictable spoken alternatives to visible text.
- Use `.accessibilityAdjustableAction` for custom increment/decrement controls.
- Use `.accessibilityAction(named:)` for meaningful secondary actions.
- Use `.accessibilityRotor` only when it materially improves navigation through repeated or structured content.

### Bad: gesture-only image action

```swift
Image(systemName: "trash")
    .onTapGesture(perform: delete)
```

### Better: native action

```swift
Button(action: delete) {
    Label("Delete", systemImage: "trash")
}
```

### Bad: combine unrelated buttons

```swift
HStack { editButton; deleteButton }
    .accessibilityElement(children: .combine)
```

### Better

Keep separate controls, or expose well-named custom actions on one row element only when that interaction has been intentionally designed and tested.

## Focus, navigation, and notifications

- Use `@AccessibilityFocusState` for meaningful SwiftUI context changes such as presenting validation summary or moving to newly displayed content. Do not bind routine selection state to accessibility focus.
- Prefer native navigation and presentation because they supply window and focus behavior.
- On supported SDKs, use SwiftUI accessibility announcement APIs for exceptional asynchronous results that state/value changes cannot convey.
- In UIKit, use `UIAccessibility.post(notification:argument:)` sparingly.
- Use `.screenChanged` for a major context/screen change and `.layoutChanged` for meaningful changes within the current context. Pass the intended focus target only when necessary.
- Set `accessibilityViewIsModal` for custom modal containers so VoiceOver cannot navigate behind them; restore focus appropriately after dismissal.
- Never post the same message from both SwiftUI state and UIKit notification bridges.

### Bad: force focus on every update

```swift
.onChange(of: value) { focused = true }
```

### Better

Update `.accessibilityValue` and move focus only when a new context or blocking error requires it.

## Dynamic Type and layout

- Use text styles and scalable fonts. In UIKit, use `UIFontMetrics` and set `adjustsFontForContentSizeCategory = true`.
- `UIButton(type: .system)` with `setTitle` keeps a fixed 15 pt title at every content size. Measured on the iOS 26 simulator, the title was still 15 pt at AX5. Use `UIButton.Configuration`, such as `UIButton(configuration: .plain())`, whose title follows Dynamic Type. Alternatively, set a text-style font with `adjustsFontForContentSizeCategory = true` on the title label.
- In SwiftUI, use `@ScaledMetric` for dimensions that should scale with text.
- Use `ViewThatFits`, adaptive stacks, and layout changes at accessibility Dynamic Type sizes instead of shrinking text.
- Use `dynamicTypeSize` environment information to change layout, not to cap user settings without a documented exceptional reason.
- Avoid fixed heights and single-line assumptions. Test all accessibility sizes, landscape, localization expansion, and narrow screens.
- Provide Large Content Viewer support for small controls in dense interfaces when larger permanent presentation is not practical.

### Bad: fixed text row

```swift
Text(title).frame(height: 44)
```

### Better

```swift
Text(title)
    .fixedSize(horizontal: false, vertical: true)
    .frame(minHeight: 44)
```

## Custom controls, charts, and media

- Make custom adjustable controls expose current value, bounds, and increment/decrement actions.
- Provide structured summaries and data access for charts; do not rely only on colored paths or canvas pixels.
- Ensure custom-drawn elements have meaningful accessibility elements and frames in screen coordinates when using UIKit containers.
- Provide captions, transcripts, audio description, and accessible playback controls when required by the content.
- Respect Reduce Motion and provide a non-motion equivalent for state changes conveyed by animation.

## UIKit details

- Set `isAccessibilityElement` on logical leaf elements, not indiscriminately on containers and all descendants.
- Preserve native `accessibilityTraits` and add/remove only the traits that represent actual semantics.
- Keep `accessibilityFrame` or `accessibilityFrameInContainerSpace` aligned with visible/tappable content and update it after layout changes.
- Use `accessibilityElements` ordering only to correct a demonstrated problem; keep it synchronized with dynamic content.
- Use custom actions for secondary operations and `accessibilityIncrement`/`accessibilityDecrement` for adjustable controls.

## Input, authentication, and privacy

- Preserve editing, paste, selection, dictation, hardware keyboard, password manager, and AutoFill behavior.
- Use appropriate `textContentType` values for names, addresses, credentials, and one-time codes when applicable.
- Do not require memory, transcription, puzzles, or blocked paste as the only authentication path.
- Keep visual and accessibility masking consistent and never expose secrets through labels, debug output, analytics, notifications, or screenshots.
- Do not design around general message-reading access; use supported system AutoFill and user-mediated input for verification codes.

## Web content

- Test VoiceOver entry/exit, headings, forms, zoom, keyboard, errors, authentication, and focus restoration in `WKWebView`.
- Native accessibility modifiers cannot repair inaccessible DOM content.
- Title the screen in native navigation so VoiceOver users know what the web content is before they enter it.

### Bad: page blocks zoom

```html
<meta name="viewport" content="width=device-width, user-scalable=no">
```

### Better: let people zoom regardless of the viewport

```swift
let configuration = WKWebViewConfiguration()
configuration.ignoresViewportScaleLimits = true
let webView = WKWebView(frame: .zero, configuration: configuration)
```

Still report the restrictive viewport to the web owners. Other browsers and web views do not apply this override.

## Diagnosis

- Use Accessibility Inspector to inspect hierarchy, labels, values, traits, actions, hit regions, and contrast before changing modifiers.
- Keep accessibility identifiers separate from user-facing labels.
- For test-layer choice, XCTest/XCUITest APIs, audits, and evidence limits, invoke the `mobile-a11y-testing` skill.

Official sources:

- Apple accessibility: https://developer.apple.com/accessibility/
- SwiftUI accessibility: https://developer.apple.com/documentation/swiftui/accessibility
- UIKit accessibility: https://developer.apple.com/documentation/uikit/accessibility
- UIButton.Configuration: https://developer.apple.com/documentation/uikit/uibutton/configuration-swift.struct
- WKWebViewConfiguration.ignoresViewportScaleLimits: https://developer.apple.com/documentation/webkit/wkwebviewconfiguration/ignoresviewportscalelimits
