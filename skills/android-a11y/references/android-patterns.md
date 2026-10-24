# Android accessibility patterns

Last reviewed: 2026-10-24. Verify exact signatures against the Android and Compose versions used by the project.
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

### Bad: duplicate image and label nodes

```kotlin
Row {
    Icon(Icons.Default.Delete, contentDescription = "Delete")
    Text("Delete")
}
```

### Better: one real action

```kotlin
Button(onClick = onDelete) {
    Icon(Icons.Default.Delete, contentDescription = null)
    Text("Delete")
}
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

## Focus and dynamic updates

Compose focus APIs such as `FocusRequester` control keyboard/input focus. TalkBack maintains separate accessibility focus and usually reacts to native focus, semantics, navigation, and window changes, but the relationship is not guaranteed. Do not repeatedly request input focus during recomposition to force TalkBack behavior.

- Prefer stable node identity and state updates over focus resets.
- Use `liveRegion` for concise, important asynchronous status; debounce rapid updates.
- Avoid `announceForAccessibility` for ordinary state changes. It is deprecated on newer Android versions; prefer semantics, window/state events, or framework behavior appropriate to the change.
- Give dialogs and sheets real platform semantics and restore focus to the initiating control when dismissed.
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
- In `AccessibilityDelegateCompat`, initialize node info without removing actions or metadata supplied by the superclass.
- For custom views, expose virtual descendants through the appropriate compatibility helper rather than one opaque canvas node.
- Do not set `contentDescription` on editable text to repeat its content; preserve hint, label, value, and editing behavior.

## Input, autofill, and sensitive data

- Preserve selection, paste, keyboard, IME actions, and autofill.
- In Compose, use supported `ContentType`/autofill semantics for the dependency version in the project.
- For credentials and authentication codes, allow system autofill and paste unless a documented security requirement prohibits it.
- Password semantics intentionally protect the value; TalkBack may announce bullets, character counts, or privacy-oriented feedback depending on settings and version. Never promise exact speech.
- If digits are visually unmasked, do not mark the field as a password merely to obtain a numeric keyboard. Choose keyboard and visual transformation independently.
- Do not request `READ_SMS` for convenience. Prefer SMS Retriever, SMS User Consent, or user-mediated platform flows when SMS verification is required.

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
- Font scaling: https://developer.android.com/about/versions/14/features#non-linear-font-scaling
- Edge-to-edge in Compose: https://developer.android.com/develop/ui/compose/system/system-bars
- Android 16 behavior changes (edge-to-edge opt-out, predictive back): https://developer.android.com/about/versions/16/behavior-changes-16
- WebView settings: https://developer.android.com/reference/android/webkit/WebSettings
