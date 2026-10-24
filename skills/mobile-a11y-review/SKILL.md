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
- **P3**: optional improvement without a demonstrated barrier.

Calibrate by the effect on the affected user, not by how likely the code path is:

- P1 when information or functionality is lost for a user group at a supported setting. Examples: text clipped or controls unreachable at large text sizes; a cap below the supported accessibility text sizes; meaning conveyed only by color; an action available only through a gesture; grouping that removes independently operable actions; focus that escapes a modal or is repeatedly moved away from the user.
- P2 when the user can still complete the task with extra effort or confusion. Examples: redundant announcements, focus-continuity risk on list updates, a missing heading, an inconsistent label.
- A defect proven by code keeps its severity even when exact assistive-technology behavior still needs device confirmation. Put the device check in **Verify**; do not lower the severity to mark uncertainty.

Report each finding in this format:

```text
<severity> — <file>:<line or symbol>
Affected users: <users and assistive technologies>
Evidence: <what the code proves; mark assumptions>
Criterion: <WCAG/EN 301 549 reference, only when useful>
Fix: <smallest viable change>
Verify: <automated layer, then device check>
```

End with three sections: **Blockers** (P0/P1, or “No blocking finding found”), **Device checks** (assistive technology, settings, and flow), and **Residual risk**.

Read [references/review-checklist.md](references/review-checklist.md). Read [references/regulatory-landscape.md](references/regulatory-landscape.md) before making standards or legal claims.
