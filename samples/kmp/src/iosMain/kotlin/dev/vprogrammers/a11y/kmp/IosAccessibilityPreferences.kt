package dev.vprogrammers.a11y.kmp

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import platform.Foundation.NSNotificationCenter
import platform.UIKit.UIAccessibilityIsReduceMotionEnabled
import platform.UIKit.UIAccessibilityReduceMotionStatusDidChangeNotification

/** iOS adapter: UIKit types stay inside the implementation, so the exported API remains platform-neutral. */
class IosAccessibilityPreferences : AccessibilityPreferences, AutoCloseable {
    private val state = MutableStateFlow(UIAccessibilityIsReduceMotionEnabled())
    override val reduceMotion: StateFlow<Boolean> = state.asStateFlow()

    // A null queue runs the block on the posting thread; MutableStateFlow is thread-safe.
    private val observer = NSNotificationCenter.defaultCenter.addObserverForName(
        name = UIAccessibilityReduceMotionStatusDidChangeNotification,
        `object` = null,
        queue = null,
    ) { _ -> state.value = UIAccessibilityIsReduceMotionEnabled() }

    override fun close() = NSNotificationCenter.defaultCenter.removeObserver(observer)
}
