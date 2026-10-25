# Android accessibility patterns

Last reviewed: 2026-10-25. Verify exact signatures against the Android and Compose versions used by the project.
Review interval: 180 days.

## Compose semantics

- Prefer `Button`, `TextField`, `Checkbox`, `Switch`, `Slider`, and Material components before constructing custom equivalents.
- Use `Modifier.semantics { ... }` to add missing semantic properties.
- Use `Modifier.clearAndSetSemantics { ... }` only when replacing all descendant semantics intentionally; it hides descendant information from accessibility and testing services.
- Use `mergeDescendants = true` only when the merged node retains every necessary label, state, action, and relationship.
- Use `hideFromAccessibility()` for decorative or redundant descendants on current Compose versions; check project compatibility before replacing older `invisibleToUser()` usage.
- Use `heading()` for actual section headings, not for visual emphasis.
- Use `paneTitle` for meaningful window-like changes such as sheets or custom panes.
- Use `error()` to expose helpful error text associated with the relevant field.
- Use `stateDescription` only when standard state semantics do not communicate the state adequately.
- Use `customActions` to make gesture-only or nested actions directly available. Avoid duplicating the primary click action.
- Use `isTraversalGroup` and `traversalIndex` only to correct a demonstrated reading-order problem. Visual placement alone does not guarantee traversal order.
- Use `collectionInfo`, `collectionItemInfo`, and progress/range semantics for custom collections and adjustable controls when native components cannot be used.
- Make a row that toggles a setting one node: `Modifier.toggleable(value = checked, role = Role.Switch, onValueChange = onChange)` on the row, and `Switch(checked = checked, onCheckedChange = null)` inside it. A clickable row next to an independently clickable `Switch` gives two actionable nodes and no checked state on the row. Use `selectable(selected, role = Role.RadioButton, onClick)` with `Modifier.selectableGroup()` on the parent for single-choice groups.
- Expose inline links as links. `ClickableText` is deprecated and resolves taps from text offsets, so TalkBack, Switch Access, and keyboard users cannot reach the links. Build the text with `withLink(LinkAnnotation.Url(url)) { append("terms") }`, or `LinkAnnotation.Clickable` for in-app navigation, and pass it to `Text`.
- Give a custom `clickable` the role it represents and a label for its outcome: `Modifier.clickable(onClickLabel = "Open order details", role = Role.Button, onClick = …)`. TalkBack reads the label as the action's description instead of a generic “activate”. Apply the same to `combinedClickable` with `onLongClickLabel`.

### Bad: a clickable row with a duplicate icon label

```kotlin
Row(Modifier.clickable(onClick = onDelete)) {
    Icon(Icons.Default.Delete, contentDescription = "Delete")
    Text("Delete")
}
```

The merged node reads “Delete” twice and exposes no button role.

### Better: one real action

```kotlin
Button(onClick = onDelete) {
    Icon(Icons.Default.Delete, contentDescription = null)
    Text("Delete")
}
```

### Better: a custom row with a role and an action label

```kotlin
Row(
    Modifier
        .fillMaxWidth()
        .clickable(onClickLabel = "Open order details", role = Role.Button, onClick = onOpen)
        .minimumInteractiveComponentSize(),
) {
    Text(title)
}
```

### Better: an accessible inline link

```kotlin
Text(
    buildAnnotatedString {
        append("Messages follow our ")
        withLink(LinkAnnotation.Url("https://example.com/terms")) { append("terms") }
        append(".")
    },
)
```

### Bad: destructive semantics replacement

```kotlin
Modifier.clearAndSetSemantics { contentDescription = "Profile" }
```

This can discard click actions, state, and descendant text.

### Better: preserve native semantics

```kotlin
Modifier.semantics { heading() }
```

Add only the missing property unless replacing the whole node is deliberate and tested.

## Names, voice access, and localization

- Keep visible control text in the accessible name, preferably at the start. A button shown as “Continue” but named only “Submit order” is difficult to activate by saying what is visible in Voice Access.
- Add extra context through surrounding structure, state, or a concise expanded name without replacing the visible words. Verify voice selection with duplicate visible labels.
- Put labels, values, custom-action names, errors, and announcements in Android resources. Use complete format strings, plurals, and locale-aware number/date formatting instead of concatenating fragments.
- Test localization expansion, RTL layout, mixed-direction text, and runtime locale changes. Confirm semantics refresh with the visible UI.
- Mark text in another language so TalkBack can switch pronunciation: in Views, wrap it in a `LocaleSpan`; in Compose, apply `SpanStyle(localeList = LocaleList("fr-FR"))` to that part of an `AnnotatedString`. Verify the voice change with TalkBack on a device.
- Do not gate essential semantics, navigation, or actions on `AccessibilityManager.isTouchExplorationEnabled` or the list of enabled accessibility services. Those signals do not identify every disabled user or input method and can change while the app runs.

## Focus and dynamic updates

Compose focus APIs such as `FocusRequester` control keyboard/input focus. TalkBack maintains separate accessibility focus and usually reacts to native focus, semantics, navigation, and window changes, but the relationship is not guaranteed. Do not repeatedly request input focus during recomposition to force TalkBack behavior.

- Prefer stable node identity and state updates over focus resets.
- Use `liveRegion` for concise, important asynchronous status; debounce rapid updates.
- Avoid `announceForAccessibility` for ordinary state changes. `View.announceForAccessibility` is deprecated as of API level 36 (Android 16); prefer semantics such as `stateDescription`, pane titles, live regions, or window changes, which TalkBack already reports.
- Give dialogs and sheets real platform semantics and restore focus to the initiating control when dismissed.
- Honor the user's **Time to take action** setting for anything that disappears on its own and contains an action, such as an Undo banner. Material3 `SnackbarHost` does this already. For custom UI, pass the default duration through `LocalAccessibilityManager.current?.calculateRecommendedTimeoutMillis(…, containsText = true, containsControls = true)` in Compose, or `AccessibilityManager.getRecommendedTimeoutMillis()` in Views (API 29+), or keep the action until the user dismisses it (WCAG 2.2.1).
- Content that moves or advances on its own for more than five seconds, such as a carousel, needs a visible pause or stop control for everyone (WCAG 2.2.2 Pause, Stop, Hide). Also stop it when animations are removed. Do not rely on detecting TalkBack instead.
- In lazy collections, avoid focus loss caused by unstable keys or replacing the entire item subtree.

### Bad: announce every keystroke

```kotlin
view.announceForAccessibility("${value.length} characters")
```

### Better: expose stable state

```kotlin
Modifier.semantics {
    stateDescription = progressText
}
```

Use a live region only when the update must be announced without focus.

## Touch, text, and layout

- Keep actionable targets at least 48 dp, including custom canvas or icon actions.
- Use `minimumInteractiveComponentSize()` where appropriate, but verify the clickable area rather than only the visual size.
- Store text dimensions in `sp`; never convert `sp` to `dp` as a fixed design value.
- Android 14 introduced nonlinear font scaling up to 200%. Do not assume `scaledDensity` is linear at large scales.
- Avoid fixed-height containers around text. Test 1.0x, 1.3x, 1.5x, and 2.0x font scales plus narrow width and RTL.
- Respect animator duration scale and the app's reduced-motion policy without removing meaningful state changes.
- Android 16 replaces high-contrast text with outline text. Standard text rendering handles this through the framework; UI toolkits and apps that bypass `android.text.Layout` for custom text rendering must observe the corresponding `AccessibilityManager` state/listener and provide an equivalent outlined result. Do not add service detection to ordinary app text that already uses platform rendering.

### Bad: clipped scaled text

```kotlin
Text(text, Modifier.height(40.dp))
```

### Better

```kotlin
Text(text, Modifier.heightIn(min = 40.dp))
```

## Edge-to-edge, insets, and back navigation

These are requirements for apps that target the stated SDK levels:

- Apps targeting SDK 35 run edge-to-edge on Android 15. Apps targeting SDK 36 can no longer opt out on Android 16 devices; `windowOptOutEdgeToEdgeEnforcement` is deprecated and disabled there.
- Apply system bar, display cutout, and IME insets (for example `Modifier.safeDrawingPadding()` or `WindowInsets.safeDrawing`) so focused controls, errors, and snackbars are not hidden under system bars or the keyboard. This supports WCAG 2.4.11 Focus Not Obscured (Minimum).
- Test with three-button and gesture navigation, the IME open, and 200% font scale.
- Apps targeting SDK 36 on Android 16 no longer receive `onBackPressed` or `KEYCODE_BACK`. Handle back through `BackHandler`/`PredictiveBackHandler` in Compose or `OnBackPressedDispatcher` in Views so dialogs, sheets, and custom panes still dismiss for TalkBack, Switch Access, and keyboard users.

## Keyboard focus visibility

- Keep a visible focus indicator for hardware keyboard and Switch Access navigation. `clickable(indication = null)` and custom indications can remove the focused-state highlight.
- Verify Tab and arrow-key order on custom layouts; Compose focus order and TalkBack traversal order are separate.

## Views APIs

- Prefer platform widgets and Material components.
- Use `ViewCompat.setAccessibilityDelegate` only when native widget exposure is insufficient.
- Use `ViewCompat.setAccessibilityHeading`, `ViewCompat.setStateDescription`, `android:labelFor`, and `importantForAccessibility` for their intended relationships.
- Expose gesture-only or nested actions with `ViewCompat.addAccessibilityAction(view, label) { … }`, and give the default click or long-click a meaningful label with `ViewCompat.replaceAccessibilityAction(view, AccessibilityActionCompat.ACTION_CLICK, label, null)`. Give a custom pane, such as an in-app panel, a title with `ViewCompat.setAccessibilityPaneTitle`.
- In `AccessibilityDelegateCompat`, initialize node info without removing actions or metadata supplied by the superclass.
- For custom views with separately meaningful or clickable regions, such as a calendar, implement a virtual view hierarchy with `ExploreByTouchHelper` and attach it with `ViewCompat.setAccessibilityDelegate`. One opaque node for the whole drawing gives services only the container's description.
- Send an `AccessibilityEvent` when a custom view's content changes, and handle `KEYCODE_DPAD_CENTER` and `KEYCODE_ENTER` like a tap.
- Do not set `contentDescription` on editable text to repeat its content; preserve hint, label, value, and editing behavior.

## Charts, custom drawing, media, and maps

- A composable that draws on `Canvas` or uses a custom `Layout` exposes nothing until you add semantics. Give the drawing a `contentDescription` that states its takeaway, and expose each part that carries its own meaning or action as a separate semantics node. Use `collectionInfo` and `collectionItemInfo` when the parts are indexed.
- For charts, provide a text summary of the trend and a way to reach exact values, such as a list or table of the data. Do not distinguish series by color alone, and check that bars, lines, and their boundaries meet 3:1 non-text contrast (WCAG 1.4.11).
- For maps, provide a list of the places shown with the same actions, such as details or directions. Whether individual markers are reachable depends on the map SDK, so verify it with TalkBack instead of assuming it.
- Provide captions for prerecorded video with speech (WCAG 1.2.2) and audio description when important visual information is not in the soundtrack (WCAG 1.2.5). With Media3, `PlayerView` renders subtitle tracks. Call `setUserDefaultStyle()` and `setUserDefaultTextSize()` on its `SubtitleView` so captions follow the system caption preferences.
- Give custom playback controls labels, and keep them reachable with TalkBack, Switch Access, and a keyboard. Audio that plays automatically for more than three seconds needs a control to pause or stop it, or to change its volume independently (WCAG 1.4.2).

### Bad: drawing only

```kotlin
Canvas(Modifier.fillMaxWidth().height(160.dp)) { drawBars(sales) }
```

TalkBack has no node to focus and no data to read.

### Better: summary plus reachable values

```kotlin
Column {
    Canvas(
        Modifier
            .fillMaxWidth()
            .height(160.dp)
            .semantics { contentDescription = summary },
    ) { drawBars(sales) }
    val numbers = NumberFormat.getIntegerInstance()
    sales.forEach { (month, value) -> Text(stringResource(R.string.sales_value, month, numbers.format(value))) }
}
```

`sales_value` is a resource such as `<string name="sales_value">%1$s: %2$s</string>`, so translators can reorder the parts.

## Input, autofill, and sensitive data

- Preserve selection, paste, keyboard, IME actions, and autofill.
- In Compose, use supported `ContentType`/autofill semantics for the dependency version in the project.
- For credentials and authentication codes, allow system autofill and paste unless a documented security requirement prohibits it.
- Password semantics intentionally protect the value; TalkBack may announce bullets, character counts, or privacy-oriented feedback depending on settings and version. Never promise exact speech.
- If digits are visually unmasked, do not mark the field as a password merely to obtain a numeric keyboard. Choose keyboard and visual transformation independently.
- Do not request `READ_SMS` for convenience. Prefer SMS Retriever, SMS User Consent, or user-mediated platform flows when SMS verification is required.
- For secrets and financial or identity data, use `Modifier.semantics { sensitiveData = true }` in Compose, or in Views `android:accessibilityDataSensitive="yes"` or `View.setAccessibilityDataSensitive(View.ACCESSIBILITY_DATA_SENSITIVE_YES)` (API 34+), or `AccessibilityNodeInfoCompat.setAccessibilityDataSensitive(true)` in a delegate, when supported by the project's SDK and dependencies. This limits exposure to services that are not declared accessibility tools; it does not replace masking, redaction, secure logging, screenshot policy, or threat analysis, and it must not hide the value from legitimate assistive technology users.

## WebView and hybrid UI

- Provide an accessible title/context for the WebView and test focus entry and exit.
- Audit DOM semantics separately; native labels do not repair inaccessible web content.
- Verify keyboard, TalkBack, zoom, errors, and authentication transitions across the native/web boundary.
- Keep pinch zoom available. Do not hard-code `textZoom`; check that web text follows the 200% font scale on a device.
- Title the screen in native chrome, such as the top app bar, so TalkBack users know what the web content is before they enter it.

### Bad: disable zoom for a fixed layout

```kotlin
webView.settings.setSupportZoom(false)
```

### Better

```kotlin
webView.settings.apply {
    setSupportZoom(true)
    builtInZoomControls = true
    displayZoomControls = false
}
```

`displayZoomControls = false` hides the legacy on-screen buttons and keeps pinch zoom. A page's `user-scalable=no` viewport can still block zoom, so report it as a web content finding.

## Diagnosis

- Inspect Compose semantics with `printToLog`/`printToString` and compare merged and unmerged trees before changing modifiers.
- For test-layer choice, test APIs, and evidence limits, invoke the `mobile-a11y-testing` skill.

Official sources:

- Compose semantics: https://developer.android.com/develop/ui/compose/accessibility/semantics
- Android accessibility principles: https://developer.android.com/guide/topics/ui/accessibility/principles
- `View.announceForAccessibility` (deprecated in API level 36; checked against the API 36 SDK stubs on 2026-10-25): https://developer.android.com/reference/android/view/View#announceForAccessibility(java.lang.CharSequence)
- `LinkAnnotation` and `withLink`: https://developer.android.com/develop/ui/compose/text/user-interactions
- `AccessibilityManager.getRecommendedTimeoutMillis`: https://developer.android.com/reference/android/view/accessibility/AccessibilityManager#getRecommendedTimeoutMillis(int,%20int)
- WCAG 2.2.1 Timing Adjustable and 2.2.2 Pause, Stop, Hide: https://www.w3.org/TR/WCAG22/#enough-time
- Compose `clickable` with `onClickLabel` and `role`: https://developer.android.com/develop/ui/compose/accessibility/key-steps
- `LocaleSpan`: https://developer.android.com/reference/android/text/style/LocaleSpan
- Font scaling: https://developer.android.com/about/versions/14/features#non-linear-font-scaling
- Edge-to-edge in Compose: https://developer.android.com/develop/ui/compose/system/system-bars
- Android 16 behavior changes (edge-to-edge opt-out, predictive back): https://developer.android.com/about/versions/16/behavior-changes-16
- Android 16 accessibility features (outline text): https://developer.android.com/about/versions/16/features#accessibility
- Sensitive accessibility data: https://developer.android.com/reference/androidx/core/view/accessibility/AccessibilityNodeInfoCompat#setAccessibilityDataSensitive(boolean)
- Android security guidance for `accessibilityDataSensitive`: https://developer.android.com/blog/posts/enhancing-android-security-stop-malware-from-snooping-on-your-app-data
- WebView settings: https://developer.android.com/reference/android/webkit/WebSettings
- Custom views and virtual view hierarchies: https://developer.android.com/guide/topics/ui/accessibility/views/custom-views
- Media3 `SubtitleView`: https://developer.android.com/reference/androidx/media3/ui/SubtitleView
- WCAG 2.2 captions, audio description, audio control, and non-text contrast: https://www.w3.org/TR/WCAG22/
