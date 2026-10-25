package repair

import androidx.compose.foundation.layout.Column
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.semantics.SemanticsNode
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.semantics.getOrNull
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import evals.fixtures.AddressForm
import evals.fixtures.Order
import evals.fixtures.OrderCard
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

// Hidden checks for the repaired fixture. They read the merged semantics tree, which is what
// accessibility services see, and accept any fix that exposes the behavior.
@RunWith(RobolectricTestRunner::class)
class RepairTest {
    @get:Rule
    val rule = createComposeRule()

    private fun SemanticsNode.mentions(phrase: String): Boolean {
        val text = config.getOrNull(SemanticsProperties.Text).orEmpty().map { it.text } +
            config.getOrNull(SemanticsProperties.ContentDescription).orEmpty() +
            listOfNotNull(config.getOrNull(SemanticsProperties.Error))
        return text.any { phrase.lowercase() in it.lowercase() }
    }

    private fun mentioning(phrase: String) = SemanticsMatcher("mentions $phrase") { it.mentions(phrase) }

    @Test
    fun trackActionIsReachable() {
        var tracked = false
        rule.setContent { OrderCard(Order("1234", "Shipped"), onOpen = {}, onTrack = { tracked = true }) }

        val buttons = rule.onAllNodes(hasClickAction() and mentioning("Track"))
        if (buttons.fetchSemanticsNodes().isNotEmpty()) {
            buttons[0].performClick()
        } else {
            val action = rule.onAllNodes(SemanticsMatcher.keyIsDefined(SemanticsActions.CustomActions))
                .fetchSemanticsNodes()
                .flatMap { it.config.getOrNull(SemanticsActions.CustomActions).orEmpty() }
                .firstOrNull { "track" in it.label.lowercase() }
            rule.runOnIdle { action?.action?.invoke() }
        }

        rule.runOnIdle { assertTrue("Track is not reachable as a click or custom action", tracked) }
    }

    @Test
    fun errorIsExposedOnField() {
        rule.setContent { AddressForm(errors = listOf("Enter a street"), street = "", onStreetChange = {}) }

        rule.onNode(SemanticsMatcher.keyIsDefined(SemanticsProperties.EditableText))
            .assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Error))
    }

    @Test
    fun existingBehaviorIsPreserved() {
        var opened = false
        var street = ""
        rule.setContent {
            Column {
                OrderCard(Order("1234", "Shipped"), onOpen = { opened = true }, onTrack = {})
                AddressForm(errors = listOf("Enter a street"), street = "", onStreetChange = { street = it })
            }
        }

        rule.onAllNodes(hasClickAction() and mentioning("1234"))[0].performClick()
        rule.runOnIdle { assertTrue("Opening the order no longer works", opened) }
        assertTrue(rule.onAllNodes(mentioning("Shipped")).fetchSemanticsNodes().isNotEmpty())
        assertTrue(rule.onAllNodes(mentioning("Enter a street"), useUnmergedTree = true).fetchSemanticsNodes().isNotEmpty())
        rule.onNode(SemanticsMatcher.keyIsDefined(SemanticsProperties.EditableText)).performTextInput("Main")
        rule.runOnIdle { assertEquals("Main", street) }
    }
}
