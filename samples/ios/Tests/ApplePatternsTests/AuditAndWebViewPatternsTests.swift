import XCTest
@testable import ApplePatterns

/// Compiled counterpart of the audit example in test-matrix.md. Call it from a UI test target
/// after `app.launch()`; a unit test bundle cannot launch an app, so this file only compiles it.
@MainActor
func auditCheckoutScreen(_ app: XCUIApplication) throws {
    try app.performAccessibilityAudit(for: [.dynamicType, .contrast, .hitRegion, .sufficientElementDescription]) { issue in
        // Return true only for a triaged false positive, matched as narrowly as possible.
        issue.auditType == .contrast && issue.element?.identifier == "decorative-watermark"
    }
}

@MainActor
final class AuditAndWebViewPatternsTests: XCTestCase {
    func testWebViewConfigurationIgnoresViewportScaleLimits() {
        XCTAssertTrue(makeZoomableWebViewConfiguration().ignoresViewportScaleLimits)
    }
}
