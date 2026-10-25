struct NotificationSettingsView: View {
    @Binding var pushEnabled: Bool
    @Binding var digestEnabled: Bool
    let isOffline: Bool
    let summary: String
    let onSave: () -> Void

    var body: some View {
        Form {
            Section("Notifications") {
                HStack {
                    Text("Push notifications")
                    Spacer()
                    Toggle("", isOn: $pushEnabled)
                        .labelsHidden()
                }
                Toggle("Weekly digest", isOn: $digestEnabled)
            }

            Section {
                HStack {
                    if isOffline {
                        Image(decorative: "offline-badge")
                    }
                    Text(summary)
                        .font(.footnote)
                        .lineLimit(1)
                        .minimumScaleFactor(0.5)
                }
                Button("Save", action: onSave)
            }
        }
    }
}
