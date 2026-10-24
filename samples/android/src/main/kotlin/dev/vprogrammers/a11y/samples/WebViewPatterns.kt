package dev.vprogrammers.a11y.samples

import android.webkit.WebView

// Compiled counterpart of the WebView guidance in android-patterns.md.

/** Keep pinch zoom available without the legacy on-screen zoom buttons. */
fun keepWebZoomAvailable(webView: WebView) {
    webView.settings.apply {
        setSupportZoom(true)
        builtInZoomControls = true
        displayZoomControls = false
    }
}
