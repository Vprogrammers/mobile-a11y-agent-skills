# Apple accessibility patterns

Last reviewed: 2026-10-25. Verify availability and signatures against the deployment target and Xcode SDK used by the project.
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
- Give a custom toggle, such as a tappable row that switches a setting, the toggle trait and its state: `.accessibilityAddTraits(.isToggle)` with `.accessibilityValue` in SwiftUI, or the `.toggleButton` trait in UIKit; both need iOS 17 or later. Prefer a native `Toggle` with a real label.
- Expose inline links as links: use `Link`, or a Markdown or `AttributedString` link inside `Text`, instead of `onTapGesture` on a text range. Verify with VoiceOver that each link is reachable.
- Expose selection state with the selected trait, not only color: `.accessibilityAddTraits(filter == option ? .isSelected : [])` on each option, or use a native `Picker` with the segmented style.
- Use `.accessibilityRotor` only when it materially improves navigation through repeated or structured content.
- Mark section titles with `.accessibilityAddTraits(.isHeader)` so VoiceOver users can move between them with the Headings rotor. Add `.accessibilityHeading(_:)` with a level when the screen has nested sections. Use headings for real sections, not for visual emphasis.
- Use `.accessibilitySortPriority(_:)` inside a `.contain` group only to correct a demonstrated reading-order problem, such as a total drawn below the line items that must be read first. Higher priority is read first.
- Keep tappable targets at least 44 × 44 pt. Use `.frame(minWidth: 44, minHeight: 44)` with `.contentShape(Rectangle())` for small icons, so the hit region matches the frame.

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

### Better: a section title with a level

```swift
Text(title)
    .font(.title2)
    .accessibilityAddTraits(.isHeader)
    .accessibilityHeading(.h2)
```

## Names, voice control, and localization

- Mark text in another language so VoiceOver pronounces it correctly. In UIKit, set `accessibilityLanguage` to a BCP 47 tag on the element. In SwiftUI, an `AttributedString` run can carry Foundation's `languageIdentifier` attribute; verify on a device that VoiceOver switches voices, because SwiftUI does not document how it maps that attribute.
- Keep visible control text in the accessibility label and Voice Control input labels, preferably at the start. A control shown as “Continue” but labeled only “Submit order” is difficult to activate by saying what is visible.
- Use `.accessibilityInputLabels` for concise localized synonyms only when they improve Voice Control recognition; include the visible label and do not use input labels to hide a mismatched accessibility label.
- Localize labels, values, hints, custom-action names, errors, and announcements as complete phrases. Use String Catalog pluralization and locale-aware number/date formatting instead of concatenating fragments.
- Test localization expansion, right-to-left layout, mixed-direction text, and in-app locale changes. Keep visible and accessibility content synchronized.
- Do not gate essential semantics, navigation, or actions on a VoiceOver-running status check. VoiceOver status does not represent Voice Control, Switch Control, Full Keyboard Access, or every disabled user and can change while the app runs.

## Focus, navigation, and notifications

- Use `@AccessibilityFocusState` for meaningful SwiftUI context changes such as presenting validation summary or moving to newly displayed content. Do not bind routine selection state to accessibility focus.
- Prefer native navigation and presentation because they supply window and focus behavior.
- Announce only exceptional asynchronous results that a state or value change cannot convey. On iOS 17 and later, use `AccessibilityNotification.Announcement(message).post()`; in UIKit, `UIAccessibility.post(notification: .announcement, argument: message)`. Post UIKit notifications sparingly.
- Use `.screenChanged` for a major context/screen change and `.layoutChanged` for meaningful changes within the current context. Pass the intended focus target only when necessary.
- Set `accessibilityViewIsModal` for custom modal containers so VoiceOver cannot navigate behind them; restore focus appropriately after dismissal.
- Let VoiceOver users dismiss custom modals with the escape gesture (a two-finger Z). In UIKit, override `accessibilityPerformEscape()` to dismiss and return `true`. In SwiftUI, add `.accessibilityAction(.escape) { dismiss() }` and `.accessibilityAddTraits(.isModal)` to a custom panel. System sheets and alerts already handle escape.
- SwiftUI has no error property for a text field. Keep the error as visible text next to the field, in reading order after it. After a failed submit, move focus with `@AccessibilityFocusState` to the first invalid field or a summary, and do not replace the field's value with the error.
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
- Provide Large Content Viewer support for small controls in dense interfaces when larger permanent presentation is not practical: `.accessibilityShowsLargeContentViewer()` in SwiftUI, or `UILargeContentViewerInteraction` with `showsLargeContentViewer` and `largeContentTitle` in UIKit.

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

## Display settings

People turn on most of these settings in Accessibility > Display & Text Size; Reduce Motion is under Accessibility > Motion, and Full Keyboard Access under Accessibility > Keyboards. SwiftUI exposes them as environment values that update the view; UIKit exposes them as `UIAccessibility` properties with matching status-change notifications.

- **Differentiate Without Color** (`accessibilityDifferentiateWithoutColor`, `UIAccessibility.shouldDifferentiateWithoutColor`). Never convey state by color alone. When this setting is on, add a shape, symbol, or text even where color normally carries a secondary cue.
- **Bold Text** (`legibilityWeight`, which reflects this setting, or `UIAccessibility.isBoldTextEnabled`). When text uses a custom font or is drawn by the app, read the setting and apply a heavier weight.
- **Button Shapes** (`accessibilityShowButtonShapes`, `UIAccessibility.buttonShapesEnabled`, iOS 14+). For borderless or text-only custom buttons, add an underline or background shape when the setting is on, so actionable text is distinguishable from plain text.
- **On/Off Labels** (`UIAccessibility.isOnOffSwitchLabelsEnabled`). Prefer the native `Toggle` and `UISwitch`. A custom switch must read this setting and show on and off labels.
- **Smart Invert** (`accessibilityIgnoresInvertColors()`, `UIView.accessibilityIgnoresInvertColors`). Photos, video, and other media must keep their real colors when people use Smart Invert. Apply the modifier to the media view, not to the whole screen.
- **Reduce Transparency** (`accessibilityReduceTransparency`). Replace blurs and translucent backgrounds with opaque ones, and keep text contrast at 4.5:1 against the result.
- **Reduce Motion** (`accessibilityReduceMotion`, `UIAccessibility.isReduceMotionEnabled`). Replace large movement, parallax, and zooming transitions with a fade or no animation, and keep the state change visible.
- **Increase Contrast** (`colorSchemeContrast == .increased`, `UIAccessibility.isDarkerSystemColorsEnabled`). System colors adapt; give custom colors a higher-contrast variant, for example in the asset catalog's High Contrast appearance.
- **Full Keyboard Access**. Keep every control reachable with Tab and the arrow keys, keep the system focus indicator visible, and offer `.keyboardShortcut` for frequent actions. Test with a hardware keyboard on a device.
- Test each setting on a device together with large Dynamic Type sizes, because the combinations change layout.

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
- Content that moves or advances on its own for more than five seconds, such as a carousel, needs a visible pause or stop control for everyone (WCAG 2.2.2 Pause, Stop, Hide), and should stop when Reduce Motion is on. If you also adapt to VoiceOver, observe it with `@Environment(\.accessibilityVoiceOverEnabled)` or `UIAccessibility.voiceOverStatusDidChangeNotification`; a one-time `UIAccessibility.isVoiceOverRunning` read misses later changes and does not cover Switch Control or Voice Control users.
- Give actionable content that disappears on its own, such as an Undo banner, enough time or keep it until dismissed (WCAG 2.2.1 Timing Adjustable).

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
                    .accessibilityValue(Text(sale.value, format: .number))
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
- Mark section titles with the `.header` trait.

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
- Differentiate Without Color: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydifferentiatewithoutcolor
- Bold Text (legibilityWeight): https://developer.apple.com/documentation/swiftui/environmentvalues/legibilityweight
- Button Shapes: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityshowbuttonshapes
- On/Off Labels: https://developer.apple.com/documentation/uikit/uiaccessibility/isonoffswitchlabelsenabled
- Reduce Transparency: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency
- Swift Charts: https://developer.apple.com/documentation/charts
- accessibilityChartDescriptor(_:): https://developer.apple.com/documentation/swiftui/view/accessibilitychartdescriptor(_:)
- accessibilityChildren(children:): https://developer.apple.com/documentation/swiftui/view/accessibilitychildren(children:)
- Canvas: https://developer.apple.com/documentation/swiftui/canvas
- AVPlayer.appliesMediaSelectionCriteriaAutomatically: https://developer.apple.com/documentation/avfoundation/avplayer/appliesmediaselectioncriteriaautomatically
- Media Accessibility: https://developer.apple.com/documentation/mediaaccessibility
- accessibilityHeading(_:): https://developer.apple.com/documentation/swiftui/view/accessibilityheading(_:)
- accessibilitySortPriority(_:): https://developer.apple.com/documentation/swiftui/view/accessibilitysortpriority(_:)
- accessibilityPerformEscape(): https://developer.apple.com/documentation/objectivec/nsobject-swift.class/accessibilityperformescape()
- AccessibilityNotification.Announcement: https://developer.apple.com/documentation/accessibility/accessibilitynotification/announcement
- accessibilityLanguage: https://developer.apple.com/documentation/objectivec/nsobject-swift.class/accessibilitylanguage
- Large Content Viewer: https://developer.apple.com/documentation/uikit/uilargecontentviewerinteraction
- Reduce Motion: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion
- Smart Invert (accessibilityIgnoresInvertColors): https://developer.apple.com/documentation/swiftui/view/accessibilityignoresinvertcolors(_:)
- Toggle trait (UIAccessibilityTraitToggleButton, iOS 17): https://developer.apple.com/documentation/uikit/uiaccessibilitytraits/togglebutton
- accessibilityVoiceOverEnabled: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityvoiceoverenabled
- Increase Contrast (colorSchemeContrast): https://developer.apple.com/documentation/swiftui/environmentvalues/colorschemecontrast
- WCAG 2.2 captions, audio description, audio control, and non-text contrast: https://www.w3.org/TR/WCAG22/
