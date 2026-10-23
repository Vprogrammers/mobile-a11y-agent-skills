@Composable
fun AccessibleSettings(
    notificationsEnabled: Boolean,
    onNotificationsChanged: (Boolean) -> Unit,
) {
    Column(Modifier.verticalScroll(rememberScrollState())) {
        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineLarge,
            modifier = Modifier.semantics { heading() },
        )
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .toggleable(
                    value = notificationsEnabled,
                    role = Role.Switch,
                    onValueChange = onNotificationsChanged,
                )
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("Notifications", Modifier.weight(1f))
            Switch(
                checked = notificationsEnabled,
                onCheckedChange = null,
            )
        }
    }
}
