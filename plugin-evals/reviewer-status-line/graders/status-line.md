---
type: regex
target: trace
pattern: 'Status: (completed|blocked|needs-device-verification)'
arm: with-only
---

The reviewer's report starts with one of the completion statuses that `mobile-a11y-workflow` defines.
