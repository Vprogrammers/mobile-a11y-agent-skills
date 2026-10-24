import WebKit

// Compiled counterpart of the web content guidance in apple-patterns.md.

/// Lets people zoom even when the page sets `user-scalable=no` or a restrictive `maximum-scale`.
@MainActor
public func makeZoomableWebViewConfiguration() -> WKWebViewConfiguration {
    let configuration = WKWebViewConfiguration()
    configuration.ignoresViewportScaleLimits = true
    return configuration
}
