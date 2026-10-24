package dev.vprogrammers.a11y.kmp

import android.content.Context
import android.os.Looper
import android.provider.Settings
import androidx.compose.foundation.layout.Box
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf

// Host tests assert exposed semantics and settings mapping. They do not prove TalkBack speech.
@RunWith(RobolectricTestRunner::class)
class AndroidAccessibilityTest {
    @get:Rule
    val rule = createComposeRule()

    private val messages = mapOf("error_email_required" to "Enter your email address")

    @Test
    fun blockingState_exposesLocalizedErrorSemantics() {
        rule.setContent { Box(Modifier.validationSemantics(validateEmail(""), messages::getValue)) }

        rule.onNode(SemanticsMatcher.expectValue(SemanticsProperties.Error, "Enter your email address"))
            .assertExists()
    }

    @Test
    fun validState_exposesNoError() {
        rule.setContent { Box(Modifier.validationSemantics(validateEmail("name@example.com"), messages::getValue)) }

        rule.onNode(SemanticsMatcher.keyIsDefined(SemanticsProperties.Error)).assertDoesNotExist()
    }

    @Test
    fun removedAnimations_reduceMotionAndFollowChanges() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        Settings.Global.putFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 0f)

        AndroidAccessibilityPreferences(context).use { preferences ->
            assertTrue(preferences.reduceMotion.value)
            assertEquals(MotionPolicy.Reduced, motionPolicy(preferences))

            Settings.Global.putFloat(context.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f)
            shadowOf(Looper.getMainLooper()).idle()
            assertFalse(preferences.reduceMotion.value)
        }
    }
}
