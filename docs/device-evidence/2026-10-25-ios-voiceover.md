# iOS VoiceOver device check, 2026-10-25

Recorded with [the real-device evidence template](../../skills/mobile-a11y-testing/references/real-device-evidence-template.md). One record covers several flows because they share the device, build, and settings.

## Context

- Product and flow: compiled guidance patterns from `samples/ios`, each shown alone on a screen.
- Platform and OS version: iOS 26.7.2.
- Physical device: iPhone 14.
- App version and build: a temporary harness app that wrapped `samples/ios/Sources/ApplePatterns` in an app target, signed with a personal development team. It is not part of the repository and was uninstalled after the session.
- Build source or commit: `f5d11bc`.
- Date: 2026-10-25.
- Tester: repository maintainer, reporting what VoiceOver said and what the Caption Panel showed. Claude Code launched each screen over `devicectl`; VoiceOver speech cannot be read from the Mac.
- Assistive technology and version: VoiceOver on iOS 26.7.2, Caption Panel on.
- Relevant settings: default VoiceOver voice and verbosity.
- Text or font scale: default.
- Input method: VoiceOver touch gestures.
- Locale and layout direction: English, left to right.
- Network and account state: not relevant.

## Results

Wording is as the tester reported it. Exact phrasing can differ between iOS versions and VoiceOver settings.

| Requirement | Steps | Actual result | Result |
|---|---|---|---|
| A section title exposes a heading with its level | Swipe to “Shipping” | “Shipping, Heading level 2” | Pass |
| A custom toggle row exposes the toggle trait and state | Swipe to “Read receipts” | “Read receipts, Switch button, On, Double-tap to toggle setting” | Pass |
| A Markdown link in `Text` is a link | Swipe to “Messages follow our terms.” | VoiceOver said “link” | Pass |
| SwiftUI `languageIdentifier` switches pronunciation | Swipe to “SwiftUI says plat du jour” | Tester heard French for “plat du jour” | Pass |
| UIKit `accessibilityLanguage` switches pronunciation | Swipe to “UIKit says plat du jour” | Tester heard a French voice | Pass |
| The selected filter exposes the selected trait | Swipe through “All”, “Favorites”, “Shared” | Tester confirmed the expected output | Pass |
| A custom panel closes with the VoiceOver escape gesture | Two-finger scrub on the panel | The panel closed and “Panel closed” appeared | Pass |
| Carousel pause, Smart Invert, and the held-out settings fixture | — | Not run, to keep the session short | Not run |

- Evidence attachment or link (redacted): none kept; results are the tester's reports.
- Issue link: none.
- Known limitations: one device, one iOS version, default voice. Two results are confirmations rather than transcripts. Voice Control, Switch Control, Full Keyboard Access, Dynamic Type sizes, and RTL were not tested.
- Follow-up owner: repository maintainer.

## Evidence boundary

This record describes the tested configuration only. It does not prove behavior on other devices, OS versions, assistive technologies, settings, locales, flows, or future releases.
