package dev.vprogrammers.a11y.samples

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.getUnclippedBoundsInRoot
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onAllNodesWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.dp
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

// Host tests assert semantics only. They do not prove TalkBack speech or navigation.
@RunWith(RobolectricTestRunner::class)
class ComposePatternsTest {
    @get:Rule
    val rule = createComposeRule()

    @Test
    fun deleteButton_isOneButtonWithoutDuplicateIconLabel() {
        rule.setContent { DeleteButton(onDelete = {}) }

        rule.onNode(hasClickAction() and hasText("Delete"))
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.Role, Role.Button))
        rule.onAllNodesWithContentDescription("Delete", useUnmergedTree = true).assertCountEquals(0)
    }

    @Test
    fun sectionHeading_isHeading() {
        rule.setContent { SectionHeading("Shipping") }

        rule.onNodeWithText("Shipping").assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Heading))
    }

    @Test
    fun uploadProgress_exposesStateDescription() {
        rule.setContent { UploadProgress("40 percent uploaded") }

        rule.onNodeWithText("40 percent uploaded")
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.StateDescription, "40 percent uploaded"))
    }

    @Test
    fun featuredLabel_hidesDecorativeIcon() {
        rule.setContent { FeaturedLabel("Featured") }

        rule.onAllNodes(SemanticsMatcher.keyIsDefined(SemanticsProperties.HideFromAccessibility), useUnmergedTree = true)
            .assertCountEquals(1)
    }

    @Test
    fun passwordField_exposesErrorAndPasswordSemantics() {
        rule.setContent { PasswordField(value = "", onValueChange = {}, errorMessage = "Enter your password") }

        rule.onNode(SemanticsMatcher.keyIsDefined(SemanticsProperties.EditableText))
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.Error, "Enter your password"))
            .assert(SemanticsMatcher.keyIsDefined(SemanticsProperties.Password))
    }

    @Test
    fun oneTimeCodeField_isNotMarkedAsPassword() {
        rule.setContent { OneTimeCodeField(value = "", onValueChange = {}) }

        rule.onNode(SemanticsMatcher.keyIsDefined(SemanticsProperties.EditableText))
            .assert(SemanticsMatcher.keyNotDefined(SemanticsProperties.Password))
    }

    @Test
    fun scalableLabel_growsAtLargeFontScale() {
        rule.setContent {
            CompositionLocalProvider(LocalDensity provides Density(density = 1f, fontScale = 2f)) {
                ScalableLabel("Line one\nLine two\nLine three")
            }
        }

        val bounds = rule.onNodeWithText("Line one\nLine two\nLine three").getUnclippedBoundsInRoot()
        val height = bounds.bottom - bounds.top
        assertTrue("Expected text to grow beyond its 40 dp minimum, was $height", height > 40.dp)
    }
}
