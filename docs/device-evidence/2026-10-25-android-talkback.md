# Android TalkBack device check, 2026-10-25

Recorded with [the real-device evidence template](../../skills/mobile-a11y-testing/references/real-device-evidence-template.md). One record covers several flows because they share the device, build, and settings.

## Context

- Product and flow: compiled guidance patterns from `samples/android` and the `compose-message-thread-review` and `heldout-compose-reader-review` fixtures, each shown alone on a screen.
- Platform and OS version: Android 17 (API 37).
- Physical device: Samsung Galaxy Z Fold7 (SM-F966B), folded, cover display (1080 × 2520, 420 dpi).
- App version and build: a temporary harness app that wrapped `samples/android` as an application. It is not part of the repository and was uninstalled after the session.
- Build source or commit: `b1230de` (0.8.0 plus a README change).
- Date: 2026-10-25.
- Tester: repository maintainer, with Claude Code reading TalkBack's verbose speech log over `adb`.
- Assistive technology and version: Google TalkBack 17.1.0.
- Relevant settings: TalkBack log output level Verbose; Time to take action 10 seconds; animations on.
- Text or font scale: 1.15.
- Input method: touch gestures (swipe right and left, double tap, three-finger tap). Keyboard shortcuts and touches injected over `adb` did not move TalkBack focus, so a person performed every gesture.
- Locale and layout direction: English, left to right.
- Network and account state: not relevant; no account or network data.

## Results

Speech is quoted from TalkBack's log. The order of parts can differ between TalkBack versions and settings.

| Requirement | Steps | Actual result | Result |
|---|---|---|---|
| A custom Compose `clickable` row exposes a role and its `onClickLabel` | Swipe to “Order 1234” | “Order 1234. Button.” then “Double-tap to Open order details” | Pass |
| The row meets the 48 dp minimum | Read bounds with `uiautomator dump` | 126 px at 420 dpi = 48 dp | Pass |
| A `toggleable` row with `Role.Switch` is one node with state | Swipe to the row, double tap | “On. Read receipts. Switch.” then “Double-tap to toggle”; after double tap, “Off” | Pass |
| A `LinkAnnotation` link is reachable as a link | Swipe to the text | “Messages follow our terms.” then “Double-tap to open link. Actions available” | Pass |
| Contrast: `ClickableText` links are not reachable | Swipe through the `MessageThread` fixture | “Messages follow our terms and privacy policy.” with no link hint or actions | Defect confirmed |
| Contrast: a clickable row beside its own `Switch` | Same screen | “Send read receipts” without role or state, then a separate “On. Switch” with no name | Defect confirmed |
| An actionable banner honors Time to take action | Open the Undo banner and wait | Dismissed after 10,043 ms; its default is 4,000 ms | Pass |
| Compose `SpanStyle(localeList)` switches pronunciation | Swipe to “The menu says plat du jour” | Tester heard French for “plat du jour”; log shows fragments “The menu says ” `locale=null` and “plat du jour” `locale=fr_FR` | Pass |
| A drawn chart exposes a summary and its values | Swipe through the chart | “Sales rose from 3 to 5”, “May: 3”, “June: 5” | Pass |
| Views click label and custom action | Swipe to “Order 1234”, three-finger tap | “Double-tap to Open order details. Actions available”; the actions menu lists “Archive” | Pass |
| A clickable Views `TextView` announces a role | Same row | No role is announced | Observation: guidance now says to use a `Button` |
| Views `accessibilityDataSensitive` keeps the field readable by TalkBack | Swipe to the security code field | “password. Card security code. Edit box” | Pass. Restriction of non-tool services cannot be observed with TalkBack |
| Compose password field exposes error and password semantics | Swipe to the field | “Error: Enter your password. Editing. password. Edit box. Password. Enter your password.” | Pass with a defect: the error is read twice |
| The same field with the visible error hidden from accessibility | Swipe to the variant | “Error: Enter your password. password. Edit box. Password.” | Pass; the sample now uses this form |
| Views pane title is announced | — | Not run: the title was set at launch, not when a pane appears | Not run |

- Evidence attachment or link (redacted): TalkBack log excerpts are quoted above; no screenshots or recordings were kept.
- Issue link: none.
- Known limitations: one device, one TalkBack version, cover display only, default English voice. Voice Access, Switch Access, keyboard navigation, RTL, and font scales other than 1.15 were not tested. iOS and VoiceOver were not tested.
- Follow-up owner: repository maintainer.

## Evidence boundary

This record describes the tested configuration only. It does not prove behavior on other devices, OS versions, assistive technologies, settings, locales, flows, or future releases.
