# Mobile accessibility review checklist

Last reviewed: 2026-10-25.

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
| Custom fonts, custom switches, borderless text buttons, or state shown by color on iOS | Bold Text, On/Off Labels, Button Shapes, and Differentiate Without Color |
| Compose `Canvas`, SwiftUI `Canvas`, `Chart`, or map views | A summary, reachable values or places, and color-independent series |
| Media3 `PlayerView`, `AVPlayer`, `VideoPlayer`, or custom playback controls | Captions follow system preferences, audio description where needed, and labeled, reachable controls |
| `WebView`, `WKWebView`, `loadUrl`, `loadHTMLString` | Native title for the web content and a separate audit of the DOM and focus transitions |
| `announceForAccessibility`, `UIAccessibility.post`, `liveRegion` on frequently changing text | Announcements are limited to important asynchronous changes; `View.announceForAccessibility` is deprecated as of API level 36 |
| `FocusRequester` or `@AccessibilityFocusState` driven by ordinary state | Focus moves only for meaningful context changes |
| `clickable(indication = null)`, custom indications, or removed focus styles | Keyboard and switch focus stays visible |
| Password, OTP, payment, or identity fields with custom masking, blocked paste, or `contentType`/`textContentType` changes | Autofill, paste, and consistent visual and accessibility masking |
| Android sensitive fields without `sensitiveData`/`accessibilityDataSensitive`, or the flag applied broadly | Untrusted services are restricted without hiding necessary content from legitimate assistive technologies; masking, redaction, and secure logging remain intact |
| Custom Android text rendering that bypasses `android.text.Layout` | Android 16 outline-text preference is observed and the result remains legible |
| Visible text differs from `contentDescription`, `accessibilityLabel`, or Voice Control input labels | The accessible name contains the visible label so spoken control names remain predictable |
| Concatenated user-facing strings, hard-coded accessibility text, manual plurals, or locale-dependent formatting | Labels, values, hints, and announcements remain grammatical and synchronized in every supported locale and RTL/BiDi layout |
| Touch-exploration checks, enabled accessibility-service inspection, or VoiceOver-running status checks | Core semantics and functionality do not depend on detecting one assistive technology |
| `onBackPressed`, `KEYCODE_BACK`, missing insets on edge-to-edge screens | Back dismissal and focused content stay reachable on current SDK targets |
| `clickable` row that also contains a clickable `Switch`, `Checkbox`, or `RadioButton` | One toggleable or selectable node with a role and state |
| `ClickableText`, links resolved from tap offsets | Each link is reachable as a link (`LinkAnnotation`) |
| A fixed `delay`, timer, or `asyncAfter` that hides content with an action | The user's recommended timeout or an explicit dismiss keeps the action reachable |
| Auto-advancing carousels or timers that change content | A pause or stop control exists for everyone, and VoiceOver or TalkBack detection is observed, not read once |
| Selection shown by background or text color | The selected state is exposed (selected trait, `selectable`, segmented `Picker`) |
| Photos, video, or maps in iOS views | Media opts out of Smart Invert with `accessibilityIgnoresInvertColors` |
| Section titles styled only with a larger or bolder font | Headings are exposed (`heading()`, `.isHeader`, `.header`) so screen-reader users can navigate by them |
| Custom `clickable` rows or cards without `role` or `onClickLabel` | The node exposes the role it acts as and a meaningful action label |
| Custom modal panels on iOS without an escape action | VoiceOver's escape gesture dismisses them (`accessibilityPerformEscape`, `.accessibilityAction(.escape)`) |
| Quotes, names, or content in a language other than the app's | The language is marked (`LocaleSpan`, `SpanStyle(localeList)`, `accessibilityLanguage`) so pronunciation is correct |

## Structure and semantics

- Prefer one logical element per logical control; group only when the result has one meaning and action.
- Expose concise name, role, value, state, actions, and relationships without duplicating visible text or native speech.
- Hide decorative content while preserving meaningful imagery, charts, status, and validation.
- Check headings, landmarks/containers, lists, collection position, modal boundaries, and reading order.
- Verify custom controls expose the same operability and state as their native equivalents.
- Keep a control's visible label in its accessible name, preferably at the start, so Voice Access and Voice Control users can speak what they see.

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
- Localize labels, values, hints, actions, errors, and announcements with resource-backed complete phrases, plural rules, locale-aware formatting, and tested RTL/BiDi ordering. Keep accessibility text synchronized when the app locale changes.
- Do not gate core semantics or functionality on TalkBack, VoiceOver, touch-exploration, or accessibility-service detection. A detected service is not a reliable proxy for disability or input method.

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
- WCAG2ICT for WCAG 2.2: https://www.w3.org/TR/wcag2ict-22/
