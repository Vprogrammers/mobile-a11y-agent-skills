#!/usr/bin/env bash
# Builds the samples and eval fixtures and runs the unit tests on the first available iPhone simulator.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

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

xcodebuild test -scheme ApplePatterns-Package -destination "id=$udid" -quiet
