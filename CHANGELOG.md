# Changelog

## Unreleased

- Add a deterministic, validated light distribution with consumer-only instructions, provenance metadata, owner-attributed synchronization on canonical `main` pushes that change distribution inputs, and a canonical-repository contribution policy.
- Find the judge result object among prose braces or several JSON objects instead of slicing from the first `{` to the last `}`.
- Add five harder evals built from verified platform traps: `compose-semantics-traps-review`, `android-sdk36-behavior-review`, `uikit-container-traps-review`, `kmp-interop-traps-review`, and `test-evidence-traps-review`. The Android and iOS fixtures compile in `samples/` with runtime guards. The KMP and prose fixtures have static guards.
- Fix `clean-uikit-review`: its "clean" `UIButton(type: .system)` keeps a fixed 15 pt title at every Dynamic Type size, as measured on the simulator. The plugin reviewer reported it and the unassisted baseline did not. The fixture now uses `UIButton(configuration: .plain())`, a simulator test guards it, and `apple-patterns.md` documents the trap.
- Add severity calibration examples to `mobile-a11y-review`. A defect proven by code keeps its severity even while device confirmation is pending.
- Drop a judge's stray severity on non-defect criteria instead of rejecting the whole result. Defect severity mismatches still fail.
- Add `Skill` to every agent's `tools` list. An explicit list replaces the defaults, so before this change no agent could load the skills it is instructed to invoke. The validator now rejects an agent that invokes skills without `Skill`.
- Let restricted eval agents read skill references with `--add-dir "{plugin_dir}/skills"`, without exposing the rubrics.
- Add `samples/kmp`, which compiles the shared validation and reduced-motion contract with Android Compose/Settings and iOS UIKit adapters, common, Robolectric, and simulator tests, and an exported Objective-C header check. CI runs it on macOS.
- Add `EVAL_VARIANT=baseline` and per-eval points in `summary.json`, so the same rubrics can compare the plugin with an unassisted baseline. Retain the first reviewed baseline bundle.
- Correct the Compose accessibility-checks guidance: they require API 34+ instrumentation and pass silently on Robolectric. A guard test documents this.
- Add compiled test examples (commonTest fake, Compose semantics, XCUITest audit triage, UIKit properties) and WebView zoom guidance for Android `WebSettings` and `WKWebViewConfiguration.ignoresViewportScaleLimits`.
- Handle macOS `EPERM` from `killpg` after an eval subprocess exits.

- Run manifest-selected agents by their namespaced plugin identities in isolated restricted eval workspaces, add an official plugin eval with a no-plugin baseline, validate the plugin with Claude Code 2.1.310, and harden subprocess failure handling.
- Add opt-in scheduled agent evals and result bundles, harden the judge against prompt injection and runaway commands, validate critical Claude deny rules, structure EN 301 549 status evidence, retain failing XCTest bundles, and remove unused release automation.
- Compile clean platform eval fixtures, add per-reference freshness intervals, expand current US regulatory guidance and eval coverage, validate copied skill links, and provide an optional hardened Claude Code settings template.
- Add EN 301 549 technology self-scoping guidance and eval coverage, clean SwiftUI/Android Views/UIKit evals, agent execution boundaries, a security policy, and a real-device evidence template.
- Update EN 301 549 guidance to the latest published V4.1.1 edition, distinguish publication from Official Journal citation, and add an eval guard for unsupported harmonization claims.
- Replace the `Note` severity with `P3` so the review skill, validator, and scorer share one `P0`–`P3` scale.
- Have the Android and iOS engineer agents also invoke `mobile-a11y-review` for review-only tasks, and name the fixture path and forbid fixture edits in every eval prompt.
- Name platform skills explicitly in agents and share one invoked-skill parser between the validator and the installation smoke test.
- Lower `duplicate-delete-semantics` to P2, matching the skill's definition of degraded usability.
- Run script compilation, the installation smoke test, and unit tests from `validate.sh`, in the Ubuntu CI job instead of the macOS job.
- Skip the sample builds on the monthly link-check schedule, and build both samples before a release is created.
- Report an invalid rubric per eval without stopping validation of the others.
- Accept fenced or wrapped judge JSON and validate it before writing the result file.
- Warn 30 days before a reference review date becomes stale.
- Add static guards for the KMP and SwiftUI eval fixtures, and Dependabot updates for the Android sample's Gradle dependencies.

## 0.6.0

- Add `samples/android` and `samples/ios`, which compile the reference examples and the Android and iOS eval fixtures, with guard tests tied to rubric finding ids. CI runs both.
- Require at least one https source in every reference file and skip build output during validation.
- Add review sources to every reference and move duplicated test guidance into `mobile-a11y-testing`.
- Add draft Compose Multiplatform shared UI guidance, Swift export status, Android edge-to-edge, predictive back, and keyboard focus visibility.
- Add a literal report template to `mobile-a11y-review`.

## 0.5.0

- Separate finding kind from optional P0–P3 severity in eval rubrics.
- Add negative validator tests for malformed manifests, rubrics, references, and agent skill links.
- Add a plugin copy-install smoke test.
- Add an optional provider-neutral judge adapter for end-to-end eval runs.
- Add explicit acceptance criteria to every rubric finding.
- Harden scorer errors and tests for malformed result input.
- Pin GitHub Actions by commit SHA and add monthly Dependabot updates.

## 0.4.0

- Add clean-screen, Android Views, UIKit, mobile test-strategy, and regulatory evidence evals.
- Validate eval schemas, agent references, finding IDs, points, severities, and review dates.
- Validate optional reported severities and reject malformed scorer input.
- Add validator/scorer unit tests and monthly external-link checks.

## 0.3.0

- Add the initial deterministic validation and eval harness.
