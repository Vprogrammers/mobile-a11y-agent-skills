package dev.vprogrammers.a11y.kmp

import kotlinx.coroutines.flow.StateFlow

/**
 * Platform capability injected into shared code. An interface keeps common tests on a fake and
 * avoids an `expect`/`actual` that would need a global Android `Context`.
 */
interface AccessibilityPreferences {
    val reduceMotion: StateFlow<Boolean>
}

/** Swift-friendly enum: each platform chooses the concrete animation for the shared decision. */
enum class MotionPolicy {
    Animated,

    /** Keep the state change visible, but replace movement with a crossfade or an instant change. */
    Reduced,
}

fun motionPolicy(preferences: AccessibilityPreferences): MotionPolicy =
    if (preferences.reduceMotion.value) MotionPolicy.Reduced else MotionPolicy.Animated
