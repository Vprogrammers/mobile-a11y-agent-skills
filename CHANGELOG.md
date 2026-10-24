# Changelog

## Unreleased

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
