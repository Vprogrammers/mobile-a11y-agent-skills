package dev.vprogrammers.a11y.kmp

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlinx.coroutines.flow.MutableStateFlow

private class FakeAccessibilityPreferences(reduceMotion: Boolean) : AccessibilityPreferences {
    override val reduceMotion = MutableStateFlow(reduceMotion)
}

// Common tests prove shared decisions only. Platform mapping and assistive-technology behavior are tested natively.
class SharedContractTest {
    @Test
    fun emptyEmail_isBlockingWithMessageKey() {
        assertEquals(ValidationState("error_email_required", isBlocking = true), validateEmail("  "))
    }

    @Test
    fun malformedEmail_isBlockingWithFormatKey() {
        assertEquals("error_email_format", validateEmail("name@").messageKey)
    }

    @Test
    fun validEmail_hasNoMessage() {
        assertEquals(ValidationState.Valid, validateEmail("name@example.com"))
    }

    @Test
    fun reduceMotion_followsCurrentPreference() {
        val preferences = FakeAccessibilityPreferences(reduceMotion = false)
        assertEquals(MotionPolicy.Animated, motionPolicy(preferences))

        preferences.reduceMotion.value = true
        assertEquals(MotionPolicy.Reduced, motionPolicy(preferences))
    }
}
