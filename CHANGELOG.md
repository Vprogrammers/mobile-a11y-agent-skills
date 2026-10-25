# Changelog

## Unreleased

- Retain the r5 repair eval bundles and record the result: plugin and baseline both fixed `compose-order-card` with 8/8 in all three runs, so this eval does not yet separate them. See `evals/results/README.md`.
- Add repair evals that measure whether an engineer agent fixes a defect, not only whether it describes one. `compose-order-card` gives `android-a11y-engineer` a Gradle workspace with the `OrderCard.kt` fixture. Hidden Robolectric tests and a pattern check score the fix without a judge, and a required test fails a fix that breaks existing behavior. `run_repair_eval.py --self-check` runs in Android CI and proves the tests fail on the original and pass on a reference fix.
- Retain the r4 held-out eval bundles and record the result: on defects the skills do not teach, the plugin and the baseline both passed 3 of 6 runs. See `evals/results/README.md`.
- Stop requiring Smart Invert in the `heldout-swiftui-review` verification criterion, now `verification-covers-voiceover-and-switch-control`. A missed Smart Invert defect lost points twice.
- Name Android, iOS, or Kotlin Multiplatform in every agent description and add example requests, so routing does not pick the reviewer for web-only changes. Add a routing eval for each of the five agents and raise the plugin eval cost cap to match.
- Require the Android and iOS engineer agents to run the narrowest existing build and tests before reporting completion, or to say why they could not.
- Add iOS display-setting guidance for Differentiate Without Color, Bold Text, Button Shapes, On/Off Labels, and Reduce Transparency, with a matching code signal.
- Add a "Where to look" guide to the Android, iOS, KMP, and testing skills that maps the code in a change to a reference section. The validator now checks that link anchors match a heading.
- Run the paid `Agent eval regression` workflow only on demand. The weekly schedule failed by design whenever `CLAUDE_CODE_OAUTH_TOKEN` was not configured.
- Move the light distribution to `Vprogrammers/mobile-a11y-agent-skills-lite` and point the sync workflow and README at it.
- Add two held-out evals, `heldout-compose-review` and `heldout-swiftui-review`, built from defects whose patterns and fix APIs appear nowhere in `skills/`. Their manifest entries list `held_out_terms`, and the validator fails when a term appears in a skill file. The Compose fixture compiles in `samples/` with runtime guards; the SwiftUI fixture compiles and has static guards.
- Add an optional second judge (`EVAL_SECOND_JUDGE_COMMAND`). A run passes only when both judges pass it, and `summary.json` records both scores and whether they agree.
- Expand guidance for charts, custom drawing, maps, and media on Android and iOS: `ExploreByTouchHelper`, Canvas semantics, Swift Charts, `accessibilityChartDescriptor`, `accessibilityChildren`, Media3 caption preferences, and `AVPlayer` media selection, with compiled chart samples. Add code signals for charts, maps, and media.
- Record which iOS accessibility features the Compose Multiplatform documentation names as supported, and which it does not mention.

## 0.7.0

- Retain the r3 eval bundles: five harder evals, plugin and baseline, three runs each. The plugin passed 15 of 15 and the baseline 4 of 15; see `evals/results/README.md` for the per-finding analysis and limits.
- Rate `on-back-pressed-not-called-on-sdk36` as P2: the lost callback only stops back from hiding an informational notice, and it affects every user rather than an assistive-technology group.
- List a removed visible focus indicator for keyboard or switch users as a P1 calibration example in `mobile-a11y-review`.
- Add a code-signal table to the review checklist that maps patterns in changed code, such as unkeyed lazy lists, gesture handlers, custom drawing, and WebViews, to the behavior a reviewer must check.
- Require severity for matched defects in evals whose prompts ask for it (`severity_required` in the manifest). The suite gives both variants the P0–P3 definitions from `mobile-a11y-review`. An unrated defect earns no points, so omitting severity no longer scores better than a mismatch. The judge records the P0–P3 severity the response assigned, not the rubric's, and drops other scales.
- Score a severity mismatch as a missed finding instead of rejecting the whole judge result, and keep rejected judge output for diagnosis. In r3, every Compose, Android SDK 36, and UIKit traps run was rejected this way, so those evals produced no score.
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
