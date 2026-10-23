// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ApplePatterns",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "ApplePatterns", targets: ["ApplePatterns"]),
        .library(name: "EvalFixtures", targets: ["EvalFixtures"]),
    ],
    targets: [
        .target(name: "ApplePatterns"),
        // Symlink to evals/ios-swiftui-review/fixture so the review scenario stays valid Swift.
        .target(name: "EvalFixtures"),
        .testTarget(name: "ApplePatternsTests", dependencies: ["ApplePatterns", "EvalFixtures"]),
    ]
)
