---
name: ios-a11y
description: Implement or review SwiftUI and UIKit accessibility. Use for VoiceOver or Voice Control problems, accessibilityLabel, accessibilityValue, traits, focus, adjustable actions, rotors, Dynamic Type, Large Content Viewer, reduced motion, contrast, modal navigation, accessibility audits, or “VoiceOver does not read this”.
---

# Implement iOS accessibility

1. Inspect the Accessibility Inspector hierarchy and behavior before adding modifiers.
2. Prefer native SwiftUI and UIKit controls and preserve their label, value, traits, actions, focus, keyboard, and editing behavior.
3. Group, contain, or ignore children according to the logical interaction; do not flatten unrelated actions.
4. Expose adjustable and custom controls through native actions, not gesture instructions alone.
5. Move accessibility focus only for meaningful context changes and choose screen/layout notifications deliberately in UIKit.
6. Support accessibility Dynamic Type sizes, Voice Control, Switch Control, Full Keyboard Access, Reduce Motion, Increase Contrast, Reduce Transparency, and Large Content Viewer where relevant.
7. Test navigation, modals, lists, sliders, charts, custom drawing, media, and web content.
8. Run XCUITest accessibility audits where supported, triage findings, and verify VoiceOver/Voice Control on a real device.

Read [references/apple-patterns.md](references/apple-patterns.md) for APIs, traps, and bad-to-good examples.
