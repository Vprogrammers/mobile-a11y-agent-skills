package dev.vprogrammers.a11y.kmp

import android.content.Context
import android.database.ContentObserver
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.error
import androidx.compose.ui.semantics.semantics
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/** Android adapter: "Remove animations" sets the animator duration scale to 0. */
class AndroidAccessibilityPreferences(context: Context) : AccessibilityPreferences, AutoCloseable {
    private val resolver = context.contentResolver
    private val state = MutableStateFlow(read())
    override val reduceMotion: StateFlow<Boolean> = state.asStateFlow()

    private val observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
        override fun onChange(selfChange: Boolean) {
            state.value = read()
        }
    }

    init {
        resolver.registerContentObserver(
            Settings.Global.getUriFor(Settings.Global.ANIMATOR_DURATION_SCALE),
            false,
            observer,
        )
    }

    override fun close() = resolver.unregisterContentObserver(observer)

    private fun read(): Boolean =
        Settings.Global.getFloat(resolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f
}

/**
 * Native mapping of the shared contract: the field exposes its error through Compose semantics.
 * [resolve] turns the shared message key into localized text, for example with `stringResource`.
 */
fun Modifier.validationSemantics(state: ValidationState, resolve: (String) -> String): Modifier {
    val key = state.messageKey ?: return this
    return semantics { error(resolve(key)) }
}
