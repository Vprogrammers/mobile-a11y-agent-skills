data class Message(val id: Long, val body: String)

@Composable
fun MessageThread(
    messages: List<Message>,
    readReceipts: Boolean,
    onReadReceiptsChange: (Boolean) -> Unit,
    onDelete: (Message) -> Unit,
    onUndoDelete: (Message) -> Unit,
    onOpenUrl: (String) -> Unit,
) {
    var deleted by remember { mutableStateOf<Message?>(null) }

    Column(Modifier.fillMaxSize().padding(16.dp)) {
        Row(
            Modifier
                .fillMaxWidth()
                .clickable { onReadReceiptsChange(!readReceipts) }
                .padding(vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("Send read receipts", Modifier.weight(1f))
            Switch(checked = readReceipts, onCheckedChange = onReadReceiptsChange)
        }

        val policy = buildAnnotatedString {
            append("Messages follow our ")
            pushStringAnnotation(tag = "url", annotation = "https://example.com/terms")
            withStyle(SpanStyle(color = Color.Blue)) { append("terms") }
            pop()
            append(" and ")
            pushStringAnnotation(tag = "url", annotation = "https://example.com/privacy")
            withStyle(SpanStyle(color = Color.Blue)) { append("privacy policy") }
            pop()
            append(".")
        }
        ClickableText(policy) { offset ->
            policy.getStringAnnotations(tag = "url", start = offset, end = offset)
                .firstOrNull()
                ?.let { onOpenUrl(it.item) }
        }

        LazyColumn(Modifier.weight(1f)) {
            items(messages, key = { it.id }) { message ->
                Row(
                    Modifier.fillMaxWidth().padding(vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(message.body, Modifier.weight(1f))
                    TextButton(onClick = {
                        onDelete(message)
                        deleted = message
                    }) { Text("Delete") }
                }
            }
        }

        deleted?.let { message ->
            LaunchedEffect(message.id) {
                delay(3_000)
                deleted = null
            }
            Row(
                Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.inverseSurface)
                    .padding(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    "Message deleted",
                    Modifier.weight(1f),
                    color = MaterialTheme.colorScheme.inverseOnSurface,
                )
                TextButton(onClick = {
                    onUndoDelete(message)
                    deleted = null
                }) { Text("Undo") }
            }
        }
    }
}
