---
max_turns: 8
timeout_seconds: 180
allowed_tools: [Agent, Read, Glob, Grep, Skill]
---

Use @agent-mobile-a11y-agent-skills:accessibility-reviewer to review this SwiftUI snippet. Report only evidence-backed findings, distinguish code evidence from VoiceOver device verification, and do not claim legal compliance.

```swift
struct StatusRow: View {
    let title: String

    var body: some View {
        HStack {
            Text(title)
            Image(systemName: "checkmark.circle.fill")
        }
    }
}
```
