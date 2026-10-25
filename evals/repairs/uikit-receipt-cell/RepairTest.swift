import UIKit
import XCTest
@testable import RepairFixture

// Hidden checks for the repaired fixture. They inspect the UIKit accessibility properties that
// VoiceOver and Voice Control read, and accept any fix that exposes the behavior.
@MainActor
final class RepairTest: XCTestCase {
    private func buttons(in view: UIView) -> [UIButton] {
        view.subviews.flatMap { subview -> [UIButton] in
            if let button = subview as? UIButton { return [button] }
            return buttons(in: subview)
        }
    }

    private func labelTexts(in view: UIView) -> [String] {
        view.subviews.flatMap { subview -> [String] in
            ((subview as? UILabel)?.text).map { [$0] } ?? labelTexts(in: subview)
        }
    }

    private func configuredCell(onRemove: @escaping () -> Void = {}) -> ReceiptCell {
        let cell = ReceiptCell(style: .default, reuseIdentifier: nil)
        cell.configure(title: "Coffee", amount: "$4.00")
        cell.onRemove = onRemove
        return cell
    }

    private func perform(_ action: UIAccessibilityCustomAction) {
        if let handler = action.actionHandler {
            _ = handler(action)
        } else if let target = action.target as? NSObject {
            _ = target.perform(action.selector, with: action)
        }
    }

    func testRemoveActionIsReachable() throws {
        var removed = false
        let cell = configuredCell { removed = true }

        if cell.isAccessibilityElement {
            let action = try XCTUnwrap(
                cell.accessibilityCustomActions?.first { $0.name.lowercased().contains("remove") },
                "The cell is one element, so Remove must be a custom action"
            )
            perform(action)
        } else {
            // Outside a running assistive technology, UIKit does not fill in a button's default accessibility
            // label or element status, so check what would hide the button instead.
            let remove = try XCTUnwrap(buttons(in: cell).first {
                ($0.currentTitle ?? $0.configuration?.title ?? $0.accessibilityLabel ?? "").lowercased().contains("remove")
            })
            XCTAssertFalse(remove.isHidden || remove.accessibilityElementsHidden, "Remove is hidden from accessibility")
            for container in [cell, cell.contentView] as [UIView] {
                if let elements = container.accessibilityElements {
                    XCTAssertTrue(elements.contains { ($0 as AnyObject) === remove }, "Remove is left out of accessibilityElements")
                }
            }
            remove.sendActions(for: .touchUpInside)
        }

        XCTAssertTrue(removed, "Remove is not reachable through accessibility")
    }

    func testRemoveTitleFollowsDynamicType() throws {
        let cell = configuredCell()
        let window = UIWindow(frame: CGRect(x: 0, y: 0, width: 400, height: 800))
        window.addSubview(cell)
        cell.traitOverrides.preferredContentSizeCategory = .accessibilityExtraExtraExtraLarge
        window.layoutIfNeeded()
        let remove = try XCTUnwrap(buttons(in: cell).first)
        remove.layoutIfNeeded()

        XCTAssertGreaterThan(try XCTUnwrap(remove.titleLabel?.font.pointSize), 20)
    }

    func testCodeFieldOffersOneTimeCodeAutoFill() {
        XCTAssertEqual(CodeEntryView(frame: .zero).field.textContentType, .oneTimeCode)
    }

    func testExistingBehaviorIsPreserved() throws {
        var removed = false
        let cell = configuredCell { removed = true }
        let remove = try XCTUnwrap(buttons(in: cell).first, "The visible Remove button is gone")
        remove.sendActions(for: .touchUpInside)
        XCTAssertTrue(removed, "Tapping Remove no longer works")

        let spoken = [cell.accessibilityLabel, cell.accessibilityValue].compactMap { $0 }.joined(separator: " ")
        XCTAssertTrue(labelTexts(in: cell.contentView).contains("Coffee"), "The visible title is lost")
        if cell.isAccessibilityElement {
            // As one element, the cell's own label is all VoiceOver reads.
            XCTAssertTrue(spoken.contains("Coffee"), "VoiceOver no longer receives the title")
        }

        let code = CodeEntryView(frame: .zero)
        XCTAssertEqual(code.field.placeholder, "Verification code")
        XCTAssertEqual(code.field.keyboardType, .numberPad)
    }
}
