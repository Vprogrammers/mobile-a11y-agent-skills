package dev.vprogrammers.a11y.samples

import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.platform.AccessibilityManager
import androidx.compose.ui.platform.LocalAccessibilityManager
import androidx.compose.ui.state.ToggleableState
import androidx.compose.ui.text.LinkAnnotation
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.SemanticsActions
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.DeviceConfigurationOverride
import androidx.compose.ui.test.FontScale
import androidx.compose.ui.test.LayoutDirection
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.assertHeightIsAtLeast
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.getUnclippedBoundsInRoot
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onAllNodesWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection as Direction
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
    fun salesChart_hasSummaryAndReachableValues() {
        rule.setContent { SalesChart(listOf("May" to 3, "June" to 5), summary = "Sales rose from 3 to 5") }

        rule.onAllNodesWithContentDescription("Sales rose from 3 to 5").assertCountEquals(1)
        rule.onNodeWithText("June: 5").assertExists()
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
        // The visible supporting text is hidden, so TalkBack reads the error once (checked on a device).
        rule.onAllNodes(hasText("Enter your password"), useUnmergedTree = true).assertCountEquals(0)
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

    @Test
    fun orderRow_namesClickOutcomeAndRoleWithMinimumTarget() {
        rule.setContent { OrderRow(title = "Order 1234", onOpen = {}) }

        rule.onNodeWithText("Order 1234")
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.Role, Role.Button))
            .assert(SemanticsMatcher("click label") { it.config[SemanticsActions.OnClick].label == "Open order details" })
            .assertHeightIsAtLeast(48.dp)
    }

    @Test
    fun scalableLabel_growsWithDeviceFontScaleOverride() {
        rule.setContent {
            DeviceConfigurationOverride(DeviceConfigurationOverride.FontScale(2f)) {
                ScalableLabel("Line one\nLine two\nLine three")
            }
        }

        val bounds = rule.onNodeWithText("Line one\nLine two\nLine three").getUnclippedBoundsInRoot()
        assertTrue("Expected text to grow beyond its 40 dp minimum", bounds.bottom - bounds.top > 40.dp)
    }

    @Test
    fun salesChart_keepsValuesInRightToLeftLayout() {
        rule.setContent {
            DeviceConfigurationOverride(DeviceConfigurationOverride.LayoutDirection(Direction.Rtl)) {
                SalesChart(listOf("May" to 3), summary = "Sales were 3")
            }
        }

        rule.onNodeWithText("May: 3").assertExists()
    }

    @Test
    fun quotedPhrase_keepsTheWholeSentence() {
        rule.setContent { QuotedPhrase(intro = "The menu says ", phrase = "plat du jour", languageTag = "fr-FR") }

        rule.onNodeWithText("The menu says plat du jour").assertExists()
    }

    @Test
    fun settingToggleRow_isOneSwitchWithState() {
        rule.setContent { SettingToggleRow("Read receipts", checked = true, onCheckedChange = {}) }

        rule.onNode(hasText("Read receipts") and hasClickAction())
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.Role, Role.Switch))
            .assert(SemanticsMatcher.expectValue(SemanticsProperties.ToggleableState, ToggleableState.On))
        rule.onAllNodes(hasClickAction(), useUnmergedTree = true).assertCountEquals(1)
    }

    @Test
    fun termsNotice_exposesTheLinkAsAnAction() {
        rule.setContent { TermsNotice("https://example.com/terms") }

        // The link travels in the node's AnnotatedString, which TalkBack exposes as a link.
        rule.onNode(hasText("Messages follow our terms."))
            .assert(
                SemanticsMatcher("has a URL link") { node ->
                    node.config[SemanticsProperties.Text].any { text ->
                        text.getLinkAnnotations(0, text.length).any { (it.item as? LinkAnnotation.Url)?.url == "https://example.com/terms" }
                    }
                },
            )
    }

    @Test
    fun undoBanner_waitsForTheRecommendedTimeout() {
        var timedOut = false
        val slowUser = object : AccessibilityManager {
            override fun calculateRecommendedTimeoutMillis(
                originalTimeoutMillis: Long,
                containsIcons: Boolean,
                containsText: Boolean,
                containsControls: Boolean,
            ) = 20_000L
        }
        rule.mainClock.autoAdvance = false
        rule.setContent {
            CompositionLocalProvider(LocalAccessibilityManager provides slowUser) {
                UndoBanner("Message deleted", onUndo = {}, onTimeout = { timedOut = true })
            }
        }

        rule.mainClock.advanceTimeBy(5_000)
        assertTrue("The banner must outlast the default 4 s for this user", !timedOut)
        rule.mainClock.advanceTimeBy(16_000)
        assertTrue(timedOut)
    }
}
