final class ReceiptCell: UITableViewCell {
    private let title = UILabel()
    private let amount = UILabel()
    private let remove = UIButton(configuration: .plain())
    var onRemove: (() -> Void)?

    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        title.font = .preferredFont(forTextStyle: .headline)
        title.adjustsFontForContentSizeCategory = true
        title.numberOfLines = 0
        amount.font = .preferredFont(forTextStyle: .body)
        amount.adjustsFontForContentSizeCategory = true
        remove.configuration?.title = "Remove"
        remove.addAction(UIAction { [weak self] _ in self?.onRemove?() }, for: .touchUpInside)

        let stack = UIStackView(arrangedSubviews: [title, amount, remove])
        stack.axis = .vertical
        stack.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(stack)
        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: contentView.layoutMarginsGuide.leadingAnchor),
            stack.trailingAnchor.constraint(equalTo: contentView.layoutMarginsGuide.trailingAnchor),
            stack.topAnchor.constraint(equalTo: contentView.layoutMarginsGuide.topAnchor),
            stack.bottomAnchor.constraint(equalTo: contentView.layoutMarginsGuide.bottomAnchor),
        ])
        isAccessibilityElement = true
        accessibilityCustomActions = [
            UIAccessibilityCustomAction(name: "Remove") { [weak self] _ in
                self?.onRemove?()
                return true
            },
        ]
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func configure(title: String, amount: String) {
        self.title.text = title
        self.amount.text = amount
        accessibilityLabel = "\(title), \(amount)"
    }
}

final class CodeEntryView: UIView {
    let field = UITextField()

    override init(frame: CGRect) {
        super.init(frame: frame)
        field.placeholder = "Verification code"
        field.keyboardType = .numberPad
        field.textContentType = .oneTimeCode
        field.font = .preferredFont(forTextStyle: .body)
        field.adjustsFontForContentSizeCategory = true
        field.accessibilityIdentifier = "verification-code"
        addSubview(field)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
