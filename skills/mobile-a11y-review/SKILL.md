---
name: mobile-a11y-review
description: Review native Android, iOS, or Kotlin Multiplatform UI changes for accessibility barriers, sensitive-data exposure, semantics, focus, scaling, contrast, motion, input, and testing gaps. Use before pull requests, releases, or after accessibility regressions.
---

# Review mobile accessibility

1. Identify platforms, UI frameworks, critical flows, sensitive data, and supported OS versions.
2. Inspect standard-control usage before custom semantics.
3. Trace the accessibility tree, focus order, state changes, error handling, and alternative input.
4. Check text scaling, reflow, contrast, non-color cues, target sizes, motion, and transparency.
5. Inspect autofill, keyboard, paste, masking, logging, and announcements for sensitive fields.
6. Compare Android and iOS product requirements without requiring identical APIs.
7. Inspect automated coverage and list real-device checks separately.
8. Report P0, P1, P2, and Note findings with minimal fixes.

Read [references/review-checklist.md](references/review-checklist.md) for detailed evidence prompts.

Do not claim legal compliance or exact screen-reader speech from code review alone.
