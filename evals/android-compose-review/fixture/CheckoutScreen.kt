package evals.fixture.checkout

import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp

// Eval fixture: intentionally inaccessible. Do not copy into production code.

data class CartLine(val id: String, val title: String, val price: String)

@Composable
fun CheckoutScreen(
    lines: List<CartLine>,
    cardNumber: String,
    onCardNumberChange: (String) -> Unit,
    onRemove: (CartLine) -> Unit,
    onClose: () -> Unit,
    onPay: () -> Unit,
    showConfirm: Boolean,
    onConfirm: () -> Unit,
) {
    Box(Modifier.fillMaxSize()) {
        Column {
            // DEFECT close-icon-unlabeled: icon-only clickable with no name or role.
            Icon(
                Icons.Default.Close,
                contentDescription = null,
                modifier = Modifier.size(24.dp).clickable(onClick = onClose),
            )

            // DEFECT cart-duplicate-description: icon repeats the adjacent visible text.
            Row {
                Icon(Icons.Default.ShoppingCart, contentDescription = "Your cart")
                Text("Your cart")
            }

            LazyColumn {
                // DEFECT unstable-keys: index keys move focus to a different item after removal.
                itemsIndexed(lines, key = { index, _ -> index }) { _, line ->
                    CartLineRow(line, onRemove)
                }
            }

            OutlinedTextField(
                value = cardNumber,
                onValueChange = {
                    // DEFECT card-number-logged: sensitive payment data is written to logs.
                    Log.d("Checkout", "card=$it")
                    onCardNumberChange(it)
                },
                // DEFECT card-field-no-label: placeholder only, no persistent label.
                placeholder = { Text("1234 5678 9012 3456") },
            )

            Button(onClick = onPay) { Text("Pay") }
        }

        if (showConfirm) {
            ConfirmOverlay(onConfirm)
        }
    }
}

@Composable
private fun CartLineRow(line: CartLine, onRemove: (CartLine) -> Unit) {
    Row(
        // DEFECT swipe-only-remove: removal exists only as a horizontal drag gesture.
        Modifier.pointerInput(line.id) {
            detectHorizontalDragGestures { _, dragAmount -> if (dragAmount < -40f) onRemove(line) }
        },
    ) {
        // DEFECT fixed-height-text: text is clipped at large font scales.
        Text(line.title, Modifier.height(20.dp))
        Text(line.price)
    }
}

@Composable
private fun ConfirmOverlay(onConfirm: () -> Unit) {
    // DEFECT overlay-not-modal: custom overlay has no dialog/pane semantics, so content behind stays reachable.
    Box(
        Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)),
        contentAlignment = Alignment.Center,
    ) {
        Button(onClick = onConfirm) { Text("Confirm payment") }
    }
}
