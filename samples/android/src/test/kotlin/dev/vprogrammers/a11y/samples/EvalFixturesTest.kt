package dev.vprogrammers.a11y.samples

import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Button
import android.widget.TextView
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.state.ToggleableState
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onAllNodesWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.swipeLeft
import androidx.test.core.app.ApplicationProvider
import evals.fixtures.AccessibleRetryView
import evals.fixtures.AccessibleSettings
import evals.fixtures.CheckoutScreen
import evals.fixtures.Item
import evals.fixtures.PaymentView
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

// Guards the eval fixtures: each test proves that a rubric finding is still present in the
// fixture (or, for the clean control, still absent). Test names end with the rubric finding id.
@RunWith(RobolectricTestRunner::class)
class EvalFixturesTest {
    @get:Rule
    val rule = createComposeRule()

    @Test
    fun androidComposeReview_duplicateDeleteSemantics() {
        rule.setContent { CheckoutScreen(items = listOf(Item("coffee")), onDelete = {}) }

        rule.onAllNodesWithContentDescription("Delete coffee", useUnmergedTree = true).assertCountEquals(1)
        rule.onAllNodes(hasText("Delete coffee"), useUnmergedTree = true).assertCountEquals(1)
    }

    @Test
    fun androidComposeReview_gestureOnlyHelp() {
        rule.setContent { CheckoutScreen(items = emptyList(), onDelete = {}) }

        rule.onNodeWithText("Swipe left for help")
            .assert(SemanticsMatcher.keyNotDefined(SemanticsActions.OnClick))
            .assert(SemanticsMatcher.keyNotDefined(SemanticsActions.CustomActions))
    }

    @Test
    fun androidComposeReview_nonModalOverlay() {
        rule.setContent { CheckoutScreen(items = listOf(Item("coffee")), onDelete = {}) }
        rule.onNodeWithText("Swipe left for help").performTouchInput { swipeLeft() }

        rule.onNodeWithText("Help").assertIsDisplayed()
        rule.onNodeWithText("Checkout").assertIsDisplayed()
        rule.onAllNodes(SemanticsMatcher.keyIsDefined(SemanticsProperties.PaneTitle)).assertCountEquals(0)
    }

    @Test
    fun androidViewsReview_touchOnlyAction() {
        val view = PaymentView(ApplicationProvider.getApplicationContext())
        val node = view.createAccessibilityNodeInfo()

        assertFalse(node.isClickable)
        assertFalse(node.actionList.any { it.id == AccessibilityNodeInfo.ACTION_CLICK })
        assertNull(node.contentDescription)
        assertNull(node.stateDescription)
    }

    @Test
    fun cleanComposeReview_recognizesNoProvenBlocker() {
        rule.setContent { AccessibleSettings(notificationsEnabled = true, onNotificationsChanged = {}) }

        rule.onNodeWithText("Settings").assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Heading))
        rule.onNode(hasText("Notifications") and hasClickAction())
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.Role, Role.Switch))
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.ToggleableState, ToggleableState.On))
        rule.onAllNodes(
            hasClickAction() and
                SemanticsMatcher.keyNotDefined(SemanticsProperties.Text) and
                SemanticsMatcher.keyNotDefined(SemanticsProperties.ContentDescription),
        ).assertCountEquals(0)
    }

    @Test
    fun cleanAndroidViewsReview_recognizesNoProvenBlocker() {
        val view = AccessibleRetryView(ApplicationProvider.getApplicationContext()) {}
        val status = view.getChildAt(0) as TextView
        val retry = view.getChildAt(1) as Button

        assertEquals(2, view.childCount)
        assertEquals("Connection failed", status.text)
        assertEquals("Retry", retry.text)
        assertTrue(retry.isClickable)
        assertTrue(retry.hasOnClickListeners())
    }
}
