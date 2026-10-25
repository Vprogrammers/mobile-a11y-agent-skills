import androidx.compose.ui.semantics.error

@Composable
fun OrderCard(order: Order, onOpen: () -> Unit, onTrack: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f).clickable(onClick = onOpen)) {
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
    OutlinedTextField(
        value = street,
        onValueChange = onStreetChange,
        label = { Text("Street") },
        isError = errors.isNotEmpty(),
        supportingText = { errors.forEach { Text(it) } },
        modifier = Modifier.semantics { if (errors.isNotEmpty()) error(errors.joinToString()) },
    )
}
