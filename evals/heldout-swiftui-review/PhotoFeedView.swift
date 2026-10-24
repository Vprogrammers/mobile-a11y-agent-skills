struct Photo: Identifiable {
    let id: Int
    let imageName: String
    let caption: String
}

enum FeedFilter: String, CaseIterable {
    case all = "All"
    case favorites = "Favorites"
    case shared = "Shared"
}

struct PhotoFeedView: View {
    let featured: [Photo]
    let photos: [Photo]
    @State private var filter: FeedFilter = .all
    @State private var featuredIndex = 0
    @State private var autoAdvance = true

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                if !featured.isEmpty {
                    let photo = featured[featuredIndex % featured.count]
                    Image(photo.imageName)
                        .resizable()
                        .scaledToFill()
                        .frame(height: 220)
                        .clipped()
                        .accessibilityLabel(photo.caption)
                }

                HStack {
                    ForEach(FeedFilter.allCases, id: \.self) { option in
                        Button(option.rawValue) { filter = option }
                            .padding(.horizontal, 12)
                            .padding(.vertical, 8)
                            .background(filter == option ? Color.accentColor : Color.clear)
                            .foregroundStyle(filter == option ? Color.white : Color.primary)
                            .clipShape(Capsule())
                    }
                }

                LazyVGrid(columns: [GridItem(.adaptive(minimum: 100))]) {
                    ForEach(photos) { photo in
                        Image(photo.imageName)
                            .resizable()
                            .scaledToFill()
                            .frame(height: 100)
                            .clipped()
                            .accessibilityLabel(photo.caption)
                    }
                }
            }
            .padding()
        }
        .onAppear { autoAdvance = !UIAccessibility.isVoiceOverRunning }
        .task {
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(4))
                if autoAdvance, !featured.isEmpty {
                    featuredIndex = (featuredIndex + 1) % featured.count
                }
            }
        }
    }
}
