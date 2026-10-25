import SwiftUI

// Compiled counterparts of the "Better" SwiftUI examples in apple-patterns.md.

/// Native action instead of a gesture-only image.
public struct DeleteButton: View {
    let delete: () -> Void

    public init(delete: @escaping () -> Void) {
        self.delete = delete
    }

    public var body: some View {
        Button(action: delete) {
            Label("Delete", systemImage: "trash")
        }
    }
}

/// Text grows with Dynamic Type instead of clipping at a fixed height.
public struct ScalableRow: View {
    let title: String

    public init(title: String) {
        self.title = title
    }

    public var body: some View {
        Text(title)
            .fixedSize(horizontal: false, vertical: true)
            .frame(minHeight: 44)
    }
}

/// Adjustable custom control exposing value and increment/decrement actions.
public struct RatingControl: View {
    @Binding var rating: Int
    let range: ClosedRange<Int>

    public init(rating: Binding<Int>, range: ClosedRange<Int> = 1...5) {
        _rating = rating
        self.range = range
    }

    public var body: some View {
        HStack {
            ForEach(range, id: \.self) { value in
                Image(systemName: value <= rating ? "star.fill" : "star")
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Rating")
        .accessibilityValue("\(rating) of \(range.upperBound)")
        .accessibilityAdjustableAction { direction in
            switch direction {
            case .increment: rating = min(rating + 1, range.upperBound)
            case .decrement: rating = max(rating - 1, range.lowerBound)
            @unknown default: break
            }
        }
    }
}

/// Move focus only for a meaningful context change such as a blocking validation summary.
public struct ValidationSummaryForm: View {
    @State private var errors: [String] = []
    @AccessibilityFocusState private var summaryFocused: Bool
    let validate: () -> [String]

    public init(validate: @escaping () -> [String]) {
        self.validate = validate
    }

    public var body: some View {
        VStack(alignment: .leading) {
            if !errors.isEmpty {
                Text("\(errors.count) fields need attention")
                    .accessibilityFocused($summaryFocused)
            }
            Button("Submit") {
                errors = validate()
                summaryFocused = !errors.isEmpty
            }
        }
    }
}

/// Layout adapts at accessibility sizes instead of capping Dynamic Type.
public struct AdaptiveHeader: View {
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @ScaledMetric(relativeTo: .body) private var iconSize: CGFloat = 24
    let title: String

    public init(title: String) {
        self.title = title
    }

    public var body: some View {
        let layout = dynamicTypeSize.isAccessibilitySize
            ? AnyLayout(VStackLayout(alignment: .leading))
            : AnyLayout(HStackLayout())
        layout {
            Image(systemName: "person.crop.circle")
                .resizable()
                .frame(width: iconSize, height: iconSize)
                .accessibilityHidden(true)
            Text(title)
                .font(.headline)
                .accessibilityAddTraits(.isHeader)
        }
    }
}

/// Visible one-time code field: AutoFill and paste stay available.
public struct OneTimeCodeField: View {
    @Binding var code: String

    public init(code: Binding<String>) {
        _code = code
    }

    public var body: some View {
        TextField("Verification code", text: $code)
            .textContentType(.oneTimeCode)
            .keyboardType(.numberPad)
    }
}

public struct Sale: Identifiable {
    public let month: String
    public let value: Int
    public var id: String { month }

    public init(month: String, value: Int) {
        self.month = month
        self.value = value
    }
}

/// A Canvas chart with a synthetic accessibility element per bar.
public struct SalesChart: View {
    let sales: [Sale]

    public init(sales: [Sale]) {
        self.sales = sales
    }

    public var body: some View {
        Canvas { context, size in drawBars(sales, in: &context, size: size) }
            .frame(height: 160)
            .accessibilityLabel("Monthly sales")
            .accessibilityChildren {
                HStack {
                    ForEach(sales) { sale in
                        Rectangle()
                            .accessibilityLabel(sale.month)
                            .accessibilityValue(Text(sale.value, format: .number))
                    }
                }
            }
    }
}

/// A section title that VoiceOver users can reach with the Headings rotor, with its level.
public struct SectionTitle: View {
    let title: String

    public init(title: String) {
        self.title = title
    }

    public var body: some View {
        Text(title)
            .font(.title2)
            .accessibilityAddTraits(.isHeader)
            .accessibilityHeading(.h2)
    }
}

/// The total is read before the line items even though it is drawn last.
public struct OrderSummary: View {
    let items: [String]
    let total: String

    public init(items: [String], total: String) {
        self.items = items
        self.total = total
    }

    public var body: some View {
        VStack(alignment: .leading) {
            ForEach(items, id: \.self) { Text($0) }
            Text(total).accessibilitySortPriority(1)
        }
        .accessibilityElement(children: .contain)
    }
}

/// A custom panel that VoiceOver users can dismiss with the escape gesture.
public struct CustomPanel<Content: View>: View {
    let dismiss: () -> Void
    let content: Content

    public init(dismiss: @escaping () -> Void, @ViewBuilder content: () -> Content) {
        self.dismiss = dismiss
        self.content = content()
    }

    public var body: some View {
        VStack {
            content
            Button("Close", action: dismiss)
        }
        .accessibilityAddTraits(.isModal)
        .accessibilityAction(.escape, dismiss)
    }
}

/// Announce an asynchronous result that no visible state change conveys.
@MainActor
public func announceSaved(_ message: String) {
    AccessibilityNotification.Announcement(message).post()
}

/// A phrase in another language, tagged with its language. Verify the pronunciation with VoiceOver.
public func quotedPhrase(intro: String, phrase: String, languageTag: String) -> AttributedString {
    var quote = AttributedString(phrase)
    quote.languageIdentifier = languageTag
    return AttributedString(intro) + quote
}

/// A small tab-style control that shows its label in the Large Content Viewer.
public struct CompactTab: View {
    let title: String
    let systemImage: String
    let select: () -> Void

    public init(title: String, systemImage: String, select: @escaping () -> Void) {
        self.title = title
        self.systemImage = systemImage
        self.select = select
    }

    public var body: some View {
        Button(action: select) {
            Image(systemName: systemImage)
                .frame(minWidth: 44, minHeight: 44)
                .contentShape(Rectangle())
        }
        .accessibilityLabel(title)
        .accessibilityShowsLargeContentViewer {
            Label(title, systemImage: systemImage)
        }
    }
}

/// Motion and contrast follow the system settings.
public struct StatusBadge: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.colorSchemeContrast) private var contrast
    let text: String
    let isActive: Bool

    public init(text: String, isActive: Bool) {
        self.text = text
        self.isActive = isActive
    }

    public var body: some View {
        Label(text, systemImage: isActive ? "checkmark.circle.fill" : "circle")
            .padding(8)
            .background(contrast == .increased ? Color.primary.opacity(0.2) : Color.secondary.opacity(0.1))
            .animation(reduceMotion ? nil : .default, value: isActive)
    }
}

/// A tappable row that switches a setting exposes the toggle trait and its state.
public struct CustomToggleRow: View {
    let title: String
    @Binding var isOn: Bool

    public init(title: String, isOn: Binding<Bool>) {
        self.title = title
        _isOn = isOn
    }

    public var body: some View {
        HStack {
            Text(title)
            Spacer()
            Image(systemName: isOn ? "checkmark.circle.fill" : "circle")
                .accessibilityHidden(true)
        }
        .contentShape(Rectangle())
        .onTapGesture { isOn.toggle() }
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits([.isButton, .isToggle])
        .accessibilityValue(isOn ? Text("On") : Text("Off"))
        .accessibilityAction { isOn.toggle() }
    }
}

/// Inline links stay links for VoiceOver instead of tap targets inside the text.
public struct TermsNotice: View {
    public init() {}

    public var body: some View {
        Text("Messages follow our [terms](https://example.com/terms).")
    }
}

/// Filter options expose which one is selected, not only through color.
public struct FilterBar: View {
    @Binding var selection: String
    let options: [String]

    public init(selection: Binding<String>, options: [String]) {
        _selection = selection
        self.options = options
    }

    public var body: some View {
        HStack {
            ForEach(options, id: \.self) { option in
                Button(option) { selection = option }
                    .padding(8)
                    .background(selection == option ? Color.accentColor : Color.clear)
                    .accessibilityAddTraits(selection == option ? .isSelected : [])
            }
        }
    }
}

/// Photos keep their real colors under Smart Invert.
public struct PhotoTile: View {
    let imageName: String
    let caption: String

    public init(imageName: String, caption: String) {
        self.imageName = imageName
        self.caption = caption
    }

    public var body: some View {
        Image(imageName)
            .resizable()
            .scaledToFill()
            .accessibilityLabel(caption)
            .accessibilityIgnoresInvertColors()
    }
}

/// A carousel that advances only while unpaused and while Reduce Motion is off.
public struct FeaturedCarousel: View {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var index = 0
    @State private var isPaused = false
    let captions: [String]

    public init(captions: [String]) {
        self.captions = captions
    }

    public var body: some View {
        VStack {
            if !captions.isEmpty {
                Text(captions[index % captions.count])
            }
            Button(isPaused ? "Play slideshow" : "Pause slideshow") { isPaused.toggle() }
        }
        // Restarting the task when either condition changes keeps the timer in step with the settings.
        .task(id: isPaused || reduceMotion) {
            guard !isPaused, !reduceMotion, !captions.isEmpty else { return }
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(5))
                guard !Task.isCancelled else { break }
                index = (index + 1) % captions.count
            }
        }
    }
}

private func drawBars(_ sales: [Sale], in context: inout GraphicsContext, size: CGSize) {
    guard let maximum = sales.map(\.value).max(), maximum > 0 else { return }
    let barWidth = size.width / CGFloat(sales.count * 2)
    for (index, sale) in sales.enumerated() {
        let height = size.height * CGFloat(sale.value) / CGFloat(maximum)
        let bar = CGRect(x: CGFloat(index * 2) * barWidth, y: size.height - height, width: barWidth, height: height)
        context.fill(Path(bar), with: .color(.gray))
    }
}
