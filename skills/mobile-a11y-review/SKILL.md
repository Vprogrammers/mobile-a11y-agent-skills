---
name: mobile-a11y-review
description: Review native Android, iOS, or Kotlin Multiplatform UI for accessibility barriers and testing gaps. Use for pull requests, releases, regressions, WCAG 2.2 or EN 301 549 mapping, TalkBack or VoiceOver failures, semantics, focus, scaling, contrast, motion, navigation, media, input, WebView, or sensitive-data changes.
---

# Review mobile accessibility

1. Establish the changed scope, supported platforms, UI frameworks, critical flows, sensitive data, and OS versions.
2. Identify affected users and assistive technologies before judging implementation details.
3. Inspect standard-control usage, accessibility tree, focus order, labels, values, states, actions, errors, and alternatives to gestures.
4. Check scaling, reflow, contrast, non-color cues, target size, orientation, motion, audio, media, keyboard, switch, and voice input.
5. Check navigation, sheets, dialogs, lists, sliders, charts, custom drawing, WebView boundaries, and asynchronous updates.
6. Inspect privacy, autofill, clipboard, masking, logging, analytics, and announcements for sensitive data.
7. Map findings to standards only when useful and never infer legal applicability from WCAG alone.
8. Separate static evidence, automated checks, simulator observations, and real-device results.

Use these severities:

- **P0**: blocks a critical flow, exposes sensitive data, or makes functionality unavailable without a reasonable alternative.
- **P1**: creates a substantial barrier for an affected user group.
- **P2**: degrades usability, consistency, resilience, or maintainability.
- **Note**: optional improvement without a demonstrated barrier.

For each finding report: severity, file/location, affected users and technology, evidence, relevant criterion when appropriate, smallest viable fix, and verification method. End with blockers, device checks, and residual risk.

Read [references/review-checklist.md](references/review-checklist.md). Read [references/regulatory-landscape.md](references/regulatory-landscape.md) before making standards or legal claims.
