import SwiftUI
import UIKit
import XCTest
@testable import EvalFixtures

@MainActor
final class CleanFixturesTests: XCTestCase {
    func testCleanSwiftUIFixtureBuilds() {
        let view = AccessibleDownloadRow(progress: 0.5, onCancel: {})

        _ = view.body
    }

    func testCleanUIKitFixtureUsesNativeControlsAndDynamicType() {
        var didSave = false
        let view = AccessibleProfileView { didSave = true }
        let status = view.arrangedSubviews[0] as? UILabel
        let save = view.arrangedSubviews[1] as? UIButton

        XCTAssertEqual(status?.text, "Profile verified")
        XCTAssertTrue(status?.adjustsFontForContentSizeCategory == true)
        XCTAssertEqual(save?.title(for: .normal), "Save profile")
        save?.sendActions(for: .touchUpInside)
        XCTAssertTrue(didSave)
    }
}
