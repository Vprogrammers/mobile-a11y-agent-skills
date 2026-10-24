# Changelog

## Unreleased

- Replace the review skill's `Note` severity with `P3` so the skill, validator, scorer, and README share one `P0`–`P3` scale.
- Make the Android and iOS engineer agents invoke `mobile-a11y-review` and avoid edits when asked to review.
- Name the fixture path and forbid fixture edits in the Android Views and UIKit eval prompts.
- Run script compilation, the install smoke test, and unit tests from `scripts/validate.sh` and the Linux CI job instead of the macOS job.
- Skip Android and iOS sample builds on the monthly scheduled link check.
- Share skill-invocation parsing between the validator and install smoke test, detect every ``invoke `skill` `` reference, and require each agent to invoke a skill.
- Report a malformed rubric per eval instead of aborting validation of the remaining evals.
- Accept judge output wrapped in a Markdown code fence and reject non-object or unknown-field output before writing it.
- Add monthly Dependabot updates for the Android sample's Gradle dependencies.

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
