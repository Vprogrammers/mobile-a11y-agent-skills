import UIKit

// Compiled counterparts of the UIKit guidance in apple-patterns.md.

/// Dynamic Type label using UIFontMetrics with a custom base font.
@MainActor
public func makeScalableLabel(text: String, baseFont: UIFont = .systemFont(ofSize: 17, weight: .semibold)) -> UILabel {
    let label = UILabel()
    label.text = text
    label.numberOfLines = 0
    label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)
    label.adjustsFontForContentSizeCategory = true
    return label
}

/// Button whose title follows Dynamic Type. A legacy `UIButton(type: .system)` keeps a fixed 15 pt title.
@MainActor
public func makeScalableButton(title: String) -> UIButton {
    let button = UIButton(configuration: .plain())
    button.setTitle(title, for: .normal)
    return button
}

/// Custom modal container that keeps VoiceOver inside it while presented.
public final class ModalCardView: UIView {
    public let titleLabel = UILabel()

    public override init(frame: CGRect) {
        super.init(frame: frame)
        accessibilityViewIsModal = true
        titleLabel.accessibilityTraits.insert(.header)
        addSubview(titleLabel)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) is not supported")
    }

    /// Called when the card closes, including through the VoiceOver escape gesture.
    public var onDismiss: (() -> Void)?

    public override func accessibilityPerformEscape() -> Bool {
        guard let onDismiss else { return false }
        onDismiss()
        return true
    }

    /// Move VoiceOver to the card after presentation; this is a major context change.
    public func announcePresented() {
        UIAccessibility.post(notification: .screenChanged, argument: titleLabel)
    }
}

/// Custom adjustable control: one leaf element with value and increment/decrement.
public final class StepperView: UIView {
    public private(set) var value: Int
    public let range: ClosedRange<Int>

    public init(value: Int, range: ClosedRange<Int>) {
        self.value = value
        self.range = range
        super.init(frame: .zero)
        isAccessibilityElement = true
        accessibilityLabel = "Quantity"
        accessibilityTraits.insert(.adjustable)
        updateAccessibilityValue()
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) is not supported")
    }

    public override func accessibilityIncrement() {
        value = min(value + 1, range.upperBound)
        updateAccessibilityValue()
    }

    public override func accessibilityDecrement() {
        value = max(value - 1, range.lowerBound)
        updateAccessibilityValue()
    }

    private func updateAccessibilityValue() {
        accessibilityValue = "\(value)"
    }
}

/// Row with a secondary action exposed as a custom action instead of a swipe only.
@MainActor
public func addArchiveAction(to row: UIView, onArchive: @escaping @MainActor () -> Void) {
    let archive = UIAccessibilityCustomAction(name: "Archive") { _ in
        onArchive()
        return true
    }
    row.accessibilityCustomActions = (row.accessibilityCustomActions ?? []) + [archive]
}

/// A label whose text is in a different language from the app.
@MainActor
public func makeForeignLanguageLabel(text: String, languageTag: String) -> UILabel {
    let label = UILabel()
    label.text = text
    label.accessibilityLanguage = languageTag
    label.font = .preferredFont(forTextStyle: .body)
    label.adjustsFontForContentSizeCategory = true
    return label
}

/// A photo view that keeps its real colors under Smart Invert.
@MainActor
public func makePhotoView(image: UIImage?, caption: String) -> UIImageView {
    let view = UIImageView(image: image)
    view.isAccessibilityElement = true
    view.accessibilityLabel = caption
    view.accessibilityIgnoresInvertColors = true
    return view
}
