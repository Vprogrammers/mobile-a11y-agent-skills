package dev.vprogrammers.a11y.samples

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.minimumInteractiveComponentSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.autofill.ContentType
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.contentType
import androidx.compose.ui.semantics.error
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.hideFromAccessibility
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.intl.LocaleList
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import java.text.NumberFormat

// Compiled counterparts of the "Better" examples in android-patterns.md.

/** One real action: the icon is decorative because the visible text already names it. */
@Composable
fun DeleteButton(onDelete: () -> Unit) {
    Button(onClick = onDelete) {
        Icon(Icons.Default.Delete, contentDescription = null)
        Text("Delete")
    }
}

/** Add only the missing property instead of replacing descendant semantics. */
@Composable
fun SectionHeading(title: String) {
    Text(title, Modifier.semantics { heading() })
}

/** Expose state through semantics instead of announcing every change. */
@Composable
fun UploadProgress(progressText: String) {
    Text(progressText, Modifier.semantics { stateDescription = progressText })
}

/** Reserve live regions for concise, important asynchronous status. */
@Composable
fun SyncStatus(message: String) {
    Text(message, Modifier.semantics { liveRegion = LiveRegionMode.Polite })
}

/** Grow with font scale instead of clipping at a fixed height. */
@Composable
fun ScalableLabel(text: String) {
    Text(text, Modifier.heightIn(min = 40.dp))
}

/** Decorative icon next to text that already conveys the meaning. */
@Composable
fun FeaturedLabel(text: String) {
    Column {
        Icon(Icons.Default.Star, contentDescription = null, modifier = Modifier.semantics { hideFromAccessibility() })
        Text(text)
    }
}

/** Associate the error with its field and keep autofill available. */
@Composable
fun PasswordField(
    value: String,
    onValueChange: (String) -> Unit,
    errorMessage: String?,
) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text("Password") },
        isError = errorMessage != null,
        supportingText = errorMessage?.let { { Text(it) } },
        visualTransformation = PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
        modifier = Modifier.semantics {
            contentType = ContentType.Password
            if (errorMessage != null) error(errorMessage)
        },
    )
}

/** Visible one-time code: numeric keyboard without password semantics, autofill allowed. */
@Composable
fun OneTimeCodeField(value: String, onValueChange: (String) -> Unit) {
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        label = { Text("Verification code") },
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
        modifier = Modifier.semantics { contentType = ContentType.SmsOtpCode },
    )
}

/** Keep content out from under system bars and the IME once edge-to-edge is enforced. */
@Composable
fun EdgeToEdgeContent(content: @Composable () -> Unit) {
    Column(Modifier.safeDrawingPadding()) { content() }
}

/** A drawn chart with a summary and the exact values reachable as text. */
@Composable
fun SalesChart(sales: List<Pair<String, Int>>, summary: String) {
    Column {
        Canvas(
            Modifier
                .fillMaxWidth()
                .height(160.dp)
                .semantics { contentDescription = summary },
        ) { drawBars(sales) }
        val numbers = NumberFormat.getIntegerInstance()
        sales.forEach { (month, value) -> Text(stringResource(R.string.sales_value, month, numbers.format(value))) }
    }
}

private fun DrawScope.drawBars(sales: List<Pair<String, Int>>) {
    if (sales.isEmpty()) return
    val barWidth = size.width / (sales.size * 2)
    val max = sales.maxOf { it.second }.coerceAtLeast(1)
    sales.forEachIndexed { index, (_, value) ->
        val height = size.height * value / max
        drawRect(Color.Gray, topLeft = Offset(index * 2 * barWidth, size.height - height), size = Size(barWidth, height))
    }
}

/** A custom clickable row names the action's outcome and the role it represents. */
@Composable
fun OrderRow(title: String, onOpen: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .clickable(onClickLabel = "Open order details", role = Role.Button, onClick = onOpen)
            .minimumInteractiveComponentSize(),
    ) {
        Text(title)
    }
}

/** A phrase in another language carries its locale so TalkBack can switch pronunciation. */
@Composable
fun QuotedPhrase(intro: String, phrase: String, languageTag: String) {
    Text(
        buildAnnotatedString {
            append(intro)
            withStyle(SpanStyle(localeList = LocaleList(languageTag))) { append(phrase) }
        },
    )
}
