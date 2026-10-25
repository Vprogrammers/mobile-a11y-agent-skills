---
type: regex
target: trace
pattern: 'mobile-a11y-agent-skills:(accessibility-reviewer|mobile-a11y-review)\b'
arm: with-only
---

The session uses the plugin's `accessibility-reviewer` agent or its `mobile-a11y-review` skill. For a short, self-contained request Claude Code usually loads the skill in the main session instead of delegating, and both count.
