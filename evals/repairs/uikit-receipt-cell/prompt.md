Fix the accessibility defects in `Sources/RepairFixture/ReceiptCell.swift` in this Swift package.

VoiceOver, Voice Control, and Switch Control users must be able to remove a receipt from `ReceiptCell`, its text must follow Dynamic Type at accessibility sizes, and `CodeEntryView` must let people fill the verification code without retyping it. Keep the class names, initializers, `configure(title:amount:)`, `onRemove`, and the existing behavior. Do not add dependencies.

Build with `xcodebuild build -scheme RepairWorkspace -destination 'generic/platform=iOS Simulator'` before you finish, and report what you changed and what still needs a real-device check.
