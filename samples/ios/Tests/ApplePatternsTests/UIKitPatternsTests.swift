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

    func testConfiguredButtonTitleGrowsAtAccessibilitySizes() {
        let button = makeScalableButton(title: "Save profile")

        XCTAssertGreaterThan(titlePointSize(of: button, at: .accessibilityExtraExtraExtraLarge), 40)
    }

    /// Documents the trap in apple-patterns.md: the legacy system button title does not scale.
    func testLegacySystemButtonTitleStaysFixed() {
        let button = UIButton(type: .system)
        button.setTitle("Save profile", for: .normal)

        XCTAssertEqual(titlePointSize(of: button, at: .accessibilityExtraExtraExtraLarge), 15)
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

/// Lays the button out in a window at the given content size and returns its title font size.
@MainActor
func titlePointSize(of button: UIButton, at category: UIContentSizeCategory) -> CGFloat {
    let window = UIWindow(frame: CGRect(x: 0, y: 0, width: 400, height: 800))
    window.addSubview(button)
    button.traitOverrides.preferredContentSizeCategory = category
    window.layoutIfNeeded()
    button.layoutIfNeeded()
    return button.titleLabel?.font.pointSize ?? 0
}
