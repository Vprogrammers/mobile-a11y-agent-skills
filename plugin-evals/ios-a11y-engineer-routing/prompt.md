---
max_turns: 8
timeout_seconds: 180
allowed_tools: [Agent, Read, Glob, Grep, Skill]
---

VoiceOver reads this SwiftUI row as two separate elements and the delete action is hard to find. Fix it with the smallest change and show the corrected code.

```swift
struct ContactRow: View {
    let name: String
    let onDelete: () -> Void

    var body: some View {
        HStack {
            Image(systemName: "person.circle")
            Text(name)
        }
        .onLongPressGesture { onDelete() }
    }
}
```
