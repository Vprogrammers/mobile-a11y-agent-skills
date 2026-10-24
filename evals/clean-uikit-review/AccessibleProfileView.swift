final class AccessibleProfileView: UIStackView {
    private let status = UILabel()
    private let save = UIButton(configuration: .plain())

    init(onSave: @escaping () -> Void) {
        super.init(frame: .zero)
        axis = .vertical

        status.text = "Profile verified"
        status.font = .preferredFont(forTextStyle: .body)
        status.adjustsFontForContentSizeCategory = true

        save.setTitle("Save profile", for: .normal)
        save.addAction(UIAction { _ in onSave() }, for: .touchUpInside)

        addArrangedSubview(status)
        addArrangedSubview(save)
    }

    @available(*, unavailable)
    required init(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
}
