from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parent.parent

# Static guards for fixtures that samples/ does not exercise at runtime: the KMP fixtures cannot
# compile because they intentionally mix source sets and platform types, SwiftUI modifiers are not
# inspectable from XCTest without a third-party dependency, and the regulatory and test-evidence
# fixtures are prose. Some code findings, such as visual focus indication, cannot be asserted at runtime.
# Each pattern proves that the fixture still contains the evidence for a rubric finding. Findings in
# NOT_GUARDED are judged from the response alone or are covered elsewhere.
GUARDS: dict[str, dict[str, str]] = {
    "kmp-boundary-review": {
        "compose-type-in-common-api": r"import androidx\.compose\.ui\.semantics\.SemanticsPropertyReceiver[\s\S]*fun applyComposeSemantics\(receiver: SemanticsPropertyReceiver\)",
        "uikit-type-in-common-api": r"import platform\.UIKit\.UIAccessibilityTraits[\s\S]*val iosTraits: UIAccessibilityTraits",
        "flow-and-sealed-swift-interop": r"public sealed interface SharedAccessibilityError[\s\S]*val events: Flow<SharedAccessibilityError>",
        "optional-play-services-leak": r"public fun enableSmsRetriever\(\)",
    },
    "ios-swiftui-review": {
        "combined-unrelated-actions": r'Button\("Edit"[^\n]*\n\s*Button\("Delete"[^\n]*\n\s*\}\n\s*\.accessibilityElement\(children: \.combine\)',
        "color-only-status": r"Circle\(\)\s*\.fill\(message\.isEmpty \? \.red : \.green\)",
        "dynamic-type-cap": r"\.dynamicTypeSize\(\.\.\.DynamicTypeSize\.large\)",
        "repeated-focus-reset": r"\.onChange\(of: message\) \{ focused = true \}",
        "webview-needs-separate-audit": r"WebView\(url:",
    },
    "regulatory-evidence-review": {
        "distinguishes-published-from-cited-version": r"V4\.1\.1 is the newest published edition, it is automatically harmonized",
    },
    "clean-swiftui-review": {
        "recognizes-no-proven-blocker": r"ProgressView\(value: progress\)[\s\S]*Button\(\"Cancel\", action: onCancel\)",
    },
    "clean-android-views-review": {
        "recognizes-no-proven-blocker": r"Button\(context\)\.apply[\s\S]*setOnClickListener",
    },
    "clean-uikit-review": {
        "recognizes-no-proven-blocker": r"UIButton\(configuration: \.plain\(\)\)[\s\S]*preferredFont\(forTextStyle: \.body\)",
    },
    "en-301-549-scope-review": {
        "inventories-distinct-technologies": r"native Android and iOS[\s\S]*WebView[\s\S]*tagged PDF",
        "applies-en-self-scoping": r"only EN 301 549 clause 9",
        "distinguishes-publication-from-legal-baseline": r"latest publication, so it is automatically",
        "requires-surface-and-release-evidence": r"One successful automated scan[\s\S]*complete release",
    },
    "us-regulatory-scope-review": {
        "distinguishes-title-ii-title-iii-and-section-508": r"ADA Title II, ADA Title III, and Section 508",
        "identifies-title-ii-technical-baseline": r"all require WCAG 2\.2",
        "does-not-reduce-section-508-to-wcag": r"Section 508 does not require any software interoperability or functional-performance review",
        "rejects-scan-and-future-release-proof": r"same scan proves[\s\S]*future releases",
    },
    "compose-semantics-traps-review": {
        "indication-null-hides-focus": r"\.clickable\(\s*interactionSource = remember \{ MutableInteractionSource\(\) \},\s*indication = null,",
        "input-focus-is-not-accessibility-focus": r"LaunchedEffect\(errors\) \{\s*if \(errors\.isNotEmpty\(\)\) focusRequester\.requestFocus\(\)",
    },
    "android-sdk36-behavior-review": {
        "on-back-pressed-not-called-on-sdk36": r"override fun onBackPressed\(\)",
        "per-keystroke-announcement": r"override fun onTextChanged[\s\S]*counter\.announceForAccessibility\(counter\.text\)",
    },
    "kmp-interop-traps-review": {
        "global-context-actual": r"lateinit var appContext: Context\s*\n\s*actual fun isReduceMotionEnabled\(\)",
        "typealias-trait-escapes-header-check": r"public fun sectionTitleTraits\(\): UIAccessibilityTraits[\s\S]*header mentions UIKit types, and that check passes",
        "reduce-motion-read-once": r"public fun motionSpec\(\): MotionSpec =\s*\n\s*if \(isReduceMotionEnabled\(\)\)",
        "accessibility-sync-options-removed": r"Compose Multiplatform 1\.8\.1[\s\S]*accessibilitySyncOptions = AccessibilitySyncOptions\.Always",
    },
    "test-evidence-traps-review": {
        "robolectric-checks-do-not-run": r"app/src/test` and runs on Robolectric[\s\S]*enableAccessibilityChecks\(\)",
        "audit-handler-suppresses-all-issues": r"performAccessibilityAudit \{ _ in true \}",
        "identical-scaled-snapshots-indicate-no-scaling": r"2\.0 snapshots are pixel-identical to the 1\.0 snapshots",
        "green-suites-do-not-prove-assistive-technology": r"TalkBack and VoiceOver work correctly and this release does not need device testing",
    },
}
NOT_GUARDED: dict[str, set[str]] = {
    "kmp-boundary-review": {"proposes-platform-neutral-state-contract"},
    "ios-swiftui-review": set(),
    "regulatory-evidence-review": {
        "rejects-automated-compliance-claim",
        "distinguishes-standard-from-law",
        "requires-jurisdiction-and-scope-review",
        "requires-release-specific-evidence",
    },
    "clean-swiftui-review": {"requests-ios-device-verification"},
    "clean-android-views-review": {"requests-android-device-verification"},
    "clean-uikit-review": {"requests-ios-device-verification"},
    "en-301-549-scope-review": {"requires-context-before-legal-claim"},
    "us-regulatory-scope-review": {"requires-applicability-context"},
    # Guarded at runtime by EvalFixturesTest (Android) and ReceiptCellFixtureTests (iOS).
    "compose-semantics-traps-review": {"clear-and-set-hides-track-action", "error-not-associated-with-field"},
    "android-sdk36-behavior-review": {"password-variation-for-visible-code", "requires-android-16-device-verification"},
    "kmp-interop-traps-review": set(),
    "test-evidence-traps-review": set(),
}


class EvalFixtureGuardTests(unittest.TestCase):
    def evaluation(self, eval_id: str) -> dict[str, str]:
        manifest = json.loads((ROOT / "evals/manifest.json").read_text(encoding="utf-8"))
        return next(item for item in manifest["evaluations"] if item["id"] == eval_id)

    def test_every_rubric_finding_is_guarded_or_explicitly_exempt(self) -> None:
        for eval_id, guards in GUARDS.items():
            with self.subTest(eval_id=eval_id):
                rubric = json.loads((ROOT / self.evaluation(eval_id)["rubric"]).read_text(encoding="utf-8"))
                finding_ids = {item["id"] for item in rubric["required_findings"]}
                self.assertEqual(set(guards) | NOT_GUARDED[eval_id], finding_ids)

    def test_fixture_still_contains_rubric_evidence(self) -> None:
        for eval_id, guards in GUARDS.items():
            fixture = (ROOT / self.evaluation(eval_id)["fixture"]).read_text(encoding="utf-8")
            for finding_id, pattern in guards.items():
                with self.subTest(eval_id=eval_id, finding_id=finding_id):
                    self.assertRegex(fixture, re.compile(pattern))


if __name__ == "__main__":
    unittest.main()
