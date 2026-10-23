---
name: ios-a11y
description: Implement or review native Apple accessibility in SwiftUI or UIKit, including VoiceOver, Voice Control, Switch Control, Dynamic Type, focus, traits, values, announcements, autofill, reduced motion, contrast, and XCUITest audits.
---

# Implement iOS accessibility

1. Prefer standard SwiftUI and UIKit controls.
2. Expose one logical element for one control and hide decorative subviews.
3. Supply concise labels, values, traits, actions, and input labels.
4. Keep the backing input frame aligned with the visible control and its touch target.
5. Use accessibility focus changes only for meaningful context changes.
6. Post announcements only for important results that native state updates do not communicate.
7. Support Dynamic Type, Voice Control, Switch Control, Full Keyboard Access, Reduce Motion, Increase Contrast, and Reduce Transparency.
8. Preserve `.oneTimeCode`, paste, keyboard, and native text-editing behavior.
9. Add unit or XCUITest coverage and use `performAccessibilityAudit` where supported.
10. Verify actual VoiceOver and Voice Control behavior on a real device.

Read [references/apple-patterns.md](references/apple-patterns.md) for SwiftUI and UIKit guidance.
