package dev.vprogrammers.a11y.samples

import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onAllNodesWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import evals.fixture.checkout.CartLine
import evals.fixture.checkout.CheckoutScreen
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

// Guards the android-compose-review eval: each test proves a seeded defect still exists.
@RunWith(RobolectricTestRunner::class)
class CheckoutFixtureTest {
    @get:Rule
    val rule = createComposeRule()

    private fun showCheckout(showConfirm: Boolean = false) {
        rule.setContent {
            CheckoutScreen(
                lines = listOf(CartLine("a", "Coffee", "€4"), CartLine("b", "Tea", "€3")),
                cardNumber = "",
                onCardNumberChange = {},
                onRemove = {},
                onClose = {},
                onPay = {},
                showConfirm = showConfirm,
                onConfirm = {},
            )
        }
    }

    @Test
    fun closeIcon_hasClickActionButNoName() {
        showCheckout()

        val unnamedClickable = hasClickAction() and
            SemanticsMatcher.keyNotDefined(SemanticsProperties.ContentDescription) and
            SemanticsMatcher.keyNotDefined(SemanticsProperties.Text)
        rule.onAllNodes(unnamedClickable).assertCountEquals(1)
    }

    @Test
    fun cartHeader_duplicatesVisibleText() {
        showCheckout()

        rule.onAllNodesWithContentDescription("Your cart", useUnmergedTree = true).assertCountEquals(1)
        rule.onAllNodes(hasText("Your cart"), useUnmergedTree = true).assertCountEquals(1)
    }

    @Test
    fun cartLine_hasNoRemoveAction() {
        showCheckout()

        rule.onAllNodes(SemanticsMatcher.keyIsDefined(SemanticsActions.CustomActions)).assertCountEquals(0)
        rule.onAllNodes(hasText("Remove", substring = true)).assertCountEquals(0)
    }

    @Test
    fun confirmOverlay_leavesBackgroundReachable() {
        showCheckout(showConfirm = true)

        rule.onNodeWithText("Confirm payment").assertIsDisplayed()
        rule.onNodeWithText("Pay").assertIsDisplayed()
        rule.onAllNodes(SemanticsMatcher.keyIsDefined(SemanticsProperties.PaneTitle)).assertCountEquals(0)
    }
}
