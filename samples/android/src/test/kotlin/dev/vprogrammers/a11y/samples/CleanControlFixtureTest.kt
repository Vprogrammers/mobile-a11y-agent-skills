package dev.vprogrammers.a11y.samples

import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.state.ToggleableState
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import evals.fixture.settings.SettingsScreen
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

// Guards the compose-clean-control eval: the negative control must stay free of seeded defects.
@RunWith(RobolectricTestRunner::class)
class CleanControlFixtureTest {
    @get:Rule
    val rule = createComposeRule()

    @Test
    fun settingsScreen_exposesHeadingAndOneNamedSwitchRow() {
        rule.setContent { SettingsScreen(notificationsOn = true, onNotificationsChange = {}, onSignOut = {}) }

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
}
