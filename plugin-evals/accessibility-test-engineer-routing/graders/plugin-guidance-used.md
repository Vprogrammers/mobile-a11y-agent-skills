---
type: regex
target: trace
pattern: 'mobile-a11y-agent-skills:(accessibility-test-engineer|mobile-a11y-testing)\b'
arm: with-only
---

The session uses the plugin's `accessibility-test-engineer` agent or its `mobile-a11y-testing` skill. For a short, self-contained request Claude Code usually loads the skill in the main session instead of delegating, and both count.
