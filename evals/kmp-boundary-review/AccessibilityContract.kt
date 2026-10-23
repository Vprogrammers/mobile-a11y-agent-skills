package example.accessibility

import androidx.compose.ui.semantics.SemanticsPropertyReceiver
import kotlinx.cinterop.BetaInteropApi
import kotlinx.coroutines.flow.Flow
import platform.UIKit.UIAccessibilityTraits

public sealed interface SharedAccessibilityError {
    public data class InvalidInput(val reason: String) : SharedAccessibilityError
}

public interface SharedAccessibilityContract {
    public val events: Flow<SharedAccessibilityError>
    public val iosTraits: UIAccessibilityTraits
    public fun applyComposeSemantics(receiver: SemanticsPropertyReceiver)
    public fun enableSmsRetriever()
}
