package dev.vprogrammers.a11y.samples

import android.view.View
import android.widget.TextView
import androidx.core.view.AccessibilityDelegateCompat
import androidx.core.view.ViewCompat
import androidx.core.view.accessibility.AccessibilityNodeInfoCompat
import androidx.core.view.accessibility.AccessibilityNodeInfoCompat.AccessibilityActionCompat

// Compiled counterparts of the Views guidance in android-patterns.md.

fun markAsHeading(title: TextView) {
    ViewCompat.setAccessibilityHeading(title, true)
}

fun exposeState(toggleRow: View, isOn: Boolean) {
    ViewCompat.setStateDescription(toggleRow, if (isOn) "On" else "Off")
}

/** Adds an action without discarding actions or metadata supplied by the superclass. */
fun addArchiveAction(row: View, onArchive: () -> Unit) {
    val archiveId = ViewCompat.addAccessibilityAction(row, "Archive") { _, _ ->
        onArchive()
        true
    }
    check(archiveId != View.NO_ID)
}

class ExpandableRowDelegate(private val isExpanded: () -> Boolean) : AccessibilityDelegateCompat() {
    override fun onInitializeAccessibilityNodeInfo(host: View, info: AccessibilityNodeInfoCompat) {
        super.onInitializeAccessibilityNodeInfo(host, info)
        info.addAction(
            if (isExpanded()) AccessibilityActionCompat.ACTION_COLLAPSE else AccessibilityActionCompat.ACTION_EXPAND,
        )
    }
}
