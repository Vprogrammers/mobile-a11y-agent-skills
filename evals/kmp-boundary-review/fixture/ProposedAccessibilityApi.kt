// Eval fixture: a proposed commonMain API under review. Intentionally not compiled,
// because it references platform types that commonMain cannot see.
package com.example.shared.a11y

import androidx.compose.ui.semantics.SemanticsPropertyReceiver
import com.google.android.gms.auth.api.phone.SmsRetriever
import kotlinx.coroutines.flow.Flow
import platform.UIKit.UIAccessibilityTraits

// DEFECT compose-type-in-common: Compose semantics receiver leaks into shared code.
// DEFECT uikit-type-in-common: UIKit traits leak into shared code.
interface AccessibleField {
    fun applySemantics(receiver: SemanticsPropertyReceiver)
    val iosTraits: UIAccessibilityTraits

    // DEFECT shared-speech-string: common code decides exact screen-reader speech.
    fun spokenDescription(): String
}

// DEFECT raw-flow-export: Flow and a sealed hierarchy exported to Swift without an interop decision.
sealed class FieldError {
    data class Invalid(val reason: String) : FieldError()
    data object Missing : FieldError()
}

interface FieldValidator {
    val errors: Flow<FieldError?>
}

// DEFECT play-services-in-core: optional Play Services dependency in the core artifact.
class OtpAutofill {
    fun start() = SmsRetriever::class
}

// DEFECT expect-actual-hides-ownership: expect/actual used to smuggle native UI handles.
expect class PlatformFocusHandle {
    fun requestScreenReaderFocus()
}
