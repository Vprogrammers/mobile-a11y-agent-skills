@Composable
fun CheckoutScreen(items: List<Item>, onDelete: (Item) -> Unit) {
    var showHelp by remember { mutableStateOf(false) }

    Column {
        Text("Checkout", Modifier.height(32.dp))
        LazyColumn {
            items(items) { item ->
                Row {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Delete ${item.name}",
                        modifier = Modifier.clickable { onDelete(item) },
                    )
                    Text("Delete ${item.name}")
                }
            }
        }
        Text("Swipe left for help", Modifier.pointerInput(Unit) {
            detectHorizontalDragGestures { _, amount ->
                if (amount < 0) showHelp = true
            }
        })
    }

    if (showHelp) {
        Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f))) {
            Text("Help", Modifier.align(Alignment.Center))
        }
    }
}
