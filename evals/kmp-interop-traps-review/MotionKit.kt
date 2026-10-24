// commonMain/kotlin/example/motion/MotionSpec.kt
package example.motion

expect fun isReduceMotionEnabled(): Boolean

public data class MotionSpec(val durationMillis: Int)

public fun motionSpec(): MotionSpec =
    if (isReduceMotionEnabled()) MotionSpec(durationMillis = 0) else MotionSpec(durationMillis = 300)

// androidMain/kotlin/example/motion/MotionSpec.android.kt
package example.motion

import android.content.Context
import android.provider.Settings

lateinit var appContext: Context

actual fun isReduceMotionEnabled(): Boolean =
    Settings.Global.getFloat(appContext.contentResolver, Settings.Global.ANIMATOR_DURATION_SCALE, 1f) == 0f

// iosMain/kotlin/example/motion/MotionSpec.ios.kt
package example.motion

import platform.UIKit.UIAccessibilityIsReduceMotionEnabled
import platform.UIKit.UIAccessibilityTraitHeader
import platform.UIKit.UIAccessibilityTraits

actual fun isReduceMotionEnabled(): Boolean = UIAccessibilityIsReduceMotionEnabled()

public fun sectionTitleTraits(): UIAccessibilityTraits = UIAccessibilityTraitHeader

// iosMain/kotlin/example/motion/MainViewController.kt (Compose Multiplatform 1.8.1 shared UI)
package example.motion

import androidx.compose.ui.platform.AccessibilitySyncOptions
import androidx.compose.ui.window.ComposeUIViewController

fun MainViewController() = ComposeUIViewController(
    configure = { accessibilitySyncOptions = AccessibilitySyncOptions.Always(debugLogger = null) },
) { App(motion = motionSpec()) }

// Build notes: the iOS framework "MotionKit" is published to external Swift teams.
// CI fails if the generated Objective-C header mentions UIKit types, and that check passes.
