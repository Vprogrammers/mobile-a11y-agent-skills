---
type: regex
target: trace
pattern: 'mobile-a11y-agent-skills:(android-a11y-engineer|android-a11y)\b'
arm: with-only
---

The session uses the plugin's `android-a11y-engineer` agent or its `android-a11y` skill. For a short, self-contained request Claude Code usually loads the skill in the main session instead of delegating, and both count.
