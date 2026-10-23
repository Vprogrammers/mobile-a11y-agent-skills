# Mobile accessibility review checklist

## Semantics

- Prefer one logical element for one logical control.
- Hide decorative children from assistive technology.
- Expose role, label, value, state, and available actions without repetition.
- Use hints only when the result of an action is not already clear.
- Keep dynamic values concise and localizable.

## Navigation and input

- Follow a logical focus order independent of visual animation.
- Preserve keyboard, Switch Control, Voice Control, and external-input access.
- Keep touch targets at least 48 dp on Android and 44 pt on Apple platforms.
- Avoid custom gestures as the only way to perform an action.

## Visual access

- Support font scaling and Dynamic Type without clipping or loss of actions.
- Do not communicate state only through color.
- Check 4.5:1 text contrast and 3:1 meaningful graphics or focus indicators where applicable.
- Respect reduced motion, increased contrast, and reduced transparency.

## State changes

- Announce important asynchronous results and errors without flooding speech.
- Avoid moving accessibility focus unless context genuinely changes.
- Clear stale errors when the user corrects input.
- Preserve focus through recomposition, updates, and navigation.

## Sensitive input

- Keep visible and accessibility masking aligned.
- Do not log, persist, analytics-track, or announce secrets unexpectedly.
- Prefer platform autofill APIs over reading messages or clipboard data.
- Treat OTP, password, payment, identity, and health fields as sensitive.

## Evidence

Distinguish static findings, automated test evidence, simulator results, and real-device observations.
