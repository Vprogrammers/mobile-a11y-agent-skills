# Mobile accessibility review checklist

Last reviewed: 2026-10-24.

## Code signals

Scan the changed code for these signals before reading it line by line. Each one is a prompt to check the behavior, not a finding by itself. The platform references hold the detailed guidance.

| Signal in code | Check |
|---|---|
| Compose `items(...)`/`itemsIndexed(...)` without `key =`, or a list replaced wholesale on update | Focus and position survive insertions, removals, and reloads |
| `clearAndSetSemantics`, `mergeDescendants = true`, `.accessibilityElement(children: .combine/.ignore)` | No label, state, or secondary action is lost from the merged node |
| `pointerInput`, `detectTapGestures`, `onLongPress`, swipe or drag handlers, `.onTapGesture` | The action is also a native or custom accessibility action |
| Custom `View` with `onDraw`/canvas, or a UIKit view drawing several targets | Accessibility node contract or virtual children, not one `contentDescription` |
| `AccessibilityDelegateCompat`, `accessibilityTraits =`, `accessibilityElements =` | Superclass actions and traits are preserved and order matches dynamic content |
| Fixed `height`/`frame(height:)`, `maxLines = 1`, `lineLimit(1)`, `UIButton(type: .system)` titles | Text scales and reflows at the largest font and Dynamic Type sizes |
| Custom overlay, sheet, or dialog built from `Box`/`ZStack`/plain views | Modal boundary, system back or escape dismissal, and focus restoration |
| Compose `Canvas`, SwiftUI `Canvas`, `Chart`, or map views | A summary, reachable values or places, and color-independent series |
| Media3 `PlayerView`, `AVPlayer`, `VideoPlayer`, or custom playback controls | Captions follow system preferences, audio description where needed, and labeled, reachable controls |
| `WebView`, `WKWebView`, `loadUrl`, `loadHTMLString` | Native title for the web content and a separate audit of the DOM and focus transitions |
| `announceForAccessibility`, `UIAccessibility.post`, `liveRegion` on frequently changing text | Announcements are limited to important asynchronous changes |
| `FocusRequester` or `@AccessibilityFocusState` driven by ordinary state | Focus moves only for meaningful context changes |
| `clickable(indication = null)`, custom indications, or removed focus styles | Keyboard and switch focus stays visible |
| Password, OTP, payment, or identity fields with custom masking, blocked paste, or `contentType`/`textContentType` changes | Autofill, paste, and consistent visual and accessibility masking |
| `onBackPressed`, `KEYCODE_BACK`, missing insets on edge-to-edge screens | Back dismissal and focused content stay reachable on current SDK targets |

## Structure and semantics

- Prefer one logical element per logical control; group only when the result has one meaning and action.
- Expose concise name, role, value, state, actions, and relationships without duplicating visible text or native speech.
- Hide decorative content while preserving meaningful imagery, charts, status, and validation.
- Check headings, landmarks/containers, lists, collection position, modal boundaries, and reading order.
- Verify custom controls expose the same operability and state as their native equivalents.

## Navigation and input

- Preserve logical focus through navigation, sheets, dialogs, lazy lists, updates, and restored state.
- Avoid moving accessibility focus for ordinary value changes.
- Support keyboard, Switch Control/Switch Access, Voice Control/Voice Access, and external input.
- Provide alternatives to drag, multi-pointer, path-based, timed, and device-motion gestures.
- Keep Android targets at least 48 dp and Apple targets at least 44 pt as platform design baselines. Do not present these as a literal conversion of WCAG CSS pixels.
- Check that system bars, display cutouts, and the on-screen keyboard do not cover focused controls or errors, especially on Android apps that target SDK 35 or later.
- Check that dialogs, sheets, and custom panes dismiss through system back on Android and through escape/dismiss gestures on iOS.

## Visual access

- Test large font and accessibility text sizes without clipped text, lost actions, or horizontal scrolling for ordinary text.
- Avoid fixed-height text containers. Test orientation and narrow widths.
- Do not communicate state only through color, position, shape, sound, or animation.
- Evaluate text contrast, non-text contrast, focus visibility, dynamic colors, images, disabled states, and overlays in context.
- Respect reduced motion, increased contrast, reduced transparency, bold text, and dark appearance where supported.

## Content and flows

- Test errors, loading, empty states, confirmations, timeouts, session expiry, destructive actions, and asynchronous changes.
- Provide captions, transcripts, audio description, playback controls, and non-audio alternatives where media requires them.
- Give charts, maps, canvas, and custom drawing an equivalent textual or structured representation.
- Verify focus transitions into and out of WebViews and that web content does not create a second inaccessible navigation model.
- For Compose Multiplatform screens on iOS, verify behavior with VoiceOver on iOS; Android semantics tests do not establish iOS behavior.
- Preserve accessible authentication: allow paste, autofill, password managers, and alternatives to memory or transcription tasks.

## Privacy

- Do not log, persist, analytics-track, copy, or announce secrets unexpectedly.
- Align visual and accessibility masking.
- Use platform-supported autofill and consent-based flows instead of broad message or clipboard access.

## Evidence

- Distinguish static findings, unit tests, semantics/XCUITest evidence, scanner/audit results, simulator observations, and real-device assistive-technology results.
- Automated tools detect only a subset of barriers. Record OS, device, app build, assistive technology, settings, steps, expected result, and actual result for manual evidence.

Sources:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- Target Size (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- Focus Not Obscured (Minimum): https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html
- Android touch target guidance: https://developer.android.com/guide/topics/ui/accessibility/apps
- Apple accessibility guidelines: https://developer.apple.com/design/human-interface-guidelines/accessibility
