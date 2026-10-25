---
type: regex
target: trace
pattern: 'mobile-a11y-agent-skills:(kmp-a11y-architect|kmp-a11y)\b'
arm: with-only
---

The session uses the plugin's `kmp-a11y-architect` agent or its `kmp-a11y` skill. For a short, self-contained request Claude Code usually loads the skill in the main session instead of delegating, and both count.
