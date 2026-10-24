package dev.vprogrammers.a11y.kmp

import kotlin.test.Test
import kotlin.test.assertEquals
import platform.Foundation.NSNotificationCenter
import platform.UIKit.UIAccessibilityIsReduceMotionEnabled
import platform.UIKit.UIAccessibilityReduceMotionStatusDidChangeNotification

// Runs on the iOS simulator. It proves the adapter reads UIKit state, not VoiceOver behavior.
class IosAccessibilityPreferencesTest {
    @Test
    fun initialValue_matchesUIKit() {
        IosAccessibilityPreferences().use { preferences ->
            assertEquals(UIAccessibilityIsReduceMotionEnabled(), preferences.reduceMotion.value)
        }
    }

    @Test
    fun statusNotification_rereadsUIKit() {
        IosAccessibilityPreferences().use { preferences ->
            NSNotificationCenter.defaultCenter.postNotificationName(UIAccessibilityReduceMotionStatusDidChangeNotification, null)
            assertEquals(UIAccessibilityIsReduceMotionEnabled(), preferences.reduceMotion.value)
        }
    }
}
