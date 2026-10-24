package dev.vprogrammers.a11y.samples

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.junit4.accessibility.enableAccessibilityChecks
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.tryPerformAccessibilityChecks
import androidx.compose.ui.unit.dp
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.GraphicsMode

/**
 * Guards the evidence limit in test-matrix.md: Compose accessibility checks require an API 34+
 * device or emulator and do not report findings on Robolectric. If this test starts failing,
 * Robolectric support has changed; update the reference before relying on host-test results.
 */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class AccessibilityChecksTest {
    @get:Rule
    val rule = createComposeRule()

    @Test
    fun accessibilityChecks_doNotReportUnlabeledSmallTargetOnRobolectric() {
        rule.enableAccessibilityChecks()
        rule.setContent { Box(Modifier.size(16.dp).clickable {}) }

        // An unlabeled 16 dp target fails on a device; here the checks pass silently.
        rule.onRoot().tryPerformAccessibilityChecks()
    }
}
