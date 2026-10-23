// swift-tools-version: 6.0
import Foundation
import PackageDescription

// test.sh copies the eval fixtures into Sources/EvalFixtures with an import header.
// Without that generated directory, the package builds the samples only.
let fixturesDirectory = URL(fileURLWithPath: #filePath)
    .deletingLastPathComponent()
    .appendingPathComponent("Sources/EvalFixtures")
let hasFixtures = FileManager.default.fileExists(atPath: fixturesDirectory.path)

var targets: [Target] = [
    .target(name: "ApplePatterns"),
    .testTarget(name: "ApplePatternsTests", dependencies: ["ApplePatterns"]),
]
var products: [Product] = [
    .library(name: "ApplePatterns", targets: ["ApplePatterns"]),
]
if hasFixtures {
    targets.append(.target(name: "EvalFixtures"))
    targets.append(.testTarget(name: "EvalFixturesTests", dependencies: ["EvalFixtures"]))
    products.append(.library(name: "EvalFixtures", targets: ["EvalFixtures"]))
}

let package = Package(
    name: "ApplePatterns",
    platforms: [.iOS(.v17)],
    products: products,
    targets: targets
)
