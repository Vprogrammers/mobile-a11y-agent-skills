package dev.vprogrammers.a11y.samples

import android.text.InputType
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.state.ToggleableState
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.getUnclippedBoundsInRoot
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onAllNodesWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performTouchInput
import androidx.compose.ui.test.swipeLeft
import androidx.compose.ui.unit.Density
import androidx.test.core.app.ApplicationProvider
import evals.fixtures.AccessibleRetryView
import evals.fixtures.AccessibleSettings
import evals.fixtures.AddressForm
import evals.fixtures.CheckoutScreen
import evals.fixtures.Item
import evals.fixtures.Message
import evals.fixtures.MessageThread
import evals.fixtures.Order
import evals.fixtures.OrderCard
import evals.fixtures.PaymentView
import evals.fixtures.PinEntryActivity
import evals.fixtures.ReaderSettings
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
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

    @Test
    fun composeSemanticsTrapsReview_clearAndSetHidesTrackAction() {
        rule.setContent { OrderCard(Order("1234", "Shipped"), onOpen = {}, onTrack = {}) }

        // The merged tree is what accessibility services see; the cleared Track button is absent from it.
        rule.onAllNodes(hasText("Track")).assertCountEquals(0)
        rule.onAllNodes(hasClickAction()).assertCountEquals(1)
    }

    @Test
    fun composeSemanticsTrapsReview_errorNotAssociatedWithField() {
        rule.setContent { AddressForm(errors = listOf("Enter a street"), street = "", onStreetChange = {}) }

        rule.onNode(SemanticsMatcher.keyIsDefined(SemanticsProperties.EditableText))
            .assert(SemanticsMatcher.keyNotDefined(SemanticsProperties.Error))
        rule.onNodeWithText("Enter a street").assertIsDisplayed()
    }

    @Test
    fun androidSdk36BehaviorReview_passwordVariationForVisibleCode() {
        val activity = Robolectric.buildActivity(PinEntryActivity::class.java).setup().get()
        val pin = activity.window.decorView.descendants().filterIsInstance<EditText>().single()

        assertEquals(InputType.TYPE_NUMBER_VARIATION_PASSWORD, pin.inputType and InputType.TYPE_MASK_VARIATION)
        assertNull(pin.transformationMethod)
    }

    @Test
    fun androidSdk36BehaviorReview_onBackPressedNotCalledOnSdk36() {
        // The fixture handles back only through the legacy override that SDK 36 no longer calls.
        PinEntryActivity::class.java.getDeclaredMethod("onBackPressed")
    }

    @Test
    fun composeMessageThreadReview_clickableTextLinksNotAccessible() {
        rule.setContent { MessageThread(emptyList(), false, {}, {}, {}, {}) }

        // ClickableText resolves links from tap offsets, so the text exposes no click action or link.
        rule.onNode(hasText("Messages follow our terms and privacy policy."))
            .assert(SemanticsMatcher.keyNotDefined(SemanticsActions.OnClick))
    }

    @Test
    fun composeMessageThreadReview_toggleRowWithoutRoleOrState() {
        rule.setContent { MessageThread(emptyList(), true, {}, {}, {}, {}) }

        rule.onNode(hasText("Send read receipts") and hasClickAction())
            .assert(SemanticsMatcher.keyNotDefined(SemanticsProperties.Role))
            .assert(SemanticsMatcher.keyNotDefined(SemanticsProperties.ToggleableState))
        rule.onAllNodes(SemanticsMatcher.expectValue(SemanticsProperties.Role, Role.Switch)).assertCountEquals(1)
    }

    @Test
    fun composeMessageThreadReview_undoBannerFixedTimeout() {
        rule.mainClock.autoAdvance = false
        rule.setContent { MessageThread(listOf(Message(1, "Hello")), false, {}, {}, {}, {}) }

        rule.onNodeWithText("Delete").performClick()
        rule.mainClock.advanceTimeBy(100)
        rule.onNodeWithText("Undo").assertIsDisplayed()
        rule.mainClock.advanceTimeBy(3_100)
        rule.onNodeWithText("Undo").assertDoesNotExist()
    }

    @Test
    fun heldoutComposeReaderReview_captionSizeConvertedFromDp() {
        val fontScale = mutableFloatStateOf(1f)
        rule.setContent {
            CompositionLocalProvider(LocalDensity provides Density(density = 1f, fontScale = fontScale.floatValue)) {
                ReaderSettings("Medium", {}, {}, showTips = false, onDismissTips = {})
            }
        }
        val caption = "Changes apply to every book in your library."
        val normal = rule.onNodeWithText(caption).getUnclippedBoundsInRoot()

        fontScale.floatValue = 2f
        rule.waitForIdle()
        val large = rule.onNodeWithText(caption).getUnclippedBoundsInRoot()

        // The caption keeps its size because toSp() divides the font scale back out.
        assertEquals(normal.bottom - normal.top, large.bottom - large.top)
    }
}

private fun android.view.View.descendants(): List<android.view.View> = when (this) {
    is android.view.ViewGroup -> listOf(this) + (0 until childCount).flatMap { getChildAt(it).descendants() }
    else -> listOf(this)
}
