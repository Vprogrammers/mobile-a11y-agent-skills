# KMP accessibility boundaries

## Share

- immutable state and transitions;
- normalization and validation;
- progress and error models;
- masking policy;
- contrast calculations using primitive color values;
- localizable text inputs or callbacks;
- platform-neutral layout decisions when both platforms truly share them.

## Keep native

- Compose `Modifier.semantics`;
- Android `AccessibilityNodeInfo`, autofill, IME, and focus APIs;
- SwiftUI accessibility modifiers;
- UIKit `UIAccessibility`, traits, focus, and notifications;
- platform colors, fonts, views, and haptics;
- real-device assistive-technology verification.

## Swift interop

- Prefer clear classes, enums, primitives, and callbacks.
- Avoid exposing generic-heavy or Compose-specific APIs.
- Treat default arguments, sealed hierarchies, suspend functions, and Kotlin collections as interop decisions.
- Keep strong ownership of Kotlin objects that own native iOS views.
- Verify framework export and consumer usage in a sample app.

## Dependencies

Keep Play Services, Android-only services, or optional integrations out of the core artifact unless every consumer needs them.
