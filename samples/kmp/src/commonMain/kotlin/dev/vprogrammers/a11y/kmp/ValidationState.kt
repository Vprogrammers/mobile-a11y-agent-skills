package dev.vprogrammers.a11y.kmp

/**
 * Platform-neutral validation result. Android maps it to Compose `error()` semantics; iOS maps it
 * to native label, value, or error presentation. Common code never decides screen-reader speech.
 */
data class ValidationState(
    val messageKey: String?,
    val isBlocking: Boolean,
) {
    companion object {
        val Valid = ValidationState(messageKey = null, isBlocking = false)
    }
}

/** Shared product rule; each platform resolves [ValidationState.messageKey] to localized text. */
fun validateEmail(input: String): ValidationState {
    val value = input.trim()
    return when {
        value.isEmpty() -> ValidationState("error_email_required", isBlocking = true)
        !EMAIL.matches(value) -> ValidationState("error_email_format", isBlocking = true)
        else -> ValidationState.Valid
    }
}

private val EMAIL = Regex("""[^@\s]+@[^@\s]+\.[^@\s]+""")
