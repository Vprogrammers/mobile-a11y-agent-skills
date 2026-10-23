# Expected: iOS SwiftUI profile review

## Must find

| ID | Location | Min severity | Evidence the finding must contain |
|---|---|---|---|
| `combined-actions` | `HStack` with Edit and Delete, `.combine` | P1 | Two unrelated actions merged into one element; keep them separate. |
| `focus-on-every-update` | `ProgressView` `.onChange` | P1 | Focus moves on every progress tick; expose value and move focus only on a context change. |
| `dynamic-type-capped` | `Text("Profile")` `.dynamicTypeSize(...large)` | P1 | User text size is capped; adapt layout instead. |
| `color-only-status` | Verification `Circle` | P1 | Status conveyed only by color and not exposed to assistive technology; add text or label/value. |
| `gesture-only-avatar` | `Image` `.onTapGesture` | P2 | Tap gesture without button trait or label; use `Button`. P2 because Edit is also reachable through the Edit button. |
| `unaudited-webview` | `HelpWebView` | Note | Reported as a verification gap for VoiceOver entry/exit and DOM semantics, not as a proven defect. |

## Must not

- Present the WebView as definitely inaccessible without evidence.
- Recommend `.accessibilityHidden(true)` on the verification indicator.

## Device checks expected

VoiceOver navigation and rotor, Voice Control labels for the avatar and buttons, largest accessibility text size, and WebView entry and exit.
