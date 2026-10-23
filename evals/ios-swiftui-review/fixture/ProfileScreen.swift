import SwiftUI
import WebKit

// Eval fixture: intentionally inaccessible. Do not copy into production code.

public struct ProfileScreen: View {
    @State private var progress = 0.0
    @AccessibilityFocusState private var progressFocused: Bool
    let isVerified: Bool
    let edit: () -> Void
    let delete: () -> Void

    public init(isVerified: Bool, edit: @escaping () -> Void, delete: @escaping () -> Void) {
        self.isVerified = isVerified
        self.edit = edit
        self.delete = delete
    }

    public var body: some View {
        VStack {
            // DEFECT combined-actions: two unrelated buttons merged into one element.
            HStack {
                Button("Edit", action: edit)
                Button("Delete", action: delete)
            }
            .accessibilityElement(children: .combine)

            // DEFECT dynamic-type-capped: user text size is capped without a documented reason.
            Text("Profile")
                .font(.title)
                .dynamicTypeSize(...DynamicTypeSize.large)

            // DEFECT color-only-status: verification is conveyed only by color.
            Circle()
                .fill(isVerified ? Color.green : Color.red)
                .frame(width: 12, height: 12)

            // DEFECT focus-on-every-update: accessibility focus jumps on each progress tick.
            ProgressView(value: progress)
                .accessibilityFocused($progressFocused)
                .onChange(of: progress) { progressFocused = true }

            // DEFECT gesture-only-avatar: tap gesture on an image with no label or button trait.
            Image(systemName: "person.crop.circle")
                .onTapGesture(perform: edit)

            // DEFECT unaudited-webview: embedded web content with no title or boundary verification.
            HelpWebView(url: URL(string: "https://example.com/help")!)
                .frame(height: 300)
        }
    }
}

struct HelpWebView: UIViewRepresentable {
    let url: URL

    func makeUIView(context: Context) -> WKWebView {
        let view = WKWebView()
        view.load(URLRequest(url: url))
        return view
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
