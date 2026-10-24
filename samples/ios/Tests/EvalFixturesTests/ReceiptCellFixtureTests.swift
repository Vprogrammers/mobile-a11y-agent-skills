import UIKit
import XCTest
@testable import EvalFixtures

// Guards the uikit-container-traps-review eval: each test proves that a rubric finding is still
// present in the fixture. Test names end with the rubric finding id.
@MainActor
final class ReceiptCellFixtureTests: XCTestCase {
    private func removeButton(in cell: ReceiptCell) throws -> UIButton {
        try XCTUnwrap(Mirror(reflecting: cell).descendant("remove") as? UIButton, "Fixture no longer has remove")
    }

    func testCellElementHidesRemoveButton() throws {
        let cell = ReceiptCell(style: .default, reuseIdentifier: nil)
        cell.configure(title: "Coffee", amount: "$4.00")

        XCTAssertTrue(cell.isAccessibilityElement)
        XCTAssertTrue(cell.accessibilityCustomActions?.isEmpty ?? true)
        XCTAssertEqual(try removeButton(in: cell).title(for: .normal), "Remove")
    }

    func testLegacyButtonTitleFixedSize() throws {
        let cell = ReceiptCell(style: .default, reuseIdentifier: nil)
        let window = UIWindow(frame: CGRect(x: 0, y: 0, width: 400, height: 800))
        window.addSubview(cell)
        cell.traitOverrides.preferredContentSizeCategory = .accessibilityExtraExtraExtraLarge
        window.layoutIfNeeded()
        let remove = try removeButton(in: cell)
        remove.layoutIfNeeded()

        XCTAssertEqual(remove.titleLabel?.font.pointSize, 15)
    }

    func testMissingOneTimeCodeContentType() {
        let view = CodeEntryView(frame: .zero)

        XCTAssertNil(view.field.textContentType)
        XCTAssertEqual(view.field.keyboardType, .numberPad)
    }
}
