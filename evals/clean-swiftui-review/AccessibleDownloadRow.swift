struct AccessibleDownloadRow: View {
    let progress: Double
    let onCancel: () -> Void

    var body: some View {
        VStack(alignment: .leading) {
            Text("Downloading")
                .font(.headline)
                .accessibilityAddTraits(.isHeader)

            ProgressView(value: progress)
                .accessibilityLabel("Download progress")
                .accessibilityValue(Text(progress, format: .percent))

            Button("Cancel", action: onCancel)
        }
    }
}
