import UIKit
import XCTest
@testable import ApplePatterns

// Unit tests assert exposed accessibility properties only. They do not prove VoiceOver speech.
@MainActor
final class UIKitPatternsTests: XCTestCase {
    func testScalableLabelAdjustsForContentSizeCategory() {
        let label = makeScalableLabel(text: "Order summary")

        XCTAssertTrue(label.adjustsFontForContentSizeCategory)
        XCTAssertEqual(label.numberOfLines, 0)
    }

    func testScalableLabelGrowsAtAccessibilitySizes() {
        let base = UIFont.systemFont(ofSize: 17)
        let large = UITraitCollection(preferredContentSizeCategory: .accessibilityExtraExtraExtraLarge)

        let scaled = UIFontMetrics(forTextStyle: .body).scaledFont(for: base, compatibleWith: large)

        XCTAssertGreaterThan(scaled.pointSize, base.pointSize)
    }

    func testModalCardIsModalWithHeaderTitle() {
        let card = ModalCardView()

        XCTAssertTrue(card.accessibilityViewIsModal)
        XCTAssertTrue(card.titleLabel.accessibilityTraits.contains(.header))
    }

    func testStepperIsAdjustableAndClampsValue() {
        let stepper = StepperView(value: 5, range: 1...5)

        XCTAssertTrue(stepper.isAccessibilityElement)
        XCTAssertTrue(stepper.accessibilityTraits.contains(.adjustable))

        stepper.accessibilityIncrement()
        XCTAssertEqual(stepper.accessibilityValue, "5")

        stepper.accessibilityDecrement()
        XCTAssertEqual(stepper.accessibilityValue, "4")
    }

    func testArchiveActionKeepsExistingActions() {
        let row = UIView()
        row.accessibilityCustomActions = [UIAccessibilityCustomAction(name: "Share") { _ in true }]

        addArchiveAction(to: row) {}

        XCTAssertEqual(row.accessibilityCustomActions?.map(\.name), ["Share", "Archive"])
    }
}
