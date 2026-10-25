@Composable
fun ReaderSettings(
    textSizeLabel: String,
    onSmaller: () -> Unit,
    onLarger: () -> Unit,
    showTips: Boolean,
    onDismissTips: () -> Unit,
) {
    val captionSize = with(LocalDensity.current) { 12.dp.toSp() }

    Column(Modifier.fillMaxWidth().padding(16.dp)) {
        Text(
            "Reading settings",
            Modifier.semantics { heading() },
            style = MaterialTheme.typography.titleLarge,
        )
        Row(verticalAlignment = Alignment.CenterVertically) {
            TextButton(onClick = onSmaller, modifier = Modifier.focusProperties { canFocus = false }) {
                Text("Smaller")
            }
            Text(textSizeLabel, Modifier.weight(1f), textAlign = TextAlign.Center)
            TextButton(onClick = onLarger, modifier = Modifier.focusProperties { canFocus = false }) {
                Text("Larger")
            }
        }
        Text("Changes apply to every book in your library.", fontSize = captionSize)
    }

    if (showTips) {
        Dialog(
            onDismissRequest = onDismissTips,
            properties = DialogProperties(dismissOnBackPress = false, dismissOnClickOutside = false),
        ) {
            Surface(
                Modifier.pointerInput(Unit) {
                    detectVerticalDragGestures { _, dragAmount -> if (dragAmount > 40f) onDismissTips() }
                },
                shape = MaterialTheme.shapes.large,
            ) {
                Text("Tip: pinch to zoom pages. Swipe down to close.", Modifier.padding(24.dp))
            }
        }
    }
}
