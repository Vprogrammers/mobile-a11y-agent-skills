---
max_turns: 8
timeout_seconds: 180
allowed_tools: [Agent, Read, Glob, Grep, Skill]
---

Use the mobile-a11y-agent-skills:accessibility-reviewer agent to review this SwiftUI snippet for accessibility issues, and show me its report.

```swift
struct DownloadRow: View {
    let title: String
    let onCancel: () -> Void

    var body: some View {
        HStack {
            Text(title)
            Image(systemName: "xmark.circle")
                .onTapGesture(perform: onCancel)
        }
    }
}
```
