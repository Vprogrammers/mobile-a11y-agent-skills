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

    /// The clean control must not contain the legacy fixed-size button title that a reviewer should report.
    func testCleanUIKitFixtureButtonTitleFollowsDynamicType() throws {
        let view = AccessibleProfileView {}
        let save = try XCTUnwrap(view.arrangedSubviews[1] as? UIButton)
        let window = UIWindow(frame: CGRect(x: 0, y: 0, width: 400, height: 800))
        window.addSubview(view)
        view.traitOverrides.preferredContentSizeCategory = .accessibilityExtraExtraExtraLarge
        window.layoutIfNeeded()
        save.layoutIfNeeded()

        XCTAssertGreaterThan(save.titleLabel?.font.pointSize ?? 0, 40)
    }
}
