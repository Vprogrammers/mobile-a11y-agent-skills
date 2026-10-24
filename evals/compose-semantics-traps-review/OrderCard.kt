@Composable
fun OrderCard(order: Order, onOpen: () -> Unit, onTrack: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .clickable(
                interactionSource = remember { MutableInteractionSource() },
                indication = null,
                onClick = onOpen,
            )
            .clearAndSetSemantics { contentDescription = "Order ${order.number}, ${order.status}" }
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Text("Order ${order.number}", style = MaterialTheme.typography.titleMedium)
            Text(order.status)
        }
        TextButton(onClick = onTrack) {
            Icon(Icons.Default.LocationOn, contentDescription = null)
            Text("Track")
        }
    }
}

@Composable
fun AddressForm(errors: List<String>, street: String, onStreetChange: (String) -> Unit) {
    val focusRequester = remember { FocusRequester() }
    LaunchedEffect(errors) {
        if (errors.isNotEmpty()) focusRequester.requestFocus()
    }
    Column {
        OutlinedTextField(
            value = street,
            onValueChange = onStreetChange,
            label = { Text("Street") },
            modifier = Modifier.focusRequester(focusRequester),
        )
        errors.forEach { Text(it, color = MaterialTheme.colorScheme.error) }
    }
}
