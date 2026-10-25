---
type: regex
target: trace
pattern: 'mobile-a11y-agent-skills:(ios-a11y-engineer|ios-a11y)\b'
arm: with-only
---

The session uses the plugin's `ios-a11y-engineer` agent or its `ios-a11y` skill. For a short, self-contained request Claude Code usually loads the skill in the main session instead of delegating, and both count.
