final class ProfileViewController: UIViewController {
    private let avatar = UIImageView(image: UIImage(named: "avatar"))
    private let status = UILabel()
    private let save = UIView()

    override func viewDidLoad() {
        super.viewDidLoad()
        status.text = "Verified"
        status.textColor = .green
        status.font = .systemFont(ofSize: 14)
        save.backgroundColor = .systemBlue
        save.addGestureRecognizer(UITapGestureRecognizer(target: self, action: #selector(saveProfile)))
        avatar.isAccessibilityElement = true
        avatar.accessibilityLabel = "Image"
    }

    @objc private func saveProfile() {}
}
