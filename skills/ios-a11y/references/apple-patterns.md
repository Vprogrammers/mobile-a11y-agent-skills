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
- Provide structured summaries and data access for charts; do not rely only on colored paths or canvas pixels. Do not distinguish series by color alone, and check 3:1 non-text contrast (WCAG 1.4.11).
- Swift Charts supports accessibility by default. When the default description of a mark is not meaningful, set `accessibilityLabel` and `accessibilityValue` on the marks.
- For a chart drawn another way, including an `Image` of a chart, attach `accessibilityChartDescriptor(_:)` with an `AXChartDescriptor` (iOS 15+). It describes the chart's axes and series so VoiceOver users can explore the data.
- SwiftUI `Canvas` offers no accessibility for individual drawn elements. Add synthetic elements with `accessibilityChildren(children:)`, or use `accessibilityRepresentation(representation:)` when a native control describes the drawing better.
- In UIKit, represent each meaningful drawn item with a `UIAccessibilityElement` in an accessibility container, with frames in screen coordinates.
- For maps, give each annotation a meaningful title and provide a list of the places shown with the same actions. Verify with VoiceOver that annotations are reachable instead of assuming it.
- Provide captions for prerecorded video with speech (WCAG 1.2.2) and audio description when important visual information is not in the soundtrack (WCAG 1.2.5). Mark caption tracks with `transcribesSpokenDialogForAccessibility` and description tracks with `describesVideoForAccessibility`.
- `AVPlayer` applies media selection from the system accessibility preferences by default (`appliesMediaSelectionCriteriaAutomatically`). Do not turn that off without replacing it. When you render captions yourself, read the caption preferences through the Media Accessibility framework.
- Give custom playback controls labels and keep them reachable with VoiceOver, Switch Control, and Full Keyboard Access. Audio that plays automatically for more than three seconds needs a control to pause or stop it, or to change its volume independently (WCAG 1.4.2).
- Respect Reduce Motion and provide a non-motion equivalent for state changes conveyed by animation.

### Bad: drawing only

```swift
Canvas { context, size in drawBars(sales, in: &context, size: size) }
    .frame(height: 160)
```

VoiceOver finds no elements for the bars.

### Better: synthetic elements for the data

```swift
Canvas { context, size in drawBars(sales, in: &context, size: size) }
    .frame(height: 160)
    .accessibilityLabel("Monthly sales")
    .accessibilityChildren {
        HStack {
            ForEach(sales) { sale in
                Rectangle()
                    .accessibilityLabel(sale.month)
                    .accessibilityValue("\(sale.value)")
            }
        }
    }
```

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
- Swift Charts: https://developer.apple.com/documentation/charts
- accessibilityChartDescriptor(_:): https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor(_:)
- accessibilityChildren(children:): https://developer.apple.com/documentation/swiftui/view/accessibilitychildren(children:)
- Canvas: https://developer.apple.com/documentation/swiftui/canvas
- AVPlayer.appliesMediaSelectionCriteriaAutomatically: https://developer.apple.com/documentation/avfoundation/avplayer/appliesmediaselectioncriteriaautomatically
- Media Accessibility: https://developer.apple.com/documentation/mediaaccessibility
- WCAG 2.2 captions, audio description, audio control, and non-text contrast: https://www.w3.org/TR/WCAG22/
