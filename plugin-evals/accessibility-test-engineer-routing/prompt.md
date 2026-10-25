---
max_turns: 8
timeout_seconds: 180
allowed_tools: [Agent, Read, Glob, Grep, Skill]
---

Plan and write an automated accessibility test for this Compose error state. The field must expose its error to accessibility services. Show the test code and say what it cannot prove.

```kotlin
@Composable
fun EmailField(value: String, error: String?, onValueChange: (String) -> Unit) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text("Email") },
        isError = error != null,
        supportingText = { if (error != null) Text(error) },
    )
}
```
