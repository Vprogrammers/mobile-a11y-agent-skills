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
                            .accessibilityValue("\(sale.value)")
                    }
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
