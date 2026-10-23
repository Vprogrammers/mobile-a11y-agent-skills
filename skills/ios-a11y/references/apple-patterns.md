# Apple accessibility patterns

## SwiftUI

- Prefer native `Button`, `TextField`, `Toggle`, and navigation containers.
- Hide decorative images with `accessibilityHidden(true)`.
- Combine children only when the combined element has one clear meaning and action.
- Provide `accessibilityInputLabels` when visible text is not sufficient for Voice Control.
- Test layouts at accessibility Dynamic Type sizes.

## UIKit

- Set `isAccessibilityElement` only on the logical elements.
- Use native traits and actions.
- Keep `accessibilityFrame` or container bounds aligned with the visible and tappable control.
- Recompute layout-dependent frames after layout and trait changes.
- Use `UIAccessibility.post` sparingly and avoid duplicate speech.

## Sensitive input

- Use `textContentType = .oneTimeCode` for OTP input.
- Align visual masking with the value exposed to assistive technology.
- Never expose secret digits through debug descriptions, notifications, or analytics.
- Do not read Messages directly to implement OTP autofill.

## Testing

- Run XCUITest assertions for labels, values, identifiers, actions, focusable elements, and flow completion.
- Run `performAccessibilityAudit` where available, then triage rather than suppress findings broadly.
- Verify VoiceOver speech, rotor behavior, Voice Control overlays, Dynamic Type, and Switch Control on devices.
