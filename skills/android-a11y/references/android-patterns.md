# Android accessibility patterns

## Compose semantics

- Prefer `Button`, `TextField`, `Checkbox`, and other standard composables.
- Use `contentDescription = null` for decorative images.
- Use `mergeDescendants` only when the merged result remains understandable and actionable.
- Expose standard roles and states instead of restating them in labels.
- Use `stateDescription` only when the standard state is insufficient.
- Mark true section headings with `heading()`.

## Input

- Keep a real input control behind visually separated cells or decorations.
- Set the appropriate keyboard type and autofill content type.
- Do not use password keyboard behavior for visible digits because it can suppress useful feedback.
- Keep masked accessibility output free of the entered secret.

## Focus and announcements

- Use input focus for keyboard presentation.
- Do not repeatedly force focus during recomposition.
- Prefer state updates and live regions over `announceForAccessibility`; use explicit announcements sparingly.
- Ensure the TalkBack focus bounds match the visible control and have space for the focus indicator.

## Testing

- Use unit tests for shared transformations and descriptions.
- Use Compose semantics assertions in host tests only when the configured environment supports them.
- Use Android device tests for framework autofill, focus, IME, and TalkBack-adjacent behavior.
- Perform final TalkBack and Voice Access checks manually on supported devices.
