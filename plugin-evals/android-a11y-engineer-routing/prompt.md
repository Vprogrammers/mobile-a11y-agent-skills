---
max_turns: 8
timeout_seconds: 180
allowed_tools: [Agent, Read, Glob, Grep, Skill]
---

TalkBack users cannot activate this Compose row. Fix it with the smallest change and show the corrected code.

```kotlin
@Composable
fun AlertsRow(enabled: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.pointerInput(Unit) { detectTapGestures { onChange(!enabled) } }) {
        Text("Price alerts")
        Text(if (enabled) "On" else "Off")
    }
}
```
