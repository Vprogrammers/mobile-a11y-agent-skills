struct AccountScreen: View {
    @State private var message = ""
    @AccessibilityFocusState private var focused: Bool

    var body: some View {
        VStack {
            HStack {
                Button("Edit", action: edit)
                Button("Delete", action: delete)
            }
            .accessibilityElement(children: .combine)

            Circle()
                .fill(message.isEmpty ? .red : .green)
                .frame(width: 12, height: 12)

            WebView(url: accountURL)
        }
        .dynamicTypeSize(...DynamicTypeSize.large)
        .accessibilityFocused($focused)
        .onChange(of: message) { focused = true }
    }
}
