---
name: ios-a11y
description: Implement or review SwiftUI and UIKit accessibility. Use for VoiceOver or Voice Control problems, headings, selection state, escape from custom modals, Smart Invert, auto-advancing content, accessibilityLabel, visible-label matching, localization, VoiceOver-status detection, accessibilityValue, traits, focus, adjustable actions, rotors, Dynamic Type, Large Content Viewer, reduced motion, contrast, modal navigation, accessibility audits, or “VoiceOver does not read this”.
---

# Implement iOS accessibility

1. Inspect the Accessibility Inspector hierarchy and behavior before adding modifiers.
2. Prefer native SwiftUI and UIKit controls and preserve their label, value, traits, actions, focus, keyboard, and editing behavior.
3. Group, contain, or ignore children according to the logical interaction; do not flatten unrelated actions.
4. Expose adjustable and custom controls through native actions, not gesture instructions alone.
5. Move accessibility focus only for meaningful context changes and choose screen/layout notifications deliberately in UIKit.
6. Give users enough time: keep actionable content until it is dismissed or long enough to reach, and add a pause control to content that moves on its own.
7. Support accessibility Dynamic Type sizes, Voice Control, Switch Control, Full Keyboard Access, Reduce Motion, Increase Contrast, Reduce Transparency, Smart Invert, Bold Text, Button Shapes, Differentiate Without Color, On/Off Labels, and Large Content Viewer where relevant.
8. Test navigation, modals, lists, sliders, charts, custom drawing, media, and web content.
9. Run XCUITest accessibility audits where supported, triage findings, and verify VoiceOver/Voice Control on a real device.

## Where to look

Match the code in the change to a section of [references/apple-patterns.md](references/apple-patterns.md), which holds the APIs, traps, and bad-to-good examples. Read the whole file when the change spans several rows or none.

| Code in the change | Section |
|---|---|
| `accessibilityElement(children:)`, labels, values, traits, custom toggles, inline links, headings, reading order, selection shown by color, gestures, custom actions, small targets | [SwiftUI structure](references/apple-patterns.md#swiftui-structure) |
| `accessibilityLabel`, `accessibilityInputLabels`, hard-coded accessibility text, String Catalog, locale or RTL handling, text in another language | [Names, voice control, and localization](references/apple-patterns.md#names-voice-control-and-localization) |
| `@AccessibilityFocusState`, `UIAccessibility.post`, announcements, modals, escape, presentations, field errors | [Focus, navigation, and notifications](references/apple-patterns.md#focus-navigation-and-notifications) |
| Fonts, fixed frames, `UIButton` titles, `dynamicTypeSize` | [Dynamic Type and layout](references/apple-patterns.md#dynamic-type-and-layout) |
| Custom fonts or switches, borderless buttons, color-coded state, blur, motion, custom colors, keyboard navigation, photos or video under Smart Invert | [Display settings](references/apple-patterns.md#display-settings) |
| Custom controls, `Canvas`, charts, maps, players, carousels, timers that hide actionable content | [Custom controls, charts, and media](references/apple-patterns.md#custom-controls-charts-and-media) |
| `isAccessibilityElement`, `accessibilityElements`, frames, UIKit traits | [UIKit details](references/apple-patterns.md#uikit-details) |
| Text fields, passwords, one-time codes, AutoFill | [Input, authentication, and privacy](references/apple-patterns.md#input-authentication-and-privacy) |
| `WKWebView` | [Web content](references/apple-patterns.md#web-content) |
