package dev.vprogrammers.a11y.samples

import android.webkit.WebView
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

// Asserts WebView settings only. DOM semantics, zoom gestures, and TalkBack need a device.
@RunWith(RobolectricTestRunner::class)
class WebViewPatternsTest {
    @Test
    fun webView_keepsPinchZoomWithoutZoomButtons() {
        val webView = WebView(ApplicationProvider.getApplicationContext())

        keepWebZoomAvailable(webView)

        assertTrue(webView.settings.supportZoom())
        assertTrue(webView.settings.builtInZoomControls)
        assertFalse(webView.settings.displayZoomControls)
    }
}
