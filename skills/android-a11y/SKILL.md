---
name: android-a11y
description: Implement or review Android accessibility in Jetpack Compose or Views. Use for TalkBack or Voice Access problems, contentDescription, semantics, traversal, focus, headings, stateDescription, custom actions, live regions, font scaling, touch targets, autofill, errors, motion, contrast, WebView, accessibility testing, or “TalkBack does not read this”.
---

# Implement Android accessibility

1. Inspect the rendered semantics/accessibility tree before adding labels or announcements.
2. Prefer native controls and preserve built-in role, state, action, focus, keyboard, selection, and autofill behavior.
3. Model each logical control as one usable node; merge or clear semantics only with a verified result.
4. Expose state and errors through semantics; reserve live regions and announcements for important asynchronous changes.
5. Treat input focus and TalkBack accessibility focus as different systems. Do not claim Compose can directly request TalkBack focus through a stable public API.
6. Support large font, RTL, dark theme, reduced/remove animations, keyboard with visible focus, Switch Access, Voice Access, and 48 dp touch targets.
7. Apply system bar, cutout, and IME insets for edge-to-edge, and handle back through the predictive back APIs so panes stay dismissible.
8. Test custom controls, lists, dialogs, sheets, sliders, charts, WebViews, and navigation boundaries on representative API levels.
9. Use host tests only when their environment supports the required UI behavior; use device tests for framework integration.
10. Verify TalkBack and Voice Access on a real device before claiming actual announcements or navigation behavior.

Read [references/android-patterns.md](references/android-patterns.md) for APIs, traps, and bad-to-good examples.
