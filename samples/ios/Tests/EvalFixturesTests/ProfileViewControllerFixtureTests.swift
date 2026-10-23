import UIKit
import XCTest
@testable import EvalFixtures

// Guards the ios-uikit-review eval: each test proves that a rubric finding is still present in
// the fixture. Test names end with the rubric finding id.
@MainActor
final class ProfileViewControllerFixtureTests: XCTestCase {
    private func loadedFixture() -> ProfileViewController {
        let controller = ProfileViewController()
        controller.loadViewIfNeeded()
        return controller
    }

    private func property<T>(_ name: String, of controller: ProfileViewController) throws -> T {
        try XCTUnwrap(Mirror(reflecting: controller).descendant(name) as? T, "Fixture no longer has \(name)")
    }

    func testGenericAvatarLabel() throws {
        let avatar: UIImageView = try property("avatar", of: loadedFixture())

        XCTAssertTrue(avatar.isAccessibilityElement)
        XCTAssertEqual(avatar.accessibilityLabel, "Image")
    }

    func testFixedFontNoDynamicType() throws {
        let status: UILabel = try property("status", of: loadedFixture())

        XCTAssertFalse(status.adjustsFontForContentSizeCategory)
    }

    func testGestureBackedViewNotButton() throws {
        let save: UIView = try property("save", of: loadedFixture())

        XCTAssertFalse(save.isAccessibilityElement)
        XCTAssertFalse(save.accessibilityTraits.contains(.button))
        XCTAssertNil(save.accessibilityLabel)
    }
}
