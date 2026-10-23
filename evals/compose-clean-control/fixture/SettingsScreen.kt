package evals.fixture.settings

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material3.Button
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

// Eval fixture: negative control. No seeded defects; reviewers should not report blockers.

@Composable
fun SettingsScreen(
    notificationsOn: Boolean,
    onNotificationsChange: (Boolean) -> Unit,
    onSignOut: () -> Unit,
) {
    Column {
        Text("Settings", Modifier.semantics { heading() })

        Row(
            Modifier
                .heightIn(min = 48.dp)
                .toggleable(
                    value = notificationsOn,
                    role = Role.Switch,
                    onValueChange = onNotificationsChange,
                ),
        ) {
            Text("Notifications")
            Switch(checked = notificationsOn, onCheckedChange = null)
        }

        Button(onClick = onSignOut) { Text("Sign out") }
    }
}
