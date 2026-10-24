#!/usr/bin/env bash
# Compiles the samples and the iOS eval fixtures, then runs the unit tests on the first available iPhone simulator.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# Eval fixtures are shown to agents without import lines; compile copies with a header instead of changing them.
fixtures="Sources/EvalFixtures"
rm -rf "$fixtures" && mkdir -p "$fixtures"
for fixture in ../../evals/ios-swiftui-review/AccountScreen.swift ../../evals/ios-uikit-review/ProfileViewController.swift ../../evals/clean-swiftui-review/AccessibleDownloadRow.swift ../../evals/clean-uikit-review/AccessibleProfileView.swift ../../evals/uikit-container-traps-review/ReceiptCell.swift; do
    { printf '// Generated from evals/ by test.sh. Edit the fixture, not this copy.\nimport SwiftUI\nimport UIKit\n\n'; cat "$fixture"; } > "$fixtures/$(basename "$fixture")"
done
cp EvalFixtureStubs.swift.txt "$fixtures/EvalFixtureStubs.swift"

udid="$(xcrun simctl list devices available -j | python3 -c '
import json, sys
devices = json.load(sys.stdin)["devices"]
for runtime in sorted(devices, reverse=True):
    if "iOS" in runtime:
        for device in devices[runtime]:
            if device["name"].startswith("iPhone"):
                print(device["udid"])
                sys.exit(0)
sys.exit("No available iPhone simulator")
')"

result_bundle="${IOS_RESULT_BUNDLE_PATH:-build/TestResults.xcresult}"
simulator_arch="$(uname -m)"
rm -rf "$result_bundle"
xcodebuild test \
    -scheme ApplePatterns-Package \
    -destination "platform=iOS Simulator,id=$udid,arch=$simulator_arch" \
    -resultBundlePath "$result_bundle" \
    -quiet
